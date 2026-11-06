"""Antifake media pipeline health — "do checks actually complete?", not "is the process up?".

Incident 2026-11-06: /api/health was ok for 21 days while every media job crashed in the worker.
Consumers: GET /api/antifake/pipeline-health (external watchdog on Brain) and
scripts/antifake_ops_alerts.py (local cron). Output is coarse on purpose: no ids, no PII.
"""
from __future__ import annotations

import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

CRASH_WINDOW_MIN = int(os.environ.get("ANTIFAKE_HEALTH_CRASH_WINDOW_MIN", "60"))
CRASH_MIN_FAILED = int(os.environ.get("ANTIFAKE_HEALTH_CRASH_MIN_FAILED", "3"))
# Only recently created stuck jobs mean "worker is not picking up now"; older ones are history.
STUCK_LOOKBACK_MIN = int(os.environ.get("ANTIFAKE_HEALTH_STUCK_LOOKBACK_MIN", "15"))
SMOKE_MAX_AGE_H = float(os.environ.get("ANTIFAKE_HEALTH_SMOKE_MAX_AGE_H", "26"))
SMOKE_TIMESTAMP_FILE = Path(
    os.environ.get(
        "ANTIFAKE_SMOKE_TIMESTAMP_FILE",
        "/var/lib/aladdin/antifake_smoke_last_success.timestamp",
    )
)
CACHE_TTL_SEC = 30

_cache: Dict[str, Any] = {"at": 0.0, "value": None}


def evaluate(
    *,
    queue_enabled: bool,
    workers: Optional[int],
    failed: int,
    completed: int,
    stale_queued: int,
    smoke_age_h: Optional[float],
) -> Dict[str, Any]:
    """Pure decision so the thresholds are unit-testable without DB/redis."""
    problems: List[str] = []
    if queue_enabled and (workers is None or workers < 1):
        problems.append("worker_not_registered")
    if failed >= CRASH_MIN_FAILED and completed == 0:
        problems.append("all_media_jobs_failing")
    if stale_queued > 0:
        problems.append("jobs_stuck_in_queue")
    if smoke_age_h is None or smoke_age_h > SMOKE_MAX_AGE_H:
        problems.append("smoke_stale")
    return {"status": "ok" if not problems else "degraded", "problems": problems}


def _job_counts() -> Dict[str, int]:
    from sqlalchemy import text

    from app.database.database import engine
    from app.services.antifake_job_staleness import QUEUED_STALE_SEC
    from app.services.antifake_jobs_store import ensure_table

    ensure_table()
    now = datetime.now(timezone.utc)
    with engine.connect() as conn:
        row = conn.execute(
            text(
                """
                SELECT
                    COUNT(*) FILTER (WHERE status = 'failed') AS failed,
                    COUNT(*) FILTER (WHERE status = 'completed') AS completed
                FROM antifake_jobs
                WHERE updated_at >= :since AND job_type <> 'text' AND job_type <> 'url'
                """
            ),
            {"since": now - timedelta(minutes=CRASH_WINDOW_MIN)},
        ).mappings().first()
        stale = conn.execute(
            text(
                """
                SELECT COUNT(*) FROM antifake_jobs
                WHERE status = 'queued' AND created_at < :cutoff AND created_at >= :floor
                """
            ),
            {
                "cutoff": now - timedelta(seconds=QUEUED_STALE_SEC),
                "floor": now - timedelta(minutes=STUCK_LOOKBACK_MIN),
            },
        ).scalar()
    return {
        "failed": int((row or {}).get("failed") or 0),
        "completed": int((row or {}).get("completed") or 0),
        "stale_queued": int(stale or 0),
    }


def _worker_count() -> Dict[str, Any]:
    from app.services.antifake_queue import QUEUE_NAME, REDIS_URL, queue_enabled

    if not queue_enabled():
        return {"enabled": False, "workers": None}
    import redis
    from rq import Queue, Worker

    connection = redis.from_url(REDIS_URL)
    queue = Queue(QUEUE_NAME, connection=connection)
    return {"enabled": True, "workers": len(Worker.all(queue=queue))}


def _smoke_age_hours() -> Optional[float]:
    if not SMOKE_TIMESTAMP_FILE.is_file():
        return None
    raw = SMOKE_TIMESTAMP_FILE.read_text(encoding="utf-8").strip()
    try:
        ts = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return round((datetime.now(timezone.utc) - ts).total_seconds() / 3600.0, 2)


def collect(use_cache: bool = True) -> Dict[str, Any]:
    if use_cache and _cache["value"] is not None and time.monotonic() - _cache["at"] < CACHE_TTL_SEC:
        return _cache["value"]
    try:
        workers = _worker_count()
        counts = _job_counts()
        smoke_age = _smoke_age_hours()
        result = evaluate(
            queue_enabled=bool(workers["enabled"]),
            workers=workers["workers"],
            failed=counts["failed"],
            completed=counts["completed"],
            stale_queued=counts["stale_queued"],
            smoke_age_h=smoke_age,
        )
        result["detail"] = {
            "workers": workers["workers"],
            "media_failed_window": counts["failed"],
            "media_completed_window": counts["completed"],
            "stale_queued": counts["stale_queued"],
            "smoke_age_h": smoke_age,
            "window_min": CRASH_WINDOW_MIN,
        }
    except Exception as exc:
        result = {"status": "degraded", "problems": ["health_probe_error"], "detail": {"error": type(exc).__name__}}
    _cache.update(at=time.monotonic(), value=result)
    return result
