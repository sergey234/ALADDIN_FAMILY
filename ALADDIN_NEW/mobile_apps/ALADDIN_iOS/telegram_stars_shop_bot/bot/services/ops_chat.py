"""Ops-алерты: одинаковое сообщение всем ADMIN_IDS (+ опциональный ALERT-чат)."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

import httpx
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import Settings

if TYPE_CHECKING:
    from aiogram.types import InlineKeyboardMarkup

_log = logging.getLogger(__name__)


def ops_recipient_chat_ids(settings: Settings) -> list[str]:
    """
    Получатели ops-алертов и карточек заказов:
    все ADMIN_IDS (личка с ботом) + ALERT_TELEGRAM_CHAT_ID, если задан и ещё не в списке.
    У всех админов одна и та же информация.
    """
    out: list[str] = []
    seen: set[str] = set()
    for aid in sorted(settings.parsed_admin_ids()):
        s = str(int(aid))
        if s not in seen:
            seen.add(s)
            out.append(s)
    chat = (settings.alert_telegram_chat_id or "").strip()
    if chat and chat not in seen:
        seen.add(chat)
        out.append(chat)
    return out


def ops_chat_configured(settings: Settings) -> bool:
    return bool((settings.alert_telegram_bot_token or "").strip()) and bool(
        ops_recipient_chat_ids(settings)
    )


async def send_ops_chat_html(
    settings: Settings,
    html: str,
    *,
    dedupe_key: str | None = None,
    reply_markup: InlineKeyboardMarkup | None = None,
    cooldown_seconds: int | None = None,
) -> bool:
    """Одинаковое HTML-сообщение всем получателям. Дедуп один раз на весь fan-out."""
    if not ops_chat_configured(settings):
        return False
    if dedupe_key:
        from bot.services.alerts import _dedupe_allowed

        key = f"ops_chat:{dedupe_key.strip()}"
        if cooldown_seconds is None:
            cooldown = max(0, int(settings.alert_cooldown_seconds))
        else:
            cooldown = max(0, int(cooldown_seconds))
        if not await _dedupe_allowed(key, cooldown):
            return False

    token = (settings.alert_telegram_bot_token or "").strip()
    recipients = ops_recipient_chat_ids(settings)
    bot = Bot(token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    body = html[:4000]
    any_ok = False
    try:
        for chat_id in recipients:
            try:
                await bot.send_message(
                    chat_id,
                    body,
                    reply_markup=reply_markup,
                    disable_web_page_preview=True,
                )
                any_ok = True
            except Exception:
                _log.exception("ops_chat_send_failed chat_id=%s", chat_id)
        return any_ok
    finally:
        await bot.session.close()


def schedule_ops_chat_html(
    settings: Settings,
    html: str,
    *,
    dedupe_key: str | None = None,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    async def _run() -> None:
        try:
            await send_ops_chat_html(
                settings, html, dedupe_key=dedupe_key, reply_markup=reply_markup
            )
        except Exception:
            _log.exception("schedule_ops_chat_failed")

    asyncio.create_task(_run())


async def send_ops_chat_plain(settings: Settings, text: str) -> bool:
    """Plain text — тем же получателям, что и HTML."""
    token = (settings.alert_telegram_bot_token or "").strip()
    recipients = ops_recipient_chat_ids(settings)
    if not token or not recipients:
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    body = text[:3500]
    any_ok = False
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            for chat_id in recipients:
                try:
                    r = await client.post(
                        url,
                        json={
                            "chat_id": chat_id,
                            "text": body,
                            "disable_web_page_preview": True,
                        },
                    )
                    if r.status_code >= 300:
                        _log.warning(
                            "ops_chat_plain_failed status=%s chat_id=%s",
                            r.status_code,
                            chat_id,
                        )
                    else:
                        any_ok = True
                except Exception:
                    _log.exception("ops_chat_plain_exception chat_id=%s", chat_id)
        return any_ok
    except Exception:
        _log.exception("ops_chat_plain_client_failed")
        return False
