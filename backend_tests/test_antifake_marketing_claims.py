"""G-01 — marketing claims gate unit tests."""
from __future__ import annotations

import importlib.util
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC = importlib.util.spec_from_file_location(
    "verify_antifake_marketing_claims",
    os.path.join(ROOT, "scripts", "verify_antifake_marketing_claims.py"),
)
gate = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(gate)


class AntifakeMarketingClaimsTests(unittest.TestCase):
    def test_banned_phrase_detected(self):
        hits = []
        line = '<p>AI распознаёт фейковые звонки в реальном времени</p>'
        for rule_id, pattern in gate.BANNED:
            if pattern.search(line):
                hits.append(rule_id)
        self.assertIn("ai_fake_calls_ru", hits)

    def test_honest_line_allowed_with_skip(self):
        line = "ALADDIN не перехватывает входящие звонки автоматически"
        self.assertTrue(gate._line_allowed(line))


if __name__ == "__main__":
    unittest.main()
