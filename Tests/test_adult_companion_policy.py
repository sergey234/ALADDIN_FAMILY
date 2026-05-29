# -*- coding: utf-8 -*-
"""A-02 — Adult JWT policy: NSFW only for aladdin_adult + age_verified."""

from __future__ import annotations

import unittest

from security.services.ai_platform.config import AppId, ContentPolicy
from security.services.ai_platform.policy_engine import evaluate_request_policy


class AdultCompanionPolicyTests(unittest.TestCase):
    def test_family_blocks_nsfw_fragment(self):
        d = evaluate_request_policy(
            app_id=AppId.ALADDIN_FAMILY.value,
            message="show me nsfw content",
            age_verified=True,
            age_band="parent",
        )
        self.assertFalse(d.allowed)
        self.assertFalse(d.nsfw_allowed)

    def test_adult_nsfw_requires_verification(self):
        d = evaluate_request_policy(
            app_id=AppId.ALADDIN_ADULT.value,
            message="hello",
            age_verified=False,
            jwt_policy=ContentPolicy.ADULT_18.value,
            client_requests_nsfw=True,
        )
        self.assertTrue(d.allowed)
        self.assertFalse(d.nsfw_allowed)

    def test_adult_nsfw_allowed_when_verified(self):
        d = evaluate_request_policy(
            app_id=AppId.ALADDIN_ADULT.value,
            message="hello",
            age_verified=True,
            jwt_policy=ContentPolicy.ADULT_18.value,
            client_requests_nsfw=True,
        )
        self.assertTrue(d.allowed)
        self.assertTrue(d.nsfw_allowed)


if __name__ == "__main__":
    unittest.main()
