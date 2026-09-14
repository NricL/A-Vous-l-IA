"""Embed only the validated public snapshot into the existing Azure resource."""
import argparse
from pathlib import Path
from app.preview_public_rag import build_embeddings

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache", type=Path, required=True)
    args = parser.parse_args()
    result = build_embeddings(args.cache)
    print({key: value for key, value in result.items() if key != "case_ids"})
