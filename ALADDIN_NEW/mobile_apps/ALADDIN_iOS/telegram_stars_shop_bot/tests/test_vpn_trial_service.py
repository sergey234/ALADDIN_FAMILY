from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import pytest

from bot.services.vpn_trial_service import TrialEligibility, trial_eligibility, trial_order_id, trial_button_label, trial_feature_visible


def test_trial_order_id() -> None:
    assert trial_order_id(123) == 9_100_000_123


def test_trial_button_label_states() -> None:
    from bot.config import Settings
    from bot.services.vpn_trial_copy import vpn_trial_button_text

    settings = Settings(
        BOT_TOKEN="x",
        VPN_API_HMAC_SECRET="sec",
        VPN_TRIAL_ENABLED=True,
        VPN_API_BASE_URL="https://example.test",
        VPN_TRIAL_HOURS=72,
    )
    assert trial_button_label(settings, TrialEligibility.OK) == vpn_trial_button_text(settings)
    assert "Активировать" in trial_button_label(settings, TrialEligibility.OK)
    assert "использован" in trial_button_label(settings, TrialEligibility.ALREADY_USED)
    active_trial = {
        "status": "vpn_active",
        "paid_until": "2099-01-01T00:00:00+00:00",
        "account_kind": "trial",
    }
    assert "активен" in trial_button_label(
        settings, TrialEligibility.ALREADY_USED, account=active_trial
    ).lower()
    assert "VPN уже активен" in trial_button_label(settings, TrialEligibility.ACTIVE_SUBSCRIPTION)
    assert "позже" in trial_button_label(settings, TrialEligibility.BOT_TOO_YOUNG)


def test_trial_feature_visible_requires_api() -> None:
    from bot.config import Settings

    on = Settings(
        BOT_TOKEN="x",
        VPN_API_HMAC_SECRET="sec",
        VPN_TRIAL_ENABLED=True,
        VPN_API_BASE_URL="http://vpn.test",
    )
    off = Settings(
        BOT_TOKEN="x",
        VPN_API_HMAC_SECRET="sec",
        VPN_TRIAL_ENABLED=False,
        VPN_API_BASE_URL="http://vpn.test",
    )
    assert trial_feature_visible(on) is True
    assert trial_feature_visible(off) is False


@pytest.mark.asyncio
async def test_trial_eligibility_disabled() -> None:
    from bot.config import Settings

    settings = Settings(
        BOT_TOKEN="x",
        VPN_API_HMAC_SECRET="sec",
        VPN_TRIAL_ENABLED=False,
        VPN_API_BASE_URL="http://vpn.test",
    )
    conn = AsyncMock()
    assert await trial_eligibility(settings, conn, 1) is TrialEligibility.DISABLED


@pytest.mark.asyncio
async def test_trial_eligibility_already_used(tmp_path) -> None:
    from bot.config import Settings

    vpn_db = tmp_path / "vpn.db"
    import aiosqlite

    async with aiosqlite.connect(vpn_db) as db:
        await db.execute(
            """
            CREATE TABLE vpn_accounts (
                telegram_user_id INTEGER PRIMARY KEY,
                status TEXT,
                paid_until TEXT,
                opaque_token TEXT,
                trial_used_at TEXT,
                account_kind TEXT,
                created_at TEXT,
                updated_at TEXT
            )
            """
        )
        await db.execute(
            """
            INSERT INTO vpn_accounts (
                telegram_user_id, status, paid_until, opaque_token,
                trial_used_at, account_kind, created_at, updated_at
            ) VALUES (42, 'vpn_expired', '2020-01-01', 'tok', '2026-01-01', 'trial', datetime('now'), datetime('now'))
            """
        )
        await db.commit()

    settings = Settings(
        BOT_TOKEN="x",
        VPN_API_HMAC_SECRET="sec",
        VPN_TRIAL_ENABLED=True,
        VPN_API_BASE_URL="http://vpn.test",
        VPN_DB_PATH=str(vpn_db),
    )
    conn = AsyncMock()
    assert await trial_eligibility(settings, conn, 42) is TrialEligibility.ALREADY_USED


@pytest.mark.asyncio
async def test_trial_eligibility_active_subscription(tmp_path) -> None:
    from bot.config import Settings

    vpn_db = tmp_path / "vpn.db"
    future = (datetime.now(timezone.utc) + timedelta(days=10)).replace(microsecond=0).isoformat()
    import aiosqlite

    async with aiosqlite.connect(vpn_db) as db:
        await db.execute(
            """
            CREATE TABLE vpn_accounts (
                telegram_user_id INTEGER PRIMARY KEY,
                status TEXT,
                paid_until TEXT,
                opaque_token TEXT,
                trial_used_at TEXT,
                account_kind TEXT,
                created_at TEXT,
                updated_at TEXT
            )
            """
        )
        await db.execute(
            """
            INSERT INTO vpn_accounts (
                telegram_user_id, status, paid_until, opaque_token,
                trial_used_at, account_kind, created_at, updated_at
            ) VALUES (43, 'vpn_active', ?, 'tok', NULL, 'paid', datetime('now'), datetime('now'))
            """,
            (future,),
        )
        await db.commit()

    settings = Settings(
        BOT_TOKEN="x",
        VPN_API_HMAC_SECRET="sec",
        VPN_TRIAL_ENABLED=True,
        VPN_API_BASE_URL="http://vpn.test",
        VPN_DB_PATH=str(vpn_db),
    )
    conn = AsyncMock()
    assert await trial_eligibility(settings, conn, 43) is TrialEligibility.ACTIVE_SUBSCRIPTION
