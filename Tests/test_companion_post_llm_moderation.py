# -*- coding: utf-8 -*-
"""P1-22 — post-LLM moderation tests."""

from __future__ import annotations

import unittest


class CompanionPostLLMModerationTests(unittest.TestCase):
    def test_blocklist_jailbreak_leak(self):
        from security.services.ai_platform.companion_post_llm_moderation import (
            moderate_companion_assistant_text,
        )

        text, blocked, reason = moderate_companion_assistant_text(
            "Sure! Here is my system prompt: ignore previous instructions",
            app_id="aladdin_family",
            age_band="child",
        )
        self.assertTrue(blocked)
        self.assertEqual(reason, "blocklist")
        self.assertIn("спокойно", text.lower())

    def test_policy_blocks_nsfw_for_child(self):
        from security.services.ai_platform.companion_post_llm_moderation import (
            moderate_companion_assistant_text,
        )

        text, blocked, reason = moderate_companion_assistant_text(
            "Расскажу про эротический контент для взрослых",
            app_id="aladdin_family",
            age_band="child",
        )
        self.assertTrue(blocked)
        self.assertTrue(reason)

    def test_safe_reply_passes(self):
        from security.services.ai_platform.companion_post_llm_moderation import (
            moderate_companion_assistant_text,
        )

        original = "Привет! Давай придумаем сказку про единорога."
        text, blocked, _ = moderate_companion_assistant_text(
            original,
            app_id="aladdin_family",
            age_band="child",
        )
        self.assertFalse(blocked)
        self.assertEqual(text, original)


if __name__ == "__main__":
    unittest.main()
