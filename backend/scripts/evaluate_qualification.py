"""Offline QUAL-01 mechanical reference; never a real-catalogue accuracy score."""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import ExitStack, contextmanager
import hashlib
import json
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
from unittest.mock import patch


BACKEND = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE = BACKEND / "tests" / "fixtures" / "qualification_reference.json"
sys.path.insert(0, str(BACKEND))
VERSION = "1.0.0"
CATEGORIES = {
    "domain_coverage", "explicit_domain", "sector_context", "question_scoping",
    "ambiguity", "problem_preservation", "correction_invalidation",
    "problem_invalidation", "client_merge", "no_match",
    "wording_independence", "stable_choice_identity", "explicit_label_identity",
}
KINDS = {"full_flow", "replay", "no_match", "detect_step", "objective_order", "intention_label"}
STEPS = {"domain", "sector", "intention", "problem", "topic"}
COMMON = {"id", "kind", "category", "requirement", "domains", "expected"}
REPLAY_FIELDS = {"history", "client", "query"}
KIND_FIELDS = {
    "full_flow": {"modes"},
    "replay": REPLAY_FIELDS,
    "no_match": REPLAY_FIELDS | {"modes"},
    "detect_step": {"question"},
    "objective_order": REPLAY_FIELDS | {"current_intentions"},
    "intention_label": REPLAY_FIELDS | {"current_intentions"},
}
SCOPES = {
    "full_flow": "selection/problem/qualification-response helpers; scripted conversation",
    "replay": "selection and problem-history helpers; no endpoint assertion",
    "no_match": "Python prompt/query orchestrators; empty retrieval stub, not HTTP/SSE",
    "detect_step": "_detect_expected_step_from_assistant only; no endpoint assertion",
    "objective_order": "history replay and intention-label helper; no endpoint assertion",
    "intention_label": "explicit-label selection helper, synthetic command-prefix collision; no endpoint assertion",
}


class FixtureError(ValueError):
    pass


class OfflineViolation(AssertionError):
    pass


def require(condition, message):
    if not condition:
        raise FixtureError(message)


def fields(value, required, optional=()):
    require(isinstance(value, dict), "Expected an object")
    require(required <= value.keys() and value.keys() <= required | set(optional),
            f"Invalid fields: expected {sorted(required)}, got {sorted(value)}")


def text(value, name, *, empty=False):
    require(isinstance(value, str) and (empty or bool(value.strip())), f"Invalid {name}")


def strings(value, name, *, empty=False):
    require(isinstance(value, list) and (empty or bool(value)), f"Invalid {name}")
    for item in value:
        text(item, name)
    require(len(value) == len(set(value)), f"Duplicate {name}")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def reject_constant(value):
    raise FixtureError(f"Non-finite JSON value: {value}")


def validate_state(state, domains, intentions):
    require(isinstance(state, list) and len(state) == 3, "State must have three fields")
    for value in state:
        require(value is None or isinstance(value, str), "State fields must be strings or null")
    domain, sector, intention = state
    if domain is None:
        require(sector is None and intention is None, "Dependent selection without domain")
        return
    require(domain in domains, f"Unknown state domain: {domain}")
    sectors = domains[domain]["sectors"]
    require(sector is None or (bool(sectors) and sector in sectors + ["Autre / Non spécifique"]),
            f"Invalid sector for {domain}: {sector}")
    require(intention is None or intention in [str(i) for i in range(1, len(intentions) + 1)],
            f"Invalid intention code: {intention}")
    require(not intention or not sectors or sector is not None, "Intention without required sector")


def validate_history(history, corpus, *, allow_reference=True):
    if allow_reference and isinstance(history, str):
        require(history in corpus["histories"], f"Unknown history: {history}")
        return
    require(isinstance(history, list), "History must be an array or a named history")
    for turn in history:
        require(isinstance(turn, list) and len(turn) == 2, "Invalid history turn")
        require(turn[0] in ("assistant", "user"), "Invalid history role")
        text(turn[1], "history content")
        if turn[1].startswith("@"):
            require(turn[0] == "assistant" and turn[1][1:] in corpus["questions"],
                    "Unknown question reference")


