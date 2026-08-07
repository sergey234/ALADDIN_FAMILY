"""Объединённый онбординг: канал + согласие одним экраном."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from bot.services import onboarding_gate, users_repo


@pytest.mark.asyncio
async def test_accept_terms_skips_vpn_legal(conn) -> None:
    uid = 880001
    await users_repo.upsert_user(conn, user_id=uid, username="u", first_name="U")
    assert not await users_repo.has_vpn_legal_accepted(conn, uid)
    await users_repo.accept_terms(conn, uid)
    assert await users_repo.has_terms_accepted(conn, uid)
    assert await users_repo.has_vpn_legal_accepted(conn, uid)


@pytest.mark.asyncio
async def test_pipeline_shows_combined_when_no_terms(conn, monkeypatch: pytest.MonkeyPatch) -> None:
    uid = 880002
    await users_repo.upsert_user(conn, user_id=uid, username="u2", first_name="U")
    sent: list[tuple] = []

    async def fake_send(bot, chat_id, settings):
        sent.append(("combined", chat_id))

    monkeypatch.setattr(onboarding_gate, "send_combined_onboarding_screen", fake_send)
    monkeypatch.setattr(
        "bot.services.onboarding_gate.channel_gate_enabled",
        lambda _s: False,
    )
    bot = MagicMock()
    settings = MagicMock()
    await onboarding_gate.resume_onboarding_pipeline(bot, 1, uid, settings, conn)
    assert sent == [("combined", 1)]


@pytest.mark.asyncio
async def test_channel_check_accepts_terms_when_member(conn, monkeypatch: pytest.MonkeyPatch) -> None:
    from bot.handlers import common as common_handlers

    uid = 880003
    await users_repo.upsert_user(conn, user_id=uid, username="u3", first_name="U")
    assert not await users_repo.has_terms_accepted(conn, uid)

    cb = MagicMock()
    cb.from_user.id = uid
    cb.from_user.username = "u3"
    cb.from_user.first_name = "U"
    cb.message.chat.id = 10
    cb.message.delete = AsyncMock()
    cb.answer = AsyncMock()
    cb.bot = MagicMock()

    monkeypatch.setattr(
        "bot.handlers.common.channel_gate_enabled",
        lambda _s: True,
    )
    monkeypatch.setattr(
        "bot.handlers.common.user_is_channel_member",
        AsyncMock(return_value=True),
    )
    resumed: list[int] = []

    async def fake_resume(bot, chat_id, user_id, settings, conn):
        resumed.append(user_id)

    monkeypatch.setattr(onboarding_gate, "resume_onboarding_pipeline", fake_resume)
    monkeypatch.setattr("bot.handlers.common.onboarding_gate.resume_onboarding_pipeline", fake_resume)

    settings = MagicMock()
    await common_handlers.onboarding_channel_check(cb, settings, conn)
    assert await users_repo.has_terms_accepted(conn, uid)
    assert resumed == [uid]
    cb.message.delete.assert_awaited()


@pytest.mark.asyncio
async def test_channel_check_fail_does_not_accept_terms(conn, monkeypatch: pytest.MonkeyPatch) -> None:
    from bot.handlers import common as common_handlers

    uid = 880004
    await users_repo.upsert_user(conn, user_id=uid, username="u4", first_name="U")

    cb = MagicMock()
    cb.from_user.id = uid
    cb.message.chat.id = 11
    cb.message.delete = AsyncMock()
    cb.answer = AsyncMock()
    cb.bot = MagicMock()

    monkeypatch.setattr(
        "bot.handlers.common.channel_gate_enabled",
        lambda _s: True,
    )
    monkeypatch.setattr(
        "bot.handlers.common.user_is_channel_member",
        AsyncMock(return_value=False),
    )

    settings = MagicMock()
    await common_handlers.onboarding_channel_check(cb, settings, conn)
    assert not await users_repo.has_terms_accepted(conn, uid)
    cb.answer.assert_awaited()
    assert cb.answer.await_args.kwargs.get("show_alert") is True
    cb.message.delete.assert_not_awaited()
