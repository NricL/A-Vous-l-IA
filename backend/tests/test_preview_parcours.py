"""In-memory integration against an explicitly opted-in local renderer; no workbook."""

import copy
from dataclasses import replace
import hashlib
from html.parser import HTMLParser
import json
import os
import re
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.preview import create_app
from app.preview_parcours import ParcoursRenderer, PreviewPage, PUBLIC_STEP_TEMPLATES
from app.preview_protocol import ProtocolError, QualificationService
from app.preview_public_api import PUBLIC_ORIGIN
from app.preview_publicsnapshot import digest
from app.preview_repository import Case, DOMAINS, Retrieval, SyntheticRepository
from tests.test_preview_protocol import envelope


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.nodes, self.text, self.scripts, self.prompts = [], [], [], []
        self.current = None
        self.context = ""
        self.feed(source)
        # Match the browser's textarea first-newline rule.
        if self.context.startswith("\n"):
            self.context = self.context[1:]

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.nodes.append((tag, attrs))
        if tag == "textarea" and attrs.get("id") == "contexte-local":
            self.current = "context"
        elif tag == "script":
            self.scripts.append("")
            self.current = "script"
        elif tag == "pre":
            self.prompts.append("")
            self.current = "pre"

    def handle_endtag(self, tag):
        if tag in ("textarea", "script", "pre"):
            self.current = None

    def handle_data(self, text):
        self.text.append(text)
        if self.current == "context":
            self.context += text
        elif self.current == "script":
            self.scripts[-1] += text
        elif self.current == "pre":
            self.prompts[-1] += text


def selected(service, need="Préparer une newsletter", domain="marketing_visibilite"):
    state = service.create(need)
    state = service.act(state["session_id"], envelope(state, choice_id=domain))
    if state["phase"] == "sector":
        state = service.act(state["session_id"], envelope(state, choice_text=str(len(state["question"]["options"]))))
    state = service.act(state["session_id"], envelope(state, choice_id=state["question"]["options"][0]["id"]))
    if state["phase"] == "orientation":
        state = service.act(state["session_id"], envelope(state, "accept", choice_id=state["question"]["options"][0]["id"]))
    return service.act(state["session_id"], envelope(state, choice_id=state["question"]["options"][0]["id"]))


class PublishedShapeRepository(SyntheticRepository):
    """Synthetic text only, with the exact published-page schema; no source file or model."""

    def __init__(self):
        self._cases = {}
        for number in (9998, 9999):
            fields = {
                "title": f"SYNTHETIC : fiche de test {number}",
                "description": "Description SYNTHETIC, non issue d'un cas réel.\nConserver <A & B>.",
                "domaine_label": DOMAINS["marketing_visibilite"],
                "intention": "SYNTHETIC : préparer des fiches",
                "secteur": "Multi-sectoriel", "effort": "SYNTHETIC : effort",
                "sensibilite_donnees": "SYNTHETIC : sensibilité",
                "questions_qualification": ["Question SYNTHETIC : pour quel besoin ?", "Sans publication ?"],
                "prerequis_donnees": ["Élément SYNTHETIC : exemple autorisé", "Élément <&>"],
                "guardrails": ["Règle SYNTHETIC : ne pas envoyer.", "Règle SYNTHETIC : relire <&>."],
                "premiere_action_48h": "Action SYNTHETIC : produire une trame sans publication.",
                "mode_execution": None, "declencheurs_typiques": None,
            }
            case_id, case_hash = f"UC-{number}", f"synthetic{number}"
            url = f"{PUBLIC_ORIGIN}/action-{case_hash}.html"
            self._cases[case_id] = Case(
                case_id, "marketing_visibilite", fields["intention"], (fields["secteur"],),
                fields["title"], fields["description"], digest(fields), fields, url, url, case_hash,
            )
        self.revision = digest([case.source_hash for case in self._cases.values()])
        self.provenance = {
            "source_mode": "PUBLIC_PAGES", "catalogue_version": "Pages publiées Avoulia v4.6.1",
            "catalogue_revision": self.revision, "case_count": len(self._cases),
            "unavailable_fields": ["mode_execution", "declencheurs_typiques"],
            "parcours_mode": "Parcours actuel publié, pas un nouveau template.",
        }

    def search(self, problem, filters):
        ids = tuple(case.case_id for case in self._cases.values() if self.eligible(case, filters))
        return Retrieval(filters.as_dict(), ids, ids, "synthetic-public-shape-offline")

    def orient(self, problem, filters):
        raise AssertionError("No inference or orientation required for renderer tests")


