"""Мягкий старт: set_my_commands не валит polling (br-a*)."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from bot.main import _admin_bot_commands, _retry_bot_commands_later, _setup_bot_commands, _user_bot_commands


def _settings(*, vpn: bool, admins: set[int] | None = None) -> SimpleNamespace:
    return SimpleNamespace(
        ui_show_vpn=vpn,
        parsed_admin_ids=lambda: set(admins or ()),
    )


@pytest.mark.asyncio
async def test_setup_bot_commands_user_and_admin_scopes() -> None:
    bot = AsyncMock()
    bot.set_my_commands = AsyncMock(return_value=True)
    settings = _settings(vpn=True, admins={10, 20})
    assert await _setup_bot_commands(bot, settings) is True
    # default + 2 admin scopes
    assert bot.set_my_commands.await_count == 3
    user_cmds = {c.command for c in _user_bot_commands(settings)}
    admin_cmds = {c.command for c in _admin_bot_commands(settings)}
    assert "admin" not in user_cmds
    assert "admin" in admin_cmds
    assert "admin_help" in admin_cmds


@pytest.mark.asyncio
async def test_setup_bot_commands_timeout_is_nonfatal() -> None:
    bot = AsyncMock()
    bot.set_my_commands = AsyncMock(side_effect=TimeoutError("telegram timeout"))
    settings = _settings(vpn=False)
    assert await _setup_bot_commands(bot, settings) is False
    bot.set_my_commands.assert_awaited_once()


@pytest.mark.asyncio
async def test_retry_bot_commands_later_succeeds(monkeypatch: pytest.MonkeyPatch) -> None:
    bot = AsyncMock()
    settings = _settings(vpn=False)
    calls: list[bool] = []

    async def fake_setup(_bot, _settings) -> bool:
        calls.append(True)
        return True

    async def instant_sleep(_delay: float) -> None:
        return None

    monkeypatch.setattr("bot.main._setup_bot_commands", fake_setup)
    monkeypatch.setattr("bot.main.asyncio.sleep", instant_sleep)
    await _retry_bot_commands_later(bot, settings, delay_seconds=1.0)
    assert calls == [True]
