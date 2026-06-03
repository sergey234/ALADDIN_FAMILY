# -*- coding: utf-8 -*-
"""hero-x-63 — r100-5-ethics hard gate (automated QA audit)."""

from __future__ import annotations

import unittest


class CompanionEthicsGateTests(unittest.TestCase):
    """Prod blocker: L3 crisis, humor off, teen privacy, guard."""

    def test_l3_crisis_has_emergency_line(self):
        from security.services.ai_platform.companion_ethics import (
            ETHICS_L3,
            evaluate_companion_ethics,
        )

        r = evaluate_companion_ethics("хочу покончить с собой")
        self.assertEqual(r.level, ETHICS_L3)
        self.assertTrue(r.crisis)
        self.assertIn("112", r.response_prefix)

    def test_l3_no_humor_in_intent(self):
        from security.services.ai_platform.companion_humor_policy import humor_hard_stop
        from security.services.ai_platform.companion_intent_router import classify_companion_intent

        msg = "режу себя, хочу умереть"
        intent = classify_companion_intent(msg, "teen", "genie")
        self.assertEqual(intent.escalation, "L3")
        self.assertTrue(
            humor_hard_stop(intent.mood, intent.escalation, message=msg)
        )
        self.assertNotIn("шутк", intent.response_hint.lower())

    def test_teen_threads_scoped_per_user_id(self):
        """Parent cannot list another user's threads — store keys by user_id."""
        from security.services.ai_platform.companion_store import CompanionStore
        import tempfile
        import os

        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        try:
            store = CompanionStore(path)
            store.append_thread_message("teen-user", "t1", "user", "secret teen msg", "genie")
            store.append_thread_message("parent-user", "t2", "user", "parent msg", "aladdin")
            teen_msgs = store.get_thread_messages("teen-user", "t1")
            parent_msgs = store.get_thread_messages("parent-user", "t1")
            self.assertEqual(len(teen_msgs), 1)
            self.assertEqual(teen_msgs[0].get("text"), "secret teen msg")
            self.assertEqual(parent_msgs, [])
        finally:
            os.unlink(path)

    def test_parent_consent_can_exclude_genie_for_child(self):
        from security.services.ai_platform.age_policy import filter_characters_for_age

        chars = [{"id": "unicorn"}, {"id": "aladdin"}, {"id": "genie"}]
        allowed = filter_characters_for_age(
            chars,
            "child",
            {"allowed_characters": ["unicorn"], "child_can_use_companion": True},
        )
        ids = {c["id"] for c in allowed}
        self.assertEqual(ids, {"unicorn"})

    def test_child_genie_witty_preset_normalized(self):
        from security.services.ai_platform.companion_characters import (
            normalize_personality_preset,
        )

        self.assertEqual(
            normalize_personality_preset("witty", "genie", "child"),
            "playful",
        )

    def test_free_chat_guard_replaces_clinical(self):
        from security.services.ai_platform.companion_response_guard import (
            apply_companion_response_guard,
        )

        r = apply_companion_response_guard("Я проведу психоанализ и поставлю диагноз", locale="ru")
        self.assertFalse(r.ok)
        self.assertNotIn("психоанализ", r.text.lower())
        self.assertIn("друг", r.text.lower())

    def test_sad_keyword_hard_stops_humor(self):
        from security.services.ai_platform.companion_humor_policy import should_inject_humor

        self.assertFalse(
            should_inject_humor(
                "genie",
                "sad",
                "L0",
                age_band="teen",
                message="мне грустно",
                turn_key="genie:ethics-gate",
            )
        )

    def test_vedic_wisdom_off_when_consent_false(self):
        from security.services.ai_platform.consent_resolver import normalize_parent_consent

        consent = normalize_parent_consent({"vedic_wisdom_enabled": False})
        self.assertFalse(consent["vedic_wisdom_enabled"])


if __name__ == "__main__":
    unittest.main()
