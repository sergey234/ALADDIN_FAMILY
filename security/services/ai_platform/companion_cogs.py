# -*- coding: utf-8 -*-
"""P2-08 — Companion COGS / unit economics snapshot (MVP estimates)."""

from __future__ import annotations

from typing import Any, Dict

# Rough USD per 1k tokens (MVP placeholders)
_COST_PER_1K_INPUT = 0.00015
_COST_PER_1K_OUTPUT = 0.0006
_ALERT_DAILY_USD = float(__import__("os").getenv("COMPANION_COGS_ALERT_USD", "2.5"))


def estimate_turn_cost_usd(
    *,
    input_chars: int,
    output_chars: int,
) -> float:
    inp_tok = max(1, input_chars // 4)
    out_tok = max(1, output_chars // 4)
    return (inp_tok / 1000.0) * _COST_PER_1K_INPUT + (out_tok / 1000.0) * _COST_PER_1K_OUTPUT


def record_turn_cogs(
    store: Any,
    user_id: str,
    *,
    input_chars: int,
    output_chars: int,
    chat_mode: str = "fast",
) -> Dict[str, Any]:
    cost = estimate_turn_cost_usd(input_chars=input_chars, output_chars=output_chars)
    if chat_mode == "think":
        cost *= 2.5
    elif chat_mode == "reasoning":
        cost *= 1.6
    return store.record_cogs(user_id, cost_usd=cost)


def build_cogs_dashboard(store: Any, user_id: str) -> Dict[str, Any]:
    snap = store.get_cogs_snapshot(user_id)
    daily = float(snap.get("daily_usd") or 0.0)
    return {
        "daily_usd": round(daily, 4),
        "month_usd": round(float(snap.get("month_usd") or 0.0), 4),
        "turns_today": int(snap.get("turns_today") or 0),
        "alert_threshold_usd": _ALERT_DAILY_USD,
        "alert_triggered": daily >= _ALERT_DAILY_USD,
    }
