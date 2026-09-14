"""Upgrade only the owned value entry in already-published pages, without a workbook."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import tarfile
import time

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

from app.value_editorial import SOURCE_FIELDS, editorial_for
from scripts.editorial_sources import extract

ENTRY = r"<!-- value-entry:[^>]+-->.*?<!-- /value-entry -->"


def page_archive_entry(name, raw):
    info = tarfile.TarInfo(name)
    info.size = len(raw)
    info.mtime = int(time.time())
    return info


def transform(text, page, template):
    source = extract(text, page)
    fields = {SOURCE_FIELDS[name]: value for name, value in source["fields"].items()}
    value = editorial_for(source["case_id"], fields)
    if not value:
        raise ValueError(f"{source['case_id']}: missing or stale editorial source")
    if len(re.findall(ENTRY, text, re.S)) != 1:
        raise ValueError("Missing or ambiguous owned value entry")
    fragment = template.render(c={**fields, "editorial": value}).strip()
    updated = re.sub(ENTRY, lambda _: fragment, text, count=1, flags=re.S)
    if re.sub(ENTRY, "", updated, flags=re.S) != re.sub(ENTRY, "", text, flags=re.S):
        raise ValueError("Unowned source, prompt or experience content changed")
    if extract(updated, page) != source:
        raise ValueError("Catalogue field changed")
    if re.findall(r'data-etape="(\d)"', updated) != ["1", "2", "3", "4", "5", "6"]:
        raise ValueError("Original six steps changed")
    for claim in value["claims"].values():
        if claim["text"] is None and not claim["unknown_reason"]:
            raise ValueError("Unknown editorial field not explained")
    return updated, source


def publish(pages, templates, report, write=False):
    repo = Path(__file__).resolve().parents[2]
    relative = pages.resolve().relative_to(repo).as_posix()
    if subprocess.check_output(["git", "status", "--porcelain", "--", relative], cwd=repo).strip():
        raise ValueError("Public pages changed: inspect rather than overwrite")
    original_archive = subprocess.check_output(["git", "archive", "HEAD", relative], cwd=repo)
    env = Environment(loader=FileSystemLoader(templates), undefined=StrictUndefined,
                      autoescape=select_autoescape(("html", "html.j2")))
    template = env.get_template("value-entry.html.j2")
    prepared, historical = [], []
    with tarfile.open(fileobj=io.BytesIO(original_archive)) as source:
        for entry in source:
            name = Path(entry.name).name
            if not entry.isfile() or not re.fullmatch(r"action-[a-z0-9]+\.html", name):
                continue
            raw = source.extractfile(entry).read()
            text = raw.decode("utf-8").replace("\r\n", "\n")
            if "base Avoulia v4.6.3 — cas " not in text:
                historical.append({"page": name, "sha256": hashlib.sha256(raw).hexdigest()})
                continue
            updated, record = transform(text, name, template)
            evidence = {"page": name, "case_id": record["case_id"],
                        "source_fingerprint": record["source_fingerprint"],
                        "before": hashlib.sha256(text.encode()).hexdigest(),
                        "after": hashlib.sha256(updated.encode()).hexdigest()}
            prepared.append((name, updated.encode("utf-8"), evidence))
    if len(prepared) != 1021 or len(historical) != 4 or len({r[2]["case_id"] for r in prepared}) != 1021:
        raise ValueError("Incomplete current or historical page universe")
    archive = report.parent / "public-pages-overlay.tar"
    with tarfile.open(archive, "w") as output:
        for name, raw, _ in prepared:
            output.addfile(page_archive_entry(name, raw), io.BytesIO(raw))
    if write:
        subprocess.run([r"C:\Windows\System32\tar.exe", "-xf", str(archive.resolve()),
                        "-C", str(pages.resolve())], check=True, capture_output=True)
    result = {"contract": "editorial-value-2", "status": "written" if write else "validated",
              "source_only_coverage": 0, "rich_editorial_coverage": len(prepared), "workbooks_read": 0,
              "pages": [row[2] for row in prepared], "historical": historical,
              "overlay_sha256": hashlib.sha256(archive.read_bytes()).hexdigest()}
    report.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return {key: value for key, value in result.items() if key not in ("pages", "historical")}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pages", type=Path, required=True)
    parser.add_argument("--templates", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    print(json.dumps(publish(args.pages, args.templates, args.report, args.write)))
