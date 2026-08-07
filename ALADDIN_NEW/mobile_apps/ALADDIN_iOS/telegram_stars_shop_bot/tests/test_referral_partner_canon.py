"""Антиабуз вывода + уровни партнёра + начисления (канон 2026-07-28)."""

from __future__ import annotations

import pytest

from bot.config import load_settings
from bot.db.database import connect
from bot.services import balance_repo, orders_repo, ref_withdraw_repo, users_repo
from bot.services.order_flow import apply_completed_side_effects
from bot.services.referral_partner import (
    count_qualified_vpn_referrals,
    evaluate_withdraw_eligibility,
    level_for_qualified_count,
    user_has_own_paid_vpn_min_days,
    vpn_days_from_product_id,
)
from bot.services.referral_ux import referral_home_html, referral_stats_html, referral_withdraw_html


def test_vpn_days_and_levels() -> None:
    assert vpn_days_from_product_id("vpn_7d") == 7
    assert vpn_days_from_product_id("vpn_30d") == 30
    assert vpn_days_from_product_id("vpn_365d") == 365
    assert level_for_qualified_count(0)["id"] == "start"
    assert level_for_qualified_count(5)["vpn_first_percent"] == 20.0
    assert level_for_qualified_count(5)["stars_premium_percent"] == 2.0
    assert level_for_qualified_count(30)["id"] == "gold"
    assert level_for_qualified_count(30)["vpn_first_percent"] == 30.0


def test_min_withdraw_is_1000() -> None:
    assert ref_withdraw_repo.MIN_WITHDRAW_RUB == 1000.0


@pytest.mark.asyncio
async def test_qualified_count_ignores_7d(tmp_path) -> None:
    db = tmp_path / "q.db"
    conn = await connect(db)
    await users_repo.upsert_user(conn, user_id=1, username="ref", first_name="R")
    await users_repo.upsert_user(conn, user_id=2, username="a", first_name="A")
    await users_repo.upsert_user(conn, user_id=3, username="b", first_name="B")
    await conn.execute("UPDATE users SET referrer_id = 1 WHERE user_id IN (2, 3)")
    await conn.commit()
    await orders_repo.create_order(
        conn,
        user_id=2,
        product_id="vpn_7d",
        product_title="7d",
        payment_method="fiat",
        usd_base=1.0,
        rub_before=100.0,
        rub_after=100.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=1,
        commission_rub=0.0,
        user_note="@a",
        status="completed",
        product_kind="vpn",
    )
    oid30 = await orders_repo.create_order(
        conn,
        user_id=3,
        product_id="vpn_30d",
        product_title="30d",
        payment_method="fiat",
        usd_base=1.0,
        rub_before=200.0,
        rub_after=200.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=1,
        commission_rub=0.0,
        user_note="@b",
        status="completed",
        product_kind="vpn",
    )
    await conn.execute(
        "UPDATE orders SET fulfillment_applied_at = datetime('now') WHERE id IN "
        "(SELECT id FROM orders WHERE user_id IN (2, 3))"
    )
    await conn.commit()
    n = await count_qualified_vpn_referrals(conn, 1)
    assert n == 1
    assert await user_has_own_paid_vpn_min_days(conn, 3) is True
    assert await user_has_own_paid_vpn_min_days(conn, 2) is False
    _ = oid30
    await conn.close()


@pytest.mark.asyncio
async def test_withdraw_eligibility_gates(tmp_path) -> None:
    db = tmp_path / "e.db"
    conn = await connect(db)
    await users_repo.upsert_user(conn, user_id=10, username="me", first_name="M")
    await conn.execute("UPDATE users SET ref_balance_rub = 1500 WHERE user_id = 10")
    await conn.commit()
    el = await evaluate_withdraw_eligibility(
        conn, 10, balance=1500, min_withdraw_rub=1000, pending=False
    )
    assert el.balance_ok
    assert not el.ok
    assert not el.qualified_ok
    assert not el.own_vpn_ok
    html = referral_withdraw_html(balance=1500, pending=False, eligibility=el)
    assert "1000" in html
    assert "❌" in html
    await conn.close()


