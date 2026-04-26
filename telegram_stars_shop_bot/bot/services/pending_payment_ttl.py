from __future__ import annotations

import asyncio
import logging

from aiogram import Bot

from bot.config import Settings
from bot.db.database import connect
from bot.services import orders_repo
from bot.services.partner_outbound import emit_order_status_changed
from bot.support_links import support_order_question_url
from bot.util_html import esc

_log = logging.getLogger(__name__)


async def run_pending_payment_ttl_sweep(bot: Bot, settings: Settings) -> None:
    ttl = int(settings.order_pending_payment_expire_minutes)
    if ttl <= 0:
        return
    conn = await connect(settings.database_path)
    try:
        pairs = await orders_repo.expire_stale_pending_payment_orders(conn, ttl_minutes=ttl)
    finally:
        await conn.close()
    if not pairs:
        return
    _log.info("pending_payment_ttl_expired count=%s", len(pairs))
    for order_id, user_id in pairs:
        lines = [
            f"Заказ <b>#{esc(order_id)}</b>: время на оплату истекло.",
            "",
            "Если вы уже оплатили — напишите в поддержку с номером заказа.",
            "Новый заказ можно оформить в меню /menu.",
        ]
        url = support_order_question_url(settings, order_id)
        if url:
            lines.append("")
            lines.append(f'<a href="{esc(url)}">Написать в поддержку</a>')
        text = "\n".join(lines)
        try:
            await bot.send_message(user_id, text)
        except Exception:
            _log.warning("pending_payment_ttl_notify_failed order_id=%s user_id=%s", order_id, user_id)
        asyncio.create_task(
            emit_order_status_changed(
                db_path=settings.database_path,
                order_id=order_id,
                previous_status="pending_payment",
                new_status="expired",
            )
        )


async def pending_payment_ttl_loop(bot: Bot, settings: Settings) -> None:
    """Фоновая проверка просроченных pending_payment (пока работает polling)."""
    interval = max(30, int(settings.order_pending_payment_sweep_interval_seconds))
    while True:
        try:
            await run_pending_payment_ttl_sweep(bot, settings)
        except asyncio.CancelledError:
            raise
        except Exception:
            _log.exception("pending_payment_ttl_loop_iteration")
        try:
            await asyncio.sleep(interval)
        except asyncio.CancelledError:
            raise
