"""Горячие opaque_token по логу GET /sub/ (таблица в vpn.db, пишет vpn-api)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import aiosqlite


async def hot_token_hashes(
    conn: aiosqlite.Connection,
    *,
    per_hour_threshold: int,
    window_hours: int = 1,
) -> list[tuple[str, int]]:
    if per_hour_threshold <= 0:
        return []
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