@pytest.mark.asyncio
async def test_stars_recurring_and_vpn_once(conn, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:x")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "k" * 32)
    monkeypatch.setenv("USD_RUB_RATE", "75")
    monkeypatch.setenv("REF_BONUS_VPN_ONLY", "false")
    settings = load_settings()

    await users_repo.upsert_user(conn, user_id=200, username="ref", first_name="R")
    await users_repo.upsert_user(conn, user_id=201, username="buy", first_name="B")
    await conn.execute("UPDATE users SET referrer_id = 200 WHERE user_id = 201")
    await conn.commit()

    # 1) Stars → 1% (start)
    oid1 = await orders_repo.create_order(
        conn,
        user_id=201,
        product_id="stars_100",
        product_title="Stars",
        payment_method="fiat",
        usd_base=1.0,
        rub_before=100.0,
        rub_after=100.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=200,
        commission_rub=0.0,
        user_note="@b",
        status="completed",
        product_kind="stars",
    )
    await apply_completed_side_effects(conn, oid1, settings)
    _m, b1 = await balance_repo.get_balances(conn, 200)
    assert b1 == pytest.approx(1.0)

    # 2) Stars again → +1%
    oid2 = await orders_repo.create_order(
        conn,
        user_id=201,
        product_id="stars_100",
        product_title="Stars2",
        payment_method="fiat",
        usd_base=1.0,
        rub_before=100.0,
        rub_after=100.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=200,
        commission_rub=0.0,
        user_note="@b",
        status="completed",
        product_kind="stars",
    )
    await apply_completed_side_effects(conn, oid2, settings)
    _m, b2 = await balance_repo.get_balances(conn, 200)
    assert b2 == pytest.approx(2.0)

    # 3) VPN 30d → 15% once
    oid3 = await orders_repo.create_order(
        conn,
        user_id=201,
        product_id="vpn_30d",
        product_title="VPN30",
        payment_method="fiat",
        usd_base=1.0,
        rub_before=200.0,
        rub_after=200.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=200,
        commission_rub=0.0,
        user_note="@b",
        status="completed",
        product_kind="vpn",
    )
    await apply_completed_side_effects(conn, oid3, settings)
    _m, b3 = await balance_repo.get_balances(conn, 200)
    assert b3 == pytest.approx(2.0 + 30.0)

    # 4) VPN again → no more rub
    oid4 = await orders_repo.create_order(
        conn,
        user_id=201,
        product_id="vpn_30d",
        product_title="VPN30b",
        payment_method="fiat",
        usd_base=1.0,
        rub_before=200.0,
        rub_after=200.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=200,
        commission_rub=0.0,
        user_note="@b",
        status="completed",
        product_kind="vpn",
    )
    await apply_completed_side_effects(conn, oid4, settings)
    _m, b4 = await balance_repo.get_balances(conn, 200)
    assert b4 == pytest.approx(32.0)


def test_home_copy_canon(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:x")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "k" * 32)
    monkeypatch.setenv("USD_RUB_RATE", "75")
    s = load_settings()
    html = referral_home_html(
        ref_link="https://t.me/bot?start=ref_1",
        invited=2,
        buyers=1,
        earned_rub=75.0,
        settings=s,
        qualified_vpn=0,
    )
    assert "Реферальный баланс" in html
    assert "1000" in html
    assert "Бонусный" not in html
    assert "он же" not in html
    assert "Stars/Premium" not in html
    assert "Stars" in html and "Premium" in html
    assert "Старт" in html or "15%" in html
    st = referral_stats_html(
        {
            "referral_invited_count": 1,
            "referral_buyers_completed_count": 1,
            "referral_vpn_buyers_completed_count": 0,
            "referral_commission_earned_rub": 10,
            "ref_balance_rub": 10,
        },
        s,
        qualified_vpn=0,
    )
    assert "Уровень" in st
    from bot.services.referral_ux import referral_boost_html

    boost = referral_boost_html({}, qualified_vpn=0)
    assert "Таблица уровней" in boost
    assert "Ваш уровень" in boost
    assert "%/" not in boost
    assert "Бонусный" not in boost
    assert "Stars/Premium" not in boost
