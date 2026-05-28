"""
Реестр APNs device tokens, привязанных к анонимному subject из JWT (family_id / device_id / sub).
Память процесса; в продакшене можно заменить на Redis/БД без смены интерфейса.
"""

from __future__ import annotations

import threading
from typing import Any, Dict, List, Optional

_lock = threading.Lock()
# subject_id -> [{ "token": hex str, "platform": str }]
_by_subject: Dict[str, List[Dict[str, str]]] = {}


def subject_id_from_jwt_payload(payload: Optional[Dict[str, Any]]) -> Optional[str]:
    if not payload:
        return None
    for key in (
        "family_id",
        "familyId",
        "device_id",
        "deviceId",
        "sub",
        "user_id",
        "id",
    ):
        val = payload.get(key)
        if val is not None and str(val).strip():
            return str(val).strip()
    return None


def register_push_token(subject_id: str, token_hex: str, platform: str = "ios") -> None:
    if not subject_id or not token_hex:
        return
    token_hex = token_hex.strip().lower()
    with _lock:
        lst = _by_subject.setdefault(subject_id, [])
        for entry in lst:
            if entry.get("token") == token_hex:
                entry["platform"] = platform or entry.get("platform", "ios")
                return
        lst.append({"token": token_hex, "platform": platform or "ios"})


def get_tokens_for_subject(subject_id: str) -> List[Dict[str, str]]:
    if not subject_id:
        return []
    with _lock:
        return [dict(x) for x in _by_subject.get(subject_id, [])]


def unregister_push_token(subject_id: str, token_hex: str) -> None:
    token_hex = token_hex.strip().lower()
    with _lock:
        lst = _by_subject.get(subject_id)
        if not lst:
            return
        _by_subject[subject_id] = [e for e in lst if e.get("token") != token_hex]
        if not _by_subject[subject_id]:
            del _by_subject[subject_id]
