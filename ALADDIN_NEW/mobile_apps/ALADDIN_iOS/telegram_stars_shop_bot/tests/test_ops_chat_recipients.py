"""Получатели ops: все ADMIN_IDS (+ опциональный ALERT-чат без дубля)."""

from __future__ import annotations

from bot.config import Settings
from bot.services.ops_chat import ops_chat_configured, ops_recipient_chat_ids


def test_ops_recipients_all_admins(monkeypatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "1:x")
    monkeypatch.setenv("ADMIN_IDS", "222,111")
    monkeypatch.setenv("ALERT_TELEGRAM_BOT_TOKEN", "9:alert")
    monkeypatch.setenv("ALERT_TELEGRAM_CHAT_ID", "")
    monkeypatch.setenv("API_KEY_PEPPER", "k" * 32)
    monkeypatch.setenv("USD_RUB_RATE", "75.0")
    s = Settings()
    assert ops_recipient_chat_ids(s) == ["111", "222"]
    assert ops_chat_configured(s) is True


def test_ops_recipients_admins_plus_group_no_dup(monkeypatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "1:x")
    monkeypatch.setenv("ADMIN_IDS", "493897224,744254201")
    monkeypatch.setenv("ALERT_TELEGRAM_BOT_TOKEN", "9:alert")
    monkeypatch.setenv("ALERT_TELEGRAM_CHAT_ID", "-100999")
    monkeypatch.setenv("API_KEY_PEPPER", "k" * 32)
    monkeypatch.setenv("USD_RUB_RATE", "75.0")
    s = Settings()
    assert ops_recipient_chat_ids(s) == ["493897224", "744254201", "-100999"]


def test_ops_recipients_personal_alert_deduped_with_admin(monkeypatch) -> None:
    """Личка админа в ALERT_CHAT не дублируется."""
    monkeypatch.setenv("BOT_TOKEN", "1:x")
    monkeypatch.setenv("ADMIN_IDS", "493897224,744254201")
    monkeypatch.setenv("ALERT_TELEGRAM_BOT_TOKEN", "9:alert")
    monkeypatch.setenv("ALERT_TELEGRAM_CHAT_ID", "493897224")
    monkeypatch.setenv("API_KEY_PEPPER", "k" * 32)
    monkeypatch.setenv("USD_RUB_RATE", "75.0")
    s = Settings()
    assert ops_recipient_chat_ids(s) == ["493897224", "744254201"]


def test_ops_not_configured_without_admins_and_chat(monkeypatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "1:x")
    monkeypatch.setenv("ADMIN_IDS", "")
    monkeypatch.setenv("ALERT_TELEGRAM_BOT_TOKEN", "9:alert")
    monkeypatch.setenv("ALERT_TELEGRAM_CHAT_ID", "")
    monkeypatch.setenv("API_KEY_PEPPER", "k" * 32)
    monkeypatch.setenv("USD_RUB_RATE", "75.0")
    s = Settings()
    assert ops_recipient_chat_ids(s) == []
    assert ops_chat_configured(s) is False
