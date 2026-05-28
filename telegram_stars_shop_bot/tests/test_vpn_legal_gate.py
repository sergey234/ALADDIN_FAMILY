from __future__ import annotations

import pytest

from bot.config import load_settings
from bot.services import users_repo
from bot.services.catalog import Product
from bot.services.vpn_legal_gate import (
    VPN_LEGAL_CONTINUE_CALLBACK,
    VPN_LEGAL_GATE_CALLBACK,
    vpn_legal_gate_html,
)


@pytest.mark.asyncio
async def test_vpn_legal_requires_both_acks(conn) -> None:
    uid = 990001
    await users_repo.upsert_user(conn, user_id=uid, username="t", first_name="T")
    assert not await users_repo.has_vpn_legal_accepted(conn, uid)
    await users_repo.accept_vpn_privacy(conn, uid)
    assert not await users_repo.has_vpn_legal_accepted(conn, uid)
    await users_repo.accept_vpn_terms(conn, uid)
    assert await users_repo.has_vpn_legal_accepted(conn, uid)


def _sample_vpn_products() -> list[Product]:
    return [
        Product(
            id="vpn_30d",
            kind="vpn",
            title="30 дней",
            emoji="🌐",
            price_usd=3.0,
            price_rub=290.0,
            vpn_subscription_days=30,
        ),
    ]


def test_vpn_legal_gate_html_tariffs_above_legal(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:vpn-lg")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "g" * 32)
    monkeypatch.setenv("VPN_DOCS_PUBLIC_BASE", "https://aladdin-ai.ru/v1/legal")
    s = load_settings()
    products = _sample_vpn_products()
    html = vpn_legal_gate_html(s, products, privacy_ok=True, terms_ok=False)
    assert "☐" in html or "✅" in html
    assert "Тарифы и оплата" in html
    assert "Документы перед оплатой" in html
    assert "vpn-aup" in html
    t_pos = html.index("Тарифы и оплата")
    d_pos = html.index("Документы перед оплатой")
    assert t_pos < d_pos


def test_vpn_legal_callback_constants() -> None:
    assert VPN_LEGAL_GATE_CALLBACK == "vpn:legal:gate"
    assert VPN_LEGAL_CONTINUE_CALLBACK == "vpn:legal:continue"
