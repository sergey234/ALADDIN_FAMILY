from __future__ import annotations

import pytest

from bot.services import orders_repo, users_repo


@pytest.mark.asyncio
async def test_list_stuck_paid_orders_by_updated_at(conn) -> None:
    await users_repo.upsert_user(conn, user_id=501, username="u", first_name="U")
    oid = await orders_repo.create_order(
        conn,
        user_id=501,
        product_id="s",
        product_title="S",
        payment_method="fiat",
        usd_base=1.0,
        rub_before=10.0,
        rub_after=10.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note="@x",
        status="paid",
    )
    await conn.execute(
        "UPDATE orders SET updated_at = datetime('now', '-30 hours') WHERE id = ?",
        (oid,),
    )
    await conn.commit()

    stuck = await orders_repo.list_order_ids_stuck_paid_or_processing(conn, hours_without_update=24, limit=50)
    assert oid in stuck

    fresh = await orders_repo.list_order_ids_stuck_paid_or_processing(conn, hours_without_update=200, limit=50)
    assert oid not in fresh
