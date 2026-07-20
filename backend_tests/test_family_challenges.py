"""Unit tests for FamilyChallenge normalize + max 5 (p2-9h)."""
from __future__ import annotations

import sys
import unittest
import unittest.mock as mock

if "sqlalchemy" not in sys.modules:
    sqlalchemy_mock = mock.MagicMock()
    sys.modules["sqlalchemy"] = sqlalchemy_mock
    sys.modules["sqlalchemy.text"] = mock.MagicMock()

sys.modules.setdefault(
    "app.database.database",
    mock.MagicMock(),
)
sys.modules.setdefault(
    "app.services.antifake_family_store",
    mock.MagicMock(),
)

from app.services import family_challenges_store as challenges  # noqa: E402


class FamilyChallengesNormalizeTests(unittest.TestCase):
    def test_empty(self):
        cfg = challenges.normalize_payload(None)
        self.assertEqual(cfg["challenges"], [])

    def test_max_five(self):
        raw = {
            "challenges": [
                {"title": f"C{i}", "emoji": "🏁", "enabled": True} for i in range(8)
            ]
        }
        cfg = challenges.normalize_payload(raw)
        self.assertEqual(len(cfg["challenges"]), 5)

    def test_fields(self):
        cfg = challenges.normalize_payload(
            {
                "challenges": [
                    {
                        "id": "abc",
                        "title": "  10 squat  ",
                        "emoji": "💪",
                        "member_ids": ["c1", ""],
                        "enabled": False,
                        "created_by": "p1",
                    }
                ]
            }
        )
        c = cfg["challenges"][0]
        self.assertEqual(c["id"], "abc")
        self.assertEqual(c["title"], "10 squat")
        self.assertEqual(c["emoji"], "💪")
        self.assertEqual(c["member_ids"], ["c1"])
        self.assertFalse(c["enabled"])
        self.assertEqual(c["created_by"], "p1")

    def test_skips_blank_title(self):
        cfg = challenges.normalize_payload(
            {"challenges": [{"title": "  "}, {"title": "ok"}]}
        )
        self.assertEqual(len(cfg["challenges"]), 1)
        self.assertEqual(cfg["challenges"][0]["title"], "ok")


if __name__ == "__main__":
    unittest.main()
