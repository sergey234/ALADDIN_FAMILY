"""I-batch reports store tests."""
from __future__ import annotations

import sys
import unittest
from unittest.mock import MagicMock, patch

if "sqlalchemy" not in sys.modules:
    sqlalchemy_mock = MagicMock()
    sys.modules["sqlalchemy"] = sqlalchemy_mock
    sys.modules["sqlalchemy.text"] = MagicMock()

sys.modules.setdefault("app.database.database", MagicMock())

from app.services import antifake_reports_store as reports  # noqa: E402


class AntifakeReportsStoreTests(unittest.TestCase):
    @patch("app.services.antifake_reports_store.get_report")
    @patch("app.services.antifake_reports_store.ensure_table")
    @patch("app.services.antifake_reports_store.engine")
    def test_create_report_pending(self, _engine, _ensure, mock_get):
        mock_get.side_effect = [
            None,
            {
                "id": "r1",
                "phone_e164": "79001234567",
                "status": "pending",
                "report_type": "scam",
                "job_confidence": 80,
            },
        ]
        row = reports.create_report(
            user_id=1,
            phone="79001234567",
            job_id="00000000-0000-0000-0000-000000000001",
            label="Scam",
            note=None,
            report_type="scam",
            job_verdict="uncertain",
            job_confidence=80,
            auto_moderate=False,
        )
        self.assertEqual(row["status"], "pending")

    @patch("app.services.antifake_reports_store.moderate_report")
    @patch("app.services.antifake_reports_store.get_report")
    @patch("app.services.antifake_reports_store.ensure_table")
    @patch("app.services.antifake_reports_store.engine")
    def test_auto_approve_likely_fake(self, _engine, _ensure, mock_get, mock_mod):
        mock_get.side_effect = [
            None,
            {
                "id": "r2",
                "phone_e164": "79001234567",
                "status": "pending",
                "report_type": "scam",
                "job_verdict": "likely_fake",
                "job_confidence": 85,
            },
        ]
        mock_mod.return_value = {"id": "r2", "status": "approved"}
        row = reports.create_report(
            user_id=1,
            phone="+7 900 123-45-67",
            job_id="00000000-0000-0000-0000-000000000002",
            label=None,
            note=None,
            report_type="scam",
            job_verdict="likely_fake",
            job_confidence=85,
            auto_moderate=True,
        )
        self.assertEqual(row["status"], "approved")
        mock_mod.assert_called_once()

    def test_block_only_high_confidence(self):
        self.assertFalse(reports._block_for_confidence(94))
        self.assertTrue(reports._block_for_confidence(95))


if __name__ == "__main__":
    unittest.main()
