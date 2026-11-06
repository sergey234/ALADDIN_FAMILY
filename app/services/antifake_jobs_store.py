"""Antifake async jobs persistence (af-3-02 lite for B1)."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy import text

from app.database.database import engine
from app.services.antifake_job_staleness import stale_failure_reason

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
    try:
        from app.services.antifake_family_notify import maybe_notify_parents_likely_fake

        maybe_notify_parents_likely_fake(job_id=job_id, verdict=verdict)
    except Exception:
        pass


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


def _fail_if_stale(job: Dict[str, Any], row: Any) -> Dict[str, Any]:
    status = str(row["status"] or "")
    stamp = row["updated_at"] if status == "processing" else row["created_at"]
    if not stamp:
        return job
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=timezone.utc)
    age = (datetime.now(timezone.utc) - stamp).total_seconds()
    reason = stale_failure_reason(status, str(row["job_type"] or ""), age)
    if not reason:
        return job
    fail_job(job["job_id"], reason)
    job["status"] = "failed"
    job["verdict"] = {"error": reason}
    return job


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

    job = {
        "job_id": str(row["id"]),
        "type": row["job_type"],
        "status": row["status"],
        "verdict": verdict,
        "latency_ms": row["latency_ms"],
        "created_at": row["created_at"].isoformat() if row["created_at"] else None,
        "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
    }
    return _fail_if_stale(job, row)


def get_job_user_id(job_id: str) -> Optional[int]:
    ensure_table()
    with engine.connect() as conn:
        row = conn.execute(
            text(
                """
                SELECT user_id FROM antifake_jobs
                WHERE id = CAST(:id AS UUID)
                """
            ),
            {"id": job_id},
        ).mappings().first()
    if not row:
        return None
    return int(row["user_id"])


def _funnel_metrics_for_user(user_id: int) -> Dict[str, Any]:
    """M-02: enable → sync → check funnel (no PII)."""
    checks_total = 0
    cd_enabled = False
    cd_synced_count = 0
    ensure_table()
    try:
        with engine.connect() as conn:
            checks_total = int(
                conn.execute(
                    text(
                        """
                        SELECT COUNT(*) FROM antifake_jobs
                        WHERE user_id = :user_id AND status = 'completed'
                        """
                    ),
                    {"user_id": int(user_id)},
                ).scalar()
                or 0
            )
            try:
                cd_row = conn.execute(
                    text(
                        """
                        SELECT extension_enabled, synced_count
                        FROM antifake_family_cd_status
                        WHERE user_id = :user_id
                        ORDER BY updated_at DESC
                        LIMIT 1
                        """
                    ),
                    {"user_id": int(user_id)},
                ).mappings().first()
                if cd_row:
                    cd_enabled = bool(cd_row["extension_enabled"])
                    cd_synced_count = int(cd_row["synced_count"] or 0)
            except Exception:
                pass
    except Exception:
        checks_total = 0

    return {
        "cd_extension_enabled": cd_enabled,
        "cd_synced_count": cd_synced_count,
        "checks_completed": checks_total,
        "funnel_ready": cd_enabled and cd_synced_count > 0 and checks_total > 0,
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
                    COALESCE(AVG(latency_ms), 0) AS avg_latency_ms,
                    COALESCE(
                        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms),
                        0
                    ) AS p95_latency_ms
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

    from app.services.antifake_service import MODEL_VERSION, SLA_MS

    stub_rate = _stub_rate_for_user(user_id)
    verdict_dist = _verdict_distribution_for_user(user_id)
    latency_by_type = _latency_by_type_for_user(user_id)

    return {
        "checks_total": int(row["checks_total"] or 0),
        "fake_detected": int(row["fake_detected"] or 0),
        "by_type": by_type,
        "latency_p95_ms": int(row["p95_latency_ms"] or row["avg_latency_ms"] or 0),
        "avg_latency_ms": int(row["avg_latency_ms"] or 0),
        "latency_by_type_ms": latency_by_type,
        "verdict_distribution": verdict_dist,
        "stub_rate": stub_rate,
        "model_version": MODEL_VERSION,
        "funnel": _funnel_metrics_for_user(user_id),
        "sla_ms": dict(SLA_MS),
    }


def _stub_rate_for_user(user_id: int) -> float:
    """RH-H04: share of completed jobs that look like SFM stub masquerade."""
    try:
        with engine.connect() as conn:
            row = conn.execute(
                text(
                    """
                    SELECT
                        COUNT(*) AS total,
                        COUNT(*) FILTER (
                            WHERE verdict->>'source' IN ('sfm_mock', 'mock', 'sfm_stub')
                               OR lower(coalesce(verdict->>'agent', '')) LIKE '%stub%'
                               OR (
                                    jsonb_typeof(verdict->'reasons') = 'array'
                                    AND jsonb_array_length(verdict->'reasons') = 1
                                    AND verdict->'reasons'->>0 = 'sfm_agent'
                               )
                        ) AS stubs
                    FROM antifake_jobs
                    WHERE user_id = :user_id AND status = 'completed'
                    """
                ),
                {"user_id": int(user_id)},
            ).mappings().first()
        total = int((row or {}).get("total") or 0)
        stubs = int((row or {}).get("stubs") or 0)
        if total <= 0:
            return 0.0
        return round(stubs / total, 4)
    except Exception:
        return 0.0


def _verdict_distribution_for_user(user_id: int) -> Dict[str, int]:
    dist = {
        "likely_fake": 0,
        "uncertain": 0,
        "likely_real": 0,
        "insufficient_data": 0,
    }
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text(
                    """
                    SELECT verdict->>'verdict' AS v, COUNT(*) AS cnt
                    FROM antifake_jobs
                    WHERE user_id = :user_id AND status = 'completed'
                    GROUP BY verdict->>'verdict'
                    """
                ),
                {"user_id": int(user_id)},
            ).mappings().all()
        for item in rows:
            key = str(item.get("v") or "")
            if key in dist:
                dist[key] = int(item.get("cnt") or 0)
    except Exception:
        pass
    return dist


def _latency_by_type_for_user(user_id: int) -> Dict[str, int]:
    out = {"text": 0, "audio": 0, "video": 0, "call": 0, "document": 0}
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text(
                    """
                    SELECT job_type,
                           COALESCE(AVG(latency_ms), 0) AS avg_ms
                    FROM antifake_jobs
                    WHERE user_id = :user_id AND status = 'completed'
                    GROUP BY job_type
                    """
                ),
                {"user_id": int(user_id)},
            ).mappings().all()
        for item in rows:
            key = str(item.get("job_type") or "")
            if key in out:
                out[key] = int(item.get("avg_ms") or 0)
    except Exception:
        pass
    return out