def validate_corpus(corpus):
    fields(corpus, {
        "schema_version", "corpus_version", "reference_contract", "source_commit",
        "application_commit", "provenance", "domains", "synthetic_intentions",
        "problem_example", "questions", "histories", "scenarios", "not_evaluated",
    })
    require(type(corpus["schema_version"]) is int and corpus["schema_version"] == 1,
            "Unsupported schema_version")
    require(corpus["corpus_version"] == VERSION, "Unsupported corpus_version")
    text(corpus["reference_contract"], "reference contract")
    for name in ("source_commit", "application_commit"):
        text(corpus[name], name)
        require(re.fullmatch(r"[0-9a-f]{40}", corpus[name]) is not None, f"Invalid {name}")
    provenance = corpus["provenance"]
    fields(provenance, {"taxonomy_source", "synthetic", "real_catalogue",
                        "expert_validated", "user_validated", "expectations", "fixture_revision"})
    require(provenance["taxonomy_source"] == "app/rag_constants.py", "Invalid taxonomy source")
    for key, expected in (("synthetic", True), ("real_catalogue", False),
                          ("expert_validated", False), ("user_validated", False)):
        require(provenance[key] is expected, f"Invalid provenance flag: {key}")
    text(provenance["expectations"], "expectations provenance")
    text(provenance["fixture_revision"], "fixture revision")
    strings(corpus["synthetic_intentions"], "synthetic intentions")
    require(len(corpus["synthetic_intentions"]) == 2 and
            all("fictif" in s for s in corpus["synthetic_intentions"]),
            "Version 1 requires two explicitly fictitious intentions")
    text(corpus["problem_example"], "problem example")
    fields(corpus["questions"], {"domain", "sector", "intention", "problem", "no_match"})
    for value in corpus["questions"].values():
        text(value, "question")
    rows = corpus["domains"]
    require(isinstance(rows, list) and len(rows) == 14, "Exactly 14 domain snapshots required")
    domains = {}
    labels = set()
    for number, row in enumerate(rows, 1):
        fields(row, {"number", "code", "label", "sectors"})
        require(type(row["number"]) is int and row["number"] == number, "Invalid domain number/order")
        text(row["code"], "domain code")
        text(row["label"], "domain label")
        strings(row["sectors"], "sectors", empty=True)
        require(row["code"] not in domains and row["label"] not in labels, "Duplicate domain")
        domains[row["code"]] = row
        labels.add(row["label"])
    require(isinstance(corpus["histories"], dict) and bool(corpus["histories"]), "Empty histories")
    for name, history in corpus["histories"].items():
        text(name, "history name")
        validate_history(history, corpus, allow_reference=False)
    scenarios = corpus["scenarios"]
    require(isinstance(scenarios, list) and bool(scenarios), "Empty scenario coverage")
    ids, covered, categories, targets = set(), set(), set(), set()
    for case in scenarios:
        require(isinstance(case, dict), "Invalid scenario")
        kind = case.get("kind")
        require(isinstance(kind, str) and kind in KINDS, f"Unknown scenario kind: {kind}")
        fields(case, COMMON | KIND_FIELDS[kind])
        text(case["id"], "scenario ID")
        require(re.fullmatch(r"[a-z0-9-]+", case["id"]) is not None, "Invalid scenario ID")
        require(case["id"] not in ids, f"Duplicate scenario ID: {case['id']}")
        ids.add(case["id"])
        require(isinstance(case["category"], str) and case["category"] in CATEGORIES,
                "Unknown category")
        categories.add(case["category"])
        target = kind in {"detect_step", "objective_order", "intention_label"}
        require(case["requirement"] == ("target_requirement" if target else "supported_baseline"),
                "Invalid requirement classification")
        if target:
            targets.add(kind)
        strings(case["domains"], "scenario domains", empty=kind == "replay")
        require(set(case["domains"]) <= domains.keys(), "Unknown scenario domain")
        expected = case["expected"]
        if kind in {"replay", "objective_order", "intention_label", "no_match"}:
            validate_history(case["history"], corpus)
            validate_state(case["client"], domains, corpus["synthetic_intentions"])
            text(case["query"], "query")
        if kind == "full_flow":
            fields(expected, {"state", "phases"})
            require(case["modes"] == ["numeric", "label"], "Both entry modes required")
            require(len(case["domains"]) == 1, "One domain per full flow")
            domain = case["domains"][0]
            require(domain not in covered, "Duplicate full-flow domain")
            covered.add(domain)
            validate_state(expected["state"], domains, corpus["synthetic_intentions"])
            sectors = domains[domain]["sectors"]
            require(expected["state"] == [domain, sectors[0] if sectors else None, "1"],
                    "Full flow must choose first synthetic options")
            phases = (["sector"] if sectors else []) + ["intention", "problem", "search"]
            require(expected["phases"] == phases, "Invalid expected phase sequence")
        elif kind == "replay":
            fields(expected, {"state"}, {"problem", "ready", "intention_label"})
            validate_state(expected["state"], domains, corpus["synthetic_intentions"])
            if "problem" in expected:
                text(expected["problem"], "expected problem", empty=True)
            if "ready" in expected:
                require(type(expected["ready"]) is bool, "Invalid expected readiness")
                if expected["ready"]:
                    state = expected["state"]
                    require(bool(state[0] and state[2]) and bool(expected.get("problem")),
                            "Ready expectation requires qualification and problem")
            if "intention_label" in expected:
                require(expected["intention_label"] in corpus["synthetic_intentions"],
                        "Unknown expected intention label")
        elif kind == "detect_step":
            fields(expected, {"step"})
            text(case["question"], "question")
            require(isinstance(expected["step"], str) and expected["step"] in STEPS,
                    "Unknown expected step")
        elif kind in {"objective_order", "intention_label"}:
            fields(expected, {"intention_label"})
            strings(case["current_intentions"], "reordered intentions")
            require(len(case["current_intentions"]) == 2 and
                    all("fictif" in s for s in case["current_intentions"]),
                    "Two explicitly fictitious intentions required")
            if kind == "objective_order":
                require(set(case["current_intentions"]) == set(corpus["synthetic_intentions"]),
                        "Reordering must preserve the same synthetic intentions")
            require(expected["intention_label"] in case["current_intentions"],
                    "Unknown expected intention label")
        else:
            fields(expected, {"state", "answer", "sources", "suggested_case_ids", "retrieval_requests"})
            require(case["modes"] == ["prompt", "query"], "Both Python orchestrators required")
            validate_state(expected["state"], domains, corpus["synthetic_intentions"])
            text(expected["answer"], "no-match answer")
            require(expected["sources"] == [] and expected["suggested_case_ids"] == [],
                    "No-match expectations cannot contain catalogue results")
            requests = expected["retrieval_requests"]
            require(isinstance(requests, list) and bool(requests), "Empty retrieval expectations")
            for request in requests:
                fields(request, {"query", "state"})
                text(request["query"], "retrieval query")
                validate_state(request["state"], domains, corpus["synthetic_intentions"])
    require(covered == domains.keys(), "Incomplete domain coverage")
    require(categories == CATEGORIES, "Incomplete category coverage")
    require(targets == {"detect_step", "objective_order", "intention_label"},
            "Missing target requirement probes")
    require(isinstance(corpus["not_evaluated"], list) and bool(corpus["not_evaluated"]),
            "Missing explicit limitations")
    for gap in corpus["not_evaluated"]:
        fields(gap, {"id", "next", "reason"})
        for value in gap.values():
            text(value, "limitation")
        require(gap["id"] not in ids, "Duplicate limitation/scenario ID")
        ids.add(gap["id"])
    return corpus


