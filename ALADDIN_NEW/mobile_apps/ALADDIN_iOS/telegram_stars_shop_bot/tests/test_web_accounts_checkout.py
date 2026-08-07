"""Unit tests: shop accounts layer + web product catalog."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest


@pytest.mark.asyncio
async def test_accounts_web_and_telegram_link_flow():
    from bot.db.database import connect
    from bot.services import accounts_repo

    with tempfile.TemporaryDirectory() as td:
        db = Path(td) / "shop.db"
        conn = await connect(db)
        try:
            web = await accounts_repo.create_web_account(conn)
            assert web["vpn_subject_id"] < 0
            assert web.get("telegram_user_id") in (None, )
            aid = str(web["account_id"])

            tg = await accounts_repo.ensure_account_for_telegram(conn, telegram_user_id=424242)
            assert int(tg["vpn_subject_id"]) == 424242
            assert int(tg["telegram_user_id"]) == 424242

            code = await accounts_repo.issue_link_token(conn, account_id=aid, ttl_minutes=30)
            status, detail, from_subj = await accounts_repo.consume_link_token(
                conn, code=code, telegram_user_id=777001
            )
            assert status == "ok"
            assert detail == aid
            assert from_subj == int(web["vpn_subject_id"])
            linked = await accounts_repo.get_account_by_id(conn, aid)
            assert int(linked["telegram_user_id"]) == 777001

            access = await accounts_repo.issue_order_access_token(
                conn, order_id=1, account_id=aid, ttl_days=14
            )
            tok = await accounts_repo.resolve_order_access_token(conn, access)
            assert tok is not None
            assert int(tok["order_id"]) == 1
            assert tok.get("expires_at")
            age = accounts_repo.order_access_token_age_hours(tok)
            assert age is not None and age < 1.0
        finally:
            await conn.close()


@pytest.mark.asyncio
async def test_order_access_token_expired():
    from datetime import datetime, timedelta, timezone

    from bot.db.database import connect
    from bot.services import accounts_repo

    with tempfile.TemporaryDirectory() as td:
        db = Path(td) / "shop.db"
        conn = await connect(db)
        try:
            web = await accounts_repo.create_web_account(conn)
            aid = str(web["account_id"])
            raw = accounts_repo.new_access_token()
            past = (datetime.now(timezone.utc) - timedelta(days=1)).replace(microsecond=0).isoformat()
            await conn.execute(
                """
                INSERT INTO order_access_tokens (token_hash, order_id, account_id, created_at, expires_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (accounts_repo.hash_token(raw), 99, aid, past, past),
            )
            await conn.commit()
            assert await accounts_repo.resolve_order_access_token(conn, raw) is None
        finally:
            await conn.close()


@pytest.mark.asyncio
async def test_create_web_order_sets_source_and_account():
    from bot.db.database import connect
    from bot.services import accounts_repo, orders_repo

    with tempfile.TemporaryDirectory() as td:
        db = Path(td) / "shop.db"
        conn = await connect(db)
        try:
            web = await accounts_repo.create_web_account(conn)
            oid = await orders_repo.create_web_order(
                conn,
                account_id=str(web["account_id"]),
                vpn_subject_id=int(web["vpn_subject_id"]),
                product_id="vpn_30d",
                product_title="VPN 30 дней",
                rub_after=200.0,
                referrer_id=None,
                vpn_subscription_days=30,
            )
            order = await orders_repo.get_order(conn, oid)
            assert str(order["source"]) == "web"
            assert str(order["account_id"]) == str(web["account_id"])
            assert str(order["product_kind"]) == "vpn"
            assert str(order["status"]) == "pending_payment"
        finally:
            await conn.close()


def test_trial_offer_is_simple_variant_c():
    from bot.services.vpn_connect_copy import vpn_trial_offer_html

    html = vpn_trial_offer_html(None)
    assert "Нажмите «Активировать»" in html
    assert "127.0.0.1" not in html
    assert "Vless-TCP Reality" not in html
    assert "HWID" not in html
