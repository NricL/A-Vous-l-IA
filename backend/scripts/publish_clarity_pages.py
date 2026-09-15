"""Render current journeys from committed public HTML only; never open a workbook."""
import argparse
import hashlib
import html
import importlib.util
import io
import json
from pathlib import Path
import re
import subprocess
import tarfile

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

from app.value_editorial import SOURCE_FIELDS, editorial_for
from scripts.editorial_sources import extract, unique
from scripts.publish_editorial_pages import page_archive_entry


def section(text, number):
    return unique(rf'<section[^>]*data-etape="{number}"[^>]*>(.*?)</section>', text, decode=False)


def public_case(text, page):
    source = extract(text, page)
    c = {SOURCE_FIELDS[k]: v for k, v in source["fields"].items()}
    c["use_case_id"] = source["case_id"]
    pills = [html.unescape(p) for p in re.findall(r'<span class="puce(?: sensible)?">(.*?)</span>', text)]
    if len(pills) != 4 or not pills[2].startswith("Effort : ") or not pills[3].startswith("Données : "):
        raise ValueError(f"{page}: metadata shape changed")
    c.update(domaine_label=pills[0], intention=pills[1], effort=pills[2][9:],
             sensibilite_donnees=pills[3][10:])
    c["questions"] = [html.unescape(q) for q in re.findall(r"<li>(.*?)</li>", section(text, 1), re.S)]
    c["prereqs"] = [html.unescape(p) for p in re.findall(
        r'<label class="source" for="e2p\d+">(.*?)</label>', section(text, 2), re.S)]
    prompts = [html.unescape(p) for p in re.findall(r"<pre>(.*?)</pre>", text, re.S)]
    if not prompts:
        raise ValueError(f"{page}: missing public context")
    sectors = re.findall(r"^Contexte secteur : (.*?)\.\n", prompts[0], re.M)
    if len(sectors) > 1:
        raise ValueError(f"{page}: ambiguous sector")
    c["secteur"] = sectors[0] if sectors else None
    step5 = section(text, 5)
    if "Testez le fonctionnement sur un périmètre réel limité" in step5:
        c["mode_execution"] = "no_code"
    elif "Avec les données et validations nécessaires" in step5:
        c["mode_execution"] = "outil"
    else:
        raise ValueError(f"{page}: unknown execution mode")
    footer = unique(r"<footer>(.*?)</footer>", text, decode=False)
    app_url = unique(r'<a href="([^"]+)">', footer)
    return c, app_url, source


def load_rendering(root):
    spec = importlib.util.spec_from_file_location("public_parcours_prompts", root / "pipeline/parcours_prompts.py")
    prompts = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prompts)
    env = Environment(loader=FileSystemLoader(root / "templates"), undefined=StrictUndefined,
                      autoescape=select_autoescape(("html", "html.j2")))
    templates = {p.stem: p.read_text(encoding="utf-8") for p in (root / "templates/etapes").glob("*.md")}
    return prompts, env.get_template("page.html.j2"), templates


def render(c, app_url, page, rendering):
    import markdown
    from urllib.parse import urlsplit
    prompts, template, steps = rendering
    value = editorial_for(c["use_case_id"], c)
    if not value:
        raise ValueError(f"{page}: missing or stale approved editorial content")
    parsed = urlsplit(app_url)
    case_hash = page.removeprefix("action-").removesuffix(".html")
    result = template.render(
        c={**c, "editorial": value, "prompt_principal": prompts.prompt_principal(c),
           "prompts_preparation": [prompts.prompt_preparation(c, p) for p in c["prereqs"]],
           "prompt_reutilisation": prompts.prompt_reutilisation(c)},
        hash=case_hash, version_base="v4.6.3", app_url=app_url,
        app_label=parsed.netloc + parsed.path.rstrip("/"),
        etape5=markdown.markdown(steps["etape5_" + c["mode_execution"]]),
        etape6=markdown.markdown(steps["etape6_" + c["mode_execution"]]))
    counter = 0
    def checkbox(match):
        nonlocal counter
        counter += 1
        return (f'<div class="coche"><input type="checkbox" id="auto{counter}" data-suivi>'
                f'<label for="auto{counter}">{match[1]}</label></div>')
    return re.sub(r"<li>\[ \] (.*?)</li>", checkbox, result)


def check_prompts(text, c, prompts):
    expected = ([prompts.prompt_preparation(c, p) for p in c["prereqs"]]
                + [prompts.prompt_principal(c), prompts.prompt_reutilisation(c)])
    actual = [html.unescape(p) for p in re.findall(r"<pre>(.*?)</pre>", text, re.S)]
    if actual != expected:
        raise ValueError("Displayed/copied prompt contract changed")
    for prompt in actual:
        if c["cas_utilisation"] not in prompt or c["guardrails"] not in prompt or c["premiere_action_48h"] not in prompt:
            raise ValueError("Missing case, action or safety context")
        authored = prompt
        # Only authored instructions are checked for hidden stage dependencies; source stays verbatim.
        for value in sorted([str(v) for v in c.values() if isinstance(v, str)] + c["prereqs"], key=len, reverse=True):
            authored = authored.replace(value, "")
        if re.search(r"étape\s*[1-6]|ci-dessus|déjà fournis plus haut|reprends", authored, re.I):
            raise ValueError("Hidden conversation or step dependency")
        for required in ("[", "crochets non complétés", "trois questions", "données dont le partage est autorisé",
                         "N'invente jamais", "Aucun envoi", "validation humaine"):
            if required not in prompt:
                raise ValueError(f"Missing standalone contract: {required}")
    if len(re.findall(r"<pre>", section(text, 4))) != 1 or len(re.findall(r"<pre>", section(text, 6))) != 1:
        raise ValueError("Prompts are outside their working step")


