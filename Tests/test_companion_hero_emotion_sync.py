# -*- coding: utf-8 -*-
"""HERO-3-25 — iOS `CompanionHeroEmotion` ↔ BE `COMPANION_HERO_EMOTIONS` (13 state)."""

from __future__ import annotations

import unittest

# Canonical set — keep in sync with CompanionModels.swift `CompanionHeroEmotion`.
IOS_COMPANION_HERO_EMOTIONS = frozenset(
    {
        "idle",
        "happy",
        "listening",
        "speaking",
        "alert",
        "comfort",
        "celebrate",
        "thinking",
        "sad",
        "playful",
        "curious",
        "nostalgic",
        "excited",
    }
)

DIALOGUE_PHASES = frozenset({"listening", "thinking", "speaking"})
CONTENT_EMOTIONS = IOS_COMPANION_HERO_EMOTIONS - DIALOGUE_PHASES


class TestCompanionHeroEmotionSync(unittest.TestCase):
    def test_be_matches_ios_canonical_set(self):
        from security.services.ai_platform.companion_emotions import COMPANION_HERO_EMOTIONS

        self.assertEqual(
            set(COMPANION_HERO_EMOTIONS),
            set(IOS_COMPANION_HERO_EMOTIONS),
            "BE COMPANION_HERO_EMOTIONS must match iOS CompanionHeroEmotion",
        )

    def test_thirteen_states_partition(self):
        self.assertEqual(len(IOS_COMPANION_HERO_EMOTIONS), 13)
        self.assertEqual(len(DIALOGUE_PHASES), 3)
        self.assertEqual(len(CONTENT_EMOTIONS), 10)
        self.assertFalse(DIALOGUE_PHASES & CONTENT_EMOTIONS)

    def test_rive_mapping_names_match_enum(self):
        """CompanionHeroRiveMapping.riveStateName uses rawValue 1:1."""
        for name in IOS_COMPANION_HERO_EMOTIONS:
            self.assertEqual(name, name.lower())
            self.assertTrue(name.isascii())


if __name__ == "__main__":
    unittest.main()