def load_corpus(path=DEFAULT_FIXTURE):
    try:
        corpus = json.loads(Path(path).read_text(encoding="utf-8"),
                            object_pairs_hook=unique_object, parse_constant=reject_constant)
    except json.JSONDecodeError as error:
        raise FixtureError(f"Invalid JSON: {error}") from error
    return validate_corpus(corpus)


@contextmanager
def offline_runtime(corpus):
    """Guard Python networking before import, and fail even if app code catches a block."""
    attempts = []

    def forbidden(name):
        def reject(*args, **kwargs):
            attempts.append(name)
            raise OfflineViolation(f"Forbidden offline I/O: {name}")
        return reject

    with ExitStack() as stack:
        for owner, name in (
            (socket.socket, "connect"), (socket.socket, "connect_ex"),
            (socket.socket, "sendto"), (socket, "create_connection"), (socket, "getaddrinfo"),
        ):
            stack.enter_context(patch.object(owner, name, side_effect=forbidden(f"socket.{name}")))
        from app import haystack_rag as rag
        rag._invalidate_metadata_cache()
        stack.callback(rag._invalidate_metadata_cache)
        for name in (
            "get_document_store", "_get_generator", "_get_text_embedder", "_retrieve_docs",
            "_retrieve_docs_for_question", "build_rag_retrieval_only_pipeline", "build_parcours_info",
        ):
            stack.enter_context(patch.object(rag, name, side_effect=forbidden(name)))
        stack.enter_context(patch.object(rag, "_fetch_documents_for_domaine", return_value=[]))
        stack.enter_context(patch.object(rag, "_get_q2_choices_list",
                                         return_value=list(corpus["synthetic_intentions"])))
        stack.enter_context(patch.object(rag.stats, "record"))
        try:
            yield rag
        finally:
            if attempts:
                raise OfflineViolation("Offline boundary attempts: " + ", ".join(attempts))


