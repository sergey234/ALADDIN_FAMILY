"""Тесты экрана счёта для Stars/Premium (не только VPN)."""

from __future__ import annotations

import pytest

from bot.services.catalog import Product
from bot.services.checkout_client_copy import assert_no_forbidden_client_terms
from bot.services.order_invoice_screen import order_invoice_screen_html


@pytest.mark.asyncio
async def test_shop_order_invoice_html_stars_brief(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LAVA_SHOP_ID", "a81738ce-8116-4b99-bdd7-5338fab2162d")
    monkeypatch.setenv("LAVA_SECRET_KEY", "secret")
    monkeypatch.setenv("LAVA_HOOK_URL", "https://example.com/hook")
    from bot.config import load_settings

    s = load_settings()
    s.bot_token = "x"
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
    assert "USD" in html
    assert "Оплатите до" in html or "кнопку оплаты" in html.lower()
    assert "Счёт на оплату создан" not in html
    assert "База" not in html
    assert "USDT" not in html
    assert_no_forbidden_client_terms(html)
