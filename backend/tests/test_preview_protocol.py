import copy
import json
import unittest
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.preview import create_app
from app.preview_protocol import PROMPTS, ProtocolError, QualificationService
from app.preview_repository import DOMAINS, OTHER_SECTOR, Retrieval, SyntheticRepository

GENZ_NEED = "améliorer la pertinence des description produit pour l'adapter à la GenZ"


def envelope(state, action="choose", **kwargs):
    return {
        "protocol_version": 1, "request_id": uuid.uuid4().hex,
        "revision": state["revision"], "question_id": state["question"]["id"],
        "catalogue_revision": state["catalogue_revision"], "action": action, **kwargs,
    }


class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.repository = SyntheticRepository()
        self.service = QualificationService(self.repository)
        self.state = self.service.create()

    def act(self, action="choose", **kwargs):
        self.state = self.service.act(self.state["session_id"], envelope(self.state, action, **kwargs))
        return self.state

    def choose_label(self, label):
        matches = [option for option in self.state["question"]["options"] if option["label"] == label]
        self.assertEqual(len(matches), 1)
        return self.act(choice_id=matches[0]["id"])

    def marketing(self, need=GENZ_NEED):
        self.act(choice_id="marketing_visibilite", initial_need=need)
        self.choose_label(OTHER_SECTOR)
        self.choose_label("Créer des contenus marketing")
        return self.state

    def test_first_question_has_all_fourteen_canonical_domains(self):
        self.assertEqual(self.state["phase"], "domain")
        self.assertEqual([option["id"] for option in self.state["question"]["options"]], list(DOMAINS))
        self.assertEqual(len(self.state["question"]["options"]), 14)
        for domain in DOMAINS:
            state = self.service.create()
            result = self.service.act(state["session_id"], envelope(state, choice_id=domain))
            expected = "sector" if self.repository.sectors(domain) else "objective"
            self.assertEqual(result["phase"], expected, domain)

    def test_question_rephrasing_cannot_change_identity_or_transition(self):
        changed = QualificationService(self.repository, prompts={"domain": "Votre priorité métier ?"})
        clone = copy.deepcopy(self.service.sessions[self.state["session_id"]])
        changed.sessions[clone.session_id] = clone
        other = changed._snapshot(clone)
        self.assertEqual(self.state["question"]["id"], other["question"]["id"])
        self.assertNotEqual(self.state["question"]["prompt"], other["question"]["prompt"])
        result = changed.act(clone.session_id, envelope(self.state, choice_id="production"))
        self.assertEqual(result["confirmed"]["domain"], "production")

    def test_unknown_ambiguous_labels_numbers_and_negation_do_not_select(self):
        for unknown in ("1", "oui", "non", "Marketing", "marketing_visibilite ou production", "BTP", "absent"):
            before = self.service.read(self.state["session_id"])
            with self.assertRaises(ProtocolError) as caught:
                self.act(choice_id=unknown)
            self.assertEqual(caught.exception.code, "unknown_choice")
            self.assertEqual(self.service.read(self.state["session_id"]), before)

    def test_text_choices_map_only_current_numbers_exact_labels_or_curated_aliases(self):
        for text in ("5", "Marketing & visibilité", "  MARKETING & VISIBILITE  ", "marketing", "5. Marketing"):
            self.act("reset")
            self.act(choice_text=text)
            self.assertEqual(self.state["confirmed"]["domain"], "marketing_visibilite")
            self.act(choice_text=str(len(self.state["question"]["options"])))
            self.assertEqual(self.state["confirmed"]["sector"], OTHER_SECTOR)
            self.act(choice_text="Créer des contenus marketing")
            self.assertEqual(self.state["phase"], "problem")
            self.act("describe", text="Préparer une newsletter")
            self.act(choice_text="1")
            self.assertEqual(self.state["card"]["case_id"], "SYN-MARKETING")
            self.assertEqual(self.state["question"]["options"], [])

    def test_text_unknown_ambiguous_conflicting_or_stale_is_transactional(self):
        for text in ("0", "15", "5 production", "5. production", "marketing ou production",
                     "je pense marketing", "oui", "non", "visibilite", "5 et 12", ""):
            before = self.service.read(self.state["session_id"])
            with self.assertRaises(ProtocolError):
                self.act(choice_text=text)
            self.assertEqual(self.service.read(self.state["session_id"]), before)
        with self.assertRaises(ProtocolError) as caught:
            self.act(choice_text="5", choice_id="production")
        self.assertEqual(caught.exception.code, "conflicting_choice")
        stale = envelope(self.state, choice_text="5")
        self.act(choice_text="5")
        with self.assertRaises(ProtocolError) as caught:
            self.service.act(self.state["session_id"], stale)
        self.assertEqual(caught.exception.code, "stale_question")
        self.act("back", target="domain")
        with self.assertRaises(ProtocolError):
            self.service.act(self.state["session_id"], stale)
        current = self.service.sessions[self.state["session_id"]]
        current.issued["question"]["options"][0]["label"] = "Marketing"
        with self.assertRaises(ProtocolError):
            self.act(choice_text="marketing")

    def test_sector_optional_and_multi_sector_eligibility(self):
        self.act(choice_id="direction_strategie")
        self.assertEqual(self.state["phase"], "objective")
        self.assertIsNone(self.state["confirmed"]["sector"])
        self.act("reset")
        self.act(choice_id="marketing_visibilite")
        self.choose_label(OTHER_SECTOR)
        labels = [item["label"] for item in self.state["question"]["options"]]
        self.assertIn("Créer des contenus marketing", labels)
        self.assertNotIn("Préparer une annonce de menu fictive", labels)
        self.act("back", target="sector")
        self.choose_label("Restauration")
        self.assertIn("Préparer une annonce de menu fictive",
                      [item["label"] for item in self.state["question"]["options"]])

    def test_canonical_objective_and_sector_ids_not_positions_or_display_labels(self):
        self.act(choice_id="marketing_visibilite")
        sector_ids = {item["label"]: item["id"] for item in self.state["question"]["options"]}
        self.choose_label(OTHER_SECTOR)
        objective = self.state["question"]["options"][0]
        self.assertTrue(objective["id"].startswith("objective:"))
        self.assertNotEqual(objective["id"], objective["label"])
        self.act("back", target="domain")
        self.act(choice_id="production")
        self.assertEqual(sector_ids[OTHER_SECTOR],
                         next(item["id"] for item in self.state["question"]["options"] if item["label"] == OTHER_SECTOR))

    def test_preserve_initial_need_and_automatically_search_after_objective(self):
        text = GENZ_NEED + ", sans WhatsApp ni saisonnalité, pas de site web."
        self.marketing(text)
        self.assertEqual(self.state["initial_need"], text)
        self.assertEqual(self.state["problem_original"], text)
        self.assertEqual(self.state["phase"], "orientation")
        self.assertEqual(self.state["diagnostics"]["main"]["result_ids"], [])
        self.assertEqual(self.state["diagnostics"]["main"]["filters_applied"]["domain"], "marketing_visibilite")
        self.assertEqual([item["case_id"] for item in self.state["question"]["options"]], ["SYN-PRODUCT"])
        self.assertNotIn("SYN-PRODUCT-WHATSAPP", self.state["diagnostics"]["orientation"]["result_ids"])

    def test_orientation_refusal_keeps_confirmed_state_problem_and_main_filters(self):
        self.marketing()
        before = copy.deepcopy(self.state)
        self.act("refuse")
        self.assertEqual(self.state["phase"], "results")
        self.assertEqual(self.state["confirmed"], before["confirmed"])
        self.assertEqual(self.state["problem_original"], before["problem_original"])
        self.assertEqual(self.state["diagnostics"]["main"], before["diagnostics"]["main"])
        self.assertEqual(self.state["question"]["options"], [])
        self.assertNotIn("describe", self.state["allowed_actions"])

    def test_orientation_acceptance_revalidates_then_searches_main_filters(self):
        self.marketing()
        before = self.state
        self.act("accept", choice_id=self.state["question"]["options"][0]["id"])
        self.assertEqual(self.state["phase"], "results")
        self.assertEqual(self.state["confirmed"]["domain"], "ventes_developpement")
        self.assertEqual(self.state["confirmed"]["sector"], OTHER_SECTOR)
        self.assertEqual(self.state["problem_original"], GENZ_NEED)
        self.assertEqual(self.state["diagnostics"]["main"]["filters_applied"]["domain"], "ventes_developpement")
        self.assertEqual(self.state["diagnostics"]["main"]["result_ids"], ["SYN-PRODUCT"])
        with self.assertRaises(ProtocolError):
            self.service.act(before["session_id"], envelope(before, "accept",
                             choice_id=before["question"]["options"][0]["id"]))

    def test_orientation_from_sectorless_domain_requires_explicit_sector_then_objective(self):
        self.act(choice_id="direction_strategie", initial_need=GENZ_NEED)
        self.choose_label("Comparer des scénarios fictifs")
        self.assertEqual(self.state["phase"], "orientation")
        self.assertTrue(self.state["question"]["options"][0]["sector_revalidation_required"])
        self.act("accept", choice_id=self.state["question"]["options"][0]["id"])
        self.assertEqual(self.state["phase"], "sector")
        self.assertIsNone(self.state["confirmed"]["objective"])
        self.assertIsNone(self.state["diagnostics"]["main"])
        self.choose_label(OTHER_SECTOR)
        self.assertEqual(self.state["phase"], "objective")
        self.choose_label("Créer et optimiser les contenus de vente")
        self.assertEqual(self.state["diagnostics"]["main"]["result_ids"], ["SYN-PRODUCT"])

    def test_orientation_never_switches_sector_to_find_a_case(self):
        self.marketing("Préparer une annonce du menu de demain")
        self.assertEqual(self.state["phase"], "results")
        self.assertEqual(self.state["question"]["options"], [])
        self.assertEqual(self.state["confirmed"]["sector"], OTHER_SECTOR)
        self.assertNotIn("SYN-MARKETING-RESTAURATION",
                         self.state["diagnostics"]["orientation"]["candidate_ids"])

    def test_unknown_problem_has_no_generic_answer_or_unrelated_offer(self):
        self.marketing("Je cherche une solution inconnue à plusieurs choses")
        self.assertEqual(self.state["phase"], "results")
        self.assertEqual(self.state["question"]["options"], [])
        self.assertIn("Aucun cas", self.state["question"]["prompt"])
        self.assertIsNone(self.state["card"])

    def test_negated_task_is_not_a_positive_match(self):
        self.marketing("Je ne veux pas de newsletter ni de fiche produit")
        self.assertEqual(self.state["phase"], "results")
        self.assertEqual(self.state["diagnostics"]["main"]["result_ids"], [])
        self.assertEqual(self.state["diagnostics"]["orientation"]["result_ids"], [])

    def test_explicit_result_rejection_can_open_secondary_orientation(self):
        self.marketing("Préparer une newsletter, mais améliorer une fiche produit")
        self.assertEqual(self.state["phase"], "results")
        self.assertEqual(self.state["diagnostics"]["main"]["result_ids"], ["SYN-MARKETING"])
        self.assertIsNone(self.state["diagnostics"]["orientation"])
        confirmed = copy.deepcopy(self.state["confirmed"])
        self.act("reject")
        self.assertEqual(self.state["phase"], "orientation")
        self.assertEqual(self.state["confirmed"], confirmed)
        self.act("refuse")
        self.assertEqual([item["id"] for item in self.state["question"]["options"]], ["SYN-MARKETING"])

    def test_case_card_is_short_verbatim_terminal_and_has_provenance(self):
        self.marketing("Préparer une newsletter")
        self.act(choice_id="SYN-MARKETING")
        source = self.repository.get("SYN-MARKETING")
        self.assertEqual(self.state["phase"], "terminal")
        self.assertEqual(self.state["card"]["description"], source.description)
        self.assertEqual(self.state["card"]["title"], source.title)
        self.assertEqual(self.state["card"]["source_hash"], source.source_hash)
        self.assertLess(len(self.state["card"]["description"]), 400)
        self.assertNotIn("describe", self.state["allowed_actions"])
        self.assertEqual(self.state["question"]["options"], [])
        self.assertIsNone(self.state["card"]["parcours_url"])  # No invented source URL.
        self.assertEqual(self.state["card"]["preview_parcours_url"],
                         f"/preview/parcours/{self.state['session_id']}?revision={self.state['revision']}")
        self.assertIn("/handoff", self.state["card"]["handoff_url"])
        handoff = self.service.handoff(self.state["session_id"])
        self.assertEqual(handoff["source_fields"], source.source_fields)
        self.assertEqual(handoff["local_context"]["problem_original"], "Préparer une newsletter")
        self.act("back", target="results")
        self.assertEqual([item["id"] for item in self.state["question"]["options"]], ["SYN-MARKETING"])

    def test_initial_need_survives_back_but_scoped_problem_does_not(self):
        self.marketing()
        self.act("back", target="problem")
        self.act("describe", text="Préparer une newsletter, sans promesse commerciale")
        self.act("back", target="objective")
        self.assertEqual(self.state["problem_original"], GENZ_NEED)
        self.assertIsNone(self.state["confirmed"]["objective"])
        self.assertIsNone(self.state["diagnostics"]["main"])
        self.act("back", target="sector")
        self.assertIsNone(self.state["confirmed"]["sector"])
        self.act("back", target="domain")
        self.assertIsNone(self.state["confirmed"]["domain"])
        self.assertEqual(self.state["initial_need"], GENZ_NEED)
        self.act("reset")
        self.assertEqual(self.state["initial_need"], "")

    def test_problem_given_after_qualification_is_invalidated_on_parent_back(self):
        self.marketing("")
        self.assertEqual(self.state["phase"], "problem")
        self.act("describe", text="Préparer une newsletter")
        self.act("back", target="objective")
        self.assertEqual(self.state["problem_original"], "")
        self.choose_label("Créer des contenus marketing")
        self.assertEqual(self.state["phase"], "problem")

    def test_problem_ambiguous_yes_does_not_advance(self):
        self.marketing("")
        before = self.state
        for text in ("", "oui", "non", "42"):
            with self.assertRaises(ProtocolError):
                self.act("describe", text=text)
            self.assertEqual(self.service.read(before["session_id"]), before)

    def test_double_retry_idempotent_but_changed_or_late_duplicate_rejected(self):
        request = envelope(self.state, choice_id="marketing_visibilite")
        self.state = self.service.act(self.state["session_id"], request)
        self.assertEqual(self.service.act(self.state["session_id"], request), self.state)
        with self.assertRaises(ProtocolError):
            self.service.act(self.state["session_id"], {**request, "choice_id": "production"})
        self.choose_label(OTHER_SECTOR)
        with self.assertRaises(ProtocolError):
            self.service.act(self.state["session_id"], request)

    def test_concurrent_choices_only_one_commits(self):
        session_id = self.state["session_id"]
        requests = [envelope(self.state, choice_id=domain)
                    for domain in ("marketing_visibilite", "production")]
        def run(request):
            try:
                return self.service.act(session_id, request)
            except ProtocolError as error:
                return error.code
        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(run, requests))
        self.assertEqual(sum(isinstance(result, dict) for result in results), 1)
        self.assertIn("stale_question", results)
        self.assertEqual(self.service.read(session_id)["revision"], 1)

    def test_old_buttons_question_context_protocol_and_catalogue_guards(self):
        old = self.state
        self.act(choice_id="marketing_visibilite")
        for request in (
            envelope(old, choice_id="production"),
            {**envelope(self.state, choice_id="production"), "question_id": old["question"]["id"]},
            {**envelope(self.state), "protocol_version": 2},
            {**envelope(self.state), "catalogue_revision": "wrong"},
        ):
            with self.assertRaises(ProtocolError):
                self.service.act(self.state["session_id"], request)
        self.repository.revision = "changed"
        with self.assertRaises(ProtocolError) as caught:
            self.choose_label(OTHER_SECTOR)
        self.assertEqual(caught.exception.code, "catalogue_changed")
        self.act("reset")
        self.assertEqual(self.state["catalogue_revision"], "changed")
        self.assertEqual(self.state["phase"], "domain")

    def test_retrieval_adapter_cannot_bypass_filters_or_invent_cases(self):
        self.act(choice_id="marketing_visibilite", initial_need="Préparer une newsletter")
        self.choose_label(OTHER_SECTOR)
        before = copy.deepcopy(self.state)
        objective = self.state["question"]["options"][0]["id"]
        original = self.repository.search
        def broken(problem, filters):
            result = original(problem, filters)
            return replace(result, results=("SYN-PRODUCT",))
        with patch.object(self.repository, "search", broken):
            with self.assertRaises(ProtocolError) as caught:
                self.act(choice_id=objective)
            self.assertEqual(caught.exception.code, "retrieval_contract")
        self.assertEqual(self.service.read(before["session_id"]), before)

    def test_selected_case_cannot_be_guessed_from_other_results(self):
        self.marketing("Préparer une newsletter")
        with self.assertRaises(ProtocolError):
            self.act(choice_id="SYN-PRODUCT")
        self.assertIsNone(self.state["card"])

    def test_expired_session_never_restores_partial_history(self):
        self.service.ttl_seconds = 0
        with self.assertRaises(ProtocolError) as caught:
            self.service.read(self.state["session_id"])
        self.assertEqual(caught.exception.code, "expired_session")


class PreviewHttpTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(mode="synthetic")
        self.client = TestClient(self.app)
        response = self.client.post("/api/preview/v1/sessions", json={"protocol_version": 1})
        self.assertEqual(response.status_code, 200)
        self.state = response.json()
        self.url = f"/api/preview/v1/sessions/{self.state['session_id']}"

    def test_mode_is_opt_in_without_legacy_or_azure_imports(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(RuntimeError):
                create_app()
        self.assertEqual(self.client.post("/api/v1/chat", json={}).status_code, 404)
        health = self.client.get("/health").json()
        self.assertTrue(health["preview"])
        self.assertEqual(health["source"]["source_mode"], "SYNTHETIC")

    def test_http_and_sse_share_versioned_state_and_stale_guard(self):
        request = envelope(self.state, choice_id="marketing_visibilite")
        response = self.client.post(self.url + "/actions/stream", json=request)
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/event-stream", response.headers["content-type"])
        event = json.loads(next(line[6:] for line in response.text.splitlines() if line.startswith("data: ")))
        self.assertEqual(event["phase"], "sector")
        self.assertEqual(event["revision"], 1)
        self.assertEqual(event, self.client.get(self.url).json())
        self.assertEqual(self.client.post(self.url + "/actions", json=request).json(), event)
        stale = self.client.post(self.url + "/actions/stream", json=envelope(self.state, choice_id="production"))
        self.assertEqual(stale.status_code, 409)
        self.assertEqual(stale.json()["error"], "stale_question")
        self.assertIn("application/json", stale.headers["content-type"])
        wrong = self.client.post(self.url + "/actions", json={**request, "protocol_version": 2})
        self.assertEqual(wrong.status_code, 422)

    def test_no_remote_host_origin_or_cache(self):
        self.assertEqual(self.client.get("/health", headers={"Host": "attacker.example"}).status_code, 403)
        self.assertEqual(self.client.post("/api/preview/v1/sessions", json={"protocol_version": 1},
                                         headers={"Origin": "https://public.example"}).status_code, 403)
        response = self.client.get(self.url)
        self.assertEqual(response.headers["cache-control"], "no-store")
        self.assertEqual(response.headers["referrer-policy"], "no-referrer")
        for origin in ("https://public.example", "http://127.0.0.1:8766", "http://127.0.0.1:9999",
                       "http://127.0.0.1:8767.attacker.example", "null"):
            self.assertEqual(self.client.get("/health", headers={"Origin": origin}).status_code, 403)
        for origin in ("http://127.0.0.1:8767", "http://127.0.0.1:4178"):
            self.assertEqual(self.client.get("/health", headers={"Origin": origin}).status_code, 200)
        self.assertEqual(self.client.get("/health", headers={"Sec-Fetch-Site": "cross-site"}).status_code, 403)
        with self.assertRaises(ValueError):
            create_app(mode="synthetic", backend_origin="https://external.example")

    def test_http_choice_text_is_revision_bound(self):
        request = envelope(self.state, choice_text="5. marketing")
        response = self.client.post(self.url + "/actions", json=request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["confirmed"]["domain"], "marketing_visibilite")
        self.assertEqual(self.client.post(self.url + "/actions", json={
            **request, "request_id": uuid.uuid4().hex,
        }).status_code, 409)

    def test_live_http_fixture_flow_and_local_handoff_are_real_transitions(self):
        service = self.app.state.qualification
        def send(action="choose", **kwargs):
            response = self.client.post(self.url + "/actions", json=envelope(self.state, action, **kwargs))
            self.assertEqual(response.status_code, 200, response.text)
            self.state = response.json()
        send(choice_id="marketing_visibilite", initial_need=GENZ_NEED)
        send(choice_id=next(option["id"] for option in self.state["question"]["options"] if option["label"] == OTHER_SECTOR))
        send(choice_id=next(option["id"] for option in self.state["question"]["options"] if option["label"] == "Créer des contenus marketing"))
        send("accept", choice_id=self.state["question"]["options"][0]["id"])
        send(choice_id="SYN-PRODUCT")
        self.assertEqual(self.state["phase"], "terminal")
        self.assertEqual(self.state, service.read(self.state["session_id"]))
        handoff = self.client.get(self.state["card"]["handoff_url"]).json()
        self.assertEqual(handoff["local_context"]["problem_original"], GENZ_NEED)
        page = self.client.get(f"/preview/context/{self.state['session_id']}?revision={self.state['revision']}")
        self.assertEqual(page.status_code, 200)
        self.assertIn("SYNTHÉTIQUE", page.text)
        self.assertIn("n'est pas le parcours en six étapes", page.text)
        self.assertNotIn("https://", page.text)


if __name__ == "__main__":
    unittest.main()
