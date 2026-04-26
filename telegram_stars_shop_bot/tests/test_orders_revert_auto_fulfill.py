from __future__ import annotations

import pytest

from bot.db.database import connect
from bot.services import orders_repo, users_repo


@pytest.mark.asyncio
async def test_revert_processing_to_paid_without_provider_ref(tmp_path) -> None:
    db = tmp_path / "revert.db"
    conn = await connect(db)
    await users_repo.upsert_user(conn, user_id=1, username="u", first_name="U")
    oid = await orders_repo.create_order(
        conn,
        user_id=1,
        product_id="stars_100",
        product_title="S",
        payment_method="t",
        usd_base=1.0,
        rub_before=1.0,
        rub_after=1.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note="@x",
        status="processing",
    )
    ok = await orders_repo.revert_processing_to_paid_after_auto_fulfill_failure(conn, oid)
    assert ok is True
    row = await orders_repo.get_order(conn, oid)
    assert str(row["status"]) == "paid"
    await conn.close()


@pytest.mark.asyncio
async def test_revert_noop_when_provider_ref_set(tmp_path) -> None:
    db = tmp_path / "revert2.db"
    conn = await connect(db)
    await users_repo.upsert_user(conn, user_id=1, username="u", first_name="U")
    oid = await orders_repo.create_order(
        conn,
        user_id=1,
        product_id="stars_100",
        product_title="S",
        payment_method="t",
        usd_base=1.0,
        rub_before=1.0,
        rub_after=1.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note="@x",
        status="processing",
    )
    await conn.execute(
        "UPDATE orders SET fulfillment_provider_ref = ? WHERE id = ?",
        ("ext-uuid", oid),
    )
    await conn.commit()
    ok = await orders_repo.revert_processing_to_paid_after_auto_fulfill_failure(conn, oid)
    assert ok is False
    row = await orders_repo.get_order(conn, oid)
    assert str(row["status"]) == "processing"
    await conn.close()
