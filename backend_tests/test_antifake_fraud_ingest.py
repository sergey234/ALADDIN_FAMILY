"""C-04 fraud ingest tests."""
from __future__ import annotations

import sys
import unittest
from unittest.mock import MagicMock, patch

if "sqlalchemy" not in sys.modules:
    sqlalchemy_mock = MagicMock()
    sys.modules["sqlalchemy"] = sqlalchemy_mock
    sys.modules["sqlalchemy.text"] = MagicMock()

sys.modules.setdefault("app.database.database", MagicMock())

from app.services import antifake_fraud_ingest as ingest  # noqa: E402


class AntifakeFraudIngestTests(unittest.TestCase):
    @patch("app.services.antifake_fraud_ingest.upsert_number", return_value=True)
    def test_ingest_call_likely_fake(self, mock_upsert):
        ok = ingest.maybe_ingest_from_call_verdict(
            {"verdict": "likely_fake", "confidence": 0.9},
            caller_id="+7 495 123-45-67",
            display_name="Bank",
        )
        self.assertTrue(ok)
        mock_upsert.assert_called_once()

    @patch("app.services.antifake_fraud_ingest.upsert_number", return_value=True)
    def test_skip_uncertain(self, mock_upsert):
        ok = ingest.maybe_ingest_from_call_verdict(
            {"verdict": "uncertain", "confidence": 0.5},
            caller_id="79001234567",
        )
        self.assertFalse(ok)
        mock_upsert.assert_not_called()

    @patch("app.services.antifake_fraud_ingest.upsert_number", return_value=True)
    def test_report_ingest(self, mock_upsert):
        ok = ingest.ingest_from_report(phone="78005553535", label="Scam")
        self.assertTrue(ok)


if __name__ == "__main__":
    unittest.main()
