# -*- coding: utf-8 -*-
"""hero-x-51 — vedic wisdom gated by parent consent."""

import unittest

from security.services.ai_platform.consent_resolver import normalize_parent_consent


class CompanionConsentWisdomTests(unittest.TestCase):
    def test_normalize_default_vedic_on(self):
        consent = normalize_parent_consent(None)
        self.assertTrue(consent.get("vedic_wisdom_enabled"))

    def test_normalize_respects_false(self):
        consent = normalize_parent_consent({"vedic_wisdom_enabled": False})
        self.assertFalse(consent["vedic_wisdom_enabled"])

    def test_backward_compat_missing_field(self):
        consent = normalize_parent_consent(
            {"memory_enabled": True, "child_can_use_companion": True}
        )
        self.assertTrue(consent.get("vedic_wisdom_enabled"))


if __name__ == "__main__":
    unittest.main()
