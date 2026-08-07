from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from bot.config import load_settings
from bot.handlers.hub import profile_body_html
from bot.services import users_repo


@pytest.mark.asyncio
async def test_profile_body_no_ref_content(conn, monkeypatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:pf-test")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("REF_BONUS_VPN_ONLY", "false")
    settings = load_settings()
    await users_repo.upsert_user(conn, user_id=55001, username="p", first_name="P")
    await conn.execute(
        "UPDATE users SET balance_rub = 12.5, ref_balance_rub = 3.25 WHERE user_id = 55001"
    )
    await conn.commit()

    bot = MagicMock()
    bot.get_me = AsyncMock()
    html = await profile_body_html(bot, settings, conn, 55001)

    assert "Пригласить" not in html
    assert "nav:reffaq" not in html
    assert "Статистика приглашений" not in html
    assert "ref_" not in html
    assert "💳" in html and "Основной баланс" in html
    assert "🎁" in html and "Реферальный баланс" in html
    assert "Бонусный" not in html
    assert "он же" not in html
    assert "Уровень" not in html
    assert "Stars/Premium" not in html
    assert "можно тратить" in html.lower() or "VPN, Stars и Premium" in html
    assert "только для оплаты VPN" not in html
    assert "🛡️" in html
    assert "ID:" in html and "55001" in html