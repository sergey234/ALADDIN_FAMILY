# -*- coding: utf-8 -*-
"""Age gating for wellness features (p1-04, p1-06)."""

from __future__ import annotations

from typing import Any, Dict, Optional


def normalize_age_band(age_band: Optional[str]) -> str:
    band = (age_band or "teen").strip().lower()
    if band not in ("child", "teen", "parent", "senior", "adult_app"):
        return "teen"
    return band


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
