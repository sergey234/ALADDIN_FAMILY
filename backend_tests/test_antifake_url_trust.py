"""fws-04 URL disinformation — reasons + sources contract."""
from __future__ import annotations

import sys
import unittest
from unittest.mock import MagicMock, patch

if "sqlalchemy" not in sys.modules:
    sqlalchemy_mock = MagicMock()
    sys.modules["sqlalchemy"] = sqlalchemy_mock
    sys.modules["sqlalchemy.text"] = MagicMock()
    sys.modules["sqlalchemy.ext"] = MagicMock()
    sys.modules["sqlalchemy.ext.declarative"] = MagicMock()

sys.modules.setdefault("app.database.database", MagicMock())

from app.services import antifake_url_trust as trust  # noqa: E402
from app.services.antifake_service import check_url  # noqa: E402


class AntifakeUrlTrustTests(unittest.TestCase):
    def test_phishing_url_reasons_and_sources(self):
        reasons, sources = trust.analyze_url_signals(
            "http://login-secure.evil-bank.ru.com/verify-account"
        )
        self.assertIn("url_phishing_path", reasons)
        self.assertIn("url_typosquat_tld", reasons)
        self.assertTrue(sources)
        self.assertTrue(all(s.get("url") for s in sources))

    def test_neutral_url_has_independent_source(self):
        reasons, sources = trust.analyze_url_signals("https://www.wikipedia.org/")
        self.assertEqual(reasons, ["url_looks_neutral"])
        self.assertTrue(any(s.get("id") == "independent_check" for s in sources))

    def test_edu_neutral_may_have_empty_sources(self):
        """gai-01 — честный empty: .edu без отдельного источника допустим."""
        reasons, sources = trust.analyze_url_signals("https://www.mit.edu/")
        self.assertEqual(reasons, ["url_looks_neutral"])
        self.assertEqual(sources, [])

    @patch("app.services.antifake_phishing_domains_store.lookup_url_domain", return_value=None)
    @patch("app.services.antifake_service._sfm_execute")
    @patch("app.services.antifake_security.validate_check_url", return_value="https://www.mit.edu/")
    def test_check_url_always_includes_sources_key(self, _validate, mock_sfm, _feed):
        """gai-01 — ключ sources всегда в ответе URL-проверки (даже [])."""
        mock_sfm.return_value = {"success": False, "error": "offline"}
        out = check_url("https://www.mit.edu/")
        self.assertIn("sources", out)
        self.assertIsInstance(out["sources"], list)

    @patch("app.services.antifake_phishing_domains_store.lookup_url_domain", return_value=None)
    @patch("app.services.antifake_service._sfm_execute")
    @patch("app.services.antifake_security.validate_check_url", return_value="http://bit.ly/abc123")
    def test_check_url_returns_sources(self, _validate, mock_sfm, _feed):
        mock_sfm.return_value = {"success": False, "error": "offline"}
        out = check_url("http://bit.ly/abc123")
        self.assertIn("sources", out)
        self.assertIsInstance(out["sources"], list)
        self.assertGreaterEqual(len(out["sources"]), 1)
        self.assertNotIn("pattern:", " ".join(out.get("reasons") or []))


if __name__ == "__main__":
    unittest.main()
