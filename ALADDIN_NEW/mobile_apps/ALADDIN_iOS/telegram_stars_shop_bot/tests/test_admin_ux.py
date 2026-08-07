"""Smoke tests for admin business UX (no DB)."""

from bot.services.admin_stats_repo import DashboardAgg
from bot.services import admin_ux


def _agg() -> DashboardAgg:
    return DashboardAgg(
        revenue_rub=1250.0,
        orders_count=2,
        net_profit_rub=48.5,
        stars_units_sold=0,
        stars_revenue_rub=0.0,
        premium_units_sold=0,
        premium_revenue_rub=0.0,
        vpn_units_sold=2,
        vpn_revenue_rub=1250.0,
        arppu_rub=625.0,
        vpn_revenue_share_pct=100.0,
        distinct_referrers=0,
        fees_rub=1.5,
        vpn_net_profit_rub=48.5,
        stars_net_profit_rub=0.0,
        premium_net_profit_rub=0.0,
    )


def test_business_dashboard_has_no_tech_jargon():
    text = admin_ux.format_business_dashboard(
        period_label_s="7 дней",
        agg=_agg(),
        rm={"total_referral_bonus_rub": 10},
        vpn_cp={
            "vpn_cp_paid_accounts_vpn_active": 9,
            "vpn_cp_paid_accounts_vpn_expired": 1,
            "vpn_cp_paid_accounts_total": 10,
        },
        vpn_status="degraded",
        pending_payment=2,
        pending_fulfill_count=1,
        pending_fulfill_rub=1200.0,
        rent_monthly_rub=1000.0,
        rent_period_rub=admin_ux.rent_estimate_rub(monthly_rub=1000.0, days=7),
        delta_revenue_pct=12.5,
        delta_net_pct=-3.0,
        usd_rub_rate=90.0,
    )
    low = text.lower()
    assert "p95" not in low
    assert "rtt" not in low
    assert "swap" not in low
    assert "circuit" not in low
    assert "webhook sla" not in low
    assert "Выручка" in text
    assert "Чистая прибыль" in text
    assert "USDT" in text
    assert "Комиссии" in text
    assert "Валовая после комиссии" not in text
    assert "В ожидании" in text
    assert "прибыль ещё не посчитана" in text
    assert "После аренды" in text
    assert "оплаченные подписки" in text
    assert "Активных: <b>9</b>" in text
    assert "Требует внимания" in text
    assert "Ai Monkey Stars" in text
    assert "к прошлому" in text
    assert "+12.5%" in text


def test_hub_keyboard_has_core_sections():
    kb = admin_ux.hub_keyboard(period_token="7")
    labels = [b.text for row in kb.inline_keyboard for b in row]
    for need in ("Продажи", "VPN", "Рефералы", "Финансы", "Обновить", "Полный тех.отчёт", "С запуска"):
        assert any(need in (t or "") for t in labels), need
    cbs = [b.callback_data for row in kb.inline_keyboard for b in row]
    assert "aux:d:start" in cbs


def test_format_money_rub_usdt():
    assert "USDT" in admin_ux.format_money_rub_usdt(rub=90.0, usd_rub_rate=90.0)
    assert admin_ux.format_money_rub_usdt(rub=10.0, usd_rub_rate=0) == "10.00 ₽"


def test_period_tokens():
    assert admin_ux.days_from_token("today") == 1
    assert admin_ux.days_from_token("7") == 7
    assert admin_ux.days_from_token("all") is None
    assert admin_ux.days_from_token("start") is None
    assert admin_ux.period_label(None, token="start") == "с запуска"
    assert admin_ux.period_label(None, token="all") == "всё время"


def test_d5_pct_delta_and_line():
    from bot.services import admin_stats_repo as asr

    assert asr.pct_delta(110, 100) == 10.0
    assert asr.pct_delta(90, 100) == -10.0
    assert asr.pct_delta(0, 0) is None
    assert asr._period_clause_previous(None) is None
    assert asr._period_clause_previous(7) is not None
    line = admin_ux.format_delta_line(revenue_pct=5.0, net_pct=None)
    assert line and "выр. +5%" in line
    assert admin_ux.format_delta_line(revenue_pct=None, net_pct=None) is None


def test_finance_hub_shows_kpi():
    text = admin_ux.format_finance_hub(
        period_label_s="7 дней",
        agg=_agg(),
        pending_fulfill_count=1,
        pending_fulfill_rub=1200.0,
    )
    assert "Выручка" in text
    assert "Комиссии" in text
    assert "Чистая прибыль" in text
    assert "Банк/Lava" in text
    assert "0.015" in text
    assert "/admin_cogs" in text


