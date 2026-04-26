from __future__ import annotations

import pytest

from bot.config import load_settings
from bot.services import orders_repo, users_repo
from bot.services.order_flow import apply_completed_side_effects


@pytest.mark.asyncio
async def test_update_status_rejects_completed_to_completed(conn) -> None:
    oid = await orders_repo.create_order(
        conn,
        user_id=8009,
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
        status="completed",
    )
    with pytest.raises(ValueError, match="invalid_order_transition"):
        await orders_repo.update_status(conn, oid, "completed")


@pytest.mark.asyncio
async def test_referrer_commission_on_first_completed(conn, monkeypatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:orderflow-test")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("REF_REFERRER_COMMISSION_FIRST_ORDER_PERCENT", "15")
    settings = load_settings()

    await users_repo.upsert_user(conn, user_id=8001, username="buyer", first_name="B")
    await users_repo.upsert_user(conn, user_id=8002, username="ref", first_name="R")
    await conn.execute("UPDATE users SET referrer_id = 8002 WHERE user_id = 8001")
    await conn.commit()

    oid = await orders_repo.create_order(
        conn,
        user_id=8001,
        product_id="s",
        product_title="S",
        payment_method="fiat",
        usd_base=1.0,
        rub_before=100.0,
        rub_after=100.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=8002,
        commission_rub=0.0,
        user_note="@x",
        status="completed",
    )
    await apply_completed_side_effects(conn, oid, settings)

    ref = await users_repo.get_user(conn, 8002)
    assert float(ref["ref_balance_rub"] or 0) == pytest.approx(15.0, rel=1e-3)

    await apply_completed_side_effects(conn, oid, settings)
    ref2 = await users_repo.get_user(conn, 8002)
    assert float(ref2["ref_balance_rub"] or 0) == pytest.approx(15.0, rel=1e-3)
