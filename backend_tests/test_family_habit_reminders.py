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


if __name__ == "__main__":
    unittest.main()
