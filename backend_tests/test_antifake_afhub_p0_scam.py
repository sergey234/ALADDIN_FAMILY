"""afhub-p0-06 — golden SMS RU/EN: money+urgency must be likely_fake (not ~27% authentic)."""
from __future__ import annotations

import unittest
from unittest.mock import patch

from app.services.antifake_scam_lexicon import (
    anti_green_verdict,
    has_urgency_and_money,
    match_lexicon_tags,
)
from app.services.antifake_service import _analyze_text_heuristic, check_text


SCAM_RU = [
    "Я скамер-переведи мне срочно деньги на карту!",
    "Я с камер. Переведи мне деньги срочно.",
    "Срочно переведи деньги на карту",
    "Переведите мне срочно на карту",
]

SCAM_EN = [
    "Send me money urgently to my card",
    "Transfer money right now to my card",
    "I'm a scammer — send money urgently!",
]

BENIGN = [
    "Привет, как дела сегодня?",
    "Hello, how was your day?",
    "Сегодня в Москве прошёл дождь.",
]


class TestAfhubP0ScamLexicon(unittest.TestCase):
    def test_match_urgency_and_money_ru(self):
        tags = match_lexicon_tags(SCAM_RU[1])
        self.assertIn("urgency", tags)
        self.assertIn("scam", tags)
        self.assertTrue(has_urgency_and_money(tags))

    def test_anti_green(self):
        v, c = anti_green_verdict("likely_real", ["rules:urgency_manipulation"], 0.27)
        self.assertEqual(v, "uncertain")
        self.assertGreaterEqual(c, 0.40)


class TestAfhubP0HeuristicSms(unittest.TestCase):
    def test_scam_ru_sms_likely_fake(self):
        for text in SCAM_RU:
            out = _analyze_text_heuristic(text, mode="sms")
            self.assertEqual(
                out.get("verdict"),
                "likely_fake",
                msg=f"RU scam should be likely_fake: {text!r} → {out}",
            )
            self.assertGreaterEqual(float(out.get("confidence") or 0), 0.72)

    def test_scam_en_sms_likely_fake(self):
        for text in SCAM_EN:
            out = _analyze_text_heuristic(text, mode="sms")
            self.assertEqual(
                out.get("verdict"),
                "likely_fake",
                msg=f"EN scam should be likely_fake: {text!r} → {out}",
            )

    def test_scam_ru_news_also_likely_fake(self):
        """Even if client forgot sms mode, urgency+money floor still fires."""
        out = _analyze_text_heuristic(SCAM_RU[0], mode="news")
        self.assertEqual(out.get("verdict"), "likely_fake")
        self.assertGreaterEqual(float(out.get("confidence") or 0), 0.85)

    def test_benign_not_hard_fake(self):
        for text in BENIGN:
            out = _analyze_text_heuristic(text, mode="sms")
            self.assertNotEqual(
                out.get("verdict"),
                "likely_fake",
                msg=f"benign must not be likely_fake: {text!r} → {out}",
            )


class TestAfhubP0EnsembleCheckText(unittest.TestCase):
    @patch("app.services.antifake_service._sfm_execute", return_value={"success": False})
    @patch("app.services.antifake_service._try_local_ml_text", return_value=None)
    def test_check_text_sms_scam(self, _local, _sfm):
        out = check_text(SCAM_RU[1], mode="sms")
        self.assertEqual(out.get("verdict"), "likely_fake")
        self.assertNotIn(out.get("source"), ("sfm_mock", "mock"))


if __name__ == "__main__":
    unittest.main()
