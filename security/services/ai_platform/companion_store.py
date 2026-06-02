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
                CREATE TABLE IF NOT EXISTS wellness_checkins (
                    user_id TEXT NOT NULL,
                    day TEXT NOT NULL,
                    mood_emoji TEXT,
                    mood_score INTEGER,
                    sleep_hours REAL,
                    stress_level INTEGER,
                    energy_level INTEGER,
                    notes TEXT,
                    source TEXT NOT NULL DEFAULT 'app',
                    age_band TEXT,
                    created_at TEXT NOT NULL,
                    PRIMARY KEY (user_id, day)
                );
                CREATE TABLE IF NOT EXISTS wellness_assessments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    assessment_type TEXT NOT NULL,
                    answers_json TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    severity TEXT NOT NULL,
                    suggest_professional INTEGER NOT NULL DEFAULT 0,
                    disclaimer_version TEXT NOT NULL DEFAULT 'v1',
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS wellness_exercises (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    pillar TEXT NOT NULL,
                    exercise_type TEXT NOT NULL,
                    state_json TEXT NOT NULL DEFAULT '{}',
                    step_index INTEGER NOT NULL DEFAULT 0,
                    completed INTEGER NOT NULL DEFAULT 0,
                    thread_id TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS wellness_settings (
                    user_id TEXT PRIMARY KEY,
                    primary_pillar TEXT,
                    exercise_id TEXT,
                    exercise_step INTEGER NOT NULL DEFAULT 0,
                    exercise_step_total INTEGER NOT NULL DEFAULT 0,
                    escalation_level TEXT NOT NULL DEFAULT 'L0',
                    parent_share_aggregate INTEGER NOT NULL DEFAULT 0,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS wellness_outcomes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    pillar TEXT NOT NULL,
                    helpful INTEGER NOT NULL,
                    note TEXT,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS wellness_dreams (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    dream_text TEXT NOT NULL,
                    mood_tag TEXT,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS wellness_alert_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    action_taken TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS wellness_habit_plans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    if_then TEXT NOT NULL,
                    streak INTEGER NOT NULL DEFAULT 0,
                    active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS wellness_insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    pillar TEXT NOT NULL,
                    observe_text TEXT NOT NULL,
                    next_step_text TEXT,
                    source TEXT NOT NULL DEFAULT 'exercise',
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS wellness_crisis_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    level TEXT NOT NULL,
                    source TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )
            try:
                conn.execute(
                    "ALTER TABLE wellness_settings ADD COLUMN daily_reminder_hour INTEGER DEFAULT 19"
                )
            except sqlite3.OperationalError:
                pass
            try:
                conn.execute(
                    "ALTER TABLE wellness_settings ADD COLUMN daily_reminder_enabled INTEGER DEFAULT 0"
                )
            except sqlite3.OperationalError:
                pass
            try:
                conn.execute(
                    "ALTER TABLE wellness_settings ADD COLUMN last_idle_nudge_day TEXT"
                )
            except sqlite3.OperationalError:
                pass
            for col, ddl in (
                ("session_pillar_locked", "TEXT"),
                ("session_started_at", "TEXT"),
                ("last_session_completed_at", "TEXT"),
                ("last_outcome_prompt_day", "TEXT"),
                ("fatigue_streak_pillar", "TEXT"),
                ("fatigue_streak_count", "INTEGER DEFAULT 0"),
                ("alliance_score", "INTEGER DEFAULT 50"),
                ("hero_emotion", "TEXT"),
                ("last_trauma_referral_day", "TEXT"),
                ("last_weekly_meaning_day", "TEXT"),
                ("session_pack_folder", "TEXT"),
                ("session_pack_version", "TEXT"),
            ):
                try:
                    conn.execute(
                        f"ALTER TABLE wellness_settings ADD COLUMN {col} {ddl}"
                    )
                except sqlite3.OperationalError:
                    pass

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

    def get_wellness_settings(self, user_id: str) -> Dict[str, Any]:
        with self._lock, self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM wellness_settings WHERE user_id=?",
                (user_id,),
            ).fetchone()
            if not row:
                return {
                    "primary_pillar": None,
                    "exercise_id": None,
                    "exercise_step": 0,
                    "exercise_step_total": 0,
                    "escalation_level": "L0",
                    "parent_share_aggregate": 0,
                    "daily_reminder_hour": 19,
                    "daily_reminder_enabled": 0,
                }
            data = dict(row)
            if data.get("daily_reminder_hour") is None:
                data["daily_reminder_hour"] = 19
            return data

    def upsert_wellness_settings(
        self,
        user_id: str,
        *,
        primary_pillar: Optional[str] = None,
        exercise_id: Optional[str] = None,
        exercise_step: Optional[int] = None,
        exercise_step_total: Optional[int] = None,
        escalation_level: Optional[str] = None,
        parent_share_aggregate: Optional[int] = None,
        last_idle_nudge_day: Optional[str] = None,
        session_pillar_locked: Optional[str] = None,
        session_started_at: Optional[str] = None,
        last_session_completed_at: Optional[str] = None,
        last_outcome_prompt_day: Optional[str] = None,
        fatigue_streak_pillar: Optional[str] = None,
        fatigue_streak_count: Optional[int] = None,
        last_weekly_meaning_day: Optional[str] = None,
        clear_session_lock: bool = False,
    ) -> Dict[str, Any]:
        current = self.get_wellness_settings(user_id)
        if primary_pillar is not None:
            current["primary_pillar"] = primary_pillar
        if exercise_id is not None:
            current["exercise_id"] = exercise_id
        if exercise_step is not None:
            current["exercise_step"] = int(exercise_step)
        if exercise_step_total is not None:
            current["exercise_step_total"] = int(exercise_step_total)
        if escalation_level is not None:
            current["escalation_level"] = escalation_level
        if parent_share_aggregate is not None:
            current["parent_share_aggregate"] = int(parent_share_aggregate)
        if last_idle_nudge_day is not None:
            current["last_idle_nudge_day"] = last_idle_nudge_day
        if session_pillar_locked is not None:
            current["session_pillar_locked"] = session_pillar_locked
        if session_started_at is not None:
            current["session_started_at"] = session_started_at
        if last_session_completed_at is not None:
            current["last_session_completed_at"] = last_session_completed_at
        if last_outcome_prompt_day is not None:
            current["last_outcome_prompt_day"] = last_outcome_prompt_day
        if fatigue_streak_pillar is not None:
            current["fatigue_streak_pillar"] = fatigue_streak_pillar
        if fatigue_streak_count is not None:
            current["fatigue_streak_count"] = int(fatigue_streak_count)
        if last_weekly_meaning_day is not None:
            current["last_weekly_meaning_day"] = last_weekly_meaning_day
        if clear_session_lock:
            current["session_pillar_locked"] = None
            current["session_started_at"] = None
        now = datetime.utcnow().isoformat()
        with self._lock, self._conn() as conn:
            exists = conn.execute(
                "SELECT 1 FROM wellness_settings WHERE user_id=?",
                (user_id,),
            ).fetchone()
            if parent_share_aggregate is None and not exists:
                # p1-23: new wellness_settings row — parent aggregate OFF by default
                current["parent_share_aggregate"] = 0
            conn.execute(
                """
                INSERT INTO wellness_settings(
                    user_id, primary_pillar, exercise_id, exercise_step,
                    exercise_step_total, escalation_level, parent_share_aggregate,
                    daily_reminder_hour, daily_reminder_enabled, last_idle_nudge_day,
                    session_pillar_locked, session_started_at, last_session_completed_at,
                    last_outcome_prompt_day, fatigue_streak_pillar, fatigue_streak_count,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    primary_pillar=excluded.primary_pillar,
                    exercise_id=excluded.exercise_id,
                    exercise_step=excluded.exercise_step,
                    exercise_step_total=excluded.exercise_step_total,
                    escalation_level=excluded.escalation_level,
                    parent_share_aggregate=excluded.parent_share_aggregate,
                    daily_reminder_hour=excluded.daily_reminder_hour,
                    daily_reminder_enabled=excluded.daily_reminder_enabled,
                    last_idle_nudge_day=excluded.last_idle_nudge_day,
                    session_pillar_locked=excluded.session_pillar_locked,
                    session_started_at=excluded.session_started_at,
                    last_session_completed_at=excluded.last_session_completed_at,
                    last_outcome_prompt_day=excluded.last_outcome_prompt_day,
                    fatigue_streak_pillar=excluded.fatigue_streak_pillar,
                    fatigue_streak_count=excluded.fatigue_streak_count,
                    updated_at=excluded.updated_at
                """,
                (
                    user_id,
                    current.get("primary_pillar"),
                    current.get("exercise_id"),
                    int(current.get("exercise_step") or 0),
                    int(current.get("exercise_step_total") or 0),
                    str(current.get("escalation_level") or "L0"),
                    int(current.get("parent_share_aggregate") or 0),
                    int(current.get("daily_reminder_hour") or 19),
                    int(current.get("daily_reminder_enabled") or 0),
                    current.get("last_idle_nudge_day"),
                    current.get("session_pillar_locked"),
                    current.get("session_started_at"),
                    current.get("last_session_completed_at"),
                    current.get("last_outcome_prompt_day"),
                    current.get("fatigue_streak_pillar"),
                    int(current.get("fatigue_streak_count") or 0),
                    now,
                ),
            )
        result = self.get_wellness_settings(user_id)
        if result:
            try:
                from security.services.ai_platform.wellness_store_dual import (
                    mirror_settings_to_postgres,
                )

                mirror_settings_to_postgres(result)
            except Exception:
                pass
        return result

    def update_wellness_misc(
        self,
        user_id: str,
        **fields: Any,
    ) -> Dict[str, Any]:
        """Patch optional wellness_settings columns (weekly meaning, etc.)."""
        if not fields:
            return self.get_wellness_settings(user_id)
        allowed = {
            "last_weekly_meaning_day",
            "last_trauma_referral_day",
            "session_pack_folder",
            "session_pack_version",
        }
        sets = []
        vals: List[Any] = []
        for key, val in fields.items():
            if key in allowed:
                sets.append(f"{key}=?")
                vals.append(val)
        if not sets:
            return self.get_wellness_settings(user_id)
        now = datetime.utcnow().isoformat()
        sets.append("updated_at=?")
        vals.append(now)
        vals.append(user_id)
        with self._lock, self._conn() as conn:
            exists = conn.execute(
                "SELECT 1 FROM wellness_settings WHERE user_id=?",
                (user_id,),
            ).fetchone()
            if not exists:
                conn.execute(
                    """
                    INSERT INTO wellness_settings(
                        user_id, escalation_level, parent_share_aggregate, updated_at
                    ) VALUES (?, 'L0', 0, ?)
                    """,
                    (user_id, now),
                )
            conn.execute(
                f"UPDATE wellness_settings SET {', '.join(sets)} WHERE user_id=?",
                vals,
            )
        return self.get_wellness_settings(user_id)

    def update_wellness_alliance(
        self,
        user_id: str,
        *,
        alliance_score: int,
        hero_emotion: Optional[str] = None,
    ) -> Dict[str, Any]:
        score = max(0, min(100, int(alliance_score)))
        emotion = hero_emotion or "warm"
        now = datetime.utcnow().isoformat()
        with self._lock, self._conn() as conn:
            exists = conn.execute(
                "SELECT 1 FROM wellness_settings WHERE user_id=?",
                (user_id,),
            ).fetchone()
            if not exists:
                conn.execute(
                    """
                    INSERT INTO wellness_settings(
                        user_id, escalation_level, parent_share_aggregate,
                        alliance_score, hero_emotion, updated_at
                    ) VALUES (?, 'L0', 0, ?, ?, ?)
                    """,
                    (user_id, score, emotion, now),
                )
            else:
                conn.execute(
                    """
                    UPDATE wellness_settings
                    SET alliance_score=?, hero_emotion=?, updated_at=?
                    WHERE user_id=?
                    """,
                    (score, emotion, now, user_id),
                )
        return self.get_wellness_settings(user_id)

    def upsert_wellness_checkin(
        self,
        user_id: str,
        *,
        day: str,
        mood_emoji: Optional[str] = None,
        mood_score: Optional[int] = None,
        sleep_hours: Optional[float] = None,
        stress_level: Optional[int] = None,
        energy_level: Optional[int] = None,
        notes: Optional[str] = None,
        source: str = "app",
        age_band: Optional[str] = None,
    ) -> Dict[str, Any]:
        now = datetime.utcnow().isoformat()
        with self._lock, self._conn() as conn:
            conn.execute(
                """
                INSERT INTO wellness_checkins(
                    user_id, day, mood_emoji, mood_score, sleep_hours, stress_level,
                    energy_level, notes, source, age_band, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id, day) DO UPDATE SET
                    mood_emoji=excluded.mood_emoji,
                    mood_score=excluded.mood_score,
                    sleep_hours=excluded.sleep_hours,
                    stress_level=excluded.stress_level,
                    energy_level=excluded.energy_level,
                    notes=excluded.notes,
                    source=excluded.source,
                    age_band=excluded.age_band,
                    created_at=excluded.created_at
                """,
                (
                    user_id,
                    day,
                    mood_emoji,
                    mood_score,
                    sleep_hours,
                    stress_level,
                    energy_level,
                    notes,
                    source,
                    age_band,
                    now,
                ),
            )
            row = conn.execute(
                "SELECT * FROM wellness_checkins WHERE user_id=? AND day=?",
                (user_id, day),
            ).fetchone()
        out = dict(row) if row else {}
        if out:
            try:
                from security.services.ai_platform.wellness_store_dual import (
                    mirror_checkin_to_postgres,
                )

                mirror_checkin_to_postgres(out)
            except Exception:
                pass
        return out

    def get_wellness_checkin(self, user_id: str, day: str) -> Optional[Dict[str, Any]]:
        with self._lock, self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM wellness_checkins WHERE user_id=? AND day=?",
                (user_id, day),
            ).fetchone()
        return dict(row) if row else None

    def list_wellness_checkins(self, user_id: str, *, days: int = 7) -> List[Dict[str, Any]]:
        with self._lock, self._conn() as conn:
            rows = conn.execute(
                """
                SELECT * FROM wellness_checkins
                WHERE user_id=?
                ORDER BY day DESC
                LIMIT ?
                """,
                (user_id, max(1, int(days))),
            ).fetchall()
        return [dict(r) for r in rows]

    def save_wellness_assessment(
        self,
        user_id: str,
        *,
        assessment_type: str,
        answers: List[int],
        score: int,
        severity: str,
        suggest_professional: bool,
        disclaimer_version: str = "v1",
    ) -> Dict[str, Any]:
        now = datetime.utcnow().isoformat()
        with self._lock, self._conn() as conn:
            cur = conn.execute(
                """
                INSERT INTO wellness_assessments(
                    user_id, assessment_type, answers_json, score, severity,
                    suggest_professional, disclaimer_version, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    assessment_type,
                    json.dumps(answers),
                    int(score),
                    severity,
                    1 if suggest_professional else 0,
                    disclaimer_version,
                    now,
                ),
            )
            row = conn.execute(
                "SELECT * FROM wellness_assessments WHERE id=?",
                (cur.lastrowid,),
            ).fetchone()
        return dict(row) if row else {}

    def list_wellness_assessments(
        self, user_id: str, *, limit: int = 20
    ) -> List[Dict[str, Any]]:
        with self._lock, self._conn() as conn:
            rows = conn.execute(
                """
                SELECT * FROM wellness_assessments
                WHERE user_id=?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (user_id, max(1, int(limit))),
            ).fetchall()
        return [dict(r) for r in rows]

    def create_wellness_exercise(
        self,
        user_id: str,
        *,
        pillar: str,
        exercise_type: str,
        step_index: int,
        step_total: int,
        state_json: str,
        created_at: str,
        thread_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        now = created_at
        with self._lock, self._conn() as conn:
            cur = conn.execute(
                """
                INSERT INTO wellness_exercises(
                    user_id, pillar, exercise_type, state_json, step_index,
                    completed, thread_id, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, 0, ?, ?, ?)
                """,
                (
                    user_id,
                    pillar,
                    exercise_type,
                    state_json,
                    int(step_index),
                    thread_id,
                    now,
                    now,
                ),
            )
            row = conn.execute(
                "SELECT * FROM wellness_exercises WHERE id=?",
                (cur.lastrowid,),
            ).fetchone()
        return dict(row) if row else {}

    def get_wellness_exercise(
        self, user_id: str, exercise_id: int
    ) -> Optional[Dict[str, Any]]:
        with self._lock, self._conn() as conn:
            row = conn.execute(
                """
                SELECT * FROM wellness_exercises
                WHERE id=? AND user_id=?
                """,
                (int(exercise_id), user_id),
            ).fetchone()
        return dict(row) if row else None

    def get_active_wellness_exercise(self, user_id: str) -> Optional[Dict[str, Any]]:
        with self._lock, self._conn() as conn:
            row = conn.execute(
                """
                SELECT * FROM wellness_exercises
                WHERE user_id=? AND completed=0
                ORDER BY id DESC LIMIT 1
                """,
                (user_id,),
            ).fetchone()
        return dict(row) if row else None

    def update_wellness_exercise(
        self,
        user_id: str,
        exercise_id: int,
        *,
        step_index: int,
        state_json: str,
    ) -> Dict[str, Any]:
        now = datetime.utcnow().isoformat()
        with self._lock, self._conn() as conn:
            conn.execute(
                """
                UPDATE wellness_exercises
                SET step_index=?, state_json=?, updated_at=?
                WHERE id=? AND user_id=?
                """,
                (int(step_index), state_json, now, int(exercise_id), user_id),
            )
            row = conn.execute(
                "SELECT * FROM wellness_exercises WHERE id=? AND user_id=?",
                (int(exercise_id), user_id),
            ).fetchone()
        return dict(row) if row else {}

    def complete_wellness_exercise(
        self,
        user_id: str,
        exercise_id: int,
        *,
        state_json: str,
    ) -> Dict[str, Any]:
        now = datetime.utcnow().isoformat()
        with self._lock, self._conn() as conn:
            conn.execute(
                """
                UPDATE wellness_exercises
                SET completed=1, state_json=?, updated_at=?
                WHERE id=? AND user_id=?
                """,
                (state_json, now, int(exercise_id), user_id),
            )
            row = conn.execute(
                "SELECT * FROM wellness_exercises WHERE id=? AND user_id=?",
                (int(exercise_id), user_id),
            ).fetchone()
        return dict(row) if row else {}

    def list_wellness_exercises(
        self, user_id: str, *, limit: int = 20
    ) -> List[Dict[str, Any]]:
        with self._lock, self._conn() as conn:
            rows = conn.execute(
                """
                SELECT id, pillar, exercise_type, step_index, completed, created_at, updated_at
                FROM wellness_exercises
                WHERE user_id=?
                ORDER BY id DESC
                LIMIT ?
                """,
                (user_id, max(1, int(limit))),
            ).fetchall()
        return [dict(r) for r in rows]

    def save_wellness_outcome(
        self,
        user_id: str,
        *,
        pillar: str,
        helpful: int,
        note: Optional[str],
        created_at: str,
    ) -> Dict[str, Any]:
        with self._lock, self._conn() as conn:
            cur = conn.execute(
                """
                INSERT INTO wellness_outcomes(user_id, pillar, helpful, note, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, pillar, int(helpful), note, created_at),
            )
            row = conn.execute(
                "SELECT * FROM wellness_outcomes WHERE id=?",
                (cur.lastrowid,),
            ).fetchone()
        return dict(row) if row else {}

    def save_wellness_insight(
        self,
        user_id: str,
        *,
        pillar: str,
        observe_text: str,
        next_step_text: Optional[str] = None,
        source: str = "exercise",
        created_at: Optional[str] = None,
    ) -> Dict[str, Any]:
        now = created_at or datetime.utcnow().isoformat()
        with self._lock, self._conn() as conn:
            cur = conn.execute(
                """
                INSERT INTO wellness_insights(
                    user_id, pillar, observe_text, next_step_text, source, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    pillar,
                    observe_text[:500],
                    (next_step_text or "")[:500] or None,
                    source,
                    now,
                ),
            )
            row = conn.execute(
                "SELECT * FROM wellness_insights WHERE id=?",
                (cur.lastrowid,),
            ).fetchone()
        return dict(row) if row else {}

    def save_wellness_habit_plan(
        self,
        user_id: str,
        *,
        if_then: str,
        created_at: Optional[str] = None,
    ) -> Dict[str, Any]:
        now = created_at or datetime.utcnow().isoformat()
        with self._lock, self._conn() as conn:
            cur = conn.execute(
                """
                INSERT INTO wellness_habit_plans(
                    user_id, if_then, streak, active, created_at, updated_at
                ) VALUES (?, ?, 0, 1, ?, ?)
                """,
                (user_id, if_then[:500], now, now),
            )
            row = conn.execute(
                "SELECT * FROM wellness_habit_plans WHERE id=?",
                (cur.lastrowid,),
            ).fetchone()
        return dict(row) if row else {}

    def list_wellness_habit_plans(
        self, user_id: str, *, active_only: bool = True
    ) -> List[Dict[str, Any]]:
        with self._lock, self._conn() as conn:
            if active_only:
                rows = conn.execute(
                    """
                    SELECT * FROM wellness_habit_plans
                    WHERE user_id=? AND active=1
                    ORDER BY id DESC
                    LIMIT 20
                    """,
                    (user_id,),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT * FROM wellness_habit_plans
                    WHERE user_id=?
                    ORDER BY id DESC
                    LIMIT 20
                    """,
                    (user_id,),
                ).fetchall()
        return [dict(r) for r in rows]

    def get_last_wellness_insight(self, user_id: str) -> Optional[Dict[str, Any]]:
        with self._lock, self._conn() as conn:
            row = conn.execute(
                """
                SELECT * FROM wellness_insights
                WHERE user_id=?
                ORDER BY id DESC
                LIMIT 1
                """,
                (user_id,),
            ).fetchone()
        return dict(row) if row else None

    def list_wellness_outcomes(
        self, user_id: str, *, limit: int = 10
    ) -> List[Dict[str, Any]]:
        with self._lock, self._conn() as conn:
            rows = conn.execute(
                """
                SELECT * FROM wellness_outcomes
                WHERE user_id=?
                ORDER BY id DESC
                LIMIT ?
                """,
                (user_id, max(1, int(limit))),
            ).fetchall()
        return [dict(r) for r in rows]

    def save_wellness_dream(
        self,
        user_id: str,
        *,
        dream_text: str,
        mood_tag: Optional[str] = None,
        created_at: Optional[str] = None,
    ) -> Dict[str, Any]:
        now = created_at or datetime.utcnow().isoformat()
        with self._lock, self._conn() as conn:
            cur = conn.execute(
                """
                INSERT INTO wellness_dreams(user_id, dream_text, mood_tag, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, dream_text[:4000], mood_tag, now),
            )
            row = conn.execute(
                "SELECT * FROM wellness_dreams WHERE id=?",
                (cur.lastrowid,),
            ).fetchone()
        return dict(row) if row else {}

    def list_wellness_dreams(
        self, user_id: str, *, limit: int = 30
    ) -> List[Dict[str, Any]]:
        with self._lock, self._conn() as conn:
            rows = conn.execute(
                """
                SELECT id, dream_text, mood_tag, created_at
                FROM wellness_dreams
                WHERE user_id=?
                ORDER BY id DESC
                LIMIT ?
                """,
                (user_id, max(1, int(limit))),
            ).fetchall()
        return [dict(r) for r in rows]

    def log_wellness_crisis_event(
        self,
        user_id: str,
        *,
        level: str,
        source: str,
        created_at: str,
    ) -> Dict[str, Any]:
        with self._lock, self._conn() as conn:
            cur = conn.execute(
                """
                INSERT INTO wellness_crisis_log(user_id, level, source, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, level, source, created_at),
            )
            row = conn.execute(
                "SELECT * FROM wellness_crisis_log WHERE id=?",
                (cur.lastrowid,),
            ).fetchone()
        return dict(row) if row else {}

    def last_wellness_crisis_l3_at(self, user_id: str) -> Optional[str]:
        with self._lock, self._conn() as conn:
            row = conn.execute(
                """
                SELECT created_at FROM wellness_crisis_log
                WHERE user_id=? AND level='L3'
                ORDER BY id DESC
                LIMIT 1
                """,
                (user_id,),
            ).fetchone()
        return str(row["created_at"]) if row else None

    def list_wellness_crisis_log(
        self, user_id: str, *, limit: int = 10
    ) -> List[Dict[str, Any]]:
        with self._lock, self._conn() as conn:
            rows = conn.execute(
                """
                SELECT id, level, source, created_at
                FROM wellness_crisis_log
                WHERE user_id=?
                ORDER BY id DESC
                LIMIT ?
                """,
                (user_id, max(1, int(limit))),
            ).fetchall()
        return [dict(r) for r in rows]

    def save_wellness_alert_log(
        self,
        user_id: str,
        *,
        alert_type: str,
        severity: str,
        action_taken: str,
        created_at: str,
    ) -> Dict[str, Any]:
        with self._lock, self._conn() as conn:
            cur = conn.execute(
                """
                INSERT INTO wellness_alert_log(user_id, alert_type, severity, action_taken, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, alert_type, severity, action_taken, created_at),
            )
            row = conn.execute(
                "SELECT * FROM wellness_alert_log WHERE id=?",
                (cur.lastrowid,),
            ).fetchone()
        return dict(row) if row else {}

    def list_wellness_alert_log(
        self, user_id: str, *, limit: int = 20
    ) -> List[Dict[str, Any]]:
        with self._lock, self._conn() as conn:
            rows = conn.execute(
                """
                SELECT id, alert_type, severity, action_taken, created_at
                FROM wellness_alert_log
                WHERE user_id=?
                ORDER BY id DESC
                LIMIT ?
                """,
                (user_id, max(1, int(limit))),
            ).fetchall()
        return [dict(r) for r in rows]

    def list_wellness_insights(
        self, user_id: str, *, limit: int = 50
    ) -> List[Dict[str, Any]]:
        with self._lock, self._conn() as conn:
            rows = conn.execute(
                """
                SELECT * FROM wellness_insights
                WHERE user_id=?
                ORDER BY id DESC
                LIMIT ?
                """,
                (user_id, max(1, int(limit))),
            ).fetchall()
        return [dict(r) for r in rows]

    def delete_all_wellness_data(self, user_id: str) -> Dict[str, int]:
        """p3-05 — erase wellness tables for GDPR/152-ФЗ delete request."""
        counts: Dict[str, int] = {}
        tables = (
            "wellness_checkins",
            "wellness_assessments",
            "wellness_exercises",
            "wellness_outcomes",
            "wellness_dreams",
            "wellness_alert_log",
            "wellness_habit_plans",
            "wellness_insights",
            "wellness_crisis_log",
        )
        with self._lock, self._conn() as conn:
            for table in tables:
                cur = conn.execute(
                    f"DELETE FROM {table} WHERE user_id=?",
                    (user_id,),
                )
                counts[table] = int(cur.rowcount or 0)
            cur = conn.execute(
                "DELETE FROM wellness_settings WHERE user_id=?",
                (user_id,),
            )
            counts["wellness_settings"] = int(cur.rowcount or 0)
        return counts


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
