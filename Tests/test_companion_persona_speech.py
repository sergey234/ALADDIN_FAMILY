# -*- coding: utf-8 -*-
"""HERO-3-16 — speech personas (SPEECH-Q)."""

import unittest


class TestCompanionPersonaSpeech(unittest.TestCase):
    def test_genie_prefix_distinct_from_aladdin(self):
        from security.services.ai_platform.companion_persona import companion_system_base

        genie = companion_system_base("genie", "teen")
        aladdin = companion_system_base("aladdin", "teen")
        self.assertIn("Джин", genie)
        self.assertNotIn("Джин", aladdin)
        self.assertIn("наставник-человек", aladdin)

    def test_witty_blocked_for_child(self):
        from security.services.ai_platform.companion_characters import normalize_personality_preset

        self.assertEqual(normalize_personality_preset("witty", "genie", "child"), "playful")

    def test_genie_humor_hint_on_playful(self):
        from security.services.ai_platform.companion_intent_router import classify_companion_intent

        r = classify_companion_intent("расскажи анекдот", "teen", "genie")
        self.assertEqual(r.mood, "playful")
        self.assertIn("сказочн", r.response_hint.lower())

    def test_sad_no_jokes_genie(self):
        from security.services.ai_platform.companion_intent_router import classify_companion_intent

        r = classify_companion_intent("мне грустно", "teen", "genie")
        self.assertIn("Без шуток", r.response_hint)

    def test_age_policy_child_has_all_heroes(self):
        from security.services.ai_platform.age_policy import get_age_band_rules

        rules = get_age_band_rules("child")
        self.assertEqual(set(rules.allowed_characters), {"unicorn", "aladdin", "genie"})

    def test_age_policy_teen_has_genie(self):
        from security.services.ai_platform.age_policy import get_age_band_rules

        rules = get_age_band_rules("teen")
        self.assertIn("genie", rules.allowed_characters)


if __name__ == "__main__":
    unittest.main()
