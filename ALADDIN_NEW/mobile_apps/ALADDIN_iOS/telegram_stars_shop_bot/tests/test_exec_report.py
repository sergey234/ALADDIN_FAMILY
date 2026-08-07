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
    await users_repo.upsert_user(conn, user_id=94002, username="u94002", first_name="S")
    oid_stars = await orders_repo.create_order(
        conn,
        user_id=94002,
        product_id="stars_100",
        product_title="⭐ 100 Stars",
        payment_method="fiat",
        usd_base=1.0,
        rub_before=150.0,
        rub_after=150.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note="@s",
        status="completed",
        product_kind="stars",
        stars_qty=100,
    )
    await apply_completed_side_effects(conn, oid_stars, settings)
    await users_repo.upsert_user(conn, user_id=94003, username="u94003", first_name="P")
    oid_prem = await orders_repo.create_order(
        conn,
        user_id=94003,
        product_id="premium_3",
        product_title="Premium 3м",
        payment_method="fiat",
        usd_base=10.0,
        rub_before=999.0,
        rub_after=999.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note="@p",
        status="completed",
        product_kind="premium",
        premium_months=3,
    )
    await apply_completed_side_effects(conn, oid_prem, settings)
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

    agg_short = await admin_stats_repo.aggregate_dashboard(
        conn, days=7, real_paid_only=True, exclude_user_ids=set()
    )
    agg_long = await admin_stats_repo.aggregate_dashboard(
        conn, days=30, real_paid_only=True, exclude_user_ids=set()
    )
    pay_short = await admin_stats_repo.payment_funnel_metrics(
        conn, days=7, real_paid_only=True, exclude_user_ids=set()
    )
    webhook_short = await admin_stats_repo.webhook_sla_metrics(conn, days=7)
    cross_short = await admin_stats_repo.cross_sell_metrics(
        conn, days=7, window_days=30, real_paid_only=True, exclude_user_ids=set()
    )
    ret_short = await admin_stats_repo.retention_metrics(
        conn, days=7, real_paid_only=True, exclude_user_ids=set()
    )
    acq_short = await admin_stats_repo.acquisition_metrics(
        conn, days=7, real_paid_only=True, exclude_user_ids=set()
    )
    vpn_summary = await admin_stats_repo.product_sales_summary(
        conn, kind="vpn", days=7, real_paid_only=True, exclude_user_ids=set()
    )
    vpn_mix = await admin_stats_repo.vpn_by_term(
        conn, days=7, real_paid_only=True, exclude_user_ids=set()
    )
    stars_summary = await admin_stats_repo.product_sales_summary(
        conn, kind="stars", days=7, real_paid_only=True, exclude_user_ids=set()
    )
    stars_mix = await admin_stats_repo.stars_by_package(
        conn, days=7, real_paid_only=True, exclude_user_ids=set()
    )
    premium_summary = await admin_stats_repo.product_sales_summary(
        conn, kind="premium", days=7, real_paid_only=True, exclude_user_ids=set()
    )
    premium_mix = await admin_stats_repo.premium_by_term(
        conn, days=7, real_paid_only=True, exclude_user_ids=set()
    )
    crypto_short = await admin_stats_repo.crypto_payment_metrics(
        conn, days=7, real_paid_only=True, exclude_user_ids=set()
    )
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
        active_paid_vpn=1,
        vpn_summary=vpn_summary,
        vpn_mix=vpn_mix,
        stars_summary=stars_summary,
        stars_mix=stars_mix,
        premium_summary=premium_summary,
        premium_mix=premium_mix,
        crypto_short=crypto_short,
    )
    assert "Weekly Executive Report" in text or "Недельный" in text
    assert "1) CAC" in text
    assert "Стоимость привлечения 1 платящего пользователя" in text
    assert "2) Выручка" in text
    assert "Сколько денег пришло за период" in text
    assert "3) VPN share" in text
    assert "Какая доля выручки приходится на VPN" in text
    assert "Средний чек одного платящего пользователя" in text
    assert "9) Payment success" in text
    assert "Какая доля созданных заказов дошла до оплаты" in text
    assert "10) Webhook SLA" in text
    assert "Насколько вовремя и успешно приходят уведомления об оплате" in text
    assert "11) Активные платные VPN" in text
    assert "Сколько людей реально оплатили VPN и сейчас пользуются ключом" in text
    assert "VPN 30" in text
    assert "12) Stars (продажи)" in text
    assert "100" in text and "⭐" in text
    assert "13) Premium (продажи)" in text
    assert "3" in text and "мес" in text
    assert "14) Крипта (USDT)" in text
    assert "Оплаты криптой (USDT)" in text
    assert "доля:" in text
    assert "уник. покупателей:" in text
    assert "Только реальные оплаты" in text
    assert "9901" not in text


