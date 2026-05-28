from __future__ import annotations

import pytest

from bot.services import orders_repo, vpn_admin_support_repo


@pytest.mark.asyncio
async def test_last_vpn_order_id_for_user_prefers_latest(conn) -> None:
    uid = 424_242
    o1 = await orders_repo.create_order(
        conn,
        user_id=uid,
        product_id="vpn_30d",
        product_title="VPN",
        payment_method="test",
        usd_base=4.0,
        rub_before=360.0,
        rub_after=360.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note=None,
        status="completed",
        product_kind="vpn",
    )
    o2 = await orders_repo.create_order(
        conn,
        user_id=uid,
        product_id="vpn_30d",
        product_title="VPN 2",
        payment_method="test",
        usd_base=4.0,
        rub_before=360.0,
        rub_after=360.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note=None,
        status="completed",
        product_kind="vpn",
    )
    await orders_repo.create_order(
        conn,
        user_id=uid,
        product_id="stars_100",
        product_title="Stars",
        payment_method="test",
        usd_base=1.0,
        rub_before=90.0,
        rub_after=90.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note=None,
        status="completed",
        product_kind="stars",
    )
    last = await orders_repo.last_vpn_order_id_for_user(conn, uid)
    assert last == o2
    assert last != o1


@pytest.mark.asyncio
async def test_last_vpn_order_id_by_product_id_prefix(conn) -> None:
    uid = 777_001
    oid = await orders_repo.create_order(
        conn,
        user_id=uid,
        product_id="vpn_30d",
        product_title="VPN",
        payment_method="test",
        usd_base=4.0,
        rub_before=360.0,
        rub_after=360.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note=None,
        status="paid",
        product_kind="",
    )
    last = await orders_repo.last_vpn_order_id_for_user(conn, uid)
    assert last == oid


@pytest.mark.asyncio
async def test_fetch_vpn_account_admin_snapshot(tmp_path) -> None:
    from aladdin_shop_vpn_api.aladdin_shop_vpn_api.db import init_schema

    p = tmp_path / "vpn_snap.db"
    await init_schema(p)
    import aiosqlite

    async with aiosqlite.connect(p) as db:
        await db.execute(
            """
            INSERT INTO vpn_accounts (
                telegram_user_id, status, paid_until, opaque_token, created_at, updated_at
            ) VALUES (900001, 'vpn_failed', '2026-01-01T00:00:00+00:00', 'tok', datetime('now'), datetime('now'))
            """
        )
        await db.execute(
            """
            INSERT INTO jobs (
                job_type, payload_json, status, idempotency_key, next_run_at, created_at, updated_at
            ) VALUES (
                'provision',
                '{"telegram_user_id":900001,"order_id":1,"paid_until":"2026-01-01T00:00:00+00:00"}',
                'failed', 'k1', datetime('now'), datetime('now'), datetime('now')
            )
            """
        )
        await db.commit()
    snap = await vpn_admin_support_repo.fetch_vpn_account_admin_snapshot(p, 900001)
    assert snap is not None
    assert snap.get("status") == "vpn_failed"
    assert len(snap.get("recent_jobs") or []) >= 1
    html = vpn_admin_support_repo.format_vpn_admin_snapshot_html(snap)
    assert "900001" in html
    assert "provision" in html
