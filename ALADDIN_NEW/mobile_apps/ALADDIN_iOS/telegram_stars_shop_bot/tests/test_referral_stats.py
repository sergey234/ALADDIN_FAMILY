from __future__ import annotations

import pytest

from bot.config import load_settings
from bot.services import orders_repo, users_repo
from bot.services.order_flow import apply_completed_side_effects


@pytest.mark.asyncio
async def test_user_stats_referral_fields(conn, monkeypatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:ref-stats")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "ref_stats_test_pepper_minimum_32_chars")
    settings = load_settings()

    await users_repo.upsert_user(conn, user_id=9100, username="ref", first_name="R")
    await users_repo.upsert_user(conn, user_id=9101, username="b1", first_name="B")
    await users_repo.upsert_user(conn, user_id=9102, username="b2", first_name="B2")
    await conn.execute("UPDATE users SET referrer_id = 9100 WHERE user_id IN (9101, 9102)")
    await conn.commit()

    st0 = await users_repo.user_stats(conn, 9100)
    assert st0["referral_invited_count"] == 2
    assert st0["referral_buyers_completed_count"] == 0
    assert st0["referral_commission_earned_rub"] == 0.0

    oid = await orders_repo.create_order(
        conn,
        user_id=9101,
        product_id="s",
        product_title="S",
        payment_method="fiat",
        usd_base=1.0,
        rub_before=100.0,
        rub_after=100.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=9100,
        commission_rub=0.0,
        user_note="@x",
        status="completed",
    )
    await apply_completed_side_effects(conn, oid, settings)

    st1 = await users_repo.user_stats(conn, 9100)
    assert st1["referral_invited_count"] == 2
    assert st1["referral_buyers_completed_count"] == 1
    assert float(st1["referral_commission_earned_rub"]) == pytest.approx(
        100.0 * (settings.ref_commission_percent / 100.0), rel=1e-3
    )
