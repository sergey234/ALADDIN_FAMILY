"""Уведомления о смене статуса заказа → единый ops-чат."""

from __future__ import annotations

import asyncio
import logging

from bot.config import Settings
from bot.db.database import connect
from bot.services import orders_repo, users_repo
from bot.services.ops_chat import send_ops_chat_html
from bot.util_html import esc

_log = logging.getLogger(__name__)


def schedule_notify_admins_order_paid(settings: Settings, order_id: int) -> None:
    """После автоматического перехода в paid."""

    async def _run() -> None:
        try:
            conn = await connect(settings.database_path)
            try:
                order = await orders_repo.get_order(conn, order_id)
                if order is None:
                    return
                u = await users_repo.get_user(conn, int(order["user_id"]))
                uname = u["username"] if u else None
                user_line = f"@{uname}" if uname else f"id {order['user_id']}"
                recipient = str(order["user_note"] or "").strip() or "—"
                rub = f"{float(order['rub_after_discounts']):.2f}"
                text = (
                    f"<b>✅ Заказ #{esc(order_id)} оплачен</b>\n\n"
                    f"Пользователь: {esc(user_line)}\n"
                    f"Товар: {esc(order['product_title'])}\n"
                    f"Получатель: <code>{esc(recipient)}</code>\n"
                    f"Сумма: <b>{esc(rub)} ₽</b>\n\n"
                    f"<i>Автовыдача запущена.</i>"
                )
            finally:
                await conn.close()
            await send_ops_chat_html(settings, text)
        except Exception:
            _log.exception("admin_notify_paid_failed order_id=%s", order_id)

    asyncio.create_task(_run())


def schedule_notify_admins_order_completed(
    settings: Settings,
    order_id: int,
    *,
    source: str = "auto",
) -> None:
    """После выдачи Stars/Premium (webhook, poller или ручное «Выдан»)."""

    async def _run() -> None:
        try:
            conn = await connect(settings.database_path)
            try:
                order = await orders_repo.get_order(conn, order_id)
                if order is None:
                    return
                u = await users_repo.get_user(conn, int(order["user_id"]))
                uname = u["username"] if u else None
                user_line = f"@{uname}" if uname else f"id {order['user_id']}"
                recipient = str(order["user_note"] or "").strip() or "—"
                ref = str(order["fulfillment_provider_ref"] or "").strip() or "—"
                applied = str(order["fulfillment_applied_at"] or order["updated_at"] or "").strip() or "—"
                src = {
                    "auto": "автовыдача (iStar)",
                    "istar_poll": "опрос статуса iStar",
                    "admin": "оператор",
                }.get(source, source)
                rub = f"{float(order['rub_after_discounts']):.2f}"
                text = (
                    f"<b>🎁 Заказ #{esc(order_id)} выдан</b>\n\n"
                    f"Пользователь: {esc(user_line)}\n"
                    f"Товар: {esc(order['product_title'])}\n"
                    f"Получатель: <code>{esc(recipient)}</code>\n"
                    f"Сумма: <b>{esc(rub)} ₽</b>\n"
                    f"Источник: <i>{esc(src)}</i>\n"
                    f"Время: <code>{esc(applied)}</code>\n"
                    f"iStar ref: <code>{esc(ref)}</code>"
                )
            finally:
                await conn.close()
            await send_ops_chat_html(settings, text)
        except Exception:
            _log.exception("admin_notify_completed_failed order_id=%s", order_id)

    asyncio.create_task(_run())


def schedule_notify_admins_auto_fulfill_manual_needed(
    settings: Settings,
    *,
    order_id: int,
    error_summary: str,
) -> None:
    """Временный сбой iStar — заказ в очереди (ops-чат, без дубля send_alert)."""

    async def _run() -> None:
        try:
            err = esc((error_summary or "unknown")[:400])
            text = (
                f"<b>⚠️ Заказ #{esc(order_id)}: автовыдача не удалась</b>\n\n"
                f"Ошибка: <code>{err}</code>\n\n"
                f"<i>Заказ остаётся в очереди — бот повторит сам.</i>\n"
                f"<i>Если iStar долго лежит — выдайте вручную и нажмите «Выдан».</i>"
            )
            await send_ops_chat_html(
                settings,
                text,
                dedupe_key=f"auto_fulfill_manual_needed:{order_id}",
            )
        except Exception:
            _log.exception("admin_notify_autoff_fail order_id=%s", order_id)

    asyncio.create_task(_run())
