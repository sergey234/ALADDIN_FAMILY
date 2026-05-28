"""Идемпотентность VPN expiry push в shop.db."""

from __future__ import annotations

import aiosqlite


async def ensure_vpn_expiry_notices_table(conn: aiosqlite.Connection) -> None:
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS vpn_expiry_notices (
            telegram_user_id INTEGER NOT NULL,
            kind TEXT NOT NULL,
            sent_at TEXT NOT NULL DEFAULT (datetime('now')),
            PRIMARY KEY (telegram_user_id, kind)
        )
        """
    )
    await conn.commit()


async def notice_already_sent(conn: aiosqlite.Connection, *, telegram_user_id: int, kind: str) -> bool:
    cur = await conn.execute(
        "SELECT 1 FROM vpn_expiry_notices WHERE telegram_user_id = ? AND kind = ? LIMIT 1",
        (int(telegram_user_id), str(kind).strip()),
    )
    return (await cur.fetchone()) is not None


async def mark_notice_sent(conn: aiosqlite.Connection, *, telegram_user_id: int, kind: str) -> None:
    await conn.execute(
        """
        INSERT OR IGNORE INTO vpn_expiry_notices (telegram_user_id, kind, sent_at)
        VALUES (?, ?, datetime('now'))
        """,
        (int(telegram_user_id), str(kind).strip()),
    )
    await conn.commit()