class PreviewParcoursAvailabilityTests(unittest.TestCase):
    def test_missing_opt_in_is_visible_not_generic_fallback(self):
        with patch.dict(os.environ, {}, clear=True):
            app = create_app(mode="synthetic")
            service = app.state.qualification
            state = selected(service)
            response = TestClient(app).get(state["card"]["preview_parcours_url"])
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["error"], "parcours_unavailable")
        self.assertIn("AVIA_PREVIEW_PARCOURS_ROOT", response.json()["message"])
        self.assertIn("Aucun remplacement générique", response.json()["message"])
        self.assertEqual(response.headers["cache-control"], "no-store")

    def test_bad_root_and_missing_dependencies_fail_closed(self):
        service = QualificationService(SyntheticRepository())
        transfer = service.handoff(selected(service)["session_id"])
        for root in ("relative", "\\\\server\\share"):
            with self.assertRaises(ProtocolError) as caught:
                ParcoursRenderer(root, "http://127.0.0.1:4178").render(transfer)
            self.assertEqual(caught.exception.code, "parcours_unavailable")
        renderer = ParcoursRenderer("unused", "http://127.0.0.1:4178")
        with patch.object(renderer, "_load", side_effect=ModuleNotFoundError(name="pandas")):
            with self.assertRaises(ProtocolError) as caught:
                renderer.render(transfer)
        self.assertEqual(caught.exception.code, "parcours_dependency_missing")
        self.assertIn("pandas", str(caught.exception))

    def test_unselected_expired_and_changed_catalogue_are_rejected(self):
        app = create_app(mode="synthetic")
        client, service = TestClient(app), app.state.qualification
        state = service.create()
        self.assertEqual(client.get(f"/preview/parcours/{state['session_id']}").status_code, 422)
        state = selected(service)
        service.repository.revision = "changed"
        self.assertEqual(client.get(state["card"]["preview_parcours_url"]).status_code, 409)
        service.ttl_seconds = 0
        self.assertEqual(client.get(state["card"]["preview_parcours_url"]).status_code, 404)

    def test_incompatible_template_cannot_silently_drop_context(self):
        page = PreviewPage("Need", "hash")
        page.feed("<html><head></head><body>Missing context</body></html>")
        with self.assertRaises(ValueError):
            page.result()

    def test_old_parcours_and_handoff_links_cannot_return_a_new_case_or_context(self):
        app = create_app(mode="synthetic")
        client, service = TestClient(app), app.state.qualification
        old = selected(service)
        session_id = old["session_id"]
        state = service.act(session_id, envelope(old, "back", target="problem"))
        state = service.act(session_id, envelope(state, "describe", text="Préparer une fiche produit pour une nouvelle audience"))
        state = service.act(session_id, envelope(state, "accept", choice_id=state["question"]["options"][0]["id"]))
        state = service.act(session_id, envelope(state, choice_id=state["question"]["options"][0]["id"]))
        self.assertNotEqual(old["card"]["case_id"], state["card"]["case_id"])
        for url in (old["card"]["preview_parcours_url"], old["card"]["handoff_url"],
                f"/preview/context/{session_id}?revision={old['revision']}"):
            response = client.get(url)
            self.assertEqual(response.status_code, 409, response.text)
            self.assertEqual(response.json()["error"], "stale_handoff")
            self.assertNotIn("source_fields", response.json())
        current = client.get(state["card"]["handoff_url"])
        self.assertEqual(current.status_code, 200)
        self.assertEqual(current.json()["case_id"], state["card"]["case_id"])
        for path in (f"/preview/parcours/{session_id}", f"/api/preview/v1/sessions/{session_id}/handoff"):
            self.assertEqual(client.get(path).status_code, 422)

    def test_only_explicit_public_pages_or_synthetic_sources_can_render(self):
        service = QualificationService(PublishedShapeRepository())
        transfer = service.handoff(selected(service)["session_id"])
        for mode in ("PUBLIC_API", "General", "PRIVATE", "unknown", None):
            with self.subTest(mode=mode):
                candidate = copy.deepcopy(transfer)
                candidate["source"]["source_mode"] = mode
                with self.assertRaises(ProtocolError) as caught:
                    ParcoursRenderer(None, "http://127.0.0.1:4178").render(candidate)
                self.assertEqual(caught.exception.code, "unsupported_parcours_source")
                self.assertEqual(caught.exception.status, 422)

    def test_public_source_shape_identity_and_missing_mode_are_not_inferred(self):
        service = QualificationService(PublishedShapeRepository())
        original = service.handoff(selected(service)["session_id"])
        mutations = (
            lambda t: t["source_fields"].update(mode_execution="outil"),
            lambda t: t["source_fields"].update(declencheurs_typiques="déduit"),
            lambda t: t["source_fields"].update(classification="General"),
            lambda t: t["source_fields"].pop("prerequis_donnees"),
            lambda t: t["source_fields"].update(questions_qualification=None),
            lambda t: t["source"].update(catalogue_version="v4.6.2"),
            lambda t: t.update(case_id="General"),
            lambda t: t.update(case_hash="anotherhash"),
            lambda t: t.update(source_url=t["source_url"] + "?besoin=interdit"),
            lambda t: t.update(source_url="https://unverified.example/action-synthetic9998.html"),
            lambda t: t.update(catalogue_revision="changed"),
        )
        for mutate in mutations:
            candidate = copy.deepcopy(original)
            mutate(candidate)
            candidate["source_hash"] = digest(candidate["source_fields"])
            with self.subTest(candidate=candidate["source_hash"]):
                with self.assertRaises(ProtocolError) as caught:
                    ParcoursRenderer(None, "http://127.0.0.1:4178").render(candidate)
                self.assertEqual(caught.exception.code, "public_parcours_source_invalid")
                self.assertEqual(caught.exception.status, 422)
        changed = copy.deepcopy(original)
        changed["source_fields"]["guardrails"][0] += " modification"
        with self.assertRaises(ProtocolError) as caught:
            ParcoursRenderer(None, "http://127.0.0.1:4178").render(changed)
        self.assertEqual(caught.exception.code, "parcours_source_changed")
        self.assertEqual(caught.exception.status, 409)
        self.assertIn("Empreinte source", caught.exception.message)

    def test_public_card_handoff_and_context_stay_revision_bound(self):
        service = QualificationService(PublishedShapeRepository())
        app = create_app(repository=service.repository)
        service, client = app.state.qualification, TestClient(app)
        need = "SYNTHETIC : conserver ce besoin et ses exclusions, sans WhatsApp"
        old = selected(service, need)
        transfer = client.get(old["card"]["handoff_url"]).json()
        self.assertEqual(transfer["source_fields"], service.repository.get(old["card"]["case_id"]).source_fields)
        self.assertEqual(transfer["source_hash"], digest(transfer["source_fields"]))
        self.assertIsNone(transfer["source_fields"]["mode_execution"])
        self.assertIsNone(transfer["source_fields"]["declencheurs_typiques"])
        self.assertEqual(transfer["local_context"]["problem_original"], need)
        self.assertEqual(transfer["local_context"]["initial_need"], need)
        self.assertEqual(transfer["revision"], old["revision"])
        self.assertEqual(transfer["parcours_render_policy"], "public-neutral-v1")
        self.assertEqual(old["card"]["parcours_render_policy"], "public-neutral-v1")
        self.assertIn("localement", transfer["context_policy"])
        self.assertIn("Nouveau gabarit local", transfer["source"]["parcours_mode"])
        self.assertNotIn(need, old["card"]["preview_parcours_url"])
        self.assertEqual(old["card"]["preview_parcours_url"],
                         f"/preview/parcours/{old['session_id']}?revision={old['revision']}")
        state = service.act(old["session_id"], envelope(old, "back", target="results"))
        new = service.act(old["session_id"], envelope(state, choice_id=state["question"]["options"][1]["id"]))
        self.assertNotEqual(old["card"]["case_id"], new["card"]["case_id"])
        for url in (old["card"]["preview_parcours_url"], old["card"]["handoff_url"]):
            response = client.get(url, follow_redirects=False)
            self.assertEqual(response.status_code, 409)
            self.assertEqual(response.json()["error"], "stale_handoff")
        latest = client.get(new["card"]["handoff_url"]).json()
        self.assertEqual(latest["case_id"], new["card"]["case_id"])
        self.assertEqual(latest["source_url"], new["card"]["source_url"])

    def test_public_selected_source_cannot_be_remapped_within_same_revision(self):
        for change in ("case_hash", "source_hash", "source_url", "parcours_url", "fields"):
            with self.subTest(change=change):
                repository = PublishedShapeRepository()
                app = create_app(repository=repository)
                service, client = app.state.qualification, TestClient(app)
                state = selected(service)
                case = repository.get(state["card"]["case_id"])
                if change == "fields":
                    case.source_fields["title"] += " modification"
                else:
                    repository._cases[case.case_id] = replace(case, **{change: "changed"})
                for url in (state["card"]["handoff_url"], state["card"]["preview_parcours_url"]):
                    response = client.get(url, follow_redirects=False)
                    self.assertEqual(response.status_code, 409)
                    self.assertEqual(response.json()["error"], "selected_source_changed")


