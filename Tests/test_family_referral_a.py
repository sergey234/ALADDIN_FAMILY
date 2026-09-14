"""Unit tests: Family Invite Pro (Вариант A) pure rules."""

from __future__ import annotations

import unittest

from app.services.family_referral_a import (
    FRIEND_DISCOUNT_PERCENT,
    QualifyInput,
    evaluate_qualify,
    tier_for_qualified_count,
)


class FamilyReferralATests(unittest.TestCase):
    def test_tiers(self) -> None:
        self.assertEqual(tier_for_qualified_count(1).tier.value, "bronze")
        self.assertEqual(tier_for_qualified_count(3).referrer_protection_days, 14)
        self.assertEqual(tier_for_qualified_count(10).tier.value, "platinum")

    def test_qualify_paid(self) -> None:
        r = evaluate_qualify(
            QualifyInput(
                referrer_family_id="FAM_A",
                friend_family_id="FAM_B",
                referrer_has_active_tariff=True,
                friend_has_paid=True,
                friend_active_protection_days=0,
                already_rewarded_pair=False,
                is_same_family=False,
            ),
            referrer_qualified_count_before=0,
        )
        self.assertTrue(r.ok)
        self.assertEqual(r.friend_discount_percent, FRIEND_DISCOUNT_PERCENT)
        self.assertEqual(r.referrer_days, 7)
        self.assertEqual(r.tier, "bronze")

    def test_qualify_active_14_days(self) -> None:
        r = evaluate_qualify(
            QualifyInput(
                referrer_family_id="FAM_A",
                friend_family_id="FAM_B",
                referrer_has_active_tariff=True,
                friend_has_paid=False,
                friend_active_protection_days=14,
                already_rewarded_pair=False,
                is_same_family=False,
            ),
            referrer_qualified_count_before=2,
        )
        self.assertTrue(r.ok)
        self.assertEqual(r.referrer_days, 14)  # 3rd → silver
        self.assertEqual(r.tier, "silver")

    def test_anti_self(self) -> None:
        r = evaluate_qualify(
            QualifyInput(
                referrer_family_id="FAM_A",
                friend_family_id="FAM_A",
                referrer_has_active_tariff=True,
                friend_has_paid=True,
                friend_active_protection_days=0,
                already_rewarded_pair=False,
                is_same_family=True,
            )
        )
        self.assertFalse(r.ok)
        self.assertEqual(r.reason, "anti_self_or_same_family")

    def test_pair_once(self) -> None:
        r = evaluate_qualify(
            QualifyInput(
                referrer_family_id="FAM_A",
                friend_family_id="FAM_B",
                referrer_has_active_tariff=True,
                friend_has_paid=True,
                friend_active_protection_days=0,
                already_rewarded_pair=True,
                is_same_family=False,
            )
        )
        self.assertFalse(r.ok)
        self.assertEqual(r.reason, "pair_already_rewarded")

    def test_referrer_must_be_active(self) -> None:
        r = evaluate_qualify(
            QualifyInput(
                referrer_family_id="FAM_A",
                friend_family_id="FAM_B",
                referrer_has_active_tariff=False,
                friend_has_paid=True,
                friend_active_protection_days=0,
                already_rewarded_pair=False,
                is_same_family=False,
            )
        )
        self.assertFalse(r.ok)
        self.assertEqual(r.reason, "referrer_inactive_tariff")


if __name__ == "__main__":
    unittest.main()
