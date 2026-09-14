"""Apply presentation-only fragments to already-public v4.6.3 HTML; never read a workbook."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import re

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

from app.value_contract import HORIZON, LIMIT, TRADEOFF, USEFUL_WHEN, VERSION

HANDOFF = "AVIA vous oriente et fournit un guide ; l'exécution se fait dans l'assistant IA autorisé que vous choisissez. Copier un prompt ne l'envoie pas et ne lance aucun travail dans cet assistant."


def transform(text, templates):
    if 'value-entry:' in text:
        raise ValueError("Already enriched: do not apply twice")
    identity = re.findall(r"base Avoulia v4\.6\.3 — cas (UC-\d{4})\.", text)
    if len(identity) != 1:
        raise ValueError("Not an unambiguous current public page")
    step4 = re.findall(r'<section[^>]*data-etape="4"[^>]*>(.*?)</section>', text, re.S)
    actions = re.findall(r'<p class="source">(.*?)</p>', step4[0], re.S) if len(step4) == 1 else []
    if len(actions) != 1:
        raise ValueError("Missing or ambiguous public source action")
    c = {"premiere_action_48h": html.unescape(actions[0])}
    fragments = {name: templates.get_template(f"value-{name}.html.j2").render(c=c)
                 for name in ("entry", "review", "return", "script")}
    for value in (HORIZON, LIMIT, TRADEOFF, USEFUL_WHEN, VERSION):
        if value not in fragments["entry"]:
            raise ValueError("API/parcours presentation contract drift")
    replacements = [
        ("</header>", "</header>\n" + fragments["entry"]),
        ("<h2>Commencez par un petit essai</h2>",
         "<h2>Commencez par un petit essai</h2>\n  <p>" + HANDOFF + "</p>"),
        ('<div class="valider"><input type="checkbox" id="fin-5"',
         fragments["review"] + '\n        <div class="valider"><input type="checkbox" id="fin-5"'),
        ('<div class="valider"><input type="checkbox" id="fin-6"',
         fragments["return"] + '\n        <div class="valider"><input type="checkbox" id="fin-6"'),
        ("</body>", fragments["script"] + "\n</body>"),
    ]
    before_prompts = re.findall(r"<pre>(.*?)</pre>", text, re.S)
    before_source = re.findall(r'<(?:p|span)[^>]*class="[^"]*\bsource\b[^"]*"[^>]*>(.*?)</(?:p|span)>', text, re.S)
    original = text
    for old, new in replacements:
        if text.count(old) != 1:
            raise ValueError("Missing or ambiguous insertion anchor")
        text = text.replace(old, new, 1)
    if re.findall(r"<pre>(.*?)</pre>", text, re.S) != before_prompts:
        raise ValueError("Prompt changed")
    for source in before_source:
        if source not in text:
            raise ValueError("Source field changed")
    if re.findall(r'data-etape="(\d)"', text) != ["1", "2", "3", "4", "5", "6"]:
        raise ValueError("Step order changed")
    return text, {"case_id": identity[0], "before": hashlib.sha256(original.encode()).hexdigest(),
                  "after": hashlib.sha256(text.encode()).hexdigest()}


def publish(pages, template_root, report, write=False):
    templates = Environment(loader=FileSystemLoader(template_root), undefined=StrictUndefined,
                            autoescape=select_autoescape(("html", "html.j2")))
    prepared, historical = [], []
    for path in sorted(pages.glob("action-*.html")):
        original = path.read_text(encoding="utf-8")
        if "base Avoulia v4.6.3 — cas " not in original:
            historical.append({"page": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
            continue
        rendered, evidence = transform(original, templates)
        prepared.append((path, rendered, {"page": path.name, **evidence}))
        if len(prepared) % 100 == 0:
            print(f"Validated {len(prepared)} public pages", flush=True)
    if len(prepared) != 1021 or len(historical) != 4 or len({p[2]["case_id"] for p in prepared}) != 1021:
        raise ValueError("Expected 1021 unique current pages and four historical pages")
    if write:
        for path, rendered, _ in prepared:
            path.write_text(rendered, encoding="utf-8", newline="\n")
    result = {"contract": VERSION, "status": "written" if write else "validated",
              "source_only_coverage": len(prepared), "rich_editorial_coverage": 0,
              "workbooks_read": 0, "pages": [p[2] for p in prepared], "historical": historical}
    report.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return {k: v for k, v in result.items() if k not in ("pages", "historical")}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pages", type=Path, required=True)
    parser.add_argument("--templates", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    print(json.dumps(publish(args.pages, args.templates, args.report, args.write)))
