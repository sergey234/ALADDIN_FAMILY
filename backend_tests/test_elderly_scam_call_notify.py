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
        sent, deduped, reason = scam.maybe_notify_parents_money_or_code(member_user_id=7)
        self.assertEqual(sent, 1)
        self.assertFalse(deduped)
        self.assertEqual(reason, "sent")
        sent2, deduped2, reason2 = scam.maybe_notify_parents_money_or_code(member_user_id=7)
        self.assertEqual(sent2, 0)
        self.assertTrue(deduped2)
        self.assertEqual(reason2, "deduped")
        antifake_path.assert_not_called()

    @patch("app.services.elderly_scam_call_notify._send_apns_sync", return_value=False)
    @patch("app.services.elderly_scam_call_notify.get_push_tokens", return_value=["tok"])
    @patch("app.services.elderly_scam_call_notify.get_parent_user_ids", return_value=[2])
    @patch("app.services.elderly_scam_call_notify.member_display_name", return_value=None)
    def test_failed_send_can_be_retried(self, *_mocks):
        sent, deduped, reason = scam.maybe_notify_parents_money_or_code(member_user_id=8)
        self.assertEqual(sent, 0)
        self.assertFalse(deduped)
        self.assertEqual(reason, "push_failed")
        self.assertNotIn(8, scam._last_push_by_member)

    @patch("app.services.elderly_scam_call_notify.get_parent_user_ids", return_value=[])
    def test_no_other_parent_does_not_lock(self, _parents):
        sent, deduped, reason = scam.maybe_notify_parents_money_or_code(member_user_id=9)
        self.assertEqual((sent, deduped, reason), (0, False, "no_other_parent"))
        self.assertNotIn(9, scam._last_push_by_member)

    @patch("app.services.elderly_scam_call_notify.get_member_role", return_value="child")
    @patch("app.services.elderly_scam_call_notify.resolve_primary_family_id", return_value="fam")
    def test_child_teen_parent_and_elderly_may_send(self, _family, role_mock):
        for role in ("parent", "child", "teenager", "elderly"):
            role_mock.return_value = role
            self.assertTrue(scam.caller_has_family_role(1))
        role_mock.return_value = "guest"
        self.assertFalse(scam.caller_has_family_role(1))


if __name__ == "__main__":
    unittest.main()
