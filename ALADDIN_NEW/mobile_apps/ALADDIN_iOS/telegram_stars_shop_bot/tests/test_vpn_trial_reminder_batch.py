from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from bot.services.vpn_expiry_notify import run_vpn_expiry_notify_batch
from bot.services.vpn_trial_reminder import (
    KIND_TRIAL_D1,
    KIND_TRIAL_H6,
    KIND_TRIAL_EXPIRED,
    run_vpn_trial_reminder_batch,
    trial_kind_for_hours_left,
)


def test_trial_kind_windows() -> None:
    assert trial_kind_for_hours_left(24.0) == KIND_TRIAL_D1
    assert trial_kind_for_hours_left(5.0) == KIND_TRIAL_H6
    assert trial_kind_for_hours_left(12.0) is None
    assert trial_kind_for_hours_left(1.0) is None


@pytest.mark.asyncio
async def test_expiry_notify_skips_trial_expired_for_trial_users(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    import aiosqlite

    from bot.config import Settings

    vpn_db = tmp_path / "vpn.db"
    shop_db = tmp_path / "shop.db"
    future = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()

    async with aiosqlite.connect(vpn_db) as db:
        await db.execute(
            """
            CREATE TABLE vpn_accounts (
                telegram_user_id INTEGER PRIMARY KEY,
                status TEXT,
                paid_until TEXT,
                trial_used_at TEXT,
                account_kind TEXT
            )
            """
        )
        await db.execute(
            "INSERT INTO vpn_accounts VALUES (1, 'vpn_expired', ?, '2026-07-01', 'trial')",
            (past,),
        )
        await db.execute(
            "INSERT INTO vpn_accounts VALUES (2, 'vpn_expired', ?, NULL, 'paid')",
            (past,),
        )
        await db.execute(
            "INSERT INTO vpn_accounts VALUES (3, 'vpn_active', ?, NULL, 'paid')",
            (future,),
        )
        await db.commit()

    settings = Settings(
        BOT_TOKEN="x",
        VPN_API_HMAC_SECRET="sec",
        DATABASE_PATH=str(shop_db),
        VPN_DB_PATH=str(vpn_db),
        VPN_EXPIRY_NOTIFY_ENABLED=True,
    )

    bot = MagicMock()
    bot.send_message = AsyncMock()

    sent_paid = await run_vpn_expiry_notify_batch(bot, settings)
    assert sent_paid == 1
    assert bot.send_message.await_count == 1
    tid = bot.send_message.await_args_list[0].args[0]
    assert tid == 2


@pytest.mark.asyncio
async def test_trial_reminder_sends_h6_and_expired(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    import aiosqlite

    from bot.config import Settings

    vpn_db = tmp_path / "vpn.db"
    shop_db = tmp_path / "shop.db"
    now = datetime.now(timezone.utc).replace(microsecond=0)
    h6_until = (now + timedelta(hours=5)).isoformat()
    past = (now - timedelta(hours=2)).isoformat()

    async with aiosqlite.connect(vpn_db) as db:
        await db.execute(
            """
            CREATE TABLE vpn_accounts (
                telegram_user_id INTEGER PRIMARY KEY,
                status TEXT,
                paid_until TEXT,
                trial_used_at TEXT,
                account_kind TEXT
            )
            """
        )
        await db.execute(
            """
            INSERT INTO vpn_accounts VALUES
            (101, 'vpn_active', ?, '2026-07-08', 'trial'),
            (102, 'vpn_expired', ?, '2026-07-07', 'trial'),
            (990100005, 'vpn_active', ?, '2026-07-08', 'trial')
            """,
            (h6_until, past, h6_until),
        )
        await db.commit()

    settings = Settings(
        BOT_TOKEN="x",
        VPN_API_HMAC_SECRET="sec",
        DATABASE_PATH=str(shop_db),
        VPN_DB_PATH=str(vpn_db),
        VPN_TRIAL_ENABLED=True,
    )

    bot = MagicMock()
    bot.send_message = AsyncMock()

    sent = await run_vpn_trial_reminder_batch(bot, settings)
    assert sent == 2
    assert bot.send_message.await_count == 2
    tids = {call.args[0] for call in bot.send_message.await_args_list}
    assert tids == {101, 102}
    # friend seed must not be notified
    assert 990100005 not in tids


@pytest.mark.asyncio
async def test_trial_reminder_sends_d1(tmp_path) -> None:
    import aiosqlite

    from bot.config import Settings

    vpn_db = tmp_path / "vpn.db"
    shop_db = tmp_path / "shop.db"
    now = datetime.now(timezone.utc).replace(microsecond=0)
    d1_until = (now + timedelta(hours=24)).isoformat()

    async with aiosqlite.connect(vpn_db) as db:
        await db.execute(
            """
            CREATE TABLE vpn_accounts (
                telegram_user_id INTEGER PRIMARY KEY,
                status TEXT,
                paid_until TEXT,
                trial_used_at TEXT,
                account_kind TEXT
            )
            """
        )
        await db.execute(
            "INSERT INTO vpn_accounts VALUES (201, 'vpn_active', ?, '2026-07-08', 'trial')",
            (d1_until,),
        )
        await db.commit()

    settings = Settings(
        BOT_TOKEN="x",
        VPN_API_HMAC_SECRET="sec",
        DATABASE_PATH=str(shop_db),
        VPN_DB_PATH=str(vpn_db),
        VPN_TRIAL_ENABLED=True,
    )
    bot = MagicMock()
    bot.send_message = AsyncMock()
    sent = await run_vpn_trial_reminder_batch(bot, settings)
    assert sent == 1
    text = bot.send_message.await_args_list[0].args[1]
    assert "1 день" in text