@pytest.mark.asyncio
async def test_product_sales_summary_excludes_trial(conn, monkeypatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:exec-mix")
    settings = load_settings()
    await users_repo.upsert_user(conn, user_id=95001, username="t95001", first_name="T")
    oid_ok = await orders_repo.create_order(
        conn,
        user_id=95001,
        product_id="stars_50",
        product_title="⭐ 50",
        payment_method="fiat",
        usd_base=1.0,
        rub_before=80.0,
        rub_after=80.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note=None,
        status="completed",
        product_kind="stars",
        stars_qty=50,
    )
    await apply_completed_side_effects(conn, oid_ok, settings)
    oid_trial = await orders_repo.create_order(
        conn,
        user_id=95001,
        product_id="stars_50",
        product_title="⭐ 50 trial",
        payment_method="vpn_trial",
        usd_base=0.0,
        rub_before=0.0,
        rub_after=0.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note=None,
        status="completed",
        product_kind="stars",
        stars_qty=50,
    )
    await apply_completed_side_effects(conn, oid_trial, settings)
    summary = await admin_stats_repo.product_sales_summary(
        conn, kind="stars", days=7, real_paid_only=True, exclude_user_ids=set()
    )
    assert int(summary["orders"]) == 1
    assert float(summary["revenue_rub"]) == 80.0
    mix = await admin_stats_repo.stars_by_package(
        conn, days=7, real_paid_only=True, exclude_user_ids=set()
    )
    assert len(mix) == 1
    assert int(mix[0]["pack"]) == 50
    assert int(mix[0]["n"]) == 1


@pytest.mark.asyncio
async def test_crypto_payment_metrics_share(conn, monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:exec-crypto")
    settings = load_settings()
    await users_repo.upsert_user(conn, user_id=96001, username="c96001", first_name="C")
    oid_fiat = await orders_repo.create_order(
        conn,
        user_id=96001,
        product_id="stars_50",
        product_title="⭐ 50",
        payment_method="fiat",
        usd_base=1.0,
        rub_before=100.0,
        rub_after=100.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note=None,
        status="completed",
        product_kind="stars",
        stars_qty=50,
    )
    await apply_completed_side_effects(conn, oid_fiat, settings)
    await users_repo.upsert_user(conn, user_id=96002, username="c96002", first_name="K")
    oid_crypto = await orders_repo.create_order(
        conn,
        user_id=96002,
        product_id="stars_100",
        product_title="⭐ 100",
        payment_method="crypto",
        usd_base=1.0,
        rub_before=200.0,
        rub_after=200.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note=None,
        status="completed",
        product_kind="stars",
        stars_qty=100,
    )
    await apply_completed_side_effects(conn, oid_crypto, settings)
    await conn.execute(
        "UPDATE orders SET invoice_last_provider = 'xrocket' WHERE id = ?",
        (oid_crypto,),
    )
    await conn.commit()
    m = await admin_stats_repo.crypto_payment_metrics(
        conn, days=7, real_paid_only=True, exclude_user_ids=set()
    )
    assert int(m["orders"]) == 1
    assert float(m["revenue_rub"]) == 200.0
    assert float(m["share_pct"]) == pytest.approx(66.67, abs=0.05)


def test_exec_report_last_sent_roundtrip(tmp_path, monkeypatch) -> None:
    from bot.services.exec_report import (
        exec_report_state_path,
        parse_exec_cadences,
        read_exec_report_last_sent,
        write_exec_report_last_sent,
    )

    monkeypatch.setenv("BOT_TOKEN", "9:exec-state")
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "shop.db"))
    settings = load_settings()
    path = exec_report_state_path(settings, "daily")
    assert path.name == "exec_report_last_sent_daily.txt"
    assert read_exec_report_last_sent(path) is None
    write_exec_report_last_sent(path, 1_700_000_000.0)
    assert read_exec_report_last_sent(path) == pytest.approx(1_700_000_000.0)
    keys = [c.key for c in parse_exec_cadences("daily,weekly,monthly,quarterly,semi")]
    assert keys == ["daily", "weekly", "monthly", "quarterly", "semi"]
    assert [c.days for c in parse_exec_cadences("all")] == [1, 7, 30, 90, 150]