def history_for(case, corpus):
    history = case["history"]
    if isinstance(history, str):
        history = corpus["histories"][history]
    return [{"role": role, "content": corpus["questions"][content[1:]]
             if content.startswith("@") else content} for role, content in history]


def observation(rag, history, state):
    problem = rag._user_probleme_q3_text(history, selected_state=tuple(state))
    return {
        "state": list(state),
        "problem": problem,
        "ready": bool(problem and rag._should_inject_rag_documents(*state)),
        "intention_label": rag._get_intention_label_from_code(state[0], state[2], secteur_choisi=state[1]),
    }


def expanded_cases(corpus):
    for case in corpus["scenarios"]:
        for mode in case.get("modes", ["helper"]):
            yield dict(case, id=f"{case['id']}.{mode}" if "modes" in case else case["id"], mode=mode)


def expected_for(case, corpus):
    expected = dict(case["expected"])
    if case["kind"] != "full_flow":
        return expected
    domain, sector, intention = expected["state"]
    states = [[domain, None, None]]
    if sector is not None:
        states.append([domain, sector, None])
    states += [[domain, sector, intention], [domain, sector, intention]]
    expected["checkpoints"] = [
        {"state": state, "problem": corpus["problem_example"] if i == len(states) - 1 else "",
         "ready": i == len(states) - 1, "phase": phase}
        for i, (state, phase) in enumerate(zip(states, expected["phases"]))
    ]
    expected["problem"] = corpus["problem_example"]
    expected["ready"] = True
    return expected