def test_finance_section_kb_periods():
    kb = admin_ux.finance_section_kb(period_token="30")
    cbs = [b.callback_data for row in kb.inline_keyboard for b in row]
    for need in (
        "aux:finance:today",
        "aux:finance:7",
        "aux:finance:30",
        "aux:finance:all",
        "aux:finance:start",
    ):
        assert need in cbs, need
    labels = [b.text for row in kb.inline_keyboard for b in row]
    assert any(t and "· 30 дней ·" in t for t in labels)
    hub = admin_ux.hub_keyboard(period_token="start")
    assert any(
        (b.callback_data or "") == "aux:finance:start"
        for row in hub.inline_keyboard
        for b in row
    )


def test_vpn_hub_human():
    text = admin_ux.format_vpn_hub(
        period_label_s="7 дней",
        vpn_status="ok",
        vpn_cp={
            "vpn_cp_paid_accounts_total": 10,
            "vpn_cp_paid_accounts_vpn_active": 9,
            "vpn_cp_paid_accounts_vpn_expired": 1,
            "vpn_cp_jobs_pending": 0,
            "vpn_cp_jobs_failed": 0,
        },
        vpn_units_sold=2,
        vpn_revenue_rub=1250.0,
        vpn_net_profit_rub=1250.0,
    )
    assert "Сервис работает" in text
    assert "Активных" in text
    assert "p95" not in text.lower()
    assert "rtt" not in text.lower()
    kb = admin_ux.vpn_section_kb(period_token="7")
    cbs = [b.callback_data for row in kb.inline_keyboard for b in row]
    assert "aux:vpn:30" in cbs
    assert "ast:vpn_health" in cbs
    assert "aux:vpn_health_simple:7" in cbs


def test_ref_and_withdraw_hub():
    text = admin_ux.format_ref_hub(
        period_label_s="7 дней",
        rm={"total_referral_bonus_rub": 100.0, "orders_with_ref_discount": 2},
        vpn_rm={
            "vpn_ref_grants": 3,
            "vpn_ref_distinct_referrers": 2,
            "vpn_ref_referrer_days": 14,
            "vpn_ref_friend_days": 7,
        },
        top_refs=[{"rid": 1, "bonus_rub": 50.0, "orders_n": 2}],
        available_bonus_rub=40.0,
        withdraw_pending_count=1,
        withdraw_pending_rub=1000.0,
    )
    assert "Начислено бонусов" in text
    assert "Топ рефереров" in text
    w = admin_ux.format_withdraw_hub(
        summary={"pending_count": 1, "pending_rub": 1000, "paid_count": 2, "paid_rub": 2000}
    )
    assert "Ожидают" in w
    assert "Выплачено" in w
    assert "aux:ref:7" in [
        b.callback_data for row in admin_ux.ref_section_kb().inline_keyboard for b in row
    ]


def test_a8_coverage_cmdrun():
    """audit-03/04: critical admin cmds reachable from section keyboards."""
    cbs: set[str] = set()
    for kb in (
        admin_ux.vpn_section_kb(),
        admin_ux.finance_section_kb(),
        admin_ux.mkt_section_kb(),
        admin_ux.sys_section_kb(),
        admin_ux.settings_section_kb(),
        admin_ux.promo_section_kb(),
        admin_ux.contest_section_kb(),
        admin_ux.export_section_kb(),
        admin_ux.ref_section_kb(),
        admin_ux.attention_section_kb(),
    ):
        for row in kb.inline_keyboard:
            for b in row:
                if b.callback_data:
                    cbs.add(b.callback_data)
    for need in (
        "aux:cmdrun:admin_vpn_finalize",
        "aux:cmdrun:admin_vpn_revoke",
        "aux:cmdrun:admin_vpn",
        "aux:cmdrun:admin_recalc_profit",
        "aux:cmdrun:admin_fin_set",
        "aux:cmdrun:admin_broadcast",
        "aux:cmdrun:admin_promo",
        "aux:export_run:30",
        "ast:vpn_health",
    ):
        assert need in cbs, need
    assert not any("cmdhint" in c for c in cbs)
    # business dashboard still jargon-free
    text = admin_ux.format_business_dashboard(
        period_label_s="7 дней",
        agg=_agg(),
        rm={"total_referral_bonus_rub": 1},
        vpn_cp={"vpn_cp_paid_accounts_vpn_active": 1, "vpn_cp_paid_accounts_vpn_expired": 0, "vpn_cp_paid_accounts_total": 1},
        vpn_status="ok",
    )
    low = text.lower()
    for bad in ("p95", "rtt", "swap", "circuit", "webhook sla", "control plane"):
        assert bad not in low, bad
    assert "Активных" in admin_ux.format_promo_hub(active_n=2, total_n=5)
    assert "Конкурсы" in admin_ux.format_contest_hub(active_title="Test", total_n=1)
    assert "Рассылка" in admin_ux.format_mkt_hub(acq={"acq_spend_rub": 10, "acq_paid_users": 1, "acq_cac_rub": 10})
    assert "CSV" in admin_ux.format_export_hub()
    assert "диагностика" in admin_ux.format_sys_hub().lower()
    assert "notices" in admin_ux.format_settings_hub().lower() or "Notices" in admin_ux.format_settings_hub() or "VPN notices" in admin_ux.format_settings_hub()
    hub = admin_ux.hub_keyboard(period_token="7")
    cbs = [b.callback_data for row in hub.inline_keyboard for b in row]
    assert "aux:promo:7" in cbs
    assert "aux:export:7" in cbs
    assert "aux:sys:7" in cbs
    assert "aux:export_run:30" in [
        b.callback_data for row in admin_ux.export_section_kb().inline_keyboard for b in row
    ]


