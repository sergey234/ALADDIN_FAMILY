from __future__ import annotations

import pytest

from bot.config import load_settings
from bot.services.pricing import referral_discount_percent_snapshot
from bot.services import admin_stats_repo, analytics_repo, feedback_repo, orders_repo, users_repo
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


@pytest.mark.asyncio
async def test_split_core_metrics_bundle(conn, monkeypatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:split-core")
    settings = load_settings()
    await users_repo.upsert_user(conn, user_id=93001, username="u93001", first_name="A")
    await users_repo.upsert_user(conn, user_id=93002, username="u93002", first_name="B")

    # user 93001: stars -> vpn cross-sell
    o1 = await orders_repo.create_order(
        conn,
        user_id=93001,
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
        user_note="@a",
        status="completed",
        product_kind="stars",
        stars_qty=100,
        premium_months=None,
    )
    await apply_completed_side_effects(conn, o1, settings)
    o2 = await orders_repo.create_order(
        conn,
        user_id=93001,
        product_id="vpn_30",
        product_title="🌐 VPN 30",
        payment_method="fiat",
        usd_base=1.0,
        rub_before=200.0,
        rub_after=200.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note="@a",
        status="completed",
        product_kind="vpn",
        stars_qty=None,
        premium_months=None,
    )
    await apply_completed_side_effects(conn, o2, settings)

    # user 93002: pending -> paid (funnel), no completion
    _ = await orders_repo.create_order(
        conn,
        user_id=93002,
        product_id="premium_1",
        product_title="💎 Premium 1m",
        payment_method="fiat",
        usd_base=1.0,
        rub_before=150.0,
        rub_after=150.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note="@b",
        status="paid",
        product_kind="premium",
        stars_qty=None,
        premium_months=1,
    )

    # acquisition spend + attribution
    await conn.execute(
        """
        INSERT INTO marketing_spend_daily (spend_date, source, campaign, spend_rub, clicks, impressions)
        VALUES (date('now'), 'tg_ads', '2026Q2_vpn_ru_acq_speed', 1000, 100, 1000)
        """
    )
    await conn.execute(
        """
        INSERT INTO user_acquisition (user_id, first_source, first_campaign, first_creative, last_source, last_campaign, last_creative)
        VALUES (93001, 'tg_ads', '2026Q2_vpn_ru_acq_speed', 'video_utility_a', 'tg_ads', '2026Q2_vpn_ru_acq_speed', 'video_utility_a')
        """
    )
    await analytics_repo.log_event(conn, user_id=93001, event_type="offer_impression", meta={"source": "tg_ads"})
    await analytics_repo.log_event(conn, user_id=93001, event_type="offer_click", meta={"source": "tg_ads"})
    await analytics_repo.log_event(conn, user_id=93001, event_type="order_created", meta={"source": "tg_ads"})

    # webhook delivery sample
    await conn.execute(
        """
        INSERT INTO outbound_webhook_events (api_client_id, order_id, event_type, target_url, payload_json, status, attempts, delivered_at, created_at)
        VALUES (1, ?, 'order.status_changed', 'https://example.test/hook', '{}', 'delivered', 1, datetime('now'), datetime('now'))
        """,
        (o2,),
    )
    await conn.commit()

    agg = await admin_stats_repo.aggregate_dashboard(conn, days=None)
    assert agg.revenue_rub == pytest.approx(300.0)
    assert agg.vpn_revenue_rub == pytest.approx(200.0)
    assert agg.vpn_revenue_share_pct > 60
    assert agg.arppu_rub == pytest.approx(300.0)

    funnel = await admin_stats_repo.payment_funnel_metrics(conn, days=None)
    assert int(funnel["funnel_created_orders"]) >= 3
    assert int(funnel["funnel_paid_orders"]) >= 3

    webhook = await admin_stats_repo.webhook_sla_metrics(conn, days=None)
    assert int(webhook["webhook_total"]) >= 1
    assert float(webhook["webhook_success_rate_pct"]) >= 99.0

    cross = await admin_stats_repo.cross_sell_metrics(conn, days=None, window_days=30)
    assert int(cross["cross_sell_sp_base"]) >= 1
    assert int(cross["cross_sell_sp_to_vpn_n"]) >= 1

    ret = await admin_stats_repo.retention_metrics(conn, days=None)
    assert int(ret["retention_cohort_size"]) >= 1

    acq = await admin_stats_repo.acquisition_metrics(conn, days=None)
    assert float(acq["acq_spend_rub"]) == pytest.approx(1000.0)
    assert int(acq["acq_paid_users"]) >= 1
    assert float(acq["acq_cac_rub"]) > 0
    assert float(acq["acq_ctr_pct"]) >= 99.0
    assert float(acq["acq_cr_pct"]) >= 99.0


def test_referral_discount_percent_snapshot_unit() -> None:
    assert referral_discount_percent_snapshot(rub_list=100.0, rub_referral_discount=7.0) == pytest.approx(7.0)
    assert referral_discount_percent_snapshot(rub_list=0.0, rub_referral_discount=5.0) == 0.0


@pytest.mark.asyncio
async def test_feedback_metrics_bundle(conn) -> None:
    await feedback_repo.save_feedback(conn, user_id=94010, kind="nps", score=10, product_scope="shop")
    await feedback_repo.save_feedback(conn, user_id=94011, kind="nps", score=2, product_scope="shop")
    await feedback_repo.save_feedback(conn, user_id=94012, kind="csat", score=5, product_scope="shop")
    await feedback_repo.save_feedback(conn, user_id=94013, kind="csat", score=3, product_scope="shop")
    m = await admin_stats_repo.feedback_metrics(conn, days=None)
    assert int(m["nps_responses"]) == 2
    assert int(m["nps_promoters"]) == 1
    assert int(m["nps_detractors"]) == 1
    assert float(m["nps_score"]) == pytest.approx(0.0)
    assert int(m["csat_responses"]) == 2
    assert int(m["csat_positive"]) == 1
    assert float(m["csat_pct"]) == pytest.approx(50.0)
