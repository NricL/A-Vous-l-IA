import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from app import haystack_rag as rag


def user(text):
    return {"role": "user", "content": text}


def assistant(text):
    return {"role": "assistant", "content": text}


DOMAIN_QUESTION = "Dans quel domaine souhaitez-vous agir en priorité ?"
SECTOR_QUESTION = "Pour mieux cibler, pouvez-vous me dire dans quel secteur vous opérez ?"
INTENTION_QUESTION = "Quel est votre objectif principal dans ce domaine ?"
PROBLEM_QUESTION = "Pouvez-vous décrire le problème concret que vous rencontrez actuellement ?"
PROBLEM = "Je suis dans le BTP et je perds 3 heures à rédiger les comptes rendus de réunion."
INTENTIONS = ["Rédiger les comptes rendus", "Coordonner les interventions"]


class SyntheticRagTests(unittest.TestCase):
    def setUp(self):
        # Toutes les données sont fictives ; aucun accès Chroma, Azure ou fichier métier.
        for target in ("get_document_store", "_get_generator", "_retrieve_docs"):
            p = patch.object(rag, target, side_effect=AssertionError(f"Unexpected I/O: {target}"))
            p.start()
            self.addCleanup(p.stop)
        self.original_metadata_fetch = rag._fetch_documents_for_domaine
        p = patch.object(rag, "_fetch_documents_for_domaine", return_value=[])
        p.start()
        self.addCleanup(p.stop)
        p = patch.object(rag, "_get_q2_choices_list", return_value=INTENTIONS)
        p.start()
        self.addCleanup(p.stop)
        p = patch.object(rag.stats, "record")
        p.start()
        self.addCleanup(p.stop)

    def guided_history(self, problem=PROBLEM):
        return [
            assistant(rag.WELCOME_MESSAGE), user(problem),
            assistant(DOMAIN_QUESTION), user("13"),
            assistant(SECTOR_QUESTION), user("1"),
            assistant(INTENTION_QUESTION),
        ]


