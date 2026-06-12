"""Redis/RQ enqueue for antifake media jobs with sync fallback (af-3-01)."""
from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

REDIS_URL = os.environ.get(
    "ANTIFAKE_REDIS_URL",
    os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/0"),
)
QUEUE_NAME = os.environ.get("ANTIFAKE_QUEUE_NAME", "aladdin-antifake")
ASYNC_MODE = os.environ.get("ANTIFAKE_ASYNC_MEDIA", "auto").strip().lower()


def queue_enabled() -> bool:
    if ASYNC_MODE in ("0", "false", "no", "off"):
        return False
    if ASYNC_MODE in ("1", "true", "yes", "on"):
        return True
    try:
        import redis

        client = redis.from_url(REDIS_URL)
        client.ping()
        return True
    except Exception as exc:
        logger.debug("antifake queue disabled (redis unavailable): %s", exc)
        return False


def enqueue_media_job(
    *,
    job_id: str,
    job_type: str,
    file_path: str,
    extra: Optional[Dict[str, Any]] = None,
) -> bool:
    if not queue_enabled():
        return False

    try:
        import redis
        from rq import Queue

        connection = redis.from_url(REDIS_URL)
        queue = Queue(QUEUE_NAME, connection=connection)
        queue.enqueue(
            "app.services.antifake_worker_tasks.process_media_job",
            job_id,
            job_type,
            file_path,
            extra or {},
            job_timeout=int(os.environ.get("ANTIFAKE_JOB_TIMEOUT_SEC", "300")),
            failure_ttl=int(os.environ.get("ANTIFAKE_JOB_FAILURE_TTL_SEC", "3600")),
            result_ttl=int(os.environ.get("ANTIFAKE_JOB_RESULT_TTL_SEC", "600")),
            job_id=job_id,
        )
        logger.info("antifake enqueued job=%s type=%s queue=%s", job_id, job_type, QUEUE_NAME)
        return True
    except Exception as exc:
        logger.warning("antifake enqueue failed job=%s: %s", job_id, exc)
        return False
