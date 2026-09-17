"""afhub-p1-01 — scam-intent tags separate from fake-news sensationalism."""
from __future__ import annotations

import sys
import unittest
from unittest.mock import MagicMock

if "sqlalchemy" not in sys.modules:
    sys.modules["sqlalchemy"] = MagicMock()
    sys.modules["sqlalchemy.text"] = MagicMock()

from app.services.antifake_scam_intent import (  # noqa: E402
    classify_scam_intent,
    has_payment_scam_intent,
    is_news_only_signal,
    merge_intent_into_hits,
)
from app.services.antifake_service import _analyze_text_heuristic  # noqa: E402


class TestScamIntentClassify(unittest.TestCase):
    def test_otp_authority(self):
        tags = classify_scam_intent(
            "Служба безопасности банка: назовите код из СМС"
        )
        self.assertIn("intent_otp", tags)
        self.assertIn("intent_authority", tags)
        self.assertTrue(has_payment_scam_intent(tags))

    def test_sbp_money(self):
        tags = classify_scam_intent("СБП перевод — срочно переведите на карту")
        self.assertIn("intent_sbp", tags)
        self.assertTrue(
            "intent_money_transfer" in tags or "intent_card" in tags
        )

    def test_news_sensationalism_not_payment(self):
        tags = classify_scam_intent(
            "Шокирующая правда — они скрывают, doctors hate this"
        )
        self.assertFalse(has_payment_scam_intent(tags))

    def test_merge_adds_scam_coarse(self):
        merged = merge_intent_into_hits(["urgency"], ["intent_otp"])
        self.assertIn("intent_otp", merged)
        self.assertIn("scam", merged)


class TestScamIntentHeuristic(unittest.TestCase):
    def test_otp_sms_likely_fake(self):
        out = _analyze_text_heuristic(
            "Банк: ваш счёт заблокирован, продиктуйте код подтверждения",
            mode="sms",
        )
        self.assertEqual(out.get("verdict"), "likely_fake")
        reasons = " ".join(out.get("reasons") or [])
        self.assertTrue(
            "intent_otp" in reasons or "scam" in reasons,
            msg=out,
        )

    def test_news_shock_not_hard_scam_floor(self):
        """Sensational news alone must not get money+urgency floor."""
        out = _analyze_text_heuristic(
            "Шокирующая правда: они скрывают секрет. They don't want you to know about this long article about politics and society today.",
            mode="news",
        )
        # May be uncertain/fake from sensationalism, but must not invent payment intents
        reasons = out.get("reasons") or []
        self.assertNotIn("intent_otp", reasons)
        self.assertNotIn("intent_sbp", reasons)
        self.assertFalse(is_news_only_signal(["intent_otp"]))


if __name__ == "__main__":
    unittest.main()
