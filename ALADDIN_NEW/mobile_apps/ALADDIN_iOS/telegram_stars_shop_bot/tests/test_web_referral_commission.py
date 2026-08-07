"""wsref-00/03b: web VPN order with referrer → commission on completed (same as bot)."""

from __future__ import annotations

import pytest

from bot.config import load_settings
from bot.db.database import connect
from bot.services import accounts_repo, balance_repo, orders_repo, users_repo
from bot.services.order_flow import apply_completed_side_effects
from bot.services.vpn_referral_repo import ensure_my_vpn_referral_code, resolve_code_owner


def _settings(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("BOT_TOKEN", "9:webref")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "k" * 32)
    monkeypatch.setenv("USD_RUB_RATE", "75")
    return load_settings()


@pytest.mark.asyncio
async def test_web_completed_order_credits_referrer_ref_balance(tmp_path, monkeypatch):
    settings = _settings(monkeypatch)
    db = tmp_path / "web_ref.db"
    conn = await connect(db)
    try:
        referrer = 551001
        await users_repo.upsert_user(conn, user_id=referrer, username="partner", first_name="P")
        await conn.execute(
            "UPDATE users SET ref_balance_rub = 0 WHERE user_id = ?", (referrer,)
        )
        await conn.commit()
        code = await ensure_my_vpn_referral_code(conn, referrer)
        assert await resolve_code_owner(conn, code) == referrer

        web = await accounts_repo.create_web_account(
            conn, referrer_telegram_id=referrer
        )
        assert int(web["referrer_telegram_id"]) == referrer
        subject = int(web["vpn_subject_id"])
        assert subject < 0

        oid = await orders_repo.create_web_order(
            conn,
            account_id=str(web["account_id"]),
            vpn_subject_id=subject,
            product_id="vpn_7d",
            product_title="7d",
            rub_after=100.0,
            referrer_id=referrer,
            vpn_subscription_days=7,
        )
        await orders_repo.update_status(conn, oid, "paid")
        await orders_repo.update_status(conn, oid, "completed")
        await apply_completed_side_effects(conn, oid, settings)

        order = await orders_repo.get_order(conn, oid)
        assert str(order["source"]) == "web"
        assert int(order["referrer_id"]) == referrer
        assert int(order["commission_paid"]) == 1
        assert float(order["commission_rub"]) > 0
        # Start level: 15% of 100 = 15
        assert float(order["commission_rub"]) == pytest.approx(15.0)

        bal = await balance_repo.get_ref_balance(conn, referrer)
        assert bal == pytest.approx(15.0)
    finally:
        await conn.close()


@pytest.mark.asyncio
async def test_reassign_referral_on_telegram_link(tmp_path):
    from bot.services.vpn_referral_repo import (
        ensure_my_vpn_referral_code,
        reassign_referral_owner_on_telegram_link,
        resolve_code_owner,
    )

    db = tmp_path / "reassign_ref.db"
    conn = await connect(db)
    try:
        web = await accounts_repo.create_web_account(conn)
        subject = int(web["vpn_subject_id"])
        code = await ensure_my_vpn_referral_code(conn, subject)
        tg = 88001122
        await users_repo.upsert_user(conn, user_id=tg, username="tg", first_name="T")
        kept = await reassign_referral_owner_on_telegram_link(
            conn, from_subject_id=subject, to_telegram_user_id=tg
        )
        assert kept == code
        assert await resolve_code_owner(conn, code) == tg
    finally:
        await conn.close()


@pytest.mark.asyncio
async def test_web_order_without_referrer_no_commission(tmp_path, monkeypatch):
    settings = _settings(monkeypatch)
    db = tmp_path / "web_noref.db"
    conn = await connect(db)
    try:
        web = await accounts_repo.create_web_account(conn)
        oid = await orders_repo.create_web_order(
            conn,
            account_id=str(web["account_id"]),
            vpn_subject_id=int(web["vpn_subject_id"]),
            product_id="vpn_7d",
            product_title="7d",
            rub_after=50.0,
            referrer_id=None,
            vpn_subscription_days=7,
        )
        await orders_repo.update_status(conn, oid, "paid")
        await orders_repo.update_status(conn, oid, "completed")
        await apply_completed_side_effects(conn, oid, settings)
        order = await orders_repo.get_order(conn, oid)
        assert float(order["commission_rub"] or 0) == 0.0
        assert int(order["commission_paid"] or 0) == 0
        assert order["fulfillment_applied_at"] is not None
    finally:
        await conn.close()
