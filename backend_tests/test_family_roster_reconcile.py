"""Unit tests for app.services.family_roster_reconcile."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock

from app.services.family_roster_reconcile import (
    max_family_slots_for_subscription_level,
    reconcile_sole_child_roster_for_owner,
)


class TestMaxSlots(unittest.TestCase):
    def test_defaults(self) -> None:
        self.assertEqual(max_family_slots_for_subscription_level(None), 1)
        self.assertEqual(max_family_slots_for_subscription_level(""), 1)
        self.assertEqual(max_family_slots_for_subscription_level("Trial"), 3)
        self.assertEqual(max_family_slots_for_subscription_level("family"), 6)


class TestReconcile(unittest.TestCase):
    def test_noop_when_not_owner(self) -> None:
        db = MagicMock()
        log = MagicMock()
        db.execute.side_effect = [
            MagicMock(fetchone=lambda: ("trial",)),
            MagicMock(fetchone=lambda: (999,)),
        ]
        self.assertFalse(
            reconcile_sole_child_roster_for_owner(
                db, family_id="FAM_1", actor_user_id=1, log=log
            )
        )

    def test_promotes_sole_child_when_owner_and_trial(self) -> None:
        db = MagicMock()
        log = MagicMock()
        r3 = MagicMock()
        r3.fetchall.return_value = [("MEM_A", "child", None)]
        upd = MagicMock()
        upd.rowcount = 1
        db.execute.side_effect = [
            MagicMock(fetchone=lambda: ("trial",)),
            MagicMock(fetchone=lambda: (1,)),
            r3,
            upd,
        ]

        self.assertTrue(
            reconcile_sole_child_roster_for_owner(
                db, family_id="FAM_1", actor_user_id=1, log=log
            )
        )
        db.commit.assert_called_once()
        log.info.assert_called()

    def test_skips_when_two_members(self) -> None:
        db = MagicMock()
        log = MagicMock()
        r3 = MagicMock()
        r3.fetchall.return_value = [
            ("MEM_A", "child", None),
            ("MEM_B", "child", None),
        ]
        db.execute.side_effect = [
            MagicMock(fetchone=lambda: ("trial",)),
            MagicMock(fetchone=lambda: (1,)),
            r3,
        ]
        self.assertFalse(
            reconcile_sole_child_roster_for_owner(
                db, family_id="FAM_1", actor_user_id=1, log=log
            )
        )

    def test_promotes_placeholder_child_on_free_tier(self) -> None:
        """Sole placeholder child (user_id NULL) must repair even when subscription is free."""
        db = MagicMock()
        log = MagicMock()
        r3 = MagicMock()
        r3.fetchall.return_value = [("MEM_A", "child", None)]
        upd = MagicMock()
        upd.rowcount = 1
        db.execute.side_effect = [
            MagicMock(fetchone=lambda: ("free",)),
            MagicMock(fetchone=lambda: (1,)),
            r3,
            upd,
        ]

        self.assertTrue(
            reconcile_sole_child_roster_for_owner(
                db, family_id="FAM_1", actor_user_id=1, log=log
            )
        )
        db.commit.assert_called_once()

    def test_skips_free_tier_when_row_has_user_id(self) -> None:
        db = MagicMock()
        log = MagicMock()
        r3 = MagicMock()
        r3.fetchall.return_value = [("MEM_A", "child", 42)]
        db.execute.side_effect = [
            MagicMock(fetchone=lambda: ("free",)),
            MagicMock(fetchone=lambda: (1,)),
            r3,
        ]
        self.assertFalse(
            reconcile_sole_child_roster_for_owner(
                db, family_id="FAM_1", actor_user_id=1, log=log
            )
        )


if __name__ == "__main__":
    unittest.main()
