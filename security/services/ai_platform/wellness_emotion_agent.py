# -*- coding: utf-8 -*-
"""Mood inference for pillar routing: regex/keywords + optional LLM fallback (p2-33)."""

from __future__ import annotations

import os
import re
from typing import Any, Dict, Optional, Tuple

from .wellness_journal import mood_score_from_emoji

# Extended lexicon when check-in emoji is missing or free-text notes exist.
_MOOD_PATTERNS: Tuple[Tuple[str, int], ...] = (
    (r"(ужас|паник|не\s+выдерж|хочу\s+умер|суицид)", 1),
    (r"(груст|печал|тоск|плач|одинок)", 1),
    (r"(тревож|волную|страш|нервнич)", 2),
    (r"(устал|выгор|нет\s+сил|истощ)", 2),
    (r"(норм|терпим|сойдёт|сойдет)", 3),
    (r"(радост|счаст|класс|отличн|хорошо)", 4),
    (r"(восторг|супер|круто|прекрасн)", 5),
    (r"\b(terrible|hopeless|suicid|panic)\b", 1),
    (r"\b(sad|depress|lonely|crying)\b", 1),
    (r"\b(anxious|worried|scared|nervous)\b", 2),
    (r"\b(tired|exhaust|burnout|drained)\b", 2),
    (r"\b(okay|fine|alright|neutral)\b", 3),
    (r"\b(happy|glad|good|better)\b", 4),
    (r"\b(great|amazing|wonderful|joy)\b", 5),
)


def infer_mood_score_from_text(text: str) -> Optional[int]:
    blob = (text or "").strip().lower()
    if not blob:
        return None
    for pattern, score in _MOOD_PATTERNS:
        if re.search(pattern, blob, re.I):
            return score
    return None


def _llm_mood_score(text: str) -> Optional[int]:
    """Optional LLM path when FEATURE_WELLNESS_MOOD_LLM=1 (disabled in smoke/tests)."""
    if os.getenv("FEATURE_WELLNESS_MOOD_LLM", "").lower() not in ("1", "true", "yes"):
        return None
    for mod in (
        "security.services.ai_platform.companion_llm",
        "security.services.ai_platform.llm_client",
    ):
        try:
            mod_ref = __import__(mod, fromlist=["companion_chat_complete"])
            fn = getattr(mod_ref, "companion_chat_complete", None)
            if not fn:
                continue
            prompt = (
                "Return ONLY one digit 1-5 for mood (1=very low, 5=great). "
                f"User text: {text[:400]}"
            )
            raw = fn(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4,
                temperature=0,
            )
            digit = re.search(r"[1-5]", str(raw or ""))
            if digit:
                return int(digit.group())
        except Exception:
            continue
    return None


def resolve_mood_score(
    *,
    checkin: Optional[Dict[str, Any]] = None,
    message: str = "",
    notes: str = "",
) -> Tuple[Optional[int], str]:
    """
    Returns (mood_score, source).
    source: checkin | notes | message_regex | llm | none
    """
    if checkin:
        score = checkin.get("mood_score")
        if score is not None:
            return int(score), "checkin"
        emoji_score = mood_score_from_emoji(checkin.get("mood_emoji"))
        if emoji_score is not None:
            return emoji_score, "checkin_emoji"

    for src, blob in (("notes", notes), ("message", message)):
        score = infer_mood_score_from_text(blob)
        if score is not None:
            return score, f"{src}_regex"

    combined = " ".join(x for x in (message, notes) if x).strip()
    if combined:
        llm_score = _llm_mood_score(combined)
        if llm_score is not None:
            return llm_score, "llm"

    return None, "none"


def resolve_mood_for_user(
    store: Any,
    user_id: str,
    *,
    message: str = "",
) -> Tuple[Optional[int], str]:
    from datetime import date

    checkin = store.get_wellness_checkin(user_id, date.today().isoformat())
    notes = str((checkin or {}).get("notes") or "")
    return resolve_mood_score(checkin=checkin, message=message, notes=notes)
