"""Apply reviewed accessibility-only changes to public pages, never a workbook."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import tarfile

from scripts.editorial_sources import extract
from scripts.publish_editorial_pages import page_archive_entry

REPLACEMENTS = (
    (
        "input:focus-visible,summary:focus-visible,textarea:focus-visible,select:focus-visible{outline:2px solid var(--action);outline-offset:2px}",
        "input:focus-visible,summary:focus-visible,textarea:focus-visible,select:focus-visible{outline:2px solid var(--action);outline-offset:2px}\n"
        "summary:focus-visible{outline-offset:-3px}\n"
        ".copie-statut{position:absolute;width:1px;height:1px;padding:0;overflow:hidden;clip-path:inset(50%);white-space:nowrap}",
    ),
    (
        "</div>\n<script>",
        '</div>\n<p id="copie-statut" class="copie-statut" role="status" aria-atomic="true"></p>\n<script>',
    ),
    (
        "  // boutons copier\n",
        "  // boutons copier\n  var statutCopie=document.getElementById('copie-statut');\n",
    ),
    (
        "    btn.addEventListener('click',function(){\n",
        "    btn.addEventListener('click',function(){\n      statutCopie.textContent='';\n",
    ),
    (
        '      function ok(){ btn.textContent="Copié ✓"; setTimeout(function(){btn.textContent="Copier";},2000); }',
        '      function ok(){ btn.textContent="Copié ✓"; statutCopie.textContent="Texte copié. Collez-le vous-même dans votre assistant IA autorisé."; setTimeout(function(){btn.textContent="Copier";},2000); }',
    ),
    (
        "          manuel.focus(); manuel.select();",
        '          manuel.focus(); manuel.select();\n          statutCopie.textContent="Copie automatique indisponible. Le texte est sélectionné pour une copie manuelle.";',
    ),
)


def replace_owned(text):
    if 'id="copie-statut"' in text or "summary:focus-visible{outline-offset:-3px}" in text:
        raise ValueError("Accessibility patch already present")
    result = text
    for before, after in REPLACEMENTS:
        if result.count(before) != 1:
            raise ValueError("Missing or ambiguous approved replacement")
        result = result.replace(before, after, 1)
    restored = result
    for before, after in reversed(REPLACEMENTS):
        restored = restored.replace(after, before, 1)
    if restored != text:
        raise ValueError("Unowned bytes changed")
    return result


def transform(text, page):
    source = extract(text, page)
    updated = replace_owned(text)
    if source != extract(updated, page):
        raise ValueError("Source identity or fields changed")
    for pattern in (r"<pre\b[^>]*>.*?</pre>", r"<!-- value-entry:.*?<!-- /value-entry -->",
                    r'data-etape="\d"'):
        if re.findall(pattern, text, re.S) != re.findall(pattern, updated, re.S):
            raise ValueError("Prompt, editorial value or six steps changed")
    return updated, source


def publish(report, write=False):
    repo = Path(__file__).resolve().parents[2]
    relative = "backend/app/static/parcours"
    if subprocess.check_output(["git", "status", "--porcelain", "--", relative], cwd=repo).strip():
        raise ValueError("Public pages already modified")
    original = subprocess.check_output(["git", "archive", "HEAD", relative], cwd=repo)
    prepared, historical = [], []
    with tarfile.open(fileobj=io.BytesIO(original)) as archive:
        for entry in archive:
            name = Path(entry.name).name
            if not entry.isfile() or not re.fullmatch(r"action-[a-z0-9]+\.html", name):
                continue
            raw = archive.extractfile(entry).read()
            text = raw.decode("utf-8")
            if "base Avoulia v4.6.3 — cas " not in text:
                historical.append({"page": name, "sha256": hashlib.sha256(raw).hexdigest()})
                continue
            # git archive can apply Windows checkout endings; deployment uses canonical LF.
            text = text.replace("\r\n", "\n")
            raw = text.encode()
            updated, source = transform(text, name)
            evidence = {"page": name, "case_id": source["case_id"],
                        "source_fingerprint": source["source_fingerprint"],
                        "before": hashlib.sha256(raw).hexdigest(),
                        "after": hashlib.sha256(updated.encode()).hexdigest()}
            prepared.append((name, updated.encode(), evidence))
    if len(prepared) != 1021 or len(historical) != 4 or len({p[2]["case_id"] for p in prepared}) != 1021:
        raise ValueError("Incomplete page universe")
    overlay = report.parent / "public-pages-overlay.tar"
    with tarfile.open(overlay, "w") as archive:
        for name, raw, _ in prepared:
            archive.addfile(page_archive_entry(name, raw), io.BytesIO(raw))
    if write:
        subprocess.run([r"C:\Windows\System32\tar.exe", "-xf", str(overlay.resolve()),
                        "-C", str(repo / relative)], check=True, capture_output=True)
    result = {"status": "written" if write else "validated", "workbooks_read": 0,
              "current_pages": 1021, "source_fields_prompts_editorial_unchanged": True,
              "pages": [p[2] for p in prepared], "historical": historical,
              "overlay_sha256": hashlib.sha256(overlay.read_bytes()).hexdigest()}
    report.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return {k: v for k, v in result.items() if k not in ("pages", "historical")}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    print(json.dumps(publish(args.report, args.write)))
