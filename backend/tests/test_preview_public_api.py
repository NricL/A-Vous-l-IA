"""Contract tests with an explicit mock transport; no real catalogue claims."""

import copy
import unittest
import uuid
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.preview import create_app
from app.preview_protocol import ProtocolError, QualificationService
from app.preview_public_api import (
    NO_RESULTS, OBJECTIVE_PROMPT, PROBLEM_PROMPT, PUBLIC_ORIGIN, SECTOR_PROMPT,
    PublicAPIRepository, PublicChatTransport, public_parcours_url,
)
from app.preview_repository import DOMAINS, canonical_id


def envelope(state, action="choose", **fields):
    return {"protocol_version": 1, "catalogue_revision": state["catalogue_revision"],
            "revision": state["revision"], "question_id": state["question"]["id"],
            "request_id": uuid.uuid4().hex, "action": action, **fields}


class MockPublicChat:
    def __init__(self):
        self.calls = []
        self.codes = list(DOMAINS)
        self.labels = list(DOMAINS.values())
        self.objectives = ["Objectif public simulé A", "Objectif public simulé B"]
        self.no_results = False
        self.error = False
        self.bad_row = {}
        self.bad_echo = {}
        self.non_result = False
        self.answer_suffix = ""

    def __call__(self, payload):
        self.calls.append(copy.deepcopy(payload))
        if self.error:
            raise OSError("mock network error")
        response = {
            "selected_domain_code": payload.get("selected_domain_code"),
            "selected_sector": payload.get("selected_sector"),
            "selected_intention": payload.get("selected_intention"),
            "suggested_case_ids": [], "suggested_cases": None,
        }
        message = payload["message"]
        code = payload.get("selected_domain_code")
        if message == "Bonjour":
            response["answer"] = "Dans quel domaine souhaitez-vous agir en priorité ?\n" + "\n".join(
                f"{n}. {label}" for n, label in enumerate(self.labels, 1))
        elif code is None:
            response["selected_domain_code"] = self.codes[int(message) - 1]
            response["answer"] = SECTOR_PROMPT + " vous opérez ?\n1. Industrie\n2. Autre / Non spécifique"
        elif payload.get("selected_intention"):
            response.update(self.bad_echo)
            if self.non_result:
                response["answer"] = "Réponse libre non reconnue."
            elif self.no_results:
                response["answer"] = NO_RESULTS
            else:
                row = {
                    "id": "UC-9999", "cas_utilisation": "Titre de test, non catalogue",
                    "description_cas_utilisation": "Description du transport simulé, non catalogue.",
                    "secteur": "Multi-sectoriel", "case_hash": "mock123456",
                    "parcours_url": PUBLIC_ORIGIN + "/action-mock123456.html",
                    "content": " | ".join(["UC-9999", code, self.objectives[0], "Test", "Multi-sectoriel",
                                            "Titre de test, non catalogue", "Description de test."]),
                    "unknown_private_audit": "must not be copied",
                }
                row.update(self.bad_row)
                response.update(answer="Texte généré, jamais utilisé comme source." + self.answer_suffix,
                                suggested_case_ids=["UC-9999"], suggested_cases=[row])
        elif payload.get("selected_sector") is not None:
            response.update(answer=PROBLEM_PROMPT, selected_intention="observed-token-A")
        else:
            response["selected_sector"] = "Industrie" if message == "1" else "Autre / Non spécifique"
            response["answer"] = OBJECTIVE_PROMPT + "\n" + "\n".join(
                f"{n}. {label}" for n, label in enumerate(self.objectives, 1))
        return response


class PublicRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.api = MockPublicChat()
        self.repository = PublicAPIRepository(self.api)
        self.service = QualificationService(self.repository)
        self.state = self.service.create()

    def act(self, action="choose", **fields):
        self.state = self.service.act(self.state["session_id"], envelope(self.state, action, **fields))
        return self.state

    def choose(self, index):
        return self.act(choice_id=self.state["question"]["options"][index]["id"])

    def qualify(self, need=""):
        self.act(choice_id=self.state["question"]["options"][4]["id"], initial_need=need)
        self.choose(1)
        self.choose(0)

    def search(self, text="Texte de test sans publication ni envoi de messages."):
        self.qualify()
        return self.act("describe", text=text)

    def test_real_mode_has_source_label_ids_and_no_fixture_filler(self):
        options = self.state["question"]["options"]
        self.assertEqual(len(options), 14)
        self.assertEqual(options[4]["id"], canonical_id("domain", self.api.labels[4]))
        self.choose(4)
        self.assertEqual([item["label"] for item in self.state["question"]["options"]],
                         ["Industrie", "Autre / Non spécifique"])
        self.choose(1)
        self.assertEqual([item["label"] for item in self.state["question"]["options"]], self.api.objectives)
        self.assertEqual(self.state["question"]["options"][0]["id"],
                         canonical_id("objective", options[4]["id"], self.api.objectives[0]))

    def test_verbatim_query_real_observed_token_and_returned_source_only(self):
        text = "\n  Ma demande fictive, sans WhatsApp ; ni site web, ne rien inventer.  "
        self.search(text)
        sent = self.api.calls[-1]
        self.assertEqual(sent["message"], text)
        self.assertEqual(sent["history"], [])
        self.assertEqual(sent["selected_intention"], "observed-token-A")
        self.assertEqual(sent["selected_domain_code"], "marketing_visibilite")
        self.assertEqual(sent["selected_sector"], "Autre / Non spécifique")
        self.assertEqual(self.state["problem_original"], text)
        self.assertEqual(self.state["diagnostics"]["main"]["result_ids"], ["UC-9999"])
        self.assertEqual(self.state["diagnostics"]["main"]["details"]["candidate_scope"], "returned_cases_only")
        self.choose(0)
        transfer = self.service.handoff(self.state["session_id"], self.state["revision"])
        self.assertEqual(transfer["source_fields"]["mode_execution"], None)
        self.assertNotIn("unknown_private_audit", transfer["source_fields"])
        self.assertNotIn("content", transfer["source_fields"])
        self.assertNotIn("parcours", transfer["source_fields"])
        self.assertEqual(transfer["source_fields"]["description"], "Description du transport simulé, non catalogue.")
        self.assertIn("transmis", transfer["context_policy"])

    def test_empty_real_result_abstains_orientation_without_more_calls(self):
        self.api.no_results = True
        self.qualify()
        before = len(self.api.calls)
        self.act("describe", text="Demande fictive inconnue, sans modification.")
        self.assertEqual(len(self.api.calls) - before, 5)
        self.assertEqual(self.state["phase"], "results")
        self.assertEqual(self.state["question"]["options"], [])
        self.assertEqual(self.state["diagnostics"]["orientation"]["engine"], "public-orientation-unavailable")
        self.assertFalse(self.state["diagnostics"]["orientation"]["details"]["supported"])
        self.assertEqual(self.state["diagnostics"]["main"]["result_ids"], [])

    def test_network_failure_and_non_result_do_not_commit_or_fallback(self):
        self.qualify()
        before = copy.deepcopy(self.state)
        self.api.error = True
        with self.assertRaises(ProtocolError) as caught:
            self.act("describe", text="Besoin fictif.")
        self.assertEqual(caught.exception.code, "public_unavailable")
        self.assertEqual(self.service.read(before["session_id"]), before)
        self.api.error = False
        self.api.non_result = True
        with self.assertRaises(ProtocolError) as caught:
            self.act("describe", text="Besoin fictif.")
        self.assertEqual(caught.exception.code, "public_non_result")
        self.assertEqual(self.service.read(before["session_id"]), before)
        self.assertEqual(self.repository.provenance["case_count"], 0)

    def test_shifted_objective_menu_cannot_reinterpret_old_choice(self):
        self.qualify()
        before = len(self.api.calls)
        self.api.objectives.reverse()
        with self.assertRaises(ProtocolError) as caught:
            self.act("describe", text="Besoin fictif.")
        self.assertEqual(caught.exception.code, "public_source_changed")
        self.assertEqual(len(self.api.calls) - before, 3)
        self.assertEqual(self.repository.provenance["retrieval_calls"], 0)

    def test_shifted_domain_menu_cannot_reinterpret_first_domain_selection(self):
        old_question = copy.deepcopy(self.state)
        self.api.labels.reverse()
        with self.assertRaises(ProtocolError) as caught:
            self.choose(4)
        self.assertEqual(caught.exception.code, "public_source_changed")
        self.assertEqual(self.service.read(self.state["session_id"]), old_question)
        self.assertEqual(self.repository.provenance["retrieval_calls"], 0)

    def test_wrong_sector_or_domain_or_objective_is_rejected(self):
        self.qualify()
        for header in [
            "UC-9999 | production | Objectif public simulé A | Test | Multi-sectoriel | Titre de test, non catalogue | Test",
            "UC-9999 | marketing_visibilite | Mauvais objectif | Test | Multi-sectoriel | Titre de test, non catalogue | Test",
            "UC-9999 | marketing_visibilite | Objectif public simulé A | Test | Industrie | Titre de test, non catalogue | Test",
        ]:
            self.api.bad_row = {"content": header}
            with self.assertRaises(ProtocolError):
                self.act("describe", text="Besoin fictif.")
        self.api.bad_row = {}
        self.api.bad_echo = {"selected_sector": "Industrie"}
        with self.assertRaises(ProtocolError) as caught:
            self.act("describe", text="Besoin fictif.")
        self.assertEqual(caught.exception.code, "public_filter_changed")
        self.assertEqual(self.repository.provenance["case_count"], 0)

    def test_stale_actions_duplicate_receipts_and_handoff_remain_guarded(self):
        self.search()
        action = envelope(self.state, choice_id="UC-9999")
        selected = self.service.act(self.state["session_id"], action)
        before = len(self.api.calls)
        self.assertEqual(self.service.act(self.state["session_id"], action), selected)
        self.assertEqual(selected["phase"], "terminal")
        self.assertEqual(selected["question"]["options"], [])
        self.assertNotIn("describe", selected["allowed_actions"])
        self.assertEqual(len(self.api.calls), before)
        with self.assertRaises(ProtocolError):
            self.service.handoff(selected["session_id"], selected["revision"] - 1)
        self.state = selected
        self.act("back", target="results")
        with self.assertRaises(ProtocolError):
            self.service.handoff(selected["session_id"], selected["revision"])

    def test_health_and_absent_consent_do_not_issue_external_requests(self):
        api = MockPublicChat()
        repository = PublicAPIRepository(api)
        client = TestClient(create_app(repository))
        self.assertEqual(client.get("/health").json()["source"]["source_mode"], "PUBLIC_API")
        self.assertEqual(api.calls, [])
        denied = client.post("/api/preview/v1/sessions", json={"protocol_version": 1})
        self.assertEqual(denied.status_code, 403)
        self.assertEqual(api.calls, [])
        accepted = client.post("/api/preview/v1/sessions", json={"protocol_version": 1, "external_consent": True})
        self.assertEqual(accepted.status_code, 200)
        self.assertEqual(len(api.calls), 1)

    def test_terminal_redirect_is_revision_guarded_and_contains_no_user_context(self):
        self.search("Contexte strictement local dans le lien, sans pièce jointe.")
        self.choose(0)
        client = TestClient(create_app(self.repository))
        client.app.state.qualification.sessions = self.service.sessions
        path = self.state["card"]["preview_parcours_url"]
        response = client.get(path, follow_redirects=False)
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers["location"], PUBLIC_ORIGIN + "/action-mock123456.html")
        self.assertEqual(response.headers["referrer-policy"], "no-referrer")
        self.assertEqual(response.headers["cache-control"], "no-store")
        self.act("back", target="results")
        self.assertEqual(client.get(path, follow_redirects=False).status_code, 409)

    def test_public_urls_are_strictly_bounded_without_query_or_redirect_hosts(self):
        for value in [
            "https://evil.example/action-mock123456.html", PUBLIC_ORIGIN + "/action-mock123456.html?context=secret",
            PUBLIC_ORIGIN + "/action-mock123456.html#secret", PUBLIC_ORIGIN + "/action-other.html",
            PUBLIC_ORIGIN.replace("https:", "http:") + "/action-mock123456.html",
            PUBLIC_ORIGIN + "/../action-mock123456.html",
        ]:
            with self.assertRaises(ProtocolError):
                public_parcours_url(value, "mock123456")

    def test_unknown_mode_never_enables_real_api(self):
        with self.assertRaises(RuntimeError):
            create_app(mode="public")

    def test_transport_is_fixed_origin_post_no_credentials_no_retry(self):
        transport = PublicChatTransport()
        with patch.object(transport.opener, "open", side_effect=TimeoutError) as opened:
            with self.assertRaises(ProtocolError):
                transport({"message": "fictif", "history": []})
        self.assertEqual(opened.call_count, 1)
        request = opened.call_args.args[0]
        self.assertEqual(request.full_url, PUBLIC_ORIGIN + "/api/v1/chat")
        self.assertEqual(request.get_method(), "POST")
        self.assertNotIn("Authorization", dict(request.header_items()))


if __name__ == "__main__":
    unittest.main()
