"""Synthetic candidate-visibility and identity contracts, not model-accuracy tests."""
import json
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from app import haystack_rag as rag
from app.models import ChatRequest
from scripts import diagnose_infilter_retrieval as diagnostic
from tests import test_chat_relevance as helpers


def candidate_pool():
    peripheral = [
        helpers.synthetic_case(
            f"peripheral-{i}", f"Vérifier le budget atelier {i}",
            "Comparer les dépenses prévues et réalisées pour cet atelier.",
        )
        for i in range(6)
    ]
    return peripheral + helpers.synthetic_cases()


class InFilterCandidateTests(unittest.TestCase):
    def setUp(self):
        self.docs = candidate_pool()
        for owner, name, kwargs in (
            (rag, "get_document_store", {"side_effect": AssertionError("No live store")}),
            (rag, "_get_generator", {"side_effect": AssertionError("No live model")}),
            (rag, "_retrieve_docs", {"side_effect": AssertionError("No unfiltered retrieval")}),
            (rag, "_fetch_documents_for_domaine", {"return_value": self.docs}),
            (rag, "_get_q2_choices_list", {"return_value": [helpers.INTENTION]}),
            (rag.stats, "record", {}),
            (rag, "build_parcours_info", {"return_value": {}}),
            (helpers.routes, "build_parcours_info", {"return_value": {}}),
            (helpers.routes, "track_backend_chat_event", {}),
            (helpers.routes, "get_settings", {"return_value": SimpleNamespace(use_rag=True)}),
        ):
            active = patch.object(owner, name, **kwargs)
            active.start()
            self.addCleanup(active.stop)

    def _prompt(self, query, docs=None):
        return rag._build_rag_prompt_from_docs(
            query, "", "", self.docs if docs is None else docs,
            [{"role": "user", "content": query}],
            selected_domain_code=helpers.DOMAIN, selected_sector="BTP", selected_intention="1",
        )

    def _response(self, query, streaming, generated, docs=None):
        request = ChatRequest(
            message=query, selected_domain_code=helpers.DOMAIN,
            selected_sector="BTP", selected_intention="1",
        )
        prompts = []

        def render(prompt):
            prompts.append(prompt)
            return generated(prompt)

        with (
            patch.object(rag, "_retrieve_docs_for_question",
                         return_value=self.docs if docs is None else docs),
            patch.object(rag, "_get_generator", return_value=Mock(
                run=Mock(side_effect=lambda messages: {"replies": [render(messages[0].text)]}),
            )),
            patch.object(helpers.routes, "stream_prompt", side_effect=lambda prompt: iter([render(prompt)])),
        ):
            if streaming:
                events = [json.loads(line.removeprefix("data:").strip())
                          for line in helpers.routes._stream_chat(request, None)]
                result = next(event for event in events if event.get("done"))
                result["answer"] = "".join(event.get("t", "") for event in events)
            else:
                result = helpers.routes.chat(request, SimpleNamespace(headers={})).model_dump()
        return result, prompts

    @staticmethod
    def _select_if_visible(selected):
        def generate(prompt):
            titles = {case["titre"] for case in json.loads(prompt.rsplit("\n\n", 1)[1])["candidats"]}
            return helpers.model_list([doc for doc in selected if doc.meta["cas_utilisation"] in titles])
        return generate

    def test_selector_sees_entire_retrieved_pool_not_only_five_display_slots(self):
        payload = json.loads(self._prompt(helpers.QUERY).rsplit("\n\n", 1)[1])
        self.assertEqual(len(payload["candidats"]), len(self.docs))
        self.assertEqual([row["titre"] for row in payload["candidats"]],
                         [doc.meta["cas_utilisation"] for doc in self.docs])
        self.assertEqual([row["numero"] for row in payload["candidats"]],
                         list(range(1, len(self.docs) + 1)))
        self.assertIn("au maximum cinq", self._prompt(helpers.QUERY))

    def test_candidate_inventory_keeps_aligned_source_identity_beyond_five(self):
        sources, ids, contents, extras = rag._docs_to_payload(self.docs)
        self.assertEqual(ids, [doc.id for doc in self.docs])
        self.assertEqual(contents, [doc.content for doc in self.docs])
        self.assertEqual(sources, contents)
        self.assertEqual([row["cas_utilisation"] for row in extras],
                         [doc.meta["cas_utilisation"] for doc in self.docs])

    def test_http_and_sse_can_retain_a_candidate_below_the_display_cutoff(self):
        for query, selected in (
            (helpers.QUERY, self.docs[6]),
            ("Je veux identifier les risques avant une intervention.", self.docs[7]),
            ("Je veux assembler les indicateurs hebdomadaires.", self.docs[8]),
        ):
            for streaming in (False, True):
                with self.subTest(query=query, streaming=streaming):
                    result, prompts = self._response(query, streaming, self._select_if_visible([selected]))
                    self.assertEqual(len(prompts), 1)
                    self.assertEqual(result["suggested_case_ids"], [selected.id])
                    self.assertEqual(result["sources"], [selected.content])
                    self.assertEqual(result["suggested_cases"][0]["content"], selected.content)
                    self.assertEqual(result["suggested_cases"][0]["cas_utilisation"],
                                     selected.meta["cas_utilisation"])
                    self.assertEqual(result["selected_domain_code"], helpers.DOMAIN)
                    self.assertEqual(result["selected_sector"], "BTP")
                    self.assertEqual(result["selected_intention"], "1")
                    self.assertEqual(rag._resolve_detail_selection("1", result["suggested_cases"]), 0)

    def test_negations_reach_selector_unchanged_and_are_not_lexically_decided(self):
        query = "Pas de budget atelier ni de prévention : je veux rédiger un compte rendu des échanges."
        selected = self.docs[6]
        for streaming in (False, True):
            with self.subTest(streaming=streaming):
                result, prompts = self._response(query, streaming, self._select_if_visible([selected]))
                self.assertEqual(json.loads(prompts[0].rsplit("\n\n", 1)[1])["besoin_concret"], query)
                self.assertEqual(result["suggested_case_ids"], [selected.id])
                self.assertNotIn(query, result["suggested_cases"][0]["content"])

    def test_multiple_retained_candidates_keep_ranked_order_and_display_numbering(self):
        selected = [self.docs[6], self.docs[9]]
        for streaming in (False, True):
            with self.subTest(streaming=streaming):
                result, _ = self._response(
                    "Je veux un compte rendu et la liste des actions décidées.", streaming,
                    self._select_if_visible(list(reversed(selected))),
                )
                self.assertEqual(result["suggested_case_ids"], [doc.id for doc in selected])
                for number, doc in enumerate(selected, 1):
                    self.assertIn(f"{number}. {doc.meta['cas_utilisation']}", result["answer"])
                index = rag._resolve_detail_selection("2", result["suggested_cases"])
                self.assertEqual(result["suggested_cases"][index]["id"], selected[1].id)

    def test_display_and_payload_remain_limited_to_five_after_selection(self):
        for streaming in (False, True):
            with self.subTest(streaming=streaming):
                result, _ = self._response(helpers.QUERY, streaming, self._select_if_visible(self.docs))
                self.assertEqual(result["suggested_case_ids"], [doc.id for doc in self.docs[:5]])
                self.assertEqual(len(result["suggested_cases"]), 5)
                self.assertNotIn(self.docs[5].meta["cas_utilisation"], result["answer"])

    def test_last_candidate_in_configured_fifty_document_budget_remains_selectable(self):
        selected = self.docs[9]
        docs = [
            helpers.synthetic_case(f"budget-{i}", f"Budget fictif {i}", "Comparer les dépenses.")
            for i in range(49)
        ] + [selected]
        for streaming in (False, True):
            with self.subTest(streaming=streaming):
                result, prompts = self._response(
                    helpers.QUERY, streaming, self._select_if_visible([selected]), docs,
                )
                self.assertEqual(len(json.loads(prompts[0].rsplit("\n\n", 1)[1])["candidats"]), 50)
                self.assertEqual(result["suggested_case_ids"], [selected.id])

    def test_late_candidate_detail_remains_terminal_and_uses_its_own_parcours(self):
        selected = self.docs[9]
        for streaming in (False, True):
            with self.subTest(streaming=streaming):
                result, _ = self._response(helpers.QUERY, streaming, self._select_if_visible([selected]))
                self.assertEqual(result["suggested_case_ids"], [selected.id])
                request = ChatRequest(
                    message="1", selected_domain_code=helpers.DOMAIN, selected_sector="BTP",
                    selected_intention="1", last_suggested_cases=result["suggested_cases"],
                    history=[{"role": "user", "content": helpers.QUERY},
                             {"role": "assistant", "content": result["answer"]}],
                )
                parcours = {
                    "parcours_url": f"https://example.invalid/parcours/{selected.id}",
                    "cta_label": "Consulter le parcours",
                }
                with (
                    patch.object(rag, "_enrich_case_from_document_store", side_effect=lambda case: case),
                    patch.object(rag, "_retrieve_docs_for_question", side_effect=AssertionError("No new retrieval")),
                    patch.object(rag, "build_parcours_info", return_value=parcours) as lookup,
                    patch.object(helpers.routes, "build_parcours_info", return_value=parcours),
                    patch.object(helpers.routes, "stream_prompt", side_effect=AssertionError("No detail model")),
                ):
                    if streaming:
                        events = [json.loads(line.removeprefix("data:").strip())
                                  for line in helpers.routes._stream_chat(request, None)]
                        payload = next(event for event in events if event.get("done"))
                        answer = "".join(event.get("t", "") for event in events)
                    else:
                        payload = helpers.routes.chat(request, SimpleNamespace(headers={})).model_dump()
                        answer = payload["answer"]
                self.assertTrue(all(call.args[0] == selected.id for call in lookup.call_args_list))
                self.assertEqual(payload["suggested_cases"][0]["parcours_url"], parcours["parcours_url"])
                self.assertIn(selected.meta["cas_utilisation"], answer)
                self.assertIn(selected.meta["description_cas_utilisation"], answer)
                self.assertNotIn("Souhaitez-vous approfondir", answer)
                self.assertNotIn("Répondez 1 ou 2", answer)

    def test_semantic_zero_match_and_empty_retrieval_remain_terminal(self):
        for docs in (self.docs, []):
            for streaming in (False, True):
                with self.subTest(empty=not docs, streaming=streaming):
                    result, prompts = self._response(
                        "Je veux calculer une déclaration fiscale.", streaming,
                        lambda prompt: rag.NO_MATCH_MESSAGE, docs,
                    )
                    self.assertEqual(result["answer"], rag.NO_MATCH_MESSAGE)
                    self.assertEqual(result["suggested_case_ids"], [])
                    self.assertFalse(result["suggested_cases"])
                    self.assertEqual(result["sources"], [])
                    self.assertEqual(len(prompts), int(bool(docs)))

    def test_unknown_titles_and_ambiguous_ids_are_not_assigned_to_hidden_candidates(self):
        cases = [rag._doc_to_case_dict(doc, i) for i, doc in enumerate(self.docs)]
        answer, retained = rag._reconcile_generated_case_list("7. Titre inventé\nTexte inventé.", cases)
        self.assertEqual((answer, retained), (rag.NO_MATCH_MESSAGE, []))
        cases[0]["id"] = cases[6]["id"]
        answer, retained = rag._reconcile_generated_case_list(helpers.model_list([self.docs[6]]), cases)
        self.assertEqual((answer, retained), (rag.NO_MATCH_MESSAGE, []))

    def test_vector_and_fallback_filters_stay_exact_with_no_cross_domain_recovery(self):
        selected = helpers.synthetic_case(
            "applicable", "Restituer les échanges", "Rédiger la synthèse des échanges.", "Multi-sectoriel",
        )
        excluded = [
            helpers.synthetic_case("wrong-sector", "Titre fictif A", "Texte fictif A", "Commerce & retail"),
            helpers.synthetic_case("wrong-domain", "Titre fictif B", "Texte fictif B", "Multi-sectoriel"),
            helpers.synthetic_case("wrong-intention", "Titre fictif C", "Texte fictif C", "Multi-sectoriel"),
        ]
        excluded[1].meta["domaine"] = "finance_pilotage"
        excluded[2].meta["intention"] = "Autre objectif synthétique"
        docs = excluded + [selected]
        observed = []

        def pipeline(filters=None):
            observed.append(filters)
            return Mock(run=Mock(return_value={
                "retriever": {"documents": [doc for doc in docs if helpers.matches_filter(doc, filters)]},
            }))

        with (
            patch.object(rag, "_fetch_documents_for_domaine", return_value=[selected, excluded[0], excluded[2]]),
            patch.object(rag, "build_rag_retrieval_only_pipeline", side_effect=pipeline),
        ):
            result = rag._retrieve_docs_for_question(
                helpers.QUERY, helpers.DOMAIN, "1", "Autre / Non spécifique",
            )
        self.assertEqual([doc.id for doc in result], [selected.id])
        self.assertEqual(len(observed), 2)
        for filters in observed:
            self.assertEqual(filters["operator"], "AND")
            self.assertEqual(len(filters["conditions"]), 3)
            self.assertTrue(all(not helpers.matches_filter(doc, filters) for doc in excluded))

    def test_read_only_diagnosis_bounds_tied_ranks_without_exporting_source_text(self):
        first = helpers.synthetic_case("higher", "Cahier", "Cahier", "Multi-sectoriel")
        tied = [helpers.synthetic_case(f"tie-{i}", "Texte réservé", "Texte réservé", "Multi-sectoriel")
                for i in range(3)]
        with (
            patch.object(diagnostic, "read_documents", return_value=[first] + tied),
            patch.object(rag, "get_settings", return_value=SimpleNamespace(top_k_retrieve=50)),
        ):
            report = diagnostic.diagnose(
                "Cahier", helpers.DOMAIN, "Autre / Non spécifique", "1", tied[1].id,
            )
        self.assertEqual(report["stages"][0]["eligible_count"], 0)
        stage = report["stages"][1]
        self.assertEqual(stage["eligible_count"], 4)
        self.assertEqual(stage["target_rank_interval_any_vector_tie_order"], [2, 4])
        self.assertFalse(report["model_called"])
        self.assertNotIn("Texte réservé", json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    unittest.main()
