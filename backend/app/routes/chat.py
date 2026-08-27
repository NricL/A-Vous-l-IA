import json
import re

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.config import get_settings
from app.models import ChatRequest, ChatResponse, SuggestedCase
from app.rag import chat_simple, chat_simple_stream, stream_prompt
from app.haystack_rag import query_rag_haystack, get_rag_prompt_and_sources, WELCOME_MESSAGE
from app.parcours_util import build_parcours_info, get_parcours_pitch, PARCOURS_PITCH_SENTINEL
from app.rag_constants import Q1_DOMAINS_LIST, CHOIX_Q1_TO_DOMAINE_CODE
from app.telemetry import track_backend_chat_event
from app import stats

router = APIRouter(prefix="/chat", tags=["chat"])
_UC_CODE_RE = re.compile(r"\bUC-\d{3,5}\b", re.IGNORECASE)

# Mapping code domaine -> libellé Q1 lisible (pour les stats d'usage).
_DOMAINE_CODE_TO_LABEL = {
    code: Q1_DOMAINS_LIST[n - 1]
    for n, code in CHOIX_Q1_TO_DOMAINE_CODE.items()
    if 1 <= n <= len(Q1_DOMAINS_LIST)
}


def _domaine_label(code: str | None) -> str:
    code = (code or "").strip()
    return _DOMAINE_CODE_TO_LABEL.get(code, code)


def _record_usage_stats(request: ChatRequest, selected_domain_code, suggested_cases, niveau2_prebuilt) -> None:
    """Stats d'usage simples (Axe 3.1). Non bloquant : toute erreur est avalée."""
    try:
        # Domaine : enregistré au moment où il est choisi (transition : pas encore fixé côté requête).
        if not (request.selected_domain_code or "").strip() and (selected_domain_code or "").strip():
            stats.record("domaine", _domaine_label(selected_domain_code))
        # Problématique (Q3) : message libre qui produit la liste de cas (pas un numéro, pas un détail).
        msg = (request.message or "").strip()
        if suggested_cases and not niveau2_prebuilt and not msg.isdigit() and len(msg) >= 4:
            stats.record("probleme", msg)
    except Exception:
        pass

# Le RAG_PROMPT demande au LLM de RÉAFFICHER le message d'accueil au début de CHAQUE réponse.
# Or il est déjà affiché une seule fois au chargement du chat (GET /chat/welcome). On retire donc
# ce préambule redondant en tête de chaque réponse (tolérant aux espaces/retours à la ligne, aux
# guillemets, et — important — au type d'apostrophe : le LLM produit souvent des apostrophes
# typographiques « ’ » là où WELCOME_MESSAGE utilise des apostrophes droites « ' »).
# Normalisation 1:1 (un caractère → un caractère) : préserve les indices, donc on peut retirer la
# portion trouvée sur le texte ORIGINAL sans le déformer.
_WELCOME_NORMALIZE = {0x2019: 0x27, 0x2018: 0x27, 0x201C: 0x22, 0x201D: 0x22, 0x00AB: 0x22, 0x00BB: 0x22}


def _normalize_quotes(s: str) -> str:
    return s.translate(_WELCOME_NORMALIZE)


_WELCOME_RE = re.compile(
    r'^\s*"?\s*' + r"\s+".join(re.escape(tok) for tok in _normalize_quotes(WELCOME_MESSAGE).split()) + r'\s*"?',
    re.IGNORECASE,
)


def _strip_repeated_welcome(text: str) -> str:
    """Retire le préambule d'accueil répété par le LLM (déjà montré une fois au chargement)."""
    match = _WELCOME_RE.match(_normalize_quotes(text))
    if not match:
        return text
    return text[match.end():].lstrip()



@router.get("/welcome")
def chat_welcome():
    """Retourne le premier message que l'agent affiche au chargement du chat."""
    return {"message": WELCOME_MESSAGE}


@router.post("/parcours-click")
def parcours_click(payload: dict | None = None):
    """Stat : l'utilisateur a cliqué sur le bouton parcours (conversion clé). Appelé par le frontend."""
    value = ""
    if isinstance(payload, dict):
        value = str(payload.get("case_id") or payload.get("case_hash") or "").strip()
    stats.record("parcours_click", value or "clic")
    return {"ok": True}


@router.post("/feedback")
def case_feedback(payload: dict | None = None):
    """Stat : l'utilisateur juge un cas pertinent (👍) ou peu pertinent (👎). Appelé par le frontend."""
    if not isinstance(payload, dict):
        return {"ok": False}
    useful = bool(payload.get("useful"))
    label = str(payload.get("case_label") or payload.get("case_hash") or "").strip() or "cas"
    stats.record("feedback_up" if useful else "feedback_down", label[:200])
    return {"ok": True}


