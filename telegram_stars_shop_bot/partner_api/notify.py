from __future__ import annotations

import logging

import httpx

from bot.config import Settings

logger = logging.getLogger(__name__)


def _admin_order_markup(order_id: int) -> dict:
    return {
        "inline_keyboard": [
            [
                {"text": "✅ Оплачен", "callback_data": f"adm:paid:{order_id}"},
                {"text": "⚙️ В работе", "callback_data": f"adm:proc:{order_id}"},
            ],
            [{"text": "🎁 Выдан", "callback_data": f"adm:done:{order_id}"}],
        ]
    }


def _admin_topup_markup(topup_id: int) -> dict:
    return {
        "inline_keyboard": [
            [{"text": "✅ Зачислить баланс", "callback_data": f"top:ok:{topup_id}"}],
        ]
    }


async def notify_admins_new_api_order(settings: Settings, order_id: int) -> None:
    """Те же админы и те же callback-кнопки, что при заказе из бота."""
    if not settings.bot_token or not settings.parsed_admin_ids():
        return
    url = f"https://api.telegram.org/bot{settings.bot_token}/sendMessage"
    text = f"<b>Новый заказ (Partner API)</b>\n\nID: <code>{order_id}</code>"
    payload_base = {
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": _admin_order_markup(order_id),
    }
    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            for aid in settings.parsed_admin_ids():
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
    payload_base = {
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": _admin_topup_markup(topup_id),
    }
    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            for aid in settings.parsed_admin_ids():
                try:
                    r = await client.post(url, json={"chat_id": aid, **payload_base})
                    r.raise_for_status()
                except Exception as e:
                    logger.warning("admin topup notify failed for %s: %s", aid, e)
    except Exception as e:
        logger.warning("notify_admins_new_topup: %s", e)
