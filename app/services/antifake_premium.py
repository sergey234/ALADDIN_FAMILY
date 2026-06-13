"""Premium gate for antifake API (af-2-08)."""
from __future__ import annotations

import os
from typing import Any, Dict

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


def user_has_antifake_access(user: Dict[str, Any], smoke_secret: str | None = None) -> bool:
    expected = os.environ.get("ANTIFAKE_INTERNAL_SMOKE_SECRET")
    if expected and smoke_secret and smoke_secret == expected:
        return True

    # TEMP QA: allow all authenticated users while testing Hub (set ANTIFAKE_ALLOW_FREE=0 before prod).
    if os.environ.get("ANTIFAKE_ALLOW_FREE", "1") == "1":
        return True

    sub = user.get("subscription") or {}
    if isinstance(sub, dict):
        level = str(sub.get("level") or "").lower()
        if level in PREMIUM_LEVELS:
            return True

    level = str(user.get("subscription_level") or "").lower()
    return level in PREMIUM_LEVELS
