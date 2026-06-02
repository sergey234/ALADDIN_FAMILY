# -*- coding: utf-8 -*-
"""Pillar → Rive emotion + TTS voice hints (p3-09)."""

from __future__ import annotations

from typing import Any, Dict

PILLAR_RIVE_MAP: Dict[str, Dict[str, str]] = {
    "cognitive": {
        "rive_state": "think",
        "emotion": "focused",
        "tts_voice": "calm_neutral",
        "color_hex": "#7C4DFF",
    },
    "behavioral": {
        "rive_state": "step",
        "emotion": "encouraging",
        "tts_voice": "warm_upbeat",
        "color_hex": "#00BFA5",
    },
    "humanistic": {
        "rive_state": "presence",
        "emotion": "gentle",
        "tts_voice": "soft_slow",
        "color_hex": "#FF6F61",
    },
    "jung": {
        "rive_state": "dream",
        "emotion": "curious",
        "tts_voice": "whisper_reflect",
        "color_hex": "#5C6BC0",
    },
}


def pillar_rive_payload(pillar: str, *, locale: str = "ru") -> Dict[str, Any]:
    key = (pillar or "humanistic").lower()
    base = PILLAR_RIVE_MAP.get(key) or PILLAR_RIVE_MAP["humanistic"]
    return {
        "pillar": key,
        "rive_asset": f"wellness_{key}_hero.riv",
        **base,
        "locale": locale,
    }
