# -*- coding: utf-8 -*-
"""Wellness product events (p2-27) — no PII / no chat text."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

WELLNESS_EVENT_CHECKIN = "wellness_checkin"
WELLNESS_EVENT_PILLAR_SELECT = "wellness_pillar_select"
WELLNESS_EVENT_EXERCISE_START = "wellness_exercise_start"
WELLNESS_EVENT_EXERCISE_DONE = "wellness_exercise_done"
WELLNESS_EVENT_ASSESSMENT = "wellness_assessment"
WELLNESS_EVENT_ALERT = "wellness_alert"

ALLOWED_WELLNESS_EVENTS = frozenset(
    {
        WELLNESS_EVENT_CHECKIN,
        WELLNESS_EVENT_PILLAR_SELECT,
        WELLNESS_EVENT_EXERCISE_START,
        WELLNESS_EVENT_EXERCISE_DONE,
        WELLNESS_EVENT_ASSESSMENT,
        WELLNESS_EVENT_ALERT,
    }
)


def record_wellness_event(
    *,
    user_id: str,
    event: str,
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    if event not in ALLOWED_WELLNESS_EVENTS:
        logger.warning("wellness analytics: unknown event %s", event)
        return
    safe: Dict[str, Any] = {}
    if extra:
        for key in (
            "pillar",
            "exercise_id",
            "assessment_type",
            "score_band",
            "severity",
            "age_band",
            "alert_type",
        ):
            if key in extra and extra[key] is not None:
                safe[key] = extra[key]
    try:
        from security.services.ai_platform.companion_analytics import (
            record_companion_product_event,
        )

        record_companion_product_event(
            user_id=user_id,
            event="companion_message",
            extra={"age_band": safe.get("age_band"), "emotion": event, **safe},
        )
    except Exception as exc:
        logger.warning("wellness analytics failed: %s", exc)
