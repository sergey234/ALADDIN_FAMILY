"""Идемпотентность пуша «устройство подключилось» (shop.db)."""

from __future__ import annotations

import aiosqlite


async def ensure_device_first_notices_table(conn: aiosqlite.Connection) -> None:
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS vpn_device_first_notices (
            slot_id INTEGER NOT NULL PRIMARY KEY,
            telegram_user_id INTEGER NOT NULL,
            sent_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    await conn.commit()


async def notice_already_sent(conn: aiosqlite.Connection, *, slot_id: int) -> bool:
    cur = await conn.execute(
        "SELECT 1 FROM vpn_device_first_notices WHERE slot_id = ? LIMIT 1",
        (int(slot_id),),
    )
    return (await cur.fetchone()) is not None


async def mark_notice_sent(
    conn: aiosqlite.Connection, *, slot_id: int, telegram_user_id: int
) -> None:
    await conn.execute(
        """
        INSERT OR IGNORE INTO vpn_device_first_notices (slot_id, telegram_user_id, sent_at)
        VALUES (?, ?, datetime('now'))
        """,
        (int(slot_id), int(telegram_user_id)),
    )
    await conn.commit()
