"""Antifake async jobs persistence (af-3-02 lite for B1)."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy import text

from app.database.database import engine

_CREATE = """
CREATE TABLE IF NOT EXISTS antifake_jobs (
    id UUID PRIMARY KEY,
    user_id BIGINT NOT NULL,
    job_type VARCHAR(32) NOT NULL,
    status VARCHAR(16) NOT NULL DEFAULT 'queued',
    verdict JSONB,
    latency_ms INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


def ensure_table() -> None:
    with engine.begin() as conn:
        conn.execute(text(_CREATE))


def create_job(user_id: int, job_type: str) -> str:
    ensure_table()
    job_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO antifake_jobs (id, user_id, job_type, status, created_at, updated_at)
                VALUES (CAST(:id AS UUID), :user_id, :job_type, 'queued', :now, :now)
                """
            ),
            {"id": job_id, "user_id": int(user_id), "job_type": job_type, "now": now},
        )
    return job_id


def complete_job(job_id: str, verdict: Dict[str, Any], latency_ms: int) -> None:
    ensure_table()
    now = datetime.now(timezone.utc)
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                UPDATE antifake_jobs
                SET status = 'completed',
                    verdict = CAST(:verdict AS JSONB),
                    latency_ms = :latency_ms,
                    updated_at = :now
                WHERE id = CAST(:id AS UUID)
                """
            ),
            {
                "id": job_id,
                "verdict": json.dumps(verdict),
                "latency_ms": latency_ms,
                "now": now,
            },
        )


def fail_job(job_id: str, error: str) -> None:
    ensure_table()
    now = datetime.now(timezone.utc)
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                UPDATE antifake_jobs
                SET status = 'failed',
                    verdict = CAST(:verdict AS JSONB),
                    updated_at = :now
                WHERE id = CAST(:id AS UUID)
                """
            ),
            {
                "id": job_id,
                "verdict": json.dumps({"error": error}),
                "now": now,
            },
        )


def mark_job_processing(job_id: str) -> None:
    ensure_table()
    now = datetime.now(timezone.utc)
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                UPDATE antifake_jobs
                SET status = 'processing', updated_at = :now
                WHERE id = CAST(:id AS UUID) AND status = 'queued'
                """
            ),
            {"id": job_id, "now": now},
        )


def get_job(job_id: str, user_id: int) -> Optional[Dict[str, Any]]:
    ensure_table()
    with engine.connect() as conn:
        row = conn.execute(
            text(
                """
                SELECT id, job_type, status, verdict, latency_ms, created_at, updated_at
                FROM antifake_jobs
                WHERE id = CAST(:id AS UUID) AND user_id = :user_id
                """
            ),
            {"id": job_id, "user_id": int(user_id)},
        ).mappings().first()

    if not row:
        return None

    verdict = row["verdict"]
    if isinstance(verdict, str):
        verdict = json.loads(verdict)

    return {
        "job_id": str(row["id"]),
        "type": row["job_type"],
        "status": row["status"],
        "verdict": verdict,
        "latency_ms": row["latency_ms"],
        "created_at": row["created_at"].isoformat() if row["created_at"] else None,
        "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
    }


def metrics_for_user(user_id: int) -> Dict[str, Any]:
    ensure_table()
    with engine.connect() as conn:
        row = conn.execute(
            text(
                """
                SELECT
                    COUNT(*) AS checks_total,
                    COUNT(*) FILTER (
                        WHERE verdict->>'verdict' = 'likely_fake'
                    ) AS fake_detected,
                    COALESCE(AVG(latency_ms), 0) AS avg_latency_ms
                FROM antifake_jobs
                WHERE user_id = :user_id AND status = 'completed'
                """
            ),
            {"user_id": int(user_id)},
        ).mappings().first()

        type_rows = conn.execute(
            text(
                """
                SELECT job_type, COUNT(*) AS cnt
                FROM antifake_jobs
                WHERE user_id = :user_id AND status = 'completed'
                GROUP BY job_type
                """
            ),
            {"user_id": int(user_id)},
        ).mappings().all()

    by_type = {"text": 0, "audio": 0, "video": 0, "call": 0, "document": 0}
    for item in type_rows:
        key = str(item["job_type"] or "")
        if key in by_type:
            by_type[key] = int(item["cnt"] or 0)

    return {
        "checks_total": int(row["checks_total"] or 0),
        "fake_detected": int(row["fake_detected"] or 0),
        "by_type": by_type,
        "latency_p95_ms": int(row["avg_latency_ms"] or 0),
    }
