from __future__ import annotations

import aiosqlite


async def create_sell_request(
    conn: aiosqlite.Connection,
    *,
    user_id: int,
    stars: int,
    rub_offer: float,
) -> int:
    cur = await conn.execute(
        """
        INSERT INTO sell_requests (user_id, stars, rub_offer, status)
        VALUES (?, ?, ?, 'new')
        """,
        (user_id, stars, rub_offer),
    )
    await conn.commit()
    return int(cur.lastrowid)


async def list_user_sells(conn: aiosqlite.Connection, user_id: int, limit: int = 10) -> list[aiosqlite.Row]:
    cur = await conn.execute(
        "SELECT * FROM sell_requests WHERE user_id = ? ORDER BY id DESC LIMIT ?",
        (user_id, limit),
    )
    return await cur.fetchall()


async def count_user_sells(conn: aiosqlite.Connection, user_id: int) -> int:
    cur = await conn.execute(
        "SELECT COUNT(*) AS c FROM sell_requests WHERE user_id = ?",
        (user_id,),
    )
    row = await cur.fetchone()
    return int(row["c"] if row else 0)


async def list_user_sells_page(
    conn: aiosqlite.Connection,
    user_id: int,
    *,
    limit: int,
    offset: int,
) -> list[aiosqlite.Row]:
    cur = await conn.execute(
        """
        SELECT * FROM sell_requests WHERE user_id = ?
        ORDER BY id DESC LIMIT ? OFFSET ?
        """,
        (user_id, limit, offset),
    )
    return await cur.fetchall()


async def get_sell(conn: aiosqlite.Connection, sell_id: int) -> aiosqlite.Row | None:
    cur = await conn.execute("SELECT * FROM sell_requests WHERE id = ?", (sell_id,))
    return await cur.fetchone()


async def update_sell_status(conn: aiosqlite.Connection, sell_id: int, status: str) -> None:
    await conn.execute("UPDATE sell_requests SET status = ? WHERE id = ?", (status, sell_id))
    await conn.commit()


async def list_recent_sells(conn: aiosqlite.Connection, limit: int = 12) -> list[aiosqlite.Row]:
    cur = await conn.execute("SELECT * FROM sell_requests ORDER BY id DESC LIMIT ?", (limit,))
    return await cur.fetchall()
