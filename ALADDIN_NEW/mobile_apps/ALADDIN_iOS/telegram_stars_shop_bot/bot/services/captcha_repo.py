"""Одноразовые emoji-капчи (онбординг и чек-аут)."""

from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass
from typing import Literal

import aiosqlite

_PURGE_SQL = "DELETE FROM captcha_challenges WHERE expires_at < ?"
_LOCK: asyncio.Lock | None = None

TakeStatus = Literal["ok", "wrong", "missing", "forbidden"]


def _lock() -> asyncio.Lock:
    global _LOCK
    if _LOCK is None:
        _LOCK = asyncio.Lock()
    return _LOCK


@dataclass(frozen=True)
class CaptchaTake:
    status: TakeStatus
    hint_word: str | None = None


def normalize_emoji(value: str) -> str:
    """Сравнение эмодзи без variation-selector (⭐ vs ⭐️)."""
    return (value or "").replace("\ufe0f", "").replace("\ufe0e", "").strip()


def emoji_token(emoji: str) -> str:
    return (emoji or "").encode("utf-8").hex()


def emoji_from_token(token: str) -> str | None:
    try:
        raw = bytes.fromhex((token or "").strip())
        text = raw.decode("utf-8")
    except Exception:
        return None
    return text or None


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
    purp = purpose[:32]
    async with _lock():
        await conn.execute(_PURGE_SQL, (now,))
        # Старые кнопки той же проверки больше не принимаем (иначе «яблоко» с прошлого экрана).
        await conn.execute(
            "DELETE FROM captcha_challenges WHERE user_id = ? AND purpose = ?",
            (int(user_id), purp),
        )
        exp = now + int(max(60, ttl_seconds))
        cur = await conn.execute(
            """
            INSERT INTO captcha_challenges (user_id, purpose, correct_idx, options_json, expires_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (int(user_id), purp, int(correct_idx), options_json, exp),
        )
        await conn.commit()
        return int(cur.lastrowid)


async def take_challenge(
    conn: aiosqlite.Connection,
    *,
    challenge_id: int,
    user_id: int,
    purpose: str,
    picked_idx: int | None = None,
    picked_emoji: str | None = None,
    word_by_emoji: dict[str, str] | None = None,
) -> CaptchaTake:
    """
    Проверка ответа.
    Предпочтительно по эмодзи (устойчиво к RTL/перестановке кнопок),
    индекс — запасной путь для старых сообщений.
    """
    now = int(time.time())
    words = word_by_emoji or {}
    async with _lock():
        await conn.execute(_PURGE_SQL, (now,))
        cur = await conn.execute(
            """
            SELECT user_id, purpose, correct_idx, options_json FROM captcha_challenges
            WHERE id = ? AND expires_at >= ?
            """,
            (int(challenge_id), now),
        )
        row = await cur.fetchone()
        if row is None:
            return CaptchaTake("missing")
        if int(row["user_id"]) != int(user_id):
            return CaptchaTake("forbidden")
        if str(row["purpose"]) != purpose:
            return CaptchaTake("forbidden")

        try:
            options = json.loads(row["options_json"] or "[]")
        except Exception:
            options = []
        if not isinstance(options, list) or not options:
            return CaptchaTake("missing")

        correct_idx = int(row["correct_idx"])
        if correct_idx < 0 or correct_idx >= len(options):
            return CaptchaTake("missing")
        target = str(options[correct_idx])
        target_n = normalize_emoji(target)
        hint = words.get(target) or words.get(target_n)

        ok = False
        if picked_emoji is not None:
            ok = normalize_emoji(picked_emoji) == target_n
        elif picked_idx is not None:
            pi = int(picked_idx)
            if 0 <= pi < len(options):
                ok = normalize_emoji(str(options[pi])) == target_n

        if not ok:
            return CaptchaTake("wrong", hint_word=hint)

        await conn.execute("DELETE FROM captcha_challenges WHERE id = ?", (int(challenge_id),))
        await conn.commit()
        return CaptchaTake("ok", hint_word=hint)


async def take_challenge_if_correct(
    conn: aiosqlite.Connection,
    *,
    challenge_id: int,
    user_id: int,
    purpose: str,
    picked_idx: int,
) -> bool:
    """Совместимость со старыми тестами: True только при ok."""
    res = await take_challenge(
        conn,
        challenge_id=challenge_id,
        user_id=user_id,
        purpose=purpose,
        picked_idx=picked_idx,
    )
    return res.status == "ok"
