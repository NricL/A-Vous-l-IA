"""Offline candidate checks; never instantiate Azure authentication or rebuild assets."""

import argparse
import json
import os
from pathlib import Path
from unittest.mock import patch

import tiktoken

from app.preview_candidate_payload import validate_candidate_payload
from app.preview_parcours import ParcoursRenderer
from app.preview_public_rag import PublicPagesRepository


class OfflineAzure:
    calls = {}
    tokens = {}

    def embed(self, _texts):
        raise RuntimeError("Network inference is forbidden during candidate validation.")

    def select(self, _messages, **_options):
        raise RuntimeError("Network inference is forbidden during candidate validation.")


def validate(cache: Path, parcours_root: Path):
    with patch("socket.socket.connect", side_effect=RuntimeError("Offline validation forbids network access.")):
        snapshot = validate_candidate_payload(cache)
        os.environ["TIKTOKEN_CACHE_DIR"] = str(cache / "tokenizer")
        tiktoken.get_encoding("o200k_base")
        repository = PublicPagesRepository(cache, azure=OfflineAzure())
        case = repository.get(repository.ids[0])
        renderer = ParcoursRenderer(
            str(parcours_root.resolve()), "https://nricl.github.io",
            app_url="https://nricl.github.io/A-Vous-l-IA/preview",
            allowed_origins={"https://nricl.github.io"}, cloud=True)
        transfer = {
            "case_id": case.case_id, "case_hash": case.case_hash, "source_hash": case.source_hash,
            "source_fields": case.source_fields, "source": repository.provenance,
            "source_url": case.source_url, "parcours_url": case.parcours_url,
            "catalogue_revision": repository.revision,
            "local_context": {"problem_original": "Exemple fictif de validation hors ligne."},
        }
        page = renderer.render(transfer)
        if 'href="https://nricl.github.io/A-Vous-l-IA/preview"' not in page:
            raise ValueError("The approved application backlink is missing.")
    return {"status": "ok", "source_mode": "PUBLIC_PAGES", "case_count": len(repository.ids),
            "catalogue_revision": repository.revision, "observed_versions": snapshot["observed_versions"],
            "azure_calls": 0}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--public-cache", type=Path, required=True)
    parser.add_argument("--parcours-root", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(validate(args.public_cache.resolve(), args.parcours_root.resolve()), ensure_ascii=False))
