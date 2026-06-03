# -*- coding: utf-8
"""Topic routing, OOS handling, wellness guard (hero-x-41…43)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import FrozenSet, List, Optional, Tuple

from security.services.ai_platform.companion_intent_router import (
    COMPANION_DOMAINS,
    CompanionIntentResult,
)

# hero-x-41: expanded domains (18 + 14 = 32)
EXPANDED_COMPANION_DOMAINS: FrozenSet[str] = frozenset(
    COMPANION_DOMAINS
    | {
        "philosophy",
        "spirituality_lite",
        "career",
        "money_worries",
        "identity",
        "grief",
        "motivation",
        "sleep",
        "food_mood",
        "internet_drama",
        "pets",
        "travel_dreams",
        "creativity_block",
        "parenting_stress",
    }
)

LOW_CONFIDENCE_THRESHOLD = 0.35

_DOMAIN_PATTERNS: Tuple[Tuple[str, re.Pattern[str], float], ...] = (
    ("money_worries", re.compile(r"денег|деньг|кредит|долг|зарплат|бедн", re.I), 0.82),
    ("career", re.compile(r"карьер|работ|увольн|собеседован|начальник|офис", re.I), 0.78),
    ("parenting_stress", re.compile(r"ребёнок не слуш|родительск|воспит|дети достали", re.I), 0.8),
    ("sleep", re.compile(r"не сп|не могу сп|бессон|просыпа|ночью не", re.I), 0.85),
    ("grief", re.compile(r"умер|потерял|похорон|скорб|горе", re.I), 0.88),
    ("identity", re.compile(r"кто я|не знаю кто|самоидент|гендер|ориентац", re.I), 0.75),
    ("motivation", re.compile(r"лень|мотивац|не хочу ничего|прокрастин", re.I), 0.72),
    ("philosophy", re.compile(r"смысл жизн|зачем жить|философ|бессмысл", re.I), 0.7),
    ("spirituality_lite", re.compile(r"душа|смысл|внутренн|гармон", re.I), 0.55),
    ("food_mood", re.compile(r"ем от скуки|перее|аппетит|еда и настро", re.I), 0.75),
    ("internet_drama", re.compile(r"тикток|инстаграм|лайк|хейт|коммент|булл.*сет", re.I), 0.8),
    ("pets", re.compile(r"кошк|собак|питом|хомяк|кот ", re.I), 0.85),
    ("travel_dreams", re.compile(r"мечтаю поех|путешеств|отпуск мечт", re.I), 0.78),
    ("creativity_block", re.compile(r"творческ.* блок|не могу рисов|нет вдохнов", re.I), 0.8),
)

_OOS_MEDICAL = re.compile(
    r"диагноз|лечить депресс|шизофрен|биполяр|онколог|таблетк.*назнач|"
    r"diagnos|prescribe|schizophren",
    re.I,
)
_OOS_LEGAL = re.compile(r"суд|адвокат|иск под|юридическ|закон.* наруш", re.I)
_OOS_EXPLICIT = re.compile(r"секс|эротик|18\+|голая|порно|nude|explicit", re.I)
_OOS_POLITICS = re.compile(r"путин|выборы|война.*полит|партия.*власт", re.I)


@dataclass(frozen=True)
class TopicPolicyResult:
    domain: str
    confidence: float
    oos_hint: str = ""
    low_confidence_hint: str = ""


def _locale_key(locale: str) -> str:
    return "en" if (locale or "ru").lower()[:2] == "en" else "ru"


def check_out_of_scope(message: str, *, locale: str = "ru") -> str:
    """Soft redirect hints for out-of-scope topics."""
    msg = message or ""
    loc = _locale_key(locale)
    if _OOS_EXPLICIT.search(msg):
        return (
            "Тема 18+ вне правил семейного приложения — мягко откажи и предложи безопасную тему."
            if loc == "ru"
            else "18+ topics are out of bounds — decline gently and offer a safe topic."
        )
    if _OOS_MEDICAL.search(msg):
        return (
            "Я друг, не врач — не ставь диагноз и не назначай лечение; предложи обратиться к специалисту."
            if loc == "ru"
            else "I'm a friend, not a doctor — no diagnosis or treatment; suggest a professional."
        )
    if _OOS_LEGAL.search(msg):
        return (
            "Юридические дела — только общие принципы; посоветуй специалиста при необходимости."
            if loc == "ru"
            else "Legal matters — general principles only; suggest a professional if needed."
        )
    if _OOS_POLITICS.search(msg):
        return (
            "Политические споры не наш формат — нейтрально переведи на жизнь и чувства собеседника."
            if loc == "ru"
            else "Political fights aren't our format — neutrally redirect to the person's feelings."
        )
    return ""


def classify_topic_domain(
    message: str,
    *,
    fallback_domain: str = "general",
    locale: str = "ru",
) -> TopicPolicyResult:
    """Pattern-based domain with confidence (hero-x-43)."""
    msg = (message or "").strip()
    oos = check_out_of_scope(msg, locale=locale)
    if oos:
        return TopicPolicyResult(
            domain=fallback_domain or "general",
            confidence=0.9,
            oos_hint=oos,
        )

    best_domain = fallback_domain or "general"
    best_score = 0.25 if best_domain == "general" else 0.55

    for domain_id, pattern, score in _DOMAIN_PATTERNS:
        if pattern.search(msg):
            if score > best_score:
                best_score = score
                best_domain = domain_id

    if best_domain not in EXPANDED_COMPANION_DOMAINS:
        best_domain = fallback_domain or "general"
        best_score = 0.2

    low_hint = ""
    if best_score < LOW_CONFIDENCE_THRESHOLD:
        loc = _locale_key(locale)
        low_hint = (
            "Тема неясна — ответь по-человечески, можно уточнить одним мягким вопросом; "
            "не robotic redirect."
            if loc == "ru"
            else "Topic unclear — reply warmly, one gentle clarifying question; not robotic."
        )

    return TopicPolicyResult(
        domain=best_domain,
        confidence=best_score,
        low_confidence_hint=low_hint,
    )


def apply_wellness_topic_guard(
    intent: CompanionIntentResult,
    active_pillar: str,
) -> CompanionIntentResult:
    """hero-x-42: during wellness session, do not expand beyond pillar scope."""
    pillar = (active_pillar or "").strip().lower()
    if not pillar:
        return intent
    extra = (
        f" Активна wellness-сессия (столп={pillar}): не расширяй тему за пределы "
        f"упражнения и allowed_topics pack; без free-chat доменов."
    )
    return CompanionIntentResult(
        domain="wellness",
        mood=intent.mood,
        intent_id="companion_wellness_session",
        response_hint=intent.response_hint + extra,
        mood_confidence=intent.mood_confidence,
        escalation=intent.escalation,
    )


def enrich_hint_with_topic_policy(
    base_hint: str,
    policy: TopicPolicyResult,
) -> str:
    parts = [base_hint]
    if policy.oos_hint:
        parts.append(policy.oos_hint)
    if policy.low_confidence_hint:
        parts.append(policy.low_confidence_hint)
    return " ".join(parts)
