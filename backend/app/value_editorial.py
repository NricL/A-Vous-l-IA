"""Reviewed editorial hypotheses, isolated from catalogue fields and selection."""
from functools import lru_cache
import hashlib
import json
from pathlib import Path

SOURCE_FIELDS = {
    "title": "cas_utilisation",
    "description": "description_cas_utilisation",
    "first_action": "premiere_action_48h",
    "guardrails": "guardrails",
}
CONTENT_PATH = Path(__file__).resolve().parent / "content" / "value_editorial.json"


def source_fields(source):
    return {name: str(source.get(key) or "").replace("\r\n", "\n").replace("\r", "\n")
            for name, key in SOURCE_FIELDS.items()}


def source_fingerprint(fields):
    normalized = {name: str(fields.get(name) or "").replace("\r\n", "\n").replace("\r", "\n")
                  for name in SOURCE_FIELDS}
    raw = json.dumps(normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


@lru_cache(maxsize=1)
def load_editorial():
    if not CONTENT_PATH.is_file():
        return {}
    payload = json.loads(CONTENT_PATH.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 2:
        return {}
    return {row["case_id"]: row for row in payload["cases"]}


def editorial_for(case_id, source, registry=None):
    row = (load_editorial() if registry is None else registry).get(str(case_id or "").upper())
    if not row or row["source_fingerprint"] != source_fingerprint(source_fields(source)):
        return None
    return {
        "status": "editorial_hypothesis",
        "label": "Hypothèses éditoriales — à vérifier lors de votre essai",
        "source_fingerprint": row["source_fingerprint"],
        "horizon_kind": row["horizon_kind"],
        "claims": row["claims"],
        "unknown_fields": [name for name, claim in row["claims"].items() if claim["text"] is None],
    }
