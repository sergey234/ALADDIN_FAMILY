# -*- coding: utf-8 -*-
"""P2-06 — Family-scoped context snippet for companion prompts."""

from __future__ import annotations

from typing import Any, Dict, List, Optional


def build_family_context_hint(
    storage_key: str,
    ctx: Dict[str, Any],
    *,
    store: Any,
    max_memory_items: int = 3,
) -> str:
    """Redacted family hints: scope id, age band, recent memory summaries."""
    family_id = ctx.get("family_id") or ""
    age_band = ctx.get("age_band") or "parent"
    parts: List[str] = [
        f"[Family context: age_band={age_band}; scope={storage_key[:12]}…]"
    ]
    if family_id:
        parts.append(f"family_id={family_id[:8]}…")
    consent = ctx.get("parent_consent") or {}
    if consent.get("memory_enabled"):
        try:
            items = store.list_memory_items(storage_key, limit=max_memory_items)
            if items:
                snippets = [str(m.get("summary") or "")[:120] for m in items[:max_memory_items]]
                parts.append("recent_topics=" + " | ".join(snippets))
        except Exception:
            pass
    return " ".join(parts) + "\n"
