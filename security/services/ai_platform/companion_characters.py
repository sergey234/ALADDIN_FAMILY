# -*- coding: utf-8 -*-
"""Companion character IDs and speech defaults (HERO-3)."""

from __future__ import annotations

from typing import Dict, Tuple

VALID_CHARACTER_IDS: Tuple[str, ...] = ("unicorn", "aladdin", "genie")
CHARACTER_ID_PATTERN = "^(aladdin|unicorn|genie)$"
# UX-HERO-01 (2026-05-29): all age bands — PG content via policy, not hero lockout.
STANDARD_COMPANION_CHARACTERS: Tuple[str, ...] = VALID_CHARACTER_IDS

CHARACTER_DEFAULT_PRESET: Dict[str, str] = {
    "unicorn": "playful",
    "aladdin": "mentor",
    "genie": "witty",
}

HUMOR_DENSITY: Dict[str, str] = {
    "unicorn": "medium",
    "aladdin": "low",
    "genie": "high",
}


def humor_density_for(character_id: str) -> str:
    return HUMOR_DENSITY.get(character_id, "low")


def normalize_personality_preset(
    preset: str,
    character_id: str,
    age_band: str,
) -> str:
    """Child / unicorn: witty → playful (HERO-3-12)."""
    p = (preset or "friendly").strip()
    if p == "witty" and (age_band == "child" or character_id == "unicorn"):
        return "playful"
    return p


def default_preset_for_character(character_id: str, age_band: str = "parent") -> str:
    if age_band == "senior" and character_id == "aladdin":
        return "calm"
    return CHARACTER_DEFAULT_PRESET.get(character_id, "friendly")


def available_personality_presets(age_band: str) -> Tuple[str, ...]:
    """HERO-3-15: witty недоступен для child."""
    from security.services.ai_platform.companion_persona import PERSONALITY_PRESET_HINTS

    keys = tuple(PERSONALITY_PRESET_HINTS.keys())
    if age_band == "child":
        return tuple(k for k in keys if k != "witty")
    return keys
