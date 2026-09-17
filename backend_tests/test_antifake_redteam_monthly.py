"""afhub-p3-03 — monthly red-team corpus regression (mode=sms)."""
from __future__ import annotations

import sys
import unittest
from unittest.mock import MagicMock, patch

if "sqlalchemy" not in sys.modules:
    sys.modules["sqlalchemy"] = MagicMock()
    sys.modules["sqlalchemy.text"] = MagicMock()
sys.modules.setdefault("app.database.database", MagicMock())

from app.services.antifake_service import check_text  # noqa: E402
from data.antifake.golden_dataset import (  # noqa: E402
    dataset_counts,
    golden_redteam_monthly_en,
    golden_redteam_monthly_ru,
)


class AntifakeRedteamMonthlyTests(unittest.TestCase):
    def test_corpus_size(self):
        counts = dataset_counts()
        self.assertGreaterEqual(counts["redteam_monthly_ru"], 12)
        self.assertGreaterEqual(counts["redteam_monthly_en"], 12)

    @patch("app.services.antifake_service._sfm_execute")
    def test_redteam_ru_no_green(self, mock_sfm):
        mock_sfm.return_value = {"success": False, "error": "offline"}
        for text, _ in golden_redteam_monthly_ru():
            out = check_text(text, mode="sms")
            self.assertNotEqual(out["verdict"], "likely_real", msg=text[:100])
            self.assertEqual(out["verdict"], "likely_fake", msg=text[:100])

    @patch("app.services.antifake_service._sfm_execute")
    def test_redteam_en_no_green(self, mock_sfm):
        mock_sfm.return_value = {"success": False, "error": "offline"}
        for text, _ in golden_redteam_monthly_en():
            out = check_text(text, mode="sms")
            self.assertNotEqual(out["verdict"], "likely_real", msg=text[:100])
            self.assertEqual(out["verdict"], "likely_fake", msg=text[:100])


if __name__ == "__main__":
    unittest.main()
