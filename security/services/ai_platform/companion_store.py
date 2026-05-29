# -*- coding: utf-8 -*-
"""
Persistent companion state (SQLite MVP; swap for Postgres/Redis in prod).
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
import threading
from contextlib import contextmanager
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

_DEFAULT_DB = Path(__file__).resolve().parents[2] / "data" / "companion_platform.db"


class CompanionStore:
    def __init__(self, db_path: Optional[Path] = None) -> None:
        self._path = Path(db_path or os.getenv("COMPANION_DB_PATH", str(_DEFAULT_DB)))
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._init_schema()

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(str(self._path), timeout=30)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_schema(self) -> None:
        with self._lock, self._conn() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS companion_trust (
                    user_id TEXT NOT NULL,
                    character_id TEXT NOT NULL,
                    score INTEGER NOT NULL DEFAULT 10,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (user_id, character_id)
                );
                CREATE TABLE IF NOT EXISTS companion_consent (
                    user_id TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS companion_memory_flag (
                    user_id TEXT PRIMARY KEY,
                    enabled INTEGER NOT NULL DEFAULT 0,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS usage_daily (
                    user_id TEXT NOT NULL,
                    day TEXT NOT NULL,
                    messages INTEGER NOT NULL DEFAULT 0,
                    voice_seconds INTEGER NOT NULL DEFAULT 0,
                    PRIMARY KEY (user_id, day)
                );
                CREATE TABLE IF NOT EXISTS companion_threads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    thread_id TEXT NOT NULL,
                    character_id TEXT,
                    role TEXT NOT NULL,
                    text TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_threads_user ON companion_threads(user_id, thread_id);
                CREATE TABLE IF NOT EXISTS companion_memory_items (
                    storage_key TEXT NOT NULL,
                    item_key TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (storage_key, item_key)
                );
                CREATE INDEX IF NOT EXISTS idx_memory_storage ON companion_memory_items(storage_key, updated_at);
                CREATE TABLE IF NOT EXISTS companion_profile (
                    storage_key TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS companion_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    storage_key TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    character_id TEXT NOT NULL,
                    thread_id TEXT,
                    vote TEXT NOT NULL,
                    rating INTEGER NOT NULL,
                    assistant_excerpt TEXT,
                    user_excerpt TEXT,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_companion_feedback_scope
                    ON companion_feedback(storage_key, created_at);
                CREATE TABLE IF NOT EXISTS companion_stream_cache (
                    message_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    tokens_json TEXT NOT NULL,
                    meta_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS companion_trust_meta (
                    user_id TEXT NOT NULL,
                    character_id TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (user_id, character_id)
                );
                CREATE TABLE IF NOT EXISTS companion_workspaces (
                    user_id TEXT NOT NULL,
                    workspace_id TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (user_id, workspace_id)
                );
                CREATE TABLE IF NOT EXISTS companion_cogs_daily (
                    user_id TEXT NOT NULL,
                    day TEXT NOT NULL,
                    cost_usd REAL NOT NULL DEFAULT 0,
                    turns INTEGER NOT NULL DEFAULT 0,
                    PRIMARY KEY (user_id, day)
                );
                """
            )

    def get_trust(self, user_id: str, character_id: str) -> int:
        with self._lock, self._conn() as conn:
            row = conn.execute(
                "SELECT score FROM companion_trust WHERE user_id=? AND character_id=?",
                (user_id, character_id),
            ).fetchone()
            return int(row["score"]) if row else 10

    def set_trust(self, user_id: str, character_id: str, score: int) -> int:
        score = max(0, min(100, int(score)))
        now = datetime.utcnow().isoformat()
        with self._lock, self._conn() as conn:
            conn.execute(
                """
                INSERT INTO companion_trust(user_id, character_id, score, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id, character_id) DO UPDATE SET
                    score=excluded.score, updated_at=excluded.updated_at
                """,
                (user_id, character_id, score, now),
            )
        return score

    def get_consent(self, user_id: str) -> Dict[str, Any]:
        with self._lock, self._conn() as conn:
            row = conn.execute(
                "SELECT payload FROM companion_consent WHERE user_id=?",
                (user_id,),
            ).fetchone()
            if not row:
                return {}
            return json.loads(row["payload"])

    def set_consent(self, user_id: str, payload: Dict[str, Any]) -> None:
        now = datetime.utcnow().isoformat()
        with self._lock, self._conn() as conn:
            conn.execute(
                """
                INSERT INTO companion_consent(user_id, payload, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    payload=excluded.payload, updated_at=excluded.updated_at
                """,
                (user_id, json.dumps(payload), now),
            )
            if "memory_enabled" in payload:
                conn.execute(
                    """
                    INSERT INTO companion_memory_flag(user_id, enabled, updated_at)
                    VALUES (?, ?, ?)
                    ON CONFLICT(user_id) DO UPDATE SET
                        enabled=excluded.enabled, updated_at=excluded.updated_at
                    """,
                    (user_id, 1 if payload.get("memory_enabled") else 0, now),
                )

    def memory_enabled(self, user_id: str) -> bool:
        with self._lock, self._conn() as conn:
            row = conn.execute(
                "SELECT enabled FROM companion_memory_flag WHERE user_id=?",
                (user_id,),
            ).fetchone()
            return bool(row and row["enabled"])

    def list_memory_items(self, storage_key: str, limit: int = 50) -> List[Dict[str, Any]]:
        with self._lock, self._conn() as conn:
            rows = conn.execute(
                """
                SELECT item_key, summary, updated_at
                FROM companion_memory_items
                WHERE storage_key=?
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (storage_key, limit),
            ).fetchall()
        return [
            {
                "key": r["item_key"],
                "summary": r["summary"],
                "updated_at": r["updated_at"],
            }
            for r in rows
        ]

    def upsert_memory_item(self, storage_key: str, item_key: str, summary: str) -> None:
        now = datetime.utcnow().isoformat()
        safe_summary = summary.strip()[:2000]
        if not safe_summary:
            return
        with self._lock, self._conn() as conn:
            conn.execute(
                """
                INSERT INTO companion_memory_items(storage_key, item_key, summary, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(storage_key, item_key) DO UPDATE SET
                    summary=excluded.summary, updated_at=excluded.updated_at
                """,
                (storage_key, item_key, safe_summary, now),
            )

    def get_profile(self, storage_key: str) -> Dict[str, Any]:
        with self._lock, self._conn() as conn:
            row = conn.execute(
                "SELECT payload FROM companion_profile WHERE storage_key=?",
                (storage_key,),
            ).fetchone()
            if not row:
                return {}
            return json.loads(row["payload"])

    def set_profile(self, storage_key: str, payload: Dict[str, Any]) -> None:
        now = datetime.utcnow().isoformat()
        with self._lock, self._conn() as conn:
            conn.execute(
                """
                INSERT INTO companion_profile(storage_key, payload, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(storage_key) DO UPDATE SET
                    payload=excluded.payload, updated_at=excluded.updated_at
                """,
                (storage_key, json.dumps(payload), now),
            )

    def put_stream_cache(
        self,
        message_id: str,
        user_id: str,
        tokens: List[str],
        meta: Dict[str, Any],
    ) -> None:
        try:
            from security.services.ai_platform.companion_stream_redis import (
                put_stream_cache_redis,
                stream_cache_backend,
            )
        except ImportError:
            from companion_stream_redis import (  # type: ignore
                put_stream_cache_redis,
                stream_cache_backend,
            )
        if stream_cache_backend() == "redis" and put_stream_cache_redis(
            message_id, user_id, tokens, meta
        ):
            return
        now = datetime.utcnow().isoformat()
        with self._lock, self._conn() as conn:
            conn.execute(
                """
                INSERT INTO companion_stream_cache(message_id, user_id, tokens_json, meta_json, created_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(message_id) DO UPDATE SET
                    user_id=excluded.user_id,
                    tokens_json=excluded.tokens_json,
                    meta_json=excluded.meta_json,
                    created_at=excluded.created_at
                """,
                (message_id, user_id, json.dumps(tokens), json.dumps(meta), now),
            )

    def get_stream_cache(self, message_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        try:
            from security.services.ai_platform.companion_stream_redis import (
                get_stream_cache_redis,
                stream_cache_backend,
            )
        except ImportError:
            from companion_stream_redis import (  # type: ignore
                get_stream_cache_redis,
                stream_cache_backend,
            )
        if stream_cache_backend() == "redis":
            cached = get_stream_cache_redis(message_id, user_id)
            if cached is not None:
                return cached
        with self._lock, self._conn() as conn:
            row = conn.execute(
                "SELECT user_id, tokens_json, meta_json FROM companion_stream_cache WHERE message_id=?",
                (message_id,),
            ).fetchone()
            if not row:
                return None
            if user_id and str(row["user_id"]) != str(user_id):
                return None
            return {
                "tokens": json.loads(row["tokens_json"]),
                "meta": json.loads(row["meta_json"]),
            }

    def delete_stream_cache(self, message_id: str) -> None:
        try:
            from security.services.ai_platform.companion_stream_redis import (
                delete_stream_cache_redis,
                stream_cache_backend,
            )
        except ImportError:
            from companion_stream_redis import (  # type: ignore
                delete_stream_cache_redis,
                stream_cache_backend,
            )
        if stream_cache_backend() == "redis":
            delete_stream_cache_redis(message_id)
        with self._lock, self._conn() as conn:
            conn.execute("DELETE FROM companion_stream_cache WHERE message_id=?", (message_id,))

    def record_feedback(
        self,
        storage_key: str,
        user_id: str,
        character_id: str,
        vote: str,
        rating: int,
        thread_id: Optional[str] = None,
        assistant_excerpt: Optional[str] = None,
        user_excerpt: Optional[str] = None,
    ) -> int:
        now = datetime.utcnow().isoformat()
        with self._lock, self._conn() as conn:
            cur = conn.execute(
                """
                INSERT INTO companion_feedback(
                    storage_key, user_id, character_id, thread_id, vote, rating,
                    assistant_excerpt, user_excerpt, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    storage_key,
                    user_id,
                    character_id,
                    thread_id,
                    vote,
                    int(rating),
                    (assistant_excerpt or "")[:500],
                    (user_excerpt or "")[:500],
                    now,
                ),
            )
            return int(cur.lastrowid or 0)

    def feedback_summary(self, storage_key: str, character_id: Optional[str] = None) -> Dict[str, int]:
        with self._lock, self._conn() as conn:
            if character_id:
                rows = conn.execute(
                    """
                    SELECT vote, COUNT(*) AS cnt
                    FROM companion_feedback
                    WHERE storage_key=? AND character_id=?
                    GROUP BY vote
                    """,
                    (storage_key, character_id),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT vote, COUNT(*) AS cnt
                    FROM companion_feedback
                    WHERE storage_key=?
                    GROUP BY vote
                    """,
                    (storage_key,),
                ).fetchall()
        out = {"up": 0, "down": 0}
        for r in rows:
            if r["vote"] in out:
                out[r["vote"]] = int(r["cnt"])
        return out

    def delete_all_memory_items(self, storage_key: str) -> int:
        with self._lock, self._conn() as conn:
            cur = conn.execute(
                "DELETE FROM companion_memory_items WHERE storage_key=?",
                (storage_key,),
            )
            return int(cur.rowcount or 0)

    def append_thread_message(
        self,
        user_id: str,
        thread_id: str,
        role: str,
        text: str,
        character_id: Optional[str] = None,
    ) -> None:
        now = datetime.utcnow().isoformat()
        with self._lock, self._conn() as conn:
            conn.execute(
                """
                INSERT INTO companion_threads(user_id, thread_id, character_id, role, text, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (user_id, thread_id, character_id, role, text[:4000], now),
            )

    def list_thread_summaries(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        with self._lock, self._conn() as conn:
            rows = conn.execute(
                """
                SELECT t.thread_id,
                       MAX(t.created_at) AS updated_at,
                       COUNT(*) AS message_count,
                       (
                         SELECT text FROM companion_threads t2
                         WHERE t2.user_id = t.user_id AND t2.thread_id = t.thread_id
                           AND t2.role = 'user'
                         ORDER BY t2.created_at ASC LIMIT 1
                       ) AS first_user_text,
                       (
                         SELECT character_id FROM companion_threads t3
                         WHERE t3.user_id = t.user_id AND t3.thread_id = t.thread_id
                           AND t3.character_id IS NOT NULL AND t3.character_id != ''
                         ORDER BY t3.created_at DESC LIMIT 1
                       ) AS character_id
                FROM companion_threads t
                WHERE t.user_id=?
                GROUP BY t.thread_id
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (user_id, limit),
            ).fetchall()
        out: List[Dict[str, Any]] = []
        for r in rows:
            title_src = r["first_user_text"] or "Разговор"
            out.append(
                {
                    "thread_id": r["thread_id"],
                    "title": str(title_src)[:80],
                    "updated_at": r["updated_at"],
                    "message_count": r["message_count"],
                    "character_id": r["character_id"] or "unicorn",
                }
            )
        return out

    def get_thread_messages(
        self, user_id: str, thread_id: str, limit: int = 100
    ) -> List[Dict[str, Any]]:
        with self._lock, self._conn() as conn:
            rows = conn.execute(
                """
                SELECT role, text, created_at, character_id
                FROM companion_threads
                WHERE user_id=? AND thread_id=?
                ORDER BY created_at ASC
                LIMIT ?
                """,
                (user_id, thread_id, limit),
            ).fetchall()
        return [
            {
                "role": r["role"],
                "text": r["text"],
                "created_at": r["created_at"],
                "character_id": r["character_id"],
            }
            for r in rows
        ]

    def _today(self) -> str:
        return date.today().isoformat()

    def get_usage_today(self, user_id: str) -> Dict[str, int]:
        day = self._today()
        with self._lock, self._conn() as conn:
            row = conn.execute(
                "SELECT messages, voice_seconds FROM usage_daily WHERE user_id=? AND day=?",
                (user_id, day),
            ).fetchone()
            if not row:
                return {"messages": 0, "voice_seconds": 0}
            return {"messages": int(row["messages"]), "voice_seconds": int(row["voice_seconds"])}

    def increment_messages(self, user_id: str, count: int = 1) -> Dict[str, int]:
        day = self._today()
        with self._lock, self._conn() as conn:
            conn.execute(
                """
                INSERT INTO usage_daily(user_id, day, messages, voice_seconds)
                VALUES (?, ?, ?, 0)
                ON CONFLICT(user_id, day) DO UPDATE SET
                    messages = messages + ?
                """,
                (user_id, day, count, count),
            )
        return self.get_usage_today(user_id)

    def increment_voice_seconds(self, user_id: str, seconds: int) -> Dict[str, int]:
        day = self._today()
        seconds = max(0, int(seconds))
        with self._lock, self._conn() as conn:
            conn.execute(
                """
                INSERT INTO usage_daily(user_id, day, messages, voice_seconds)
                VALUES (?, ?, 0, ?)
                ON CONFLICT(user_id, day) DO UPDATE SET
                    voice_seconds = voice_seconds + ?
                """,
                (user_id, day, seconds, seconds),
            )
        return self.get_usage_today(user_id)

    def get_trust_meta(self, user_id: str, character_id: str) -> Dict[str, Any]:
        with self._lock, self._conn() as conn:
            row = conn.execute(
                "SELECT payload FROM companion_trust_meta WHERE user_id=? AND character_id=?",
                (user_id, character_id),
            ).fetchone()
            if not row:
                return {}
            return json.loads(row["payload"])

    def set_trust_meta(self, user_id: str, character_id: str, payload: Dict[str, Any]) -> None:
        now = datetime.utcnow().isoformat()
        with self._lock, self._conn() as conn:
            conn.execute(
                """
                INSERT INTO companion_trust_meta(user_id, character_id, payload, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id, character_id) DO UPDATE SET
                    payload=excluded.payload, updated_at=excluded.updated_at
                """,
                (user_id, character_id, json.dumps(payload), now),
            )

    def list_workspaces(self, user_id: str, limit: int = 30) -> List[Dict[str, Any]]:
        with self._lock, self._conn() as conn:
            rows = conn.execute(
                """
                SELECT workspace_id, payload, updated_at
                FROM companion_workspaces
                WHERE user_id=?
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (user_id, limit),
            ).fetchall()
        out: List[Dict[str, Any]] = []
        for r in rows:
            data = json.loads(r["payload"])
            data.setdefault("workspace_id", r["workspace_id"])
            data["updated_at"] = r["updated_at"]
            out.append(data)
        return out

    def get_workspace(self, user_id: str, workspace_id: str) -> Optional[Dict[str, Any]]:
        with self._lock, self._conn() as conn:
            row = conn.execute(
                "SELECT payload FROM companion_workspaces WHERE user_id=? AND workspace_id=?",
                (user_id, workspace_id),
            ).fetchone()
            if not row:
                return None
            return json.loads(row["payload"])

    def upsert_workspace(self, user_id: str, workspace_id: str, payload: Dict[str, Any]) -> None:
        now = datetime.utcnow().isoformat()
        with self._lock, self._conn() as conn:
            conn.execute(
                """
                INSERT INTO companion_workspaces(user_id, workspace_id, payload, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id, workspace_id) DO UPDATE SET
                    payload=excluded.payload, updated_at=excluded.updated_at
                """,
                (user_id, workspace_id, json.dumps(payload), now),
            )

    def record_cogs(self, user_id: str, *, cost_usd: float) -> Dict[str, Any]:
        day = self._today()
        cost = max(0.0, float(cost_usd))
        with self._lock, self._conn() as conn:
            conn.execute(
                """
                INSERT INTO companion_cogs_daily(user_id, day, cost_usd, turns)
                VALUES (?, ?, ?, 1)
                ON CONFLICT(user_id, day) DO UPDATE SET
                    cost_usd = cost_usd + excluded.cost_usd,
                    turns = turns + 1
                """,
                (user_id, day, cost),
            )
        return self.get_cogs_snapshot(user_id)

    def get_cogs_snapshot(self, user_id: str) -> Dict[str, Any]:
        day = self._today()
        month_prefix = day[:7]
        with self._lock, self._conn() as conn:
            daily = conn.execute(
                "SELECT cost_usd, turns FROM companion_cogs_daily WHERE user_id=? AND day=?",
                (user_id, day),
            ).fetchone()
            month_rows = conn.execute(
                "SELECT cost_usd FROM companion_cogs_daily WHERE user_id=? AND day LIKE ?",
                (user_id, f"{month_prefix}%"),
            ).fetchall()
        month_usd = sum(float(r["cost_usd"]) for r in month_rows)
        return {
            "daily_usd": float(daily["cost_usd"]) if daily else 0.0,
            "turns_today": int(daily["turns"]) if daily else 0,
            "month_usd": month_usd,
        }


_store: Optional[CompanionStore] = None


def get_companion_store() -> CompanionStore:
    global _store
    if _store is None:
        backend = os.getenv("COMPANION_STORE_BACKEND", "sqlite").strip().lower()
        if backend == "postgres":
            logger = logging.getLogger(__name__)
            logger.warning(
                "COMPANION_STORE_BACKEND=postgres requested; using SQLite MVP until migration (P1-12)"
            )
        _store = CompanionStore()
    return _store
