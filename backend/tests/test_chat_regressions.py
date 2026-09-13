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
        rag._invalidate_metadata_cache()
        self.addCleanup(rag._invalidate_metadata_cache)
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
    def test_french_initial_needs_survive_numeric_guidance_without_topic_keywords(self):
        for text in (
            "Je tiens un magasin de décoration et je voudrais réduire mes invendus.",
            "Je tiens un magasin de décoration et souhaite écouler mes invendus.",
            "J'ai un magasin de décoration. Comment écouler les articles qui ne se vendent plus ?",
            "Bonjour, je souhaite vendre les articles qui restent en rayon.",
            "Nous voulons convertir nos notes de visite en compte rendu.",
            "On voudrait mieux répondre aux demandes des clients.",
            "J'aimerais rapprocher nos factures des paiements reçus.",
            "Je cherche à comparer les propositions reçues.",
            "Je dois transformer mes notes de réunion de chantier en compte rendu.",
            "Les invendus s'accumulent dans ma boutique.",
            "Mes clients n'obtiennent jamais de réponse.",
            "J'ai des invendus dans mon magasin de décoration.",
            "Réduire les articles qui restent sur les étagères.",
        ):
            history = self.guided_history(text) + [user("1")]
            with self.subTest(text=text):
                self.assertEqual(rag._user_probleme_q3_text(history), text)
                self.assertEqual(rag._derive_selection_state_from_history(history),
                                 ("activites_terrain", "BTP", "1"))

    def test_social_profession_and_control_turns_never_become_a_need(self):
        for text in (
            "Bonjour !", "Hello", "Bonsoir, merci !", "Merci pour votre aide.",
            "Je suis commerçante.", "Bonjour. Je dirige un magasin de décoration.",
            "Je gère une boutique.", "Je suis responsable marketing et communication.",
            "Je suis commerçante. Je tiens une boutique de décoration.",
            "Je suis artisan et j'exerce dans le BTP.",
            "Je travaille pour un cabinet de conseil.", "Je ne travaille pas dans le BTP.",
            "J'ai un magasin de décoration.", "J'ai une boutique.", "Nous avons une entreprise.",
            "Je ne sais pas encore", "OK, merci !", "pas de problème", "1",
            "Détaille le point 1", "Pouvez-vous me donner plus de détails ?",
        ):
            for state, prefix in (
                (None, []),
                (("activites_terrain", "BTP", "1"), [assistant(PROBLEM_QUESTION)]),
            ):
                with self.subTest(text=text, state=state):
                    self.assertEqual(rag._user_probleme_q3_text(prefix + [user(text)], selected_state=state), "")

    def test_initial_need_survives_domain_correction_but_obsolete_q3_does_not(self):
        initial = "Je voudrais réduire les articles invendus dans mon magasin."
        correction = [user("Finances & rentabilité"), assistant(SECTOR_QUESTION), user("2"),
                      assistant(INTENTION_QUESTION), user("1")]
        history = self.guided_history(initial) + [user("1")]
        self.assertEqual(rag._user_probleme_q3_text(history + correction), initial)
        explicit_q3 = history + [assistant(PROBLEM_QUESTION), user("Les notes restent dispersées.")]
        self.assertEqual(rag._user_probleme_q3_text(explicit_q3 + correction), "")
        for correction_text in ("Industrie", INTENTIONS[1]):
            self.assertEqual(rag._user_probleme_q3_text(explicit_q3 + [user(correction_text)]), "")

    def test_latest_meaningful_clarification_replaces_initial_need_during_guidance(self):
        clarification = "J'aimerais comparer les commandes aux quantités réellement vendues."
        history = self.guided_history("Je voudrais réduire les invendus.")[:-1] + [
            user(clarification), assistant(INTENTION_QUESTION), user("1"),
        ]
        self.assertEqual(rag._user_probleme_q3_text(history), clarification)
        self.assertEqual(rag._user_probleme_q3_text(history + [user("OK, merci !")]), clarification)

    def test_early_need_replay_respects_partial_history_and_domains_without_sector(self):
        need = "J'aimerais comparer les propositions reçues."
        for domain, sector in (("activites_terrain", "BTP"), ("direction_strategie", None)):
            for entry in (rag.get_rag_prompt_and_sources, rag.query_rag_haystack):
                with (
                    self.subTest(domain=domain, entry=entry.__name__),
                    patch.object(rag, "_retrieve_docs_for_question", return_value=[]) as retrieve,
                ):
                    entry("1", [user(need), assistant(INTENTION_QUESTION)],
                          selected_domain_code=domain, selected_sector=sector)
                retrieve.assert_called_once_with(
                    need, selected_domain_code=domain, selected_intention="1", selected_sector=sector,
                )
        self.assertEqual(rag._user_probleme_q3_text(
            [assistant(INTENTION_QUESTION), user("1")],
            selected_state=("activites_terrain", "BTP", "1"),
        ), "")

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


