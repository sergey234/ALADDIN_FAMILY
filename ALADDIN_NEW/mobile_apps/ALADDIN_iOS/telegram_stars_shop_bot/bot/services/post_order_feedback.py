"""NPS 0–10 сразу после выдачи заказа (completed)."""

from __future__ import annotations

import logging

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import Settings
from bot.keyboards.shop_kb import feedback_nps_kb

_log = logging.getLogger(__name__)

NPS_PROMPT_TEXT = (
    "Оцените, пожалуйста, наш сервис по шкале NPS (0-10), "
    "где <b>10</b> — точно порекомендуете:"
)

WISHES_PROMPT_TEXT = (
    "<b>Спасибо за высокую оценку!</b>\n"
    "Мы стремимся стать лучше — поделитесь <b>пожеланиями и рекомендациями</b> "
    "или нажмите «Пропустить»."
)

NEGATIVE_PROMPT_TEXT = (
    "<b>Спасибо за честную оценку.</b>\n"
    "Расскажите, пожалуйста, <b>что не понравилось</b> — это поможет нам улучшить сервис."
)


async def send_post_order_nps_prompt_only(settings: Settings, *, user_id: int, order_id: int) -> None:
    if not settings.feature_feedback_collection_enabled:
        return
    bot = Bot(settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    try:
        await bot.send_message(
            int(user_id),
            NPS_PROMPT_TEXT,
            reply_markup=feedback_nps_kb(order_id),
        )
    except Exception:
        _log.warning("post_order_nps_prompt_failed user_id=%s order_id=%s", user_id, order_id, exc_info=True)
    finally:
        await bot.session.close()


def schedule_post_order_nps_prompt(settings: Settings, *, user_id: int, order_id: int) -> None:
    import asyncio

    async def _run() -> None:
        await send_post_order_nps_prompt_only(settings, user_id=user_id, order_id=order_id)

    asyncio.create_task(_run())


def feedback_order_scope(order_id: int) -> str:
    return f"order:{int(order_id)}"


def parse_order_scope(product_scope: str) -> int | None:
    raw = (product_scope or "").strip()
    if not raw.startswith("order:"):
        return None
    try:
        return int(raw.split(":", 1)[1])
    except (TypeError, ValueError, IndexError):
        return None
