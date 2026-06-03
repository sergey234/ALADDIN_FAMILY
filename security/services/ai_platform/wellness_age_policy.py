# -*- coding: utf-8 -*-
"""Age gating for wellness features (p1-04, p1-06)."""

from __future__ import annotations

from typing import Any, Dict, Optional


def normalize_age_band(age_band: Optional[str]) -> str:
    band = (age_band or "teen").strip().lower()
    if band not in ("child", "teen", "parent", "senior", "adult_app"):
        return "teen"
    return band


def _role_from_user(user: dict) -> str:
    payload = user.get("payload") if isinstance(user.get("payload"), dict) else {}
    for key in ("family_role", "role", "member_role", "user_role"):
        raw = user.get(key) or payload.get(key)
        if raw:
            return str(raw).strip().lower()
    return ""


def _token_type(user: dict) -> str:
    raw = user.get("type")
    if raw:
        return str(raw).strip().lower()
    payload = user.get("payload") if isinstance(user.get("payload"), dict) else {}
    return str(payload.get("type") or "").strip().lower()


def _is_device_registration_user(user: dict) -> bool:
    """Device JWTs lose type=device_auth at sign (create_access_token → type=access)."""
    token_type = _token_type(user)
    if token_type in ("device_auth", "device_refresh"):
        return True
    payload = user.get("payload") if isinstance(user.get("payload"), dict) else {}
    return bool(payload.get("device_id") or user.get("device_id"))


def resolve_wellness_age_band(user: dict) -> str:
    """Wellness pillars: parent/senior accounts must not get child band from stale JWT."""
    explicit = normalize_age_band(user.get("age_band"))
    role = _role_from_user(user)
    token_type = _token_type(user)
    is_device = _is_device_registration_user(user)
    if role in ("parent", "guardian", "mother", "father", "родитель"):
        return "parent"
    if role in ("elderly", "senior", "grandparent", "пожилой", "люди 60+"):
        return "senior"
    if role in ("child", "kid", "ребенок", "ребёнок"):
        return "child"
    if role in ("teen", "teenager", "подросток"):
        return "teen"
    if explicit in ("parent", "senior", "adult_app"):
        return explicit
    if explicit == "child" and not is_device:
        return "parent"
    if is_device and explicit in ("teen", "child"):
        return "child"
    return explicit


def can_use_phq_lite(age_band: str) -> bool:
    return normalize_age_band(age_band) in ("teen", "parent", "senior", "adult_app")


def can_use_full_assessments(age_band: str) -> bool:
    return normalize_age_band(age_band) in ("teen", "parent", "senior", "adult_app")


def can_use_mbi_lite(age_band: str) -> bool:
    """Burnout MBI-lite — parent/senior only (p2-06)."""
    return normalize_age_band(age_band) in ("parent", "senior", "adult_app")


def wellness_consent_from_payload(consent: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "wellness_accepted": bool(consent.get("wellness_accepted")),
        "wellness_accepted_at": consent.get("wellness_accepted_at"),
        "wellness_disclaimer_version": consent.get("wellness_disclaimer_version") or "v1",
        "psychological_support_enabled": bool(
            consent.get("psychological_support_enabled")
            or consent.get("psychological_support_agent")
        ),
    }


def has_wellness_consent(consent: Dict[str, Any], *, age_band: str) -> bool:
    band = normalize_age_band(age_band)
    w = wellness_consent_from_payload(consent)
    if not w["wellness_accepted"]:
        return False
    if band == "child":
        return w["psychological_support_enabled"]
    return True