def transform(text, page, rendering):
    c, app_url, source = public_case(text, page)
    updated = render(c, app_url, page, rendering)
    after, after_url, after_source = public_case(updated, page)
    if (c, app_url, source) != (after, after_url, after_source):
        raise ValueError(f"{page}: a public source field, identity or link changed")
    for marker in ("data-etape", "data-fin"):
        if re.findall(rf'{marker}="(\d)"', updated) != list("123456"):
            raise ValueError(f"{page}: six-step sequence changed")
    for forbidden in ("Conditions, contreparties et première action", "Passages source utilisés",
                      "Gardez le lien", "gardez le lien", "Revenir volontairement", "copier-lien",
                      "lien-retour", "quickwin-accordion"):
        if forbidden in updated:
            raise ValueError(f"{page}: obsolete interface remains")
    # Existing copy fallback, focus behavior, persisted checkboxes and unsaved review stay intact.
    before_script = unique(r'<p id="copie-statut".*?(<script>.*?</script>)', text, decode=False)
    after_script = unique(r'<p id="copie-statut".*?(<script>.*?</script>)', updated, decode=False)
    if before_script != after_script:
        raise ValueError(f"{page}: interaction script changed")
    before_review = re.findall(r"<!-- value-review:.*?<!-- /value-review -->", text, re.S)
    if before_review != re.findall(r"<!-- value-review:.*?<!-- /value-review -->", updated, re.S):
        raise ValueError(f"{page}: optional unsaved review changed")
    check_prompts(updated, c, rendering[0])
    return updated, source, c


def publish(templates, report, write=False, previous_report=None):
    repo = Path(__file__).resolve().parents[2]
    relative = "backend/app/static/parcours"
    dirty = subprocess.check_output(["git", "status", "--porcelain", "--", relative], cwd=repo).decode().splitlines()
    if dirty:
        if previous_report is None:
            raise ValueError("Public pages already modified; inspect before replacing")
        previous = json.loads(previous_report.read_text(encoding="utf-8"))
        if previous.get("status") != "written" or previous.get("current_pages") != 1021:
            raise ValueError("Expected a prior complete written clarity receipt")
        allowed = {relative + "/" + row["page"] for row in previous["pages"]}
        if any(line[:3] != " M " or line[3:] not in allowed for line in dirty):
            raise ValueError("Unowned changes exist in public pages")
        allowlist = report.parent / "owned-page-allowlist.txt"
        allowlist.write_text("\n".join(row["page"] for row in previous["pages"]) + "\n", encoding="utf-8")
        packed = subprocess.check_output([r"C:\Windows\System32\tar.exe", "-cf", "-", "-C",
                                          str(repo / relative), "-T", str(allowlist.resolve())])
        with tarfile.open(fileobj=io.BytesIO(packed)) as current:
            hashes = {m.name: hashlib.sha256(current.extractfile(m).read().replace(b"\r\n", b"\n")).hexdigest()
                      for m in current if m.isfile()}
        if hashes != {row["page"]: row["after"] for row in previous["pages"]}:
            raise ValueError("Page changed since prior clarity write")
    rendering = load_rendering(templates)
    original = subprocess.check_output(["git", "archive", "HEAD", relative], cwd=repo)
    prepared, historical, inputs = [], [], 0
    with tarfile.open(fileobj=io.BytesIO(original)) as archive:
        for entry in archive:
            page = Path(entry.name).name
            if not entry.isfile() or not re.fullmatch(r"action-[a-z0-9]+\.html", page):
                continue
            raw = archive.extractfile(entry).read()
            text = raw.decode("utf-8").replace("\r\n", "\n")
            if "base Avoulia v4.6.3 — cas " not in text:
                historical.append({"page": page, "sha256": hashlib.sha256(raw).hexdigest()})
                continue
            updated, source, c = transform(text, page, rendering)
            inputs += len(c["prereqs"])
            prepared.append((page, updated.encode(), {
                "page": page, "case_id": source["case_id"], "source_fingerprint": source["source_fingerprint"],
                "before": hashlib.sha256(text.encode()).hexdigest(),
                "after": hashlib.sha256(updated.encode()).hexdigest(),
                "domain": c["domaine_label"], "mode": c["mode_execution"], "preparation_prompts": len(c["prereqs"])}))
    if len(prepared) != 1021 or len(historical) != 4 or inputs != 3774 or len({p[2]["case_id"] for p in prepared}) != 1021:
        raise ValueError("Incomplete public page/input universe")
    overlay = report.parent / "public-pages-overlay.tar"
    with tarfile.open(overlay, "w") as archive:
        for name, raw, _ in prepared:
            archive.addfile(page_archive_entry(name, raw), io.BytesIO(raw))
    if write:
        subprocess.run([r"C:\Windows\System32\tar.exe", "-xf", str(overlay.resolve()),
                        "-C", str(repo / relative)], check=True, capture_output=True)
    result = {"status": "written" if write else "validated", "current_pages": 1021,
              "preparation_prompts": inputs, "production_prompts": 1021, "reuse_prompts": 1021,
              "workbooks_read": 0, "all_public_source_fields_and_urls_unchanged": True,
              "editorial_data_unchanged": True, "old_prompts_intentionally_replaced": True,
              "pages": [p[2] for p in prepared], "historical": historical,
              "overlay_sha256": hashlib.sha256(overlay.read_bytes()).hexdigest()}
    report.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return {k: v for k, v in result.items() if k not in ("pages", "historical")}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--templates", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--previous-report", type=Path)
    args = parser.parse_args()
    print(json.dumps(publish(args.templates, args.report, args.write, args.previous_report)))
