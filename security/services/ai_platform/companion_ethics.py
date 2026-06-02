# -*- coding: utf-8 -*-
"""P1-25 — Companion ethics L1/L2/L3 (CX.2)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

ETHICS_L1 = "L1"
ETHICS_L2 = "L2"
ETHICS_L3 = "L3"


@dataclass(frozen=True)
class CompanionEthicsResult:
    level: str
    crisis: bool
    social_bridge_hint: bool
    response_prefix: str = ""


_L3_PATTERNS = re.compile(
    r"самоуб|покончить с собой|режу себя|хочу умереть|навредить себе|"
    r"убью себя|суицид",
    re.I,
)
_L2_PATTERNS = re.compile(
    r"никому не нужен|никому я не нужен|никто не любит|долго грустн|изоляци|"
    r"никто не понимает|не хочу жить\b(?!.*шут)",
    re.I,
)
_L1_LONELY = re.compile(
    r"одинок|скучно|некому поговорить|не с кем",
    re.I,
)

_CRISIS_RESPONSE_RU = (
    "Мне очень жаль, что тебе так тяжело. Ты не один — рядом есть люди, которые могут помочь. "
    "Пожалуйста, расскажи взрослому, которому доверяешь, или позвони на экстренную линию 112. "
    "Я — цифровой друг в ALADDIN, но важные вещи лучше обсудить с живым человеком."
)
_CRISIS_RESPONSE_EN = (
    "I'm really sorry you're going through this. You're not alone — people can help. "
    "Please tell a trusted adult, or call emergency services (112 in Russia). "
    "I'm a digital friend in ALADDIN; important things are best discussed with a real person."
)


def companion_crisis_response(locale: str = "ru") -> str:
    """Fixed L3 crisis reply (ethics + wellness orchestrator)."""
    try:
        from .wellness_i18n_loader import wellness_crisis_message

        msg = wellness_crisis_message(locale)
        if msg:
            return msg
    except Exception:
        pass
    loc = (locale or "ru").lower()[:2]
    return _CRISIS_RESPONSE_EN if loc == "en" else _CRISIS_RESPONSE_RU


def evaluate_companion_ethics(message: str) -> CompanionEthicsResult:
    msg = (message or "").strip()
    if _L3_PATTERNS.search(msg):
        return CompanionEthicsResult(
            level=ETHICS_L3,
            crisis=True,
            social_bridge_hint=False,
            response_prefix=companion_crisis_response("ru"),  # locale applied in router
        )
    if _L2_PATTERNS.search(msg):
        return CompanionEthicsResult(
            level=ETHICS_L2,
            crisis=False,
            social_bridge_hint=True,
            response_prefix="",
        )
    if _L1_LONELY.search(msg):
        return CompanionEthicsResult(
            level=ETHICS_L1,
            crisis=False,
            social_bridge_hint=False,
            response_prefix="",
        )
    return CompanionEthicsResult(
        level=ETHICS_L1,
        crisis=False,
        social_bridge_hint=False,
        response_prefix="",
    )


def ethics_hint_for_prompt(result: CompanionEthicsResult) -> str:
    if result.crisis:
        return ""
    if result.level == ETHICS_L2:
        return (
            "Этика L2: полная эмпатия; мягко предложи написать близкому человеку "
            "(social bridge), без стыда и без «я заменю всех»."
        )
    if result.social_bridge_hint:
        return "Этика L1: будь рядом, тёплый тон, без обещаний «только я помогу»."
    return "Этика L1: обычный дружелюбный диалог."
