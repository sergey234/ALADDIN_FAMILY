"""Unit tests for trial/expire metrics collector."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from bot.services.vpn_trial_expire_metrics import collect_trial_expire_metrics


def _seed(db_path: Path) -> None:
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        """
        CREATE TABLE vpn_accounts (
            telegram_user_id INTEGER PRIMARY KEY,
            status TEXT,
            account_kind TEXT,
            paid_until TEXT,
            trial_used_at TEXT,
            xray_client_uuid TEXT
        )
        """
    )
    conn.execute(
        "INSERT INTO vpn_accounts VALUES (1,'vpn_active','trial','2099-01-01T00:00:00+00:00',"
        "'2026-01-01T00:00:00+00:00','aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa')"
    )
    conn.execute(
        "INSERT INTO vpn_accounts VALUES (2,'vpn_expired','trial','2020-01-01T00:00:00+00:00',"
        "'2020-01-01T00:00:00+00:00',NULL)"
    )
    conn.commit()
    conn.close()


def test_collect_clean(tmp_path: Path) -> None:
    db = tmp_path / "vpn.db"
    _seed(db)
    xray = tmp_path / "config.json"
    xray.write_text(
        json.dumps(
            {
                "inbounds": [
                    {
                        "protocol": "vless",
                        "tag": "t",
                        "settings": {
                            "clients": [
                                {
                                    "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                                    "email": "vpn-1",
                                },
                                {"id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb", "email": "bridge-hop"},
                            ]
                        },
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    m = collect_trial_expire_metrics(db, xray)
    assert m["trial_active"] == 1
    assert m["trial_expired"] == 1
    assert m["trial_used_at"] == 2
    assert m["overdue_active"] == 0
    assert m["expired_with_uuid"] == 0
    assert m["xray_orphan_clients"] == 0
    assert m["ok"] is True


def test_collect_detects_orphan(tmp_path: Path) -> None:
    db = tmp_path / "vpn.db"
    _seed(db)
    xray = tmp_path / "config.json"
    xray.write_text(
        json.dumps(
            {
                "inbounds": [
                    {
                        "protocol": "vless",
                        "settings": {
                            "clients": [
                                {
                                    "id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
                                    "email": "vpn-zombie",
                                }
                            ]
                        },
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    m = collect_trial_expire_metrics(db, xray)
    assert m["xray_orphan_clients"] == 1
    assert m["ok"] is False
