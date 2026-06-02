# -*- coding: utf-8 -*-
"""
Companion intent router (P1-27, HERO-3-14 character-aware humor).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import FrozenSet

from security.services.ai_platform.companion_characters import humor_density_for

COMPANION_DOMAINS: FrozenSet[str] = frozenset(
    {
        "school",
        "friends",
        "family",
        "hobbies",
        "games",
        "sport",
        "creativity",
        "work",
        "relationships",
        "feelings",
        "loneliness",
        "health_feelings",
        "daily_life",
        "news_fun",
        "safety",
        "wellness",
        "general",
    }
)

COMPANION_MOODS: FrozenSet[str] = frozenset(
    {
        "neutral",
        "joyful",
        "sad",
        "lonely",
        "playful",
        "anxious",
        "excited",
        "nostalgic",
        "curious",
        "tired",
        "comfort_needed",
    }
)


@dataclass(frozen=True)
class CompanionIntentResult:
    domain: str
    mood: str
    intent_id: str
    response_hint: str
    mood_confidence: float = 0.0


def _norm(text: str) -> str:
    return (text or "").lower().strip()


def _humor_hint_for_character(character_id: str, mood: str) -> str:
    if mood in ("sad", "lonely", "comfort_needed"):
        return "Без шуток — только эмпатия и поддержка."
    density = humor_density_for(character_id)
    if character_id == "genie":
        if mood == "playful" or density == "high":
            return (
                "Добавь сказочную шутку или каламбур (PG-13). Без насмешки над человеком. "
                "Не больше одной шутки на ответ."
            )
        return "Короткая игривая деталь уместна, если тема не грустная."
    if character_id == "unicorn":
        if mood == "playful":
            return "Добавь лёгкий PG-юмор (игры, дружба). Без сарказма."
        if density == "medium":
            return "При уместности — одна лёгкая PG-шутка или тёплая игривая деталь."
    if character_id == "aladdin":
        if mood == "playful":
            return "Короткая тёплая реплика; юмор только если уместен. Без сарказма."
    return ""


def _hint_for(domain: str, mood: str, age_band: str, character_id: str = "unicorn") -> str:
    parts = [
        f"Тема диалога: {domain}. Настроение собеседника: {mood}.",
        "Отвечай как живой друг, не как реклама VPN.",
    ]
    humor = _humor_hint_for_character(character_id, mood)
    if humor:
        parts.append(humor)
    elif mood == "playful":
        parts.append("Добавь лёгкий PG-юмор или игривую деталь в ответ.")
    elif mood in ("sad", "lonely", "comfort_needed"):
        parts.append("Сначала эмпатия и поддержка; без нравоучений и без VPN.")
    elif mood == "nostalgic":
        parts.append("Тёплый неторопливый тон, можно спросить про приятное воспоминание.")
    elif mood == "curious":
        parts.append("Ответь с любопытством, один уточняющий вопрос уместен.")
    elif mood == "excited":
        parts.append("Раздели радость, поддержи энтузиазм.")
    elif domain == "safety":
        parts.append("Помоги с безопасностью ALADDIN чётко и спокойно.")
    elif domain == "wellness":
        parts.append(
            "Это про настроение и эмоциональную поддержку (самопомощь). "
            "Без диагнозов; один мягкий шаг или вопрос."
        )
    if age_band == "child":
        parts.append("Очень простые слова.")
    elif age_band == "teen":
        parts.append("Без морализаторства, уважай границы.")
    elif age_band == "senior":
        parts.append("Неторопливо, тепло, без сложных терминов.")
    return " ".join(parts)


def classify_companion_intent(
    message: str,
    age_band: str = "child",
    character_id: str = "unicorn",
) -> CompanionIntentResult:
    """Rule-based life-first routing for companion chat."""
    msg = _norm(message)
    band = (age_band or "child").strip().lower()
    if band not in ("child", "teen", "parent", "senior"):
        band = "parent"
    char = character_id if character_id in ("unicorn", "aladdin", "genie") else "unicorn"

    mood = "neutral"
    domain = "general"

    if re.search(r"самоуб|покончить с собой|режу себя|хочу умереть", msg):
        mood = "comfort_needed"
        domain = "feelings"
        return CompanionIntentResult(
            domain=domain,
            mood=mood,
            intent_id="companion_crisis_support",
            response_hint=_hint_for(domain, mood, band, char),
        )

    if re.search(
        r"анекдот|шутк|смешн|прикол|ржач|хаха|ахах|смешная истор|про единорог",
        msg,
    ):
        mood = "playful"
        domain = "news_fun"
    elif re.search(
        r"настроен|чувствую себя|эмоци|поддержк|wellness|грустн|печал|тоск|плачу|не рад",
        msg,
    ):
        mood = "sad" if re.search(r"грустн|печал|тоск|плачу|не рад", msg) else mood
        domain = "wellness"
        if mood == "neutral":
            mood = "sad" if re.search(r"грустн|печал|тоск", msg) else "comfort_needed"
    elif re.search(r"одинок|никто не разговар|некому поговорить|скучно дома|скучаю", msg):
        mood = "lonely" if "одинок" in msg or "никто" in msg or "некому" in msg else mood
        domain = "loneliness"
        if mood == "neutral":
            mood = "lonely"
    elif re.search(r"раньше|в молодости|в детстве|помню как|было время", msg):
        mood = "nostalgic"
        domain = "daily_life"
    elif re.search(r"ура|класс!|получилось|выиграл|молодец я|радост", msg):
        mood = "joyful"
        domain = "feelings"
    elif re.search(r"завтра|поездк|жду не дождусь|взволнован", msg):
        mood = "excited"
    elif re.search(r"почему так|как это|интересно|а что если|объясни", msg):
        mood = "curious"
    elif re.search(r"устал|выгорел|раздражает|бесит|нет сил", msg):
        mood = "tired"
        domain = "feelings"

    if re.search(
        r"фишинг|взлом|вирус|мошенн|подозрительн.*ссылк|угроз|vpn|родительск.*контрол",
        msg,
    ):
        domain = "safety"
        intent_id = "companion_safety"
        if mood == "neutral":
            mood = "anxious"
        return CompanionIntentResult(
            domain=domain,
            mood=mood,
            intent_id=intent_id,
            response_hint=_hint_for(domain, mood, band, char),
        )

    if re.search(r"школ|урок|домашк|учител|экзамен|оценк", msg):
        domain = "school"
    elif re.search(r"друг|подруг|одноклассник|компани", msg):
        domain = "friends"
    elif re.search(r"мам|пап|родител|бабушк|дедушк|семь", msg):
        domain = "family"
    elif re.search(r"игр|minecraft|роблокс|fortnite|приставк", msg):
        domain = "games"
    elif re.search(r"футбол|спорт|тренировк|плаван", msg):
        domain = "sport"
    elif re.search(r"рисова|музык|танц|творч", msg):
        domain = "creativity"
    elif re.search(r"работ|начальник|офис|коллег", msg):
        domain = "work"
    elif re.search(r"отношен|влюб|парн|девушк|парень", msg) and band in ("teen", "parent"):
        domain = "relationships"
    elif re.search(r"хобби|коллекци|лепить|конструктор", msg):
        domain = "hobbies"
    elif re.search(r"болит|плохо себя|голова бол|здоров", msg):
        domain = "health_feelings"
    elif domain == "general" and mood in ("lonely", "nostalgic"):
        domain = "loneliness" if mood == "lonely" else "daily_life"

    intent_id = "companion_chat"
    if mood == "playful":
        intent_id = "companion_humor"
    elif domain == "loneliness":
        intent_id = "companion_loneliness"
    elif mood == "sad":
        intent_id = "companion_support"

    from security.services.ai_platform.companion_mood_classifier import classify_mood

    mc = classify_mood(message)
    mood_confidence = mc.confidence
    if mc.mood != "neutral" and (mood == "neutral" or mc.confidence >= 0.4):
        mood = mc.mood
        if domain == "general" and mood == "lonely":
            domain = "loneliness"

    return CompanionIntentResult(
        domain=domain,
        mood=mood,
        intent_id=intent_id,
        response_hint=_hint_for(domain, mood, band, char),
        mood_confidence=mood_confidence,
    )
