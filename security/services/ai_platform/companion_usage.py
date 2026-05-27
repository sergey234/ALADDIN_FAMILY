# -*- coding: utf-8 -*-
"""P1-11 — Companion usage snapshot for soft-cap UI warnings."""

from __future__ import annotations

from typing import Any, Dict, Optional

from .companion_store import get_companion_store
from .usage_meters import _daily_message_cap, _monthly_voice_seconds_cap


def build_usage_snapshot(
    user_id: str,
    subscription_level: str,
    limits: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    limits = limits or {}
    store = get_companion_store()
    usage = store.get_usage_today(user_id)
    msg_cap = _daily_message_cap(subscription_level, limits)
    messages = int(usage.get("messages") or 0)
    voice_sec = int(usage.get("voice_seconds") or 0)
    voice_daily_cap = max(60, _monthly_voice_seconds_cap(limits) // 30)

    msg_pct = min(100, int(messages * 100 / max(1, msg_cap)))
    voice_pct = min(100, int(voice_sec * 100 / max(1, voice_daily_cap)))
    warn_at = 80

    return {
        "messages_today": messages,
        "messages_daily_cap": msg_cap,
        "messages_usage_percent": msg_pct,
        "voice_seconds_today": voice_sec,
        "voice_daily_cap_seconds": voice_daily_cap,
        "voice_usage_percent": voice_pct,
        "warn_threshold_percent": warn_at,
        "should_warn_messages": msg_pct >= warn_at and messages < msg_cap,
        "should_warn_voice": voice_pct >= warn_at and voice_sec < voice_daily_cap,
        "message_limit_reached": messages >= msg_cap,
        "voice_limit_reached": voice_sec >= voice_daily_cap,
    }
