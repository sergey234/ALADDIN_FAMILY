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
    assert "🟢 Оплата" in texts
    assert "📖 Инструкция" not in texts
    assert "📖 Как подключить" not in texts
    assert "Политика конфиденциальности" not in texts


def test_speed_card_copy_mentions_gbit() -> None:
    assert "10 Гбит" in _vpn_y_speed_html()