def _sse_line(obj: dict) -> str:
    return f"data: {json.dumps(obj, ensure_ascii=False)}\n\n"


def _last_suggested_cases_to_dicts(request: ChatRequest) -> list[dict] | None:
    if not request.last_suggested_cases:
        return None
    out: list[dict] = []
    for c in request.last_suggested_cases:
        d: dict = {"id": c.id, "content": c.content}
        if c.effort is not None:
            d["effort"] = c.effort
        if c.prerequis_donnees is not None:
            d["prerequis_donnees"] = c.prerequis_donnees
        if c.guardrails is not None:
            d["guardrails"] = c.guardrails
        if c.questions_qualification is not None:
            d["questions_qualification"] = c.questions_qualification
        if c.sensibilite_donnees is not None:
            d["sensibilite_donnees"] = c.sensibilite_donnees
        if c.cas_utilisation is not None:
            d["cas_utilisation"] = c.cas_utilisation
        if c.description_cas_utilisation is not None:
            d["description_cas_utilisation"] = c.description_cas_utilisation
        if c.premiere_action_48h is not None:
            d["premiere_action_48h"] = c.premiere_action_48h
        if c.mode_execution is not None:
            d["mode_execution"] = c.mode_execution
        if c.secteur is not None:
            d["secteur"] = c.secteur
        if c.declencheurs_typiques is not None:
            d["declencheurs_typiques"] = c.declencheurs_typiques
        out.append(d)
    return out


def _build_suggested_cases(
    ids: list[str],
    full_contents: list[str],
    case_extras: list[dict[str, str | None]] | None = None,
) -> list[SuggestedCase]:
    n = min(len(ids), len(full_contents))
    rows: list[SuggestedCase] = []
    for i in range(n):
        ex = case_extras[i] if case_extras and i < len(case_extras) else {}
        
        # Generate parcours URL for each case
        parcours_info = build_parcours_info(ids[i])
        
        rows.append(
            SuggestedCase(
                id=ids[i],
                content=full_contents[i],
                case_hash=parcours_info.get("case_hash"),
                parcours_url=parcours_info.get("parcours_url"),
                parcours_cta_label=parcours_info.get("cta_label"),
                effort=ex.get("effort"),
                prerequis_donnees=ex.get("prerequis_donnees"),
                guardrails=ex.get("guardrails"),
                questions_qualification=ex.get("questions_qualification"),
                sensibilite_donnees=ex.get("sensibilite_donnees"),
                cas_utilisation=ex.get("cas_utilisation"),
                description_cas_utilisation=ex.get("description_cas_utilisation"),
                premiere_action_48h=ex.get("premiere_action_48h"),
                mode_execution=ex.get("mode_execution"),
                secteur=ex.get("secteur"),
                declencheurs_typiques=ex.get("declencheurs_typiques"),
            )
        )
    return rows


def _append_parcours_links_to_answer(
    answer: str,
    suggested_cases: list[SuggestedCase] | None,
    pending_use_case_id: str | None = None,
    pending_case_index: int | None = None,
) -> str:
    """
    Garantit qu'au moins un lien parcours est visible dans le texte final.
    - Si un cas précis est ciblé (pending_use_case_id / pending_case_index), on ajoute ce lien.
    - Sinon, on ajoute le lien du 1er cas suggéré.
    """
    text = (answer or "").strip()
    if not text or not suggested_cases:
        return answer
    # Idempotence : si un pitch parcours (bloc "Passez à l'action") est déjà présent,
    # ne pas en rajouter un second. Couvre le cas où _build_niveau2_detail_payload a déjà
    # ajouté le suffixe côté haystack_rag, puis où cette fonction est rappelée sur la
    # réponse pré-construite (source du bloc dupliqué constaté en prod).
    if PARCOURS_PITCH_SENTINEL in text:
        return answer
    if ("http://" in text or "https://" in text) and ("/action/" in text or "/action-" in text):
        return answer

    target: SuggestedCase | None = None
    if pending_use_case_id:
        target = next((c for c in suggested_cases if c.id == pending_use_case_id), None)
    elif pending_case_index is not None and 0 <= pending_case_index < len(suggested_cases):
        target = suggested_cases[pending_case_index]
    else:
        target = suggested_cases[0]

    parcours_url = (target.parcours_url or "").strip() if target else ""
    if not parcours_url or parcours_url in text:
        return answer

    return text + get_parcours_pitch()["message_suffix"]


