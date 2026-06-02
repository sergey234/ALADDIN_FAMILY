# -*- coding: utf-8 -*-
"""Wellness canary cohort gate (p3-10)."""

from __future__ import annotations

import hashlib
import os
from typing import Any, Dict, Optional


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or not str(raw).strip():
        return default
    try:
        return max(0, min(100, int(str(raw).strip())))
    except ValueError:
        return default


def wellness_canary_percent() -> int:
    """0 = nobody (except bypass), 100 = all users when wellness enabled."""
    return _env_int("WELLNESS_CANARY_PERCENT", 100)


def wellness_canary_bypass_uids() -> set[str]:
    """Ops/smoke accounts always in cohort."""
    raw = os.getenv("WELLNESS_CANARY_BYPASS_UIDS", "")
    out = {x.strip() for x in raw.split(",") if x.strip()}
    out.update({"901701", "901702", "901703", "901704"})
    return out


def wellness_canary_bucket(user_id: str) -> int:
    """Stable 0..99 bucket for user_id."""
    key = (user_id or "0").strip()
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % 100


def user_in_wellness_canary(user_id: Optional[str]) -> bool:
    if not user_id:
        return True
    uid = str(user_id).strip()
    if uid in wellness_canary_bypass_uids():
        return True
    pct = wellness_canary_percent()
    if pct >= 100:
        return True
    if pct <= 0:
        return False
    return wellness_canary_bucket(uid) < pct


def build_canary_status(*, user_id: Optional[str] = None) -> Dict[str, Any]:
    from security.services.ai_platform.feature_flags import FEATURE_WELLNESS_ENABLED

    pct = wellness_canary_percent()
    bucket = wellness_canary_bucket(user_id) if user_id else None
    in_cohort = user_in_wellness_canary(user_id) if user_id else None
    return {
        "wellness_enabled": bool(FEATURE_WELLNESS_ENABLED),
        "canary_percent": pct,
        "canary_bucket": bucket,
        "in_canary": in_cohort,
        "bypass": bool(user_id and str(user_id) in wellness_canary_bypass_uids()),
    }
