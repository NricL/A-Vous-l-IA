"""Text-only snapshot of independently published pages; no workbook or local source reader."""

import csv
import hashlib
import io
import json
import re
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from bs4 import BeautifulSoup

from app.preview_public_api import NoRedirect, PUBLIC_ORIGIN, public_parcours_url
from app.preview_repository import DOMAINS

MAPPING_URL = "https://raw.githubusercontent.com/NricL/A-Vous-l-IA/main/backend/app/static/parcours/mapping_uc_hash.csv"
ACCEPTED_VERSION = "v4.6.1"
SCHEMA_VERSION = 1
SOURCE_FIELDS = {
    "title", "description", "domaine_label", "intention", "secteur", "effort",
    "sensibilite_donnees", "questions_qualification", "prerequis_donnees",
    "guardrails", "premiere_action_48h", "mode_execution", "declencheurs_typiques",
}


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def one_text(soup, selector):
    elements = soup.select(selector)
    return elements[0].get_text().strip() if len(elements) == 1 else None


def parse_page(raw: bytes, case_id: str, case_hash: str) -> dict:
    url = public_parcours_url(f"{PUBLIC_ORIGIN}/action-{case_hash}.html", case_hash)
    soup = BeautifulSoup(raw.decode("utf-8-sig"), "html.parser")
    for node in soup(["script", "style", "iframe", "noscript"]):
        node.decompose()
    footer = one_text(soup, "footer") or ""
    versions = re.findall(r"base Avoulia (v\d+\.\d+\.\d+)\s*—\s*cas (UC-\d{3,5})", footer)
    if len(versions) != 1 or versions[0][1] != case_id:
        raise ValueError(f"Published footer identity unavailable or conflicting: {case_id}")
    version = versions[0][0]
    receipt = {"case_id": case_id, "case_hash": case_hash, "url": url,
               "version": version, "page_sha256": hashlib.sha256(raw).hexdigest()}
    if version != ACCEPTED_VERSION:
        return {**receipt, "excluded": "observed_version_not_v4.6.1"}
    title = one_text(soup, "header h1")
    description = one_text(soup, "header .resume")
    badges = [p.get_text().strip() for p in soup.select("header .puces .puce")]
    prompts = [p.get_text() for p in soup.select("pre")]

    def prompt_field(label):
        values = set()
        for prompt in prompts:
            values.update(re.findall(r"^" + re.escape(label) + r" : (.+)\.\s*$", prompt, re.MULTILINE))
        if len(values) != 1:
            return None
        return next(iter(values)).strip()

    domain_label = prompt_field("Domaine métier du cas")
    objective = prompt_field("Mon objectif prioritaire est")
    sector = prompt_field("Contexte secteur")
    prompt_title = prompt_field("Cas d'usage cible")
    domains = [code for code, label in DOMAINS.items() if label == domain_label]
    if (not title or not description or len(domains) != 1 or len(badges) != 4
            or badges[:2] != [domain_label, objective] or prompt_title != title
            or not sector or not badges[2].startswith("Effort : ")
            or not badges[3].startswith("Données : ")):
        raise ValueError(f"Published identity/scope fields unavailable or conflicting: {case_id}")
    # Lists preserve individual published labels, not a reconstructed private cell.
    def labels(prefix):
        values = [node.get_text().strip() for node in soup.select(f'label[for^="{prefix}"]')]
        return values or None

    action = None
    for node in soup.select('[data-etape="4"] .contenu > p'):
        if node.get_text().strip() == "Votre première action proposée — adaptez le délai à vos contraintes :":
            following = node.find_next_sibling("p")
            if following is not None and not following.get("class"):
                action = following.get_text().strip()
    fields = {
        "title": title, "description": description, "domaine_label": domain_label,
        "intention": objective, "secteur": sector, "effort": badges[2][len("Effort : "):],
        "sensibilite_donnees": badges[3][len("Données : "):],
        "questions_qualification": labels("e1q"), "prerequis_donnees": labels("e2p"),
        "guardrails": labels("e3g"), "premiere_action_48h": action,
        "mode_execution": None, "declencheurs_typiques": None,
    }
    return {**receipt, "source_mode": "PUBLIC_PAGES", "domain": domains[0],
            "source_fields": fields, "source_hash": digest(fields),
            "unavailable_fields": [key for key, value in fields.items() if value is None]}


