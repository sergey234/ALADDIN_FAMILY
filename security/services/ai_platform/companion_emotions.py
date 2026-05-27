# -*- coding: utf-8 -*-
"""Companion hero emotions (P1-30) — mood/domain → avatar emotion."""

from __future__ import annotations

from typing import FrozenSet, Optional

# Sync with iOS `CompanionHeroEmotion` (P1-08 Rive later).
COMPANION_HERO_EMOTIONS: FrozenSet[str] = frozenset(
    {
        "idle",
        "happy",
        "listening",
        "speaking",
        "alert",
        "comfort",
        "celebrate",
        "thinking",
        "sad",
        "playful",
        "curious",
        "nostalgic",
        "excited",
    }
)


def emotion_for_companion(
    *,
    domain: str,
    mood: str,
    blocked: bool = False,
    fallback_intent: Optional[str] = None,
) -> str:
    """
    Map companion domain + mood to hero emotion (CX.4).
    Security factual intents from assistant may still pass fallback_intent.
    """
    if blocked:
        return "alert"

    if fallback_intent in ("threat_analysis", "report_incident", "incident_analyze"):
        return "alert"
    if domain == "safety":
        return "alert"

    mood_map = {
        "playful": "playful",
        "sad": "sad",
        "lonely": "comfort",
        "comfort_needed": "comfort",
        "joyful": "happy",
        "excited": "excited",
        "nostalgic": "nostalgic",
        "curious": "curious",
        "anxious": "comfort",
        "tired": "comfort",
        "neutral": "happy",
    }
    if mood in mood_map:
        emo = mood_map[mood]
        if mood == "joyful" and domain in ("games", "sport", "hobbies"):
            return "celebrate"
        return emo

    if domain == "safety":
        return "alert"
    if domain == "loneliness":
        return "comfort"
    return "happy"


def emotion_for_mood(message: str, *, blocked: bool = False) -> str:
    """Shortcut: classify mood from message via companion_intent_router."""
    from security.services.ai_platform.companion_intent_router import classify_companion_intent

    result = classify_companion_intent(message)
    return emotion_for_companion(
        domain=result.domain,
        mood=result.mood,
        blocked=blocked,
    )
