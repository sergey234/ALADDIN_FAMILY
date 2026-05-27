# -*- coding: utf-8 -*-
"""P1-26 — persona must be life-first, not security-first."""

from __future__ import annotations

import unittest

SECURITY_MARKERS = (
    "vpn",
    "угроз",
    "родительск",
    "инцидент",
    "настройки приложения",
)

LIFE_MARKERS = (
    "дружб",
    "хобби",
    "учёб",
    "скук",
    "эмоци",
    "юмор",
    "поддерж",
    "игр",
    "мечт",
    "семь",
)


class CompanionPersonaLifeFirstTests(unittest.TestCase):
    def test_unicorn_child_life_markers_dominate(self):
        from security.services.ai_platform.companion_persona import companion_system_base

        text = companion_system_base("unicorn", "child").lower()
        life_hits = sum(1 for m in LIFE_MARKERS if m in text)
        sec_hits = sum(1 for m in SECURITY_MARKERS if m in text)
        self.assertGreaterEqual(life_hits, 5, "expected rich life-domain vocabulary")
        self.assertGreater(life_hits, sec_hits, "life markers should outnumber security markers")

    def test_security_on_demand_not_default_opening(self):
        from security.services.ai_platform.companion_persona import companion_system_base

        text = companion_system_base("aladdin", "parent").lower()
        self.assertTrue(
            "по запросу" in text or "если пользователь" in text or "спросил" in text,
            "security block should be conditional",
        )
        # First ~120 chars should not push VPN as primary topic
        opening = text[:120]
        self.assertNotIn("vpn", opening)

    def test_playful_preset_not_security_jokes_only(self):
        from security.services.ai_platform.companion_persona import (
            PERSONALITY_PRESET_HINTS,
            build_companion_system_prefix,
        )

        hint = PERSONALITY_PRESET_HINTS["playful"].lower()
        self.assertIn("юмор", hint)
        self.assertNotIn("защит", hint)

        full = build_companion_system_prefix(
            "unicorn",
            {"personality_preset": "playful"},
            "teen",
        ).lower()
        self.assertIn("игрив", full)

    def test_senior_tone_present(self):
        from security.services.ai_platform.companion_persona import companion_system_base

        text = companion_system_base("unicorn", "senior")
        self.assertIn("60+", text)


if __name__ == "__main__":
    unittest.main()
