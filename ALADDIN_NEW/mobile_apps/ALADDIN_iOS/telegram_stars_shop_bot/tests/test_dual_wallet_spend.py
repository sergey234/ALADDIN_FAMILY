from __future__ import annotations

import pytest

from bot.config import load_settings
from bot.services import balance_repo, orders_repo, users_repo
from bot.services.dual_wallet import (
    MSG_BONUS_FORBIDDEN,
    MSG_INSUFFICIENT_MAIN,
    user_message_for_wallet_error,
    wallet_plan_for_kind,
)
from bot.services.order_flow import apply_completed_side_effects


def _settings(monkeypatch: pytest.MonkeyPatch, **env: str):
    monkeypatch.setenv("BOT_TOKEN", "9:dual-wallet-test")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("REF_BONUS_VPN_ONLY", "true")
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    return load_settings()


@pytest.mark.asyncio
async def test_commission_credits_bonus_only(conn, monkeypatch) -> None:
    settings = _settings(monkeypatch, REF_REFERRER_COMMISSION_FIRST_ORDER_PERCENT="15")
    await users_repo.upsert_user(conn, user_id=9101, username="buyer", first_name="B")
    await users_repo.upsert_user(conn, user_id=9102, username="ref", first_name="R")
    await conn.execute("UPDATE users SET referrer_id = 9102 WHERE user_id = 9101")
    await conn.commit()

    oid = await orders_repo.create_order(
        conn,
        user_id=9101,
        product_id="stars_100",
        product_title="Stars",
        payment_method="fiat",
        usd_base=1.0,
        rub_before=100.0,
        rub_after=100.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=9102,
        commission_rub=0.0,
        user_note="@x",
        status="completed",
        product_kind="stars",
    )
    await apply_completed_side_effects(conn, oid, settings)

    main, bonus = await balance_repo.get_balances(conn, 9102)
    assert main == pytest.approx(0.0)
    # Старт: Stars/Premium 1% с каждой покупки
    assert bonus == pytest.approx(1.0)
    cur = await conn.execute(
        "SELECT kind FROM ledger WHERE user_id = 9102 ORDER BY id DESC LIMIT 1"
    )
    row = await cur.fetchone()
    assert row is not None
    assert row["kind"] == "bonus_credit"


