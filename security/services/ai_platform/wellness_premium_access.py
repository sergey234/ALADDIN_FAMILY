# -*- coding: utf-8 -*-
"""
p3-06 — Premium wellness paywall gate (subscription + ethics from p3-12).
"""

from __future__ import annotations

from typing import Any, Dict, Optional

PREMIUM_SUBSCRIPTION_LEVELS = frozenset({"personal", "family", "premium", "trial"})


def _user_subscription_level(user: dict) -> str:
    raw = (
        user.get("subscription_level")
        or (user.get("subscription") or {}).get("level")
        or "free"
    )
    return str(raw).strip().lower()


def wellness_subscription_premium(user: dict) -> bool:
    return _user_subscription_level(user) in PREMIUM_SUBSCRIPTION_LEVELS


def wellness_premium_features_gate(
    store: Any,
    user_id: str,
    user: dict,
    *,
    profile: Optional[Dict[str, Any]] = None,
    age_band: str = "teen",
) -> Dict[str, Any]:
    """Combined ethics (p3-12) + subscription gate for timeline / full assessments."""
    from security.services.ai_platform.wellness_crisis_monitor import wellness_premium_eligible

    ethics = wellness_premium_eligible(
        store, user_id, profile=profile, age_band=age_band
    )
    if not ethics.get("eligible"):
        return {
            "allowed": False,
            "reason": ethics.get("reason") or "wellness_premium_blocked",
            "message_key": _reason_to_key(str(ethics.get("reason") or "")),
            "ethics": ethics,
            "subscription_active": wellness_subscription_premium(user),
        }
    if not wellness_subscription_premium(user):
        return {
            "allowed": False,
            "reason": "wellness_premium_subscription_required",
            "message_key": "wellness_error_premium_subscription",
            "ethics": ethics,
            "subscription_active": False,
        }
    return {
        "allowed": True,
        "reason": None,
        "message_key": None,
        "ethics": ethics,
        "subscription_active": True,
    }


def _reason_to_key(reason: str) -> str:
    mapping = {
        "wellness_consent_required": "wellness_error_consent_required",
        "crisis_cooldown_48h": "wellness_error_crisis_cooldown",
        "wellness_premium_blocked": "wellness_error_premium_blocked",
        "wellness_premium_subscription_required": "wellness_error_premium_subscription",
    }
    return mapping.get(reason, "wellness_error_premium_blocked")


def require_premium_features(
    store: Any,
    user_id: str,
    user: dict,
    *,
    profile: Optional[Dict[str, Any]] = None,
    age_band: str = "teen",
    locale: str = "ru",
) -> None:
    from security.services.ai_platform.wellness_api_errors import raise_wellness_error

    gate = wellness_premium_features_gate(
        store, user_id, user, profile=profile, age_band=age_band
    )
    if not gate.get("allowed"):
        raise_wellness_error(str(gate.get("reason") or "wellness_premium_blocked"), locale=locale)
