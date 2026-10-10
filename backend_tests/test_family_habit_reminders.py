"""fws-02 family habit reminders tests."""
from __future__ import annotations

import sys
import unittest

if "sqlalchemy" not in sys.modules:
    import unittest.mock as mock

    sqlalchemy_mock = mock.MagicMock()
    sys.modules["sqlalchemy"] = sqlalchemy_mock
    sys.modules["sqlalchemy.text"] = mock.MagicMock()

sys.modules.setdefault("app.database.database", __import__("unittest.mock", fromlist=["MagicMock"]).MagicMock())

from app.services import family_habit_reminders_store as habits  # noqa: E402


class FamilyHabitRemindersStoreTests(unittest.TestCase):
    def test_normalize_defaults(self):
        cfg = habits.normalize_config(None)
        self.assertIn("water", cfg["presets"])
        self.assertFalse(cfg["presets"]["water"]["enabled"])
        # p1-7a
        self.assertFalse(cfg["presets"]["water"]["ping_until_done"])
        self.assertEqual(cfg["presets"]["water"]["ping_interval_minutes"], 20)
        self.assertEqual(cfg["presets"]["water"]["ping_max_per_day"], 6)

    def test_clamp_schedule(self):
        cfg = habits.normalize_config(
            {"presets": {"water": {"enabled": True, "hour": 99, "minute": -3}}}
        )
        self.assertEqual(cfg["presets"]["water"]["hour"], 23)
        self.assertEqual(cfg["presets"]["water"]["minute"], 0)
        self.assertEqual(cfg["presets"]["water"]["daily_liters"], 2.0)
        self.assertEqual(cfg["presets"]["water"]["interval_minutes"], 120)
        self.assertFalse(cfg["presets"]["water"]["ping_until_done"])

    def test_ping_fields_clamp(self):
        cfg = habits.normalize_config(
            {
                "presets": {
                    "phone_down": {
                        "enabled": True,
                        "hour": 21,
                        "minute": 0,
                        "ping_until_done": True,
                        "ping_interval_minutes": 7,
                        "ping_max_per_day": 99,
                    }
                }
            }
        )
        pd = cfg["presets"]["phone_down"]
        self.assertTrue(pd["ping_until_done"])
        self.assertEqual(pd["ping_interval_minutes"], 15)
        self.assertEqual(pd["ping_max_per_day"], 12)

    def test_medicine_defaults(self):
        cfg = habits.normalize_config(None)
        med = cfg["presets"]["medicine"]
        self.assertFalse(med["enabled"])
        self.assertEqual(med["hour"], 9)
        self.assertTrue(med["ping_until_done"])
        self.assertEqual(med["ping_interval_minutes"], 20)
        self.assertEqual(med["ping_max_per_day"], 6)

    def test_water_extended_fields(self):
        cfg = habits.normalize_config(
            {
                "presets": {
                    "water": {
                        "enabled": True,
                        "hour": 9,
                        "minute": 0,
                        "end_hour": 21,
                        "end_minute": 0,
                        "interval_minutes": 95,
                        "daily_liters": 1.7,
                    }
                }
            }
        )
        water = cfg["presets"]["water"]
        self.assertEqual(water["interval_minutes"], 90)
        self.assertEqual(water["daily_liters"], 1.5)

    def test_if_then_sync_lines(self):
        cfg = habits.normalize_config(
            {
                "presets": {
                    "water": {"enabled": True, "hour": 10, "minute": 30},
                    "phone_down": {"enabled": False, "hour": 21, "minute": 0},
                }
            }
        )
        lines = habits.if_then_lines_for_sync(cfg)
        self.assertEqual(len(lines), 1)
        self.assertIn("10:30", lines[0])

    # --- fhc-07 custom[] ---

    def test_legacy_without_custom_is_empty_list(self):
        cfg = habits.normalize_config(
            {"presets": {"water": {"enabled": True, "hour": 10, "minute": 0}}}
        )
        self.assertEqual(cfg["custom"], [])
        self.assertIn("water", cfg["presets"])
        self.assertTrue(cfg["presets"]["water"]["enabled"])

    def test_custom_normalize_max_five_and_clamp(self):
        items = []
        for i in range(8):
            items.append(
                {
                    "id": f"c{i}",
                    "title": f"Item {i}",
                    "emoji": "📞",
                    "enabled": True,
                    "mode": "once_daily",
                    "hour": 99,
                    "minute": -1,
                    "interval_minutes": 5,
                    "sort_order": i,
                }
            )
        cfg = habits.normalize_config({"presets": {}, "custom": items})
        self.assertEqual(len(cfg["custom"]), 5)
        self.assertEqual(cfg["custom"][0]["hour"], 23)
        self.assertEqual(cfg["custom"][0]["minute"], 0)
        self.assertEqual(cfg["custom"][0]["interval_minutes"], 15)

    def test_custom_empty_title_dropped(self):
        cfg = habits.normalize_config(
            {
                "custom": [
                    {"id": "a", "title": "   ", "mode": "window"},
                    {"id": "b", "title": "Call mom", "mode": "once_daily", "hour": 20},
                ]
            }
        )
        self.assertEqual(len(cfg["custom"]), 1)
        self.assertEqual(cfg["custom"][0]["id"], "b")
        self.assertEqual(cfg["custom"][0]["title"], "Call mom")

    def test_custom_unknown_mode_kept_disabled(self):
        cfg = habits.normalize_config(
            {
                "custom": [
                    {
                        "id": "x",
                        "title": "Weird",
                        "mode": "weekly_rrule",
                        "enabled": True,
                        "hour": 10,
                        "minute": 0,
                    }
                ]
            }
        )
        self.assertEqual(len(cfg["custom"]), 1)
        self.assertEqual(cfg["custom"][0]["mode"], "weekly_rrule")
        self.assertFalse(cfg["custom"][0]["enabled"])

    def test_custom_once_at_and_fire_at(self):
        cfg = habits.normalize_config(
            {
                "custom": [
                    {
                        "id": "d1",
                        "title": "Tuesday",
                        "mode": "once_at",
                        "enabled": True,
                        "fire_at": "2026-10-14T18:00:00Z",
                        "hour": 18,
                        "minute": 0,
                    }
                ]
            }
        )
        self.assertEqual(cfg["custom"][0]["mode"], "once_at")
        self.assertTrue(cfg["custom"][0]["enabled"])
        self.assertEqual(cfg["custom"][0]["fire_at"], "2026-10-14T18:00:00Z")

    def test_custom_title_length_clamp(self):
        long_title = "a" * 80
        cfg = habits.normalize_config(
            {"custom": [{"title": long_title, "mode": "window", "interval_minutes": 60}]}
        )
        self.assertEqual(len(cfg["custom"][0]["title"]), 40)


if __name__ == "__main__":
    unittest.main()