@pytest.mark.asyncio
async def test_stars_reject_when_only_bonus(conn, monkeypatch) -> None:
    settings = _settings(monkeypatch)
    await users_repo.upsert_user(conn, user_id=9201, username="u", first_name="U")
    await conn.execute(
        "UPDATE users SET balance_rub = 0, ref_balance_rub = 200 WHERE user_id = 9201"
    )
    await conn.commit()

    with pytest.raises(ValueError, match="insufficient_main"):
        await orders_repo.create_paid_order_from_balance(
            conn,
            user_id=9201,
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
    main, bonus = await balance_repo.get_balances(conn, 9201)
    assert main == pytest.approx(0.0)
    assert bonus == pytest.approx(200.0)


@pytest.mark.asyncio
async def test_premium_reject_when_only_bonus(conn, monkeypatch) -> None:
    settings = _settings(monkeypatch)
    await users_repo.upsert_user(conn, user_id=9202, username="u", first_name="U")
    await conn.execute(
        "UPDATE users SET balance_rub = 0, ref_balance_rub = 500 WHERE user_id = 9202"
    )
    await conn.commit()

    with pytest.raises(ValueError, match="insufficient_main"):
        await orders_repo.create_paid_order_from_balance(
            conn,
            user_id=9202,
            product_id="prem_3",
            product_title="Premium",
            usd_base=5.0,
            rub_before=450.0,
            rub_after=450.0,
            referral_discount_rub=0.0,
            wholesale_discount_rub=0.0,
            referrer_id=None,
            user_note="@u",
            settings=settings,
            product_kind="premium",
            premium_months=3,
        )


@pytest.mark.asyncio
async def test_vpn_bonus_only_spend(conn, monkeypatch) -> None:
    settings = _settings(monkeypatch)
    await users_repo.upsert_user(conn, user_id=9301, username="u", first_name="U")
    await conn.execute(
        "UPDATE users SET balance_rub = 10, ref_balance_rub = 200 WHERE user_id = 9301"
    )
    await conn.commit()

    oid = await orders_repo.create_paid_order_from_balance(
        conn,
        user_id=9301,
        product_id="vpn_30",
        product_title="VPN",
        usd_base=2.0,
        rub_before=150.0,
        rub_after=150.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        user_note="self",
        settings=settings,
        product_kind="vpn",
    )
    order = await orders_repo.get_order(conn, oid)
    assert float(order["balance_applied_rub"] or 0) == pytest.approx(0.0)
    assert float(order["bonus_applied_rub"] or 0) == pytest.approx(150.0)
    main, bonus = await balance_repo.get_balances(conn, 9301)
    assert main == pytest.approx(10.0)
    assert bonus == pytest.approx(50.0)


@pytest.mark.asyncio
async def test_vpn_split_bonus_then_main(conn, monkeypatch) -> None:
    settings = _settings(monkeypatch)
    await users_repo.upsert_user(conn, user_id=9302, username="u", first_name="U")
    await conn.execute(
        "UPDATE users SET balance_rub = 80, ref_balance_rub = 70 WHERE user_id = 9302"
    )
    await conn.commit()

    oid = await orders_repo.create_paid_order_from_balance(
        conn,
        user_id=9302,
        product_id="vpn_30",
        product_title="VPN",
        usd_base=2.0,
        rub_before=100.0,
        rub_after=100.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        user_note="self",
        settings=settings,
        product_kind="vpn",
    )
    order = await orders_repo.get_order(conn, oid)
    assert float(order["bonus_applied_rub"] or 0) == pytest.approx(70.0)
    assert float(order["balance_applied_rub"] or 0) == pytest.approx(30.0)
    main, bonus = await balance_repo.get_balances(conn, 9302)
    assert main == pytest.approx(50.0)
    assert bonus == pytest.approx(0.0)


@pytest.mark.asyncio
async def test_vpn_mix_partial_bonus_first(conn, monkeypatch) -> None:
    settings = _settings(monkeypatch)
    await users_repo.upsert_user(conn, user_id=9303, username="u", first_name="U")
    await conn.execute(
        "UPDATE users SET balance_rub = 20, ref_balance_rub = 40 WHERE user_id = 9303"
    )
    await conn.commit()

    oid = await orders_repo.create_order_with_balance_partial(
        conn,
        user_id=9303,
        product_id="vpn_30",
        product_title="VPN",
        payment_method="mix_fiat",
        usd_base=2.0,
        rub_before=200.0,
        rub_invoice_total=200.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        user_note="self",
        balance_apply=50.0,
        settings=settings,
        product_kind="vpn",
    )
    order = await orders_repo.get_order(conn, oid)
    assert str(order["status"]) == "pending_payment"
    assert float(order["bonus_applied_rub"] or 0) == pytest.approx(40.0)
    assert float(order["balance_applied_rub"] or 0) == pytest.approx(10.0)
    assert orders_repo.amount_due_external(order) == pytest.approx(150.0)


@pytest.mark.asyncio
async def test_topup_credits_main_only(conn, monkeypatch) -> None:
    settings = _settings(monkeypatch, TOPUP_MIN_RUB="50")
    await users_repo.upsert_user(conn, user_id=9401, username="u", first_name="U")
    await conn.execute(
        "UPDATE users SET balance_rub = 0, ref_balance_rub = 77 WHERE user_id = 9401"
    )
    await conn.commit()
    tid = await balance_repo.create_topup_request(
        conn, user_id=9401, amount_rub=100.0, settings=settings
    )
    ok = await balance_repo.approve_topup(conn, tid)
    assert ok is True
    main, bonus = await balance_repo.get_balances(conn, 9401)
    assert main == pytest.approx(100.0)
    assert bonus == pytest.approx(77.0)


def test_wallet_plan_messages() -> None:
    with pytest.raises(ValueError, match="insufficient_main"):
        wallet_plan_for_kind("stars", 50, 0, 100)
    assert user_message_for_wallet_error("bonus_forbidden_for_product") == MSG_BONUS_FORBIDDEN
    assert user_message_for_wallet_error("insufficient_main") == MSG_INSUFFICIENT_MAIN
