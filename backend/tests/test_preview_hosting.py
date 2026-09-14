"""Cloud boundaries with synthetic repositories and mocked SDKs; no Azure calls."""

import asyncio
import os
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace
from typing import get_type_hints
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

from app.preview import create_app
from app.preview_hosting import HostingPolicy, MAX_BODY_BYTES, MAX_INFLIGHT, PreviewBoundary, application_url
from app.preview_parcours import ParcoursRenderer
from app.preview_public_rag import API_VERSION, ENDPOINT, ExistingAzure
from app.preview_repository import SyntheticRepository
from tests.test_preview_parcours import PublishedShapeRepository, selected
from tests.test_preview_protocol import envelope

BACKEND = "https://avoulia-backend--qual-20260913-r1.purpleocean-980317d1.francecentral.azurecontainerapps.io"
FRONTEND = "https://avoulia-frontend--qual-20260913-r1.purpleocean-980317d1.francecentral.azurecontainerapps.io"
APP_URL = "https://nricl.github.io/A-Vous-l-IA/preview"
CLOUD = {
    "AVIA_PREVIEW_HOSTING": "azure_test",
    "AVIA_PREVIEW_MODE": "public_pages",
    "AVIA_PREVIEW_ORIGIN": BACKEND,
    "AVIA_PREVIEW_FRONTEND_ORIGIN": FRONTEND,
    "AVIA_PREVIEW_APP_URL": APP_URL,
    "AVIA_PREVIEW_TRUSTED_PROXY_CIDRS": "10.20.0.0/24",
}
AUTH = {
    "AVIA_PREVIEW_AZURE_AUTH": "environment-key",
    "AZURE_OPENAI_ENDPOINT": ENDPOINT,
    "AZURE_OPENAI_API_KEY": "unit-test-not-a-credential",
    "AZURE_OPENAI_CHAT_DEPLOYMENT": "gpt-5-mini",
    "AZURE_OPENAI_EMBEDDING_DEPLOYMENT": "text-embedding-3-small",
    "AZURE_OPENAI_API_VERSION": API_VERSION,
}