class SelectionRegressionTests(SyntheticRagTests):
    def test_same_numeric_reply_is_consumed_once_per_question(self):
        history = [
            assistant(DOMAIN_QUESTION), user("7"),
            assistant(SECTOR_QUESTION), user("2"),
            assistant(INTENTION_QUESTION), user("2"),
            assistant(PROBLEM_QUESTION),
        ]
        result = rag._resolve_current_selection_state(
            history, "Je perds 3 heures sur chaque compte rendu.", "finance_pilotage", "Commerce & retail", "2"
        )
        self.assertEqual(result[1:], ("finance_pilotage", "Commerce & retail", "2"))
        self.assertEqual(rag._get_domaine_code_from_history(result[0]), "finance_pilotage")

    def test_only_initial_numeric_reply_defaults_to_domain(self):
        self.assertEqual(
            rag._derive_selection_state_from_history([user("3")]), ("ressources_humaines", None, None)
        )
        history = self.guided_history() + [user("1"), assistant("Votre objectif et votre secteur sont validés.")]
        self.assertEqual(
            rag._resolve_current_selection_state(history, "2", None, None, None)[1:],
            ("activites_terrain", "BTP", "1"),
        )
        self.assertEqual(
            rag._resolve_current_selection_state([assistant(DOMAIN_QUESTION), user("13")], "2", None, None, None)[1:],
            ("activites_terrain", None, None),
        )

    def test_microtheme_question_does_not_reinterpret_intention_number(self):
        history = self.guided_history() + [user("1"), assistant("Q2.5 — Pour affiner, quel aspect vous concerne le plus ?")]
        self.assertEqual(
            rag._resolve_current_selection_state(history, "2", None, None, None)[1:],
            ("activites_terrain", "BTP", "1"),
        )

    def test_sector_number_is_not_reinterpreted_as_intention(self):
        history = self.guided_history()[:-1]
        self.assertEqual(rag._derive_selection_state_from_history(history), ("activites_terrain", "BTP", None))
        self.assertEqual(
            rag._derive_selection_state_from_history(history, "activites_terrain"),
            ("activites_terrain", "BTP", None),
        )

    def test_explicit_domain_correction_resets_dependent_choices(self):
        history = self.guided_history() + [user("1"), assistant(PROBLEM_QUESTION)]
        for correction in ("Finances & rentabilité", "je choisis le domaine 7"):
            with self.subTest(correction=correction):
                result = rag._resolve_current_selection_state(
                    history, correction, "activites_terrain", "BTP", "1"
                )
                self.assertEqual(result[1:], ("finance_pilotage", None, None))

    def test_historical_reset_does_not_resurrect_stale_client_state(self):
        history = self.guided_history() + [
            user("1"), user("Finances & rentabilité"), assistant(SECTOR_QUESTION)
        ]
        self.assertEqual(
            rag._resolve_current_selection_state(history, "inconnu", "activites_terrain", "BTP", "1")[1:],
            ("finance_pilotage", None, None),
        )
        history += [user("Chantiers & activités terrain"), assistant(SECTOR_QUESTION)]
        self.assertEqual(
            rag._resolve_current_selection_state(history, "inconnu", "activites_terrain", "BTP", "1")[1:],
            ("activites_terrain", None, None),
        )

    def test_compatible_client_answers_survive_incomplete_history(self):
        history = [assistant(DOMAIN_QUESTION), user("13"), assistant(PROBLEM_QUESTION)]
        self.assertEqual(
            rag._resolve_current_selection_state(history, PROBLEM, "activites_terrain", "BTP", "1")[1:],
            ("activites_terrain", "BTP", "1"),
        )

    def test_sector_correction_resets_intention_and_repeat_preserves_it(self):
        state = ("activites_terrain", "BTP", "1")
        self.assertEqual(rag._resolve_selection_state("Industrie", *state), ("activites_terrain", "Industrie", None))
        self.assertEqual(rag._resolve_selection_state("BTP", *state), state)
        self.assertEqual(rag._resolve_selection_state("Chantiers & activités terrain", *state), state)

    def test_intention_correction_and_numeric_backtracking(self):
        state = ("activites_terrain", "BTP", "1")
        self.assertEqual(
            rag._resolve_selection_state(INTENTIONS[1], *state),
            ("activites_terrain", "BTP", "2"),
        )
        self.assertEqual(
            rag._resolve_selection_state("7", *state, expected_step="domain"),
            ("finance_pilotage", None, None),
        )
        self.assertEqual(
            rag._resolve_selection_state("2", *state, expected_step="sector"),
            ("activites_terrain", "Services & artisanat", None),
        )

    def test_truncated_history_uses_client_state_before_current_correction(self):
        result = rag._resolve_current_selection_state(
            [assistant(INTENTION_QUESTION)], "2", "activites_terrain", "BTP", None
        )
        self.assertEqual(result[1:], ("activites_terrain", "BTP", "2"))
        result = rag._resolve_current_selection_state(
            [], "Finances & rentabilité", "activites_terrain", "BTP", "1"
        )
        self.assertEqual(result[1:], ("finance_pilotage", None, None))

    def test_unknown_ambiguous_and_narrative_selections_are_not_guessed(self):
        for text in ("1 ou 2", "99", "Je dirige une entreprise BTP", PROBLEM, "3 réunions par jour"):
            with self.subTest(text=text):
                self.assertEqual(
                    rag._resolve_selection_state(text, None, None, None, expected_step="domain"),
                    (None, None, None),
                )
        for text in ("industrie ou commerce", "service", "2 réunions", "9"):
            self.assertIsNone(rag._parse_sector_from_message(text, ["Industrie", "Services & artisanat"]))
        self.assertIsNone(rag._parse_intention_from_message("Rédiger", INTENTIONS))

    def test_numbered_label_and_explicit_selection_are_supported(self):
        for text in ("13. Chantiers & activités terrain", "Je choisis Chantiers & activités terrain"):
            self.assertEqual(rag._resolve_selection_state(text, None, None, None)[0], "activites_terrain")
        self.assertIsNone(rag._parse_domaine_from_message("7. Chantiers & activités terrain"))

    def test_explicit_early_sector_is_reused_only_after_domain_validation(self):
        history = [assistant(rag.WELCOME_MESSAGE), user(PROBLEM), assistant(DOMAIN_QUESTION)]
        self.assertEqual(rag._derive_selection_state_from_history(history), (None, None, None))
        self.assertEqual(
            rag._resolve_current_selection_state(history, "13", None, None, None)[1:],
            ("activites_terrain", "BTP", None),
        )
        history += [user("13"), assistant(INTENTION_QUESTION)]
        self.assertEqual(rag._derive_selection_state_from_history(history), ("activites_terrain", "BTP", None))
        self.assertEqual(
            rag._resolve_current_selection_state(history, "Finances & rentabilité", None, None, None)[1:],
            ("finance_pilotage", None, None),
        )

    def test_ambiguous_or_negated_early_sector_is_not_inferred(self):
        for text in ("Je travaille dans le BTP ou Industrie", "Je ne travaille pas dans le BTP"):
            history = [user(text), assistant(DOMAIN_QUESTION)]
            self.assertEqual(
                rag._resolve_current_selection_state(history, "13", None, None, None)[1:],
                ("activites_terrain", None, None),
            )

    def test_unknown_answer_does_not_advance_or_disable_clarification(self):
        history = self.guided_history() + [user("aucune idée"), assistant(INTENTION_QUESTION)]
        state = rag._resolve_current_selection_state(history, "1 ou 2", None, None, None)[1:]
        self.assertEqual(state, ("activites_terrain", "BTP", None))
        hint = rag._get_rag_hint(history)
        self.assertIn("doit être clarifié", hint)
        self.assertNotIn("ne pose plus", hint)


