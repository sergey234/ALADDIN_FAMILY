from __future__ import annotations

import logging

from bot.config import Settings
from bot.db.database import connect
from bot.keyboards.shop_kb import admin_order_reply_markup_for_api, admin_topup_reply_markup_for_api
from bot.services import orders_repo
from bot.services.admin_order_ff import ff_context_from_order_row, format_fulfillment_admin_block
from bot.services.ops_chat import send_ops_chat_html

logger = logging.getLogger(__name__)


async def notify_admins_new_api_order(settings: Settings, order_id: int) -> None:
    """Новый заказ Partner API → единый ops-чат."""
    ff_ctx = None
    extra = ""
    conn = await connect(settings.database_path)
    try:
        row = await orders_repo.get_order(conn, order_id)
        if row is not None:
            ff_ctx = ff_context_from_order_row(row)
            extra = format_fulfillment_admin_block(row)
    finally:
        await conn.close()
    text = f"<b>Новый заказ (Partner API)</b>\n\nID: <code>{order_id}</code>{extra}"
    actor = settings.default_ops_actor_id()
    markup = None
    if actor is not None:
        markup_dict = admin_order_reply_markup_for_api(
            order_id, settings=settings, actor_id=actor, order_ff=ff_ctx
        )
        if markup_dict:
            from aiogram.types import InlineKeyboardMarkup

            markup = InlineKeyboardMarkup.model_validate(markup_dict)
    try:
        await send_ops_chat_html(settings, text, reply_markup=markup)
    except Exception as e:
        logger.warning("notify_admins_new_api_order: %s", e)


async def notify_admins_new_topup(settings: Settings, topup_id: int, user_id: int, amount_rub: float) -> None:
    text = (
        f"<b>Пополнение (Partner API)</b>\n\n"
        f"ID: <code>{topup_id}</code>\n"
        f"Пользователь: <code>{user_id}</code>\n"
        f"Сумма: <b>{amount_rub:.2f} ₽</b>"
    )
    actor = settings.default_ops_actor_id()
    markup = None
    if actor is not None:
        rm = admin_topup_reply_markup_for_api(topup_id, settings=settings, actor_id=actor)
        if rm is not None:
            from aiogram.types import InlineKeyboardMarkup

            markup = InlineKeyboardMarkup.model_validate(rm)
    try:
        await send_ops_chat_html(settings, text, reply_markup=markup)
    except Exception as e:
        logger.warning("notify_admins_new_topup: %s", e)
