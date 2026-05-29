# -*- coding: utf-8 -*-
"""P2-15 — Teen loneliness / bullying / rejection playbook hints."""

from __future__ import annotations

import re
from typing import Optional

_BULLYING = re.compile(
    r"(буллинг|булл[яи]|обзыва|травл|издева|дразн|высмеива|травят|bullying|mocked)",
    re.I,
)
_REJECTION = re.compile(
    r"(меня не зовут|никто не зовёт|не берут в компан|отверг|не нужен|не нужна|rejected|left out)",
    re.I,
)
_NO_FRIENDS = re.compile(
    r"(нет друзей|без друзей|ни одного друга|no friends|friendless)",
    re.I,
)


def teen_playbook_hint(age_band: str, domain: str, message: str) -> Optional[str]:
    if (age_band or "").lower() != "teen":
        return None
    if domain not in ("loneliness", "feelings", "friends", "relationships"):
        return None
    text = message or ""
    if _BULLYING.search(text):
        return (
            "[Teen playbook: bullying — сочувствие, PG-13, без диагнозов. "
            "Предложи рассказать взрослому, которому доверяешь. "
            "Не обещай, что герой заменит людей.]\n"
        )
    if _REJECTION.search(text):
        return (
            "[Teen playbook: rejection — нормализуй чувства, мягкая поддержка, "
            "одна идея маленького шага (клуб, сообщение знакомому).]\n"
        )
    if _NO_FRIENDS.search(text) or domain == "loneliness":
        return (
            "[Teen playbook: loneliness — эмпатия, без стыда. "
            "Можно мягко предложить написать близкому человеку. PG-13.]\n"
        )
    return None
