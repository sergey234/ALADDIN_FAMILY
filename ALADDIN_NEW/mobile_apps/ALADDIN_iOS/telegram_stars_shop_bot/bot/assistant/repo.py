"""Persistence for assistant sessions / turns / tickets / kb."""

from __future__ import annotations

import json
from typing import Any

import aiosqlite

from bot.assistant.redact import redact_for_log


async def get_or_create_session(
    conn: aiosqlite.Connection,
    user_id: int,
    *,
    ttl_min: int = 30,
    max_turns: int = 20,
) -> int:
    """Active session or new. Ends stale / over-limit."""
    cur = await conn.execute(
        """
        SELECT id, turn_count, last_active_at FROM assistant_sessions
        WHERE user_id = ? AND ended_at IS NULL
        ORDER BY id DESC LIMIT 1
        """,
        (int(user_id),),
    )
    row = await cur.fetchone()
    if row is not None:
        sid = int(row["id"])
        turns = int(row["turn_count"] or 0)
        # Idle / max turns → close and reopen.
        expired = False
        cur2 = await conn.execute(
            """
            SELECT CASE WHEN datetime(last_active_at, ?) < datetime('now') THEN 1 ELSE 0 END AS expired
            FROM assistant_sessions WHERE id = ?
            """,
            (f"+{int(ttl_min)} minutes", sid),
        )
        er = await cur2.fetchone()
        if er and int(er["expired"] or 0) == 1:
            expired = True
        if expired or turns >= int(max_turns):
            await end_session(conn, sid)
        else:
            await conn.execute(
                "UPDATE assistant_sessions SET last_active_at = datetime('now') WHERE id = ?",
                (sid,),
            )
            await conn.commit()
            return sid

    cur = await conn.execute(
        """
        INSERT INTO assistant_sessions (user_id, started_at, last_active_at, turn_count)
        VALUES (?, datetime('now'), datetime('now'), 0)
        """,
        (int(user_id),),
    )
    await conn.commit()
    return int(cur.lastrowid)


async def end_session(conn: aiosqlite.Connection, session_id: int) -> None:
    await conn.execute(
        "UPDATE assistant_sessions SET ended_at = datetime('now') WHERE id = ? AND ended_at IS NULL",
        (int(session_id),),
    )
    await conn.commit()


async def end_user_sessions(conn: aiosqlite.Connection, user_id: int) -> None:
    await conn.execute(
        """
        UPDATE assistant_sessions SET ended_at = datetime('now')
        WHERE user_id = ? AND ended_at IS NULL
        """,
        (int(user_id),),
    )
    await conn.commit()


async def bump_turn(conn: aiosqlite.Connection, session_id: int) -> int:
    await conn.execute(
        """
        UPDATE assistant_sessions
        SET turn_count = turn_count + 1, last_active_at = datetime('now')
        WHERE id = ?
        """,
        (int(session_id),),
    )
    await conn.commit()
    cur = await conn.execute(
        "SELECT turn_count FROM assistant_sessions WHERE id = ?",
        (int(session_id),),
    )
    row = await cur.fetchone()
    return int(row["turn_count"] if row else 0)


async def add_turn(
    conn: aiosqlite.Connection,
    *,
    session_id: int,
    user_id: int,
    role: str,
    content: str,
    topic_guess: str | None = None,
    tool_names: list[str] | None = None,
    kb_chunk_ids: list[str] | None = None,
) -> None:
    await conn.execute(
        """
        INSERT INTO assistant_turns
          (session_id, user_id, role, content, topic_guess, tool_names, kb_chunk_ids, redacted)
        VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        """,
        (
            int(session_id),
            int(user_id),
            (role or "")[:16],
            redact_for_log(content),
            (topic_guess or None),
            json.dumps(tool_names or [], ensure_ascii=False) if tool_names else None,
            json.dumps(kb_chunk_ids or [], ensure_ascii=False) if kb_chunk_ids else None,
        ),
    )
    await conn.commit()


