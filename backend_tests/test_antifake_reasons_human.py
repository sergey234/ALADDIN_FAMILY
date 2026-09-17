"""Unit tests for antifake reasons_human SSOT (TI-UX-01)."""
from __future__ import annotations

import unittest

from app.services.antifake_reason_i18n import (
    attach_human_reasons,
    humanize_reasons,
    resolve_ui_lang_from_headers,
)


class ReasonI18nTests(unittest.TestCase):
    def test_known_codes_ru_en(self):
        ru = humanize_reasons(["fuzzy_typosquat", "feed_known_phishing_domain"], lang="ru")
        en = humanize_reasons(["fuzzy_typosquat", "feed_known_phishing_domain"], lang="en")
        self.assertEqual(len(ru), 2)
        self.assertEqual(len(en), 2)
        self.assertIn("подделка", ru[0].lower())
        self.assertIn("fake", en[0].lower())
        self.assertNotIn("fuzzy_typosquat", " ".join(ru))
        self.assertNotIn("feed_known", " ".join(en))

    def test_unknown_code_no_snake_case(self):
        # Unknown machine codes are skipped (not shown as snake_case to families).
        out = humanize_reasons(["totally_unknown_machine_code"], lang="ru")
        self.assertEqual(out, [])
        # Known codes still humanize without underscores
        known = humanize_reasons(["urgency"], lang="ru")
        self.assertEqual(len(known), 1)
        self.assertNotIn("_", known[0])

    def test_ensemble_tagged_reason(self):
        out = humanize_reasons(["sfm:urgency"], lang="ru")
        self.assertTrue(any("срочн" in x.lower() for x in out))

    def test_attach_refreshes_language(self):
        payload = {"verdict": "likely_fake", "reasons": ["scam"], "reasons_human": ["old"]}
        en = attach_human_reasons(payload, lang="en")
        self.assertTrue(any("money" in x.lower() or "scam" in x.lower() for x in en["reasons_human"]))

    def test_resolve_lang_accept_language(self):
        self.assertEqual(
            resolve_ui_lang_from_headers(accept_language="en-US,en;q=0.9"),
            "en",
        )
        self.assertEqual(
            resolve_ui_lang_from_headers(accept_language="ru-RU,ru;q=0.9,en;q=0.8"),
            "ru",
        )
        self.assertEqual(
            resolve_ui_lang_from_headers(x_aladdin_lang="en"),
            "en",
        )
        self.assertEqual(
            resolve_ui_lang_from_headers(query_lang="en-GB"),
            "en",
        )


if __name__ == "__main__":
    unittest.main()