def test_rent_estimate():
    assert admin_ux.rent_estimate_rub(monthly_rub=1000, days=30) == 1000.0
    assert admin_ux.rent_estimate_rub(monthly_rub=1000, days=7) == round(1000 * 7 / 30, 2)
    assert admin_ux.rent_estimate_rub(monthly_rub=0, days=7) == 0.0


def test_sales_screen_status_counts():
    text = admin_ux.format_sales_screen(
        period_label_s="7 дней",
        agg=_agg(),
        status_counts={
            "paid": 1,
            "processing": 1,
            "completed": 5,
            "cancelled": 2,
            "expired": 1,
            "pending_payment": 3,
        },
    )
    assert "Выручка" in text
    assert "Средний чек" in text
    assert "Выдано: <b>5</b>" in text
    assert "Оплачено (ещё не выдано): <b>2</b>" in text
    assert "Ждут оплаты: <b>3</b>" in text
    assert "Отмена/истёк: <b>3</b>" in text
    assert "VPN" in text
    assert "p95" not in text.lower()


def test_sales_section_kb_buttons():
    kb = admin_ux.sales_section_kb(period_token="7")
    labels = [b.text for row in kb.inline_keyboard for b in row]
    for need in ("Последние заказы", "Найти заказ", "По товарам", "Динамика"):
        assert any(need in (t or "") for t in labels), need
    cbs = [b.callback_data for row in kb.inline_keyboard for b in row]
    assert "aux:orders:7" in cbs
    assert "aux:find_order:7" in cbs


def test_orders_list_and_merge_kb():
    kb = admin_ux.orders_list_kb([101, 102, 103], period_token="30")
    cbs = [b.callback_data for row in kb.inline_keyboard for b in row]
    assert "aux:order:101:30" in cbs
    assert "aux:sales:30" in cbs
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    a = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="A", callback_data="adm:done:1")]]
    )
    b = admin_ux.order_card_back_kb(period_token="7", user_id=55)
    m = admin_ux.merge_inline_kb(a, b)
    assert len(m.inline_keyboard) == 1 + len(b.inline_keyboard)
    assert m.inline_keyboard[0][0].callback_data == "adm:done:1"
    assert any("aux:user:55:7" == x.callback_data for row in b.inline_keyboard for x in row)


def test_user_card_format_and_kb():
    text = admin_ux.format_user_card(
        user_id=42,
        username="demo",
        first_name="Demo",
        created_at="2026-01-01",
        referrer_id=7,
        stats={
            "spent_rub": 100.0,
            "completed_orders": 2,
            "ref_balance_rub": 5.0,
            "balance_rub": 1.0,
            "referral_invited_count": 3,
            "referral_buyers_completed_count": 1,
            "referral_commission_earned_rub": 10.0,
        },
        products={
            "open_orders": 1,
            "vpn_units": 1,
            "vpn_rub": 50.0,
            "stars_units": 0,
            "stars_rub": 0.0,
            "premium_units": 1,
            "premium_rub": 50.0,
        },
        vpn_status="active",
        vpn_until="2026-12-01",
        vpn_kind="paid",
    )
    assert "42" in text
    assert "Потрачено" in text
    assert "active" in text
    assert "p95" not in text.lower()
    kb = admin_ux.user_card_kb(user_id=42, period_token="7")
    cbs = [b.callback_data for row in kb.inline_keyboard for b in row]
    assert "aux:user_orders:42:7" in cbs
    assert "aux:user_vpn:42:7" in cbs
    hub = admin_ux.users_section_kb(period_token="30")
    assert any("aux:find_user:30" == b.callback_data for row in hub.inline_keyboard for b in row)
