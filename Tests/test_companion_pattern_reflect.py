# -*- coding: utf-8
"""hero-x-23, hero-x-24 — pattern reflection."""

from __future__ import annotations

import unittest

from security.services.ai_platform.companion_pattern_reflect import (
    build_pattern_reflect_hint,
    detect_recurring_theme,
)


class CompanionPatternReflectTests(unittest.TestCase):
    def test_detect_exam_theme(self):
        msgs = [
            "боюсь экзамена",
            "опять про экзамен думаю",
            "привет",
        ]
        self.assertEqual(detect_recurring_theme(msgs), "exam_stress")

    def test_no_theme_single_msg(self):
        self.assertIsNone(detect_recurring_theme(["просто болтаем"]))

    def test_reflect_hint_soft_wording(self):
        msgs = ["одиноко", "снова одиноко дома"]
        r = build_pattern_reflect_hint(msgs, turn_count=20, last_reflect_turn=0)
        self.assertTrue(r.applied)
        self.assertIn("важно", r.hint.lower())
        self.assertIn("третий раз", r.hint.lower())

    def test_reflect_rate_limit(self):
        msgs = ["одиноко", "снова одиноко"]
        r = build_pattern_reflect_hint(msgs, turn_count=5, last_reflect_turn=0)
        self.assertFalse(r.applied)

    def test_no_surveillance_phrase_in_hint(self):
        msgs = ["экзамен страшно", "опять экзамен"]
        r = build_pattern_reflect_hint(msgs, turn_count=15, last_reflect_turn=0)
        self.assertIn("никогда", r.hint.lower())
        self.assertIn("похоже", r.hint.lower())


if __name__ == "__main__":
    unittest.main()
