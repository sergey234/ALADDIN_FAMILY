from __future__ import annotations

import pytest

from bot.config import load_settings
from bot.services import admin_stats_repo, orders_repo, users_repo
from bot.services.exec_report import build_exec_report_text
from bot.services.order_flow import apply_completed_side_effects


@pytest.mark.asyncio
async def test_build_exec_report_text_contains_top10_blocks(conn, monkeypatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:exec-report")
    settings = load_settings()
    await users_repo.upsert_user(conn, user_id=94001, username="u94001", first_name="R")
    oid = await orders_repo.create_order(
        conn,
        user_id=94001,
        product_id="vpn_30",
        product_title="🌐 VPN 30",
        payment_method="fiat",
        usd_base=1.0,
        rub_before=300.0,
        rub_after=300.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note="@r",
        status="completed",
        product_kind="vpn",
    )
    await apply_completed_side_effects(conn, oid, settings)
    await conn.execute(
        """
        INSERT INTO outbound_webhook_events (api_client_id, order_id, event_type, target_url, payload_json, status, attempts, delivered_at, created_at)
        VALUES (1, ?, 'order.status_changed', 'https://example.test/hook', '{}', 'delivered', 1, datetime('now'), datetime('now'))
        """,
        (oid,),
    )
    await conn.execute(
        """
        INSERT INTO marketing_spend_daily (spend_date, source, campaign, spend_rub, clicks, impressions)
        VALUES (date('now'), 'tg_ads', '2026Q2_vpn_ru_acq_speed', 500, 50, 5000)
        """
    )
    await conn.execute(
        """
        INSERT INTO user_acquisition (user_id, first_source, first_campaign, first_creative, last_source, last_campaign, last_creative)
        VALUES (94001, 'tg_ads', '2026Q2_vpn_ru_acq_speed', 'video_utility_a', 'tg_ads', '2026Q2_vpn_ru_acq_speed', 'video_utility_a')
        """
    )
    await conn.commit()

    agg_short = await admin_stats_repo.aggregate_dashboard(conn, days=7)
    agg_long = await admin_stats_repo.aggregate_dashboard(conn, days=30)
    pay_short = await admin_stats_repo.payment_funnel_metrics(conn, days=7)
    webhook_short = await admin_stats_repo.webhook_sla_metrics(conn, days=7)
    cross_short = await admin_stats_repo.cross_sell_metrics(conn, days=7, window_days=30)
    ret_short = await admin_stats_repo.retention_metrics(conn, days=7)
    acq_short = await admin_stats_repo.acquisition_metrics(conn, days=7)
    text = build_exec_report_text(
        generated_at="2026-06-02 12:00 UTC",
        short_days=7,
        long_days=30,
        agg_short=agg_short,
        agg_long=agg_long,
        pay_short=pay_short,
        webhook_short=webhook_short,
        cross_short=cross_short,
        ret_short=ret_short,
        acq_short=acq_short,
    )
    assert "Weekly Executive Report" in text
    assert "1) CAC" in text
    assert "2) Выручка" in text
    assert "3) VPN share" in text
    assert "9) Payment success" in text
    assert "10) Webhook SLA" in text
