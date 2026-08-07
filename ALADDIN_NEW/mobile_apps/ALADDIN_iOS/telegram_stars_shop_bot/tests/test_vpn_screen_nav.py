"""Навигация «Назад» и клавиатуры уровней VPN."""

from __future__ import annotations

from bot.handlers.vpn import _vpn_marketing_kb, _vpn_y_speed_html
from bot.services.vpn_screen_nav import (
    BTN_OK_MARKETING,
    VPN_NAV_MARKETING,
    kb_back_marketing,
)


def test_marketing_card_back_uses_nav_vpn() -> None:
    kb = kb_back_marketing()
    assert kb.inline_keyboard[0][0].text == BTN_OK_MARKETING
    assert kb.inline_keyboard[0][0].callback_data == VPN_NAV_MARKETING


def test_marketing_kb_has_no_help_or_policy_rows(monkeypatch) -> None:
    from bot.config import load_settings

    monkeypatch.setenv("BOT_TOKEN", "9:vpn-kb")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "k" * 32)
    s = load_settings()
    kb = _vpn_marketing_kb(s, show_continue=True)
    texts = [btn.text for row in kb.inline_keyboard for btn in row]
    assert "🌐 Тарифы VPN" in texts
    assert "🟢 Оплата" not in texts
    assert "🎬 Скачать Happ" in texts
    assert "🎬 Видео: скачать Happ в РФ" not in texts
    assert "Обход блокировок" not in texts
    assert "📖 Инструкция" not in texts
    assert "📖 Как подключить" not in texts
    assert "Политика конфиденциальности" not in texts


def test_vpn_tariffs_cta_by_status() -> None:
    from bot.services.vpn_connect_copy import vpn_tariffs_cta_label

    assert vpn_tariffs_cta_label(active=False) == "🌐 Тарифы VPN"
    assert vpn_tariffs_cta_label(active=True) == "💎 Продлить VPN"


def test_kb_happ_install_has_app_store_payment_connect() -> None:
    from bot.services.vpn_happ_constants import HAPP_IOS_APP_STORE_GLOBAL_URL
    from bot.services.vpn_screen_nav import VPN_NAV_MAIN, kb_happ_install_video_screen

    kb = kb_happ_install_video_screen(from_payment=True)
    texts = [btn.text for row in kb.inline_keyboard for btn in row]
    assert "📲 Открыть Happ в App Store" in texts
    assert "⬅️ К оплате" in texts
    assert "⬅️ К подключению VPN" in texts
    urls = [btn.url for row in kb.inline_keyboard for btn in row if btn.url]
    assert HAPP_IOS_APP_STORE_GLOBAL_URL in urls
    callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row if btn.callback_data]
    assert "vpn:legal:gate" in callbacks
    assert VPN_NAV_MAIN in callbacks