class ProblemReuseTests(SyntheticRagTests):
    def test_sector_specific_numbered_objective_uses_real_q2_order(self):
        docs = [
            SimpleNamespace(content="Synthetic", meta={"intention": "Analyser les stocks", "secteur": "Industrie"}),
            SimpleNamespace(content="Synthetic", meta={"intention": INTENTIONS[0], "secteur": "BTP"}),
        ]
        history = [user(PROBLEM), assistant(DOMAIN_QUESTION), user("13"), assistant(INTENTION_QUESTION)]
        with (
            patch.object(rag, "_fetch_documents_for_domaine", return_value=docs),
            patch.object(rag, "_get_q2_choices_list", side_effect=rag.get_q2_choices),
            patch.object(rag, "_retrieve_docs_for_question", return_value=[]) as retrieve,
        ):
            result = rag.get_rag_prompt_and_sources(
                "1. Rédiger les comptes rendus", history,
                selected_domain_code="activites_terrain", selected_sector="BTP",
            )
        self.assertEqual(result[5:8], ("activites_terrain", "BTP", "1"))
        self.assertEqual(retrieve.call_args.args, (PROBLEM,))

    def test_truncated_history_objective_selection_is_not_a_problem(self):
        for entry in (rag.get_rag_prompt_and_sources, rag.query_rag_haystack):
            with (
                self.subTest(entry=entry.__name__),
                patch.object(rag, "_retrieve_docs_for_question", return_value=[]) as retrieve,
                patch.object(rag, "_get_generator", return_value=Mock(run=Mock(return_value={"replies": ["Réponse"]}))),
            ):
                result = entry(INTENTIONS[0], [assistant(INTENTION_QUESTION)],
                               selected_domain_code="activites_terrain", selected_sector="BTP")
            retrieve.assert_not_called()
            if entry == rag.get_rag_prompt_and_sources:
                self.assertIn("prochaine question non résolue : Q3", result[0])

    def test_early_sector_numbered_objective_cannot_replace_original_problem(self):
        history = [user(PROBLEM), assistant(DOMAIN_QUESTION), user("13"), assistant(INTENTION_QUESTION)]
        for entry in (rag.get_rag_prompt_and_sources, rag.query_rag_haystack):
            with (
                self.subTest(entry=entry.__name__),
                patch.object(rag, "_retrieve_docs_for_question", return_value=[]) as retrieve,
                patch.object(rag, "_get_generator", return_value=Mock(run=Mock(return_value={"replies": ["Réponse"]}))),
            ):
                result = entry("1. Rédiger les comptes rendus", history)
            self.assertEqual(retrieve.call_args.args, (PROBLEM,))
            state = result[5:8] if entry == rag.get_rag_prompt_and_sources else result[8:11]
            self.assertEqual(state, ("activites_terrain", "BTP", "1"))
        history += [user("1. Rédiger les comptes rendus"), assistant(PROBLEM_QUESTION), user("1. Rédiger les comptes rendus")]
        self.assertEqual(rag._user_probleme_q3_text(history), PROBLEM)

    def test_acknowledgement_substrings_are_substantive_problems(self):
        for text in (
            "Je perds du temps à négocier avec les fournisseurs.",
            "L'éblouissement empêche de lire les notes.",
            "Oui, les notes restent dispersées.",
        ):
            self.assertFalse(rag._is_affirmation(text))
            for entry in (rag.get_rag_prompt_and_sources, rag.query_rag_haystack):
                with (
                    self.subTest(text=text, entry=entry.__name__),
                    patch.object(rag, "_retrieve_docs_for_question", return_value=[]) as retrieve,
                    patch.object(rag, "_get_generator", return_value=Mock(run=Mock(return_value={"replies": ["Réponse"]}))),
                ):
                    entry(text, [assistant(PROBLEM_QUESTION)], selected_domain_code="activites_terrain",
                          selected_sector="BTP", selected_intention="1")
                self.assertEqual(retrieve.call_args.args, (text,))

    def test_complete_client_state_accepts_substantive_problem_without_q3_prompt(self):
        text = "Les notes restent dispersées."
        for history in (
            [],
            [assistant("Parlons de votre situation.")],
            [assistant(DOMAIN_QUESTION), user("13"), assistant("Les choix précédents sont validés.")],
        ):
            for entry in (rag.get_rag_prompt_and_sources, rag.query_rag_haystack):
                with (
                    self.subTest(history=history, entry=entry.__name__),
                    patch.object(rag, "_retrieve_docs_for_question", return_value=[]) as retrieve,
                    patch.object(rag, "_get_generator", return_value=Mock(run=Mock(return_value={"replies": ["Réponse"]}))),
                ):
                    result = entry(text, history, selected_domain_code="activites_terrain",
                                   selected_sector="BTP", selected_intention="1")
                self.assertEqual(retrieve.call_args.args, (text,))
                if entry == rag.get_rag_prompt_and_sources:
                    self.assertIn(f"Problème déjà exprimé (texte utilisateur): {text}", result[0])

    def test_q3_details_noun_is_not_a_request_to_expand_a_case(self):
        history = self.guided_history(problem="Bonjour") + [user("1"), assistant(PROBLEM_QUESTION)]
        for text in ("Les comptes rendus manquent de détails.", "Les notes sont imprécises."):
            for context in (history, []):
                for entry in (rag.get_rag_prompt_and_sources, rag.query_rag_haystack):
                    with (
                        self.subTest(text=text, history=context, entry=entry.__name__),
                        patch.object(rag, "_retrieve_docs_for_question", return_value=[]) as retrieve,
                        patch.object(rag, "_retrieve_docs") as detail_fallback,
                        patch.object(rag, "_get_generator", return_value=Mock(run=Mock(return_value={"replies": ["Réponse"]}))),
                    ):
                        entry(text, context, selected_domain_code="activites_terrain", selected_sector="BTP",
                              selected_intention="1")
                    self.assertEqual(retrieve.call_args.args, (text,))
                    detail_fallback.assert_not_called()
        for request in ("Détails", "Le détail", "Détails sur le compte rendu", "Pouvez-vous me donner plus de détails ?"):
            self.assertTrue(rag._is_detail_request(request), request)

    def test_no_theme_fallback_during_q3_or_from_previous_objective_number(self):
        history = self.guided_history(problem="Bonjour") + [user("1"), assistant(PROBLEM_QUESTION)]
        for entry in (rag.get_rag_prompt_and_sources, rag.query_rag_haystack):
            with (
                self.subTest(entry=entry.__name__),
                patch.object(rag, "_retrieve_docs_for_question", return_value=[]) as retrieve,
                patch.object(rag, "_retrieve_docs") as detail_fallback,
                patch.object(rag, "_get_generator", return_value=Mock(run=Mock(return_value={"replies": ["Réponse"]}))),
            ):
                entry("Détaille celui sur les réunions", history,
                      selected_domain_code="activites_terrain", selected_sector="BTP", selected_intention="1")
            retrieve.assert_not_called()
            detail_fallback.assert_not_called()

    def test_complete_client_state_still_excludes_choices_details_and_acknowledgements(self):
        state = ("activites_terrain", "BTP", "1")
        for text in ("oui", "OK, merci !", "vas-y", "1", "1. Rédiger les comptes rendus",
                     "Rédiger les comptes rendus", "détaille le point 1", "je ne sais pas"):
            with self.subTest(text=text):
                self.assertEqual(rag._user_probleme_q3_text([user(text)], selected_state=state), "")
        for text in ("oui", "OK, merci !", "vas-y", "Oui s'il te plaît", "d'accord"):
            self.assertTrue(rag._is_affirmation(text))

    def test_early_problem_is_preserved_verbatim_not_replaced_by_labels(self):
        history = self.guided_history() + [user(INTENTIONS[0])]
        self.assertEqual(rag._user_probleme_q3_text(history), PROBLEM)
        self.assertEqual(rag._user_probleme_q3_text(history + [user("1")], "1"), PROBLEM)
        self.assertEqual(
            rag._user_probleme_q3_text([user("Je dirige une entreprise dans le BTP.")]), ""
        )

    def test_explicit_problem_answer_does_not_require_keyword_heuristic(self):
        history = self.guided_history() + [
            user("1"), assistant(PROBLEM_QUESTION), user("Les notes restent dispersées.")
        ]
        self.assertEqual(rag._user_probleme_q3_text(history), "Les notes restent dispersées.")

    def test_both_entrypoints_retrieve_problem_not_numeric_objective(self):
        doc = SimpleNamespace(id="synthetic", content="Description synthétique du cas.", meta={})
        for streaming in (True, False):
            with (
                self.subTest(streaming=streaming),
                patch.object(rag, "_retrieve_docs_for_question", return_value=[doc]) as retrieve,
                patch.object(rag, "_get_generator", return_value=Mock(run=Mock(return_value={"replies": ["Réponse"]}))),
            ):
                entry = rag.get_rag_prompt_and_sources if streaming else rag.query_rag_haystack
                result = entry("1", self.guided_history(), selected_domain_code="activites_terrain", selected_sector="BTP")
                self.assertEqual(len(result), 11)
                self.assertEqual(result[5:8] if streaming else result[8:11], ("activites_terrain", "BTP", "1"))
                retrieve.assert_called_once_with(
                    PROBLEM, selected_domain_code="activites_terrain", selected_intention="1", selected_sector="BTP"
                )
                if streaming:
                    self.assertIn(PROBLEM, result[0])
                    self.assertIn("ne repose aucune question déjà résolue", result[0])

    def test_no_problem_means_q3_not_numeric_retrieval(self):
        history = self.guided_history(problem="Bonjour")
        with patch.object(rag, "_retrieve_docs_for_question") as retrieve:
            result = rag.get_rag_prompt_and_sources("1", history)
        retrieve.assert_not_called()
        self.assertIn("prochaine question non résolue : Q3", result[0])

    def test_empty_retrieval_does_not_repeat_completed_questions(self):
        with patch.object(rag, "_retrieve_docs_for_question", return_value=[]):
            result = rag.get_rag_prompt_and_sources("1", self.guided_history())
        self.assertIn("Aucun cas ne correspond aux filtres validés", result[0])
        self.assertNotIn("Pose UNIQUEMENT la prochaine question non résolue", result[0])


