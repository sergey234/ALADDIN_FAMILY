# -*- coding: utf-8 -*-
"""
Postgres wellness store (p3-11): schema, dual-write mirror, read path.

Env:
  WELLNESS_PG_DSN / DATABASE_URL — postgres connection
  WELLNESS_PG_DUAL_WRITE=1 — mirror writes from companion_store (SQLite primary)
  WELLNESS_PG_READ=1 — read checkins from Postgres when configured
  WELLNESS_FIELD_ENCRYPTION_KEY — optional Fernet for notes/dreams (placeholder)
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

WELLNESS_PG_DSN = os.environ.get("WELLNESS_PG_DSN") or os.environ.get("DATABASE_URL")
WELLNESS_PG_DUAL_WRITE = os.getenv("WELLNESS_PG_DUAL_WRITE", "0").strip().lower() in (
    "1",
    "true",
    "yes",
)
WELLNESS_PG_READ = os.getenv("WELLNESS_PG_READ", "0").strip().lower() in ("1", "true", "yes")


def wellness_store_backend() -> str:
    if WELLNESS_PG_DSN:
        return "postgres"
    return "sqlite"


def dual_write_enabled() -> bool:
    return bool(WELLNESS_PG_DSN and WELLNESS_PG_DUAL_WRITE)


def pg_read_enabled() -> bool:
    return bool(WELLNESS_PG_DSN and WELLNESS_PG_READ)


def _connect():
    dsn = WELLNESS_PG_DSN
    if not dsn:
        return None
    try:
        import psycopg2  # type: ignore
        import psycopg2.extras  # type: ignore

        return psycopg2.connect(dsn, cursor_factory=psycopg2.extras.RealDictCursor)
    except Exception:
        return None


def ensure_schema() -> bool:
    conn = _connect()
    if not conn:
        return False
    schema_path = os.path.join(os.path.dirname(__file__), "wellness_pg_schema.sql")
    try:
        with open(schema_path, encoding="utf-8") as fh:
            ddl = fh.read()
        with conn:
            with conn.cursor() as cur:
                cur.execute(ddl)
        return True
    except Exception:
        return False
    finally:
        conn.close()


class WellnessPostgresStore:
    """Postgres adapter + ops ping."""

    def __init__(self, dsn: Optional[str] = None) -> None:
        self.dsn = dsn or WELLNESS_PG_DSN

    def is_configured(self) -> bool:
        return bool(self.dsn)

    def encrypt_field(self, plaintext: str) -> str:
        key = os.environ.get("WELLNESS_FIELD_ENCRYPTION_KEY", "").strip()
        if not key or not plaintext:
            return plaintext
        try:
            from cryptography.fernet import Fernet  # type: ignore

            f = Fernet(key.encode() if len(key) == 44 else Fernet.generate_key())
            return f.encrypt(plaintext.encode()).decode()
        except Exception:
            return plaintext

    def decrypt_field(self, ciphertext: str) -> str:
        return ciphertext

    def ping(self) -> dict[str, Any]:
        backend = wellness_store_backend()
        configured = self.is_configured()
        reachable = False
        if configured:
            conn = _connect()
            if conn:
                try:
                    with conn:
                        with conn.cursor() as cur:
                            cur.execute("SELECT 1")
                    reachable = True
                except Exception:
                    reachable = False
                finally:
                    conn.close()
        return {
            "backend": backend,
            "configured": configured,
            "reachable": reachable,
            "dual_write": dual_write_enabled(),
            "read_postgres": pg_read_enabled(),
        }

    def upsert_checkin_row(self, row: Dict[str, Any]) -> None:
        conn = _connect()
        if not conn or not row:
            return
        notes = row.get("notes")
        if notes:
            notes = self.encrypt_field(str(notes))
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO wellness_checkins(
                            user_id, day, mood_emoji, mood_score, sleep_hours,
                            stress_level, energy_level, notes, source, age_band, created_at
                        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        ON CONFLICT (user_id, day) DO UPDATE SET
                            mood_emoji=EXCLUDED.mood_emoji,
                            mood_score=EXCLUDED.mood_score,
                            sleep_hours=EXCLUDED.sleep_hours,
                            stress_level=EXCLUDED.stress_level,
                            energy_level=EXCLUDED.energy_level,
                            notes=EXCLUDED.notes,
                            source=EXCLUDED.source,
                            age_band=EXCLUDED.age_band,
                            created_at=EXCLUDED.created_at
                        """,
                        (
                            row.get("user_id"),
                            row.get("day"),
                            row.get("mood_emoji"),
                            row.get("mood_score"),
                            row.get("sleep_hours"),
                            row.get("stress_level"),
                            row.get("energy_level"),
                            notes,
                            row.get("source") or "app",
                            row.get("age_band"),
                            row.get("created_at") or datetime.utcnow().isoformat(),
                        ),
                    )
        finally:
            conn.close()

    def upsert_settings_row(self, row: Dict[str, Any]) -> None:
        conn = _connect()
        if not conn or not row:
            return
        uid = row.get("user_id")
        if not uid:
            return
        payload = json.dumps(row, ensure_ascii=False)
        now = row.get("updated_at") or datetime.utcnow().isoformat()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO wellness_settings(user_id, settings_json, updated_at)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (user_id) DO UPDATE SET
                            settings_json=EXCLUDED.settings_json,
                            updated_at=EXCLUDED.updated_at
                        """,
                        (uid, payload, now),
                    )
        finally:
            conn.close()

    def list_checkins(self, user_id: str, *, days: int = 7) -> List[Dict[str, Any]]:
        conn = _connect()
        if not conn:
            return []
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT * FROM wellness_checkins
                        WHERE user_id=%s
                        ORDER BY day DESC
                        LIMIT %s
                        """,
                        (user_id, max(1, int(days))),
                    )
                    rows = cur.fetchall()
            out = []
            for r in rows:
                d = dict(r)
                if d.get("notes"):
                    d["notes"] = self.decrypt_field(str(d["notes"]))
                out.append(d)
            return out
        finally:
            conn.close()
