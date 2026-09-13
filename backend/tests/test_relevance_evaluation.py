"""Offline checks for the live evaluation harness; no network or real-data reads."""
import argparse
import copy
import json
import unittest
from unittest.mock import Mock, patch

from scripts import evaluate_chat_relevance as evaluation


SAVED_ZERO_MATCH_RESPONSE = """Bonjour, je vais vous aider à identifier des cas d'usage concrets de l'IA adaptés à votre organisation. Pour commencer, je vais vous poser quelques questions simples afin de cibler précisément votre priorité.

D'après vos choix (Domaine : Chantiers & activités terrain — Secteur : BTP — Intention : Partager les informations terrain) et votre problème déclaré ("Je dois calculer la TVA et établir la déclaration fiscale annuelle de mon entreprise"), aucun des cas disponibles pour cette combinaison domaine/intention ne répond directement à une tâche de calcul de TVA ou de déclaration fiscale.

1) Voulez-vous plutôt explorer le domaine "Finances & rentabilité" pour traiter la TVA et la déclaration fiscale ? (répondez "oui" ou "non")

2) Si non, souhaitez-vous que j'essaie d'identifier des liens possibles entre vos informations terrain et la préparation fiscale (par ex. consolidation de feuilles de présence, extraction de factures terrain) ? (répondez "oui" ou "non")"""


class RelevanceEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.documents = evaluation.synthetic_documents()

    def test_six_specific_one_zero_one_unscored_and_sixteen_call_bound(self):
        scenarios = evaluation.scenarios()
        self.assertEqual(len(scenarios) * 2, evaluation.MAX_CALLS)
        self.assertEqual(sum(bool(row["expected_ids"]) for row in scenarios), 6)
        self.assertEqual(sum(row["expected_ids"] == [] for row in scenarios), 1)
        self.assertEqual(sum(row["expected_ids"] is None for row in scenarios), 1)

    def test_current_prompt_preserves_candidates_query_and_reversed_order(self):
        for docs in (self.documents, list(reversed(self.documents))):
            prompt = evaluation.build_prompt("Besoin synthétique précis pour mon chantier.", docs)
            self.assertIn("Un secteur commun ne suffit pas", prompt)
            self.assertIn("Partager les informations terrain", prompt)
            candidates = json.loads(prompt.rsplit("\n\n", 1)[1])["candidats"]
            self.assertEqual(
                [(c["numero"], c["titre"], c["description"]) for c in candidates],
                [(i, doc.meta["cas_utilisation"], doc.content) for i, doc in enumerate(docs, 1)],
            )

    def test_synonym_query_has_zero_production_keyword_overlap(self):
        scenario = next(row for row in evaluation.scenarios() if row["id"] == "synonyms-zero-keyword-overlap")
        keywords = set(evaluation.rag._query_keywords(scenario["query"]))
        for doc in self.documents:
            self.assertFalse(keywords & set(evaluation.rag._doc_search_blob(doc).split()))

    def test_recognized_relevant_and_peripheral_selection(self):
        raw = f"1. **{self.documents[0].meta['cas_utilisation']}**\nRéponse synthétique."
        outcome = evaluation.assess_response(raw, self.documents, ["synthetic-summary"])
        self.assertTrue(outcome["hypothesis_pass"])
        outcome = evaluation.assess_response(raw, self.documents, ["synthetic-safety"])
        self.assertTrue(outcome["relevance_failure"])
        self.assertFalse(outcome["parse_failure"])
        self.assertEqual(outcome["unexpected_peripheral_ids"], ["synthetic-summary"])

    def test_unknown_numbered_list_cannot_pass_zero_match(self):
        outcome = evaluation.assess_response("1. **Cas inventé**\nTexte.", self.documents, [])
        self.assertEqual(outcome["retained_ids"], [])
        self.assertEqual(outcome["response_kind"], "all_unrecognized_parse_failure")
        self.assertTrue(outcome["parse_failure"])
        self.assertFalse(outcome["correct_zero_match"])

    def test_zero_match_statement_and_anchored_numbered_question_are_separate_signals(self):
        raw = "Aucun des cas ne répond à votre besoin.\n1) Voulez-vous explorer un autre domaine ?"
        result = evaluation.assess_response(raw, self.documents, [])
        self.assertTrue(result["raw_explicit_zero_match_statement"])
        self.assertTrue(result["numbered_output_detected"])
        self.assertEqual(result["response_kind"], "semantic_exclusion")
        self.assertTrue(result["numbered_clarifications_only"])
        self.assertTrue(result["correct_zero_match"])
        self.assertFalse(result["parse_failure"])

    def test_saved_live_zero_match_numbered_clarifications_are_not_candidate_headings(self):
        result = evaluation.assess_response(SAVED_ZERO_MATCH_RESPONSE, self.documents, [])
        self.assertEqual(result["retained_ids"], [])
        self.assertTrue(result["hypothesis_pass"])
        self.assertTrue(result["numbered_clarifications_only"])
        self.assertFalse(result["parse_failure"])
        self.assertFalse(result["diagnostic_inconclusive"])
        self.assertEqual(result["diagnostic_version"], evaluation.DIAGNOSTIC_VERSION)

    def test_no_match_prefix_never_excuses_fabricated_case_lists(self):
        prefix = "Aucun cas directement pertinent.\n\n"
        question = "1) Voulez-vous explorer un autre domaine ?"
        endings = [
            "1. **Cas inventé**\nDescription inventée.",
            "1) Cas inventé ?",
            "1. Cas inventé\nPourquoi c’est pertinent pour vous :\nExemple.",
            question + "\n\n2. Cas inventé\nDescription.",
            question + "\nDescription d'un cas inventé.",
            question + "\n\nCas inventé\nCe que cela permet concrètement : résultat.",
            "- **Cas inventé**\nDescription.",
            "### Cas inventé\nDescription.",
            "**Cas inventé**\nDescription.",
            "1) Souhaitez-vous utiliser le cas inventé ?",
        ]
        for ending in endings:
            with self.subTest(ending=ending):
                result = evaluation.assess_response(prefix + ending, self.documents, [])
                self.assertFalse(result["correct_zero_match"])
                self.assertFalse(result["hypothesis_pass"])
                self.assertTrue(result["parse_failure"])
                self.assertTrue(result["diagnostic_inconclusive"])

    def test_numbered_question_recognition_is_bounded_anchored_and_conservative(self):
        prefix = "Aucun cas directement pertinent.\n\n"
        cases = [
            "1) Faut-il revoir cela ?",
            "1) Voulez-vous explorer un autre domaine",
            "2) Voulez-vous explorer un autre domaine ?",
            "1) Voulez-vous explorer un autre domaine ?\n2) Pouvez-vous préciser votre besoin ?\n"
            "3) Pouvez-vous décrire votre problème ?",
            "1) Voulez-vous explorer le domaine " + "x" * 351 + " ?",
            "1) Voulez-vous explorer un autre domaine ?\nUn autre texte ambigu.",
            "1) Voulez-vous explorer un autre domaine ? Encore une question ?",
            "1) **Voulez-vous explorer un autre domaine ?**",
        ]
        for raw in cases:
            with self.subTest(raw=raw):
                result = evaluation.assess_response(prefix + raw, self.documents, [])
                self.assertFalse(result["numbered_clarifications_only"])
                self.assertFalse(result["hypothesis_pass"])
                self.assertTrue(result["diagnostic_inconclusive"])
        no_prefix = "1) Voulez-vous explorer un autre domaine ?"
        self.assertFalse(evaluation.assess_response(no_prefix, self.documents, [])["hypothesis_pass"])

    def test_reassessment_preserves_original_evidence_and_synonym_hypothesis(self):
        synonym_raw = (
            f"1. {self.documents[0].meta['cas_utilisation']}\nSynthèse.\n\n"
            f"4. {self.documents[3].meta['cas_utilisation']}\nActions."
        )
        source = {
            "expectation_status": evaluation.HYPOTHESIS,
            "synthetic_candidates": [
                evaluation.rag._doc_to_case_dict(doc, index)
                for index, doc in enumerate(self.documents)
            ],
            "summary": {"hypothesis_passes": 0, "parse_failures": 1},
            "results": [],
        }
        for name, raw, expected in (
            ("zero-match", SAVED_ZERO_MATCH_RESPONSE, []),
            ("synonyms-zero-keyword-overlap", synonym_raw, ["synthetic-summary"]),
        ):
            source["results"].append({
                "scenario_id": name, "repeat": 1, "raw_response": raw, "expected_ids": expected,
                "candidate_order": [doc.id for doc in self.documents], "finish_reason": "stop",
                "hypothesis_pass": False, "parse_failure": name == "zero-match",
            })
        before = copy.deepcopy(source)
        with (
            patch.object(evaluation, "discover_config", side_effect=AssertionError("No Azure")),
            patch.object(evaluation, "call_model", side_effect=AssertionError("No model")),
        ):
            reassessed = evaluation.reassess_report(source)
        self.assertEqual(source, before)
        self.assertEqual(reassessed["original_report"], before)
        self.assertEqual(reassessed["new_model_calls"], 0)
        self.assertTrue(reassessed["results"][0]["hypothesis_pass"])
        self.assertFalse(reassessed["results"][1]["hypothesis_pass"])
        self.assertEqual(reassessed["results"][1]["unexpected_peripheral_ids"], ["synthetic-actions"])
        for old, new in zip(before["results"], reassessed["results"]):
            self.assertEqual(old["raw_response"], new["raw_response"])
            self.assertEqual(old["expected_ids"], new["expected_ids"])
        self.assertEqual(reassessed["summary"]["diagnostic_inconclusive_calls"], 0)

    def test_semantic_exclusion_is_distinct_from_empty_or_unstructured(self):
        good = evaluation.assess_response("Aucun cas directement pertinent.", self.documents, [])
        self.assertTrue(good["correct_zero_match"])
        self.assertFalse(good["parse_failure"])
        for raw in ("", "Je peux vous aider.", "Pouvez-vous préciser votre demande ?"):
            result = evaluation.assess_response(raw, self.documents, [])
            self.assertFalse(result["correct_zero_match"])
            self.assertFalse(result["hypothesis_pass"])

    def test_ambiguous_has_no_forced_relevance_label(self):
        result = evaluation.assess_response("Pouvez-vous préciser ?", self.documents, None)
        self.assertIsNone(result["hypothesis_pass"])
        self.assertIsNone(result["relevance_failure"])
        self.assertFalse(result["parse_failure"])

    def test_truncation_cannot_pass(self):
        raw = f"1. {self.documents[0].meta['cas_utilisation']}\n"
        result = evaluation.assess_response(raw, self.documents, ["synthetic-summary"], "length")
        self.assertTrue(result["generation_failure"])
        self.assertFalse(result["hypothesis_pass"])
        self.assertIsNone(result["relevance_failure"])
        self.assertFalse(result["parse_failure"])

    def test_dry_run_never_discovers_azure_or_calls_model(self):
        args = argparse.Namespace(live=False, auth="azure-cli-token", output=None)
        with (
            patch.object(evaluation, "discover_config", side_effect=AssertionError("No Azure")),
            patch.object(evaluation, "live_client", side_effect=AssertionError("No model")),
        ):
            report, code = evaluation.run(args)
        self.assertEqual(code, 0)
        self.assertEqual(report["attempted_calls"], 0)
        self.assertEqual(len(report["results"]), 16)
        self.assertEqual(report["summary"]["scored_calls"], 0)
        first, second = report["results"][:2]
        self.assertEqual(first["candidate_order"], list(reversed(second["candidate_order"])))

    def test_transport_error_stops_without_retry_or_false_success(self):
        args = argparse.Namespace(live=True, auth="azure-cli-token", output=None)
        with (
            patch.object(evaluation, "discover_config", return_value={}),
            patch.object(evaluation, "live_client", return_value=Mock()),
            patch.object(evaluation, "call_model", side_effect=RuntimeError("SECRET")) as call,
        ):
            report, code = evaluation.run(args)
        self.assertEqual(code, 2)
        self.assertEqual(report["attempted_calls"], 1)
        self.assertEqual(call.call_count, 1)
        self.assertNotIn("SECRET", str(report))
        self.assertEqual(report["status"], "transport_or_config_error")

    def test_resume_skips_failed_attempt_and_obeys_total_budget(self):
        args = argparse.Namespace(live=True, auth="azure-cli-token", output=None, interval_seconds=0)
        generated = {"raw_response": "Aucun cas pertinent.", "finish_reason": "stop"}
        with (
            patch.object(evaluation, "discover_config", return_value={}),
            patch.object(evaluation, "live_client", return_value=Mock()),
            patch.object(evaluation, "call_model",
                         side_effect=[generated, generated, RuntimeError("rate limit")]),
        ):
            report, code = evaluation.run(args)
        self.assertEqual(code, 2)
        self.assertEqual(report["attempted_calls"], 3)
        args.resume = True
        args.output = Mock()
        args.output.read_text.return_value = json.dumps(report)
        with (
            patch.object(evaluation, "discover_config", return_value={}),
            patch.object(evaluation, "live_client", return_value=Mock()),
            patch.object(evaluation, "call_model", return_value=generated) as call,
            patch("builtins.print"),
        ):
            resumed, code = evaluation.run(args)
        self.assertEqual(code, 2)
        self.assertEqual(call.call_count, 13)
        self.assertEqual(resumed["attempted_calls"], 16)
        self.assertEqual(resumed["summary"]["transport_failures"], 1)
        self.assertEqual(resumed["status"], "completed_with_transport_errors")

    def test_cli_scenario_repeats_tokens_and_invalid_bounds(self):
        args = evaluation.parse_args([
            "--scenario", "zero-match", "--scenario", "synonyms-zero-keyword-overlap",
            "--repeats", "2", "--max-completion-tokens", "6000",
        ])
        self.assertEqual(args.scenario, ["zero-match", "synonyms-zero-keyword-overlap"])
        self.assertEqual(args.max_completion_tokens, 6000)
        self.assertFalse(args.live)
        defaults = evaluation.parse_args([])
        self.assertEqual((defaults.repeats, defaults.max_completion_tokens), (2, 1200))
        for flags in (["--repeats", "3"], ["--max-completion-tokens", "6001"],
                      ["--max-completion-tokens", "0"], ["--scenario", "unknown"]):
            with self.subTest(flags=flags), patch("sys.stderr"), self.assertRaises(SystemExit) as raised:
                evaluation.parse_args(flags)
            self.assertEqual(raised.exception.code, 2)

    def test_live_cli_requires_explicit_resource_scope(self):
        with patch("sys.stderr"), self.assertRaises(SystemExit) as raised:
            evaluation.parse_args(["--live", "--output", "nonexistent-evaluation.json"])
        self.assertEqual(raised.exception.code, 2)

    def test_subset_limits_actual_calls_and_forwards_completion_bound(self):
        args = evaluation.parse_args([
            "--scenario", "zero-match", "--scenario", "synonyms-zero-keyword-overlap",
            "--max-completion-tokens", "6000", "--interval-seconds", "0",
        ])
        args.live = True
        generated = {"raw_response": "Aucun cas pertinent.", "finish_reason": "stop"}
        with (
            patch.object(evaluation, "discover_config", return_value={}),
            patch.object(evaluation, "live_client", return_value=Mock()),
            patch.object(evaluation, "call_model", return_value=generated) as call,
            patch("builtins.print"),
        ):
            report, code = evaluation.run(args)
        self.assertEqual(code, 1)
        self.assertEqual(report["max_calls"], 4)
        self.assertEqual(report["attempted_calls"], 4)
        self.assertEqual(call.call_count, 4)
        self.assertTrue(all(item.args[-1] == 6000 for item in call.call_args_list))
        self.assertEqual(report["repeats"], 2)
        self.assertEqual(report["max_completion_tokens"], 6000)

    def test_transport_preserves_parameters_without_reasoning_override(self):
        client = Mock()
        stream = Mock()
        stream.__enter__ = Mock(return_value=iter([]))
        stream.__exit__ = Mock(return_value=False)
        client.chat.completions.create.return_value = stream
        evaluation.call_model(client, {"deployment": "existing-model"}, "synthetic prompt", 6000)
        kwargs = client.chat.completions.create.call_args.kwargs
        self.assertEqual(kwargs["max_completion_tokens"], 6000)
        self.assertEqual(kwargs["temperature"], 1)
        self.assertEqual(kwargs["model"], "existing-model")
        self.assertEqual(kwargs["messages"], [{"role": "user", "content": "synthetic prompt"}])
        self.assertNotIn("reasoning_effort", kwargs)

    def test_unscored_generation_failure_has_nonzero_inconclusive_exit(self):
        args = evaluation.parse_args(["--scenario", "ambiguous-observation", "--repeats", "1"])
        args.live = True
        with (
            patch.object(evaluation, "discover_config", return_value={}),
            patch.object(evaluation, "live_client", return_value=Mock()),
            patch.object(evaluation, "call_model",
                         return_value={"raw_response": "", "finish_reason": "length"}),
            patch("builtins.print"),
        ):
            report, code = evaluation.run(args)
        self.assertEqual(code, 3)
        self.assertEqual(report["status"], "inconclusive_generation_failure")
        self.assertEqual(report["summary"]["hypothesis_failures"], 0)
        self.assertEqual(report["summary"]["generation_failures"], 1)

    def test_summarize_accounts_for_reasoning_inside_total_not_extra_budget(self):
        row = evaluation.assess_response("Aucun cas pertinent.", self.documents, [])
        row.update(scenario_id="zero-match", usage={
            "prompt_tokens": 4000, "completion_tokens": 1500, "total_tokens": 5500,
            "completion_tokens_details": {"reasoning_tokens": 1300},
        })
        summary = evaluation.summarize([row])
        self.assertEqual(summary["usage_totals"]["completion_tokens"], 1500)
        self.assertEqual(summary["reasoning_tokens"], 1300)
        self.assertEqual(summary["non_reasoning_completion_tokens"], 200)
        self.assertEqual(summary["calls_with_reasoning_usage"], 1)

    def test_resume_rejects_changed_identity_or_accounting_before_azure(self):
        args = evaluation.parse_args(["--scenario", "zero-match", "--repeats", "1"])
        args.live = True
        with (
            patch.object(evaluation, "discover_config", return_value={"deployment": "original"}),
            patch.object(evaluation, "live_client", return_value=Mock()),
            patch.object(evaluation, "call_model",
                         return_value={"raw_response": "Aucun cas pertinent.", "finish_reason": "stop"}),
            patch("builtins.print"),
        ):
            original, _ = evaluation.run(args)
        mutations = {
            "tokens": lambda r: r.update(max_completion_tokens=6000),
            "schema": lambda r: r.update(schema_version=1),
            "scope": lambda r: r["azure_scope"].update(subscription="changed"),
            "fixture": lambda r: r["synthetic_candidates"][0].update(content="changed"),
            "prompt": lambda r: r["evaluation_plan"][0].update(prompt_sha256="changed"),
            "expected": lambda r: r["evaluation_plan"][0].update(expected_ids=["synthetic-safety"]),
            "reconciler": lambda r: r.update(reconciler_sha256="changed"),
            "count": lambda r: r.update(attempted_calls=0),
            "duplicates": lambda r: r["results"].append(r["results"][0]),
        }
        args.resume = True
        args.output = Mock()
        for name, mutate in mutations.items():
            altered = copy.deepcopy(original)
            mutate(altered)
            args.output.read_text.return_value = json.dumps(altered)
            with (
                self.subTest(name=name),
                patch.object(evaluation, "discover_config", side_effect=AssertionError("No Azure")),
                self.assertRaises(evaluation.EvaluationError),
            ):
                evaluation.run(args)
        args.output.write_text.assert_not_called()
        args.output.read_text.return_value = json.dumps(original)
        with (
            patch.object(evaluation, "discover_config", return_value={"deployment": "changed"}),
            patch.object(evaluation, "live_client", side_effect=AssertionError("No credential/model")),
        ):
            report, code = evaluation.run(args)
        self.assertEqual(code, 2)
        self.assertIn("configuration changed", report["error"]["message"])


if __name__ == "__main__":
    unittest.main()