class PreviewParcoursIntegrationTests(unittest.TestCase):
    def setUp(self):
        root = os.environ.get("AVIA_PREVIEW_PARCOURS_ROOT") or os.environ.get("PARCOURS_SOURCE_ROOT")
        if not root:
            self.skipTest("Set AVIA_PREVIEW_PARCOURS_ROOT explicitly to run local renderer integration.")
        self.renderer = ParcoursRenderer(root, "http://127.0.0.1:4178")
        self.generator = self.renderer._load()
        for name in ("charge_base", "load_workbook"):
            guard = patch.object(self.generator, name, side_effect=AssertionError("No workbook access"))
            guard.start()
            self.addCleanup(guard.stop)
        guard = patch.object(self.generator.pd, "read_excel", side_effect=AssertionError("No workbook access"))
        guard.start()
        self.addCleanup(guard.stop)
        self.app = create_app(mode="synthetic", parcours_root=root)
        self.service = self.app.state.qualification
        self.client = TestClient(self.app)

    def test_all_sixteen_fixtures_render_six_steps_with_hash_of_complete_source(self):
        repository = self.service.repository
        self.assertEqual(repository.provenance["case_count"], 16)
        for case in repository._cases.values():
            with self.subTest(case=case.case_id):
                source = copy.deepcopy(case.source_fields)
                digest = hashlib.sha256(json.dumps(source, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
                self.assertEqual(digest, case.source_hash)
                transfer = {"case_id": case.case_id, "source_fields": source, "source_hash": digest,
                            "source": repository.provenance, "local_context": {"problem_original": "Contexte fictif"}}
                page = Page(self.renderer.render(transfer))
                self.assertEqual([attrs["data-etape"] for _, attrs in page.nodes if "data-etape" in attrs],
                                 ["1", "2", "3", "4", "5", "6"])
                self.assertEqual(page.context, "Contexte fictif")
                self.assertIn(case.title, "".join(page.text))
                self.assertIn(case.description, "".join(page.text))
                self.assertIn(source["parcours"]["guardrails"], page.prompts[-1])
                self.assertEqual(source, case.source_fields)
                source["parcours"]["guardrails"] += " changed"
                with self.assertRaises(ProtocolError):
                    self.renderer.render(transfer)

    def test_http_selected_case_to_six_steps_preserves_hostile_need_without_source_mutation(self):
        need = ('améliorer la pertinence des description produit pour l\'adapter à la GenZ, sans WhatsApp\n'
                '</textarea><script>window.pwned=1</script><img src=x onerror=alert(1)> & " < >')
        state = selected(self.service, need)
        self.assertEqual(state["card"]["case_id"], "SYN-PRODUCT")
        self.assertEqual(state["phase"], "terminal")
        self.assertEqual(state["question"]["options"], [])
        response = self.client.get(state["card"]["preview_parcours_url"], headers={"Origin": "http://127.0.0.1:8767"})
        self.assertEqual(response.status_code, 200, response.text)
        page = Page(response.text)
        self.assertEqual(page.context, need)
        self.assertIn("16 cas fictifs", "".join(page.text))
        self.assertIn("SYNTHÉTIQUE · NON PRODUCTION", response.text)
        self.assertFalse(any(tag in ("img", "link", "form") for tag, _ in page.nodes))
        self.assertEqual(len(page.scripts), 2)  # Theme and the original copy/progress script.
        self.assertNotIn(need, "".join(page.scripts))
        self.assertNotIn(need, page.prompts[-1])
        self.assertEqual(page.prompts[-1], self.generator.prompt_principal(
            self.service.repository.get("SYN-PRODUCT").source_fields["parcours"]))
        self.assertIn('href="http://127.0.0.1:4178/preview"', response.text)
        self.assertNotIn("fonts.googleapis", response.text)
        self.assertEqual(response.headers["cache-control"], "no-store")
        self.assertEqual(response.headers["referrer-policy"], "no-referrer")
        policy = response.headers["content-security-policy"]
        for rule in ("default-src 'self'", "connect-src 'none'", "form-action 'none'", "frame-ancestors 'none'"):
            self.assertIn(rule, policy)

    def test_eight_thousand_char_need_is_not_truncated_and_missing_fields_do_not_get_inferred(self):
        need = "\nPréparer une newsletter\n" + ("x" * 7900)
        transfer = self.service.handoff(selected(self.service, need)["session_id"])
        page = Page(self.renderer.render(transfer))
        self.assertEqual(page.context, need)
        self.assertEqual(next(attrs["maxlength"] for tag, attrs in page.nodes
                              if tag == "textarea" and attrs.get("id") == "contexte-local"), "8000")
        del transfer["source_fields"]["parcours"]["prereqs"]
        transfer["source_hash"] = hashlib.sha256(json.dumps(
            transfer["source_fields"], sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        with self.assertRaises(ProtocolError) as caught:
            self.renderer.render(transfer)
        self.assertEqual(caught.exception.code, "parcours_unavailable")

    def test_renderer_failure_is_an_explicit_unavailable_error(self):
        transfer = self.service.handoff(selected(self.service)["session_id"])
        with patch.object(self.generator, "load_template", side_effect=RuntimeError("Broken template")):
            with self.assertRaises(ProtocolError) as caught:
                self.renderer.render(transfer)
        self.assertEqual(caught.exception.code, "parcours_unavailable")
        self.assertIn("Aucun remplacement générique", str(caught.exception))


class PublicParcoursIntegrationTests(unittest.TestCase):
    def setUp(self):
        root = os.environ.get("AVIA_PREVIEW_PARCOURS_ROOT") or os.environ.get("PARCOURS_SOURCE_ROOT")
        if not root:
            self.skipTest("Set AVIA_PREVIEW_PARCOURS_ROOT explicitly to run local renderer integration.")
        self.renderer = ParcoursRenderer(root, "http://127.0.0.1:4178")
        self.generator = self.renderer._load()
        for name in ("charge_base", "load_workbook"):
            guard = patch.object(self.generator, name, side_effect=AssertionError("No workbook access"))
            guard.start()
            self.addCleanup(guard.stop)
        guard = patch.object(self.generator.pd, "read_excel", side_effect=AssertionError("No workbook access"))
        guard.start()
        self.addCleanup(guard.stop)
        self.app = create_app(repository=PublishedShapeRepository(), parcours_root=root)
        self.service, self.client = self.app.state.qualification, TestClient(self.app)

    def test_public_none_uses_only_explicit_neutral_presentation_and_verbatim_sources(self):
        need = "\nSYNTHETIC : améliorer les descriptions sans WhatsApp.\n</textarea><script>alert(1)</script><&>"
        transfer = self.service.handoff(selected(self.service, need)["session_id"])
        before = copy.deepcopy(transfer)
        with patch.object(self.generator, "render_page", wraps=self.generator.render_page) as render:
            rendered = self.renderer.render(transfer)
        page = Page(rendered)
        self.assertEqual(transfer, before)
        self.assertEqual(digest(transfer["source_fields"]), transfer["source_hash"])
        self.assertIsNone(render.call_args.args[0]["mode_execution"])
        self.assertEqual(render.call_args.args[4], {})
        self.assertEqual(render.call_args.kwargs["step_templates"], PUBLIC_STEP_TEMPLATES)
        self.assertIsNone(self.renderer.step_templates)
        self.assertEqual(page.context, need)
        self.assertEqual([attrs["data-etape"] for _, attrs in page.nodes if "data-etape" in attrs],
                         ["1", "2", "3", "4", "5", "6"])
        self.assertEqual(sum(int(n) * (60 if unit == "h" else 1)
                             for n, unit in re.findall(r'class="duree">(\d+) (min|h)</span>', rendered)), 132)
        self.assertIn("2h12 de travail actif estimé, hors test terrain", rendered)
        self.assertIn("Ce repère est indicatif", rendered)
        text = "".join(page.text)
        for field, value in transfer["source_fields"].items():
            if value is not None:
                for part in value if isinstance(value, list) else [value]:
                    self.assertIn(part, text, field)
        self.assertIn("2 cas réels issus des pages déjà publiées v4.6.1", text)
        self.assertIn("Nouveau gabarit local, textes source v4.6.1 conservés", text)
        self.assertIn("non publiés, donc inconnus", text)
        self.assertIn("choix de présentation neutre, pas une métadonnée métier", text)
        self.assertNotIn("16 cas fictifs", text)
        self.assertNotIn("v4.6.2", text)
        self.assertNotIn("SYNTHÉTIQUE · NON PRODUCTION", text)
        self.assertIn("temps habituel et temps total de l'essai", text)
        self.assertIn("une recette validée, un responsable et une prochaine tâche", text)
        self.assertFalse(any(tag in ("img", "link", "form", "iframe") for tag, _ in page.nodes))
        self.assertFalse(any(attrs.get("src") for _, attrs in page.nodes))
        self.assertTrue(all(not attrs.get("href") or attrs["href"].startswith(("#", "http://127.0.0.1:4178/preview"))
                            for _, attrs in page.nodes))
        self.assertEqual(len(page.scripts), 2)
        self.assertNotIn(need, "".join(page.scripts))
        self.assertNotIn(need, "\n".join(page.prompts))
        for prompt in page.prompts:
            for guard in transfer["source_fields"]["guardrails"]:
                self.assertIn(guard, prompt)
        self.assertIn("addEventListener('click'", page.scripts[-1])
        self.assertIn("contexte-local').value", page.scripts[-1])
        self.assertNotIn("fonts.googleapis", rendered)
        self.assertNotIn(transfer["source_url"], rendered)
        self.assertNotRegex("".join(page.scripts), r"\b(fetch|XMLHttpRequest|sendBeacon|WebSocket)\b")

    def test_public_http_renders_locally_without_redirect_and_retains_host_csp(self):
        need = "SYNTHETIC besoin exact </textarea><img src=x> sans publication"
        state = selected(self.service, need)
        with patch("urllib.request.OpenerDirector.open", side_effect=AssertionError("No network on parcours")):
            response = self.client.get(state["card"]["preview_parcours_url"], follow_redirects=False)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertNotIn("location", response.headers)
        self.assertEqual(Page(response.text).context, need)
        self.assertIn("PUBLIC_PAGES", response.text)
        self.assertEqual(response.headers["cache-control"], "no-store")
        self.assertEqual(response.headers["referrer-policy"], "no-referrer")
        for rule in ("default-src 'self'", "connect-src 'none'", "font-src 'none'",
                     "img-src 'none'", "form-action 'none'", "frame-ancestors 'none'"):
            self.assertIn(rule, response.headers["content-security-policy"])
        self.assertEqual(self.client.get(state["card"]["preview_parcours_url"],
                                        headers={"Origin": "https://untrusted.example"}).status_code, 403)


if __name__ == "__main__":
    unittest.main()
