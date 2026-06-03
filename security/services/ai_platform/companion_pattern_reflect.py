# -*- coding: utf-8
"""Pattern reflection — soft theme detect (hero-x-23, hero-x-24)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

_THEME_PATTERNS: Tuple[Tuple[str, re.Pattern[str]], ...] = (
    ("exam_stress", re.compile(r"экзамен|оценк|ЕГЭ|контрольн|домашк", re.I)),
    ("loneliness", re.compile(r"одинок|некому|никто не", re.I)),
    ("family_conflict", re.compile(r"мам|пап|родител|ругаем|крич", re.I)),
    ("self_doubt", re.compile(r"не получ|я туп|не справ|бесполез", re.I)),
    ("sleep_worry", re.compile(r"не сп|бессон|ночью|устал", re.I)),
    ("friend_drama", re.compile(r"друг|подруг|игнор|булл|насмеш", re.I)),
)

_MAX_REFLECT_EVERY_TURNS = 10
_MIN_THEME_HITS = 2


@dataclass(frozen=True)
class PatternReflectResult:
    hint: str
    theme: str
    applied: bool


def _themes_in_text(text: str) -> List[str]:
    found: List[str] = []
    for theme_id, pat in _THEME_PATTERNS:
        if pat.search(text or ""):
            found.append(theme_id)
    return found


def detect_recurring_theme(user_messages: Sequence[str]) -> Optional[str]:
    """If same theme appears in ≥2 of last 3 user turns, return theme id."""
    if len(user_messages) < 2:
        return None
    recent = list(user_messages)[-3:]
    counts: dict = {}
    for msg in recent:
        for theme in _themes_in_text(msg):
            counts[theme] = counts.get(theme, 0) + 1
    for theme, count in sorted(counts.items(), key=lambda x: -x[1]):
        if count >= _MIN_THEME_HITS:
            return theme
    return None


def build_pattern_reflect_hint(
    user_messages: Sequence[str],
    *,
    turn_count: int,
    last_reflect_turn: int = -999,
    locale: str = "ru",
) -> PatternReflectResult:
    """
    hero-x-24: max 1 reflection hint per 10 turns; no «ты третий раз» wording.
    """
    if turn_count - last_reflect_turn < _MAX_REFLECT_EVERY_TURNS:
        return PatternReflectResult(hint="", theme="", applied=False)

    theme = detect_recurring_theme(user_messages)
    if not theme:
        return PatternReflectResult(hint="", theme="", applied=False)

    loc = (locale or "ru").lower()[:2]
    if loc == "en":
        soft = (
            f"[PATTERN reflect internal] theme={theme}. "
            "If natural, one soft line: «sounds like this matters a lot to you» — "
            "never count turns or say «you mentioned X again»."
        )
    else:
        soft = (
            f"[PATTERN reflect internal] theme={theme}. "
            "Если уместно — одна мягкая фраза: «похоже, это правда важно для тебя» — "
            "никогда не считай повторы и не говори «ты уже третий раз»."
        )
    return PatternReflectResult(
        hint=soft + "\n",
        theme=theme,
        applied=True,
    )