def observe_case(case, corpus, rag):
    kind = case["kind"]
    if kind == "detect_step":
        return {"step": rag._detect_expected_step_from_assistant(case["question"])}
    if kind == "full_flow":
        domain = next(d for d in corpus["domains"] if d["code"] == case["domains"][0])
        mode = case["mode"]
        turns = [("domain", str(domain["number"]) if mode == "numeric" else domain["label"])]
        if domain["sectors"]:
            turns.append(("sector", "1" if mode == "numeric" else domain["sectors"][0]))
        turns += [("intention", "1" if mode == "numeric" else corpus["synthetic_intentions"][0]),
                  ("problem", corpus["problem_example"])]
        history, state, checkpoints = [], [None, None, None], []
        for step, reply in turns:
            history.append({"role": "assistant", "content": corpus["questions"][step]})
            result = rag._resolve_current_selection_state(history, reply, *state)
            history, state = result[0], list(result[1:])
            current = observation(rag, history, state)
            answer = rag._qualification_response(*state, "Liste de secteurs fictive",
                                                 "Liste d'objectifs fictive", "", current["problem"])
            phase = rag._detect_expected_step_from_assistant(answer) if answer else (
                "search" if current["ready"] else "unresolved")
            checkpoints.append({key: current[key] for key in ("state", "problem", "ready")} | {"phase": phase})
        return current | {"checkpoints": checkpoints, "phases": [c["phase"] for c in checkpoints]}
    history = history_for(case, corpus)
    if kind == "no_match":
        entry = rag.get_rag_prompt_and_sources if case["mode"] == "prompt" else rag.query_rag_haystack
        with patch.object(rag, "_retrieve_docs_for_question", return_value=[]) as retrieve:
            result = entry(case["query"], history, selected_domain_code=case["client"][0],
                           selected_sector=case["client"][1], selected_intention=case["client"][2])
        return {
            "state": list(result[5:8] if case["mode"] == "prompt" else result[8:11]),
            "answer": result[8] if case["mode"] == "prompt" else result[0],
            "sources": result[1], "suggested_case_ids": result[2],
            "retrieval_requests": [
                {"query": call.args[0], "state": [call.kwargs["selected_domain_code"],
                 call.kwargs["selected_sector"], call.kwargs["selected_intention"]]}
                for call in retrieve.call_args_list
            ],
        }
    with ExitStack() as stack:
        if kind in {"objective_order", "intention_label"}:
            stack.enter_context(patch.object(rag, "_get_q2_choices_list",
                                             return_value=case["current_intentions"]))
        result = rag._resolve_current_selection_state(history, case["query"], *case["client"])
        return observation(rag, result[0], result[1:])


def score(expected, actual):
    if not isinstance(actual, dict):
        return [{"field": "$", "expected": expected, "actual": actual}]
    return [{"field": key, "expected": value, "actual": actual.get(key), "missing": key not in actual}
            for key, value in expected.items() if key not in actual or actual[key] != value]


def counts(results):
    return {"total": len(results), "passed": sum(r["status"] == "pass" for r in results),
            "failed": sum(r["status"] == "fail" for r in results)}


def evaluate(corpus, *, observer=None):
    validate_corpus(corpus)
    results = []
    with offline_runtime(corpus) as rag:
        taxonomy = [
            {"number": number, "code": code, "label": rag.Q1_DOMAINS_LIST[number - 1],
             "sectors": [] if code in rag.DOMAINES_SANS_SECTEURS else list(rag.SECTEURS_PAR_DOMAINE.get(code, []))}
            for number, code in rag.CHOIX_Q1_TO_DOMAINE_CODE.items()
        ]
        taxonomy_differences = score({"domains": corpus["domains"]}, {"domains": taxonomy})
        for case in expanded_cases(corpus):
            expected = expected_for(case, corpus)
            actual = (observer or observe_case)(case, corpus, rag)
            differences = score(expected, actual)
            results.append({
                "id": case["id"], "kind": case["kind"], "mode": case["mode"],
                "category": case["category"], "requirement": case["requirement"],
                "domains": case["domains"], "scope": SCOPES[case["kind"]],
                "status": "fail" if differences else "pass",
                "expected": expected, "actual": actual, "differences": differences,
            })
    categories = {category: counts([r for r in results if r["category"] == category])
                  for category in sorted(CATEGORIES)}
    domain_coverage = {}
    for domain in corpus["domains"]:
        flows = [r for r in results if r["kind"] == "full_flow" and domain["code"] in r["domains"]]
        domain_coverage[domain["code"]] = {
            **counts(flows), "number": domain["number"], "label": domain["label"],
            "sector_required": bool(domain["sectors"]), "modes": sorted(r["mode"] for r in flows),
        }
    report = {
        "report_schema_version": 1, "evaluator_version": VERSION,
        "corpus_version": corpus["corpus_version"], "reference_contract": corpus["reference_contract"],
        "measurement": "Mechanical synthetic qualification only; not real-catalogue semantic accuracy.",
        "provenance": corpus["provenance"],
        "source_commit": corpus["source_commit"], "application_commit": corpus["application_commit"],
        "offline": {"network_allowed": False, "model_allowed": False, "workbook_read": False,
                    "real_retrieval": False, "metadata": "empty documents; two fictitious intentions",
                    "unexpected_io_attempts": 0},
        "summary": counts(results),
        "requirements": {name: counts([r for r in results if r["requirement"] == name])
                         for name in ("supported_baseline", "target_requirement")},
        "modes": dict(sorted(Counter(r["mode"] for r in results).items())),
        "categories": categories, "domain_coverage": domain_coverage,
        "taxonomy_snapshot": {"status": "fail" if taxonomy_differences else "pass",
                              "differences": taxonomy_differences},
        "observed_gaps": [r["id"] for r in results if r["status"] == "fail"
                          and r["requirement"] == "target_requirement"],
        "not_evaluated": [dict(item, status="not_evaluated") for item in corpus["not_evaluated"]],
        "results": results,
    }
    report["exit_code"] = int(bool(report["summary"]["failed"] or taxonomy_differences))
    return report


