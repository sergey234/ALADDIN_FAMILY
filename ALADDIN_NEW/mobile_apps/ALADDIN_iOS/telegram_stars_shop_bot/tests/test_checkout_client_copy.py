"""Клиентские тексты checkout: ₽/USD/получатель, без техтерминов."""

from __future__ import annotations

import pytest

from bot.config import Settings
from bot.services.checkout_client_copy import (
    FORBIDDEN_CLIENT_TERMS,
    ask_username_html,
    assert_no_forbidden_client_terms,
    invoice_brief_html,
    offer_with_recipient_choice_html,
    payment_methods_intro_html,
    price_block_html,
    review_html,
    vpn_invoice_brief_html,
    vpn_offer_html,
)
from bot.services.order_invoice_screen import order_invoice_screen_html
from bot.services.catalog import Product
from bot.services.vpn_invoice_screen import vpn_invoice_screen_html
from bot.keyboards.shop_kb import go_to_payment_kb, recipient_dest_kb


def _settings() -> Settings:
    return Settings.model_validate({"BOT_TOKEN": "x", "USD_RUB_RATE": "80"})


def test_price_block_has_rub_usd_no_forbidden() -> None:
    s = _settings()
    html = price_block_html(s, 800.0, catalog_usd=10.0)
    assert "800.00" in html
    assert "USD" in html
    assert_no_forbidden_client_terms(html)
    for t in FORBIDDEN_CLIENT_TERMS:
        assert t.lower() not in html.lower()


def test_stars_offer_and_review() -> None:
    s = _settings()
    offer = offer_with_recipient_choice_html(
        s, title="⭐ 100 Stars", rub=160.0, catalog_usd=2.0, kind="stars"
    )
    assert "Кому отправить Stars" in offer
    assert_no_forbidden_client_terms(offer)

    rev = review_html(
        s,
        title="⭐ 100 Stars",
        rub=160.0,
        catalog_usd=2.0,
        recipient="@alice",
        for_self=True,
        kind="stars",
    )
    assert "Покупка для себя" in rev
    assert "@alice" in rev
    assert_no_forbidden_client_terms(rev)

    gift = review_html(
        s,
        title="⭐ 100 Stars",
        rub=160.0,
        catalog_usd=2.0,
        recipient="@bob",
        for_self=False,
        kind="stars",
    )
    assert "@bob" in gift
    assert_no_forbidden_client_terms(gift)


def test_premium_same_templates() -> None:
    s = _settings()
    offer = offer_with_recipient_choice_html(
        s, title="💎 Premium 3 мес.", rub=1200.0, catalog_usd=15.0, kind="premium"
    )
    assert "Premium" in offer
    assert_no_forbidden_client_terms(offer)
    ask = ask_username_html(kind="premium")
    assert "@username" in ask.lower() or "username" in ask.lower()


def test_vpn_offer_same_price_block_as_stars() -> None:
    s = _settings()
    html = vpn_offer_html(s, title="🌐 30 дней", rub=199.0, catalog_usd=3.0)
    assert "по курсу ЦБ" in html
    assert "наценка" not in html
    assert "USDT" not in html
    assert_no_forbidden_client_terms(html)


def test_payment_intro_and_invoice_fiat_no_usdt() -> None:
    s = _settings()
    pay = payment_methods_intro_html(
        s, title="⭐ 100 Stars", rub=160.0, catalog_usd=2.0, recipient="@me"
    )
    assert "способ оплаты" in pay.lower()
    assert "USDT" not in pay
    assert_no_forbidden_client_terms(pay)

    inv = invoice_brief_html(
        s,
        title="⭐ 100 Stars",
        rub=160.0,
        catalog_usd=2.0,
        recipient="@me",
        deadline="12:00:00 МСК",
        pay_crypto=False,
    )
    assert "USDT" not in inv
    assert_no_forbidden_client_terms(inv)

    cry = invoice_brief_html(
        s,
        title="⭐ 100 Stars",
        rub=160.0,
        recipient="@me",
        pay_crypto=True,
    )
    assert "USDT" in cry


def test_keyboards_cta() -> None:
    kb = recipient_dest_kb("stars_100")
    texts = [b.text for row in kb.inline_keyboard for b in row]
    assert any("Себе" in t for t in texts)
    assert any("Другому" in t for t in texts)

    pay = go_to_payment_kb("stars_100", gift=False)
    pay_texts = [b.text for row in pay.inline_keyboard for b in row]
    assert any("Перейти к оплате" in t for t in pay_texts)


@pytest.mark.asyncio
async def test_order_invoice_brief_no_forbidden() -> None:
    s = _settings()
    p = Product(
        id="stars_100",
        kind="stars",
        title="100 Stars",
        emoji="⭐",
        price_usd=1.8,
        stars=100,
        sort_order=0,
    )
    html = await order_invoice_screen_html(
        s,
        None,
        order_id=99,
        rub_due=150.0,
        product=p,
        telegram_user_id=1,
        payment_method="fiat",
        recipient_note="@buyer",
    )
    assert "150.00" in html
    assert "@buyer" in html
    assert "Счёт на оплату создан" not in html
    assert "USDT" not in html
    assert_no_forbidden_client_terms(html)


@pytest.mark.asyncio
async def test_vpn_invoice_brief_no_forbidden() -> None:
    s = Settings.model_validate({"BOT_TOKEN": "x", "USD_RUB_RATE": "80", "LAVA_INVOICE_EXPIRE_MINUTES": "30"})
    p = Product(
        id="vpn_30d",
        kind="vpn",
        title="30 дней",
        emoji="🌐",
        price_usd=3.0,
        vpn_subscription_days=30,
        sort_order=1,
    )
    html = await vpn_invoice_screen_html(
        s,
        None,
        order_id=7,
        rub_due=199.0,
        product=p,
        telegram_user_id=1,
        payment_method="fiat",
    )
    assert "199.00" in html
    assert "по курсу ЦБ" in html
    assert "наценка" not in html
    assert "USDT" not in html
    assert_no_forbidden_client_terms(html)
    # crypto path may mention USDT
    html_c = await vpn_invoice_screen_html(
        s,
        None,
        order_id=7,
        rub_due=199.0,
        product=p,
        telegram_user_id=1,
        payment_method="crypto",
    )
    assert "USDT" in html_c
