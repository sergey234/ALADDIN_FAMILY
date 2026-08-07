"""Регрессия VPN legal gate: документы + одно «Продолжить», без галочек."""

from __future__ import annotations

import pytest

from bot.config import load_settings
from bot.services import users_repo
from bot.services.catalog import Product
from bot.services.vpn_legal_gate import (
    VPN_LEGAL_CONTINUE_BTN,
    VPN_LEGAL_CONTINUE_CALLBACK,
    VPN_LEGAL_GATE_CALLBACK,
    vpn_legal_gate_html,
    vpn_legal_gate_kb,
    vpn_purchase_html,
    vpn_purchase_kb,
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


@pytest.mark.asyncio
async def test_accept_vpn_legal_both(conn) -> None:
    uid = 990002
    await users_repo.upsert_user(conn, user_id=uid, username="t2", first_name="T")
    assert not await users_repo.has_vpn_legal_accepted(conn, uid)
    await users_repo.accept_vpn_legal_both(conn, uid)
    assert await users_repo.has_vpn_legal_accepted(conn, uid)


def _sample_vpn_products() -> list[Product]:
    return [
        Product(
            id="vpn_30d",
            kind="vpn",
            title="30 дней",
            emoji="🌐",
            price_usd=3.0,
            price_rub=200.0,
            vpn_subscription_days=30,
        ),
    ]


def test_vpn_legal_gate_html_docs_only(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:vpn-lg")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "g" * 32)
    monkeypatch.setenv("VPN_DOCS_PUBLIC_BASE", "https://aladdin-ai.ru/v1/legal")
    s = load_settings()
    products = _sample_vpn_products()
    html = vpn_legal_gate_html(s, products, flow="purchase")
    assert "Документы перед выбором тарифа" in html
    assert "🌐 Тарифы VPN" in html
    assert "vpn-aup" in html
    assert VPN_LEGAL_CONTINUE_BTN in html
    assert "Ознакомлен" not in html
    assert "Подтверждение документов" not in html
    assert "Тарифы и оплата" not in html
    assert "🟢 Оплата" not in html


def test_vpn_legal_gate_kb_no_checkboxes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:vpn-lg")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "g" * 32)
    monkeypatch.setenv("VPN_DOCS_PUBLIC_BASE", "https://aladdin-ai.ru/v1/legal")
    s = load_settings()
    products = _sample_vpn_products()
    kb = vpn_legal_gate_kb(s, products, flow="purchase")
    labels = [b.text for row in kb.inline_keyboard for b in row]
    assert "📄 Политика конфиденциальности" in labels
    assert "📄 Пользовательское соглашение" in labels
    assert VPN_LEGAL_CONTINUE_BTN in labels
    assert "🔑 Управление VPN" in labels
    assert not any("Ознакомлен" in t for t in labels)
    assert not any("30 дней" in t for t in labels)


def test_vpn_purchase_kb_has_tariffs(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:vpn-lg")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "g" * 32)
    s = load_settings()
    products = _sample_vpn_products()
    html = vpn_purchase_html(s, products)
    assert "Тарифы и оплата" in html
    kb = vpn_purchase_kb(s, products)
    labels = [b.text for row in kb.inline_keyboard for b in row]
    assert any("30 дней" in t and "200" in t for t in labels)
    assert not any("Ознакомлен" in t for t in labels)


@pytest.mark.asyncio
async def test_shop_terms_skips_vpn_legal_gate(conn) -> None:
    uid = 990003
    await users_repo.upsert_user(conn, user_id=uid, username="t3", first_name="T")
    await users_repo.accept_terms(conn, uid)
    assert await users_repo.has_vpn_legal_accepted(conn, uid)


def test_vpn_legal_callback_constants() -> None:
    assert VPN_LEGAL_GATE_CALLBACK == "vpn:legal:gate"
    assert VPN_LEGAL_CONTINUE_CALLBACK == "vpn:legal:continue"
