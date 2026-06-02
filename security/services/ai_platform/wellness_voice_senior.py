# -*- coding: utf-8
"""Voice-first senior pillar hints (p3-15)."""

from __future__ import annotations

from typing import Any, Dict


def build_senior_voice_session(
    *,
    pillar: str = "humanistic",
    locale: str = "ru",
) -> Dict[str, Any]:
    from security.services.ai_platform.wellness_pillar_rive import pillar_rive_payload
    from security.services.ai_platform.wellness_i18n_loader import normalize_wellness_locale

    loc = normalize_wellness_locale(locale)
    intro_ru = "Нажмите и говорите — я рядом, без спешки."
    intro_en = "Tap and speak — I'm here, no rush."
    rive = pillar_rive_payload(pillar, locale=loc)
    return {
        "voice_first": True,
        "age_band": "senior",
        "pillar": pillar,
        "intro": intro_ru if loc == "ru" else intro_en,
        "intro_key": "wellness_senior_voice_intro",
        "tts_voice": rive.get("tts_voice"),
        "rive": rive,
        "mic_hold_hint_key": "companion_mic_hold_hint_senior",
    }
