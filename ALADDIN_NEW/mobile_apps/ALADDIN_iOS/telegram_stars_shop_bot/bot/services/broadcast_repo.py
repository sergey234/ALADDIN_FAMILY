"""Репозиторий ручных маркетинговых рассылок (не VPN-сервис)."""

from __future__ import annotations

import aiosqlite


async def ensure_broadcast_schema(conn: aiosqlite.Connection) -> None:
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS broadcasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_user_id INTEGER NOT NULL,
            mode TEXT NOT NULL,
            body_html TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            sent_count INTEGER NOT NULL DEFAULT 0,
            fail_count INTEGER NOT NULL DEFAULT 0,
            skip_count INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            finished_at TEXT
        )
        """
    )
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS broadcast_deliveries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            broadcast_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            error TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE(broadcast_id, user_id)
        )
        """
    )
    await conn.commit()


async def is_marketing_opt_in(conn: aiosqlite.Connection, user_id: int) -> bool:
    cur = await conn.execute(
        "SELECT COALESCE(marketing_opt_in, 1) AS o FROM users WHERE user_id = ?",
        (int(user_id),),
    )
    row = await cur.fetchone()
    if row is None:
        return True
    return int(row["o"] or 0) == 1


async def set_marketing_opt_in(conn: aiosqlite.Connection, user_id: int, enabled: bool) -> None:
    await conn.execute(
        "UPDATE users SET marketing_opt_in = ? WHERE user_id = ?",
        (1 if enabled else 0, int(user_id)),
    )
    await conn.commit()


async def count_unsubscribed(conn: aiosqlite.Connection) -> int:
    cur = await conn.execute(
        "SELECT COUNT(*) AS n FROM users WHERE COALESCE(marketing_opt_in, 1) = 0"
    )
    row = await cur.fetchone()
    return int(row["n"] if row else 0)


async def create_broadcast(
    conn: aiosqlite.Connection,
    *,
    admin_user_id: int,
    mode: str,
    body_html: str,
) -> int:
    cur = await conn.execute(
        """
        INSERT INTO broadcasts (admin_user_id, mode, body_html, status)
        VALUES (?, ?, ?, 'running')
        """,
        (int(admin_user_id), mode, body_html),
    )
    await conn.commit()
    return int(cur.lastrowid)


async def finish_broadcast(
    conn: aiosqlite.Connection,
    broadcast_id: int,
    *,
    sent: int,
    fail: int,
    skip: int,
) -> None:
    await conn.execute(
        """
        UPDATE broadcasts
        SET status = 'done', sent_count = ?, fail_count = ?, skip_count = ?,
            finished_at = datetime('now')
        WHERE id = ?
        """,
        (int(sent), int(fail), int(skip), int(broadcast_id)),
    )
    await conn.commit()


async def log_delivery(
    conn: aiosqlite.Connection,
    *,
    broadcast_id: int,
    user_id: int,
    status: str,
    error: str | None = None,
) -> None:
    await conn.execute(
        """
        INSERT OR REPLACE INTO broadcast_deliveries
            (broadcast_id, user_id, status, error)
        VALUES (?, ?, ?, ?)
        """,
        (int(broadcast_id), int(user_id), status, error),
    )
    await conn.commit()


async def get_broadcast(conn: aiosqlite.Connection, broadcast_id: int):
    cur = await conn.execute("SELECT * FROM broadcasts WHERE id = ?", (int(broadcast_id),))
    return await cur.fetchone()


async def list_recipient_ids(
    conn: aiosqlite.Connection,
    *,
    mode: str,
    admin_ids: set[int],
    actor_id: int,
) -> list[int]:
    """Режимы: dry | admins | cohort:N | all. Только marketing_opt_in=1 (кроме dry/admins)."""
    m = (mode or "").strip().lower()
    if m == "dry":
        return [int(actor_id)]
    if m == "admins":
        return sorted(int(x) for x in admin_ids)
    limit: int | None = None
    if m.startswith("cohort:"):
        try:
            limit = max(1, min(500, int(m.split(":", 1)[1])))
        except ValueError:
            limit = 100
    elif m != "all":
        return [int(actor_id)]
    sql = """
        SELECT user_id FROM users
        WHERE COALESCE(marketing_opt_in, 1) = 1
        ORDER BY created_at ASC, user_id ASC
    """
    if limit is not None:
        sql += f" LIMIT {int(limit)}"
    cur = await conn.execute(sql)
    rows = await cur.fetchall()
    return [int(r["user_id"]) for r in rows]
