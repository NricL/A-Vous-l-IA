"""Opt-in isolated preview. Local by default; Azure test hosting must be explicit."""

import html
import json
import os
import threading
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse
from pydantic import BaseModel, ConfigDict, Field

from app.preview_protocol import ProtocolError, QualificationService
from app.preview_repository import CatalogueRepository, SyntheticRepository
from app.preview_parcours import ParcoursRenderer
from app.preview_hosting import HostingPolicy, PreviewBoundary
from app.preview_public_api import PublicAPIRepository, public_parcours_url

PREFIX = "/api/preview/v1"


class CreateSession(BaseModel):
    protocol_version: Literal[1]
    initial_need: str = Field(default="", max_length=8000)
    external_consent: bool = False
    source_mode: Literal["SYNTHETIC", "PUBLIC_API", "PUBLIC_PAGES"] | None = None

    model_config = ConfigDict(extra="forbid")


class Action(BaseModel):
    protocol_version: Literal[1]
    catalogue_revision: str
    revision: int = Field(ge=0)
    question_id: str
    request_id: str = Field(min_length=8, max_length=128)
    action: Literal["choose", "describe", "back", "reset", "reject", "accept", "refuse"]
    choice_id: str | None = None
    choice_text: str | None = Field(default=None, max_length=500)
    target: str | None = None
    text: str | None = Field(default=None, max_length=8000)
    initial_need: str | None = Field(default=None, max_length=8000)

    model_config = ConfigDict(extra="forbid")


