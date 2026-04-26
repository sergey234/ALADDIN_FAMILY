from __future__ import annotations

import asyncio
import logging

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import Settings
from bot.support_links import support_order_question_url
from bot.util_html import esc

_log = logging.getLogger(__name__)


async def send_buyer_html(settings: Settings, user_id: int, html: str) -> None:
    """Одно сообщение покупателю (HTML). Ошибки сети — только в лог."""
    bot = Bot(settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    try:
        await bot.send_message(int(user_id), html)
    finally:
        await bot.session.close()


def schedule_buyer_html(settings: Settings, user_id: int, html: str) -> None:
    """Fire-and-forget из воркера / вебхуков (не блокирует HTTP и SQLite)."""

    async def _run() -> None:
        try:
            await send_buyer_html(settings, user_id, html)
        except Exception:
            _log.warning("buyer_notify_failed user_id=%s", user_id, exc_info=True)

    asyncio.create_task(_run())


def buyer_message_admin_status_change(*, order_id: int, new_status: str) -> str | None:
    """Текст покупателю после смены статуса из админки (план 37-7)."""
    oid = esc(order_id)
    if new_status == "paid":
        return (
            f"<b>Оплата получена</b>\n"
            f"Заказ <b>#{oid}</b> отмечен оплаченным.\n"
            f"Отправка Stars / Premium обычно занимает несколько минут."
        )
    if new_status == "processing":
        return (
            f"<b>Заказ в работе</b>\n"
            f"<b>#{oid}</b>: готовим отправку получателю."
        )
    if new_status == "completed":
        return f"<b>Готово</b>\nЗаказ <b>#{oid}</b> выдан. Спасибо за покупку!"
    if new_status == "refunded":
        return (
            f"<b>Сторно / возврат по заказу</b>\n"
            f"<b>#{oid}</b>: статус в магазине обновлён. Если вопрос остался — напишите в поддержку с номером заказа."
        )
    if new_status == "payment_disputed":
        return (
            f"<b>Разбор по оплате</b>\n"
            f"<b>#{oid}</b>: заказ отмечен как спорный; поддержка свяжется при необходимости. Сохраните номер заказа."
        )
    return None


def buyer_message_auto_submitted(*, order_id: int) -> str:
    oid = esc(order_id)
    return (
        f"<b>Отправляем</b>\n"
        f"Заказ <b>#{oid}</b> оплачен; запрос на отправку Stars / Premium передан.\n"
        f"Обычно это занимает несколько минут."
    )


def buyer_message_auto_create_failed(*, order_id: int, settings: Settings) -> str:
    oid = esc(order_id)
    lines = [
        "<b>Авто-отправка не удалась</b>",
        f"Заказ <b>#{oid}</b>: провайдер не принял отправку сразу.",
        "Оператор подключится вручную; деньги не пропали.",
    ]
    url = support_order_question_url(settings, order_id)
    if url:
        lines.append("")
        lines.append(f'<a href="{esc(url)}">Написать в поддержку</a>')
    else:
        lines.append("")
        lines.append("Напишите в поддержку с номером заказа.")
    return "\n".join(lines)


def buyer_message_istar_completed(*, order_id: int) -> str:
    oid = esc(order_id)
    return f"<b>Готово</b>\nЗаказ <b>#{oid}</b> выдан. Спасибо за покупку!"


def buyer_message_istar_failed(*, order_id: int, settings: Settings, reason: str | None = None) -> str:
    oid = esc(order_id)
    tail = ""
    if reason:
        tail = f"\n<i>{esc(reason[:400])}</i>"
    lines = [
        "<b>Не удалось отправить автоматически</b>",
        f"Заказ <b>#{oid}</b>: провайдер сообщил об ошибке.{tail}",
        "Напишите в поддержку — разберём вручную.",
    ]
    url = support_order_question_url(settings, order_id)
    if url:
        lines.append("")
        lines.append(f'<a href="{esc(url)}">Написать в поддержку</a>')
    return "\n".join(lines)
