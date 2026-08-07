from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from bot.config import load_settings
from bot.handlers.common import checkout_captcha_pick
from bot.handlers.shop import AWAITING_CHECKOUT_AFTER_CAPTCHA, finalize_checkout_order, order_submit
from bot.services import captcha_repo, catalog, orders_repo, users_repo
from bot.states.checkout import CheckoutStates

_REPO_BOT = Path(__file__).resolve().parents[1] / "bot"
PRODUCTS_YAML = _REPO_BOT / "products.yaml"


def _products():
    return catalog.load_products(PRODUCTS_YAML)


def _mock_cb(*, user_id: int = 9001) -> MagicMock:
    cb = MagicMock()
    cb.data = "chk:c:1:0"
    cb.from_user = MagicMock()
    cb.from_user.id = user_id
    cb.message = MagicMock()
    cb.message.delete = AsyncMock()
    cb.message.edit_text = AsyncMock()
    cb.answer = AsyncMock()
    cb.bot = MagicMock()
    return cb


def _mock_state(*, data: dict | None = None, state: str | None = CheckoutStates.waiting_confirm.state) -> MagicMock:
    st = MagicMock()
    st.get_data = AsyncMock(return_value=data or {})
    st.get_state = AsyncMock(return_value=state)
    st.update_data = AsyncMock()
    st.clear = AsyncMock()
    st.set_state = AsyncMock()
    return st


async def _setup_checkout_user(conn, *, user_id: int = 9001) -> None:
    await users_repo.upsert_user(conn, user_id=user_id, username="buyer", first_name="B")
    await users_repo.complete_onboarding(conn, user_id)


async def _checkout_fsm_data() -> dict:
    return {
        AWAITING_CHECKOUT_AFTER_CAPTCHA: True,
        "product_id": "stars_100",
        "payment": "fiat",
        "recipient": "@recipient",
    }


async def _order_count(conn, user_id: int) -> int:
    return await orders_repo.count_user_orders(conn, user_id)


@pytest.mark.asyncio
async def test_checkout_captcha_wrong_answer_creates_no_order(conn) -> None:
    settings = load_settings()
    await _setup_checkout_user(conn)
    cid = await captcha_repo.create_challenge(
        conn,
        user_id=9001,
        purpose="checkout",
        correct_idx=1,
        options_json=json.dumps(["🍌", "🥕", "🌹"], ensure_ascii=False),
    )
    cb = _mock_cb()
    cb.data = f"chk:c:{cid}:0"
    state = _mock_state(data=await _checkout_fsm_data())

    await checkout_captcha_pick(cb, state, settings, conn, _products(), cb.bot)

    assert await _order_count(conn, 9001) == 0
    cb.answer.assert_awaited()
    alert = cb.answer.await_args
    assert alert.kwargs.get("show_alert") is True
    assert "Неверно" in (alert.args[0] if alert.args else "")


@pytest.mark.asyncio
async def test_checkout_captcha_success_without_resume_flag_creates_no_order(conn) -> None:
    settings = load_settings()
    await _setup_checkout_user(conn)
    cid = await captcha_repo.create_challenge(
        conn,
        user_id=9001,
        purpose="checkout",
        correct_idx=0,
        options_json=json.dumps(["⭐", "💎", "🍎"], ensure_ascii=False),
    )
    cb = _mock_cb()
    cb.data = f"chk:c:{cid}:0"
    state = _mock_state(data={"product_id": "stars_100", "payment": "fiat", "recipient": "@x"})

    await checkout_captcha_pick(cb, state, settings, conn, _products(), cb.bot)

    assert await _order_count(conn, 9001) == 0
    cb.answer.assert_awaited_once_with(
        "Сессия устарела. Вернитесь к оформлению заказа.", show_alert=True
    )


