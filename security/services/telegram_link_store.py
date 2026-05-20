# -*- coding: utf-8 -*-
"""SQLite store for Telegram ↔ ALADDIN account linking (tg-auth)."""
from __future__ import annotations

import os
import secrets
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

_DEFAULT_DB = "/opt/aladdin-backend/data/telegram_links.db"
_CODE_TTL_SEC = 600


@dataclass(frozen=True)
class TelegramLink:
    telegram_user_id: int
    aladdin_user_id: str
    telegram_username: Optional[str]
    ai_opt_in: bool
    linked_at: float


def _db_path() -> str:
    return os.getenv("TELEGRAM_LINK_DB", _DEFAULT_DB)


def ensure_db() -> None:
    path = Path(_db_path())
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS pending_codes (
                code TEXT PRIMARY KEY,
                aladdin_user_id TEXT NOT NULL,
                ai_opt_in INTEGER NOT NULL DEFAULT 0,
                expires_at REAL NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS links (
                telegram_user_id INTEGER PRIMARY KEY,
                aladdin_user_id TEXT NOT NULL,
                telegram_username TEXT,
                ai_opt_in INTEGER NOT NULL DEFAULT 0,
                linked_at REAL NOT NULL
            )
            """
        )
        conn.commit()


def create_link_code(*, aladdin_user_id: str, ai_opt_in: bool) -> str:
    ensure_db()
    code = secrets.token_hex(3).upper()[:6]
    expires = time.time() + _CODE_TTL_SEC
    with sqlite3.connect(_db_path()) as conn:
        conn.execute("DELETE FROM pending_codes WHERE expires_at < ?", (time.time(),))
        conn.execute(
            "INSERT OR REPLACE INTO pending_codes (code, aladdin_user_id, ai_opt_in, expires_at) VALUES (?, ?, ?, ?)",
            (code, aladdin_user_id, 1 if ai_opt_in else 0, expires),
        )
        conn.commit()
    return code


def confirm_link(*, code: str, telegram_user_id: int, telegram_username: Optional[str]) -> Optional[TelegramLink]:
    ensure_db()
    now = time.time()
    with sqlite3.connect(_db_path()) as conn:
        row = conn.execute(
            "SELECT aladdin_user_id, ai_opt_in, expires_at FROM pending_codes WHERE code = ?",
            (code.upper().strip(),),
        ).fetchone()
        if not row:
            return None
        aladdin_user_id, ai_opt_in, expires_at = row
        if expires_at < now:
            conn.execute("DELETE FROM pending_codes WHERE code = ?", (code.upper().strip(),))
            conn.commit()
            return None
        conn.execute(
            """
            INSERT OR REPLACE INTO links (telegram_user_id, aladdin_user_id, telegram_username, ai_opt_in, linked_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (telegram_user_id, aladdin_user_id, telegram_username, ai_opt_in, now),
        )
        conn.execute("DELETE FROM pending_codes WHERE code = ?", (code.upper().strip(),))
        conn.commit()
    return TelegramLink(
        telegram_user_id=telegram_user_id,
        aladdin_user_id=aladdin_user_id,
        telegram_username=telegram_username,
        ai_opt_in=bool(ai_opt_in),
        linked_at=now,
    )


def get_link(telegram_user_id: int) -> Optional[TelegramLink]:
    ensure_db()
    with sqlite3.connect(_db_path()) as conn:
        row = conn.execute(
            "SELECT aladdin_user_id, telegram_username, ai_opt_in, linked_at FROM links WHERE telegram_user_id = ?",
            (telegram_user_id,),
        ).fetchone()
    if not row:
        return None
    return TelegramLink(
        telegram_user_id=telegram_user_id,
        aladdin_user_id=row[0],
        telegram_username=row[1],
        ai_opt_in=bool(row[2]),
        linked_at=row[3],
    )


def unlink(telegram_user_id: int) -> bool:
    ensure_db()
    with sqlite3.connect(_db_path()) as conn:
        cur = conn.execute("DELETE FROM links WHERE telegram_user_id = ?", (telegram_user_id,))
        conn.commit()
        return cur.rowcount > 0
