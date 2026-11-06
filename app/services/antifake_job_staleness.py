"""When an antifake job the worker never finished must be reported as failed (stdlib only)."""
from __future__ import annotations

import os
from typing import Optional

QUEUED_STALE_SEC = int(os.environ.get("ANTIFAKE_JOB_QUEUED_STALE_SEC", "90"))
PROCESSING_GRACE_SEC = int(os.environ.get("ANTIFAKE_JOB_PROCESSING_GRACE_SEC", "60"))
_FALLBACK_SLA_SEC = {"text": 8, "url": 8, "audio": 120, "video": 300, "document": 120, "call": 180}


def sla_seconds(job_type: str) -> int:
    try:
        from app.services.antifake_service import SLA_MS

        if job_type in SLA_MS:
            return max(1, int(SLA_MS[job_type]) // 1000)
    except Exception:
        pass
    return _FALLBACK_SLA_SEC.get(job_type, 300)


def stale_failure_reason(status: str, job_type: str, age_seconds: float) -> Optional[str]:
    if status == "queued" and age_seconds > QUEUED_STALE_SEC:
        return "worker_unavailable"
    if status == "processing" and age_seconds > sla_seconds(job_type) + PROCESSING_GRACE_SEC:
        return "worker_timeout"
    return None
