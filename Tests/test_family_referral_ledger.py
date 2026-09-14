"""Unit tests: Family Invite Pro ledger helpers (no SQLAlchemy required)."""

from __future__ import annotations

import unittest

from app.services.family_referral_ledger import progress_for_qualified, soft_device_hash


class FamilyReferralLedgerHelpersTests(unittest.TestCase):
    def test_soft_device_hash_stable(self):
        a = soft_device_hash("device-abc")
        b = soft_device_hash("device-abc")
        self.assertEqual(a, b)
        self.assertEqual(len(a or ""), 32)
        self.assertIsNone(soft_device_hash(None))
        self.assertIsNone(soft_device_hash(""))

    def test_progress_thresholds(self):
        self.assertEqual(progress_for_qualified(0)["next_tier_at"], 1)
        self.assertEqual(progress_for_qualified(1)["next_tier_at"], 3)
        self.assertEqual(progress_for_qualified(2)["remaining"], 1)
        self.assertEqual(progress_for_qualified(3)["next_tier_at"], 5)
        self.assertEqual(progress_for_qualified(5)["next_tier_at"], 10)
        self.assertIsNone(progress_for_qualified(10)["next_tier_at"])
        self.assertEqual(progress_for_qualified(10)["remaining"], 0)


if __name__ == "__main__":
    unittest.main()
