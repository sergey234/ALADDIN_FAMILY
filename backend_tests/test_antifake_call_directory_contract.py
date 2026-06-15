"""Q-03 — call-directory JSON contract (server ↔ iOS AntifakeCallDirectoryAPIResponse)."""
from __future__ import annotations

import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

if "sqlalchemy" not in sys.modules:
    sqlalchemy_mock = MagicMock()
    sys.modules["sqlalchemy"] = sqlalchemy_mock
    sys.modules["sqlalchemy.text"] = MagicMock()

sys.modules.setdefault("app.database.database", MagicMock())

from app.services import antifake_call_directory_store as store  # noqa: E402

# Mirrors Core/Security/AntifakeCallDirectorySyncService.swift CodingKeys
IOS_REQUIRED_TOP = frozenset({"identified", "blocked", "total_count", "updated_at"})
IOS_OPTIONAL_TOP = frozenset({"truncated", "max_entries"})
IOS_IDENTIFIED_KEYS = frozenset({"phone", "label"})

GOLDEN = {
    "identified": [
        {"phone": "74951234567", "label": "Possible scam?"},
        {"phone": "78005553535", "label": None},
    ],
    "blocked": ["79990001122"],
    "total_count": 113,
    "updated_at": "2026-06-15T12:00:00+00:00",
    "truncated": False,
    "max_entries": 50000,
}


def _validate_ios_contract(payload: dict) -> None:
    missing = IOS_REQUIRED_TOP - set(payload.keys())
    if missing:
        raise AssertionError(f"missing keys: {sorted(missing)}")
    if not isinstance(payload["identified"], list):
        raise AssertionError("identified must be list")
    if not isinstance(payload["blocked"], list):
        raise AssertionError("blocked must be list")
    for item in payload["identified"]:
        if not isinstance(item, dict):
            raise AssertionError("identified item must be object")
        extra = set(item.keys()) - IOS_IDENTIFIED_KEYS
        if extra:
            raise AssertionError(f"unknown identified keys: {extra}")
        if "phone" not in item:
            raise AssertionError("identified.phone required")
    for phone in payload["blocked"]:
        if not isinstance(phone, str):
            raise AssertionError("blocked entries must be strings")


class AntifakeCallDirectoryContractTests(unittest.TestCase):
    def test_golden_fixture_matches_ios_contract(self):
        _validate_ios_contract(GOLDEN)

    @patch("app.services.antifake_call_directory_store.ensure_table")
    @patch("app.services.antifake_call_directory_store.engine")
    def test_store_payload_matches_ios_contract(self, mock_engine, _ensure):
        conn = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = conn
        now = datetime.now(timezone.utc)
        conn.execute.side_effect = [
            MagicMock(
                mappings=MagicMock(
                    return_value=MagicMock(
                        all=MagicMock(
                            return_value=[
                                {
                                    "phone_e164": "74951234567",
                                    "label": "Scam",
                                    "block": False,
                                    "updated_at": now,
                                },
                                {
                                    "phone_e164": "79990001122",
                                    "label": None,
                                    "block": True,
                                    "updated_at": now,
                                },
                            ]
                        )
                    )
                )
            ),
            MagicMock(scalar=MagicMock(return_value=2)),
            MagicMock(scalar=MagicMock(return_value=now)),
        ]

        payload = store.get_call_directory_payload()
        _validate_ios_contract(payload)

    def test_roundtrip_json_encoding(self):
        raw = json.dumps(GOLDEN)
        decoded = json.loads(raw)
        _validate_ios_contract(decoded)
        self.assertEqual(decoded["total_count"], 113)


if __name__ == "__main__":
    unittest.main()