def create_app(repository: CatalogueRepository | None = None, *, mode: str | None = None,
               parcours_root: str | None = None, backend_origin: str | None = None) -> FastAPI:
    selected_mode = mode if mode is not None else os.environ.get("AVIA_PREVIEW_MODE")
    hosting = HostingPolicy.from_environment(backend_origin)
    cloud = hosting.mode == "azure_test"
    if cloud and (selected_mode != "public_pages"
                  or repository is not None and repository.provenance["source_mode"] != "PUBLIC_PAGES"):
        raise RuntimeError("azure_test permits PUBLIC_PAGES only; no source fallback.")
    if repository is None and selected_mode not in {"synthetic", "public_api", "public_pages"}:
        raise RuntimeError("Preview disabled. Explicitly set AVIA_PREVIEW_MODE=synthetic, public_api or public_pages; no fallback.")
    supplied_repository = repository is not None

    def make_repository(name):
        if name == "public_pages":
            from app.preview_public_rag import PublicPagesRepository
            cache = os.environ.get("AVIA_PREVIEW_PUBLIC_CACHE")
            if not cache:
                raise RuntimeError("PUBLIC_PAGES requires AVIA_PREVIEW_PUBLIC_CACHE; no private source lookup.")
            return PublicPagesRepository(Path(cache))
        return PublicAPIRepository() if name == "public_api" else SyntheticRepository()

    if repository is None:
        repository = make_repository(selected_mode)
    service = QualificationService(repository)
    services = {repository.provenance["source_mode"]: service}
    source_lock = threading.RLock()

    def source_service(source_mode=None):
        name = source_mode or repository.provenance["source_mode"]
        if cloud and name != "PUBLIC_PAGES":
            raise ProtocolError("source_not_allowed", "Cette préversion expose uniquement PUBLIC_PAGES v4.6.1.", 403)
        with source_lock:
            if name not in services:
                if supplied_repository or name == "PUBLIC_PAGES" and not os.environ.get("AVIA_PREVIEW_PUBLIC_CACHE"):
                    raise ProtocolError("source_unavailable", "Ce mode source n'est pas configuré. Aucun repli.", 503)
                try:
                    services[name] = QualificationService(make_repository(name.lower()))
                except (ValueError, OSError, RuntimeError):
                    raise ProtocolError("source_unavailable", "Source ou index local indisponible. Aucun repli.", 503) from None
            return services[name]

    def for_session(session_id):
        with source_lock:
            return next((item for item in services.values() if session_id in item.sessions), service)
    renderer = ParcoursRenderer(parcours_root, hosting.frontend_origin, app_url=hosting.app_url,
                               allowed_origins=set(hosting.cors_origins) | {hosting.own_origin}, cloud=cloud)
    if cloud:
        # Validate the local renderer at startup without opening a workbook or calling a model.
        renderer.template = renderer._load().load_template()
    app = FastAPI(title="AVIA isolated qualification preview", docs_url=None, redoc_url=None, openapi_url=None)
    app.state.qualification = service
    app.state.hosting = hosting
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(hosting.cors_origins),
        allow_methods=["GET", "POST"], allow_headers=["Content-Type"],
    )

    app.add_middleware(PreviewBoundary, policy=hosting)

    @app.exception_handler(ProtocolError)
    async def protocol_error(_request: Request, error: ProtocolError):
        return JSONResponse({"error": error.code, "message": error.message}, status_code=error.status)

    @app.get("/health")
    async def health(source_mode: Literal["SYNTHETIC", "PUBLIC_API", "PUBLIC_PAGES"] | None = None):
        if cloud and source_mode not in (None, "PUBLIC_PAGES"):
            raise ProtocolError("source_not_allowed", "Cette préversion expose uniquement PUBLIC_PAGES v4.6.1.", 403)
        # No session lock, queued worker or external readiness call on the probe path.
        selected = service if cloud else source_service(source_mode)
        return {"status": "ok", "preview": True, "protocol_version": 1,
                "hosting_mode": hosting.mode,
                "allowed_source_modes": ["PUBLIC_PAGES"] if cloud else ["SYNTHETIC", "PUBLIC_API", "PUBLIC_PAGES"],
                "session_policy": {"storage": "process_memory", "max_sessions": 128, "ttl_seconds": 3600,
                                   "workers": 1, "replicas": 1, "authentication": "anonymous",
                                   "warning": "Identifiant de session = lien porteur, pas une protection MIP. "
                                              "Ne saisissez aucune donnée personnelle ou confidentielle."},
                "source": selected.repository.provenance}

    @app.post(f"{PREFIX}/sessions")
    def start(payload: CreateSession):
        selected_service = source_service(payload.source_mode)
        if selected_service.repository.provenance["source_mode"] in {"PUBLIC_API", "PUBLIC_PAGES"} and not payload.external_consent:
            raise ProtocolError("external_consent_required",
                                "Confirmez l'envoi externe du besoin au service Azure existant avant de commencer.", 403)
        snapshot = selected_service.create(payload.initial_need)
        return snapshot

    @app.get(f"{PREFIX}/sessions/{{session_id}}")
    def state(session_id: str):
        return for_session(session_id).read(session_id)

    @app.post(f"{PREFIX}/sessions/{{session_id}}/actions")
    def act(session_id: str, payload: Action):
        return for_session(session_id).act(session_id, payload.model_dump(exclude_none=True))

    @app.post(f"{PREFIX}/sessions/{{session_id}}/actions/stream")
    def stream(session_id: str, payload: Action):
        # Apply and validate before opening the stream: stale actions get HTTP
        # 409, not a misleading 200 or partial text that could mutate the UI.
        snapshot = for_session(session_id).act(session_id, payload.model_dump(exclude_none=True))
        event = f"id: {snapshot['revision']}\nevent: state\ndata: {json.dumps(snapshot, ensure_ascii=False)}\n\n"
        return StreamingResponse(iter([event]), media_type="text/event-stream")

    @app.get(f"{PREFIX}/sessions/{{session_id}}/handoff")
    def handoff(session_id: str, revision: int = Query(ge=0)):
        return for_session(session_id).handoff(session_id, revision)

    @app.get("/preview/parcours/{session_id}", response_class=HTMLResponse)
    def parcours(session_id: str, revision: int = Query(ge=0)):
        transfer = for_session(session_id).handoff(session_id, revision)
        if transfer["source"]["source_mode"] == "PUBLIC_API":
            return RedirectResponse(public_parcours_url(transfer["parcours_url"], transfer["case_hash"]),
                                    status_code=303, headers={"Referrer-Policy": "no-referrer"})
        return HTMLResponse(renderer.render(transfer), headers={
            "Content-Security-Policy": (
                "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; "
                "connect-src 'none'; img-src 'none'; font-src 'none'; object-src 'none'; "
                "base-uri 'none'; form-action 'none'; frame-ancestors 'none'"
            ),
        })

    @app.get(f"/preview/context/{{session_id}}", response_class=HTMLResponse)
    def context(session_id: str, revision: int = Query(ge=0)):
        transfer = for_session(session_id).handoff(session_id, revision)
        if transfer["source"]["source_mode"] != "SYNTHETIC":
            raise ProtocolError("context_view_unavailable",
                                "En mode public, utilisez la fiche locale et le parcours actuel publié.", 422)
        source = transfer["source_fields"]
        # This is a local transfer sheet, explicitly NOT a generated six-step
        # parcours. The page generator can consume the JSON handoff separately.
        return HTMLResponse(
            "<!doctype html><html lang='fr'><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width,initial-scale=1'>"
            "<title>AVIA — transfert local synthétique</title>"
            "<main style='max-width:760px;margin:3rem auto;padding:1rem;font:18px system-ui'>"
            "<p><strong>PRÉVERSION SYNTHÉTIQUE — NON PRODUCTION</strong></p>"
            "<h1>Fiche de transfert locale</h1>"
            "<p>Ce document n'est pas le parcours en six étapes. Aucun parcours source n'est disponible pour ce cas fictif.</p>"
            f"<h2>{html.escape(source['title'])}</h2><p>{html.escape(source['description'])}</p>"
            "<h2>Votre contexte local (distinct de la source)</h2>"
            f"<pre style='white-space:pre-wrap'>{html.escape(transfer['local_context']['problem_original'])}</pre>"
            f"<p>ID : {html.escape(transfer['case_id'])}</p>"
            f"<p style='overflow-wrap:anywhere'>Empreinte source : {html.escape(transfer['source_hash'])}</p>"
            "<p>Aucun contenu envoyé à un tiers. Aucun lien public ne contient votre besoin.</p></main></html>",
            headers={"Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; frame-ancestors 'none'"},
        )

    return app
