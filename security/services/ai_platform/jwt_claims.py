# -*- coding: utf-8 -*-
"""JWT claims for Companion Platform (Family + Adult)."""

from __future__ import annotations

from typing import Any, Dict, Optional

from .companion_characters import STANDARD_COMPANION_CHARACTERS

_ALL_CHARS = list(STANDARD_COMPANION_CHARACTERS)

from .config import AppId, DEFAULT_POLICY_BY_APP

DEFAULT_LIMITS_BY_LEVEL: Dict[str, Dict[str, int]] = {
    "free": {"max_ai_messages": 50, "voice_minutes_month": 30},
    "trial": {"max_ai_messages": 200, "voice_minutes_month": 60},
    "premium": {"max_ai_messages": 1000, "voice_minutes_month": 120},
}


def infer_age_band(token_data: dict) -> str:
    role = str(
        token_data.get("family_role")
        or token_data.get("role")
        or token_data.get("member_role")
        or ""
    ).strip().lower()
    if role in ("parent", "guardian", "mother", "father", "родитель"):
        return "parent"
    if role in ("elderly", "senior", "grandparent", "пожилой", "люди 60+"):
        return "senior"
    if role in ("teen", "teenager", "подросток"):
        return "teen"
    if role in ("child", "kid", "ребенок", "ребёнок"):
        return "child"

    explicit = token_data.get("age_band")
    if explicit in ("child", "teen", "parent", "senior", "adult_app"):
        return explicit
    if token_data.get("type") in ("device_auth", "device_refresh"):
        return "child"
    return "parent"


def default_parent_consent(age_band: str) -> Dict[str, Any]:
    if age_band == "child":
        return {
            "memory": False,
            "memory_enabled": False,
            "companion": True,
            "child_can_use_companion": True,
            "allowed_characters": list(_ALL_CHARS),
        }
    if age_band == "teen":
        return {
            "memory": False,
            "memory_enabled": False,
            "companion": True,
            "child_can_use_companion": True,
            "allowed_characters": list(_ALL_CHARS),
        }
    return {
        "memory": True,
        "memory_enabled": True,
        "companion": True,
        "child_can_use_companion": True,
        "allowed_characters": list(_ALL_CHARS),
    }


def subscription_level_from_token(token_data: dict) -> str:
    sub = token_data.get("subscription")
    if isinstance(sub, dict) and sub.get("level"):
        return str(sub["level"])
    return str(token_data.get("subscription_level") or "free")


def enrich_access_token_data(data: dict) -> dict:
    """Merge platform claims into access-token payload before signing."""
    out = dict(data)
    sub = out.get("sub") or str(out.get("user_id") or out.get("id") or "anonymous")
    out["sub"] = sub

    age_band = infer_age_band(out)
    out["age_band"] = age_band

    if age_band == "adult_app":
        out["app_id"] = AppId.ALADDIN_ADULT.value
        out["age_verified"] = bool(out.get("age_verified", True))
    else:
        out["app_id"] = out.get("app_id", AppId.ALADDIN_FAMILY.value)
        out["age_verified"] = bool(out.get("age_verified", False))

    try:
        app = AppId(out["app_id"])
    except ValueError:
        app = AppId.ALADDIN_FAMILY
        out["app_id"] = app.value

    if not out.get("content_policy"):
        out["content_policy"] = DEFAULT_POLICY_BY_APP[app].value

    if "parent_consent" not in out or not isinstance(out.get("parent_consent"), dict):
        out["parent_consent"] = default_parent_consent(age_band)

    level = subscription_level_from_token(out)
    limits = DEFAULT_LIMITS_BY_LEVEL.get(level, DEFAULT_LIMITS_BY_LEVEL["free"])
    existing_sub = out.get("subscription")
    if isinstance(existing_sub, dict) and existing_sub.get("limits"):
        limits = {**limits, **(existing_sub.get("limits") or {})}
    out["subscription"] = {"level": level, "limits": limits}
    out["subscription_level"] = level
    return out


def parse_user_from_payload(payload: dict) -> dict:
    """Normalized user dict for routers (extends get_current_user)."""
    subscription = payload.get("subscription") or {}
    if not isinstance(subscription, dict):
        subscription = {}
    limits = subscription.get("limits") or {}
    level = subscription.get("level") or payload.get("subscription_level") or "free"
    parent_consent = payload.get("parent_consent")
    if not isinstance(parent_consent, dict):
        parent_consent = default_parent_consent(payload.get("age_band", "parent"))

    user_id = payload.get("sub") or payload.get("user_id") or payload.get("id")

    return {
        "user_id": str(user_id) if user_id is not None else None,
        "email": payload.get("email"),
        "subscription_level": level,
        "limits": limits,
        "payload": payload,
        "app_id": payload.get("app_id", AppId.ALADDIN_FAMILY.value),
        "age_band": payload.get("age_band", "parent"),
        "age_verified": bool(payload.get("age_verified", False)),
        "parent_consent": parent_consent,
        "content_policy": payload.get("content_policy"),
    }


def merge_get_current_user(decoded: dict) -> dict:
    """Build get_current_user return shape from raw JWT payload."""
    enriched = enrich_access_token_data(decoded)
    return parse_user_from_payload(enriched)
