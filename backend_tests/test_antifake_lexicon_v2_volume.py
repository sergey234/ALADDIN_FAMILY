"""afhub lexicon_v2 — family optimum counts + weak singles + RU/EN words+phrases."""
from __future__ import annotations

import sys
import unittest
from unittest.mock import MagicMock

if "sqlalchemy" not in sys.modules:
    sys.modules["sqlalchemy"] = MagicMock()
    sys.modules["sqlalchemy.text"] = MagicMock()

from app.services.antifake_scam_intent import intent_stats  # noqa: E402
from app.services.antifake_scam_lexicon import (  # noqa: E402
    LEXICON_VERSION,
    lexicon_stats,
)
from app.services.antifake_service import _analyze_text_heuristic  # noqa: E402


class TestLexiconV2FamilyOptimum(unittest.TestCase):
    def test_version_and_volume(self):
        self.assertEqual(LEXICON_VERSION, "lexicon_v2")
        st = lexicon_stats()
        self.assertGreaterEqual(st["unique"], 150)
        self.assertLessEqual(st["unique"], 280)
        self.assertGreaterEqual(st["single_words"], 40)
        self.assertGreaterEqual(st["multiword_phrases"], 60)

    def test_intent_has_words_and_phrases(self):
        st = intent_stats()
        self.assertGreaterEqual(st["single_words"], 20)
        self.assertGreaterEqual(st["multiword_phrases"], 30)

    def test_weak_single_money_not_hard_fake(self):
        out = _analyze_text_heuristic("Где мои деньги лежат", mode="sms")
        self.assertNotEqual(out.get("verdict"), "likely_fake")

    def test_word_plus_phrase_scam(self):
        out = _analyze_text_heuristic("Срочно переведи деньги на карту", mode="sms")
        self.assertEqual(out.get("verdict"), "likely_fake")

    def test_en_word_and_phrase(self):
        out = _analyze_text_heuristic(
            "Urgent: send me money to my card right now", mode="sms"
        )
        self.assertEqual(out.get("verdict"), "likely_fake")

    def test_bank_name_alone_not_hard_fake(self):
        out = _analyze_text_heuristic("Иду в сбер за справкой", mode="sms")
        self.assertNotEqual(out.get("verdict"), "likely_fake")


if __name__ == "__main__":
    unittest.main()
