from __future__ import annotations

from typing import Any

import aiosqlite


async def list_contests(conn: aiosqlite.Connection, *, limit: int = 20) -> list[aiosqlite.Row]:
    cur = await conn.execute(
        "SELECT * FROM partner_contests ORDER BY id DESC LIMIT ?",
        (limit,),
    )
    return await cur.fetchall()


async def get_contest(conn: aiosqlite.Connection, contest_id: int) -> aiosqlite.Row | None:
    cur = await conn.execute("SELECT * FROM partner_contests WHERE id = ?", (contest_id,))
    return await cur.fetchone()


async def get_active_contest(conn: aiosqlite.Connection) -> aiosqlite.Row | None:
    cur = await conn.execute(
        """
        SELECT * FROM partner_contests
        WHERE is_active = 1
          AND datetime('now') >= datetime(starts_at)
          AND datetime('now') <= datetime(ends_at)
        ORDER BY id DESC
        LIMIT 1
        """
    )
    return await cur.fetchone()


async def create_contest(
    conn: aiosqlite.Connection,
    *,
    title: str,
    prize_text: str,
    starts_at: str,
    ends_at: str,
    activate: bool,
) -> int:
    if activate:
        await conn.execute("UPDATE partner_contests SET is_active = 0")
    cur = await conn.execute(
        """
        INSERT INTO partner_contests (title, prize_text, starts_at, ends_at, is_active)
        VALUES (?, ?, ?, ?, ?)
        """,
        (title, prize_text, starts_at, ends_at, 1 if activate else 0),
    )
    await conn.commit()
    return int(cur.lastrowid)


async def set_contest_active(conn: aiosqlite.Connection, contest_id: int, *, active: bool) -> bool:
    row = await get_contest(conn, contest_id)
    if row is None:
        return False
    if active:
        await conn.execute("UPDATE partner_contests SET is_active = 0")
    await conn.execute(
        "UPDATE partner_contests SET is_active = ? WHERE id = ?",
        (1 if active else 0, contest_id),
    )
    await conn.commit()
    return True


async def deactivate_all(conn: aiosqlite.Connection) -> None:
    await conn.execute("UPDATE partner_contests SET is_active = 0")
    await conn.commit()


async def leaderboard_for_contest(
    conn: aiosqlite.Connection,
    *,
    starts_at: str,
    ends_at: str,
    limit: int = 15,
) -> list[dict[str, Any]]:
    """
    Топ рефереров: число выданных (completed) заказов с referrer_id в периоде по updated_at заказа.
    """
    cur = await conn.execute(
        """
        SELECT referrer_id AS rid, COUNT(*) AS cnt,
               SUM(rub_after_discounts) AS volume_rub
        FROM orders
        WHERE status = 'completed'
          AND referrer_id IS NOT NULL
          AND datetime(updated_at) >= datetime(?)
          AND datetime(updated_at) <= datetime(?)
        GROUP BY referrer_id
        ORDER BY cnt DESC, volume_rub DESC
        LIMIT ?
        """,
        (starts_at, ends_at, limit),
    )
    rows = await cur.fetchall()
    return [
        {"referrer_id": int(r["rid"]), "orders": int(r["cnt"]), "volume_rub": float(r["volume_rub"] or 0)}
        for r in rows
    ]


async def user_contest_stats(
    conn: aiosqlite.Connection,
    *,
    user_id: int,
    starts_at: str,
    ends_at: str,
) -> dict[str, Any] | None:
    cur = await conn.execute(
        """
        SELECT COUNT(*) AS cnt, SUM(rub_after_discounts) AS volume_rub
        FROM orders
        WHERE status = 'completed'
          AND referrer_id = ?
          AND datetime(updated_at) >= datetime(?)
          AND datetime(updated_at) <= datetime(?)
        """,
        (user_id, starts_at, ends_at),
    )
    row = await cur.fetchone()
    if row is None:
        return None
    return {"orders": int(row["cnt"] or 0), "volume_rub": float(row["volume_rub"] or 0)}


async def rank_for_referrer(
    conn: aiosqlite.Connection,
    *,
    referrer_id: int,
    starts_at: str,
    ends_at: str,
) -> int | None:
    """Позиция в таблице (1 — лучший) по числу успешных заказов рефералов."""
    board = await leaderboard_for_contest(conn, starts_at=starts_at, ends_at=ends_at, limit=500)
    for i, row in enumerate(board, start=1):
        if row["referrer_id"] == referrer_id:
            return i
    return None
