# -*- coding: utf-8 -*-
"""Where-phone family snapshot: one Apple Maps link, child sees only self."""

from __future__ import annotations

import unittest

from app.services.family_where_phone_rules import map_url_ok, rows_for_viewer


class FamilyWherePhoneRulesTests(unittest.TestCase):
    def test_apple_maps_link_ok(self):
        self.assertTrue(map_url_ok("https://maps.apple.com/?ll=53.200000,50.150000"))

    def test_other_hosts_rejected(self):
        self.assertFalse(map_url_ok("https://maps.google.com/?ll=1,2"))
        self.assertFalse(map_url_ok("http://maps.apple.com/?ll=1,2"))
        self.assertFalse(map_url_ok("https://maps.apple.com/?q=home"))
        self.assertFalse(map_url_ok("https://maps.apple.com/?ll=99,10"))

    def test_child_sees_only_own_row(self):
        rows = [
            {"member_id": "MEM_CHILD", "display_name": "Маша"},
            {"member_id": "MEM_PARENT", "display_name": "Папа"},
        ]
        self.assertEqual(
            rows_for_viewer(rows, "child", "MEM_CHILD"),
            [{"member_id": "MEM_CHILD", "display_name": "Маша"}],
        )
        self.assertEqual(
            rows_for_viewer(rows, "teenager", "MEM_CHILD"),
            [{"member_id": "MEM_CHILD", "display_name": "Маша"}],
        )

    def test_parent_sees_every_row(self):
        rows = [
            {"member_id": "MEM_CHILD"},
            {"member_id": "MEM_PARENT"},
        ]
        self.assertEqual(len(rows_for_viewer(rows, "parent", "MEM_PARENT")), 2)


if __name__ == "__main__":
    unittest.main()
