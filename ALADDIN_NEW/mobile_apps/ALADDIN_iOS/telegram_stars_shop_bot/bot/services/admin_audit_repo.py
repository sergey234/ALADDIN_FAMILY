from __future__ import annotations

import aiosqlite


async def append_admin_action(
    conn: aiosqlite.Connection,
    *,
    admin_user_id: int,
    action: str,
    payload_json: str | None = None,
) -> None:
    await conn.execute(
        """
        INSERT INTO admin_audit_log (admin_user_id, action, payload_json)
        VALUES (?, ?, ?)
        """,
        (admin_user_id, action, payload_json),
    )
    await conn.commit()


async def list_recent_break_glass_actions(
    conn: aiosqlite.Connection,
    *,
    lookback_hours: int,
    limit: int = 200,
) -> list[aiosqlite.Row]:
    h = max(1, int(lookback_hours))
    lim = max(1, int(limit))
    mod = f"-{h} hours"
    cur = await conn.execute(
        """
        SELECT id, created_at, admin_user_id, payload_json
        FROM admin_audit_log
        WHERE action = 'adm:paid_break_glass'
          AND datetime(created_at) >= datetime('now', ?)
        ORDER BY id DESC
        LIMIT ?
        """,
        (mod, lim),
    )
    return await cur.fetchall()
