"""afhub-p1-03 — caller spoof heuristics (authority / short code / personal)."""
from __future__ import annotations

import sys
import unittest
from unittest.mock import MagicMock

if "sqlalchemy" not in sys.modules or not hasattr(sys.modules.get("sqlalchemy"), "ext"):
    sys.modules["sqlalchemy"] = MagicMock()
    sys.modules["sqlalchemy.text"] = MagicMock()
    sys.modules["sqlalchemy.ext"] = MagicMock()
    sys.modules["sqlalchemy.ext.declarative"] = MagicMock()
sys.modules.setdefault("app.database.database", MagicMock())

from app.services.antifake_service import _analyze_caller_spoof_heuristics  # noqa: E402


class TestCallSpoofHeuristics(unittest.TestCase):
    def test_bank_on_personal_mobile(self):
        reasons, score = _analyze_caller_spoof_heuristics(
            caller_id="+79001234567",
            display_name="Сбербанк",
        )
        self.assertIn("authority_label_personal_number", reasons)
        self.assertGreaterEqual(score, 0.35)

    def test_bank_on_short_code(self):
        reasons, score = _analyze_caller_spoof_heuristics(
            caller_id="900",
            display_name="Bank Security",
        )
        self.assertIn("authority_label_short_code", reasons)
        self.assertGreaterEqual(score, 0.45)

    def test_display_mismatch(self):
        reasons, score = _analyze_caller_spoof_heuristics(
            caller_id="+79001112233",
            display_name="+79009998877",
        )
        self.assertIn("display_number_mismatch", reasons)
        self.assertGreaterEqual(score, 0.35)

    def test_benign_unknown(self):
        reasons, score = _analyze_caller_spoof_heuristics(
            caller_id="+79001112233",
            display_name="Unknown",
        )
        self.assertEqual(reasons, [])
        self.assertEqual(score, 0.0)


if __name__ == "__main__":
    unittest.main()
