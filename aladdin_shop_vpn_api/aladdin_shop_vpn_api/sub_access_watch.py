"""Учёт обращений к GET /sub/ и детект «горячих» токенов (шаринг, P3)."""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone

import aiosqlite


def _hash_token(opaque_token: str) -> str:
    return hashlib.sha256((opaque_token or "").strip().encode("utf-8")).hexdigest()[:16]


async def ensure_sub_access_log_table(conn: aiosqlite.Connection) -> None:
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS sub_access_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            opaque_token_hash TEXT NOT NULL,
            accessed_at TEXT NOT NULL
        )
        """
    )
    await conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_sub_access_hash_time
        ON sub_access_log(opaque_token_hash, accessed_at)
        """
    )


async def record_sub_access(conn: aiosqlite.Connection, *, opaque_token: str) -> None:
    await ensure_sub_access_log_table(conn)
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    h = _hash_token(opaque_token)
    await conn.execute(
        "INSERT INTO sub_access_log (opaque_token_hash, accessed_at) VALUES (?, ?)",
        (h, now),
    )
    await conn.commit()
    await _prune_old(conn)


async def _prune_old(conn: aiosqlite.Connection, *, keep_days: int = 7) -> None:
    cutoff = (datetime.now(timezone.utc) - timedelta(days=keep_days)).replace(microsecond=0).isoformat()
    await conn.execute("DELETE FROM sub_access_log WHERE accessed_at < ?", (cutoff,))


async def hot_token_hashes(
    conn: aiosqlite.Connection,
    *,
    per_hour_threshold: int,
    window_hours: int = 1,
) -> list[tuple[str, int]]:
    """Список (hash, count) за последний window_hours, где count > threshold."""
    if per_hour_threshold <= 0:
        return []
    await ensure_sub_access_log_table(conn)
    since = (
        datetime.now(timezone.utc) - timedelta(hours=window_hours)
    ).replace(microsecond=0).isoformat()
    cur = await conn.execute(
        """
        SELECT opaque_token_hash, COUNT(*) AS cnt
        FROM sub_access_log
        WHERE accessed_at >= ?
        GROUP BY opaque_token_hash
        HAVING cnt > ?
        ORDER BY cnt DESC
        LIMIT 20
        """,
        (since, int(per_hour_threshold)),
    )
    rows = await cur.fetchall()
    return [(str(r[0]), int(r[1])) for r in rows]
