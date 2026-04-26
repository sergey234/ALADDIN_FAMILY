from __future__ import annotations

import logging

import httpx

from bot.config import Settings
from bot.db.database import connect
from bot.keyboards.shop_kb import admin_order_reply_markup_for_api, admin_topup_reply_markup_for_api
from bot.services import orders_repo
from bot.services.admin_order_ff import ff_context_from_order_row, format_fulfillment_admin_block

logger = logging.getLogger(__name__)


async def notify_admins_new_api_order(settings: Settings, order_id: int) -> None:
    """Те же админы и те же callback-кнопки, что при заказе из бота."""
    if not settings.bot_token or not settings.parsed_admin_ids():
        return
    url = f"https://api.telegram.org/bot{settings.bot_token}/sendMessage"
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
    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            for aid in settings.parsed_admin_ids():
                payload_base = {
                    "text": text,
                    "parse_mode": "HTML",
                    "reply_markup": admin_order_reply_markup_for_api(
                        order_id, settings=settings, actor_id=aid, order_ff=ff_ctx
                    ),
                }
                try:
                    r = await client.post(url, json={"chat_id": aid, **payload_base})
                    r.raise_for_status()
                except Exception as e:
                    logger.warning("admin notify failed for %s: %s", aid, e)
    except Exception as e:
        logger.warning("notify_admins_new_api_order: %s", e)


async def notify_admins_new_topup(settings: Settings, topup_id: int, user_id: int, amount_rub: float) -> None:
    if not settings.bot_token or not settings.parsed_admin_ids():
        return
    url = f"https://api.telegram.org/bot{settings.bot_token}/sendMessage"
    text = (
        f"<b>Пополнение (Partner API)</b>\n\n"
        f"ID: <code>{topup_id}</code>\n"
        f"Пользователь: <code>{user_id}</code>\n"
        f"Сумма: <b>{amount_rub:.2f} ₽</b>"
    )
    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            for aid in settings.parsed_admin_ids():
                payload_base: dict = {"text": text, "parse_mode": "HTML"}
                rm = admin_topup_reply_markup_for_api(topup_id, settings=settings, actor_id=aid)
                if rm is not None:
                    payload_base["reply_markup"] = rm
                try:
                    r = await client.post(url, json={"chat_id": aid, **payload_base})
                    r.raise_for_status()
                except Exception as e:
                    logger.warning("admin topup notify failed for %s: %s", aid, e)
    except Exception as e:
        logger.warning("notify_admins_new_topup: %s", e)
