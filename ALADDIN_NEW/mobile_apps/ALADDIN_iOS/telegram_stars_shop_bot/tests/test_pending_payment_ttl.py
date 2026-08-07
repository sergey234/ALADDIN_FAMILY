from __future__ import annotations

import pytest

from bot.services import orders_repo, users_repo


@pytest.mark.asyncio
async def test_expire_stale_pending_payment_returns_empty_when_ttl_zero(conn) -> None:
    assert await orders_repo.expire_stale_pending_payment_orders(conn, ttl_minutes=0) == []


@pytest.mark.asyncio
async def test_expire_stale_pending_payment_updates_old_orders(conn) -> None:
    await users_repo.upsert_user(conn, user_id=9201, username="ttl", first_name="T")
    oid = await orders_repo.create_order(
        conn,
        user_id=9201,
        product_id="x",
        product_title="X",
        payment_method="fiat",
        usd_base=1.0,
        rub_before=10.0,
        rub_after=10.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note="@u",
        status="pending_payment",
    )
    await conn.execute(
        "UPDATE orders SET created_at = datetime('now', '-3 hours') WHERE id = ?",
        (oid,),
    )
    await conn.commit()
    pairs = await orders_repo.expire_stale_pending_payment_orders(conn, ttl_minutes=60)
    assert pairs == [(oid, 9201)]
    row = await orders_repo.get_order(conn, oid)
    assert row is not None
    assert str(row["status"]) == "expired"


@pytest.mark.asyncio
async def test_expire_does_not_touch_recent_pending(conn) -> None:
    await users_repo.upsert_user(conn, user_id=9202, username="ttl2", first_name="T")
    oid = await orders_repo.create_order(
        conn,
        user_id=9202,
        product_id="x",
        product_title="X",
        payment_method="fiat",
        usd_base=1.0,
        rub_before=10.0,
        rub_after=10.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note="@u",
        status="pending_payment",
    )
    pairs = await orders_repo.expire_stale_pending_payment_orders(conn, ttl_minutes=600)
    assert pairs == []
    row = await orders_repo.get_order(conn, oid)
    assert str(row["status"]) == "pending_payment"
