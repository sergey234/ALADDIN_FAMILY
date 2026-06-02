# -*- coding: utf-8 -*-
"""Reflective sub-modes inside Jung pillar (p2-12)."""

from __future__ import annotations

import re
from enum import Enum
from typing import Dict, List, Optional

from security.services.ai_platform.wellness_i18n_loader import list_reflective_modes_from_i18n


class ReflectiveMode(str, Enum):
    PRESENCE = "presence"
    DEEP_EXPLORE = "deep_explore"
    STRUCTURED_VIEW = "structured_view"
    BLIND_SPOTS = "blind_spots"
    SINGLE_QUESTION = "single_question"


_MODE_PATTERNS: Dict[ReflectiveMode, List[str]] = {
    ReflectiveMode.PRESENCE: [
        r"побудь\s+рядом",
        r"просто\s+рядом",
        r"stay\s+with\s+me",
        r"just\s+be\s+here",
    ],
    ReflectiveMode.DEEP_EXPLORE: [
        r"разбери\s+глубоко",
        r"глубоко\s+разобрать",
        r"deep\s+explore",
        r"go\s+deeper",
    ],
    ReflectiveMode.STRUCTURED_VIEW: [
        r"со\s+стороны",
        r"взгляд\s+со\s+стороны",
        r"structured\s+view",
        r"from\s+the\s+outside",
    ],
    ReflectiveMode.BLIND_SPOTS: [
        r"слеп\w*\s+зон",
        r"чего\s+не\s+замечаю",
        r"blind\s+spot",
    ],
    ReflectiveMode.SINGLE_QUESTION: [
        r"только\s+вопрос",
        r"один\s+вопрос",
        r"single\s+question",
        r"just\s+one\s+question",
    ],
}


def list_reflective_modes(*, locale: str = "ru") -> List[Dict[str, str]]:
    modes = list_reflective_modes_from_i18n(locale=locale)
    if modes:
        return modes
    loc = (locale or "ru").lower()[:2]
    if loc == "en":
        return [
            {"id": "presence", "label": "Stay with me", "hint": "Switches to humanistic pillar"},
            {"id": "deep_explore", "label": "Explore deeply", "hint": "Jung + reflective"},
            {"id": "structured_view", "label": "Outside view", "hint": "Facts vs interpretations"},
            {"id": "blind_spots", "label": "Blind spots", "hint": "Gentle patterns"},
            {"id": "single_question", "label": "One question only", "hint": "No lecture"},
        ]
    return [
        {"id": "presence", "label": "Побудь рядом", "hint": "Переключит на столп «Принять себя»"},
        {"id": "deep_explore", "label": "Разбери глубоко", "hint": "Jung + reflective"},
        {"id": "structured_view", "label": "Взгляд со стороны", "hint": "Факты и интерпретации"},
        {"id": "blind_spots", "label": "Слепые зоны", "hint": "Мягко про паттерны"},
        {"id": "single_question", "label": "Только вопрос", "hint": "Без нравоучений"},
    ]


def resolve_reflective_mode(message: str) -> Optional[str]:
    text = (message or "").strip().lower()
    if not text:
        return None
    for mode, patterns in _MODE_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, text, re.I):
                return mode.value
    return None
