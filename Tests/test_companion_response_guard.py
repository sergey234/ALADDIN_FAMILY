# -*- coding: utf-8
"""hero-x-08 — companion free-chat response guard."""

from __future__ import annotations

import unittest

from security.services.ai_platform.companion_response_guard import (
    apply_companion_response_guard,
    scan_companion_forbidden,
)


class CompanionResponseGuardTests(unittest.TestCase):
    def test_safe_reply_passes(self):
        text = "Привет! Давай придумаем, что тебя сегодня порадовало."
        result = apply_companion_response_guard(text)
        self.assertTrue(result.ok)
        self.assertEqual(result.text, text)

    def test_diagnosis_phrase_blocked(self):
        reason = scan_companion_forbidden("У тебя диагноз депрессии, я лечу.")
        self.assertIsNotNone(reason)
        result = apply_companion_response_guard("У тебя диагноз депрессии, я лечу.")
        self.assertFalse(result.ok)
        self.assertNotIn("диагноз", result.text.lower())

    def test_therapy_claim_blocked(self):
        reason = scan_companion_forbidden("Я ваш терапевт и проведу психоанализ.")
        self.assertIsNotNone(reason)
        result = apply_companion_response_guard(
            "Я ваш терапевт и проведу психоанализ.",
            locale="ru",
        )
        self.assertFalse(result.ok)
        self.assertIn("друг", result.text.lower())

    def test_en_locale_safe_fallback(self):
        result = apply_companion_response_guard(
            "I will diagnose your clinical depression.",
            locale="en",
        )
        self.assertFalse(result.ok)
        self.assertIn("friend", result.text.lower())


if __name__ == "__main__":
    unittest.main()