class PublicGet:
    def __init__(self, pause=0.25):
        self.opener = urllib.request.build_opener(NoRedirect())
        self.calls = self.failures = 0
        self.pause = max(0.25, pause)

    def __call__(self, url):
        if url != MAPPING_URL and not re.fullmatch(re.escape(PUBLIC_ORIGIN) + r"/action-[a-z0-9]{6,64}\.html", url):
            raise ValueError("Only the public mapping and known action pages are permitted")
        for attempt in range(3):
            time.sleep(self.pause if attempt == 0 else 2 ** attempt)
            self.calls += 1
            try:
                request = urllib.request.Request(url, headers={"Accept": "text/html,text/plain,text/csv",
                                                             "User-Agent": "AVIA-local-public-snapshot/1"})
                with self.opener.open(request, timeout=30) as response:
                    raw = response.read(524289)
                    if response.status != 200 or len(raw) > 524288:
                        raise ValueError("Unexpected public resource response")
                    return raw
            except urllib.error.HTTPError as error:
                self.failures += 1
                if error.code not in {408, 429, 500, 502, 503, 504} or attempt == 2:
                    raise
            except (urllib.error.URLError, TimeoutError, OSError):
                self.failures += 1
                if attempt == 2:
                    raise


def build_snapshot(cache: Path, fetch=None):
    """Sequential GETs only. Mapping stays in memory; only public-derived fields persist."""
    fetch = fetch or PublicGet()
    cache.mkdir(parents=True, exist_ok=True)
    mapping = fetch(MAPPING_URL)
    rows = list(csv.DictReader(io.StringIO(mapping.decode("utf-8-sig"))))
    if (not rows or len(rows) > 1500 or len({r.get("case_id") for r in rows}) != len(rows)
            or len({r.get("case_hash") for r in rows}) != len(rows)):
        raise ValueError("Invalid public mapping identities")
    for row in rows:
        if (set(row) != {"case_id", "case_hash"} or not re.fullmatch(r"UC-\d{3,5}", row["case_id"])
                or not re.fullmatch(r"[a-z0-9]{6,64}", row["case_hash"])):
            raise ValueError("Unexpected mapping schema")
    records, excluded, errors = [], [], []
    for number, row in enumerate(rows, 1):
        key, hashed = row["case_id"], row["case_hash"]
        path = cache / f"{key}.json"
        try:
            if path.exists():
                record = json.loads(path.read_text(encoding="utf-8"))
                if record.get("case_id") != key or record.get("case_hash") != hashed:
                    raise ValueError("Cached identity changed")
            else:
                record = parse_page(fetch(f"{PUBLIC_ORIGIN}/action-{hashed}.html"), key, hashed)
                path.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
            (excluded if record.get("excluded") else records).append(record)
        except Exception as error:
            errors.append({"case_id": key, "error": type(error).__name__, "message": str(error)[:200]})
        if number % 50 == 0 or number == len(rows):
            print(json.dumps({"processed": number, "accepted": len(records), "excluded": len(excluded),
                              "errors": len(errors), "get_calls": getattr(fetch, "calls", None)}), flush=True)
    inventory = {
        "schema_version": SCHEMA_VERSION, "source_mode": "PUBLIC_PAGES",
        "version": ACCEPTED_VERSION, "built_at": datetime.now(timezone.utc).isoformat(),
        "mapping_url": MAPPING_URL, "mapping_sha256": hashlib.sha256(mapping).hexdigest(),
        "mapping_count": len(rows), "case_count": len(records), "excluded": excluded, "errors": errors,
        "observed_versions": dict(Counter(r["version"] for r in records + excluded)),
        "get_calls_this_build": getattr(fetch, "calls", None), "get_failures_this_build": getattr(fetch, "failures", None),
        "domain_counts": dict(Counter(r["domain"] for r in records)), "records": records,
    }
    inventory["catalogue_revision"] = digest(records)
    target = cache / "snapshot.json"
    target.write_text(json.dumps(inventory, ensure_ascii=False), encoding="utf-8")
    if errors:
        raise ValueError(f"Snapshot incomplete: {len(errors)} page errors; inventory persisted, no ready index")
    return inventory


def load_snapshot(cache: Path):
    payload = json.loads((cache / "snapshot.json").read_text(encoding="utf-8"))
    records = payload["records"]
    if (payload.get("source_mode") != "PUBLIC_PAGES" or payload.get("version") != ACCEPTED_VERSION
            or payload.get("schema_version") != SCHEMA_VERSION or payload.get("errors")
            or payload.get("catalogue_revision") != digest(records)
            or len(records) != payload.get("case_count") or not records
            or len({r["case_id"] for r in records}) != len(records)):
        raise ValueError("Invalid/incomplete PUBLIC_PAGES snapshot")
    for row in records:
        fields = row["source_fields"]
        if (row.get("source_mode") != "PUBLIC_PAGES" or row.get("version") != ACCEPTED_VERSION
                or row["source_hash"] != digest(fields) or set(fields) != SOURCE_FIELDS
                or row["domain"] not in DOMAINS or fields["domaine_label"] != DOMAINS[row["domain"]]):
            raise ValueError("Unexpected public record or version")
        public_parcours_url(row["url"], row["case_hash"])
    return payload
