from __future__ import annotations

import json

import pytest

from bot.services import captcha_repo, orders_repo, users_repo


@pytest.mark.asyncio
async def test_captcha_create_and_solve_correct(conn) -> None:
    cid = await captcha_repo.create_challenge(
        conn,
        user_id=42,
        purpose="onboarding",
        correct_idx=1,
        options_json=json.dumps(["🍌", "🥕", "🌹"], ensure_ascii=False),
        ttl_seconds=120,
    )
    ok = await captcha_repo.take_challenge_if_correct(
        conn, challenge_id=cid, user_id=42, purpose="onboarding", picked_idx=1
    )
    assert ok is True
    ok2 = await captcha_repo.take_challenge_if_correct(
        conn, challenge_id=cid, user_id=42, purpose="onboarding", picked_idx=1
    )
    assert ok2 is False


@pytest.mark.asyncio
async def test_captcha_wrong_answer_keeps_challenge_until_correct(conn) -> None:
    cid = await captcha_repo.create_challenge(
        conn,
        user_id=7,
        purpose="checkout",
        correct_idx=0,
        options_json=json.dumps(["⭐", "💎", "🍎"], ensure_ascii=False),
        ttl_seconds=120,
    )
    bad = await captcha_repo.take_challenge_if_correct(
        conn, challenge_id=cid, user_id=7, purpose="checkout", picked_idx=2
    )
    assert bad is False
    good = await captcha_repo.take_challenge_if_correct(
        conn, challenge_id=cid, user_id=7, purpose="checkout", picked_idx=0
    )
    assert good is True


@pytest.mark.asyncio
async def test_captcha_wrong_user(conn) -> None:
    cid = await captcha_repo.create_challenge(
        conn,
        user_id=1,
        purpose="onboarding",
        correct_idx=0,
        options_json=json.dumps(["a", "b", "c"], ensure_ascii=False),
    )
    ok = await captcha_repo.take_challenge_if_correct(
        conn, challenge_id=cid, user_id=999, purpose="onboarding", picked_idx=0
    )
    assert ok is False


@pytest.mark.asyncio
async def test_throttle_start_allowed_updates_timestamp(conn) -> None:
    await users_repo.upsert_user(conn, user_id=100, username="u", first_name="f")
    assert await users_repo.throttle_start_allowed(conn, 100, min_seconds=60) is True
    assert await users_repo.throttle_start_allowed(conn, 100, min_seconds=60) is False


@pytest.mark.asyncio
async def test_throttle_start_zero_always_true(conn) -> None:
    await users_repo.upsert_user(conn, user_id=101, username="u", first_name="f")
    assert await users_repo.throttle_start_allowed(conn, 101, min_seconds=0) is True
    assert await users_repo.throttle_start_allowed(conn, 101, min_seconds=0) is True


@pytest.mark.asyncio
async def test_allow_order_create_interval(conn) -> None:
    from bot.config import Settings

    settings = Settings()
    uid = 555
    await users_repo.upsert_user(conn, user_id=uid, username="x", first_name="y")
    assert await orders_repo.allow_order_create_interval(conn, uid, 10.0) is True
    await orders_repo.create_order(
        conn,
        user_id=uid,
        product_id="x",
        product_title="t",
        payment_method="fiat",
        usd_base=1.0,
        rub_before=100.0,
        rub_after=100.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note=None,
        status="pending_payment",
        usd_rub_rate_snapshot=float(settings.usd_rub_rate),
    )
    assert await orders_repo.allow_order_create_interval(conn, uid, 3600.0) is False
    assert await orders_repo.allow_order_create_interval(conn, uid, 0.0) is True


def test_onboarding_terms_includes_channel_link(monkeypatch: pytest.MonkeyPatch) -> None:
    from bot.config import Settings
    from bot.services import marketing

    monkeypatch.setenv("USD_RUB_RATE", "90")
    monkeypatch.setenv(
        "OFFICIAL_CHANNEL_INVITE_URL",
        "https://t.me/+xwj4zZo4bNphZjVi",
    )
    monkeypatch.setenv("REQUIRED_CHANNEL_INVITE_URL", "")
    s = Settings()
    html = marketing.onboarding_terms_caption_html(s)
    assert "Официальный канал" in html
    assert "xwj4zZo4bNphZjVi" in html