class HostingTests(unittest.TestCase):
    def test_all_handler_annotations_resolve_on_eager_annotation_runtimes(self):
        with patch.dict(os.environ, {}, clear=True):
            app = create_app(mode="synthetic")
        for route in app.routes:
            if hasattr(route, "endpoint"):
                get_type_hints(route.endpoint)
        for handler in app.exception_handlers.values():
            get_type_hints(handler)

    def cloud_app(self):
        with patch.dict(os.environ, CLOUD, clear=True), patch.object(ParcoursRenderer, "_load") as load:
            load.return_value.load_template.return_value = Mock()
            return create_app(PublishedShapeRepository())

    def test_cross_site_pages_and_candidate_frontend_are_allowed(self):
        with TestClient(self.cloud_app(), base_url=BACKEND) as client:
            for origin in ("https://nricl.github.io", FRONTEND):
                headers = {"Origin": origin, "Sec-Fetch-Site": "cross-site"}
                response = client.get("/health", headers=headers)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.headers["access-control-allow-origin"], origin)
                self.assertEqual(response.headers["cache-control"], "no-store")
                self.assertEqual(response.headers["referrer-policy"], "no-referrer")
                self.assertEqual(response.headers["x-content-type-options"], "nosniff")
                preflight = client.options("/api/preview/v1/sessions", headers={
                    **headers, "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "content-type"})
                self.assertEqual(preflight.status_code, 200)

    def test_unexpected_origins_cross_site_without_origin_and_wrong_hosts_fail(self):
        with TestClient(self.cloud_app(), base_url=BACKEND) as client:
            for headers in (
                {"Origin": "https://evil.example"}, {"Origin": "null"}, {"Origin": ""},
                {"Origin": APP_URL}, {"Origin": "https://nricl.github.io.evil.example"},
                {"Sec-Fetch-Site": "cross-site"},
                {"Host": "avoulia-backend.purpleocean-980317d1.francecentral.azurecontainerapps.io"},
                {"Host": "evil.example", "X-Forwarded-Host": BACKEND.removeprefix("https://")},
            ):
                self.assertEqual(client.get("/health", headers=headers).status_code, 403, headers)
            response = client.get("/health", headers={"X-Forwarded-Host": "evil.example"})
            self.assertEqual(response.status_code, 200)  # Ignored, never used as the host.

    def test_original_peer_only_controls_forwarded_scheme(self):
        with patch.dict(os.environ, CLOUD, clear=True):
            policy = HostingPolicy.from_environment()
        scope = {
            "headers": [(b"host", BACKEND.removeprefix("https://").encode()),
                        (b"x-forwarded-proto", b"https"), (b"x-forwarded-for", b"10.20.0.4")],
            "scheme": "http", "client": ("198.51.100.6", 1000),
        }
        self.assertEqual(policy.rejection(scope), "https_required")
        scope["client"] = ("10.20.0.4", 1000)
        self.assertIsNone(policy.rejection(scope))
        scope["headers"][1] = (b"x-forwarded-proto", b"https,http")
        self.assertEqual(policy.rejection(scope), "https_required")
        scope["headers"].append((b"host", b"evil.example"))
        self.assertEqual(policy.rejection(scope), "invalid_headers")

    def test_pages_bearer_navigation_is_distinct_from_cross_origin_api_requests(self):
        with patch.dict(os.environ, CLOUD, clear=True):
            policy = HostingPolicy.from_environment()
        scope = {
            "method": "GET", "path": "/preview/parcours/" + "a" * 32,
            "scheme": "http", "client": ("10.20.0.4", 1000),
            "headers": [(b"host", BACKEND.removeprefix("https://").encode()),
                        (b"x-forwarded-proto", b"https"), (b"sec-fetch-site", b"cross-site"),
                        (b"sec-fetch-mode", b"navigate"), (b"sec-fetch-dest", b"document")],
        }
        self.assertIsNone(policy.rejection(scope))
        for changed in ({"method": "POST"}, {"path": "/api/preview/v1/sessions/" + "a" * 32},
                        {"path": "/health"}, {"path": "/preview/parcours/not-an-id"},
                        {"client": ("198.51.100.4", 1000)}):
            self.assertIsNotNone(policy.rejection({**scope, **changed}))
        self.assertEqual(policy.rejection({
            **scope, "headers": scope["headers"] + [(b"origin", b"https://evil.example")],
        }), "origin_not_allowed")

    def test_stale_bearer_link_is_still_rejected_after_navigation_is_allowed(self):
        app = self.cloud_app()
        state = selected(app.state.qualification)
        old_link = state["card"]["preview_parcours_url"]
        app.state.qualification.act(state["session_id"], envelope(state, "back", target="problem"))
        with TestClient(app, base_url=BACKEND) as client:
            response = client.get(old_link, headers={
                "Sec-Fetch-Site": "cross-site", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-Dest": "document",
            })
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()["error"], "stale_handoff")

    def test_cloud_misconfiguration_is_fail_closed(self):
        for changed in (
            {"AVIA_PREVIEW_ORIGIN": ""}, {"AVIA_PREVIEW_ORIGIN": "http://localhost:8767"},
            {"AVIA_PREVIEW_FRONTEND_ORIGIN": "*"}, {"AVIA_PREVIEW_APP_URL": ""},
            {"AVIA_PREVIEW_TRUSTED_PROXY_CIDRS": ""}, {"AVIA_PREVIEW_TRUSTED_PROXY_CIDRS": "*"},
            {"AVIA_PREVIEW_TRUSTED_PROXY_CIDRS": "0.0.0.0/0"},
            {"AVIA_PREVIEW_TRUSTED_PROXY_CIDRS": "::/0"}, {"AVIA_PREVIEW_MODE": "synthetic"},
        ):
            with self.subTest(changed=changed), patch.dict(os.environ, {**CLOUD, **changed}, clear=True):
                with self.assertRaises((ValueError, RuntimeError)):
                    create_app()
        with patch.dict(os.environ, CLOUD, clear=True), self.assertRaises(RuntimeError):
            create_app(SyntheticRepository())

    def test_local_defaults_remain_closed(self):
        with patch.dict(os.environ, {}, clear=True):
            app = create_app(mode="synthetic")
        with TestClient(app) as client:
            self.assertEqual(client.get("/health").status_code, 200)
            self.assertEqual(client.get("/health", headers={"Origin": "https://nricl.github.io"}).status_code, 403)
            self.assertEqual(client.get("/health", headers={"Sec-Fetch-Site": "cross-site"}).status_code, 403)
        with TestClient(app, base_url=BACKEND) as client:
            self.assertEqual(client.get("/health").status_code, 403)

    def test_public_mode_lock_consent_metadata_and_expiry(self):
        app = self.cloud_app()
        with TestClient(app, base_url=BACKEND) as client:
            for mode in ("SYNTHETIC", "PUBLIC_API"):
                self.assertEqual(client.get("/health", params={"source_mode": mode}).status_code, 403)
                self.assertEqual(client.post("/api/preview/v1/sessions", json={
                    "protocol_version": 1, "source_mode": mode, "external_consent": True}).status_code, 403)
            self.assertEqual(client.post("/api/preview/v1/sessions", json={"protocol_version": 1}).status_code, 403)
            state = client.post("/api/preview/v1/sessions", json={
                "protocol_version": 1, "source_mode": "PUBLIC_PAGES", "external_consent": True}).json()
            metadata = client.get("/health").json()
            self.assertEqual(metadata["allowed_source_modes"], ["PUBLIC_PAGES"])
            self.assertEqual(metadata["session_policy"]["ttl_seconds"], 3600)
            self.assertEqual(metadata["session_policy"]["max_sessions"], 128)
            app.state.qualification.ttl_seconds = 0
            self.assertEqual(client.get("/api/preview/v1/sessions/" + state["session_id"]).status_code, 404)

    def test_health_does_not_wait_for_user_lock_and_body_is_bounded(self):
        app = self.cloud_app()
        acquired, release = threading.Event(), threading.Event()

        def hold():
            with app.state.qualification.lock:
                acquired.set()
                release.wait(5)

        worker = threading.Thread(target=hold)
        worker.start()
        self.assertTrue(acquired.wait(2))
        try:
            with TestClient(app, base_url=BACKEND) as client:
                self.assertEqual(client.get("/health").status_code, 200)
                self.assertFalse(release.is_set())
                self.assertEqual(client.post("/api/preview/v1/sessions", content=b"x" * (MAX_BODY_BYTES + 1)).status_code, 413)
        finally:
            release.set()
            worker.join()

    def test_capacity_has_no_wait_queue_and_health_bypasses_saturation(self):
        with patch.dict(os.environ, CLOUD, clear=True):
            policy = HostingPolicy.from_environment()
        called = []

        async def app(scope, receive, send):
            called.append(scope["path"])
            await send({"type": "http.response.start", "status": 200, "headers": []})
            await send({"type": "http.response.body", "body": b"ok"})

        boundary = PreviewBoundary(app, policy)
        boundary.inflight = MAX_INFLIGHT

        async def request(path):
            sent = []
            async def send(message):
                sent.append(message)
            async def receive():
                return {"type": "http.request", "body": b""}
            await boundary({"type": "http", "method": "GET", "path": path, "scheme": "https",
                            "headers": [(b"host", BACKEND.removeprefix("https://").encode())]}, receive, send)
            return sent[0]["status"]
        self.assertEqual(asyncio.run(request("/api/preview/v1/sessions/x")), 429)
        self.assertEqual(asyncio.run(request("/health")), 200)
        self.assertEqual(called, ["/health"])

    def test_full_callback_path_validated_separately_from_origin(self):
        origins = {"https://nricl.github.io", FRONTEND}
        self.assertEqual(application_url(APP_URL, origins, cloud=True), APP_URL)
        renderer = ParcoursRenderer(None, FRONTEND, app_url=APP_URL, allowed_origins=origins, cloud=True)
        self.assertEqual(renderer.app_url, APP_URL)
        for value in (APP_URL + "?need=secret", APP_URL + "#secret", APP_URL + "/../evil",
                      APP_URL + "/%2e%2e", "https://evil.example/preview", "https://nricl.github.io"):
            with self.assertRaises(ValueError):
                application_url(value, origins, cloud=True)

    def test_missing_snapshot_fails_at_startup_before_sdk(self):
        with patch.dict(os.environ, {**CLOUD, "AVIA_PREVIEW_PUBLIC_CACHE": "missing-public-candidate"}, clear=True):
            with patch("app.preview_public_rag.AzureOpenAI") as sdk, self.assertRaises((ValueError, OSError)):
                create_app()
            sdk.assert_not_called()


class AzureAuthTests(unittest.TestCase):
    def test_environment_key_uses_actual_deployment_without_cli(self):
        with patch.dict(os.environ, {**CLOUD, **AUTH}, clear=True), \
                patch("app.preview_public_rag.tiktoken.get_encoding"), \
                patch("app.preview_public_rag.AzureOpenAI") as sdk, \
                patch("app.preview_public_rag.CHAT_BUDGET"), \
                patch("app.preview_public_rag.subprocess.run") as cli:
            azure = ExistingAzure(Path("unused-cache"))
            self.assertEqual(sdk.call_args.kwargs["api_key"], AUTH["AZURE_OPENAI_API_KEY"])
            self.assertNotIn("azure_ad_token_provider", sdk.call_args.kwargs)
            self.assertEqual(azure.chat_deployment, "gpt-5-mini")
            sdk.return_value.chat.completions.create.return_value = SimpleNamespace(
                usage=SimpleNamespace(prompt_tokens=1, completion_tokens=1), model="gpt-5-mini",
                choices=[SimpleNamespace(finish_reason="stop",
                                         message=SimpleNamespace(refusal=None, content='{"selected_ids":[]}'))])
            azure.select([{"role": "user", "content": "Fictitious unit input"}])
            self.assertEqual(sdk.return_value.chat.completions.create.call_args.kwargs["model"], "gpt-5-mini")
            sdk.return_value.embeddings.create.return_value = SimpleNamespace(
                usage=SimpleNamespace(total_tokens=1),
                data=[SimpleNamespace(index=0, embedding=[1.0] + [0.0] * 1535)])
            azure.embed(["Fictitious unit input"])
            self.assertEqual(sdk.return_value.embeddings.create.call_args.kwargs["model"], "text-embedding-3-small")
            with self.assertRaises(Exception):
                azure._azure_token()
            cli.assert_not_called()

    def test_explicit_chat_key_is_used_without_disclosing_values(self):
        values = {**CLOUD, **AUTH, "AZURE_OPENAI_API_KEY_CHAT": "different-unit-test-key"}
        with patch.dict(os.environ, values, clear=True), patch("app.preview_public_rag.tiktoken.get_encoding"), \
                patch("app.preview_public_rag.AzureOpenAI") as sdk:
            ExistingAzure(Path("unused-cache"))
            self.assertEqual(sdk.call_args_list[1].kwargs["api_key"], values["AZURE_OPENAI_API_KEY_CHAT"])
            sdk.side_effect = ValueError("different-unit-test-key")
            with self.assertRaises(RuntimeError) as error:
                ExistingAzure(Path("unused-cache"))
            self.assertNotIn("different-unit-test-key", str(error.exception))

    def test_required_config_missing_or_inconsistent_never_calls_cli_or_sdk(self):
        changes = [{name: ""} for name in AUTH]
        changes += [{"AZURE_OPENAI_ENDPOINT": "https://unapproved.example"},
                    {"AZURE_OPENAI_EMBEDDING_DEPLOYMENT": "different-vectors"},
                    {"AZURE_OPENAI_CHAT_DEPLOYMENT": "different-model"},
                    {"AZURE_OPENAI_API_VERSION": "unapproved"},
                    {"AZURE_OPENAI_AD_TOKEN": "unit-test-unwanted-auth-override"}]
        for changed in changes:
            with self.subTest(fields=list(changed)), patch.dict(os.environ, {**CLOUD, **AUTH, **changed}, clear=True), \
                    patch("app.preview_public_rag.AzureOpenAI") as sdk, \
                    patch("app.preview_public_rag.subprocess.run") as cli:
                with self.assertRaises(RuntimeError) as error:
                    ExistingAzure(Path("unused-cache"))
                self.assertNotIn(AUTH["AZURE_OPENAI_API_KEY"], str(error.exception))
                sdk.assert_not_called()
                cli.assert_not_called()
        with patch.dict(os.environ, CLOUD, clear=True), self.assertRaises(RuntimeError):
            ExistingAzure(Path("unused-cache"))

    def test_local_cli_token_remains_explicit_default(self):
        with patch.dict(os.environ, {}, clear=True), patch("app.preview_public_rag.tiktoken.get_encoding"), \
                patch("app.preview_public_rag.AzureOpenAI") as sdk:
            azure = ExistingAzure(Path("unused-cache"))
            self.assertEqual(azure.auth_mode, "cli-token")
            self.assertEqual(sdk.call_args.kwargs["azure_ad_token_provider"], azure._azure_token)
            self.assertNotIn("api_key", sdk.call_args.kwargs)


@unittest.skipUnless(os.environ.get("PARCOURS_SOURCE_ROOT"), "Explicit local renderer source required")
class CloudParcoursTests(unittest.TestCase):
    def test_backlink_retains_github_base_path_and_handoff_is_revision_bound(self):
        root = os.environ["PARCOURS_SOURCE_ROOT"]
        with patch.dict(os.environ, {**CLOUD, "PARCOURS_SOURCE_ROOT": root}, clear=True):
            app = create_app(PublishedShapeRepository())
        state = selected(app.state.qualification, "Contexte fictif", "marketing_visibilite")
        url = state["card"]["preview_parcours_url"]
        with TestClient(app, base_url=BACKEND) as client:
            response = client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertIn('href="' + APP_URL + '"', response.text)
            self.assertNotIn("Contexte", url)
            app.state.qualification.act(state["session_id"], envelope(state, "reset"))
            self.assertEqual(client.get(url).status_code, 409)


@unittest.skipUnless(os.environ.get("AVIA_PREVIEW_TEST_PUBLIC_CACHE") and os.environ.get("PARCOURS_SOURCE_ROOT"),
                     "Explicit pinned public cache and renderer source required")
class CandidateStartupTests(unittest.TestCase):
    def test_real_public_payload_factory_is_ready_without_network_or_cli(self):
        values = {**CLOUD, **AUTH, "AVIA_PREVIEW_PUBLIC_CACHE": os.environ["AVIA_PREVIEW_TEST_PUBLIC_CACHE"],
                  "PARCOURS_SOURCE_ROOT": os.environ["PARCOURS_SOURCE_ROOT"]}
        with patch.dict(os.environ, values, clear=True), patch("app.preview_public_rag.AzureOpenAI") as sdk, \
                patch("app.preview_public_rag.subprocess.run") as cli:
            with patch("socket.socket.connect", side_effect=AssertionError("No network allowed")):
                app = create_app()
            with TestClient(app, base_url=BACKEND) as client:
                source = client.get("/health", headers={"Origin": "https://nricl.github.io"}).json()["source"]
                self.assertEqual(source["case_count"], 1021)
                self.assertEqual(source["chat_deployment"], "gpt-5-mini")
                self.assertNotIn(AUTH["AZURE_OPENAI_API_KEY"], str(source))
                self.assertEqual(client.post("/api/preview/v1/sessions", json={
                    "protocol_version": 1, "external_consent": True}).status_code, 200)
            cli.assert_not_called()
            sdk.return_value.embeddings.create.assert_not_called()
            sdk.return_value.chat.completions.create.assert_not_called()
