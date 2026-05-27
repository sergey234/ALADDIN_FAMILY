# -*- coding: utf-8 -*-
"""Usage limits for companion chat + voice (daily + monthly voice)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from .companion_store import get_companion_store


@dataclass(frozen=True)
class UsageCheckResult:
    allowed: bool
    reason: Optional[str]
    messages_today: int
    voice_seconds_today: int
    limits: Dict[str, Any]


def _daily_message_cap(subscription_level: str, limits: Dict[str, Any]) -> int:
    if limits.get("max_ai_messages") is not None:
        return int(limits["max_ai_messages"])
    if subscription_level == "free":
        return 50
    if subscription_level == "trial":
        return 200
    return 10_000


def _monthly_voice_seconds_cap(limits: Dict[str, Any]) -> int:
    minutes = limits.get("voice_minutes_month")
    if minutes is None:
        return 120 * 60
    return int(minutes) * 60


def check_message_allowed(
    user_id: str,
    subscription_level: str,
    limits: Optional[Dict[str, Any]] = None,
) -> UsageCheckResult:
    limits = limits or {}
    store = get_companion_store()
    usage = store.get_usage_today(user_id)
    cap = _daily_message_cap(subscription_level, limits)
    if usage["messages"] >= cap:
        return UsageCheckResult(
            allowed=False,
            reason="daily_message_limit",
            messages_today=usage["messages"],
            voice_seconds_today=usage["voice_seconds"],
            limits=limits,
        )
    return UsageCheckResult(
        allowed=True,
        reason=None,
        messages_today=usage["messages"],
        voice_seconds_today=usage["voice_seconds"],
        limits=limits,
    )


def record_message(user_id: str) -> Dict[str, int]:
    return get_companion_store().increment_messages(user_id, 1)


def check_voice_allowed(
    user_id: str,
    limits: Optional[Dict[str, Any]] = None,
    requested_seconds: int = 0,
) -> UsageCheckResult:
    limits = limits or {}
    store = get_companion_store()
    usage = store.get_usage_today(user_id)
    cap = _monthly_voice_seconds_cap(limits)
    # MVP: approximate monthly by calendar month sum not implemented — use daily soft cap
    daily_cap = max(60, cap // 30)
    projected = usage["voice_seconds"] + max(0, requested_seconds)
    if projected > daily_cap:
        return UsageCheckResult(
            allowed=False,
            reason="voice_daily_limit",
            messages_today=usage["messages"],
            voice_seconds_today=usage["voice_seconds"],
            limits=limits,
        )
    return UsageCheckResult(
        allowed=True,
        reason=None,
        messages_today=usage["messages"],
        voice_seconds_today=usage["voice_seconds"],
        limits=limits,
    )


def record_voice_seconds(user_id: str, seconds: int) -> Dict[str, int]:
    return get_companion_store().increment_voice_seconds(user_id, seconds)
