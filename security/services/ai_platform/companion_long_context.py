# -*- coding: utf-8 -*-
"""P3-04 — Long thread context compaction hint (MVP)."""

from __future__ import annotations

from typing import Any, List


def build_long_context_hint(
    store: Any,
    user_id: str,
    thread_id: str,
    *,
    threshold: int = 24,
    keep_recent: int = 8,
) -> str:
    """When thread is long, inject a short recap hint from older messages."""
    try:
        msgs = store.get_thread_messages(user_id, thread_id, limit=threshold + keep_recent)
    except Exception:
        return ""
    if len(msgs) <= threshold:
        return ""
    older = msgs[: max(0, len(msgs) - keep_recent)]
    if not older:
        return ""
    user_bits = [m["text"][:60] for m in older if m.get("role") == "user"][-5:]
    if not user_bits:
        return ""
    recap = " · ".join(user_bits)
    return f"[Long context recap: earlier you discussed: {recap}…]\n"