async def recent_turns(
    conn: aiosqlite.Connection,
    session_id: int,
    *,
    limit: int = 8,
) -> list[dict[str, Any]]:
    cur = await conn.execute(
        """
        SELECT role, content FROM assistant_turns
        WHERE session_id = ?
        ORDER BY id DESC LIMIT ?
        """,
        (int(session_id), int(limit)),
    )
    rows = await cur.fetchall()
    out = [{"role": str(r["role"]), "content": str(r["content"] or "")} for r in rows]
    out.reverse()
    return out


async def count_user_msgs_today(conn: aiosqlite.Connection, user_id: int) -> int:
    cur = await conn.execute(
        """
        SELECT COUNT(*) AS c FROM assistant_turns
        WHERE user_id = ? AND role = 'user'
          AND date(created_at) = date('now')
        """,
        (int(user_id),),
    )
    row = await cur.fetchone()
    return int(row["c"] if row else 0)


async def count_tickets_today(conn: aiosqlite.Connection, user_id: int) -> int:
    cur = await conn.execute(
        """
        SELECT COUNT(*) AS c FROM assistant_tickets
        WHERE user_id = ? AND date(created_at) = date('now')
        """,
        (int(user_id),),
    )
    row = await cur.fetchone()
    return int(row["c"] if row else 0)


async def create_ticket(
    conn: aiosqlite.Connection,
    *,
    user_id: int,
    session_id: int | None,
    reason_code: str,
    summary: str,
    urgency: str = "normal",
    meta: dict[str, Any] | None = None,
) -> int:
    cur = await conn.execute(
        """
        INSERT INTO assistant_tickets
          (user_id, session_id, reason_code, summary, urgency, status, meta_json)
        VALUES (?, ?, ?, ?, ?, 'open', ?)
        """,
        (
            int(user_id),
            int(session_id) if session_id else None,
            (reason_code or "esc.user")[:64],
            redact_for_log(summary, max_len=1500),
            (urgency or "normal")[:32],
            json.dumps(meta or {}, ensure_ascii=False) if meta else None,
        ),
    )
    await conn.commit()
    return int(cur.lastrowid)


async def upsert_kb_chunk(
    conn: aiosqlite.Connection,
    *,
    chunk_id: str,
    topic: str,
    text_plain: str,
    source_hash: str,
) -> None:
    await conn.execute(
        """
        INSERT INTO assistant_kb_chunks (id, topic, text_plain, source_hash, updated_at)
        VALUES (?, ?, ?, ?, datetime('now'))
        ON CONFLICT(id) DO UPDATE SET
          topic = excluded.topic,
          text_plain = excluded.text_plain,
          source_hash = excluded.source_hash,
          updated_at = datetime('now')
        """,
        (chunk_id, topic, text_plain, source_hash),
    )


async def commit_kb(conn: aiosqlite.Connection) -> None:
    await conn.commit()


async def get_kb_chunks(
    conn: aiosqlite.Connection,
    chunk_ids: list[str] | None = None,
    topic: str | None = None,
) -> list[dict[str, str]]:
    if chunk_ids:
        placeholders = ",".join("?" for _ in chunk_ids)
        cur = await conn.execute(
            f"SELECT id, topic, text_plain FROM assistant_kb_chunks WHERE id IN ({placeholders})",
            tuple(chunk_ids),
        )
    elif topic:
        cur = await conn.execute(
            "SELECT id, topic, text_plain FROM assistant_kb_chunks WHERE topic = ?",
            (topic,),
        )
    else:
        cur = await conn.execute("SELECT id, topic, text_plain FROM assistant_kb_chunks")
    rows = await cur.fetchall()
    return [
        {"id": str(r["id"]), "topic": str(r["topic"]), "text_plain": str(r["text_plain"] or "")}
        for r in rows
    ]


async def get_kb_hash_map(conn: aiosqlite.Connection) -> dict[str, str]:
    cur = await conn.execute("SELECT id, source_hash FROM assistant_kb_chunks")
    rows = await cur.fetchall()
    return {str(r["id"]): str(r["source_hash"] or "") for r in rows}
