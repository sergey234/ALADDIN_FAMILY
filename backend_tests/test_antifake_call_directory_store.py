"""C-07: antifake_call_directory_store contract tests."""
from __future__ import annotations

import sys
import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

# Allow import without SQLAlchemy installed in bare CI shells.
if "sqlalchemy" not in sys.modules:
    sqlalchemy_mock = MagicMock()
    sys.modules["sqlalchemy"] = sqlalchemy_mock
    sys.modules["sqlalchemy.text"] = MagicMock()

sys.modules.setdefault("app.database.database", MagicMock())

from app.services import antifake_call_directory_store as store  # noqa: E402


class AntifakeCallDirectoryStoreTests(unittest.TestCase):
    def test_normalize_phone(self):
        self.assertEqual(store._normalize_phone("+7 (495) 123-45-67"), "74951234567")
        self.assertIsNone(store._normalize_phone("123"))

    def test_phone_log_hash(self):
        h1 = store.phone_log_hash("74951234567")
        h2 = store.phone_log_hash("74951234567")
        self.assertEqual(h1, h2)
        self.assertNotIn("7495", h1)

    def test_ru_v1_csv_exists_for_c08(self):
        self.assertTrue(store._RU_V1_CSV.is_file(), "C-08 CSV missing")
        with store._RU_V1_CSV.open(encoding="utf-8") as handle:
            lines = handle.readlines()
        self.assertGreaterEqual(len(lines), store.MIN_RU_SEED_COUNT + 1)

    @patch("app.services.antifake_call_directory_store.ensure_table")
    @patch("app.services.antifake_call_directory_store.engine")
    def test_payload_shape(self, mock_engine, _ensure):
        conn = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = conn

        execute_results = [
            MagicMock(
                mappings=MagicMock(
                    return_value=MagicMock(
                        all=MagicMock(
                            return_value=[
                                {"phone_e164": "74951234567", "label": None, "block": False, "updated_at": None},
                                {"phone_e164": "78005553535", "label": None, "block": False, "updated_at": None},
                                {"phone_e164": "79990001122", "label": "Scam", "block": True, "updated_at": None},
                            ]
                        )
                    )
                )
            ),
            MagicMock(scalar=MagicMock(return_value=3)),
            MagicMock(scalar=MagicMock(return_value=None)),
        ]
        conn.execute.side_effect = execute_results

        payload = store.get_call_directory_payload()

        self.assertIn("identified", payload)
        self.assertIn("blocked", payload)
        self.assertIn("total_count", payload)
        self.assertIn("updated_at", payload)
        self.assertIn("truncated", payload)
        self.assertIn("max_entries", payload)
        self.assertEqual(len(payload["identified"]), 2)
        self.assertEqual(payload["blocked"], ["79990001122"])

    @patch("app.services.antifake_call_directory_store.ensure_table")
    @patch("app.services.antifake_call_directory_store.engine")
    def test_since_delta_query(self, mock_engine, _ensure):
        conn = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = conn
        conn.execute.side_effect = [
            MagicMock(mappings=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))),
            MagicMock(scalar=MagicMock(return_value=113)),
            MagicMock(scalar=MagicMock(return_value=None)),
        ]

        since = datetime(2026, 6, 1, tzinfo=timezone.utc)
        payload = store.get_call_directory_payload(since=since)

        first_params = conn.execute.call_args_list[0][0][1]
        self.assertIn("since", first_params)
        self.assertEqual(payload["total_count"], 113)
        self.assertEqual(payload["identified"], [])

    def test_qa_numbers_in_csv(self):
        """C-11: QA phones ship in bundled CSV with source=qa."""
        with store._RU_V1_CSV.open(encoding="utf-8") as handle:
            import csv

            rows = list(csv.DictReader(handle))
        qa_rows = [r for r in rows if (r.get("source") or "") == "qa"]
        phones = {store._normalize_phone(r.get("phone") or "") for r in qa_rows}
        self.assertTrue(store._QA_PHONES_FOR_DEVICE_QA.issubset(phones))


if __name__ == "__main__":
    unittest.main()