def source_fingerprints(fixture):
    files = {"fixture": Path(fixture), "evaluator": Path(__file__),
             "haystack_rag": BACKEND / "app" / "haystack_rag.py",
             "rag_constants": BACKEND / "app" / "rag_constants.py"}
    head = None
    git = shutil.which("git")
    git_status = "git_unavailable"
    if git:
        result = subprocess.run([git, "--no-pager", "rev-parse", "HEAD"], cwd=BACKEND,
                               check=False, capture_output=True, text=True)
        if result.returncode == 0:
            head = result.stdout.strip()
            require(re.fullmatch(r"[0-9a-f]{40}", head) is not None, "Invalid observed Git revision")
            git_status = "available"
        elif result.returncode == 128 and "not a git repository" in result.stderr.lower():
            git_status = "no_git_checkout"
        else:
            raise FixtureError(f"Cannot establish Git provenance (exit {result.returncode})")
    return {"observed_head": head, "git_status": git_status, "python_version": sys.version.split()[0],
            "sha256": {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in files.items()}}


def write_report(path, report):
    # Exclusive creation also protects against an output file appearing after argument validation.
    with Path(path).open("x", encoding="utf-8") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")


def print_summary(report):
    total = report["summary"]
    print(f"QUAL-01 {report['corpus_version']} | offline mechanical/synthetic only")
    print(f"Scenarios: {total['total']}; passed: {total['passed']}; failed: {total['failed']}")
    print("Requirements: " + json.dumps(report["requirements"], sort_keys=True))
    print("Modes: " + json.dumps(report["modes"], sort_keys=True))
    print("Domains: 14/14 numeric + label full flows; "
          f"taxonomy snapshot: {report['taxonomy_snapshot']['status']}")
    print("Categories: " + ", ".join(f"{key}={value['passed']}/{value['total']}"
                                     for key, value in report["categories"].items()))
    for result in report["results"]:
        if result["status"] == "fail":
            print(f"FAIL {result['id']} [{result['scope']}]: "
                  + json.dumps(result["differences"], ensure_ascii=False))
    print("Observed target gaps: " + (", ".join(report["observed_gaps"]) or "none"))
    print(f"Not evaluated ({len(report['not_evaluated'])}), excluded from pass/fail counts:")
    for item in report["not_evaluated"]:
        print(f"  {item['id']} -> {item['next']}: {item['reason']}")
    print("Source fingerprints: " + json.dumps(report["source_fingerprints"], sort_keys=True))


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog="Exit codes: 0 = measured checks pass (not_evaluated excluded); "
               "1 = measured failure/target gap or taxonomy drift; "
               "2 = invalid fixture/arguments, I/O boundary violation or report I/O error. "
               "No network, model, live mode, workbook, or real-catalogue evaluation.",
    )
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--output", type=Path, help="Explicit NEW JSON path; parent must exist; never overwritten")
    args = parser.parse_args(argv)
    try:
        if args.output is not None and args.output.exists():
            raise FileExistsError(f"Refusing to overwrite report: {args.output}")
        corpus = load_corpus(args.fixture)
        report = evaluate(corpus)
        report["source_fingerprints"] = source_fingerprints(args.fixture)
        if args.output is not None:
            write_report(args.output, report)
        print_summary(report)
        return report["exit_code"]
    except (FixtureError, OfflineViolation, OSError, UnicodeError, subprocess.CalledProcessError) as error:
        print(f"QUAL-01 evaluation error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
