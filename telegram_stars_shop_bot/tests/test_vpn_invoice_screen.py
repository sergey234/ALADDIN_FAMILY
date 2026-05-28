"""Экран счёта VPN и колбэки pay:inv:*."""

from __future__ import annotations

from pathlib import Path

from bot.config import Settings
from bot.services.catalog import Product
from bot.services.lava_api import lava_invoice_signing_payload
from bot.services.vpn_invoice_screen import (
    invoice_pay_deadline_msk,
    vpn_invoice_fiat_channel_tail_html,
    vpn_invoice_screen_html,
)
from bot.services.vpn_subscription_dates import (
    compute_paid_until_after_purchase,
    format_paid_until_display_msk,
)
ROOT = Path(__file__).resolve().parents[1]
SHOP_PY = (ROOT / "bot" / "handlers" / "shop.py").read_text(encoding="utf-8")
SHOP_KB = (ROOT / "bot" / "keyboards" / "shop_kb.py").read_text(encoding="utf-8")


def test_lava_payload_include_service_sbp_only() -> None:
    p = lava_invoice_signing_payload(
        shop_id="s",
        order_id="42",
        sum_rub=100.0,
        expire_minutes=60,
        hook_url="https://h",
        success_url=None,
        fail_url=None,
        comment="ORDER42",
        include_service=["sbp"],
    )
    assert p["includeService"] == ["sbp"]


def test_invoice_deadline_crypto_60_min() -> None:
    s = Settings(bot_token="x")
    d = invoice_pay_deadline_msk(s, payment_method="crypto")
    assert d.endswith("МСК")
    assert ":" in d


def test_compute_paid_until_extends_from_current() -> None:
    cur = "2030-01-01T00:00:00+00:00"
    nxt = compute_paid_until_after_purchase(current_paid_until=cur, days=30)
    assert "2030" in nxt


def test_format_paid_until_msk() -> None:
    disp = format_paid_until_display_msk("2030-06-15T12:00:00+00:00")
    assert "." in disp


async def test_vpn_invoice_html_contains_devices_line() -> None:
    s = Settings(bot_token="x", lava_invoice_expire_minutes=30)
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
    assert "Счёт на оплату" in html
    assert "199.00" in html
    assert "несколько устройств" in html.lower() or "телефон" in html


def test_vpn_invoice_kb_source_has_channels() -> None:
    assert "VPN_SBP_INVOICE_BTN" in SHOP_KB
    assert 'pay:inv:sbp:{order_id}' in SHOP_KB
    assert 'pay:inv:card:{order_id}' in SHOP_KB
    assert 'pay:inv:crypto:{order_id}' in SHOP_KB
    assert 'pay:inv:cancel:{order_id}' in SHOP_KB


def test_shop_has_pay_inv_router() -> None:
    assert 'F.data.startswith("pay:inv:")' in SHOP_PY
    assert "_present_vpn_order_invoice" in SHOP_PY
    assert "include_service=[lava_service]" in SHOP_PY


def test_fiat_channel_tail_legacy() -> None:
    t = vpn_invoice_fiat_channel_tail_html(channel_label="🍐 СБП")
    assert "оплат" in t.lower()
