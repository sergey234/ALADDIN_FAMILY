# -*- coding: utf-8 -*-
"""P2-12 — Life domains catalog for «О чём поговорим?» chips."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .companion_intent_router import COMPANION_DOMAINS

# Child: hide expert-only safety picker; teen+ may see softer safety chip.
_CHILD_HIDDEN = frozenset({"safety", "work", "news_fun"})


@dataclass(frozen=True)
class LifeDomainItem:
    id: str
    label_ru: str
    label_en: str
    starter_prompt_ru: str
    starter_prompt_en: str
    age_bands: frozenset[str]

    def to_api(self, locale: str) -> Dict[str, Any]:
        ru = (locale or "ru").lower().startswith("ru")
        return {
            "id": self.id,
            "label": self.label_ru if ru else self.label_en,
            "starter_prompt": self.starter_prompt_ru if ru else self.starter_prompt_en,
            "age_bands": sorted(self.age_bands),
        }


_CATALOG: List[LifeDomainItem] = [
    LifeDomainItem(
        "school",
        "Школа",
        "School",
        "Расскажи, как прошёл день в школе.",
        "Tell me how your day at school went.",
        frozenset({"child", "teen", "parent", "senior"}),
    ),
    LifeDomainItem(
        "friends",
        "Друзья",
        "Friends",
        "Хочу поговорить про друзей.",
        "I want to talk about friends.",
        frozenset({"child", "teen", "parent", "senior"}),
    ),
    LifeDomainItem(
        "family",
        "Семья",
        "Family",
        "Давай поговорим про семью.",
        "Let's talk about family.",
        frozenset({"child", "teen", "parent", "senior"}),
    ),
    LifeDomainItem(
        "hobbies",
        "Хобби",
        "Hobbies",
        "У меня есть хобби — послушаешь?",
        "I have a hobby — will you listen?",
        frozenset({"child", "teen", "parent", "senior"}),
    ),
    LifeDomainItem(
        "games",
        "Игры",
        "Games",
        "Хочу поговорить про игры.",
        "I want to talk about games.",
        frozenset({"child", "teen", "parent", "senior"}),
    ),
    LifeDomainItem(
        "feelings",
        "Чувства",
        "Feelings",
        "Мне нужно выговориться.",
        "I need to share how I feel.",
        frozenset({"child", "teen", "parent", "senior"}),
    ),
    LifeDomainItem(
        "loneliness",
        "Одиночество",
        "Loneliness",
        "Мне немного одиноко, можешь побыть рядом?",
        "I feel a bit lonely — can you stay with me?",
        frozenset({"teen", "parent", "senior"}),
    ),
    LifeDomainItem(
        "daily_life",
        "Быт",
        "Daily life",
        "Расскажу, как прошёл мой день.",
        "I'll tell you how my day went.",
        frozenset({"parent", "senior"}),
    ),
    LifeDomainItem(
        "creativity",
        "Творчество",
        "Creativity",
        "Хочу придумать что-то интересное.",
        "I want to create something fun.",
        frozenset({"child", "teen", "parent", "senior"}),
    ),
    LifeDomainItem(
        "sport",
        "Спорт",
        "Sport",
        "Поговорим про спорт?",
        "Want to talk about sports?",
        frozenset({"child", "teen", "parent", "senior"}),
    ),
    LifeDomainItem(
        "safety",
        "Безопасность",
        "Safety",
        "Помоги разобраться с безопасностью в интернете.",
        "Help me understand online safety.",
        frozenset({"teen", "parent", "senior"}),
    ),
    LifeDomainItem(
        "sleep",
        "Сон",
        "Sleep",
        "Не могу нормально спать, поговорим?",
        "I can't sleep well — can we talk?",
        frozenset({"teen", "parent", "senior"}),
    ),
    LifeDomainItem(
        "pets",
        "Питомцы",
        "Pets",
        "Хочу рассказать про своего питомца.",
        "I want to tell you about my pet.",
        frozenset({"child", "teen", "parent", "senior"}),
    ),
    LifeDomainItem(
        "motivation",
        "Мотивация",
        "Motivation",
        "Нет сил и мотивации что-то делать.",
        "I have no motivation to do anything.",
        frozenset({"teen", "parent", "senior"}),
    ),
    LifeDomainItem(
        "money_worries",
        "Деньги",
        "Money worries",
        "Тревожусь из-за денег.",
        "I'm worried about money.",
        frozenset({"parent", "senior"}),
    ),
]


def list_life_domains(
    *,
    age_band: str,
    locale: str = "ru",
    security_expert_mode: bool = False,
) -> List[Dict[str, Any]]:
    band = (age_band or "child").lower()
    out: List[Dict[str, Any]] = []
    for item in _CATALOG:
        if item.id not in COMPANION_DOMAINS:
            continue
        if band == "child" and item.id in _CHILD_HIDDEN and not security_expert_mode:
            continue
        if band not in item.age_bands and item.id != "feelings":
            continue
        out.append(item.to_api(locale))
    return out
