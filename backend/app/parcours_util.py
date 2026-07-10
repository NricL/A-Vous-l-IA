"""
Parcours URL Generation & Case Hash Utility
"""

import hashlib
import os
from typing import Optional

def generate_case_hash(case_id: str, salt: Optional[str] = None) -> str:
    """
    Generate URL-safe deterministic hash from case ID + salt.
    
    Args:
        case_id: UC-XXXX identifier from Excel
        salt: AVOULIA_SALT environment variable (fixed in prod)
    
    Returns:
        URL-safe 16-char hex string
    
    Example:
        UC-0042 + salt="prod-xyz" → "vn38reuyw7kx92mn"
    """
    if salt is None:
        salt = os.getenv('AVOULIA_SALT', 'default-salt-dev')
    
    # Deterministic: SHA256(case_id + salt) → first 16 chars
    data = f"{case_id}|{salt}".encode('utf-8')
    hash_obj = hashlib.sha256(data)
    hash_hex = hash_obj.hexdigest()[:16]
    
    return hash_hex


def build_parcours_url(case_id: str, salt: Optional[str] = None) -> str:
    """
    Build complete parcours URL for a case.
    
    Args:
        case_id: UC-XXXX identifier
        salt: AVOULIA_SALT (defaults to env)
    
    Returns:
        Full URL: https://avoulia.azurewebsites.net/action/<hash>/
    """
    base_url = os.getenv('PARCOURS_BASE_URL', 'https://avoulia.azurewebsites.net')
    case_hash = generate_case_hash(case_id, salt)
    return f"{base_url}/action/{case_hash}/"


def build_parcours_info(case_id: str, salt: Optional[str] = None) -> dict:
    """
    Build dictionary with case_hash and parcours_url.
    
    Returns:
        {
            "case_hash": "vn38reuyw7kx92mn",
            "parcours_url": "https://avoulia.azurewebsites.net/action/vn38reuyw7kx92mn/"
        }
    """
    if salt is None:
        salt = os.getenv('AVOULIA_SALT')
    
    case_hash = generate_case_hash(case_id, salt)
    parcours_url = build_parcours_url(case_id, salt)
    
    return {
        "case_hash": case_hash,
        "parcours_url": parcours_url,
    }
