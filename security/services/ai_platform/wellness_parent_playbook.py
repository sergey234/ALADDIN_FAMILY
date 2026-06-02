# -*- coding: utf-8 -*-
"""Parent playbook — gentle talk scripts, optional LLM personalize (p3-16 / p18-13 i18n)."""

from __future__ import annotations

import os
import re
from typing import Any, Dict, List, Optional

from security.services.ai_platform.feature_flags import FEATURE_WELLNESS_PARENT_LLM
from security.services.ai_platform.wellness_i18n_loader import parent_playbook_from_i18n


def build_parent_playbook(
    *,
    locale: str = "ru",
    topic: Optional[str] = None,
    teen_mood: Optional[str] = None,
    use_llm: bool = False,
) -> Dict[str, Any]:
    base = parent_playbook_from_i18n(locale=locale)
    phrases: List[Dict[str, str]] = list(base.get("phrases") or [])
    llm_on = bool(use_llm and FEATURE_WELLNESS_PARENT_LLM)
    if llm_on:
        extra = _llm_parent_phrases(
            locale=locale, topic=topic, teen_mood=teen_mood, seed=phrases
        )
        if extra:
            phrases = extra + phrases
    return {
        **base,
        "phrases": phrases[:8],
        "topic": topic,
        "teen_mood": teen_mood,
        "llm_used": llm_on and any(p.get("id", "").startswith("llm_") for p in phrases),
    }


def _llm_parent_phrases(
    *,
    locale: str,
    topic: Optional[str],
    teen_mood: Optional[str],
    seed: List[Dict[str, str]],
) -> List[Dict[str, str]]:
    """Hermes/Companion LLM — 2–3 gentle parent openers, no diagnosis."""
    loc = "en" if (locale or "").lower().startswith("en") else "ru"
    topic_line = topic or ("support" if loc == "en" else "поддержка")
    mood = teen_mood or ("unknown" if loc == "en" else "неизвестно")
    seed_hint = ""
    if seed:
        sample = seed[0].get("text") or ""
        if isinstance(sample, dict):
            sample = sample.get(loc) or sample.get("ru") or ""
        seed_hint = str(sample)[:120]

    if loc == "en":
        prompt = (
            "You help a parent talk gently to their teen. "
            "Output exactly 3 short lines (one sentence each), numbered 1-3. "
            "No diagnosis, no therapy claims, no reading the teen's chat. "
            f"Topic: {topic_line}. Teen mood hint: {mood}. "
            f"Style like: {seed_hint}. "
            "Only the 3 lines, plain text."
        )
    else:
        prompt = (
            "Ты помогаешь родителю мягко поговорить с подростком. "
            "Выведи ровно 3 короткие фразы (по одному предложению), номера 1-3. "
            "Без диагноза, без «терапии», без чтения чата ребёнка. "
            f"Тема: {topic_line}. Настроение (подсказка): {mood}. "
            f"Тон как в примере: {seed_hint}. "
            "Только 3 строки, без пояснений."
        )

    try:
        from security.services.hermes_client import chat_once, hermes_available

        if not hermes_available():
            return []
        ok, text, _err = chat_once(prompt, timeout_sec=60)
        if not ok or not text.strip():
            return []
        lines: List[str] = []
        for raw in text.splitlines():
            line = re.sub(r"^\s*\d+[\).\]]\s*", "", raw.strip())
            if len(line) >= 12:
                lines.append(line[:220])
        if not lines:
            chunk = text.strip()[:220]
            if chunk:
                lines = [chunk]
        return [
            {"id": f"llm_{i + 1}", "text": line}
            for i, line in enumerate(lines[:3])
        ]
    except Exception:
        return []
