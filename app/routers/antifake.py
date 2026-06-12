"""
Antifake API — explicit routers (B1-01 / af-2-*). No wildcard. No mock.
"""
from __future__ import annotations

import logging
import time
from typing import Annotated, Any, Dict, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from pydantic import BaseModel, Field
from app.auth.auth import get_current_user
from app.services.antifake_jobs_store import (
    complete_job,
    create_job,
    fail_job,
    get_job,
    metrics_for_user,
)
from app.services.antifake_premium import user_has_antifake_access
from app.services.antifake_queue import enqueue_media_job
from app.services.antifake_rate_limit import check_rate_limit
from app.services.antifake_service import check_media, check_text, check_url
from app.services.antifake_upload_store import save_upload

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/antifake", tags=["antifake"])

MAX_MEDIA_BYTES = 25 * 1024 * 1024
TEXT_URL_LIMIT_PER_MIN = 60
MEDIA_LIMIT_PER_HOUR = 10


class CheckTextRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=8000)
    mode: Optional[str] = Field(default="news")


class CheckUrlRequest(BaseModel):
    url: str = Field(..., min_length=4, max_length=2048)


def _require_premium(user: Dict[str, Any], request: Request) -> None:
    smoke_secret = request.headers.get("X-Aladdin-Smoke")
    if not user_has_antifake_access(user, smoke_secret=smoke_secret):
        raise HTTPException(
            status_code=403,
            detail={
                "error": "premium_required",
                "message": "Antifake checks require Premium subscription",
                "premium_required": True,
            },
        )


def _validate_verdict(payload: Dict[str, Any]) -> Dict[str, Any]:
    verdict = payload.get("verdict")
    if verdict not in ("likely_fake", "uncertain", "likely_real"):
        raise HTTPException(status_code=503, detail="invalid_verdict_contract")
    source = str(payload.get("source", ""))
    if source in ("sfm_mock", "mock", "sfm_stub", "sfm_fallback"):
        raise HTTPException(status_code=503, detail="mock_source_rejected")
    return payload


@router.post("/check/text")
async def antifake_check_text(
    request: Request,
    body: CheckTextRequest,
    current_user: dict = Depends(get_current_user),
):
    _require_premium(current_user, request)
    check_rate_limit(
        user_id=int(current_user["id"]),
        bucket="text_url",
        limit=TEXT_URL_LIMIT_PER_MIN,
        window_sec=60,
    )
    result = _validate_verdict(check_text(body.text, body.mode or "news"))
    logger.info(
        "antifake_check_text user=%s verdict=%s source=%s",
        current_user.get("id"),
        result.get("verdict"),
        result.get("source"),
    )
    return result


@router.post("/check/url")
async def antifake_check_url(
    request: Request,
    body: CheckUrlRequest,
    current_user: dict = Depends(get_current_user),
):
    _require_premium(current_user, request)
    check_rate_limit(
        user_id=int(current_user["id"]),
        bucket="text_url",
        limit=TEXT_URL_LIMIT_PER_MIN,
        window_sec=60,
    )
    result = _validate_verdict(check_url(body.url))
    logger.info(
        "antifake_check_url user=%s verdict=%s",
        current_user.get("id"),
        result.get("verdict"),
    )
    return result


async def _enqueue_media_job(
    *,
    user: Dict[str, Any],
    request: Request,
    job_type: str,
    upload: UploadFile,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    _require_premium(user, request)
    check_rate_limit(
        user_id=int(user["id"]),
        bucket="media",
        limit=MEDIA_LIMIT_PER_HOUR,
        window_sec=3600,
    )
    raw = await upload.read()
    if len(raw) > MAX_MEDIA_BYTES:
        raise HTTPException(status_code=413, detail="file_too_large")

    user_id = int(user["id"])
    job_id = create_job(user_id, job_type)
    file_name = upload.filename or "upload"

    file_path = save_upload(
        user_id=user_id,
        job_id=job_id,
        file_bytes=raw,
        file_name=file_name,
    )

    if enqueue_media_job(
        job_id=job_id,
        job_type=job_type,
        file_path=str(file_path),
        extra=extra,
    ):
        logger.info("antifake_media_queued job=%s type=%s user=%s", job_id, job_type, user_id)
        return {"job_id": job_id, "status": "queued", "type": job_type}

    started = time.perf_counter()
    try:
        verdict = _validate_verdict(
            check_media(
                media_type=job_type,
                file_name=file_name,
                file_bytes=raw,
                extra=extra,
            )
        )
        verdict["job_id"] = job_id
        latency_ms = int((time.perf_counter() - started) * 1000)
        complete_job(job_id, verdict, latency_ms)
        return {"job_id": job_id, "status": "completed", **verdict}
    except HTTPException:
        fail_job(job_id, "analysis_failed")
        raise
    except Exception as exc:
        fail_job(job_id, str(exc))
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    finally:
        from app.services.antifake_upload_store import delete_upload

        delete_upload(file_path)


@router.post("/check/audio", status_code=202, response_model=None, include_in_schema=False)
async def antifake_check_audio(
    request: Request,
    file: Annotated[UploadFile, File(...)],
    current_user: dict = Depends(get_current_user),
):
    return await _enqueue_media_job(user=current_user, request=request, job_type="audio", upload=file)


@router.post("/check/video", status_code=202, response_model=None, include_in_schema=False)
async def antifake_check_video(
    request: Request,
    file: Annotated[UploadFile, File(...)],
    current_user: dict = Depends(get_current_user),
):
    return await _enqueue_media_job(user=current_user, request=request, job_type="video", upload=file)


@router.post("/check/document", status_code=202, response_model=None, include_in_schema=False)
async def antifake_check_document(
    request: Request,
    file: Annotated[UploadFile, File(...)],
    current_user: dict = Depends(get_current_user),
):
    return await _enqueue_media_job(user=current_user, request=request, job_type="document", upload=file)


@router.post("/call/analyze", status_code=202, response_model=None, include_in_schema=False)
async def antifake_call_analyze(
    request: Request,
    file: Annotated[UploadFile, File(...)],
    caller_id: Optional[str] = Form(default=None),
    display_name: Optional[str] = Form(default=None),
    current_user: dict = Depends(get_current_user),
):
    extra = {}
    if caller_id:
        extra["caller_id"] = caller_id
    if display_name:
        extra["display_name"] = display_name
    return await _enqueue_media_job(
        user=current_user,
        request=request,
        job_type="call",
        upload=file,
        extra=extra,
    )


@router.get("/jobs/{job_id}")
async def antifake_get_job(
    job_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    _require_premium(current_user, request)
    row = get_job(job_id, int(current_user["id"]))
    if not row:
        raise HTTPException(status_code=404, detail="job_not_found")

    if row["status"] == "completed" and isinstance(row.get("verdict"), dict):
        payload = dict(row["verdict"])
        payload["job_id"] = job_id
        payload["status"] = "completed"
        return _validate_verdict(payload)

    return {
        "job_id": job_id,
        "status": row["status"],
        "type": row["type"],
    }


@router.get("/metrics")
async def antifake_metrics(
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    _require_premium(current_user, request)
    return metrics_for_user(int(current_user["id"]))
