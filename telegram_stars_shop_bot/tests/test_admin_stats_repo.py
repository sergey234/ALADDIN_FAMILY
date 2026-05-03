from __future__ import annotations

import pytest

from bot.config import load_settings
from bot.services.pricing import referral_discount_percent_snapshot
from bot.services import admin_stats_repo, analytics_repo, orders_repo, users_repo
from bot.services.order_flow import apply_completed_side_effects


@pytest.mark.asyncio
async def test_aggregate_dashboard_completed_only(conn, monkeypatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:admin-stats-test")
    settings = load_settings()
    await users_repo.upsert_user(conn, user_id=91001, username="u1", first_name="U")

    pending = await orders_repo.create_order(
        conn,
        user_id=91001,
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
        user_note="@x",
        status="pending_payment",
        product_kind="stars",
        stars_qty=100,
        premium_months=None,
    )
    done = await orders_repo.create_order(
        conn,
        user_id=91001,
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
        user_note="@x",
        status="completed",
        product_kind="stars",
        stars_qty=100,
        premium_months=None,
    )
    await apply_completed_side_effects(conn, done, settings)

    all_agg = await admin_stats_repo.aggregate_dashboard(conn, days=None)
    assert all_agg.orders_count == 1
    assert all_agg.revenue_rub == pytest.approx(100.0)
    assert pending > 0


@pytest.mark.asyncio
async def test_period_today_matches_calendar_day(conn, monkeypatch) -> None:
    """days=0 и days=-1 — календарный сегодня (не «-0 days» в SQLite)."""
    monkeypatch.setenv("BOT_TOKEN", "9:admin-stats-test2")
    settings = load_settings()
    await users_repo.upsert_user(conn, user_id=91002, username="u2", first_name="U")
    oid = await orders_repo.create_order(
        conn,
        user_id=91002,
        product_id="s",
        product_title="S",
        payment_method="fiat",
        usd_base=1.0,
        rub_before=50.0,
        rub_after=50.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note="@x",
        status="completed",
    )
    await apply_completed_side_effects(conn, oid, settings)

    a0 = await admin_stats_repo.aggregate_dashboard(conn, days=0)
    am1 = await admin_stats_repo.aggregate_dashboard(conn, days=-1)
    assert a0.orders_count == am1.orders_count == 1
    assert a0.revenue_rub == am1.revenue_rub == pytest.approx(50.0)


@pytest.mark.asyncio
async def test_funnel_metrics_after_bot_entry(conn, monkeypatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:funnel-test")
    load_settings()
    await users_repo.upsert_user(conn, user_id=92001, username="v1", first_name="V")
    await analytics_repo.log_event(conn, user_id=92001, event_type="bot_entry", meta={"via": "test"})
    oid = await orders_repo.create_order(
        conn,
        user_id=92001,
        product_id="s",
        product_title="S",
        payment_method="fiat",
        usd_base=1.0,
        rub_before=80.0,
        rub_after=80.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note="@x",
        status="completed",
    )
    settings = load_settings()
    await apply_completed_side_effects(conn, oid, settings)
    f = await admin_stats_repo.funnel_metrics(conn, days=None)
    assert int(f["funnel_visitors"]) >= 1
    assert int(f["funnel_converted"]) >= 1
    assert float(f["funnel_conversion_pct"]) >= 99.0

    weeks = await admin_stats_repo.sales_by_week(conn, days=30)
    assert isinstance(weeks, list)


def test_referral_discount_percent_snapshot_unit() -> None:
    assert referral_discount_percent_snapshot(rub_list=100.0, rub_referral_discount=7.0) == pytest.approx(7.0)
    assert referral_discount_percent_snapshot(rub_list=0.0, rub_referral_discount=5.0) == 0.0
