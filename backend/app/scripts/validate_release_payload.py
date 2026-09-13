"""Validate the private catalogue/mapping and staged pages without model calls."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re

from app.services.ingest import _load_xlsx


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def quarantine_static_exports(pages: Path, private_root: Path) -> int:
    count = 0
    for item in list(pages.rglob("*")):
        if not item.is_file():
            continue
        private_export = item.suffix.lower() in {".csv", ".xlsx", ".xlsm", ".json", ".md"}
        private_export = private_export or (item.suffix.lower() == ".txt" and item.name != "robots.txt")
        if not private_export:
            continue
        target = private_root / item.relative_to(pages)
        if target.exists():
            raise ValueError("Inherited private export destination already exists.")
        target.parent.mkdir(parents=True, exist_ok=True)
        item.rename(target)
        count += 1
    return count


def validate_payload(workbook: Path, mapping_path: Path, manifest_path: Path, pages: Path) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if sha256(workbook) != manifest["workbook_sha256"]:
        raise ValueError("Private source hash mismatch.")
    if sha256(mapping_path) != manifest["mapping_sha256"]:
        raise ValueError("Private mapping hash mismatch.")
    docs = _load_xlsx(str(workbook))
    identifiers = {d.metadata["use_case_id"] for d in docs}
    if len(docs) != manifest["case_count"] or len(identifiers) != len(docs):
        raise ValueError("Catalogue count or identity mismatch.")
    mapping = {}
    hashes = set()
    with mapping_path.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            identity, case_hash = row.get("case_id"), row.get("case_hash")
            if not identity or not case_hash or not re.fullmatch(r"[a-z0-9]{10,64}", case_hash):
                raise ValueError("Invalid mapping identity.")
            if identity.upper() in mapping or case_hash in hashes:
                raise ValueError("Duplicate mapping identity.")
            mapping[identity.upper()] = case_hash
            hashes.add(case_hash)
    if not {identity.upper() for identity in identifiers} <= mapping.keys():
        raise ValueError("Catalogue identity missing from mapping.")
    for group in ("pages", "historical_pages"):
        if any(not re.fullmatch(r"action-[a-z0-9]{10,64}\.html", name) for name in manifest[group]):
            raise ValueError("Unsafe page filename in manifest.")
    expected_current = {f"action-{mapping[i.upper()]}.html" for i in identifiers}
    if expected_current != set(manifest["pages"]):
        raise ValueError("Rendered-page identity set differs from catalogue.")
    expected_historical = {f"action-{h}.html" for h in hashes} - expected_current
    if expected_historical != set(manifest["historical_pages"]):
        raise ValueError("Historical-page set differs from retained mapping.")
    for group in ("pages", "historical_pages"):
        for filename, digest in manifest[group].items():
            candidate = pages / filename
            if not candidate.is_file() or sha256(candidate) != digest:
                raise ValueError(f"Page digest mismatch in {group}.")
    for item in pages.rglob("*"):
        if item.is_file() and item.suffix.lower() in {".csv", ".xlsx", ".xlsm"}:
            raise ValueError("Private source or mapping present in static directory.")
    return {"cases": len(docs), "current_pages": len(expected_current),
            "historical_pages_preserved": len(manifest["historical_pages"])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("workbook", "mapping", "manifest", "pages"):
        parser.add_argument(name, type=Path)
    parser.add_argument("--quarantine-inherited", action="store_true")
    args = parser.parse_args()
    moved = quarantine_static_exports(args.pages, args.manifest.parent / "inherited-static") if args.quarantine_inherited else 0
    result = validate_payload(args.workbook, args.mapping, args.manifest, args.pages)
    result["inherited_exports_moved_private"] = moved
    print(json.dumps(result))


if __name__ == "__main__":
    main()
