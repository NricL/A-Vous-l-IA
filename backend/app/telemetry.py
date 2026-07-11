"""
Anonymous backend telemetry for chat funnel.
"""

import hashlib
import json
import logging
import os
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger("app.telemetry")


def _telemetry_salt() -> str:
    return os.getenv("AVOULIA_SALT", "default-salt-dev")


def hash_value(value: str) -> str:
    payload = f"{(value or '').strip()}|{_telemetry_salt()}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def _session_fingerprint(session_id: str | None) -> str | None:
    if not session_id:
        return None
    cleaned = str(session_id).strip()
    if not cleaned:
        return None
    return hash_value(cleaned)


def track_event(event_name: str, properties: dict[str, Any] | None = None, measurements: dict[str, float] | None = None) -> None:
    payload = {
        "name": event_name,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "properties": properties or {},
        "measurements": measurements or {},
    }
    logger.info("telemetry_event=%s", json.dumps(payload, ensure_ascii=False))


def track_backend_chat_event(
    *,
    event_name: str,
    session_id: str | None,
    use_rag: bool,
    suggested_cases_count: int,
    has_pending_action: bool,
    has_error: bool,
) -> None:
    track_event(
        event_name=event_name,
        properties={
            "session_fingerprint": _session_fingerprint(session_id),
            "use_rag": str(use_rag).lower(),
            "has_pending_action": str(has_pending_action).lower(),
            "has_error": str(has_error).lower(),
        },
        measurements={
            "suggested_cases_count": float(suggested_cases_count),
        },
    )

