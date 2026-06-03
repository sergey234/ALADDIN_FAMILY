# -*- coding: utf-8
"""hero-x-20, hero-x-21 — psychology internal block."""

from __future__ import annotations

import unittest

from security.services.ai_platform.companion_psychology import (
    build_psych_internal_block,
    load_psychology_internal,
)


class CompanionPsychologyTests(unittest.TestCase):
    def test_internal_yaml_loads(self):
        pack = load_psychology_internal()
        self.assertEqual(pack.get("schema"), "companion_psychology_internal_v1")
        self.assertIn("listening_ladder", pack)

    def test_psych_block_l0(self):
        block = build_psych_internal_block("teen", "L0", locale="ru")
        self.assertIn("[PSYCH v1 internal]", block)
        self.assertIn("listening_ladder", block)
        self.assertIn("диагноз", block.lower() or "user_output")

    def test_psych_block_skipped_l3(self):
        block = build_psych_internal_block("teen", "L3")
        self.assertEqual(block, "")

    def test_no_clinical_words_in_user_output_rule(self):
        block = build_psych_internal_block("parent", "L0", locale="ru")
        self.assertIn("психоанализ", block)
        self.assertIn("Запрещено", block)


if __name__ == "__main__":
    unittest.main()
