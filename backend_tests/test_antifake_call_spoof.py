"""af-4-05 — caller_id vs display_name spoof heuristics."""
from __future__ import annotations

import unittest

from app.services.antifake_service import (
    _analyze_caller_spoof_heuristics,
    _merge_call_spoof_into_verdict,
)


class AntifakeCallSpoofTests(unittest.TestCase):
    def test_authority_label_on_mobile_number(self):
        reasons, score = _analyze_caller_spoof_heuristics(
            caller_id="+7 916 123-45-67",
            display_name="Сбербанк",
        )
        self.assertIn("authority_label_personal_number", reasons)
        self.assertGreaterEqual(score, 0.35)

    def test_display_number_mismatch(self):
        reasons, score = _analyze_caller_spoof_heuristics(
            caller_id="74951234567",
            display_name="88005553535",
        )
        self.assertIn("display_number_mismatch", reasons)
        self.assertGreaterEqual(score, 0.35)

    def test_neutral_caller_no_spoof(self):
        reasons, score = _analyze_caller_spoof_heuristics(
            caller_id="74951234567",
            display_name="Unknown",
        )
        self.assertEqual(reasons, [])
        self.assertEqual(score, 0.0)

    def test_merge_elevates_verdict(self):
        base = {
            "verdict": "uncertain",
            "confidence": 0.2,
            "reasons": ["call_agent_unavailable"],
            "source": "rule_engine",
            "agent": "heuristic_call",
        }
        merged = _merge_call_spoof_into_verdict(
            base,
            ["authority_label_personal_number"],
            0.45,
        )
        self.assertGreaterEqual(float(merged["confidence"]), 0.45)
        self.assertIn("authority_label_personal_number", merged["reasons"])


if __name__ == "__main__":
    unittest.main()
