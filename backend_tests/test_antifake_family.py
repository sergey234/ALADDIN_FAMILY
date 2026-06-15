"""L-batch family moat tests."""
from __future__ import annotations

import sys
import unittest
from unittest.mock import MagicMock, patch

if "sqlalchemy" not in sys.modules:
    sqlalchemy_mock = MagicMock()
    sys.modules["sqlalchemy"] = sqlalchemy_mock
    sys.modules["sqlalchemy.text"] = MagicMock()

sys.modules.setdefault("app.database.database", MagicMock())

from app.services import antifake_family_notify as notify  # noqa: E402
from app.services import antifake_family_store as family  # noqa: E402


class AntifakeFamilyStoreTests(unittest.TestCase):
    def test_mask_phone(self):
        self.assertEqual(family._mask_phone("79001234567"), "***4567")

    @patch("app.services.antifake_family_notify.get_push_tokens", return_value=[])
    @patch("app.services.antifake_family_notify.get_parent_user_ids", return_value=[2])
    @patch("app.services.antifake_family_notify._job_user_id", return_value=1)
    def test_skip_non_fake(self, *_mocks):
        sent = notify.maybe_notify_parents_likely_fake(
            job_id="j1",
            verdict={"verdict": "likely_real", "confidence": 0.9},
        )
        self.assertEqual(sent, 0)

    @patch("app.services.antifake_family_notify._send_apns_sync", return_value=True)
    @patch("app.services.antifake_family_notify.get_push_tokens", return_value=["abc"])
    @patch("app.services.antifake_family_notify.get_parent_user_ids", return_value=[2])
    @patch("app.services.antifake_family_notify._job_user_id", return_value=1)
    def test_notify_likely_fake(self, *_mocks):
        sent = notify.maybe_notify_parents_likely_fake(
            job_id="j2",
            verdict={"verdict": "likely_fake", "confidence": 0.88},
        )
        self.assertEqual(sent, 1)


if __name__ == "__main__":
    unittest.main()
