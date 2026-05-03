"""Одноразовые emoji-капчи (онбординг и чек-аут)."""

from __future__ import annotations

import time

import aiosqlite

_PURGE_SQL = "DELETE FROM captcha_challenges WHERE expires_at < ?"


async def create_challenge(
    conn: aiosqlite.Connection,
    *,
    user_id: int,
    purpose: str,
    correct_idx: int,
    options_json: str,
    ttl_seconds: int = 600,
) -> int:
    now = int(time.time())
    await conn.execute(_PURGE_SQL, (now,))
    exp = now + int(max(60, ttl_seconds))
    cur = await conn.execute(
        """
        INSERT INTO captcha_challenges (user_id, purpose, correct_idx, options_json, expires_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (user_id, purpose[:32], int(correct_idx), options_json, exp),
    )
    await conn.commit()
    return int(cur.lastrowid)


async def take_challenge_if_correct(
    conn: aiosqlite.Connection,
    *,
    challenge_id: int,
    user_id: int,
    purpose: str,
    picked_idx: int,
) -> bool:
    now = int(time.time())
    await conn.execute(_PURGE_SQL, (now,))
    cur = await conn.execute(
        """
        SELECT user_id, purpose, correct_idx FROM captcha_challenges
        WHERE id = ? AND expires_at >= ?
        """,
        (challenge_id, now),
    )
    row = await cur.fetchone()
    if row is None:
        return False
    if int(row["user_id"]) != int(user_id) or str(row["purpose"]) != purpose:
        return False
    ok = int(row["correct_idx"]) == int(picked_idx)
    if ok:
        await conn.execute("DELETE FROM captcha_challenges WHERE id = ?", (challenge_id,))
        await conn.commit()
    return ok