class DetailPayloadTests(SyntheticRagTests):
    def test_polite_and_imperative_detail_requests_use_existing_case_not_problem_retrieval(self):
        cases = [{"id": "synthetic"}]
        payload = ("Détail exact", ["source"], ["synthetic"], ["contenu"], [{}])
        for question in (
            "Je voudrais plus de détails.", "Donne-moi plus de détails.",
            "Je veux plus de détails, merci.", "Donnez-moi davantage de détails s'il vous plaît.",
            "J'aimerais obtenir plus de détails.",
        ):
            self.assertTrue(rag._is_detail_request(question), question)
            self.assertTrue(rag._is_explicit_detail_command(question), question)
            for entry in (rag.get_rag_prompt_and_sources, rag.query_rag_haystack):
                with (
                    self.subTest(question=question, entry=entry.__name__),
                    patch.object(rag, "_build_niveau2_detail_payload", return_value=payload) as detail,
                    patch.object(rag, "build_parcours_info", return_value={}),
                    patch.object(rag, "_retrieve_docs_for_question") as retrieve,
                ):
                    result = entry(question, [assistant("Voici le cas proposé.")], cases,
                                   selected_domain_code="activites_terrain", selected_sector="BTP",
                                   selected_intention="1")
                detail.assert_called_once()
                self.assertEqual(detail.call_args.args[0], 0)
                retrieve.assert_not_called()
                self.assertEqual(result[8] if entry == rag.get_rag_prompt_and_sources else result[0], payload[0])

    def test_explicit_detail_command_still_selects_correct_displayed_case(self):
        cases = [{"id": "first"}, {"id": "second"}]
        payload = ("Détail du second", ["source"], ["first", "second"], ["un", "deux"], [{}, {}])
        for entry in (rag.get_rag_prompt_and_sources, rag.query_rag_haystack):
            with (
                self.subTest(entry=entry.__name__),
                patch.object(rag, "_build_niveau2_detail_payload", return_value=payload) as detail,
                patch.object(rag, "build_parcours_info", return_value={}),
            ):
                result = entry("détaille le 2", [assistant("Voici les cas proposés.")], cases)
            self.assertEqual(detail.call_args.args[0], 1)
            self.assertEqual(result[8] if entry == rag.get_rag_prompt_and_sources else result[0], payload[0])

    def test_rich_short_content_stays_verbatim_in_both_tuple_formats(self):
        for content in ("", "Court"):
            for detail_field in ("description_cas_utilisation", "declencheurs_typiques"):
                case = {"id": "synthetic", "content": content, "cas_utilisation": "Titre fictif",
                        detail_field: "Texte exact ; ne pas reformuler."}
                with (
                    self.subTest(content=content, field=detail_field),
                    patch.object(rag, "_enrich_case_from_document_store", side_effect=lambda c: dict(c)),
                    patch.object(rag, "build_parcours_info", return_value={"parcours_url": "https://example.invalid/action", "cta_label": "Démarrer"}),
                ):
                    stream = rag.get_rag_prompt_and_sources("1", [], [case], selected_domain_code="activites_terrain", selected_sector="BTP", selected_intention="1")
                    nonstream = rag.query_rag_haystack("1", [], [case], selected_domain_code="activites_terrain", selected_sector="BTP", selected_intention="1")
                self.assertEqual(len(stream), 11)
                self.assertEqual(len(nonstream), 11)
                self.assertEqual(stream[8], nonstream[0])
                self.assertIn(case[detail_field], stream[8])
                self.assertEqual(stream[1:5], nonstream[1:5])
                self.assertEqual(stream[5:8], nonstream[8:11])
                self.assertEqual(nonstream[5:8], (None, None, None))
                self.assertEqual(stream[9:11], ("https://example.invalid/action", "Démarrer"))

    def test_guard_still_rejects_short_unstructured_case(self):
        with patch.object(rag, "_enrich_case_from_document_store", side_effect=lambda c: dict(c)):
            for case in ({"content": "court"}, {"content": "", "cas_utilisation": "Titre seul"}):
                self.assertIsNone(rag._build_niveau2_detail_payload(0, [case], [], "1"))

    def test_nonstream_pending_and_offer_details_keep_eleven_fields(self):
        payload = ("Détail", ["source"], ["synthetic"], ["court"], [{}])
        cases = [{"id": "synthetic", "content": "court"}]
        with patch.object(rag, "_build_niveau2_detail_payload", return_value=payload):
            for kwargs, history in (
                ({"pending_action": "expand_details", "pending_use_case_id": "synthetic"}, []),
                ({}, [assistant("Souhaitez-vous le détail du 1er ?")]),
            ):
                result = rag.query_rag_haystack("oui", history, cases, **kwargs)
                self.assertEqual(result, payload + (None,) * 6)


