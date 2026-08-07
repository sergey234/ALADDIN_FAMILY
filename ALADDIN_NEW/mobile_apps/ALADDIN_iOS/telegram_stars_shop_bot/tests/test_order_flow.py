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
        product_id="vpn_30d",
        product_title="VPN",
        payment_method="fiat",
        usd_base=0.0,
        rub_before=100.0,
        rub_after=100.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=8002,
        commission_rub=0.0,
        user_note="@x",
        status="completed",
        product_kind="vpn",
    )
    await apply_completed_side_effects(conn, oid, settings)

    ref = await users_repo.get_user(conn, 8002)
    assert float(ref["ref_balance_rub"] or 0) == pytest.approx(15.0, rel=1e-3)

    order = await orders_repo.get_order(conn, oid)
    assert order is not None
    # FIN VPN: fee=0, cogs=0; ref=15 → net = 100 - 15 = 85
    assert float(order["net_profit_rub"] or 0) == pytest.approx(85.0, rel=1e-2)
    assert float(order["payment_fee_percent_snapshot"] or 0) == pytest.approx(0.0, abs=1e-6)
    assert float(order["payment_gateway_fee_rub"] or 0) == pytest.approx(0.0, abs=1e-6)

    await apply_completed_side_effects(conn, oid, settings)
    ref2 = await users_repo.get_user(conn, 8002)
    assert float(ref2["ref_balance_rub"] or 0) == pytest.approx(15.0, rel=1e-3)


@pytest.mark.asyncio
async def test_bc_payment_claim_ok_then_cooldown(conn) -> None:
    oid = await orders_repo.create_order(
        conn,
        user_id=8010,
        product_id="stars_100",
        product_title="⭐ 100",
        payment_method="fiat",
        usd_base=1.0,
        rub_before=100.0,
        rub_after=100.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note="@recv",
        status="pending_payment",
    )
    a, _w = await orders_repo.touch_bc_payment_claim_if_allowed(
        conn, order_id=oid, user_id=8010, cooldown_seconds=3600
    )
    assert a == "ok"
    b, wait = await orders_repo.touch_bc_payment_claim_if_allowed(
        conn, order_id=oid, user_id=8010, cooldown_seconds=3600
    )
    assert b == "cooldown"
    assert int(wait) > 0


@pytest.mark.asyncio
async def test_bc_payment_claim_wrong_user(conn) -> None:
    oid = await orders_repo.create_order(
        conn,
        user_id=8011,
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
        status="pending_payment",
    )
    code, _ = await orders_repo.touch_bc_payment_claim_if_allowed(
        conn, order_id=oid, user_id=9999, cooldown_seconds=60
    )
    assert code == "wrong_user"


@pytest.mark.asyncio
async def test_list_user_pending_payment_order_ids(conn) -> None:
    u = 8020
    a = await orders_repo.create_order(
        conn,
        user_id=u,
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
        status="pending_payment",
    )
    b = await orders_repo.create_order(
        conn,
        user_id=u,
        product_id="s",
        product_title="S2",
        payment_method="fiat",
        usd_base=1.0,
        rub_before=20.0,
        rub_after=20.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note="@x",
        status="pending_payment",
    )
    ids = await orders_repo.list_user_pending_payment_order_ids(conn, u, limit=10)
    assert b in ids and a in ids
    assert ids[0] == b