def _sanitize_answer_text(answer: str) -> str:
    text = (answer or "").strip()
    if not text:
        return answer
    text = _strip_repeated_welcome(text)
    text = re.sub(r"\(\s*UC-\d{3,5}\s*\)", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^\s*UC-\d{3,5}\s*[—\-:]\s*", "", text, flags=re.IGNORECASE | re.MULTILINE)
    text = _UC_CODE_RE.sub("", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _align_level1_list_with_selectable_cases(answer: str, selectable_count: int) -> str:
    """
    Empêche tout décalage UX entre les cas affichés et les cas réellement sélectionnables.
    Si le modèle affiche plus de cas numérotés que `selectable_count`, on tronque
    strictement la liste au nombre de cas réellement disponibles.
    """
    text = (answer or "").strip()
    if not text or selectable_count <= 0:
        return answer
    if "Souhaitez-vous approfondir l’un de ces cas" not in text:
        return answer

    # Isoler la zone "liste de cas" avant la question de clôture
    closing_match = re.search(
        r"(?is)(?:«\s*)?souhaitez[- ]vous approfondir l.?un de ces cas",
        text,
    )
    list_part = text[: closing_match.start()].rstrip() if closing_match else text
    closing_part = text[closing_match.start() :].strip() if closing_match else ""

    case_block_re = re.compile(
        r"(?ms)^\s*[1-9]\d*\.\s+\S.*?(?=^\s*[1-9]\d*\.\s+\S|\Z)"
    )
    blocks = list(case_block_re.finditer(list_part))
    if len(blocks) <= selectable_count:
        return answer

    prefix = list_part[: blocks[0].start()].rstrip()
    kept_blocks = [m.group(0).rstrip() for m in blocks[:selectable_count]]
    trimmed_list = "\n\n".join(kept_blocks).strip()
    rebuilt_main = "\n\n".join(part for part in (prefix, trimmed_list) if part).strip()

    if closing_part:
        return f"{rebuilt_main}\n\n{closing_part}".strip()
    return rebuilt_main


def _looks_like_detail_answer(answer: str) -> bool:
    text = (answer or "").lower()
    detail_markers = (
        "nom du cas",
        "niveau d'effort",
        "ce qu'il vous faut pour démarrer",
        "première action",
        "première étape",
        "point de vigilance",
    )
    return any(marker in text for marker in detail_markers)


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest, http_request: Request):
    """
    Envoie un message au chatbot.
    « ok / vas-y / oui » exécute l'action en attente (ex. détailler le cas) si pending_action est renvoyé.
    """
    settings = get_settings()
    history = [{"role": m.role, "content": m.content} for m in request.history]
    session_id = http_request.headers.get("X-Session-Id") or http_request.headers.get("x-session-id")
    try:
        if settings.use_rag:
            last = _last_suggested_cases_to_dicts(request)
            (
                answer,
                sources,
                suggested_case_ids,
                full_contents,
                case_extras,
                pending_action,
                pending_use_case_id,
                pending_case_index,
                selected_domain_code,
                selected_sector,
                selected_intention,
            ) = query_rag_haystack(
                request.message,
                history,
                last_suggested_cases=last,
                pending_action=request.pending_action,
                pending_use_case_id=request.pending_use_case_id,
                selected_domain_code=request.selected_domain_code,
                selected_sector=request.selected_sector,
                selected_intention=request.selected_intention,
            )
            suggested_cases = (
                _build_suggested_cases(suggested_case_ids, full_contents, case_extras) if full_contents else None
            )
            answer = _append_parcours_links_to_answer(
                answer,
                suggested_cases,
                pending_use_case_id=pending_use_case_id,
                pending_case_index=pending_case_index,
            )
            answer = _align_level1_list_with_selectable_cases(answer, len(suggested_cases or []))
            answer = _sanitize_answer_text(answer)
            track_backend_chat_event(
                event_name="backend_chat_response",
                session_id=session_id,
                use_rag=settings.use_rag,
                suggested_cases_count=len(suggested_cases or []),
                has_pending_action=bool(pending_action),
                has_error=False,
            )
            return ChatResponse(
                answer=answer,
                sources=sources,
                suggested_case_ids=suggested_case_ids,
                suggested_cases=suggested_cases,
                pending_action=pending_action,
                pending_use_case_id=pending_use_case_id,
                pending_case_index=pending_case_index,
                selected_domain_code=selected_domain_code,
                selected_sector=selected_sector,
                selected_intention=selected_intention,
            )
        answer = chat_simple(request.message, history)
        track_backend_chat_event(
            event_name="backend_chat_response",
            session_id=session_id,
            use_rag=settings.use_rag,
            suggested_cases_count=0,
            has_pending_action=False,
            has_error=False,
        )
        return ChatResponse(answer=answer, sources=[])
    except Exception as e:
        track_backend_chat_event(
            event_name="backend_chat_error",
            session_id=session_id,
            use_rag=settings.use_rag,
            suggested_cases_count=0,
            has_pending_action=False,
            has_error=True,
        )
        raise HTTPException(status_code=500, detail=f"Erreur chat: {str(e)}")


def _stream_chat(request: ChatRequest, session_id: str | None):
    settings = get_settings()
    history = [{"role": m.role, "content": m.content} for m in request.history]
    try:
        if settings.use_rag:
            last = _last_suggested_cases_to_dicts(request)
            (
                prompt_text,
                sources,
                suggested_case_ids,
                full_contents,
                case_extras,
                selected_domain_code,
                selected_sector,
                selected_intention,
                niveau2_prebuilt,
                selected_parcours_url,
                selected_parcours_cta_label,
            ) = get_rag_prompt_and_sources(
                request.message,
                history,
                last_suggested_cases=last,
                pending_action=request.pending_action,
                pending_use_case_id=request.pending_use_case_id,
                selected_domain_code=request.selected_domain_code,
                selected_sector=request.selected_sector,
                selected_intention=request.selected_intention,
            )
            suggested_cases = _build_suggested_cases(suggested_case_ids, full_contents, case_extras)
            _record_usage_stats(request, selected_domain_code, suggested_cases, niveau2_prebuilt)
            niveau2_prebuilt = _append_parcours_links_to_answer(
                niveau2_prebuilt,
                suggested_cases,
                pending_use_case_id=request.pending_use_case_id,
                pending_case_index=None,
            )
            if niveau2_prebuilt:
                yield _sse_line({"t": _sanitize_answer_text(niveau2_prebuilt)})
            else:
                streamed_chunks: list[str] = []
                for chunk in stream_prompt(prompt_text):
                    streamed_chunks.append(chunk)
                streamed_answer = _sanitize_answer_text("".join(streamed_chunks))
                if _looks_like_detail_answer(streamed_answer):
                    streamed_answer = _append_parcours_links_to_answer(
                        streamed_answer,
                        suggested_cases,
                        pending_use_case_id=request.pending_use_case_id,
                        pending_case_index=None,
                    )
                streamed_answer = _align_level1_list_with_selectable_cases(
                    streamed_answer, len(suggested_cases or [])
                )
                if streamed_answer:
                    yield _sse_line({"t": streamed_answer})
            done_payload = {
                "done": True,
                "sources": sources,
                "suggested_case_ids": suggested_case_ids,
                "suggested_cases": [c.model_dump(exclude_none=True) for c in suggested_cases],
                "selected_domain_code": selected_domain_code,
                "selected_sector": selected_sector,
                "selected_intention": selected_intention,
                # Preserve the request selection so the frontend can attach the
                # parcours CTA to the exact case on detail responses.
                "pending_action": request.pending_action,
                "pending_use_case_id": request.pending_use_case_id,
                "pending_case_index": None,
                # Bouton parcours AUTORITATIF : dès qu'un cas est réellement sélectionné
                # (réponse détail), le backend fournit l'URL + le libellé exacts. Le frontend
                # affiche le bouton directement à partir de ces champs, sans deviner le cas.
                "parcours_url": selected_parcours_url,
                "parcours_cta_label": selected_parcours_cta_label,
            }
            track_backend_chat_event(
                event_name="backend_chat_stream_done",
                session_id=session_id,
                use_rag=settings.use_rag,
                suggested_cases_count=len(suggested_cases or []),
                has_pending_action=False,
                has_error=False,
            )
            yield _sse_line(done_payload)
        else:
            for chunk in chat_simple_stream(request.message, history):
                yield _sse_line({"t": chunk})
            track_backend_chat_event(
                event_name="backend_chat_stream_done",
                session_id=session_id,
                use_rag=settings.use_rag,
                suggested_cases_count=0,
                has_pending_action=False,
                has_error=False,
            )
            yield _sse_line({"done": True, "sources": []})
    except Exception as e:
        track_backend_chat_event(
            event_name="backend_chat_stream_error",
            session_id=session_id,
            use_rag=settings.use_rag,
            suggested_cases_count=0,
            has_pending_action=False,
            has_error=True,
        )
        yield _sse_line({"error": str(e)})


@router.post("/stream")
def chat_stream(request: ChatRequest, http_request: Request):
    """
    Envoie un message et stream la réponse (SSE). Chaque événement : data: {"t": "fragment"}.
    Fin : data: {"done": true, "sources": [...]}.
    """
    session_id = http_request.headers.get("X-Session-Id") or http_request.headers.get("x-session-id")
    return StreamingResponse(
        _stream_chat(request, session_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
