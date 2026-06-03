# -*- coding: utf-8
"""hero-x-10…13, hero-x-15 — companion wisdom picker."""

from __future__ import annotations

import unittest

from security.services.ai_platform.companion_wisdom import (
    format_wisdom_block,
    load_wisdom_snippets,
    pick_wisdom_snippet,
    wisdom_frequency_allowed,
)


class CompanionWisdomTests(unittest.TestCase):
    def test_load_at_least_20_snippets(self):
        _, snippets = load_wisdom_snippets()
        self.assertGreaterEqual(len(snippets), 20)

    def test_aladdin_exam_stress_no_religion(self):
        sn = pick_wisdom_snippet(
            "aladdin",
            "school",
            "neutral",
            "teen",
            turn_count=1,
        )
        self.assertIsNotNone(sn)
        assert sn is not None
        low = sn.ru_paraphrase.lower()
        for word in ("бог", "храм", "молитва", "религия"):
            self.assertNotIn(word, low)

    def test_child_unicorn_universal_only(self):
        sn = pick_wisdom_snippet(
            "unicorn",
            "school",
            "neutral",
            "child",
            turn_count=0,
        )
        self.assertIsNotNone(sn)
        assert sn is not None
        self.assertEqual(sn.snippet_tier, "universal")

    def test_genie_skipped_when_sad(self):
        sn = pick_wisdom_snippet("genie", "feelings", "sad", "teen")
        self.assertIsNone(sn)

    def test_format_block(self):
        sn = pick_wisdom_snippet("genie", "games", "playful", "teen", turn_count=2)
        self.assertIsNotNone(sn)
        block = format_wisdom_block(sn)
        self.assertIn("[WISDOM v1]", block)

    def test_frequency_cap(self):
        self.assertTrue(wisdom_frequency_allowed(0))
        self.assertTrue(wisdom_frequency_allowed(5))
        self.assertFalse(wisdom_frequency_allowed(3))

    def test_anti_repeat_used_ids(self):
        first = pick_wisdom_snippet(
            "aladdin",
            "school",
            "neutral",
            "teen",
            turn_count=0,
        )
        self.assertIsNotNone(first)
        second = pick_wisdom_snippet(
            "aladdin",
            "school",
            "neutral",
            "teen",
            turn_count=1,
            used_snippet_ids=[first.id],
        )
        if second:
            self.assertNotEqual(second.id, first.id)


if __name__ == "__main__":
    unittest.main()
