# -*- coding: utf-8 -*-
"""A/B copy for Hub pillar cards (p2-38)."""

from __future__ import annotations

import hashlib
from typing import Any, Dict, List

_PILLARS = ("cognitive", "behavioral", "humanistic", "jung")

# Variant B uses *_b suffix keys in LocalizationManager.
_VARIANT_B_KEYS: Dict[str, Dict[str, str]] = {
    "cognitive": {
        "title_key": "wellness_pillar_cognitive_title_b",
        "subtitle_key": "wellness_pillar_cognitive_subtitle_b",
    },
    "behavioral": {
        "title_key": "wellness_pillar_behavioral_title_b",
        "subtitle_key": "wellness_pillar_behavioral_subtitle_b",
    },
    "humanistic": {
        "title_key": "wellness_pillar_humanistic_title_b",
        "subtitle_key": "wellness_pillar_humanistic_subtitle_b",
    },
    "jung": {
        "title_key": "wellness_pillar_jung_title_b",
        "subtitle_key": "wellness_pillar_jung_subtitle_b",
    },
}


def hub_ab_variant(user_id: str) -> str:
    digest = hashlib.sha256(f"wellness_hub_ab:{user_id}".encode()).hexdigest()
    return "b" if int(digest[:8], 16) % 2 == 0 else "control"


def build_hub_copy(
    user_id: str,
    *,
    pillars: List[str],
    locale: str = "ru",
) -> Dict[str, Any]:
    variant = hub_ab_variant(user_id)
    cards: List[Dict[str, str]] = []
    for pillar in pillars:
        if pillar not in _PILLARS:
            continue
        if variant == "b":
            keys = _VARIANT_B_KEYS[pillar]
        else:
            keys = {
                "title_key": f"wellness_pillar_{pillar}_title",
                "subtitle_key": f"wellness_pillar_{pillar}_subtitle",
            }
        cards.append({"pillar": pillar, **keys})
    return {
        "variant": variant,
        "locale": (locale or "ru").lower()[:2],
        "pillars": cards,
    }
