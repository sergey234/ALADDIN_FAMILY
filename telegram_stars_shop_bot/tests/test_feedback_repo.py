from __future__ import annotations

import pytest

from bot.services import analytics_repo, feedback_repo, orders_repo, users_repo


@pytest.mark.asyncio
async def test_feedback_repo_save_and_recent(conn) -> None:
    fid = await feedback_repo.save_feedback(conn, user_id=95001, kind="nps", score=9, product_scope="shop")
    assert fid > 0
    assert await feedback_repo.has_recent_feedback(conn, user_id=95001, cooldown_days=30) is True
    assert await feedback_repo.has_recent_prompt(conn, user_id=95001, cooldown_days=30) is False
    await analytics_repo.log_event(conn, user_id=95001, event_type="feedback_prompt_sent", meta={"via": "test"})
    assert await feedback_repo.has_recent_prompt(conn, user_id=95001, cooldown_days=30) is True


@pytest.mark.asyncio
async def test_feedback_repo_candidate_selection(conn) -> None:
    await users_repo.upsert_user(conn, user_id=95011, username="u95011", first_name="A")
    await users_repo.upsert_user(conn, user_id=95012, username="u95012", first_name="B")
    await orders_repo.create_order(
        conn,
        user_id=95011,
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
    await orders_repo.create_order(
        conn,
        user_id=95012,
        product_id="premium_1",
        product_title="💎 Premium 1m",
        payment_method="fiat",
        usd_base=1.0,
        rub_before=200.0,
        rub_after=200.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note="@b",
        status="completed",
        product_kind="premium",
        stars_qty=None,
        premium_months=1,
    )
    await feedback_repo.save_feedback(conn, user_id=95011, kind="csat", score=5, product_scope="shop")
    ids = await feedback_repo.list_survey_candidates(conn, lookback_days=45, cooldown_days=30, limit=100)
    assert 95012 in ids
    assert 95011 not in ids
