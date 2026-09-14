"""Extract only already-public source fields for bounded editorial review."""
import argparse
import html
import io
import json
from pathlib import Path
import re
import subprocess
import tarfile

from app.value_editorial import source_fingerprint


def unique(pattern, text, decode=True):
    found = re.findall(pattern, text, re.S)
    if len(found) != 1:
        raise ValueError("Missing or ambiguous public source field")
    return html.unescape(found[0]) if decode else found[0]


def extract(text, page):
    identity = unique(r"base Avoulia v4\.6\.3 — cas (UC-\d{4})\.", text)
    step4 = unique(r'<section[^>]*data-etape="4"[^>]*>(.*?)</section>', text, decode=False)
    step3 = unique(r'<section[^>]*data-etape="3"[^>]*>(.*?)</section>', text, decode=False)
    fields = {
        "title": unique(r"<h1>(.*?)</h1>", text),
        "description": unique(r'<p class="resume source">(.*?)</p>', text),
        "first_action": unique(r'<p class="source">(.*?)</p>', step4),
        "guardrails": unique(r'<p class="source">(.*?)</p>', step3),
    }
    return {"case_id": identity, "page": page, "source_fingerprint": source_fingerprint(fields),
            "fields": fields}


def prepare(pages, output):
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise ValueError("Refusing to overwrite an existing editorial batch")
    repo = Path(__file__).resolve().parents[2]
    relative = pages.resolve().relative_to(repo).as_posix()
    dirty = subprocess.check_output(["git", "status", "--porcelain", "--", relative], cwd=repo)
    if dirty.strip():
        raise ValueError("Public pages changed: review before choosing the committed source snapshot")
    archive = subprocess.check_output(["git", "archive", "HEAD", relative], cwd=repo)
    rows = []
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        for entry in tar:
            if not entry.isfile() or not re.fullmatch(r"action-[a-z0-9]+\.html", Path(entry.name).name):
                continue
            text = tar.extractfile(entry).read().decode("utf-8").replace("\r\n", "\n")
            if "base Avoulia v4.6.3 — cas " in text:
                rows.append(extract(text, Path(entry.name).name))
    rows.sort(key=lambda row: row["case_id"])
    if len(rows) != 1021 or len({row["case_id"] for row in rows}) != 1021:
        raise ValueError("Expected 1021 current unique public cases")
    batches = []
    for start in range(0, len(rows), 64):
        name = f"batch-{len(batches) + 1:02d}"
        batch = rows[start:start + 64]
        (output / (name + "-sources.json")).write_text(
            json.dumps({"provenance": "Already-public v4.6.3 HTML source fields only",
                        "cases": batch}, ensure_ascii=False, indent=2), encoding="utf-8")
        batches.append({"batch": name, "count": len(batch),
                        "first": batch[0]["case_id"], "last": batch[-1]["case_id"]})
    (output / "sources.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    (output / "batches.json").write_text(json.dumps(batches, indent=2), encoding="utf-8")
    return {"public_cases": len(rows), "batches": len(batches), "workbooks_read": 0}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pages", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.pages, args.output)))
