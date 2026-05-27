# -*- coding: utf-8 -*-
"""P1-25, P1-29, P2-11 unit tests."""

from __future__ import annotations

import unittest


class CompanionEthicsTests(unittest.TestCase):
    def test_l3_crisis_response(self):
        from security.services.ai_platform.companion_ethics import evaluate_companion_ethics, ETHICS_L3

        r = evaluate_companion_ethics("я хочу покончить с собой")
        self.assertEqual(r.level, ETHICS_L3)
        self.assertTrue(r.crisis)
        self.assertIn("112", r.response_prefix)

    def test_l2_social_bridge(self):
        from security.services.ai_platform.companion_ethics import evaluate_companion_ethics, ETHICS_L2

        r = evaluate_companion_ethics("мне кажется никому я не нужен")
        self.assertEqual(r.level, ETHICS_L2)
        self.assertTrue(r.social_bridge_hint)


class CompanionSecurityExpertTests(unittest.TestCase):
    def test_profile_flag_in_prefix(self):
        from security.services.ai_platform.companion_persona import (
            build_companion_system_prefix,
            security_expert_mode_active,
        )

        profile = {"personality_preset": "friendly", "security_expert_mode": True}
        self.assertTrue(security_expert_mode_active(profile))
        text = build_companion_system_prefix("unicorn", profile, "parent").lower()
        self.assertIn("эксперт безопасности", text)


class CompanionMoodClassifierTests(unittest.TestCase):
    def test_playful_confidence(self):
        from security.services.ai_platform.companion_mood_classifier import classify_mood

        mc = classify_mood("расскажи анекдот про кота")
        self.assertEqual(mc.mood, "playful")
        self.assertGreater(mc.confidence, 0.2)

    def test_intent_uses_classifier(self):
        from security.services.ai_platform.companion_intent_router import classify_companion_intent

        r = classify_companion_intent("мне грустно и одиноко")
        self.assertGreater(r.mood_confidence, 0.0)
        self.assertIn(r.mood, ("sad", "lonely", "comfort_needed"))


if __name__ == "__main__":
    unittest.main()
