"""Анти-спам повторного запроса счёта LAVA/Crypto через SQLite (транзакционно)."""

from __future__ import annotations

import aiosqlite

from bot.services import orders_repo


async def allow_checkout_invoice_attempt(
    conn: aiosqlite.Connection,
    order_id: int,
    cooldown_seconds: int,
) -> tuple[bool, float]:
    """
    True — можно вызывать createInvoice / LAVA invoice снова.
    False — слишком рано; второе значение — примерно сколько секунд подождать.
    """
    return await orders_repo.assert_invoice_request_allowed(
        conn,
        order_id=order_id,
        cooldown_seconds=int(cooldown_seconds),
    )
