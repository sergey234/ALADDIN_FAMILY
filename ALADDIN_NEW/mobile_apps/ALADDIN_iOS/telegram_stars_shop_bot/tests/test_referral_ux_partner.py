"""Реферальный UX: тексты, shop-wide bonus spend, override."""

from __future__ import annotations

import pytest

from bot.config import load_settings
from bot.services import balance_repo, orders_repo, users_repo
from bot.services.dual_wallet import wallet_plan_for_kind
from bot.services.order_flow import apply_completed_side_effects
from bot.services.pricing import commission_for_first_order
from bot.services.referral_ux import referral_boost_html, referral_home_html, referral_stats_html


def _settings(monkeypatch: pytest.MonkeyPatch, **env: str):
    monkeypatch.setenv("BOT_TOKEN", "9:refux")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "k" * 32)
    monkeypatch.setenv("USD_RUB_RATE", "75")
    monkeypatch.setenv("REF_BONUS_VPN_ONLY", "false")
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    return load_settings()


def test_referral_home_copy(monkeypatch: pytest.MonkeyPatch) -> None:
    s = _settings(monkeypatch)
    html = referral_home_html(
        ref_link="https://t.me/bot?start=ref_1",
        invited=2,
        buyers=1,
        earned_rub=75.0,
        settings=s,
        qualified_vpn=0,
    )
    assert "С выданной покупкой" in html
    assert "15%" in html
    assert "1000" in html
    assert "VPN" in html and "Stars" in html
    assert "Telegram" in html
    assert "VLESS" not in html


def test_referral_home_shows_web_link(monkeypatch: pytest.MonkeyPatch) -> None:
    s = _settings(monkeypatch)
    html = referral_home_html(
        ref_link="https://t.me/bot?start=ref_1",
        web_ref_link="https://get.aladdin-ai.ru/r/AbCdEf12",
        invited=0,
        buyers=0,
        earned_rub=0.0,
        settings=s,
    )
    assert "get.aladdin-ai.ru/r/AbCdEf12" in html
    assert "Сайт" in html


def test_referral_stats_and_boost_progress(monkeypatch: pytest.MonkeyPatch) -> None:
    s = _settings(monkeypatch)
    stats = {
        "referral_invited_count": 7,
        "referral_buyers_completed_count": 4,
        "referral_vpn_buyers_completed_count": 3,
        "referral_commission_earned_rub": 120.0,
        "ref_balance_rub": 50.0,
        "ref_partner_status": "basic",
    }
    st = referral_stats_html(stats, s, qualified_vpn=3)
    assert "Уровень" in st
    assert "Старт" in st
    assert "Stars и Premium" in st
    assert "Stars/Premium" not in st
    boost = referral_boost_html(stats, qualified_vpn=3)
    assert "Таблица уровней" in boost
    assert "15%/1%" not in boost
    assert "/1%" not in boost
    assert "Stars и Premium" in boost
    assert "Ваш уровень" in boost
    boost5 = referral_boost_html(stats, qualified_vpn=5)
    assert "Бронза" in boost5
    assert "VPN <b>20%</b>" in boost5 or "20%" in boost5


def test_commission_override() -> None:
    class _S:
        ref_commission_percent = 15.0

    assert commission_for_first_order(100.0, _S()) == 15.0  # type: ignore[arg-type]
    assert commission_for_first_order(100.0, _S(), override_percent=30) == 30.0  # type: ignore[arg-type]


def test_shop_wide_bonus_spend_plan() -> None:
    plan = wallet_plan_for_kind("stars", 100, 20, 90, ref_bonus_vpn_only=False)
    assert plan.bonus_use == pytest.approx(90.0)
    assert plan.main_use == pytest.approx(10.0)


@pytest.mark.asyncio
async def test_stars_paid_with_bonus_when_shop_wide(conn, monkeypatch) -> None:
    settings = _settings(monkeypatch)
    await users_repo.upsert_user(conn, user_id=9601, username="u", first_name="U")
    await conn.execute(
        "UPDATE users SET balance_rub = 10, ref_balance_rub = 200 WHERE user_id = 9601"
    )
    await conn.commit()
    oid = await orders_repo.create_paid_order_from_balance(
        conn,
        user_id=9601,
        product_id="stars_100",
        product_title="Stars",
        usd_base=1.0,
        rub_before=100.0,
        rub_after=100.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        user_note="@u",
        settings=settings,
        product_kind="stars",
    )
    order = await orders_repo.get_order(conn, oid)
    assert float(order["bonus_applied_rub"] or 0) == pytest.approx(100.0)
    main, bonus = await balance_repo.get_balances(conn, 9601)
    assert main == pytest.approx(10.0)
    assert bonus == pytest.approx(100.0)


@pytest.mark.asyncio
async def test_partner_override_on_first_order(conn, monkeypatch) -> None:
    settings = _settings(monkeypatch, REF_REFERRER_COMMISSION_FIRST_ORDER_PERCENT="15")
    await users_repo.upsert_user(conn, user_id=9701, username="buyer", first_name="B")
    await users_repo.upsert_user(conn, user_id=9702, username="ref", first_name="R")
    await conn.execute(
        """
        UPDATE users
        SET referrer_id = 9702
        WHERE user_id = 9701
        """
    )
    await conn.execute(
        """
        UPDATE users
        SET ref_partner_status = 'partner', ref_commission_override_pct = 30
        WHERE user_id = 9702
        """
    )
    await conn.commit()
    oid = await orders_repo.create_order(
        conn,
        user_id=9701,
        product_id="s",
        product_title="S",
        payment_method="fiat",
        usd_base=1.0,
        rub_before=100.0,
        rub_after=100.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=9702,
        commission_rub=0.0,
        user_note="@x",
        status="completed",
        product_kind="stars",
    )
    await apply_completed_side_effects(conn, oid, settings)
    _main, bonus = await balance_repo.get_balances(conn, 9702)
    assert bonus == pytest.approx(30.0)
