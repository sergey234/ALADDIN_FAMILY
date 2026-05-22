# -*- coding: utf-8 -*-
"""Rule-based intent classification for AI Security Copilot."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional, Tuple

FACTUAL_INTENTS = frozenset(
    {
        "protection_status",
        "threats_summary",
        "incident_analyze",
        "family_overview",
        "network_vpn_status",
        "recommendations",
    }
)

KB_ONLY_INTENTS = frozenset(
    {
        "parental_howto",
        "tariff_explain",
        "e2ee_howto",
        "app_help",
    }
)


@dataclass(frozen=True)
class IntentResult:
    intent_id: str
    required_tools: Tuple[str, ...]
    kb_only: bool = False


def _normalize(text: str) -> str:
    return (text or "").lower().strip()


def classify_intent(message: str, ui_context: str = "general") -> IntentResult:
    msg = _normalize(message)
    ctx = _normalize(ui_context)

    if ctx in ("feedback",):
        return IntentResult("feedback", (), False)
    if ctx in ("threat_analysis", "analyze_threat", "incident_analyze"):
        return IntentResult("incident_analyze", ("ai_assistant_analyze_threat",), False)
    if ctx in ("protection_status",):
        return IntentResult("protection_status", ("get_components_health",), False)
    if ctx in ("recommendations",):
        return IntentResult("recommendations", ("ai_assistant_recommendations",), False)

    if re.search(r"https?://|фишинг|фишингов|подозрительн|ссылк|письм", msg):
        return IntentResult("incident_analyze", ("ai_assistant_analyze_threat",), False)
    if re.search(r"угроз|заблок|блокир|статистик|аналитик|сегодня|недел", msg):
        return IntentResult("threats_summary", ("get_analytics_overview",), False)
    if re.search(r"всё ли включ|статус защит|защит[аы] включ|модул", msg):
        return IntentResult("protection_status", ("get_components_health",), False)
    if re.search(r"vpn|сеть|wi-?fi|отключ", msg):
        return IntentResult("network_vpn_status", ("get_components_health",), False)
    if re.search(r"семь|дет|ребён|ребен", msg):
        return IntentResult("family_overview", ("get_analytics_overview",), False)
    # «игр» убрано: ложное срабатывание на «ноутбук для игр» (off-topic покупки).
    if re.search(
        r"youtube|tiktok|родительск|огранич|видеоигр|игровое время|"
        r"ограничить.*игр|заблокировать.*игр",
        msg,
    ):
        return IntentResult("parental_howto", (), True)
    if re.search(r"premium|тариф|подписк", msg):
        return IntentResult("tariff_explain", (), True)
    if re.search(r"e2ee|шифрован|семейн.*чат", msg):
        return IntentResult("e2ee_howto", (), True)
    if re.search(r"улучш|рекоменд|совет", msg):
        return IntentResult("recommendations", ("ai_assistant_recommendations",), False)
    if re.search(r"не помог|обратн|feedback", msg):
        return IntentResult("feedback", (), False)
    if re.search(
        r"учишь|обуча|обучен|как работа|что умеешь|что можешь|кто ты|ты ai|"
        r"помощник aladdin|нейросет|искусствен",
        msg,
    ):
        return IntentResult("app_help", (), True)

    return IntentResult("general", ("ai_assistant_chat",), False)


def intent_requires_live_sfm(intent_id: str) -> bool:
    return intent_id in FACTUAL_INTENTS
