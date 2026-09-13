"""Offline synthetic evaluation: retrieval ordering and displayed-list identity, not model accuracy."""
import json
import unittest
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock, patch

from app import haystack_rag as rag
from app.models import ChatRequest

_offline_transport = ModuleType("app.rag")
for _name in ("chat_simple", "chat_simple_stream", "stream_prompt"):
    setattr(_offline_transport, _name, Mock(side_effect=AssertionError("No live model transport")))
with patch.dict("sys.modules", {"app.rag": _offline_transport}):
    from app.routes import chat as routes


DOMAIN = "activites_terrain"
INTENTION = "Partager les informations terrain"
QUERY = "Transformer mes notes de réunion de chantier en compte rendu."


def synthetic_case(key, title, description, sector="BTP"):
    return SimpleNamespace(id=f"synthetic-{key}", content=description, meta={
        "domaine": DOMAIN, "intention": INTENTION, "secteur": sector,
        "cas_utilisation": title, "description_cas_utilisation": description,
    })


def synthetic_cases():
    return [
        synthetic_case("summary", "Synthétiser les notes de réunion de chantier",
                       "Transformer les notes de réunion en compte rendu clair. Conserver les décisions du chantier."),
        synthetic_case("prevention", "Préparer un plan de prévention chantier",
                       "Identifier les risques de sécurité et préparer les mesures de prévention avant une intervention."),
        synthetic_case("reporting", "Consolider le reporting hebdomadaire du chantier",
                       "Assembler les indicateurs d'avancement hebdomadaire et signaler les écarts de planning."),
        synthetic_case("actions", "Suivre les décisions et actions de réunion chantier",
                       "Extraire les actions, responsables et échéances des décisions prises en réunion."),
        synthetic_case("minutes", "Formaliser un procès-verbal de chantier",
                       "Restituer les échanges et décisions dans un procès-verbal validé par les participants.",
                       "Multi-sectoriel"),
    ]


def model_list(docs):
    return "\n\n".join(
        f"{i}. **{doc.meta['cas_utilisation']}**\n"
        f"Pourquoi c'est pertinent pour vous :\n{doc.content}\n---"
        for i, doc in enumerate(docs, 1)
    ) + "\n\nSouhaitez-vous approfondir l’un de ces cas ?\nIndiquez son numéro."


def matches_filter(doc, node):
    if "conditions" in node:
        matches = [matches_filter(doc, part) for part in node["conditions"]]
        return all(matches) if node["operator"] == "AND" else any(matches)
    return doc.meta.get(node["field"].removeprefix("meta.")) == node["value"]


