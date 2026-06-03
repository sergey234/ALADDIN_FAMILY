# -*- coding: utf-8 -*-
"""hero-x-40 empathy validation-first."""

from security.services.ai_platform.companion_empathy import empathy_validation_hint
from security.services.ai_platform.companion_intent_router import classify_companion_intent


class TestCompanionEmpathy:
    def test_sad_mood_injects_validation_macro(self):
        r = classify_companion_intent("мне грустно и плохо", "teen", "unicorn")
        assert r.mood == "sad"
        assert "validation" in r.response_hint.lower() or "эмпат" in r.response_hint.lower()

    def test_empathy_hint_for_anxious(self):
        hint = empathy_validation_hint("anxious", age_band="teen", locale="ru")
        assert "тревож" in hint.lower()

    def test_playful_skips_empathy_macro(self):
        hint = empathy_validation_hint("playful", age_band="teen", locale="ru")
        assert hint == ""

    def test_senior_pause_on_lonely(self):
        hint = empathy_validation_hint("lonely", age_band="senior", locale="ru")
        assert "пауз" in hint.lower() or "рядом" in hint.lower()
