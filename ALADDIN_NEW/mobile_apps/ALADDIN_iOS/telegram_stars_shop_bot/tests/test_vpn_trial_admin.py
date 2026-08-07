from __future__ import annotations

import pytest

from bot.services import vpn_admin_support_repo


def test_format_vpn_trial_status_html() -> None:
    html = vpn_admin_support_repo.format_vpn_trial_status_html(
        {
            "telegram_user_id": 123,
            "status": "vpn_active",
            "account_kind": "trial",
            "trial_used_at": "2026-07-08T00:00:00+00:00",
            "paid_until": "2026-07-09T00:00:00+00:00",
            "device_limit": 1,
            "device_binding": {
                "hwid_prefix": "abc123def456",
                "bound_at": "2026-07-08T01:00:00+00:00",
                "last_seen_at": "2026-07-08T02:00:00+00:00",
            },
        }
    )
    assert "trial" in html
    assert "abc123def456" in html
    assert "vpn_active" in html


@pytest.mark.asyncio
async def test_fetch_vpn_trial_admin_snapshot_with_device(tmp_path) -> None:
    import aiosqlite

    vpn_db = tmp_path / "vpn.db"
    async with aiosqlite.connect(vpn_db) as db:
        await db.executescript(
            """
            CREATE TABLE vpn_accounts (
                id INTEGER PRIMARY KEY,
                telegram_user_id INTEGER UNIQUE,
                status TEXT,
                paid_until TEXT,
                opaque_token TEXT,
                wg_client_tunnel_ip TEXT,
                wg_client_public_key TEXT,
                trial_used_at TEXT,
                account_kind TEXT,
                device_limit INTEGER,
                last_error TEXT,
                created_at TEXT,
                updated_at TEXT
            );
            CREATE TABLE vpn_device_bindings (
                id INTEGER PRIMARY KEY,
                telegram_user_id INTEGER UNIQUE,
                hwid_hash TEXT UNIQUE,
                bound_at TEXT,
                last_seen_at TEXT,
                user_agent TEXT
            );
            CREATE TABLE jobs (
                id INTEGER PRIMARY KEY,
                job_type TEXT,
                status TEXT,
                attempts INTEGER,
                last_error TEXT,
                created_at TEXT,
                updated_at TEXT,
                payload_json TEXT
            );
            """
        )
        await db.execute(
            """
            INSERT INTO vpn_accounts (
                id, telegram_user_id, status, paid_until, opaque_token,
                trial_used_at, account_kind, device_limit, created_at, updated_at
            ) VALUES (1, 999, 'vpn_active', '2099-01-01', 'tok', '2026-07-08', 'trial', 1, 'now', 'now')
            """
        )
        await db.execute(
            """
            INSERT INTO vpn_device_bindings (
                telegram_user_id, hwid_hash, bound_at, last_seen_at
            ) VALUES (999, 'hash1234567890abcdef', '2026-07-08', '2026-07-08')
            """
        )
        await db.commit()

    snap = await vpn_admin_support_repo.fetch_vpn_trial_admin_snapshot(vpn_db, 999)
    assert snap is not None
    assert snap["account_kind"] == "trial"
    assert snap["device_binding"]["hwid_prefix"] == "hash12345678"