class SyntheticRelevanceTests(unittest.TestCase):
    def setUp(self):
        self.docs = synthetic_cases()
        for target, kwargs in (
            ("get_document_store", {"side_effect": AssertionError("No real document store")}),
            ("_get_generator", {"side_effect": AssertionError("No model calls")}),
            ("_retrieve_docs", {"side_effect": AssertionError("No unfiltered retrieval")}),
            ("_fetch_documents_for_domaine", {"return_value": self.docs}),
            ("_get_q2_choices_list", {"return_value": [INTENTION]}),
        ):
            p = patch.object(rag, target, **kwargs)
            p.start()
            self.addCleanup(p.stop)
        for owner, target, kwargs in (
            (rag.stats, "record", {}),
            (routes, "track_backend_chat_event", {}),
            (routes, "build_parcours_info", {"return_value": {}}),
            (rag, "build_parcours_info", {"return_value": {}}),
            (routes, "get_settings", {"return_value": SimpleNamespace(use_rag=True)}),
        ):
            p = patch.object(owner, target, **kwargs)
            p.start()
            self.addCleanup(p.stop)

    def _handler_result(self, generated, streaming, docs=None, request=None, expect_generation=True):
        request = request or ChatRequest(
            message=QUERY, selected_domain_code=DOMAIN, selected_sector="BTP", selected_intention="1"
        )
        with (
            patch.object(rag, "_retrieve_docs_for_question", return_value=self.docs if docs is None else docs),
            patch.object(rag, "_get_generator", return_value=Mock(run=Mock(return_value={"replies": [generated]}))) as generator,
            patch.object(routes, "stream_prompt", return_value=iter([generated])) as stream,
        ):
            if streaming:
                events = [json.loads(line.removeprefix("data:").strip()) for line in routes._stream_chat(request, None)]
                result = "".join(event.get("t", "") for event in events), next(event for event in events if event.get("done"))
            else:
                payload = routes.chat(request, SimpleNamespace(headers={})).model_dump()
                result = payload["answer"], payload
            self.assertEqual(generator.call_count, int(expect_generation and not streaming))
            self.assertEqual(stream.call_count, int(expect_generation and streaming))
            return result

    def _assert_no_match(self, answer, payload):
        self.assertEqual(
            answer,
            "Je n'ai pas de cas suffisamment pertinent à vous proposer avec les choix actuels. "
            "Vous pouvez préciser votre besoin ou revenir à une étape précédente pour modifier vos choix.",
        )
        self.assertEqual(payload["suggested_case_ids"], [])
        self.assertFalse(payload["suggested_cases"])
        self.assertEqual(payload["sources"], [])
        for field in ("pending_action", "pending_use_case_id", "pending_case_index",
                      "parcours_url", "parcours_cta_label"):
            self.assertIsNone(payload.get(field), field)
        self.assertEqual(payload["selected_domain_code"], DOMAIN)
        self.assertEqual(payload["selected_sector"], "BTP")
        self.assertEqual(payload["selected_intention"], "1")

    def test_initial_domain_number_after_real_welcome_then_sector_in_http_and_sse(self):
        sector_question = (
            "Pour mieux cibler mes recommandations, pouvez-vous me dire dans quel secteur "
            "vous opérez ? Répondez avec le numéro du choix. (optionnel)\n\n"
            + "\n".join(f"{i}. {label}" for i, label in enumerate(
                rag.SECTEURS_PAR_DOMAINE[DOMAIN] + ["Autre / Non spécifique"], 1
            ))
        )
        intention_question = f"Quel est votre objectif principal dans ce domaine ?\n\n1. {INTENTION}"
        for streaming in (False, True):
            for forward_state in (False, True):
                with self.subTest(streaming=streaming, forward_state=forward_state):
                    def send(request):
                        if streaming:
                            events = [
                                json.loads(line.removeprefix("data:").strip())
                                for line in routes._stream_chat(request, None)
                            ]
                            return "".join(event.get("t", "") for event in events), next(
                                event for event in events if event.get("done")
                            )
                        payload = routes.chat(request, SimpleNamespace(headers={})).model_dump()
                        return payload["answer"], payload

                    with (
                        patch.object(rag, "_retrieve_docs_for_question", side_effect=AssertionError("Still qualifying")),
                        patch.object(rag, "_get_generator", side_effect=AssertionError("No LLM for resolved menu state")),
                        patch.object(routes, "stream_prompt", side_effect=AssertionError("No LLM for resolved menu state")),
                    ):
                        history = [{"role": "assistant", "content": rag.WELCOME_MESSAGE}]
                        answer, payload = send(ChatRequest(message="13", history=history))
                        self.assertEqual(answer, sector_question)
                        self.assertEqual(payload["selected_domain_code"], DOMAIN)
                        self.assertIsNone(payload["selected_sector"])
                        self.assertIsNone(payload["selected_intention"])
                        history += [{"role": "user", "content": "13"}, {"role": "assistant", "content": answer}]
                        client_state = {
                            field: payload[field]
                            for field in ("selected_domain_code", "selected_sector", "selected_intention")
                        } if forward_state else {}
                        answer, payload = send(ChatRequest(message="BTP", history=history, **client_state))
                        self.assertEqual(answer, intention_question)
                        self.assertEqual(payload["selected_domain_code"], DOMAIN)
                        self.assertEqual(payload["selected_sector"], "BTP")
                        self.assertIsNone(payload["selected_intention"])
                        self.assertEqual(payload["suggested_case_ids"], [])

    def test_initial_number_fallback_is_limited_to_empty_or_welcome_only_history(self):
        for history in ([], [{"role": "assistant", "content": rag.WELCOME_MESSAGE}]):
            with self.subTest(history=history):
                self.assertEqual(
                    rag._resolve_current_selection_state(history, "13", None, None, None)[1:],
                    (DOMAIN, None, None),
                )
        for question in (
            "Dans quel secteur exercez-vous ?",
            "Quel est votre objectif principal ?",
            "Quel problème souhaitez-vous résoudre ?",
            "Quel cas souhaitez-vous approfondir ?",
        ):
            with self.subTest(question=question):
                self.assertEqual(
                    rag._resolve_current_selection_state(
                        [{"role": "assistant", "content": question}], "13", None, None, None,
                    )[1:],
                    (None, None, None),
                )
        self.assertEqual(
            rag._resolve_current_selection_state(
                [{"role": "user", "content": "Bonjour"}, {"role": "assistant", "content": rag.WELCOME_MESSAGE}],
                "13", None, None, None,
            )[1:],
            (None, None, None),
        )
        self.assertEqual(
            rag._resolve_current_selection_state([], "13", DOMAIN, "BTP", "1")[1:],
            (DOMAIN, "BTP", "1"),
        )

    def test_ready_zero_retrieval_returns_no_match_without_model_or_detail_stats(self):
        request = ChatRequest(
            message=QUERY, selected_domain_code=DOMAIN, selected_sector="BTP", selected_intention="1",
            pending_action="expand_details", pending_use_case_id="stale-case",
        )
        for streaming in (False, True):
            with self.subTest(streaming=streaming), patch.object(rag.stats, "record") as record:
                answer, payload = self._handler_result(
                    model_list(self.docs), streaming, docs=[], request=request, expect_generation=False,
                )
                self._assert_no_match(answer, payload)
                self.assertNotIn("cas", [call.args[0] for call in record.call_args_list])

    def test_zero_retrieval_preserves_distinct_eleven_field_contracts(self):
        with patch.object(rag, "_retrieve_docs_for_question", return_value=[]):
            for streaming in (False, True):
                with self.subTest(streaming=streaming):
                    handler = rag.get_rag_prompt_and_sources if streaming else rag.query_rag_haystack
                    result = handler(
                        QUERY, [], selected_domain_code=DOMAIN, selected_sector="BTP", selected_intention="1",
                    )
                    self.assertEqual(len(result), 11)
                    self.assertEqual(result[1:5], ([], [], [], []))
                    if streaming:
                        self.assertIn(QUERY, result[0])
                        self.assertEqual(result[5:8], (DOMAIN, "BTP", "1"))
                        self.assertEqual(result[8:], (rag.NO_MATCH_MESSAGE, None, None))
                    else:
                        self.assertEqual(result[0], rag.NO_MATCH_MESSAGE)
                        self.assertEqual(result[5:8], (None, None, None))
                        self.assertEqual(result[8:], (DOMAIN, "BTP", "1"))

    def test_retrieved_without_validated_cases_uses_same_safe_message(self):
        generations = [
            "Aucun cas directement pertinent.\n1. Quel résultat attendez-vous ?\n2. Quelles données avez-vous ?",
            "1. **Cas inconnu**\nPremière action : faites ceci.\n"
            "Souhaitez-vous approfondir l’un de ces cas ?\nIndiquez son numéro.",
            "Réponse sans liste",
        ]
        request = ChatRequest(
            message=QUERY, selected_domain_code=DOMAIN, selected_sector="BTP", selected_intention="1",
            pending_action="expand_details", pending_use_case_id="stale-case",
        )
        for generated in generations:
            for streaming in (False, True):
                with self.subTest(generated=generated, streaming=streaming):
                    answer, payload = self._handler_result(generated, streaming, request=request)
                    self._assert_no_match(answer, payload)

    def test_incomplete_qualification_or_missing_problem_is_not_no_match(self):
        generated = "Précisez votre besoin.\n1. Premier choix\n2. Autre choix"
        requests = [
            ChatRequest(message=QUERY),
            ChatRequest(message=QUERY, selected_domain_code=DOMAIN),
            ChatRequest(message=QUERY, selected_domain_code=DOMAIN, selected_sector="BTP"),
            ChatRequest(message="1", selected_domain_code=DOMAIN, selected_sector="BTP"),
        ]
        for request in requests:
            for streaming in (False, True):
                with (
                    self.subTest(request=request, streaming=streaming),
                    patch.object(rag, "_retrieve_docs_for_question", side_effect=AssertionError("Qualification is incomplete")),
                    patch.object(rag, "_get_generator", return_value=Mock(run=Mock(return_value={"replies": [generated]}))),
                    patch.object(routes, "stream_prompt", return_value=iter([generated])),
                ):
                    if streaming:
                        events = [json.loads(line.removeprefix("data:").strip()) for line in routes._stream_chat(request, None)]
                        answer = "".join(event.get("t", "") for event in events)
                        self.assertTrue(any(event.get("done") for event in events))
                    else:
                        answer = routes.chat(request, SimpleNamespace(headers={})).answer
                    if not request.selected_domain_code:
                        self.assertEqual(answer, generated)
                    elif not request.selected_sector:
                        self.assertTrue(answer.startswith("Pour mieux cibler mes recommandations"))
                        self.assertIn("1. BTP", answer)
                        self.assertNotIn("objectif principal", answer)
                    else:
                        self.assertEqual(
                            answer, f"Quel est votre objectif principal dans ce domaine ?\n\n1. {INTENTION}"
                        )
                    self.assertNotEqual(answer, rag.NO_MATCH_MESSAGE)

    def test_clarification_after_either_no_match_path_recovers_selectable_cases(self):
        clarification = "Je veux extraire les actions et responsables des notes de réunion."
        for docs in ([], self.docs):
            for streaming in (False, True):
                with self.subTest(empty_retrieval=not docs, streaming=streaming):
                    answer, payload = self._handler_result(
                        "Aucun cas directement pertinent.", streaming, docs=docs, expect_generation=bool(docs),
                    )
                    self._assert_no_match(answer, payload)
                    request = ChatRequest(
                        message=clarification,
                        history=[{"role": "user", "content": QUERY}, {"role": "assistant", "content": answer}],
                        selected_domain_code=payload["selected_domain_code"],
                        selected_sector=payload["selected_sector"],
                        selected_intention=payload["selected_intention"],
                        last_suggested_cases=payload["suggested_cases"],
                        pending_action=payload["pending_action"],
                        pending_use_case_id=payload["pending_use_case_id"],
                    )
                    with patch.object(rag, "_user_probleme_q3_text", wraps=rag._user_probleme_q3_text) as problem:
                        recovered_answer, recovered = self._handler_result(
                            model_list([self.docs[3]]), streaming, request=request,
                        )
                        self.assertEqual(
                            rag._user_probleme_q3_text(
                                problem.call_args.args[0], **problem.call_args.kwargs,
                            ),
                            clarification,
                        )
                    self.assertEqual(recovered["suggested_case_ids"], [self.docs[3].id])
                    self.assertEqual(recovered["sources"], [self.docs[3].content])
                    self.assertIn(self.docs[3].meta["cas_utilisation"], recovered_answer)
                    self.assertEqual(recovered["selected_intention"], "1")

    def test_bold_numbers_are_retained_and_selectable_in_http_and_sse(self):
        first, second = self.docs[0], self.docs[3]
        for heading in ("**{n}.** **{title}**", "**{n}. {title}**",
                        "__{n}.__ __{title}__", "**{n}**. **{title}**", "### *{n}.* *{title}*"):
            generated = "\n\n".join(
                heading.format(n=i, title=doc.meta["cas_utilisation"]) + "\n" + doc.content
                for i, doc in enumerate([first, second], 1)
            )
            for streaming in (False, True):
                with self.subTest(heading=heading, streaming=streaming):
                    answer, payload = self._handler_result(generated, streaming)
                    self.assertEqual(payload["suggested_case_ids"], [first.id, second.id])
                    self.assertEqual(payload["sources"], [first.content, second.content])
                    self.assertEqual([case["id"] for case in payload["suggested_cases"]], [first.id, second.id])
                    for i, doc in enumerate([first, second], 1):
                        self.assertIn(f"{i}. {doc.meta['cas_utilisation']}\n{doc.content}", answer)
                    selected = rag._resolve_detail_selection("2", payload["suggested_cases"])
                    self.assertEqual(payload["suggested_cases"][selected]["id"], second.id)

    def test_unknown_bold_candidate_is_not_copied_into_known_case_body(self):
        first, second = self.docs[0], self.docs[3]
        generated = (
            f"1. **{first.meta['cas_utilisation']}**\n{first.content}\n\n"
            "**2.** **Titre inventé**\nNE_DOIT_PAS_FUIR\n\n"
            f"**3.** **{second.meta['cas_utilisation']}**\n{second.content}"
        )
        for streaming in (False, True):
            with self.subTest(streaming=streaming):
                answer, payload = self._handler_result(generated, streaming)
                self.assertEqual(payload["suggested_case_ids"], [first.id, second.id])
                self.assertEqual(payload["sources"], [first.content, second.content])
                self.assertNotIn("Titre inventé", answer)
                self.assertNotIn("NE_DOIT_PAS_FUIR", answer)
                self.assertIn(first.content, answer)
                self.assertIn(second.content, answer)

    def test_blank_and_malformed_candidate_boundaries_do_not_leak(self):
        first, second = self.docs[0], self.docs[3]
        for invalid in ("**2.**", "**2.** **", "**2:** **Titre inventé**", "__2.__ __Titre inventé__",
                        "**2**", "**2** **Titre inventé**"):
            generated = (
                f"1. **{first.meta['cas_utilisation']}**\n{first.content}\n\n"
                f"{invalid}\nCORPS_INVALIDE\n\n"
                f"**3.** **{second.meta['cas_utilisation']}**\n{second.content}"
            )
            for streaming in (False, True):
                with self.subTest(invalid=invalid, streaming=streaming):
                    answer, payload = self._handler_result(generated, streaming)
                    self.assertEqual(payload["suggested_case_ids"], [first.id, second.id])
                    self.assertEqual(payload["sources"], [first.content, second.content])
                    self.assertNotIn("Titre inventé", answer)
                    self.assertNotIn("CORPS_INVALIDE", answer)
                    self.assertIn(first.content, answer)
                    self.assertIn(second.content, answer)

    def test_bold_qualification_choices_without_case_context_are_untouched(self):
        generated = "Dans quel domaine souhaitez-vous agir ?\n**1.** **Premier domaine**\n**2.** **Autre domaine**"
        for streaming in (False, True):
            with self.subTest(streaming=streaming):
                answer, payload = self._handler_result(
                    generated, streaming, docs=[], request=ChatRequest(message="Bonjour")
                )
                self.assertEqual(answer, generated)
                self.assertEqual(payload["suggested_case_ids"], [])

    def test_eight_query_scenarios_preserve_candidates_without_semantic_cutoff(self):
        # Expected leaders are synthetic relevance hypotheses, not production judgments.
        scenarios = [
            ("compte rendu réunion notes chantier", "summary"),
            ("prévention risques sécurité intervention", "prevention"),
            ("reporting avancement hebdomadaire planning", "reporting"),
            ("procès verbal échanges participants", "minutes"),
            ("actions responsables échéances décisions", "actions"),
            ("restituer fidèlement les propos échangés", "minutes"),
            ("chantier", None),
            ("document", None),
        ]
        for query, expected in scenarios:
            with self.subTest(query=query):
                ranked = rag._rank_docs_by_query_overlap(query, list(reversed(self.docs)))
                self.assertEqual({d.id for d in ranked}, {d.id for d in self.docs})
                if expected:
                    self.assertEqual(ranked[0].id, f"synthetic-{expected}")

    def test_zero_lexical_overlap_keeps_upstream_semantic_order(self):
        docs = [
            synthetic_case("oral", "Restituer les échanges", "Synthèse fidèle des propos"),
            synthetic_case("risk", "Anticiper les dangers", "Mesures de sécurité"),
        ]
        self.assertEqual(rag._rank_docs_by_query_overlap("mémoire collective", docs), docs)

    def test_relevance_order_alone_does_not_remove_peripheral_prevention_case(self):
        ranked = rag._rank_docs_by_query_overlap(QUERY, self.docs[:3])
        self.assertEqual(ranked[0].id, "synthetic-summary")
        self.assertIn("synthetic-prevention", [doc.id for doc in ranked])
        # The model must be allowed to omit a peripheral candidate; ranking is not a relevance gate.
        prompt = rag._build_rag_prompt_from_docs(
            QUERY, "", "", ranked, [{"role": "user", "content": QUERY}],
            selected_domain_code=DOMAIN, selected_sector="BTP", selected_intention="1",
        )
        self.assertIn("Un secteur commun ne suffit pas", prompt)
        self.assertIn("sans minimum", prompt)
        self.assertNotIn("Cas identifiés (3 à 5)", prompt)
        self.assertNotIn("Tu ne supprimes rien", prompt)
        candidates = json.loads(prompt.rsplit("\n\n", 1)[1])["candidats"]
        self.assertEqual(
            [(c["numero"], c["titre"], c["description"]) for c in candidates],
            [(i, doc.meta["cas_utilisation"], doc.content) for i, doc in enumerate(ranked, 1)],
        )

    def test_reconciliation_handles_subset_reordering_hallucination_and_duplicates(self):
        source = [rag._doc_to_case_dict(doc, i) for i, doc in enumerate(self.docs)]
        summary, prevention, _, actions, _ = self.docs
        scenarios = [
            (model_list([summary]), [0]),
            (model_list([actions, summary]), [0, 3]),
            (model_list([summary, summary, actions]), [0, 3]),
            (model_list([summary, synthetic_case("fake", "Cas inventé", "Non fourni"), actions]), [0, 3]),
            ("Aucun cas directement pertinent.", []),
            (model_list([synthetic_case("fake", "Cas inventé", "Non fourni")]), []),
            (model_list([prevention]), [1]),
        ]
        for generated, expected in scenarios:
            with self.subTest(generated=generated):
                answer, retained = rag._reconcile_generated_case_list(generated, source)
                self.assertEqual(retained, expected)
                self.assertNotIn("Cas inventé", answer)
                for number, index in enumerate(retained, 1):
                    self.assertIn(f"{number}. {self.docs[index].meta['cas_utilisation']}\n", answer)
                    self.assertIn(self.docs[index].content, answer)
                self.assertEqual(rag._reconcile_generated_case_list(
                    answer, [source[i] for i in retained]
                )[0], answer)

    def test_duplicate_source_titles_cannot_be_silently_assigned_to_an_id(self):
        first = self.docs[0]
        duplicate = synthetic_case("duplicate", first.meta["cas_utilisation"], "Description distincte")
        answer, retained = rag._reconcile_generated_case_list(
            model_list([first]), [rag._doc_to_case_dict(d, i) for i, d in enumerate([first, duplicate])]
        )
        self.assertEqual(retained, [])
        self.assertNotIn(first.meta["cas_utilisation"], answer)

    def test_conflicting_titles_for_same_id_are_not_selectable(self):
        cases = [rag._doc_to_case_dict(doc, i) for i, doc in enumerate(self.docs[:2])]
        cases[1]["id"] = cases[0]["id"]
        _, retained = rag._reconcile_generated_case_list(model_list(self.docs[:2]), cases)
        self.assertEqual(retained, [])

    def test_reconciler_does_not_claim_to_judge_semantic_fit(self):
        answer, retained = rag._reconcile_generated_case_list(
            model_list([self.docs[1]]), [rag._doc_to_case_dict(d, i) for i, d in enumerate(self.docs)]
        )
        self.assertEqual(retained, [1])
        self.assertIn("prévention", answer)

    def test_multisector_alternative_stays_available_with_all_prefilters(self):
        doc = self.docs[4]
        seen = []

        def pipeline(filters=None):
            seen.append(filters)
            return Mock(run=Mock(return_value={"retriever": {"documents": [doc] if matches_filter(doc, filters) else []}}))

        with patch.object(rag, "build_rag_retrieval_only_pipeline", side_effect=pipeline):
            found = rag._retrieve_docs_for_question("procès verbal échanges", DOMAIN, "1", "BTP")
        self.assertEqual(found, [doc])
        self.assertEqual(len(seen), 2)
        self.assertTrue(all(len(f["conditions"]) == 3 for f in seen))

    def test_http_and_sse_subset_identity_survives_next_detail_selection(self):
        generated = model_list([self.docs[3], self.docs[0]])  # Reordered, only two of the candidates.
        excluded = synthetic_case("foreign", "Autre métier", "Cas exclu", "Commerce & retail")
        corpus = self.docs + [excluded]
        filters_seen = []

        def pipeline(filters=None):
            filters_seen.append(filters)
            return Mock(run=Mock(return_value={"retriever": {"documents": [
                doc for doc in corpus if matches_filter(doc, filters)
            ]}}))

        request = ChatRequest(message=QUERY, selected_domain_code=DOMAIN, selected_sector="BTP", selected_intention="1")
        for streaming in (False, True):
            with (
                self.subTest(streaming=streaming),
                patch.object(rag, "build_rag_retrieval_only_pipeline", side_effect=pipeline),
                patch.object(rag, "_get_generator", return_value=Mock(run=Mock(return_value={"replies": [generated]}))),
                patch.object(routes, "stream_prompt", return_value=iter([generated[:25], generated[25:]])),
            ):
                if streaming:
                    events = [json.loads(line.removeprefix("data:").strip()) for line in routes._stream_chat(request, None)]
                    payload = next(event for event in events if event.get("done"))
                    answer = "".join(event.get("t", "") for event in events)
                else:
                    response = routes.chat(request, SimpleNamespace(headers={}))
                    payload = response.model_dump()
                    answer = payload["answer"]
            self.assertEqual(payload["suggested_case_ids"], ["synthetic-summary", "synthetic-actions"])
            self.assertEqual([case["id"] for case in payload["suggested_cases"]], payload["suggested_case_ids"])
            self.assertEqual(payload["sources"], [self.docs[0].content, self.docs[3].content])
            self.assertNotIn("prévention", answer)
            self.assertNotIn("reporting", answer)
            for number, case in enumerate(payload["suggested_cases"], 1):
                self.assertIn(f"{number}. {case['cas_utilisation']}\n", answer)
            self.assertIsNone(payload["pending_use_case_id"])
            # Client returns the displayed subset; "2" must be the actions case, not prevention.
            with patch.object(rag, "_enrich_case_from_document_store", side_effect=lambda case: dict(case)):
                detail = rag.get_rag_prompt_and_sources(
                    "2", [], payload["suggested_cases"], selected_domain_code=DOMAIN,
                    selected_sector="BTP", selected_intention="1",
                ) if streaming else rag.query_rag_haystack(
                    "2", [], payload["suggested_cases"], selected_domain_code=DOMAIN,
                    selected_sector="BTP", selected_intention="1",
                )
            detail_answer = detail[8] if streaming else detail[0]
            self.assertIn(self.docs[3].meta["cas_utilisation"], detail_answer)
            self.assertIn(self.docs[3].content, detail_answer)
            self.assertNotIn(self.docs[1].meta["cas_utilisation"], detail_answer)
        self.assertTrue(all(len(filters["conditions"]) == 3 for filters in filters_seen))

    def test_unparseable_model_list_never_exposes_unshown_selectable_ids(self):
        request = ChatRequest(message=QUERY, selected_domain_code=DOMAIN, selected_sector="BTP", selected_intention="1")
        for streaming in (False, True):
            with (
                self.subTest(streaming=streaming),
                patch.object(rag, "_retrieve_docs_for_question", return_value=self.docs),
                patch.object(rag, "_get_generator", return_value=Mock(run=Mock(return_value={"replies": ["Réponse sans liste"]}))),
                patch.object(routes, "stream_prompt", return_value=iter(["Réponse sans liste"])),
            ):
                if streaming:
                    events = [json.loads(line.removeprefix("data:").strip()) for line in routes._stream_chat(request, None)]
                    payload = next(event for event in events if event.get("done"))
                else:
                    payload = routes.chat(request, SimpleNamespace(headers={})).model_dump()
            self.assertEqual(payload["suggested_cases"], [] if streaming else None)
            self.assertEqual(payload["suggested_case_ids"], [])
            self.assertEqual(payload["sources"], [])


if __name__ == "__main__":
    unittest.main()
