from __future__ import annotations

import asyncio
import logging

from aiogram import Bot

from bot.config import Settings
from bot.db.database import connect
from bot.keyboards.shop_kb import feedback_nps_kb
from bot.services import analytics_repo, feedback_repo

logger = logging.getLogger(__name__)


async def send_feedback_prompt_once(bot: Bot, settings: Settings) -> int:
    conn = await connect(settings.database_path)
    sent = 0
    try:
        user_ids = await feedback_repo.list_survey_candidates(
            conn,
            lookback_days=int(settings.feedback_survey_lookback_days),
            cooldown_days=int(settings.feedback_survey_cooldown_days),
            limit=int(settings.feedback_survey_batch_size),
        )
        for uid in user_ids:
            try:
                await bot.send_message(
                    uid,
                    "Оцените, пожалуйста, наш сервис по шкале NPS (0-10), где 10 — точно порекомендуете:",
                    reply_markup=feedback_nps_kb(),
                )
                await analytics_repo.log_event(
                    conn,
                    user_id=uid,
                    event_type="feedback_prompt_sent",
                    meta={"product_hint": "shop", "via": "survey_loop"},
                )
                sent += 1
            except Exception as exc:
                logger.exception("feedback_prompt_send_failed user_id=%s", uid)
                try:
                    await analytics_repo.log_event(
                        conn,
                        user_id=uid,
                        event_type="feedback_prompt_failed",
                        meta={
                            "product_hint": "shop",
                            "via": "survey_loop",
                            "error": type(exc).__name__,
                        },
                    )
                except Exception:
                    logger.exception("feedback_prompt_failed_event_log_error user_id=%s", uid)
    finally:
        await conn.close()
    return sent


async def feedback_survey_loop(bot: Bot, settings: Settings) -> None:
    interval = max(300, int(settings.feedback_survey_interval_seconds))
    while True:
        try:
            await send_feedback_prompt_once(bot, settings)
        except Exception:
            logger.exception("feedback_survey_loop_iteration_failed")
        await asyncio.sleep(interval)
