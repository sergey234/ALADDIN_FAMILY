"""Уведомление пользователя после автозачисления topup."""

from __future__ import annotations

import asyncio
import logging

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import Settings
from bot.db.database import connect
from bot.keyboards.shop_kb import hub_menu_kb
from bot.services import balance_repo
from bot.util_html import esc

_log = logging.getLogger(__name__)


def schedule_topup_paid_user_notify(
    settings: Settings,
    *,
    user_id: int,
    topup_id: int,
    amount_rub: float,
) -> None:
    asyncio.create_task(
        _notify_topup_paid(settings, user_id=user_id, topup_id=topup_id, amount_rub=amount_rub)
    )


async def _notify_topup_paid(
    settings: Settings,
    *,
    user_id: int,
    topup_id: int,
    amount_rub: float,
) -> None:
    bot = Bot(settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    try:
        conn = await connect(settings.database_path)
        try:
            bal = await balance_repo.get_balance(conn, user_id)
        finally:
            await conn.close()
        text = (
            "<b>✅ Баланс успешно пополнен!</b>\n\n"
            f"Зачислено: <b>{esc(f'{amount_rub:.2f}')} ₽</b>\n"
            f"Текущий баланс: <b>{esc(f'{bal:.2f}')} ₽</b>\n\n"
            f"<i>Заявка #{esc(topup_id)}</i>"
        )
        await bot.send_message(user_id, text, reply_markup=hub_menu_kb(settings, user_id=user_id))
    except Exception:
        _log.exception("topup_paid_notify_failed user_id=%s topup_id=%s", user_id, topup_id)
    finally:
        await bot.session.close()
