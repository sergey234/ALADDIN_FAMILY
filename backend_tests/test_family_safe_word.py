"""fws-01 family safe-word tests."""
from __future__ import annotations

import sys
import unittest
from unittest.mock import patch

if "sqlalchemy" not in sys.modules:
    import unittest.mock as mock

    sqlalchemy_mock = mock.MagicMock()
    sys.modules["sqlalchemy"] = sqlalchemy_mock
    sys.modules["sqlalchemy.text"] = mock.MagicMock()

sys.modules.setdefault("app.database.database", __import__("unittest.mock", fromlist=["MagicMock"]).MagicMock())

from app.services import family_safe_word_crypto as crypto  # noqa: E402
from app.services import family_safe_word_notify as notify  # noqa: E402


class FamilySafeWordCryptoTests(unittest.TestCase):
    def test_normalize_and_verify(self):
        salt, digest = crypto.hash_phrase("  Blue   Moon  ")
        self.assertTrue(crypto.verify_phrase("blue moon", salt, digest))
        self.assertFalse(crypto.verify_phrase("red sun", salt, digest))

    def test_validate_min_four_chars_one_word_ok(self):
        self.assertEqual(crypto.validate_phrase("x"), "phrase_too_short")
        self.assertEqual(crypto.validate_phrase("abc"), "phrase_too_short")
        self.assertIsNone(crypto.validate_phrase("волк"))
        self.assertIsNone(crypto.validate_phrase("серый волк"))
        self.assertIsNone(crypto.validate_phrase("blue moon"))


class FamilySafeWordNotifyTests(unittest.TestCase):
    @patch("app.services.family_safe_word_notify.get_push_tokens", return_value=[])
    @patch("app.services.family_safe_word_notify.get_parent_user_ids", return_value=[2])
    def test_cooldown_blocks_second_push(self, *_mocks):
        notify._last_push_by_member.clear()
        first = notify.maybe_notify_parents_safe_word_mismatch(
            member_user_id=1,
            family_id="FAM_test",
        )
        second = notify.maybe_notify_parents_safe_word_mismatch(
            member_user_id=1,
            family_id="FAM_test",
        )
        self.assertEqual(first, 0)
        self.assertEqual(second, 0)

    @patch("app.services.family_safe_word_notify._send_apns_sync", return_value=True)
    @patch("app.services.family_safe_word_notify.get_push_tokens", return_value=["abc"])
    @patch("app.services.family_safe_word_notify.get_parent_user_ids", return_value=[2])
    def test_notify_parents(self, *_mocks):
        notify._last_push_by_member.clear()
        sent = notify.maybe_notify_parents_safe_word_mismatch(
            member_user_id=1,
            family_id="FAM_test",
        )
        self.assertEqual(sent, 1)


if __name__ == "__main__":
    unittest.main()
