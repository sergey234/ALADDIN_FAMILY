"""F-12: tier-2 local_ml + heuristic tune when SFM offline."""
from __future__ import annotations

import sys
import unittest
from unittest.mock import patch

if "sqlalchemy" not in sys.modules:
    from unittest.mock import MagicMock

    sys.modules["sqlalchemy"] = MagicMock()
    sys.modules["sqlalchemy.text"] = MagicMock()

from app.services.antifake_service import (  # noqa: E402
    ALLOWED_AI_SOURCES,
    _analyze_text_heuristic,
    _tier2_text_fallback,
    check_text,
)

SCAM_TEXT = (
    "шокирующая правда act now переведите деньги срочно they don't want you to know"
)


class AntifakeF12FallbackTests(unittest.TestCase):
    @patch("app.services.antifake_service._sfm_execute")
    @patch("app.services.antifake_service._try_local_ml_text")
    def test_check_text_prefers_local_ml_when_sfm_offline(self, mock_local, mock_sfm):
        mock_sfm.return_value = {"success": False, "error": "limit"}
        mock_local.return_value = {
            "verdict": "likely_fake",
            "confidence": 0.82,
            "reasons": ["sensationalism"],
            "source": "local_ml",
            "agent": "local_fake_news_detection_agent",
        }
        out = check_text(SCAM_TEXT)
        self.assertEqual(out["source"], "local_ml")
        self.assertEqual(out["verdict"], "likely_fake")

    @patch("app.services.antifake_service._try_local_ml_text", return_value=None)
    def test_heuristic_three_hits_likely_fake(self, _mock_local):
        out = _tier2_text_fallback(SCAM_TEXT)
        self.assertEqual(out["source"], "rule_engine")
        self.assertEqual(out["verdict"], "likely_fake")
        self.assertGreaterEqual(float(out["confidence"]), 0.65)

    def test_heuristic_scam_direct(self):
        out = _analyze_text_heuristic(SCAM_TEXT)
        self.assertEqual(out["verdict"], "likely_fake")

    def test_heuristic_short_neutral_insufficient_data(self):
        out = _analyze_text_heuristic("12+12=24")
        self.assertEqual(out["verdict"], "insufficient_data")
        self.assertEqual(out.get("fake_risk"), 0.0)
        self.assertIn("text_too_short", out.get("reasons", []))

    def test_normalize_local_ml_too_short_insufficient(self):
        from app.services.antifake_service import _normalize_local_ml_text_result

        out = _normalize_local_ml_text_result(
            {
                "fake_score": 0.15,
                "credibility_level": "credible",
                "pattern_hits": {},
                "structural_flags": {"too_short": True},
            },
            source="real_agent",
            agent="fake_news_detection_agent",
        )
        self.assertEqual(out["verdict"], "insufficient_data")
        self.assertEqual(out.get("fake_risk"), 0.0)

    def test_allowed_ai_sources(self):
        self.assertIn("real_agent", ALLOWED_AI_SOURCES)
        self.assertIn("local_ml", ALLOWED_AI_SOURCES)


if __name__ == "__main__":
    unittest.main()
