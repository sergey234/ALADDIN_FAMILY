# -*- coding: utf-8 -*-
"""Короткие фразы для server-side кэша TTS (20–30 на героя)."""

from __future__ import annotations

from typing import Dict, List

# RU — пилот genie, затем unicorn / aladdin
COMPANION_TTS_GREETINGS_RU: Dict[str, List[str]] = {
    "genie": [
        "Привет! Я твой джин-помощник.",
        "Слушаю тебя внимательно.",
        "Расскажи, что случилось?",
        "Я рядом, не переживай.",
        "Давай разберёмся вместе.",
        "Отличный вопрос!",
        "Хочешь поговорить о школе?",
        "Могу подсказать, как успокоиться.",
        "Ты молодец, что поделился.",
        "Я помогу найти выход.",
    ],
    "unicorn": [
        "Привет! Я единорог-помощник.",
        "Я рядом и слушаю тебя.",
        "Расскажи, как прошёл день?",
        "Ты не один, я с тобой.",
        "Давай подумаем вместе.",
        "Отлично, что ты написал.",
        "Хочешь поговорить о друзьях?",
        "Дыши спокойно, всё получится.",
        "Ты смелый и сильный.",
        "Я верю в тебя.",
    ],
    "aladdin": [
        "Привет! Я Алладин, твой друг.",
        "Слушаю, что у тебя на душе.",
        "Расскажи подробнее.",
        "Вместе мы справимся.",
        "Хороший вопрос, давай подумаем.",
        "Я помогу разобраться.",
        "Школа, семья, друзья — о чём хочешь?",
        "Спокойствие — наш первый шаг.",
        "Ты поступил правильно.",
        "Я на твоей стороне.",
    ],
}

# EN (короче — для smoke prewarm)
COMPANION_TTS_GREETINGS_EN: Dict[str, List[str]] = {
    "genie": [
        "Hi! I'm your genie helper.",
        "I'm listening.",
        "Tell me what happened.",
        "I'm here for you.",
    ],
    "unicorn": [
        "Hi! I'm your unicorn friend.",
        "I'm here with you.",
        "How was your day?",
    ],
    "aladdin": [
        "Hi! I'm Aladdin, your buddy.",
        "I'm listening carefully.",
        "We can figure this out together.",
    ],
}


def all_greeting_phrases(locale: str = "ru") -> List[tuple[str, str]]:
    """(character_id, text) pairs for prewarm."""
    table = COMPANION_TTS_GREETINGS_RU if locale.startswith("ru") else COMPANION_TTS_GREETINGS_EN
    out: List[tuple[str, str]] = []
    for character_id, phrases in table.items():
        for text in phrases:
            out.append((character_id, text))
    return out
