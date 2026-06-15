"""RQ worker tasks — heavy antifake media analysis off the API thread (af-3)."""
from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any, Dict, Optional

from app.services.antifake_jobs_store import complete_job, fail_job, mark_job_processing
from app.services.antifake_service import check_media
from app.services.antifake_upload_store import delete_upload, read_upload

logger = logging.getLogger(__name__)

FORBIDDEN_SOURCES = frozenset({"sfm_mock", "mock", "sfm_stub", "sfm_fallback"})


def _validate_verdict(payload: Dict[str, Any]) -> Dict[str, Any]:
    verdict = payload.get("verdict")
    if verdict not in ("likely_fake", "uncertain", "likely_real"):
        raise ValueError("invalid_verdict_contract")
    source = str(payload.get("source", ""))
    if source in FORBIDDEN_SOURCES:
        raise ValueError("mock_source_rejected")
    return payload


def process_media_job(
    job_id: str,
    job_type: str,
    file_path: str,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Entry point for RQ worker — reads upload, runs SFM/rule_engine, updates DB."""
    extra = extra or {}
    mark_job_processing(job_id)
    started = time.perf_counter()
    path = Path(file_path)

    try:
        raw = read_upload(path)
        if not raw:
            raise ValueError("empty_upload")

        verdict = _validate_verdict(
            check_media(
                media_type=job_type,
                file_name=path.name,
                file_bytes=raw,
                extra=extra,
            )
        )
        verdict["job_id"] = job_id
        latency_ms = int((time.perf_counter() - started) * 1000)
        complete_job(job_id, verdict, latency_ms)
        logger.info(
            "antifake_worker job=%s type=%s verdict=%s latency_ms=%s",
            job_id,
            job_type,
            verdict.get("verdict"),
            latency_ms,
        )
        if job_type == "call":
            from app.services.antifake_fraud_ingest import maybe_ingest_from_call_verdict

            maybe_ingest_from_call_verdict(
                verdict,
                caller_id=(extra or {}).get("caller_id"),
                display_name=(extra or {}).get("display_name"),
            )
        return verdict
    except Exception as exc:
        fail_job(job_id, str(exc))
        logger.exception("antifake_worker failed job=%s type=%s", job_id, job_type)
        raise
    finally:
        delete_upload(path)