@pytest.mark.asyncio
async def test_checkout_captcha_success_auto_finalizes_order(conn, monkeypatch: pytest.MonkeyPatch) -> None:
    settings = load_settings()
    monkeypatch.setattr(settings, "order_create_min_interval_seconds", 0)
    await _setup_checkout_user(conn)
    cid = await captcha_repo.create_challenge(
        conn,
        user_id=9001,
        purpose="checkout",
        correct_idx=2,
        options_json=json.dumps(["🍌", "🥕", "🌹"], ensure_ascii=False),
    )
    cb = _mock_cb()
    cb.data = f"chk:c:{cid}:2"
    state = _mock_state(data=await _checkout_fsm_data())

    present = AsyncMock()
    notify = AsyncMock()
    monkeypatch.setattr("bot.handlers.shop._present_order_invoice", present)
    monkeypatch.setattr("bot.handlers.shop._notify_admins", notify)

    await checkout_captcha_pick(cb, state, settings, conn, _products(), cb.bot)

    assert await _order_count(conn, 9001) == 1
    present.assert_awaited_once()
    notify.assert_awaited_once()
    state.clear.assert_awaited()
    # once-per-order: после счёта капча сброшена — следующий заказ снова покажет проверку
    assert await users_repo.checkout_captcha_valid(conn, 9001) is False


@pytest.mark.asyncio
async def test_captcha_consumed_after_order_forces_next_prompt(conn, monkeypatch: pytest.MonkeyPatch) -> None:
    settings = load_settings()
    monkeypatch.setattr(settings, "order_create_min_interval_seconds", 0)
    monkeypatch.setattr(settings, "checkout_captcha_once_per_order", True)
    await _setup_checkout_user(conn)
    await users_repo.extend_checkout_captcha(conn, 9001, 900)
    assert await users_repo.checkout_captcha_valid(conn, 9001) is True

    cb = _mock_cb()
    state = _mock_state(
        data={"product_id": "stars_100", "payment": "fiat", "recipient": "@x"}
    )
    present = AsyncMock()
    monkeypatch.setattr("bot.handlers.shop._present_order_invoice", present)
    monkeypatch.setattr("bot.handlers.shop._notify_admins", AsyncMock())

    await finalize_checkout_order(cb, state, _products(), settings, conn, cb.bot)

    assert await _order_count(conn, 9001) == 1
    assert await users_repo.checkout_captcha_valid(conn, 9001) is False

    prompt = AsyncMock()
    finalize = AsyncMock()
    monkeypatch.setattr("bot.handlers.shop.emoji_captcha.prompt_checkout_captcha", prompt)
    monkeypatch.setattr("bot.handlers.shop.finalize_checkout_order", finalize)
    from bot.handlers.shop import _gate_captcha_or_finalize

    await _gate_captcha_or_finalize(cb, state, _products(), settings, conn, cb.bot)
    prompt.assert_awaited_once()
    finalize.assert_not_awaited()


@pytest.mark.asyncio
async def test_order_submit_without_captcha_sets_resume_flag_and_prompts(conn, monkeypatch: pytest.MonkeyPatch) -> None:
    settings = load_settings()
    await _setup_checkout_user(conn)
    cb = _mock_cb()
    cb.data = "order:submit"
    state = _mock_state(data={"product_id": "stars_100", "payment": "fiat", "recipient": "@x"})

    prompt = AsyncMock()
    finalize = AsyncMock()
    monkeypatch.setattr("bot.handlers.shop.emoji_captcha.prompt_checkout_captcha", prompt)
    monkeypatch.setattr("bot.handlers.shop.finalize_checkout_order", finalize)

    await order_submit(cb, state, _products(), settings, conn, cb.bot)

    state.update_data.assert_awaited_once_with(**{AWAITING_CHECKOUT_AFTER_CAPTCHA: True})
    prompt.assert_awaited_once()
    finalize.assert_not_awaited()


@pytest.mark.asyncio
async def test_finalize_checkout_order_respects_create_interval(conn, monkeypatch: pytest.MonkeyPatch) -> None:
    settings = load_settings()
    monkeypatch.setattr(settings, "order_create_min_interval_seconds", 3600)
    await _setup_checkout_user(conn)
    cb = _mock_cb()
    state = _mock_state(data={"product_id": "stars_100", "payment": "fiat", "recipient": "@x"})

    await orders_repo.create_order(
        conn,
        user_id=9001,
        product_id="stars_100",
        product_title="t",
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
        usd_rub_rate_snapshot=float(settings.usd_rub_rate),
    )

    await finalize_checkout_order(cb, state, _products(), settings, conn, cb.bot)

    assert await _order_count(conn, 9001) == 1
    cb.answer.assert_awaited_once_with("Слишком частые заказы. Подождите несколько секунд.", show_alert=True)
