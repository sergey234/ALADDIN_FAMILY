"""Integration-ish: orchestrator with mock LLM (T1/T6/T8/T13) + hub button."""

from __future__ import annotations

import pytest

from bot.assistant.access import assistant_menu_visible
from bot.assistant.kb import build_kb
from bot.assistant.llm_client import LLMResult
from bot.assistant.orchestrator import handle_user_message
from bot.config import load_settings
from bot.keyboards.shop_kb import hub_menu_kb


@pytest.mark.asyncio
async def test_refund_escalates_without_llm(conn, monkeypatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "1:t")
    monkeypatch.setenv("USD_RUB_RATE", "90")
    monkeypatch.setenv("ASSISTANT_ENABLED", "true")
    monkeypatch.setenv("ASSISTANT_ADMIN_ONLY", "false")
    s = load_settings()
    await build_kb(conn, s)
    await conn.execute("INSERT OR IGNORE INTO users (user_id) VALUES (55)")
    await conn.commit()
    res = await handle_user_message(
        conn, s, user_id=55, text="Верните деньги за заказ", username="u55"
    )
    assert res.escalate_ticket_id is not None
    assert "Тикет" in res.html or "тикет" in res.html.lower()


@pytest.mark.asyncio
async def test_llm_down_fallback(conn, monkeypatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "1:t")
    monkeypatch.setenv("USD_RUB_RATE", "90")
    monkeypatch.setenv("ASSISTANT_LLM_BASE_URL", "https://example.invalid/v1")
    monkeypatch.setenv("ASSISTANT_LLM_API_KEY", "sk-test")
    monkeypatch.setenv("ASSISTANT_LLM_MODEL", "test-model")
    s = load_settings()
    await build_kb(conn, s)
    await conn.execute("INSERT OR IGNORE INTO users (user_id) VALUES (56)")
    await conn.commit()

    async def _fail(*_a, **_k):
        return LLMResult(ok=False, text="", error="http_500")

    monkeypatch.setattr("bot.assistant.orchestrator.chat_complete", _fail)
    res = await handle_user_message(
        conn, s, user_id=56, text="Как подключить Happ на Android?", username=None
    )
    assert res.llm_down is True
    assert "недоступен" in res.html.lower() or "человек" in res.html.lower()


@pytest.mark.asyncio
async def test_happy_path_mock_llm(conn, monkeypatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "1:t")
    monkeypatch.setenv("USD_RUB_RATE", "90")
    monkeypatch.setenv("ASSISTANT_LLM_BASE_URL", "https://example.invalid/v1")
    monkeypatch.setenv("ASSISTANT_LLM_API_KEY", "sk-test")
    monkeypatch.setenv("ASSISTANT_LLM_MODEL", "test-model")
    s = load_settings()
    await build_kb(conn, s)
    await conn.execute("INSERT OR IGNORE INTO users (user_id) VALUES (57)")
    await conn.commit()

    async def _ok(*_a, **_k):
        return LLMResult(
            ok=True,
            text="Шаги Happ Android из гайда. [kb.happ.android]",
        )

    monkeypatch.setattr("bot.assistant.orchestrator.chat_complete", _ok)
    res = await handle_user_message(
        conn, s, user_id=57, text="Как Happ на Android?", username=None
    )
    assert res.llm_down is False
    assert "Happ" in res.html or "happ" in res.html.lower()
    assert "kb.happ.android" in res.kb_ids or "kb.happ.android" in res.html


def test_hub_hides_assistant_when_off(monkeypatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "1:t")
    monkeypatch.setenv("USD_RUB_RATE", "90")
    monkeypatch.setenv("ASSISTANT_ENABLED", "false")
    monkeypatch.setenv("ADMIN_IDS", "1")
    s = load_settings()
    labels = [b.text for row in hub_menu_kb(s, user_id=1).inline_keyboard for b in row]
    assert "🤖 AI Помощник" not in labels
    assert assistant_menu_visible(1, s) is False


def test_hub_shows_assistant_for_admin(monkeypatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "1:t")
    monkeypatch.setenv("USD_RUB_RATE", "90")
    monkeypatch.setenv("ASSISTANT_ENABLED", "true")
    monkeypatch.setenv("ASSISTANT_ADMIN_ONLY", "true")
    monkeypatch.setenv("ADMIN_IDS", "42")
    s = load_settings()
    labels = [b.text for row in hub_menu_kb(s, user_id=42).inline_keyboard for b in row]
    assert "🤖 AI Помощник" in labels
    assert assistant_menu_visible(99, s) is False
