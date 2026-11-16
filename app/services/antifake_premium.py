"""Premium gate for antifake API (af-2-08).

Policy A: active App Trial (subscriptions.trial_end_date > now) grants the same
access as Premium/Family, even when users.subscription_level stayed `free`.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

PREMIUM_LEVELS = frozenset(
    {
        "premium",
        "trial",
        "trial_premium",
        "family",
        "personal",
        "premium_3m",
        "premium_6m",
    }
)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def trial_end_is_active(trial_end: Any) -> bool:
    """True when trial_end is a future datetime (naive UTC or aware)."""
    if trial_end is None:
        return False
    try:
        end = trial_end
        if isinstance(end, str):
            raw = end.strip().replace("Z", "+00:00")
            end = datetime.fromisoformat(raw)
        if not isinstance(end, datetime):
            return False
        if end.tzinfo is not None:
            end = end.astimezone(timezone.utc).replace(tzinfo=None)
        return end > _utcnow()
    except Exception:
        return False


def effective_level_from_parts(
    user_level: Optional[str],
    sub_level: Optional[str],
    trial_end: Any,
) -> str:
    """
    Same semantics as family._effective_level_from_user_and_subscription:
    paid > active trial window > raw levels > free.
    """
    u = (user_level or "").strip().lower()
    s = (sub_level or "").strip().lower()
    paid = PREMIUM_LEVELS - {"trial", "trial_premium"}
    if u in paid:
        return u
    if s in paid:
        return s
    if trial_end_is_active(trial_end) and (u in ("", "free", "trial") or s in ("", "free", "trial")):
        return "trial"
    if s:
        return s
    if u:
        return u
    return "free"


def level_grants_antifake(level: Optional[str]) -> bool:
    return (level or "").strip().lower() in PREMIUM_LEVELS


def user_has_antifake_access(
    user: Dict[str, Any],
    smoke_secret: str | None = None,
    *,
    client: str | None = None,
) -> bool:
    expected = os.environ.get("ANTIFAKE_INTERNAL_SMOKE_SECRET")
    if expected and smoke_secret and smoke_secret == expected:
        return True

    # Website: Premium only (no free tier). ANTIFAKE_WEB_FREE=1 is QA-only.
    if (client or "").lower() == "web" and os.environ.get("ANTIFAKE_WEB_FREE", "0") == "1":
        return True

    # Production default: premium required. Set ANTIFAKE_ALLOW_FREE=1 only for local QA.
    if os.environ.get("ANTIFAKE_ALLOW_FREE", "0") == "1":
        return True

    sub = user.get("subscription") or {}
    trial_end = None
    sub_level = None
    if isinstance(sub, dict):
        sub_level = str(sub.get("level") or "").lower() or None
        trial_end = sub.get("trial_end") or sub.get("trial_end_date") or sub.get("trialEnd")
        if level_grants_antifake(sub_level):
            return True

    user_level = str(user.get("subscription_level") or "").lower() or None
    if level_grants_antifake(user_level):
        return True

    # JWT may carry trial_end without subscription_level=trial (free + active window).
    jwt_trial_end = user.get("trial_end") or user.get("trial_end_date") or trial_end
    if trial_end_is_active(jwt_trial_end):
        return True

    eff = effective_level_from_parts(user_level, sub_level, jwt_trial_end)
    return level_grants_antifake(eff)
