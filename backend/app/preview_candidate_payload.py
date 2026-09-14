"""Pinned, already-public v461 candidate assets; no ingestion or embedding at startup."""

import hashlib
from collections import Counter
from pathlib import Path

from app.preview_publicsnapshot import load_snapshot

CATALOGUE_REVISION = "3779a90386ff17d9f528cd3b4269f31387955fc11a73d49d9de1dcff754cb807"
PUBLIC_ASSETS = {
    "snapshot.json": "75f60bf9cf99ce3b956f2aec1137f134c57bed5a4c1124dd9f35a1c237f3dfc8",
    "embeddings.json": "70738638b6df105e453f961b3441371a6197127a2f8876d8e6856276c8876ee3",
    "embeddings.npy": "71ab5cfa92434e4cfa985bebbf439d3e4048d1e81c10793eac0cb15c22fb8006",
    "tokenizer/fb374d419588a4632f3f557e76b4b70aebbca790":
        "446a9538cb6c348e3516120d7c08b09f57c36495e2acfffe59a5bf8b0cfb1a2d",
}


def validate_candidate_payload(cache: Path):
    for name, expected in PUBLIC_ASSETS.items():
        path = cache / name
        if not path.is_file() or path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError("Missing or unapproved public candidate asset; no rebuild or fallback.")
    snapshot = load_snapshot(cache)
    records = snapshot["records"]
    if (snapshot["catalogue_revision"] != CATALOGUE_REVISION or len(records) != 1021
            or snapshot["mapping_count"] != 1025 or len(snapshot["excluded"]) != 4
            or snapshot["observed_versions"] != {"v4.6.1": 1021, "v4.5.3": 4}
            or snapshot["domain_counts"] != dict(Counter(row["domain"] for row in records))
            or any(row["source_fields"][key] is not None for row in records
                   for key in ("mode_execution", "declencheurs_typiques"))):
        raise ValueError("Candidate inventory must contain the approved 1021 PUBLIC_PAGES v461 records only.")
    return snapshot
