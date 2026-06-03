# -*- coding: utf-8 -*-
"""hero-x-67/68 — teen humor preference + genie A/B scale."""

from __future__ import annotations

import os
import unittest

os.environ.setdefault("JWT_SECRET", "test-teen-humor")


class CompanionHumorTeenTests(unittest.TestCase):
    def test_less_humor_reduces_probability(self):
        from security.services.ai_platform.companion_humor_policy import humor_injection_probability

        normal = humor_injection_probability("genie", "playful", "L0", humor_preference="normal")
        less = humor_injection_probability("genie", "playful", "L0", humor_preference="less")
        self.assertGreater(normal, less)
        self.assertAlmostEqual(less, normal * 0.45, places=3)

    def test_genie_ab_high_scales_down(self):
        from security.services.ai_platform.companion_experiment import (
            genie_humor_ab_variant,
            genie_humor_probability_scale,
        )
        from security.services.ai_platform.companion_humor_policy import humor_injection_probability

        scale = genie_humor_probability_scale("high")
        self.assertAlmostEqual(scale, 0.70)
        v = genie_humor_ab_variant("user-abc", enabled=True)
        self.assertIn(v, ("max", "high"))

    def test_teen_less_passed_to_classify(self):
        from security.services.ai_platform.companion_intent_router import classify_companion_intent
        from security.services.ai_platform.companion_humor_policy import humor_injection_probability

        r = classify_companion_intent("расскажи анекдот", "teen", "genie", humor_preference="less")
        self.assertEqual(r.mood, "playful")
        less_p = humor_injection_probability("genie", "playful", "L0", humor_preference="less")
        self.assertLess(less_p, 0.35)


if __name__ == "__main__":
    unittest.main()
