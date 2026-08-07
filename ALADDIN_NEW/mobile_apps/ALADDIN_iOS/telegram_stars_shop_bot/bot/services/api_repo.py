from __future__ import annotations

import aiosqlite


async def create_api_key_request(
    conn: aiosqlite.Connection,
    *,
    user_id: int,
    contact: str,
    comment: str,
) -> int:
    cur = await conn.execute(
        """
        INSERT INTO api_key_requests (user_id, contact, comment, status)
        VALUES (?, ?, ?, 'new')
        """,
        (user_id, contact, comment),
    )
    await conn.commit()
    return int(cur.lastrowid)
