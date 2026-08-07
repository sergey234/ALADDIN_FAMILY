from __future__ import annotations

import pytest

from bot.services import orders_repo, users_repo


@pytest.mark.asyncio
async def test_manual_only_paid_not_stuck(conn) -> None:
    await users_repo.upsert_user(conn, user_id=502, username="m", first_name="M")
    oid = await orders_repo.create_order(
        conn,
        user_id=502,
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
    await orders_repo.set_order_fulfillment_mode(conn, oid, mode="manual_only")
    await conn.execute(
        "UPDATE orders SET updated_at = datetime('now', '-30 hours') WHERE id = ?",
        (oid,),
    )
    await conn.commit()

    stuck = await orders_repo.list_order_ids_stuck_paid_or_processing(conn, hours_without_update=24, limit=50)
    assert oid not in stuck

    stuck_paid = await orders_repo.list_order_ids_stuck_paid_only(conn, minutes_without_update=5, limit=50)
    assert oid not in stuck_paid


@pytest.mark.asyncio
async def test_list_stuck_paid_orders_by_updated_at(conn) -> None:
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


def test_filter_alert_order_ids_ignores_test() -> None:
    from bot.config import Settings
    from bot.services.stuck_orders_monitor import _filter_alert_order_ids

    settings = Settings(
        bot_token="1:test",
        stuck_alert_ignore_order_ids="122,123,125,136",
    )
    assert _filter_alert_order_ids(settings, [122, 136, 200, 201]) == [200, 201]
    assert _filter_alert_order_ids(settings, [122, 123, 125, 136]) == []
