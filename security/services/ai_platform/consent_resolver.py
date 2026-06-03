# -*- coding: utf-8 -*-
"""Normalize and resolve parent companion consent (user + family scope)."""

from __future__ import annotations

from typing import Any, Dict, Optional

from .companion_characters import STANDARD_COMPANION_CHARACTERS

_DEFAULT_CHARS = list(STANDARD_COMPANION_CHARACTERS)

from .companion_store import CompanionStore, get_companion_store


def normalize_parent_consent(raw: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Map JWT legacy keys (memory/companion) to API keys."""
    if not raw:
        return {
            "memory_enabled": False,
            "child_can_use_companion": True,
            "allowed_characters": list(_DEFAULT_CHARS),
            "vedic_wisdom_enabled": True,
        }
    out = dict(raw)
    if "memory_enabled" not in out:
        if "memory" in out:
            out["memory_enabled"] = bool(out.get("memory"))
        else:
            out["memory_enabled"] = False
    if "child_can_use_companion" not in out:
        companion = out.get("companion", True)
        out["child_can_use_companion"] = companion is not False
    chars = out.get("allowed_characters")
    if not isinstance(chars, list) or not chars:
        out["allowed_characters"] = list(_DEFAULT_CHARS)
    if "vedic_wisdom_enabled" not in out:
        out["vedic_wisdom_enabled"] = True
    else:
        out["vedic_wisdom_enabled"] = bool(out.get("vedic_wisdom_enabled"))
    return out


def family_consent_key(family_id: str) -> str:
    return f"family:{family_id.strip()}"


def memory_storage_key(user_id: str, family_id: Optional[str] = None) -> str:
    """Scope for companion memory rows (family overrides per-device user)."""
    fid = (family_id or "").strip()
    if fid:
        return family_consent_key(fid)
    return f"user:{user_id}"


def resolve_parent_consent(
    user_id: str,
    jwt_consent: Optional[Dict[str, Any]] = None,
    family_id: Optional[str] = None,
    store: Optional[CompanionStore] = None,
) -> Dict[str, Any]:
    """DB/family consent overrides JWT defaults."""
    st = store or get_companion_store()
    stored: Dict[str, Any] = {}
    fid = (family_id or "").strip()
    if fid:
        stored = st.get_consent(family_consent_key(fid)) or {}
    if not stored:
        stored = st.get_consent(user_id) or {}
    base = normalize_parent_consent(jwt_consent)
    merged = {**base, **normalize_parent_consent(stored)}
    return merged
