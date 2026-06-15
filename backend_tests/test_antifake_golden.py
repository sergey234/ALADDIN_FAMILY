"""F-08: golden test set RU/EN — heuristic contract (no mock sources)."""
from __future__ import annotations

import sys
import unittest
from unittest.mock import patch

if "sqlalchemy" not in sys.modules:
    from unittest.mock import MagicMock

    sys.modules["sqlalchemy"] = MagicMock()
    sys.modules["sqlalchemy.text"] = MagicMock()

from app.services.antifake_service import FORBIDDEN_SOURCES, check_text, check_url  # noqa: E402


GOLDEN_TEXT_RU = [
    ("шокирующая правда act now переведите деньги срочно they don't want you to know", "likely_fake"),
    ("Обычная погода в Москве завтра", "likely_real"),
]

GOLDEN_TEXT_EN = [
    ("act now send money immediately shocking truth they don't want you to know", "likely_fake"),
    ("Weekly weather forecast for London", "likely_real"),
]

GOLDEN_URL = [
    ("http://login-secure.evil-bank.ru.com/verify-account", "likely_fake"),
    ("https://www.wikipedia.org/", "likely_real"),
]


class AntifakeGoldenTests(unittest.TestCase):
    @patch("app.services.antifake_service._sfm_execute")
    def test_golden_text_ru(self, mock_sfm):
        mock_sfm.return_value = {"success": False, "error": "offline"}
        for text, expected in GOLDEN_TEXT_RU:
            out = check_text(text)
            self.assertIn(out["verdict"], ("likely_fake", "uncertain", "likely_real"))
            self.assertNotIn(out.get("source"), FORBIDDEN_SOURCES)
            if expected == "likely_fake":
                self.assertEqual(out["verdict"], "likely_fake", msg=text)
            if expected == "likely_real":
                self.assertIn(out["verdict"], ("likely_real", "uncertain"))

    @patch("app.services.antifake_service._sfm_execute")
    def test_golden_text_en(self, mock_sfm):
        mock_sfm.return_value = {"success": False, "error": "offline"}
        for text, expected in GOLDEN_TEXT_EN:
            out = check_text(text)
            self.assertNotIn(out.get("source"), FORBIDDEN_SOURCES)
            if expected == "likely_fake":
                self.assertEqual(out["verdict"], "likely_fake", msg=text)
            if expected == "likely_real":
                self.assertIn(out["verdict"], ("likely_real", "uncertain"))

    @patch("app.services.antifake_service._sfm_execute")
    def test_golden_urls(self, mock_sfm):
        mock_sfm.return_value = {"success": False, "error": "offline"}
        for url, expected in GOLDEN_URL:
            out = check_url(url)
            self.assertNotIn(out.get("source"), FORBIDDEN_SOURCES)
            if expected == "likely_fake":
                self.assertIn(out["verdict"], ("likely_fake", "uncertain"))


if __name__ == "__main__":
    unittest.main()
