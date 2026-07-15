"""
Parcours URL generation with optional Blob mapping.
"""

import csv
import hashlib
import io
import logging
import os
import time
from typing import Optional

logger = logging.getLogger(__name__)

_MAPPING_CACHE: dict[str, str] = {}
_MAPPING_CACHE_LOADED_AT: float = 0.0


def _mapping_cache_ttl_seconds() -> int:
    raw = os.getenv("PARCOURS_MAPPING_CACHE_TTL_SECONDS", "300").strip()
    try:
        ttl = int(raw)
    except ValueError:
        ttl = 300
    return ttl if ttl >= 0 else 300


def _mapping_cache_is_fresh() -> bool:
    if not _MAPPING_CACHE_LOADED_AT:
        return False
    ttl = _mapping_cache_ttl_seconds()
    if ttl == 0:
        return False
    return (time.time() - _MAPPING_CACHE_LOADED_AT) <= ttl


def _normalize_case_id(case_id: str) -> str:
    return (case_id or "").strip().upper()


def generate_case_hash(case_id: str, salt: Optional[str] = None) -> str:
    """Generate deterministic hash from case id + salt."""
    if salt is None:
        salt = os.getenv("AVOULIA_SALT", "default-salt-dev")
    data = f"{_normalize_case_id(case_id)}|{salt}".encode("utf-8")
    return hashlib.sha256(data).hexdigest()[:16]


def _load_mapping_from_local_csv() -> dict[str, str]:
    csv_path = (os.getenv("PARCOURS_MAPPING_LOCAL_PATH") or "").strip()
    if not csv_path or not os.path.exists(csv_path):
        return {}
    mapping: dict[str, str] = {}
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            case_id = _normalize_case_id(str(row.get("case_id") or ""))
            case_hash = str(row.get("case_hash") or "").strip().lower()
            if case_id and case_hash:
                mapping[case_id] = case_hash
    logger.info("Loaded parcours mapping from local csv (%s rows)", len(mapping))
    return mapping


def _load_mapping_from_blob() -> dict[str, str]:
    account_name = (os.getenv("STORAGE_ACCOUNT_NAME") or "").strip()
    account_key = (os.getenv("STORAGE_ACCOUNT_KEY") or "").strip()
    container_name = (os.getenv("PARCOURS_MAPPING_CONTAINER") or "parcours-mappings").strip()
    blob_name = (os.getenv("PARCOURS_MAPPING_BLOB") or "mapping_uc_hash.csv").strip()

    if not account_name or not account_key:
        return {}

    try:
        from azure.storage.blob import BlobServiceClient
    except ImportError:
        logger.warning("azure-storage-blob not installed; Blob mapping disabled")
        return {}

    account_url = f"https://{account_name}.blob.core.windows.net"
    service = BlobServiceClient(account_url=account_url, credential=account_key)
    blob_client = service.get_blob_client(container=container_name, blob=blob_name)
    payload = blob_client.download_blob().readall().decode("utf-8-sig")

    mapping: dict[str, str] = {}
    reader = csv.DictReader(io.StringIO(payload))
    for row in reader:
        case_id = _normalize_case_id(str(row.get("case_id") or ""))
        case_hash = str(row.get("case_hash") or "").strip().lower()
        if case_id and case_hash:
            mapping[case_id] = case_hash

    logger.info(
        "Loaded parcours mapping from blob (%s/%s, %s rows)",
        container_name,
        blob_name,
        len(mapping),
    )
    return mapping


def _load_mapping() -> dict[str, str]:
    mapping = _load_mapping_from_local_csv()
    if mapping:
        return mapping
    return _load_mapping_from_blob()


def _get_cached_mapping() -> dict[str, str]:
    global _MAPPING_CACHE
    global _MAPPING_CACHE_LOADED_AT
    if _mapping_cache_is_fresh():
        return _MAPPING_CACHE
    _MAPPING_CACHE = _load_mapping()
    _MAPPING_CACHE_LOADED_AT = time.time()
    return _MAPPING_CACHE


def _resolve_case_hash(case_id: str, salt: Optional[str] = None) -> str:
    normalized = _normalize_case_id(case_id)
    mapping = _get_cached_mapping()
    mapped_hash = mapping.get(normalized)
    if mapped_hash:
        return mapped_hash
    return generate_case_hash(normalized, salt)


def build_parcours_url(case_id: str, salt: Optional[str] = None) -> str:
    """Build complete parcours URL for a case."""
    base_url = os.getenv("PARCOURS_BASE_URL", "https://happy-desert-0f415f20f.7.azurestaticapps.net").rstrip("/")
    case_hash = _resolve_case_hash(case_id, salt)
    return f"{base_url}/action/{case_hash}/"


def build_parcours_info(case_id: str, salt: Optional[str] = None) -> dict:
    """Build dictionary with case_hash and parcours_url."""
    case_hash = _resolve_case_hash(case_id, salt)
    base_url = os.getenv("PARCOURS_BASE_URL", "https://happy-desert-0f415f20f.7.azurestaticapps.net").rstrip("/")
    parcours_url = f"{base_url}/action/{case_hash}/"
    return {"case_hash": case_hash, "parcours_url": parcours_url}
