from __future__ import annotations

import pytest

from bot.services import orders_repo, users_repo
from bot.services.provider_mark_paid import mark_order_paid_idempotent


@pytest.mark.asyncio
async def test_mark_paid_ok_pending_payment(conn) -> None:
    await users_repo.upsert_user(conn, user_id=501, username="u", first_name="U")
    oid = await orders_repo.create_order(
        conn,
        user_id=501,
        product_id="stars_100",
        product_title="100",
        payment_method="fiat",
        usd_base=1.0,
        rub_before=100.0,
        rub_after=100.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note="@x",
        status="pending_payment",
    )
    await conn.execute("BEGIN IMMEDIATE")
    res = await mark_order_paid_idempotent(conn, order_id=oid, idempotency_key="idem-1")
    await conn.commit()
    assert res.outcome == "ok"
    assert res.previous_status == "pending_payment"
    assert res.new_status == "paid"
    row = await orders_repo.get_order(conn, oid)
    assert row is not None
    assert str(row["status"]) == "paid"


@pytest.mark.asyncio
async def test_mark_paid_duplicate_same_idempotency_key(conn) -> None:
    await users_repo.upsert_user(conn, user_id=502, username="u2", first_name="U")
    oid = await orders_repo.create_order(
        conn,
        user_id=502,
        product_id="stars_100",
        product_title="100",
        payment_method="fiat",
        usd_base=1.0,
        rub_before=100.0,
        rub_after=100.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note="@x",
        status="pending_payment",
    )
    await conn.execute("BEGIN IMMEDIATE")
    r1 = await mark_order_paid_idempotent(conn, order_id=oid, idempotency_key="idem-dup")
    await conn.commit()
    assert r1.outcome == "ok"
    await conn.execute("BEGIN IMMEDIATE")
    r2 = await mark_order_paid_idempotent(conn, order_id=oid, idempotency_key="idem-dup")
    await conn.commit()
    assert r2.outcome == "duplicate"
    assert r2.order_id == oid


@pytest.mark.asyncio
async def test_mark_paid_not_found(conn) -> None:
    await conn.execute("BEGIN IMMEDIATE")
    res = await mark_order_paid_idempotent(conn, order_id=999999, idempotency_key="idem-nf")
    await conn.commit()
    assert res.outcome == "not_found"


@pytest.mark.asyncio
async def test_mark_paid_already_terminal_refunded(conn) -> None:
    await users_repo.upsert_user(conn, user_id=505, username="u5", first_name="U")
    oid = await orders_repo.create_order(
        conn,
        user_id=505,
        product_id="stars_100",
        product_title="100",
        payment_method="fiat",
        usd_base=1.0,
        rub_before=100.0,
        rub_after=100.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note="@x",
        status="refunded",
    )
    await conn.execute("BEGIN IMMEDIATE")
    res = await mark_order_paid_idempotent(conn, order_id=oid, idempotency_key="idem-ref")
    await conn.commit()
    assert res.outcome == "already_terminal"
    assert res.previous_status == "refunded"


@pytest.mark.asyncio
async def test_mark_paid_conflict_expired(conn) -> None:
    await users_repo.upsert_user(conn, user_id=504, username="u4", first_name="U")
    oid = await orders_repo.create_order(
        conn,
        user_id=504,
        product_id="stars_100",
        product_title="100",
        payment_method="fiat",
        usd_base=1.0,
        rub_before=100.0,
        rub_after=100.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note="@x",
        status="expired",
    )
    await conn.execute("BEGIN IMMEDIATE")
    res = await mark_order_paid_idempotent(conn, order_id=oid, idempotency_key="idem-exp")
    await conn.commit()
    assert res.outcome == "conflict"
    assert res.previous_status == "expired"


@pytest.mark.asyncio
async def test_mark_paid_conflict_wrong_status(conn) -> None:
    await users_repo.upsert_user(conn, user_id=503, username="u3", first_name="U")
    oid = await orders_repo.create_order(
        conn,
        user_id=503,
        product_id="stars_100",
        product_title="100",
        payment_method="fiat",
        usd_base=1.0,
        rub_before=100.0,
        rub_after=100.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note="@x",
        status="new",
    )
    await conn.execute("BEGIN IMMEDIATE")
    res = await mark_order_paid_idempotent(conn, order_id=oid, idempotency_key="idem-badst")
    await conn.commit()
    assert res.outcome == "conflict"
    assert res.previous_status == "new"
