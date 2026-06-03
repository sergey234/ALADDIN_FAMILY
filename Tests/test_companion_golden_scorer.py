# -*- coding: utf-8 -*-
"""hero-x-07 — golden conversation CI scorer (≥95% pass)."""

from __future__ import annotations

import unittest

from security.services.ai_platform.companion_golden_scorer import (
    load_golden_cases,
    run_golden_suite,
    score_golden_case,
)


class CompanionGoldenScorerTests(unittest.TestCase):
    def test_at_least_30_cases(self):
        cases = load_golden_cases()
        self.assertGreaterEqual(len(cases), 30)

    def test_golden_suite_pass_rate(self):
        report = run_golden_suite(min_pass_rate=0.95)
        if not report["ok"]:
            self.fail(
                f"Golden pass rate {report['pass_rate']:.1%} "
                f"({report['passed']}/{report['total']}). "
                f"Failed: {report['failed'][:5]}"
            )

    def test_sample_sad_no_humor(self):
        cases = {c["id"]: c for c in load_golden_cases()}
        r = score_golden_case(cases["g01_genie_sad_no_humor"])
        self.assertTrue(r.passed, r.reason)


if __name__ == "__main__":
    unittest.main()
