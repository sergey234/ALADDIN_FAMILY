# -*- coding: utf-8 -*-
"""P1-10 — Companion product metrics N1–N6 (no raw child PII)."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Master plan §10 — event names (ui_context in ai_chat_analytics)
COMPANION_EVENT_OPEN = "companion_open"
COMPANION_EVENT_MESSAGE = "companion_message"
COMPANION_EVENT_VOICE_START = "voice_start"
COMPANION_EVENT_VOICE_END = "voice_end"
COMPANION_EVENT_TRUST_LEVEL_UP = "trust_level_up"
COMPANION_EVENT_POLICY_BLOCKED = "policy_blocked"

ALLOWED_EVENTS = frozenset(
    {
        COMPANION_EVENT_OPEN,
        COMPANION_EVENT_MESSAGE,
        COMPANION_EVENT_VOICE_START,
        COMPANION_EVENT_VOICE_END,
        COMPANION_EVENT_TRUST_LEVEL_UP,
        COMPANION_EVENT_POLICY_BLOCKED,
    }
)


def record_companion_product_event(
    *,
    user_id: str,
    event: str,
    character_id: Optional[str] = None,
    session_id: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    """Hash-only row via ai_history_store; `extra` must not contain message text."""
    if event not in ALLOWED_EVENTS:
        logger.warning("Companion analytics: unknown event %s", event)
        return
    meta = {"event": event}
    if character_id:
        meta["character_id"] = character_id
    if extra:
        for key in ("age_band", "emotion", "voice_seconds", "trust_level", "reason"):
            if key in extra and extra[key] is not None:
                meta[key] = extra[key]
    redacted = f"companion_metric:{event}:{character_id or ''}:{session_id or ''}"
    try:
        from security.services.ai_history_store import record_analytics_event

        record_analytics_event(
            user_id=user_id,
            question_redacted=redacted,
            ui_context=event,
            session_id=session_id,
            resolved_by="companion_metrics",
            sfm_aggregates=meta,
        )
    except Exception as exc:
        logger.warning("Companion product analytics failed: %s", exc)
