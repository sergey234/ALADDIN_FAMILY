"""afhub-p1-02 — redirect follow + brand lookalike (mocked network)."""
from __future__ import annotations

import sys
import unittest
from unittest.mock import MagicMock, patch

if "sqlalchemy" not in sys.modules or not hasattr(sys.modules.get("sqlalchemy"), "ext"):
    sqlalchemy_mock = MagicMock()
    sys.modules["sqlalchemy"] = sqlalchemy_mock
    sys.modules["sqlalchemy.text"] = MagicMock()
    sys.modules["sqlalchemy.ext"] = MagicMock()
    sys.modules["sqlalchemy.ext.declarative"] = MagicMock()

sys.modules.setdefault("app.database.database", MagicMock())

from app.services.antifake_reason_i18n import humanize_reasons  # noqa: E402
from app.services.antifake_url_redirect import (  # noqa: E402
    enrich_url_check_with_redirects,
    probe_redirect_chain,
)


class TestUrlRedirectSsrf(unittest.TestCase):
    def test_blocks_private_redirect_hop(self):
        with patch(
            "app.services.antifake_url_redirect._redirects_enabled",
            return_value=True,
        ):
            # First hop ok; Location → localhost must block
            class _Resp:
                status = 302
                headers = {"Location": "http://127.0.0.1/phish"}

                def getcode(self):
                    return 302

                def __enter__(self):
                    return self

                def __exit__(self, *a):
                    return False

            opener = MagicMock()
            opener.open.return_value = _Resp()
            with patch("urllib.request.build_opener", return_value=opener):
                out = probe_redirect_chain("https://example.com/go")
        self.assertTrue(out.get("blocked") or "url_redirect_blocked_hop" in out.get("reasons", []))

    def test_host_mismatch_lookalike(self):
        hops = [
            "https://bit.ly/x",
            "https://secure-sber-online.ru.com/login",
        ]

        def fake_probe(url, **kwargs):
            return {
                "hops": hops,
                "final_url": hops[-1],
                "reasons": [
                    "url_redirect_chain",
                    "url_redirect_host_mismatch",
                    "brand_lookalike_redirect",
                ],
                "blocked": False,
                "confidence_boost": 0.15,
            }

        with patch(
            "app.services.antifake_url_redirect.probe_redirect_chain",
            side_effect=fake_probe,
        ):
            analyze, reasons, conf, final = enrich_url_check_with_redirects(
                "https://bit.ly/x",
                base_reasons=[],
                base_confidence=0.1,
            )
        self.assertIn("brand_lookalike_redirect", reasons)
        self.assertGreaterEqual(conf, 0.82)
        self.assertEqual(final, hops[-1])

    def test_reasons_i18n_ru_en(self):
        ru = humanize_reasons(["brand_lookalike_redirect"], lang="ru")
        en = humanize_reasons(["brand_lookalike_redirect"], lang="en")
        self.assertTrue(ru and "бренд" in ru[0].lower())
        self.assertTrue(en and "brand" in en[0].lower())


if __name__ == "__main__":
    unittest.main()