class IndexedSectorMenuTests(SyntheticRagTests):
    domain = "activites_terrain"

    def doc(self, sector, *, domain=None, field="secteur"):
        return SimpleNamespace(
            id=f"synthetic-{sector}", content="Exemple fictif.",
            meta={"domaine": domain or self.domain, field: sector, "intention": INTENTIONS[0]},
        )

    def test_indexed_sector_extends_menu_without_changing_existing_numbers(self):
        original = rag.SECTEURS_PAR_DOMAINE[self.domain] + ["Autre / Non spécifique"]
        docs = [
            self.doc("Atelier Zêta"), self.doc("Atelier Alpha"),
            self.doc("atelier zeta"), self.doc("btp"), self.doc("Services et artisanat"),
            self.doc("Santé & médico-social", field="Sector"),
            self.doc("Hôtellerie et tourisme", field="secteur_activité"),
            self.doc("Atelier Interdit", domain="production"),
        ]
        expected = original + ["Atelier Alpha", "Atelier Zêta", "Hôtellerie & tourisme"]
        for corpus in (docs, list(reversed(docs))):
            with patch.object(rag, "_fetch_documents_for_domaine", return_value=corpus) as metadata:
                choices = rag.get_q15_choices(self.domain)
            self.assertEqual(choices, expected)
            metadata.assert_called_once_with(self.domain, metadata_only=True)
        self.assertEqual(rag.SECTEURS_PAR_DOMAINE[self.domain], original[:-1])

    def test_compounds_and_multisector_use_same_rules_in_menu_q2_and_prefilters(self):
        compound = "Atelier Alpha / BTP; Santé et médico-social | Multi sectoriel"
        docs = [self.doc(compound), self.doc("Autre / Non spécifique; BTP")]
        with patch.object(rag, "_fetch_documents_for_domaine", return_value=docs):
            choices = rag.get_q15_choices(self.domain)
            self.assertEqual(choices[-1], "Atelier Alpha")
            self.assertEqual(len(choices), len(rag.SECTEURS_PAR_DOMAINE[self.domain]) + 2)
            for sector in ("Atelier Alpha", "BTP", "Santé & médico-social"):
                self.assertTrue(rag._doc_matches_sector(docs[0], sector))
                self.assertEqual(rag._get_doc_sector_score(docs[0], sector), 3)
                self.assertEqual(rag.get_q2_choices(self.domain, sector), [INTENTIONS[0]])
                filters = rag._build_retrieval_filters(self.domain, "1", sector)
                self.assertIn(compound, {c["value"] for c in filters["conditions"][-1]["conditions"]})
            self.assertFalse(rag._doc_matches_sector(docs[0], "Atelier Inconnu"))
            self.assertTrue(rag._doc_matches_sector(docs[0], "Atelier Inconnu", include_multisector=True))
            self.assertEqual(rag.get_q2_choices(self.domain, "Autre / Non spécifique"), [INTENTIONS[0]])
        self.assertFalse(rag._is_multisector_label("Pas multi-sectoriel"))
        aliases = self.doc("Multi-sectoriel")
        aliases.meta["Sector"] = "Atelier Alpha"
        self.assertEqual(rag._get_doc_sector_score(aliases, "Atelier Alpha"), 3)

    def test_empty_index_keeps_static_menu_and_no_match_intentions(self):
        with patch.object(rag, "_fetch_documents_for_domaine", return_value=[]):
            self.assertEqual(
                rag.get_q15_choices(self.domain),
                rag.SECTEURS_PAR_DOMAINE[self.domain] + ["Autre / Non spécifique"],
            )
            self.assertTrue(rag.get_q2_choices(self.domain, "Atelier Alpha")["fallback"])

    def test_skip_domains_never_read_sector_metadata(self):
        with patch.object(rag, "_fetch_documents_for_domaine") as metadata:
            for domain in rag.DOMAINES_SANS_SECTEURS + ["domaine_inconnu"]:
                self.assertIsNone(rag.get_q15_choices(domain))
                self.assertEqual(rag._get_secteur_choices_affichage([], domain), "")
            for domain in rag.DOMAINES_SANS_SECTEURS:
                self.assertEqual(
                    rag._resolve_selection_state("1", domain, None, None, expected_step="intention"),
                    (domain, None, "1"),
                )
        metadata.assert_not_called()

    def test_indexed_sector_resolves_text_numbers_early_mentions_and_replay(self):
        with patch.object(rag, "_fetch_documents_for_domaine", return_value=[self.doc("Atelier Alpha")]):
            choices = rag.get_q15_choices(self.domain)
            number = str(choices.index("Atelier Alpha") + 1)
            for text in (number, f"{number}. Atelier Alpha", "Je choisis atelier alpha"):
                history = [assistant(DOMAIN_QUESTION), user("13"), assistant(SECTOR_QUESTION), user(text)]
                self.assertEqual(rag._get_sector_from_history(history), "Atelier Alpha")
                self.assertEqual(rag._derive_selection_state_from_history(history), (self.domain, "Atelier Alpha", None))
            early = [user("Je travaille dans le secteur Atelier Alpha."), assistant(DOMAIN_QUESTION)]
            self.assertEqual(
                rag._resolve_current_selection_state(early, "13", None, None, None)[1:],
                (self.domain, "Atelier Alpha", None),
            )
            self.assertIsNone(rag._parse_sector_from_message("Atelier Alpha ou BTP", choices))
            self.assertEqual(
                rag._parse_sector_from_message("Services et artisanat", choices), "Services & artisanat"
            )

    def test_replay_uses_displayed_label_when_dynamic_numbers_shift(self):
        with patch.object(rag, "_fetch_documents_for_domaine", return_value=[self.doc("Atelier Zêta")]):
            old_menu = rag._get_secteur_choices_affichage([], self.domain)
            number = str(rag.get_q15_choices(self.domain).index("Atelier Zêta") + 1)
        history = [
            assistant(DOMAIN_QUESTION), user("13"),
            assistant(SECTOR_QUESTION + "\n" + old_menu), user(number),
        ]
        with patch.object(rag, "_fetch_documents_for_domaine",
                          return_value=[self.doc("Atelier Alpha"), self.doc("Atelier Zêta")]):
            self.assertEqual(rag._get_sector_from_history(history), "Atelier Zêta")
            self.assertEqual(
                rag._get_sector_from_history(history[:-1] + [user(number + ". Atelier Zêta")]), "Atelier Zêta"
            )
            self.assertEqual(
                rag._derive_selection_state_from_history(history[:-1] + [user("domaine 7")]),
                ("finance_pilotage", None, None),
            )
            self.assertIsNone(
                rag._get_sector_from_history(history[:-1] + [user(number + ". Atelier Alpha")])
            )
        with patch.object(rag, "_fetch_documents_for_domaine", return_value=[self.doc("Atelier Alpha")]):
            self.assertIsNone(rag._get_sector_from_history(history))

    def test_markdown_sector_numbers_replay_the_displayed_label_after_refresh(self):
        number = len(rag.SECTEURS_PAR_DOMAINE[self.domain]) + 2
        for line in (
            f"**{number}.** Atelier Zêta",
            f"**{number}**. **Atelier Zêta**",
            f"**{number}. Atelier Zêta**",
            f"{number}) **Atelier Zêta**",
            f"__{number}__ __Atelier Zêta__",
            f"- **{number}.** **Atelier Zêta**",
            f"### **{number}.** Atelier Zêta",
        ):
            history = [
                assistant(DOMAIN_QUESTION), user("13"),
                assistant(SECTOR_QUESTION + "\n" + line), user(str(number)),
            ]
            with (
                self.subTest(line=line),
                patch.object(rag, "_fetch_documents_for_domaine",
                             return_value=[self.doc("Atelier Alpha"), self.doc("Atelier Zêta")]),
            ):
                self.assertEqual(rag._get_sector_from_history(history), "Atelier Zêta")
            with patch.object(rag, "_fetch_documents_for_domaine", return_value=[self.doc("Atelier Alpha")]):
                self.assertIsNone(rag._get_sector_from_history(history))

    def test_http_and_streaming_use_identical_indexed_menu_and_selection(self):
        with (
            patch.object(rag, "_fetch_documents_for_domaine", return_value=[self.doc("Atelier Alpha")]),
            patch.object(rag, "_get_generator", return_value=Mock(run=Mock(return_value={"replies": ["Réponse"]}))) as generator,
            patch.object(rag, "_retrieve_docs_for_question") as retrieve,
        ):
            menu = rag._get_secteur_choices_affichage([], self.domain)
            number = str(rag.get_q15_choices(self.domain).index("Atelier Alpha") + 1)
            for entry in (rag.get_rag_prompt_and_sources, rag.query_rag_haystack):
                result = entry("13", [assistant(DOMAIN_QUESTION)])
                response = result[8] if entry == rag.get_rag_prompt_and_sources else result[0]
                self.assertIn(menu, response)
                self.assertIn("dans quel secteur", response)
                if entry == rag.get_rag_prompt_and_sources:
                    self.assertIn("prochaine question non résolue : Q1.5", result[0])
                result = entry(number, [
                    assistant(DOMAIN_QUESTION), user("13"), assistant(SECTOR_QUESTION + "\n" + menu),
                ])
                state = result[5:8] if entry == rag.get_rag_prompt_and_sources else result[8:11]
                self.assertEqual(state, (self.domain, "Atelier Alpha", None))
            generator.assert_not_called()
            retrieve.assert_not_called()

    def test_indexed_sector_advances_to_objective_then_problem_without_model_revalidation(self):
        with (
            patch.object(rag, "_fetch_documents_for_domaine", return_value=[self.doc("Atelier Alpha")]),
            patch.object(rag, "_get_generator", side_effect=AssertionError("No model for catalogue questions")),
            patch.object(rag, "_retrieve_docs_for_question", side_effect=AssertionError("No retrieval before problem")),
        ):
            menu = rag._get_secteur_choices_affichage([], self.domain)
            initial = [
                assistant(DOMAIN_QUESTION), user("13"),
                assistant(SECTOR_QUESTION + "\n" + menu),
            ]
            for entry in (rag.get_rag_prompt_and_sources, rag.query_rag_haystack):
                result = entry("Atelier Alpha", initial)
                question = result[8] if entry == rag.get_rag_prompt_and_sources else result[0]
                self.assertTrue(question.startswith("Quel est votre objectif principal"))
                self.assertIn(INTENTIONS[0], question)
                self.assertNotIn("dans quel secteur", question)
                history = initial + [user("Atelier Alpha"), assistant(question)]
                result = entry("1", history)
                question = result[8] if entry == rag.get_rag_prompt_and_sources else result[0]
                self.assertIn("problème concret", question)
                self.assertNotIn("objectif principal", question)

    def test_metadata_cache_reads_all_domain_aliases_and_reuses_results(self):
        docs = [self.doc("Atelier Alpha"), self.doc("Atelier Interdit", domain="production")]
        docs[0].meta["domaine_label_fr"] = docs[0].meta.pop("domaine")
        store = Mock(filter_documents=Mock(return_value=docs))
        with patch.object(rag, "get_document_store", return_value=store):
            first = self.original_metadata_fetch(self.domain, metadata_only=True)
            first.clear()
            self.assertEqual(self.original_metadata_fetch(self.domain, metadata_only=True), docs[:1])
        store.filter_documents.assert_called_once()
        fields = {c["field"] for c in store.filter_documents.call_args.kwargs["filters"]["conditions"]}
        self.assertEqual(fields, {f"meta.{key}" for key in rag.DOMAINE_META_KEYS})

    def test_menu_and_q2_share_complete_metadata_catalogue_without_vector_fallback(self):
        first = self.doc("BTP")
        second = self.doc("Atelier Alpha")
        second.meta["domaine_label_fr"] = second.meta.pop("domaine")
        second.meta["intention"] = "Objectif fictif Alpha"
        store = Mock(filter_documents=Mock(return_value=[first, second]))
        with (
            patch.object(rag, "get_document_store", return_value=store),
            patch.object(rag, "_fetch_documents_for_domaine", side_effect=self.original_metadata_fetch),
            patch.object(rag, "_retrieve_docs") as vector,
        ):
            self.assertIn("Atelier Alpha", rag.get_q15_choices(self.domain))
            self.assertEqual(rag.get_q2_choices(self.domain, "Atelier Alpha"), ["Objectif fictif Alpha"])
            self.assertTrue(rag.get_q2_choices(self.domain, "Atelier Inconnu")["fallback"])
            rag._build_retrieval_filters(self.domain, selected_sector="Atelier Alpha")
        store.filter_documents.assert_called_once()
        vector.assert_not_called()

    def test_only_empty_nonmetadata_reads_keep_legacy_domain_fallback(self):
        own = self.doc("Atelier Alpha")
        other = self.doc("Atelier Interdit", domain="production")
        store = Mock(filter_documents=Mock(return_value=[]))
        with (
            patch.object(rag, "get_document_store", return_value=store),
            patch.object(rag, "_retrieve_docs", return_value=[[own, other]]) as vector,
        ):
            self.assertEqual(self.original_metadata_fetch(self.domain, metadata_only=True), [])
            vector.assert_not_called()
            self.assertEqual(self.original_metadata_fetch(self.domain, top_k_fallback=12), [own])
        vector.assert_called_once_with(rag._get_domaine_label(self.domain), top_k=12)
        store.filter_documents.assert_called_once()

    def test_metadata_error_propagates_is_not_cached_and_never_uses_vectors(self):
        store = Mock(filter_documents=Mock(side_effect=[RuntimeError("synthetic lookup failure"), []]))
        with (
            patch.object(rag, "get_document_store", return_value=store),
            patch.object(rag, "_fetch_documents_for_domaine", side_effect=self.original_metadata_fetch),
            patch.object(rag, "_retrieve_docs") as vector,
        ):
            with self.assertRaisesRegex(RuntimeError, "synthetic lookup failure"):
                rag.get_q15_choices(self.domain)
            self.assertEqual(
                rag.get_q15_choices(self.domain),
                rag.SECTEURS_PAR_DOMAINE[self.domain] + ["Autre / Non spécifique"],
            )
        self.assertEqual(store.filter_documents.call_count, 2)
        vector.assert_not_called()
        rag._invalidate_metadata_cache()
        store.filter_documents.side_effect = RuntimeError("synthetic lookup failure")
        with (
            patch.object(rag, "get_document_store", return_value=store),
            patch.object(rag, "_retrieve_docs") as vector,
        ):
            with self.assertRaisesRegex(RuntimeError, "synthetic lookup failure"):
                self.original_metadata_fetch(self.domain)
        vector.assert_not_called()

    def test_metadata_cache_expires_and_isolates_index_configuration(self):
        settings = SimpleNamespace(chroma_persist_dir="synthetic-index", chroma_collection_name="first")
        store = Mock(filter_documents=Mock(return_value=[]))
        with (
            patch.object(rag, "get_document_store", return_value=store),
            patch.object(rag, "get_settings", return_value=settings),
            patch.object(rag, "monotonic", return_value=0) as clock,
        ):
            self.original_metadata_fetch(self.domain, metadata_only=True)
            self.original_metadata_fetch(self.domain, metadata_only=True)
            self.assertEqual(store.filter_documents.call_count, 1)
            clock.return_value = rag._METADATA_CACHE_TTL_SECONDS
            self.original_metadata_fetch(self.domain, metadata_only=True)
            settings.chroma_collection_name = "second"
            self.original_metadata_fetch(self.domain, metadata_only=True)
            settings.chroma_persist_dir = "other-synthetic-index"
            self.original_metadata_fetch(self.domain, metadata_only=True)
        self.assertEqual(store.filter_documents.call_count, 4)

    def test_index_writes_and_clear_invalidate_metadata_even_after_partial_failure(self):
        store = Mock(filter_documents=Mock(return_value=[]), write_documents=Mock(return_value=1))
        doc = self.doc("Atelier Alpha")
        with (
            patch.object(rag, "get_document_store", return_value=store),
            patch.object(rag, "_get_document_embedder", return_value=Mock(run=Mock(return_value={"documents": [doc]}))),
            patch.object(rag, "_drop_chroma_collection"),
        ):
            self.original_metadata_fetch(self.domain, metadata_only=True)
            self.assertEqual(rag.index_documents_haystack([doc]), 1)
            self.original_metadata_fetch(self.domain, metadata_only=True)
            self.assertEqual(store.filter_documents.call_count, 2)
            store.write_documents.side_effect = RuntimeError("synthetic partial write")
            with self.assertRaisesRegex(RuntimeError, "synthetic partial write"):
                rag.index_documents_haystack([doc])
            self.original_metadata_fetch(self.domain, metadata_only=True)
            self.assertEqual(store.filter_documents.call_count, 3)
            rag.clear_all_documents()
            self.original_metadata_fetch(self.domain, metadata_only=True)
            self.assertEqual(store.filter_documents.call_count, 4)

    def test_dimension_mismatch_is_actionable_and_never_deletes_or_retries(self):
        doc = self.doc("Atelier Alpha")
        for error in (
            rag.chromadb.errors.InvalidDimensionException("Embedding dimension 384 does not match 1536"),
            rag.chromadb.errors.InvalidArgumentError("Collection expecting embedding dimension of 1536, got 384"),
        ):
            store = Mock(filter_documents=Mock(return_value=[]), write_documents=Mock(side_effect=error))
            with (
                self.subTest(error=type(error).__name__),
                patch.object(rag, "get_document_store", return_value=store) as get_store,
                patch.object(rag, "_get_document_embedder",
                             return_value=Mock(run=Mock(return_value={"documents": [doc]}))),
                patch.object(rag, "_drop_chroma_collection") as drop,
            ):
                with self.assertRaisesRegex(ValueError, "not deleted.*original embedding configuration") as raised:
                    rag.index_documents_haystack([doc])
                self.assertIs(raised.exception.__cause__, error)
            get_store.assert_called_once()
            store.write_documents.assert_called_once_with([doc])
            store.delete_all_documents.assert_not_called()
            drop.assert_not_called()

    def test_unrelated_write_errors_with_old_magic_words_preserve_original_failure(self):
        doc = self.doc("Atelier Alpha")
        for error in (
            RuntimeError("failure on row 384"),
            RuntimeError("dimension service unavailable"),
            rag.chromadb.errors.InvalidArgumentError("invalid metadata at row 1536"),
        ):
            store = Mock(write_documents=Mock(side_effect=error))
            with (
                self.subTest(error=str(error)),
                patch.object(rag, "get_document_store", return_value=store),
                patch.object(rag, "_get_document_embedder",
                             return_value=Mock(run=Mock(return_value={"documents": [doc]}))),
                patch.object(rag, "_drop_chroma_collection") as drop,
            ):
                with self.assertRaises(type(error)) as raised:
                    rag.index_documents_haystack([doc])
                self.assertIs(raised.exception, error)
            store.write_documents.assert_called_once_with([doc])
            drop.assert_not_called()

    def test_embedding_failure_invalidates_cache_without_writing(self):
        store = Mock(filter_documents=Mock(return_value=[]))
        with (
            patch.object(rag, "get_document_store", return_value=store),
            patch.object(rag, "_get_document_embedder",
                         return_value=Mock(run=Mock(side_effect=RuntimeError("synthetic embedding failure")))),
            patch.object(rag, "_drop_chroma_collection") as drop,
        ):
            self.original_metadata_fetch(self.domain, metadata_only=True)
            with self.assertRaisesRegex(RuntimeError, "synthetic embedding failure"):
                rag.index_documents_haystack([self.doc("Atelier Alpha")])
            self.assertEqual(rag._cached_domain_metadata.cache_info().currsize, 0)
        store.write_documents.assert_not_called()
        drop.assert_not_called()

    def test_explicit_clear_is_single_delete_and_tolerates_only_real_not_found(self):
        settings = SimpleNamespace(chroma_persist_dir="synthetic-unused-index", chroma_collection_name="synthetic")
        for error in (None, rag.chromadb.errors.NotFoundError("synthetic missing collection")):
            client = Mock(delete_collection=Mock(side_effect=error))
            store = Mock(filter_documents=Mock(return_value=[]))
            with (
                self.subTest(error=error),
                patch.object(rag, "get_settings", return_value=settings),
                patch.object(rag, "get_document_store", return_value=store),
                patch.object(rag.chromadb, "PersistentClient", return_value=client),
            ):
                self.original_metadata_fetch(self.domain, metadata_only=True)
                rag.clear_all_documents()
                self.assertEqual(rag._cached_domain_metadata.cache_info().currsize, 0)
            client.delete_collection.assert_called_once_with(name="synthetic")
            store.delete_all_documents.assert_not_called()

    def test_explicit_clear_propagates_backend_failures_and_invalidates_cache(self):
        settings = SimpleNamespace(chroma_persist_dir="synthetic-unused-index", chroma_collection_name="synthetic")
        for during_initialization in (True, False):
            error = RuntimeError("synthetic backend collection not found or inaccessible")
            client = Mock(delete_collection=Mock(side_effect=error))
            store = Mock(filter_documents=Mock(return_value=[]))
            with (
                self.subTest(during_initialization=during_initialization),
                patch.object(rag, "get_settings", return_value=settings),
                patch.object(rag, "get_document_store", return_value=store),
                patch.object(rag.chromadb, "PersistentClient", return_value=client,
                             side_effect=error if during_initialization else None),
            ):
                self.original_metadata_fetch(self.domain, metadata_only=True)
                with self.assertRaises(RuntimeError) as raised:
                    rag.clear_all_documents()
                self.assertIs(raised.exception, error)
                self.assertEqual(rag._cached_domain_metadata.cache_info().currsize, 0)
            self.assertEqual(client.delete_collection.call_count, 0 if during_initialization else 1)


if __name__ == "__main__":
    unittest.main()
