"""Run from the private session files directory, with --cache public-catalogue."""
import argparse
from pathlib import Path

from app.preview_publicsnapshot import build_snapshot

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache", type=Path, required=True)
    args = parser.parse_args()
    result = build_snapshot(args.cache)
    print({key: value for key, value in result.items() if key not in {"records", "excluded"}})