class RetrievalRegressionTests(SyntheticRagTests):
    def test_q2_sector_variants_are_matched_by_prefilters_not_post_retrieval(self):
        def matches(doc, node):
            if "conditions" in node:
                values = [matches(doc, child) for child in node["conditions"]]
                return all(values) if node["operator"] == "AND" else any(values)
            return doc.meta.get(node["field"].removeprefix("meta.")) == node["value"]

        for raw in ("Multi-sectoriel", "MULTI SECTORIEL", "BTP / Industrie",
                    " bTp ; Industrie ", "BTP,Industrie", "BTP|Industrie"):
            wanted = SimpleNamespace(id="wanted", content="Comptes rendus", meta={
                "domaine": "activites_terrain", "intention": INTENTIONS[0], "Secteur": raw,
            })
            unrelated_sector = SimpleNamespace(id="other-sector", content="Comptes rendus", meta={
                "domaine": "activites_terrain", "intention": INTENTIONS[0], "Secteur": "Commerce & retail",
            })
            unrelated_intention = SimpleNamespace(id="other-intention", content="Comptes rendus", meta={
                "domaine": "activites_terrain", "intention": "Autre intention", "Secteur": "BTP",
            })
            unrelated_domain = SimpleNamespace(id="other-domain", content="Comptes rendus", meta={
                "domaine": "finance_pilotage", "intention": INTENTIONS[0], "Secteur": raw,
            })
            corpus = [wanted, unrelated_sector, unrelated_intention, unrelated_domain]
            captured = []

            def pipeline(filters=None):
                captured.append(filters)
                return Mock(run=Mock(return_value={"retriever": {"documents": [
                    doc for doc in corpus if matches(doc, filters)
                ]}}))

            with (
                self.subTest(raw=raw),
                patch.object(rag, "_fetch_documents_for_domaine", return_value=corpus[:3]) as metadata,
                patch.object(rag, "_get_q2_choices_list", side_effect=rag.get_q2_choices),
                patch.object(rag, "build_rag_retrieval_only_pipeline", side_effect=pipeline),
            ):
                choices = rag.get_q2_choices("activites_terrain", "BTP")
                self.assertIn(INTENTIONS[0], choices)
                intention = str(choices.index(INTENTIONS[0]) + 1)
                self.assertEqual(rag._retrieve_docs_for_question(PROBLEM, "activites_terrain", intention, "BTP"), [wanted])
                self.assertTrue(any(call.kwargs.get("metadata_only") for call in metadata.call_args_list))
            for filters in captured:
                self.assertEqual(len(filters["conditions"]), 3)
                self.assertFalse(matches(unrelated_sector, filters))
                self.assertFalse(matches(unrelated_intention, filters))
                self.assertFalse(matches(unrelated_domain, filters))

    def test_metadata_sector_expansion_does_not_fall_back_to_vector_search(self):
        with (
            patch.object(rag, "get_document_store", return_value=Mock(filter_documents=Mock(return_value=[]))),
            patch.object(rag, "_retrieve_docs") as vector,
        ):
            self.assertEqual(self.original_metadata_fetch("activites_terrain", metadata_only=True), [])
        vector.assert_not_called()

    def test_detail_fallback_also_prefilters_domain_intention_and_sector(self):
        history = self.guided_history() + [
            user("1"), assistant(PROBLEM_QUESTION), user(PROBLEM),
            assistant("Voici les cas proposés. Souhaitez-vous approfondir l'un de ces cas ?"),
        ]
        for entry in (rag.get_rag_prompt_and_sources, rag.query_rag_haystack):
            with (
                self.subTest(entry=entry.__name__),
                patch.object(rag, "_retrieve_docs", return_value=[]) as retrieve,
                patch.object(rag, "_retrieve_docs_for_question", return_value=[]),
                patch.object(rag, "_get_generator", return_value=Mock(run=Mock(return_value={"replies": ["Réponse"]}))),
            ):
                entry("Détaille celui sur les réunions", history)
                self.assertEqual(retrieve.call_args.args, (PROBLEM,))
                filters = retrieve.call_args.kwargs["filters"]
                self.assertEqual(len(filters["conditions"]), 3)
                self.assertIn("BTP", [c["value"] for c in filters["conditions"][2]["conditions"]])

    def test_unknown_intention_cannot_silently_remove_prefilter(self):
        with patch.object(rag, "build_rag_retrieval_only_pipeline") as retrieve:
            self.assertEqual(rag._retrieve_docs_for_question(PROBLEM, "activites_terrain", "99", "BTP"), [])
        retrieve.assert_not_called()

    def test_every_sector_fallback_keeps_all_prefilters_and_stops_empty(self):
        captured = []

        def pipeline(filters=None):
            captured.append(filters)
            return Mock(run=Mock(return_value={"retriever": {"documents": []}}))

        with patch.object(rag, "build_rag_retrieval_only_pipeline", side_effect=pipeline):
            self.assertEqual(rag._retrieve_docs_for_question(PROBLEM, "activites_terrain", "1", "BTP"), [])
        self.assertEqual(len(captured), 2)
        for filters in captured:
            self.assertEqual(filters["operator"], "AND")
            self.assertEqual(len(filters["conditions"]), 3)
            domain, intention, sector = filters["conditions"]
            self.assertIn("activites_terrain", [c["value"] for c in domain["conditions"]])
            self.assertEqual({c["value"] for c in intention["conditions"]}, {INTENTIONS[0]})
            self.assertIn("BTP", [c["value"] for c in sector["conditions"]])

    def test_repeated_background_word_cannot_outrank_query_coverage(self):
        relevant = SimpleNamespace(content="Compte rendu réunion chantier", meta={})
        unrelated = SimpleNamespace(content="Prévention chantier " + "chantier " * 30, meta={"secteur": "chantier"})
        self.assertEqual(
            rag._rank_docs_by_query_overlap("compte rendu réunion chantier", [unrelated, relevant]),
            [relevant, unrelated],
        )

    def test_lexical_ranking_preserves_semantic_candidates_and_stable_ties(self):
        docs = [SimpleNamespace(content="Synthèse des échanges", meta={}), SimpleNamespace(content="Procès-verbal", meta={})]
        self.assertEqual(rag._rank_docs_by_query_overlap("compte rendu", docs), docs)
        self.assertEqual(rag._rank_docs_by_query_overlap("1", docs), docs)


if __name__ == "__main__":
    unittest.main()
