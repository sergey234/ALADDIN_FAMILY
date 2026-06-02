# -*- coding: utf-8
"""Family prompt — «как поговорить с ребёнком» (p3-13)."""

from __future__ import annotations

from typing import Any, Dict, List


def build_family_talk_prompts(
    *,
    locale: str = "ru",
    topic: str = "mood",
    age_band: str = "teen",
) -> Dict[str, Any]:
    from security.services.ai_platform.wellness_i18n_loader import normalize_wellness_locale

    loc = normalize_wellness_locale(locale)
    prompts_ru: Dict[str, List[str]] = {
        "mood": [
            "Я заметил(а), что тебе может быть непросто. Хочешь рассказать, как день?",
            "Я рядом, без советов — просто послушаю.",
            "Что сегодня было хорошего, пусть маленького?",
        ],
        "school": [
            "Как прошёл день в школе — что запомнилось?",
            "Если что-то давит — можем вместе подумать, что поможет.",
        ],
    }
    prompts_en: Dict[str, List[str]] = {
        "mood": [
            "I noticed today might feel heavy. Want to tell me about it?",
            "I'm here to listen — no fixing unless you ask.",
            "What was one small good thing today?",
        ],
        "school": [
            "How was school — anything stick with you?",
            "If something feels heavy, we can think together about what helps.",
        ],
    }
    bank = prompts_ru if loc == "ru" else prompts_en
    items = bank.get(topic) or bank["mood"]
    return {
        "topic": topic,
        "age_band": age_band,
        "title_key": "wellness_family_talk_title",
        "prompts": [{"id": f"p{i}", "text": t} for i, t in enumerate(items, 1)],
    }
