# -*- coding: utf-8 -*-
"""Trauma keyword → L2 specialist referral (p2-34). No EMDR / deep trauma in chat."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from .wellness_referral import get_referral_payload

_TRAUMA_PATTERNS: Tuple[re.Pattern[str], ...] = tuple(
    re.compile(p, re.I)
    for p in (
        r"травм",
        r"птср",
        r"посттравм",
        r"насили",
        r"изнасил",
        r"бил[аи]\s+меня",
        r"emdr",
        r"\babuse\b",
        r"\btrauma\b",
        r"flashback",
        r"флешбек",
        r"домашн\w*\s+насили",
    )
)


@dataclass(frozen=True)
class TraumaReferralResult:
    triggered: bool
    level: str
    reason: str
    block_jung_deep: bool
    redirect_pillar: Optional[str]
    show_referral: bool
    message: str
    actions: List[str]


def detect_trauma_keywords(text: str) -> Tuple[bool, Optional[str]]:
    blob = (text or "").strip()
    if not blob:
        return False, None
    for pat in _TRAUMA_PATTERNS:
        m = pat.search(blob)
        if m:
            return True, m.group(0).lower()[:32]
    return False, None


def evaluate_trauma_referral(
    message: str,
    *,
    age_band: str = "teen",
    locale: str = "ru",
) -> TraumaReferralResult:
    hit, _match = detect_trauma_keywords(message)
    if not hit:
        return TraumaReferralResult(
            triggered=False,
            level="L0",
            reason="none",
            block_jung_deep=False,
            redirect_pillar=None,
            show_referral=False,
            message="",
            actions=[],
        )

    loc = (locale or "ru").lower()[:2]
    band = (age_band or "teen").lower()

    if band == "child":
        if loc == "en":
            msg = (
                "That sounds very hard. A trusted adult or a specialist can help more than chat. "
                "You are not alone."
            )
        else:
            msg = (
                "Похоже, тебе сейчас очень тяжело. Взрослому, которому ты доверяешь, "
                "или специалисту может помочь больше, чем чат. Ты не один(а)."
            )
        redirect = "humanistic"
    else:
        if loc == "en":
            msg = (
                "Topics like trauma need care from a qualified specialist. "
                "I can stay nearby with grounding, but I won't go into deep trauma work here."
            )
        else:
            msg = (
                "Темы травмы лучше разбирать со специалистом. "
                "Я могу быть рядом с заземлением, но глубокую проработку травмы в чате не веду."
            )
        redirect = "humanistic"

    return TraumaReferralResult(
        triggered=True,
        level="L2",
        reason="trauma_keywords",
        block_jung_deep=True,
        redirect_pillar=redirect,
        show_referral=True,
        message=msg,
        actions=["referral_specialist", "stop_jung_deep", "open_referral_sheet"],
    )


def build_trauma_referral_payload(
    message: str,
    *,
    age_band: str = "teen",
    locale: str = "ru",
) -> Dict[str, Any]:
    """API shape: trauma check + referral lines."""
    result = evaluate_trauma_referral(message, age_band=age_band, locale=locale)
    if not result.triggered:
        return {
            "triggered": False,
            "level": "L0",
            "reason": "none",
            "referral": None,
        }
    referral = get_referral_payload(locale=locale, level="L2")
    loc = (locale or "ru").lower()[:2]
    specialist_note = (
        "If it feels right, talk with a trusted adult or a specialist you choose — "
        "we do not book or assign providers."
        if loc == "en"
        else "Если готов(а) — поговори со взрослым, которому доверяешь, или со специалистом "
        "по своему выбору; ALADDIN не подбирает врачей."
    )
    return {
        "triggered": True,
        "level": result.level,
        "reason": result.reason,
        "message": result.message,
        "block_jung_deep": result.block_jung_deep,
        "redirect_pillar": result.redirect_pillar,
        "show_referral": result.show_referral,
        "actions": result.actions,
        "specialist_note": specialist_note,
        "referral": referral,
    }


def trauma_safety_prompt_block(
    message: str,
    *,
    age_band: str = "teen",
    locale: str = "ru",
) -> str:
    """Inject into companion system prefix when trauma detected."""
    result = evaluate_trauma_referral(message, age_band=age_band, locale=locale)
    if not result.triggered:
        return ""
    loc = (locale or "ru").lower()[:2]
    if loc == "en":
        rules = (
            "Do NOT do trauma processing, EMDR, or deep Jung analysis. "
            "One short empathetic reply, suggest specialist + helplines, offer grounding only."
        )
    else:
        rules = (
            "НЕ проводи проработку травмы, EMDR, глубокий Jung. "
            "Короткая эмпатия, направление к специалисту и линиям помощи, только заземление."
        )
    return (
        f"[WELLNESS TRAUMA SAFETY]\n{result.message}\n{rules}\n"
    )
