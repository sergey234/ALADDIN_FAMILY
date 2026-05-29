# -*- coding: utf-8 -*-
"""Sprint 4 — domains, social bridge, teen playbook, trust empathy, orchestrator flag."""

from __future__ import annotations

import os
import unittest

os.environ.setdefault("JWT_SECRET", "test-secret-companion-s4")


class CompanionSprint4Tests(unittest.TestCase):
    def test_life_domains_child_hides_loneliness(self):
        from security.services.ai_platform.companion_life_domains import list_life_domains

        ids = {d["id"] for d in list_life_domains(age_band="child", locale="ru")}
        self.assertIn("school", ids)
        self.assertIn("feelings", ids)
        self.assertNotIn("loneliness", ids)
        self.assertNotIn("safety", ids)

    def test_life_domains_teen_includes_loneliness(self):
        from security.services.ai_platform.companion_life_domains import list_life_domains

        ids = {d["id"] for d in list_life_domains(age_band="teen", locale="ru")}
        self.assertIn("loneliness", ids)

    def test_social_bridge_after_streak(self):
        from security.services.ai_platform.companion_social_bridge import apply_social_bridge

        profile: dict = {}
        tid = "thread-1"
        for _ in range(2):
            profile, show, suggestions = apply_social_bridge(
                profile,
                domain="loneliness",
                social_bridge_hint=True,
                crisis=False,
                thread_id=tid,
            )
        self.assertTrue(show)
        self.assertIn("family", suggestions)

    def test_teen_playbook_bullying(self):
        from security.services.ai_platform.companion_teen_playbook import teen_playbook_hint

        hint = teen_playbook_hint("teen", "friends", "нас буллят в классе")
        self.assertIsNotNone(hint)
        self.assertIn("bullying", hint)

    def test_trust_delta_empathy_loneliness(self):
        try:
            from security.api.routers.ai_companion_router import _trust_delta
        except ModuleNotFoundError as exc:
            self.skipTest(f"router deps unavailable: {exc}")

        self.assertEqual(
            _trust_delta("мне одиноко", False, domain="loneliness", mood="lonely"),
            4,
        )
        self.assertEqual(_trust_delta("привет", False, domain="games", mood="playful"), 3)

    def test_orchestrator_flag_default_off(self):
        from security.services.ai_platform.feature_flags import COMPANION_USE_ORCHESTRATOR

        self.assertFalse(COMPANION_USE_ORCHESTRATOR)

    def test_profile_normalization_keeps_social_bridge(self):
        try:
            from security.api.routers.ai_companion_router import _normalize_profile_payload
        except ModuleNotFoundError as exc:
            self.skipTest(f"router deps unavailable: {exc}")

        raw = {
            "personality_preset": "friendly",
            "social_bridge": {"loneliness_streak": 2, "last_thread": "t1"},
        }
        out = _normalize_profile_payload(raw)
        self.assertEqual(out["social_bridge"]["loneliness_streak"], 2)


if __name__ == "__main__":
    unittest.main()
