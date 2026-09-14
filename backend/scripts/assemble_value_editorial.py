"""Assemble already-authored/source-reviewed batches; does not author or prove claims."""
import argparse
import json
from pathlib import Path

from scripts.validate_value_editorial import validate_rows


def assemble(batches, revisions, output, report):
    sources = json.loads((batches / "sources.json").read_text(encoding="utf-8"))
    known = {row["case_id"]: row for row in sources}
    rows = []
    for path in sorted(batches.glob("batch-??-editorial.json")):
        rows.extend(json.loads(path.read_text(encoding="utf-8")))
    rows = validate_rows(rows, sources)
    if len(rows) != 1021 or [r["case_id"] for r in rows] != [r["case_id"] for r in sources]:
        raise ValueError("Incomplete or reordered reviewed source universe")
    changes = json.loads(revisions.read_text(encoding="utf-8"))
    if set(changes) - set(known):
        raise ValueError("Unknown editorial revision")
    changed = 0
    for row in rows:
        for name, value in changes.get(row["case_id"], {}).items():
            claim = row["claims"][name]
            claim["text"] = value["text"] if isinstance(value, dict) else value
            if name == "gain":
                claim["evidence"].append({"field": "description", "quote": known[row["case_id"]]["fields"]["description"]})
            if isinstance(value, dict):
                claim["evidence"].extend(value.get("evidence", []))
            changed += 1
    rows = validate_rows(rows, sources)
    published = [{key: row[key] for key in ("case_id", "source_fingerprint", "horizon_kind", "claims")}
                 for row in rows]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"schema_version": 2, "cases": published}, ensure_ascii=False, indent=2),
                      encoding="utf-8", newline="\n")
    result = {
        "evaluated_source_cases": len(rows),
        "authored_source_reviewed_cases": sum(any(c["text"] is not None for c in r["claims"].values()) for r in rows),
        "authored_claims": sum(c["text"] is not None for r in rows for c in r["claims"].values()),
        "unknown_fields": {name: sum(r["claims"][name]["text"] is None for r in rows) for name in rows[0]["claims"]},
        "coordinator_revised_cases": len(changes), "coordinator_revised_claims": changed,
        "measured_business_gain_established": 0, "elapsed_time_to_value_established": 0,
        "workbooks_read": 0, "structural_source_gate": "passed",
        "review_method": "Individual AI source authorship/review; coordinator targeted semantic QA. Not human or real-world validation.",
        "automated_gate_is_not_semantic_proof": True,
    }
    report.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batches", type=Path, required=True)
    parser.add_argument("--revisions", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(assemble(args.batches, args.revisions, args.output, args.report)))
