"""Ops-уведомления о NPS/отзывах пользователей → ALERT_TELEGRAM_CHAT_ID."""

from __future__ import annotations

from bot.config import Settings
from bot.services.alerts import send_alert


async def notify_ops_user_feedback(
    settings: Settings,
    *,
    user_id: int,
    username: str | None,
    kind: str,
    score: int,
    comment: str,
    order_id: int | None = None,
) -> None:
    if not settings.alerts_enabled:
        return
    uname = f"@{username}" if username else f"id={user_id}"
    oid = f" заказ <code>{order_id}</code>" if order_id else ""
    body = (
        f"Пользователь: {uname} (id <code>{user_id}</code>){oid}\n"
        f"Тип: <b>{kind}</b> · оценка: <b>{score}</b>\n"
        f"Текст:\n{(comment or '—')[:1500]}"
    )
    dedupe = f"feedback:{user_id}:{kind}:{order_id or 0}:{hash(comment) & 0xFFFF}"
    await send_alert(
        settings,
        severity="info",
        title="💬 Отзыв пользователя",
        body=body,
        dedupe_key=dedupe,
    )
