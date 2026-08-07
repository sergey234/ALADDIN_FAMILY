from __future__ import annotations

import os
import uuid

import pytest

from bot.config import Settings
from bot.services import api_clients_repo, balance_repo, orders_repo, users_repo


@pytest.mark.asyncio
async def test_create_topup_rejects_amount_out_of_range(conn, monkeypatch) -> None:
    monkeypatch.setenv("TOPUP_MIN_RUB", "200")
    monkeypatch.setenv("TOPUP_MAX_RUB", "1000")
    settings = Settings()
    await users_repo.upsert_user(conn, user_id=9101, username="t1", first_name="T")
    with pytest.raises(ValueError, match="topup_amount_invalid"):
        await balance_repo.create_topup_request(
            conn, user_id=9101, amount_rub=150.0, settings=settings
        )


@pytest.mark.asyncio
async def test_create_topup_pending_cap(conn, monkeypatch) -> None:
    monkeypatch.setenv("TOPUP_MAX_PENDING_PER_USER", "2")
    settings = Settings()
    await users_repo.upsert_user(conn, user_id=9102, username="t2", first_name="T")
    await conn.execute(
        "INSERT INTO topup_requests (user_id, amount_rub, status) VALUES (9102, 100, 'pending'), (9102, 100, 'pending')"
    )
    await conn.commit()
    with pytest.raises(ValueError, match="topup_pending_cap"):
        await balance_repo.create_topup_request(
            conn, user_id=9102, amount_rub=500.0, settings=settings
        )


@pytest.mark.asyncio
async def test_create_topup_rate_limit(conn, monkeypatch) -> None:
    monkeypatch.setenv("TOPUP_MIN_INTERVAL_SECONDS", "999999")
    settings = Settings()
    await users_repo.upsert_user(conn, user_id=9103, username="t3", first_name="T")
    await balance_repo.create_topup_request(conn, user_id=9103, amount_rub=300.0, settings=settings)
    with pytest.raises(ValueError, match="topup_rate_limit"):
        await balance_repo.create_topup_request(conn, user_id=9103, amount_rub=400.0, settings=settings)


@pytest.mark.asyncio
async def test_require_pending_order_cap(conn, monkeypatch) -> None:
    monkeypatch.setenv("MAX_PENDING_PAYMENT_ORDERS_PER_USER", "2")
    settings = Settings()
    await users_repo.upsert_user(conn, user_id=9104, username="t4", first_name="T")
    for _ in range(2):
        await orders_repo.create_order(
            conn,
            user_id=9104,
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
            user_note="@x",
            status="pending_payment",
        )
    with pytest.raises(ValueError, match="order_pending_cap"):
        await orders_repo.require_pending_order_cap(conn, 9104, settings)


@pytest.mark.asyncio
async def test_expire_other_pending_payment_orders(conn) -> None:
    await users_repo.upsert_user(conn, user_id=9200, username="t20", first_name="T")
    o1 = await orders_repo.create_order(
        conn,
        user_id=9200,
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
        user_note="@x",
        status="pending_payment",
    )
    o2 = await orders_repo.create_order(
        conn,
        user_id=9200,
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
        user_note="@x",
        status="pending_payment",
    )
    expired = await orders_repo.expire_other_pending_payment_orders(
        conn, user_id=9200, keep_order_id=o2
    )
    assert o1 in expired
    row1 = await orders_repo.get_order(conn, o1)
    row2 = await orders_repo.get_order(conn, o2)
    assert str(row1["status"]) == "expired"
    assert str(row2["status"]) == "pending_payment"


@pytest.mark.asyncio
async def test_cancel_user_pending_order(conn) -> None:
    await users_repo.upsert_user(conn, user_id=9201, username="t21", first_name="T")
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
        user_note="@x",
        status="pending_payment",
    )
    assert await orders_repo.cancel_user_pending_order(conn, order_id=oid, user_id=9201) == "ok"
    row = await orders_repo.get_order(conn, oid)
    assert str(row["status"]) == "expired"
    assert await orders_repo.cancel_user_pending_order(conn, order_id=oid, user_id=9201) == "wrong_status"
    assert await orders_repo.cancel_user_pending_order(conn, order_id=oid, user_id=999) == "wrong_user"


@pytest.mark.asyncio
async def test_cancel_all_user_pending_orders(conn) -> None:
    await users_repo.upsert_user(conn, user_id=9202, username="t22", first_name="T")
    ids = []
    for _ in range(3):
        ids.append(
            await orders_repo.create_order(
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
                user_note="@x",
                status="pending_payment",
            )
        )
    cancelled = await orders_repo.cancel_all_user_pending_orders(conn, user_id=9202)
    assert set(cancelled) == set(ids)
    assert await orders_repo.count_user_orders_by_status(conn, 9202, "pending_payment") == 0


@pytest.mark.asyncio
async def test_create_order_partner_api_pending_cap(conn, monkeypatch) -> None:
    monkeypatch.setenv("MAX_PENDING_PAYMENT_ORDERS_PER_USER", "1")
    settings = Settings()
    pepper = os.environ["API_KEY_PEPPER"]
    await users_repo.upsert_user(conn, user_id=9105, username="t5", first_name="T")
    _, raw = await api_clients_repo.create_api_client(
        conn, owner_user_id=9105, pepper=pepper, label="cap", revoke_previous=False
    )
    row = await api_clients_repo.get_active_by_secret(conn, raw, pepper)
    cid = int(row["id"])
    await orders_repo.create_order(
        conn,
        user_id=9105,
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
        user_note="@x",
        status="pending_payment",
    )
    with pytest.raises(ValueError, match="order_pending_cap"):
        await orders_repo.create_order_partner_api(
            conn,
            owner_user_id=9105,
            api_client_id=cid,
            idempotency_key=str(uuid.uuid4()),
            external_ref=None,
            product_id="stars_100",
            product_title="S",
            payment_method="fiat",
            usd_base=1.0,
            rub_before=100.0,
            rub_after=100.0,
            referral_discount_rub=0.0,
            wholesale_discount_rub=0.0,
            referrer_id=None,
            user_note="@y",
            settings=settings,
        )
