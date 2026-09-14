"""Offline reference integrity and scorer safeguards, not assertions that gaps must persist."""
import copy
from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import socket
import subprocess
import sys
import unittest
from unittest.mock import patch

from scripts import evaluate_qualification as evaluation


class QualificationReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = evaluation.load_corpus()
        cls.report = evaluation.evaluate(cls.corpus)

    def test_supported_paths_and_fixed_taxonomy(self):
        failures = [r for r in self.report["results"]
                    if r["requirement"] == "supported_baseline" and r["status"] != "pass"]
        self.assertEqual([r["id"] for r in failures], [],
                         str([(r["id"], [d["field"] for d in r["differences"]]) for r in failures]))
        self.assertEqual(self.report["taxonomy_snapshot"]["status"], "pass")
        coverage = self.report["domain_coverage"]
        self.assertEqual(len(coverage), 14)
        self.assertEqual(sum(d["sector_required"] for d in coverage.values()), 11)
        for domain, result in coverage.items():
            with self.subTest(domain=domain):
                self.assertEqual(result["modes"], ["label", "numeric"])
                self.assertEqual(result["total"], 2)
                self.assertEqual(result["passed"], 2)
        self.assertEqual(self.report["offline"]["unexpected_io_attempts"], 0)

    def test_bad_observer_is_not_a_success_shaped_fallback(self):
        report = evaluation.evaluate(self.corpus, observer=lambda case, corpus, rag: {})
        self.assertEqual(report["summary"]["passed"], 0)
        self.assertEqual(report["summary"]["failed"], report["summary"]["total"])
        self.assertEqual(report["exit_code"], 1)
        self.assertTrue(all(result["differences"] for result in report["results"]))
        self.assertTrue(all(result["actual"] == {} for result in report["results"]))

    def test_scorer_detects_missing_null_wrong_state_and_problem(self):
        expected = {"state": ["activites_terrain", "BTP", "1"], "problem": "Sans saisonnalité."}
        self.assertEqual(evaluation.score(expected, copy.deepcopy(expected)), [])
        self.assertEqual(len(evaluation.score(expected, {
            "state": ["finance_pilotage", None, None], "problem": "Avec saisonnalité.",
        })), 2)
        self.assertTrue(evaluation.score({"value": None}, {}))
        self.assertTrue(evaluation.score({"state": []}, None))

    def test_target_requirements_not_frozen_as_expected_failures(self):
        targets = [r for r in self.report["results"] if r["requirement"] == "target_requirement"]
        self.assertEqual({r["kind"] for r in targets},
                         {"detect_step", "objective_order", "intention_label"})
        for result in targets:
            self.assertEqual(result["status"], "fail" if result["differences"] else "pass")
            self.assertIn("no endpoint assertion", result["scope"])
        self.assertEqual(self.report["observed_gaps"],
                         [r["id"] for r in targets if r["differences"]])

    def test_unsupported_constraints_are_never_scored_as_passes(self):
        self.assertEqual(self.report["summary"]["total"], len(self.report["results"]))
        self.assertTrue(all(g["status"] == "not_evaluated" for g in self.report["not_evaluated"]))
        self.assertTrue(any(g["id"] == "reply-correlation" and g["next"] == "QUAL-02"
                            for g in self.report["not_evaluated"]))
        self.assertFalse(self.report["provenance"]["real_catalogue"])
        self.assertFalse(self.report["provenance"]["expert_validated"])
        self.assertFalse(self.report["provenance"]["user_validated"])

    def test_schema_rejects_malformed_or_incomplete_corpora(self):
        def altered(path, value):
            corpus = copy.deepcopy(self.corpus)
            cursor = corpus
            for part in path[:-1]:
                cursor = cursor[part]
            cursor[path[-1]] = value
            return corpus

        invalid = [
            altered(["schema_version"], 2),
            altered(["schema_version"], True),
            altered(["corpus_version"], "unknown"),
            altered(["source_commit"], "not-a-commit"),
            altered(["provenance", "synthetic"], False),
            altered(["provenance", "real_catalogue"], True),
            altered(["domains"], []),
            altered(["domains", 0, "number"], 2),
            altered(["domains", 1, "code"], "direction_strategie"),
            altered(["scenarios"], []),
            altered(["scenarios", 0, "kind"], "fabricated_score"),
            altered(["scenarios", 0, "id"], "flow-02"),
            altered(["scenarios", 0, "modes"], ["numeric"]),
            altered(["scenarios", 0, "domains"], ["unknown"]),
            altered(["scenarios", 0, "expected", "state"], ["unknown", None, "1"]),
            altered(["scenarios", 0, "expected", "state"], [None, None, "1"]),
            altered(["scenarios", 0, "expected", "state"], ["direction_strategie", "BTP", "1"]),
            altered(["scenarios", 1, "expected", "state"], ["organisation_coordination", None, "1"]),
            altered(["scenarios", 1, "expected", "state"], ["organisation_coordination", "Commerce & retail", "99"]),
            altered(["scenarios", 0, "expected", "phases"], []),
            altered(["scenarios", 14, "history"], [["system", "Texte"]]),
            altered(["scenarios", 14, "history"], [["assistant", "@unknown"]]),
            altered(["scenarios", 14, "history"], "unknown"),
            altered(["scenarios", 14, "expected", "ready"], "yes"),
            altered(["scenarios", 14, "expected", "ready"], True),
            altered(["not_evaluated"], []),
        ]
        extra = copy.deepcopy(self.corpus)
        extra["scenarios"][0]["expected"]["typo"] = True
        invalid.append(extra)
        incomplete = copy.deepcopy(self.corpus)
        incomplete["scenarios"].pop(0)
        invalid.append(incomplete)
        for number, corpus in enumerate(invalid):
            with self.subTest(number=number), self.assertRaises(evaluation.FixtureError):
                evaluation.validate_corpus(corpus)

    def test_strict_json_rejects_duplicates_nan_and_bad_syntax(self):
        for raw in ('{"schema_version":1,"schema_version":1}', '{"x":NaN}', '{"x":Infinity}', '{'):
            with self.subTest(raw=raw), patch.object(Path, "read_text", return_value=raw):
                with self.assertRaises(evaluation.FixtureError):
                    evaluation.load_corpus()

    def test_network_and_real_data_boundaries_fail_even_when_swallowed(self):
        for attempt in (
            lambda rag: socket.create_connection(("127.0.0.1", 1)),
            lambda rag: socket.getaddrinfo("example.invalid", 443),
            lambda rag: rag.get_document_store(),
            lambda rag: rag._get_generator(),
            lambda rag: rag._retrieve_docs("Besoin fictif"),
            lambda rag: rag._retrieve_docs_for_question("Besoin fictif"),
        ):
            with self.subTest(attempt=attempt), self.assertRaises(evaluation.OfflineViolation):
                with evaluation.offline_runtime(self.corpus) as rag:
                    try:
                        attempt(rag)
                    except evaluation.OfflineViolation:
                        pass

    def test_report_writer_requires_exclusive_creation(self):
        path = Path(__file__)
        before = path.read_bytes()
        with self.assertRaises(FileExistsError):
            evaluation.write_report(path, self.report)
        self.assertEqual(path.read_bytes(), before)
        stream = io.StringIO()
        with patch.object(Path, "open") as opened:
            opened.return_value.__enter__.return_value = stream
            evaluation.write_report(Path("new-report.json"), self.report)
            opened.assert_called_once_with("x", encoding="utf-8")
        self.assertEqual(json.loads(stream.getvalue()), self.report)

    def test_cli_invalid_fixture_or_existing_report_exits_two(self):
        for args in (["--output", str(Path(__file__))],
                     ["--fixture", str(Path(__file__))]):
            stdout, stderr = io.StringIO(), io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = evaluation.main(args)
            self.assertEqual(code, 2)
            self.assertIn("QUAL-01 evaluation error", stderr.getvalue())
            self.assertNotIn("passed:", stdout.getvalue())

    def test_standalone_command_output_and_exit_follow_observations(self):
        command = [sys.executable, "-B", str(evaluation.BACKEND / "scripts" / "evaluate_qualification.py")]
        result = subprocess.run(command, cwd=evaluation.BACKEND, capture_output=True, text=True,
                                encoding="utf-8", errors="replace", timeout=120)
        self.assertEqual(result.returncode, self.report["exit_code"], result.stderr)
        for marker in ("Scenarios:", "Requirements:", "Modes:", "Domains: 14/14",
                       "Categories:", "Observed target gaps:", "Not evaluated (",
                       "Source fingerprints:"):
            self.assertIn(marker, result.stdout)
        self.assertNotIn("100%", result.stdout)

    def test_fingerprints_are_local_content_hashes(self):
        result = evaluation.source_fingerprints(evaluation.DEFAULT_FIXTURE)
        if result["git_status"] == "available":
            self.assertRegex(result["observed_head"], r"^[0-9a-f]{40}$")
        else:
            self.assertIn(result["git_status"], ("git_unavailable", "no_git_checkout"))
            self.assertIsNone(result["observed_head"])
        self.assertEqual(set(result["sha256"]), {"fixture", "evaluator", "haystack_rag", "rag_constants"})
        for digest in result["sha256"].values():
            self.assertRegex(digest, r"^[0-9a-f]{64}$")

    def test_exported_context_records_missing_git_without_inventing_a_revision(self):
        with patch.object(evaluation.shutil, "which", return_value=None):
            result = evaluation.source_fingerprints(evaluation.DEFAULT_FIXTURE)
        self.assertIsNone(result["observed_head"])
        self.assertEqual(result["git_status"], "git_unavailable")
        self.assertEqual(len(result["sha256"]), 4)
        absent = subprocess.CompletedProcess([], 128, "", "fatal: not a git repository")
        with (
            patch.object(evaluation.shutil, "which", return_value="git"),
            patch.object(evaluation.subprocess, "run", return_value=absent),
        ):
            result = evaluation.source_fingerprints(evaluation.DEFAULT_FIXTURE)
        self.assertIsNone(result["observed_head"])
        self.assertEqual(result["git_status"], "no_git_checkout")

    def test_git_errors_are_not_misreported_as_missing_export_metadata(self):
        error = subprocess.CompletedProcess([], 128, "", "fatal: detected dubious ownership")
        with (
            patch.object(evaluation.shutil, "which", return_value="git"),
            patch.object(evaluation.subprocess, "run", return_value=error),
        ):
            with self.assertRaises(evaluation.FixtureError):
                evaluation.source_fingerprints(evaluation.DEFAULT_FIXTURE)


if __name__ == "__main__":
    unittest.main()
