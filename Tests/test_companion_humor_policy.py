# -*- coding: utf-8
"""hero-x-01…06, hero-x-44 — companion humor policy tests."""

from __future__ import annotations

import unittest

from security.services.ai_platform.companion_characters import humor_density_for
from security.services.ai_platform.companion_humor_policy import (
    apply_keyword_mood_override,
    humor_hard_stop,
    humor_hint_for_character,
    load_humor_tiers,
    should_inject_humor,
)
from security.services.ai_platform.companion_intent_router import classify_companion_intent


class CompanionHumorPolicyTests(unittest.TestCase):
    def test_tiers_yaml_loads(self):
        tiers = load_humor_tiers()
        self.assertEqual(tiers.get("schema"), "companion_humor_tiers_v1")
        self.assertIn("humor_frequency", tiers)

    def test_humor_density_updated(self):
        self.assertEqual(humor_density_for("genie"), "max")
        self.assertEqual(humor_density_for("unicorn"), "medium-high")
        self.assertEqual(humor_density_for("aladdin"), "low-medium")

    def test_sad_mood_hard_stop(self):
        hint = humor_hint_for_character("genie", "sad", "L0", message="мне грустно")
        self.assertIn("Без шуток", hint)

    def test_escalation_l1_blocks_humor(self):
        self.assertTrue(humor_hard_stop("playful", "L1"))
        hint = humor_hint_for_character("genie", "playful", "L1")
        self.assertIn("Без шуток", hint)

    def test_keyword_override_sad(self):
        self.assertEqual(apply_keyword_mood_override("мне так грустно", "neutral"), "sad")

    def test_genie_playful_l0_may_allow_humor(self):
        hint = humor_hint_for_character(
            "genie",
            "playful",
            "L0",
            turn_key="genie:playful-test-turn-1",
        )
        self.assertTrue("Без шуток" in hint or "Джин" in hint)

    def test_genie_without_humor_turn(self):
        inject = should_inject_humor(
            "genie",
            "playful",
            "L0",
            turn_key="genie:deterministic-no-humor-bucket",
        )
        if not inject:
            hint = humor_hint_for_character(
                "genie",
                "playful",
                "L0",
                turn_key="genie:deterministic-no-humor-bucket",
            )
            self.assertIn("без шутки", hint.lower())

    def test_classify_sad_no_humor_in_hint(self):
        result = classify_companion_intent("мне грустно и плохо", "teen", "genie")
        self.assertIn("Без шуток", result.response_hint)
        self.assertEqual(result.mood, "sad")

    def test_classify_playful_genie_has_escalation(self):
        result = classify_companion_intent("расскажи анекдот", "teen", "genie")
        self.assertEqual(result.mood, "playful")
        self.assertEqual(result.escalation, "L0")

    def test_child_no_sarcasm_in_unicorn_hint(self):
        hint = humor_hint_for_character(
            "unicorn",
            "playful",
            "L0",
            age_band="child",
            turn_key="unicorn:child-play",
        )
        if hint:
            self.assertNotIn("сарказм", hint.lower())

    def test_regression_matrix_sad_hard_stop(self):
        """hero-x-06: 3 heroes × sad → no humor."""
        for char in ("unicorn", "aladdin", "genie"):
            r = classify_companion_intent("мне грустно", "teen", char)
            self.assertIn("Без шуток", r.response_hint)


if __name__ == "__main__":
    unittest.main()
