from __future__ import annotations

import aiosqlite


async def upsert_user(
    conn: aiosqlite.Connection,
    *,
    user_id: int,
    username: str | None,
    first_name: str | None,
) -> None:
    await conn.execute(
        """
        INSERT INTO users (user_id, username, first_name)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            username=excluded.username,
            first_name=excluded.first_name
        """,
        (user_id, username, first_name),
    )
    await conn.commit()


async def set_referrer_if_empty(
    conn: aiosqlite.Connection,
    *,
    user_id: int,
    referrer_id: int,
) -> bool:
    if user_id == referrer_id:
        return False
    cur = await conn.execute("SELECT referrer_id FROM users WHERE user_id = ?", (user_id,))
    row = await cur.fetchone()
    if row is None:
        await upsert_user(conn, user_id=user_id, username=None, first_name=None)
    cur = await conn.execute("SELECT referrer_id FROM users WHERE user_id = ?", (user_id,))
    row = await cur.fetchone()
    if row and row["referrer_id"] is not None:
        return False
    await conn.execute(
        "UPDATE users SET referrer_id = ? WHERE user_id = ? AND referrer_id IS NULL",
        (referrer_id, user_id),
    )
    await conn.commit()
    return True


async def get_user(conn: aiosqlite.Connection, user_id: int) -> aiosqlite.Row | None:
    cur = await conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    return await cur.fetchone()


async def user_stats(conn: aiosqlite.Connection, user_id: int) -> dict[str, float | int]:
    from bot.services import balance_repo
    cur = await conn.execute(
        """
        SELECT
            COALESCE(SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END), 0) AS completed_cnt,
            COALESCE(SUM(CASE WHEN status = 'completed' THEN rub_after_discounts ELSE 0 END), 0) AS spent_rub
        FROM orders WHERE user_id = ?
        """,
        (user_id,),
    )
    row = await cur.fetchone()
    u = await get_user(conn, user_id)
    ref_balance = float(u["ref_balance_rub"]) if u else 0.0
    bal = await balance_repo.get_balance(conn, user_id)
    return {
        "completed_orders": int(row["completed_cnt"] if row else 0),
        "spent_rub": float(row["spent_rub"] if row else 0),
        "ref_balance_rub": ref_balance,
        "balance_rub": bal,
    }
