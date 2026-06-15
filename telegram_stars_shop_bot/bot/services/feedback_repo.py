from __future__ import annotations

import aiosqlite


async def save_feedback(
    conn: aiosqlite.Connection,
    *,
    user_id: int,
    kind: str,
    score: int,
    product_scope: str = "all",
    comment: str = "",
) -> int:
    k = (kind or "").strip().lower()
    if k not in ("nps", "csat"):
        raise ValueError("feedback_kind_invalid")
    s = int(score)
    if k == "nps" and not (0 <= s <= 10):
        raise ValueError("feedback_score_invalid")
    if k == "csat" and not (1 <= s <= 5):
        raise ValueError("feedback_score_invalid")
    cur = await conn.execute(
        """
        INSERT INTO user_feedback (user_id, product_scope, kind, score, comment)
        VALUES (?, ?, ?, ?, ?)
        """,
        (int(user_id), (product_scope or "all")[:32], k, s, (comment or "")[:800]),
    )
    await conn.commit()
    return int(cur.lastrowid)


async def has_recent_feedback(conn: aiosqlite.Connection, *, user_id: int, cooldown_days: int) -> bool:
    d = max(1, int(cooldown_days))
    cur = await conn.execute(
        """
        SELECT 1
        FROM user_feedback
        WHERE user_id = ?
          AND date(created_at) >= date('now', ?)
        LIMIT 1
        """,
        (int(user_id), f"-{d} days"),
    )
    return (await cur.fetchone()) is not None


async def has_recent_prompt(conn: aiosqlite.Connection, *, user_id: int, cooldown_days: int) -> bool:
    d = max(1, int(cooldown_days))
    cur = await conn.execute(
        """
        SELECT 1
        FROM analytics_events
        WHERE user_id = ?
          AND event_type = 'feedback_prompt_sent'
          AND date(created_at) >= date('now', ?)
        LIMIT 1
        """,
        (int(user_id), f"-{d} days"),
    )
    return (await cur.fetchone()) is not None


async def list_survey_candidates(
    conn: aiosqlite.Connection,
    *,
    lookback_days: int,
    cooldown_days: int,
    limit: int,
) -> list[int]:
    lookback = max(1, int(lookback_days))
    cool = max(1, int(cooldown_days))
    lim = max(1, min(500, int(limit)))
    cur = await conn.execute(
        """
        SELECT DISTINCT o.user_id
        FROM orders o
        WHERE o.status = 'completed'
          AND date(COALESCE(o.completed_at, o.updated_at)) >= date('now', ?)
          AND NOT EXISTS (
              SELECT 1 FROM user_feedback uf
              WHERE uf.user_id = o.user_id
                AND date(uf.created_at) >= date('now', ?)
          )
          AND NOT EXISTS (
              SELECT 1 FROM analytics_events ae
              WHERE ae.user_id = o.user_id
                AND ae.event_type = 'feedback_prompt_sent'
                AND date(ae.created_at) >= date('now', ?)
          )
        ORDER BY o.user_id DESC
        LIMIT ?
        """,
        (f"-{lookback} days", f"-{cool} days", f"-{cool} days", lim),
    )
    rows = await cur.fetchall()
    return [int(r[0]) for r in rows]
