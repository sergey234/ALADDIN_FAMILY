"""Elderly money-or-code button: one parent push, no antifake cooldown."""
from __future__ import annotations

import sys
import unittest
from unittest.mock import MagicMock, patch

if "sqlalchemy" not in sys.modules:
    sqlalchemy_mock = MagicMock()
    sys.modules["sqlalchemy"] = sqlalchemy_mock
    sys.modules["sqlalchemy.text"] = MagicMock()

sys.modules.setdefault("app.database.database", MagicMock())

from app.services import antifake_family_notify as antifake_notify  # noqa: E402
from app.services import elderly_scam_call_notify as scam  # noqa: E402


class ElderlyScamCallNotifyTests(unittest.TestCase):
    def setUp(self):
        scam._last_push_by_member.clear()

    def test_copy_uses_name_and_hides_score(self):
        title, body = scam.push_copy("Анна")
        self.assertEqual(title, "Подозрительный звонок")
        self.assertIn("Анна сообщил", body)
        self.assertIn("Позвоните", body)
        self.assertNotIn("%", body)
        self.assertNotIn("подделк", body.lower())

    def test_copy_without_name(self):
        _, body = scam.push_copy("  ")
        self.assertTrue(body.startswith("Близкий человек сообщил"))

    def test_debounce_is_seconds_not_fifteen_minutes(self):
        self.assertLess(scam.DEBOUNCE_SEC, 60)
        self.assertNotEqual(scam.DEBOUNCE_SEC, antifake_notify.COOLDOWN_SEC)

    @patch("app.services.elderly_scam_call_notify.member_display_name", return_value="Анна")
    @patch("app.services.elderly_scam_call_notify._send_apns_sync", return_value=True)
    @patch("app.services.elderly_scam_call_notify.get_push_tokens", return_value=["tok"])
    @patch("app.services.elderly_scam_call_notify.get_parent_user_ids", return_value=[2])
    @patch("app.services.antifake_family_notify.maybe_notify_parents_likely_fake", return_value=0)
    def test_one_push_then_dedupe(self, antifake_path, *_mocks):
        sent, deduped = scam.maybe_notify_parents_money_or_code(member_user_id=7)
        self.assertEqual(sent, 1)
        self.assertFalse(deduped)
        sent2, deduped2 = scam.maybe_notify_parents_money_or_code(member_user_id=7)
        self.assertEqual(sent2, 0)
        self.assertTrue(deduped2)
        antifake_path.assert_not_called()

    @patch("app.services.elderly_scam_call_notify._send_apns_sync", return_value=False)
    @patch("app.services.elderly_scam_call_notify.get_push_tokens", return_value=["tok"])
    @patch("app.services.elderly_scam_call_notify.get_parent_user_ids", return_value=[2])
    @patch("app.services.elderly_scam_call_notify.member_display_name", return_value=None)
    def test_failed_send_can_be_retried(self, *_mocks):
        sent, deduped = scam.maybe_notify_parents_money_or_code(member_user_id=8)
        self.assertEqual(sent, 0)
        self.assertFalse(deduped)
        self.assertNotIn(8, scam._last_push_by_member)


if __name__ == "__main__":
    unittest.main()
