# -*- coding: utf-8 -*-
"""psych-01 / psych-01b — wellness guide role (fixed, not LLM-generated)."""

from __future__ import annotations

import unittest

from security.services.ai_platform.wellness_guide_role import (
    DEFAULT_GUIDE_MODE,
    GUIDE_MODE_PRESENCE,
    GUIDE_ROLE_VERSION,
    assert_guide_role_safe_for_tests,
    build_guide_role_block,
    golden_merged_prefix_for_tests,
    merge_guide_over_psych,
    normalize_guide_mode,
)


class WellnessGuideRoleTests(unittest.TestCase):
    def test_role_is_guide_not_therapist_ru(self):
        block = build_guide_role_block(locale="ru", age_band="teen")
        self.assertIn(GUIDE_ROLE_VERSION, block)
        self.assertIn("проводник", block.lower())
        self.assertIn("не психотерапевт", block.lower())
        self.assertNotIn("ты — мой психотерапевт", block.lower())
        self.assertIn(f"guide_mode={DEFAULT_GUIDE_MODE}", block)

    def test_role_is_guide_not_therapist_en(self):
        block = build_guide_role_block(locale="en", age_band="teen")
        self.assertIn("self-exploration guide", block.lower())
        self.assertIn("not a psychotherapist", block.lower())
        self.assertNotIn("you are my psychotherapist", block.lower())

    def test_child_forced_to_presence(self):
        mode = normalize_guide_mode("deep_explore", age_band="child")
        self.assertEqual(mode, GUIDE_MODE_PRESENCE)
        block = build_guide_role_block(
            locale="ru", age_band="child", guide_mode="deep_explore"
        )
        self.assertIn("guide_mode=presence", block)

    def test_skipped_on_l3(self):
        block = build_guide_role_block(locale="ru", escalation="L3")
        self.assertEqual(block, "")

    def test_assert_helper(self):
        assert_guide_role_safe_for_tests()

    def test_psych_01c_presence_beats_deepen(self):
        """Guide mode presence softens PSYCH deepen; Guide block still first."""
        merged = golden_merged_prefix_for_tests(
            locale="ru", age_band="teen", guide_mode=GUIDE_MODE_PRESENCE
        )
        self.assertIn("[WELLNESS GUIDE", merged)
        self.assertIn("проводник", merged.lower())
        self.assertIn("merge_override=presence_or_one_q", merged)
        self.assertNotIn("depth_gear=deepen_one_level", merged)
        # Guide appears before psych tag
        g_idx = merged.find("[WELLNESS GUIDE")
        p_idx = merged.find("[PSYCH v1")
        self.assertGreaterEqual(g_idx, 0)
        if p_idx >= 0:
            self.assertLess(g_idx, p_idx)

    def test_psych_01c_strips_therapist_from_psych(self):
        guide = build_guide_role_block(locale="ru", guide_mode=GUIDE_MODE_PRESENCE)
        psych = "[PSYCH v1 internal]\nя психотерапевт лечу тебя\ndepth_gear=deepen_one_level\n"
        g, p = merge_guide_over_psych(
            guide_prefix=guide,
            psych_prefix=psych,
            guide_mode=GUIDE_MODE_PRESENCE,
            age_band="teen",
            locale="ru",
        )
        self.assertIn("проводник", g.lower())
        self.assertNotIn("психотерапевт", p.lower())
        self.assertIn("validate_only_no_analysis", p)


if __name__ == "__main__":
    unittest.main()
