from __future__ import annotations

import pytest

from bot.config import Settings
from bot.services import balance_repo, orders_repo, users_repo


@pytest.mark.asyncio
async def test_amount_due_external_matches_total_minus_balance(conn) -> None:
    await users_repo.upsert_user(conn, user_id=8801, username="pi", first_name="P")
    oid = await orders_repo.create_order(
        conn,
        user_id=8801,
        product_id="stars_100",
        product_title="100",
        payment_method="mix_crypto",
        usd_base=1.0,
        rub_before=300.0,
        rub_after=300.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note="@x",
        status="pending_payment",
        balance_applied_rub=120.0,
    )
    row = await orders_repo.get_order(conn, oid)
    assert orders_repo.amount_due_external(row) == 180.0


@pytest.mark.asyncio
async def test_create_order_with_balance_partial_due_equals_remainder(conn) -> None:
    await users_repo.upsert_user(conn, user_id=8802, username="pi2", first_name="P")
    await balance_repo.add_balance(conn, user_id=8802, delta=500.0, kind="test_grant")
    settings = Settings()
    oid = await orders_repo.create_order_with_balance_partial(
        conn,
        user_id=8802,
        product_id="stars_100",
        product_title="100",
        payment_method="mix_crypto",
        usd_base=1.0,
        rub_before=200.0,
        rub_invoice_total=200.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        user_note="@x",
        balance_apply=50.0,
        settings=settings,
    )
    row = await orders_repo.get_order(conn, oid)
    assert float(row["rub_after_discounts"]) == 200.0
    assert float(row["balance_applied_rub"] or 0) == 50.0
    assert str(row["status"]) == "pending_payment"
    assert orders_repo.amount_due_external(row) == 150.0
