from __future__ import annotations

import os
import uuid

import pytest

from bot.services import api_clients_repo, orders_repo, users_repo


@pytest.mark.asyncio
async def test_create_order_partner_api_idempotent(conn) -> None:
    pepper = os.environ["API_KEY_PEPPER"]

    await users_repo.upsert_user(conn, user_id=7001, username="u1", first_name="U")
    _, raw = await api_clients_repo.create_api_client(
        conn, owner_user_id=7001, pepper=pepper, label="t", revoke_previous=False
    )
    row = await api_clients_repo.get_active_by_secret(conn, raw, pepper)
    assert row is not None
    cid = int(row["id"])
    idem = str(uuid.uuid4())
    oid1, created1 = await orders_repo.create_order_partner_api(
        conn,
        owner_user_id=7001,
        api_client_id=cid,
        idempotency_key=idem,
        external_ref="ext1",
        product_id="stars_100",
        product_title="⭐ 100 Stars",
        payment_method="fiat",
        usd_base=1.0,
        rub_before=100.0,
        rub_after=90.0,
        referral_discount_rub=10.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        user_note="@dest",
    )
    assert created1 is True
    oid2, created2 = await orders_repo.create_order_partner_api(
        conn,
        owner_user_id=7001,
        api_client_id=cid,
        idempotency_key=idem,
        external_ref="ext1",
        product_id="stars_100",
        product_title="⭐ 100 Stars",
        payment_method="fiat",
        usd_base=1.0,
        rub_before=100.0,
        rub_after=90.0,
        referral_discount_rub=10.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        user_note="@dest",
    )
    assert created2 is False
    assert oid1 == oid2


@pytest.mark.asyncio
async def test_amount_due_external(conn) -> None:
    pepper = os.environ["API_KEY_PEPPER"]
    await users_repo.upsert_user(conn, user_id=7002, username="u2", first_name="U")
    _, raw = await api_clients_repo.create_api_client(
        conn, owner_user_id=7002, pepper=pepper, label="t", revoke_previous=False
    )
    row = await api_clients_repo.get_active_by_secret(conn, raw, pepper)
    cid = int(row["id"])
    oid, _ = await orders_repo.create_order_partner_api(
        conn,
        owner_user_id=7002,
        api_client_id=cid,
        idempotency_key=str(uuid.uuid4()),
        external_ref=None,
        product_id="x",
        product_title="T",
        payment_method="fiat",
        usd_base=1.0,
        rub_before=100.0,
        rub_after=100.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        user_note="@x",
    )
    order = await orders_repo.get_order(conn, oid)
    assert orders_repo.amount_due_external(order) == 100.0
