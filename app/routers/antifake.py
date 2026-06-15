"""
Antifake API — explicit routers (B1-01 / af-2-*). No wildcard. No mock.
"""
from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Annotated, Any, Dict, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile
from pydantic import BaseModel, Field
from app.auth.auth import get_current_user
from app.services.antifake_call_directory_store import get_call_directory_payload
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
from app.services.antifake_security import (
    AntifakeSecurityError,
    redact_phone_for_log,
    redact_text_for_log,
    redact_url_for_log,
    validate_media_upload,
)
from app.services.antifake_upload_store import save_upload

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/antifake", tags=["antifake"])

MAX_MEDIA_BYTES = 25 * 1024 * 1024
TEXT_URL_LIMIT_PER_MIN = 60
MEDIA_LIMIT_PER_HOUR = 10
REPORTS_LIMIT_PER_HOUR = 5


class CheckTextRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=8000)
    mode: Optional[str] = Field(default="news")


class CheckUrlRequest(BaseModel):
    url: str = Field(..., min_length=4, max_length=2048)


class ReportScamRequest(BaseModel):
    job_id: str = Field(..., min_length=8, max_length=64)
    phone: str = Field(..., min_length=10, max_length=20)
    label: Optional[str] = Field(default=None, max_length=128)
    note: Optional[str] = Field(default=None, max_length=2000)


class AppealScamRequest(BaseModel):
    job_id: str = Field(..., min_length=8, max_length=64)
    phone: str = Field(..., min_length=10, max_length=20)
    note: Optional[str] = Field(default=None, max_length=2000)


class WhitelistMutateRequest(BaseModel):
    phones: list[str] = Field(..., min_length=1, max_length=20)


class ModerateReportRequest(BaseModel):
    action: str = Field(..., pattern="^(approve|reject)$")


class FamilyPushTokenRequest(BaseModel):
    token: str = Field(..., min_length=32, max_length=128)
    platform: str = Field(default="ios", max_length=16)


class FamilyCDStatusRequest(BaseModel):
    extension_enabled: bool = Field(default=False)
    synced_count: int = Field(default=0, ge=0, le=500_000)


class MediaJobQueuedResponse(BaseModel):
    """B-03: OpenAPI contract for async media uploads."""

    job_id: str
    status: str = Field(..., description="queued | completed")
    type: str = Field(..., description="audio | video | document | call")


class MediaJobCompletedResponse(BaseModel):
    job_id: str
    status: str = "completed"
    type: Optional[str] = None
    verdict: str
    confidence: Optional[float] = None
    source: Optional[str] = None


_MEDIA_UPLOAD_OPENAPI: dict[int | str, dict] = {
    202: {
        "description": "Job queued — poll GET /api/antifake/jobs/{job_id}",
        "content": {
            "application/json": {
                "example": {"job_id": "uuid", "status": "queued", "type": "audio"}
            }
        },
    },
    200: {
        "description": "Sync completion when worker queue unavailable",
        "content": {
            "application/json": {
                "example": {
                    "job_id": "uuid",
                    "status": "completed",
                    "verdict": "uncertain",
                    "confidence": 0.5,
                    "source": "probe",
                }
            }
        },
    },
    400: {"description": "Invalid upload (bad mime/extension)"},
    403: {"description": "Premium required"},
    413: {"description": "file_too_large (>25MB)"},
    429: {"description": "rate_limit — too many media uploads"},
    503: {"description": "Analysis unavailable / mock rejected"},
}


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


def _sync_check_with_job(
    *,
    user_id: int,
    job_type: str,
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    """I-08: every completed check gets a persisted job_id."""
    job_id = create_job(user_id, job_type)
    started = time.perf_counter()
    result = _validate_verdict(payload)
    result["job_id"] = job_id
    latency_ms = int((time.perf_counter() - started) * 1000)
    complete_job(job_id, result, latency_ms)
    return result


def _require_completed_job(job_id: str, user_id: int) -> Dict[str, Any]:
    row = get_job(job_id, user_id)
    if not row:
        raise HTTPException(status_code=404, detail="job_not_found")
    if row["status"] != "completed":
        raise HTTPException(status_code=400, detail="job_not_completed")
    return row


def _job_verdict_fields(row: Dict[str, Any]) -> tuple[Optional[str], int]:
    verdict_payload = row.get("verdict")
    if not isinstance(verdict_payload, dict):
        return None, 0
    verdict = str(verdict_payload.get("verdict") or "")
    raw_conf = verdict_payload.get("confidence")
    if raw_conf is None:
        return verdict or None, 0
    conf_f = float(raw_conf)
    if conf_f <= 1.0:
        return verdict or None, int(min(99, round(conf_f * 100)))
    return verdict or None, int(min(99, round(conf_f)))


def _require_internal_smoke(request: Request) -> None:
    import os

    expected = os.environ.get("ANTIFAKE_INTERNAL_SMOKE_SECRET")
    provided = request.headers.get("X-Aladdin-Smoke")
    if not expected or not provided or provided != expected:
        raise HTTPException(status_code=403, detail="forbidden")


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
    result = _sync_check_with_job(
        user_id=int(current_user["id"]),
        job_type="text",
        payload=check_text(body.text, body.mode or "news"),
    )
    logger.info(
        "antifake_check_text user=%s verdict=%s source=%s job=%s text=%s",
        current_user.get("id"),
        result.get("verdict"),
        result.get("source"),
        result.get("job_id"),
        redact_text_for_log(body.text),
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
    result = _sync_check_with_job(
        user_id=int(current_user["id"]),
        job_type="url",
        payload=check_url(body.url),
    )
    logger.info(
        "antifake_check_url user=%s verdict=%s job=%s url=%s",
        current_user.get("id"),
        result.get("verdict"),
        result.get("job_id"),
        redact_url_for_log(body.url),
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
    try:
        validate_media_upload(
            job_type=job_type,
            file_name=upload.filename or "upload",
            file_bytes=raw,
            content_type=upload.content_type,
        )
    except AntifakeSecurityError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
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
        if job_type == "call":
            from app.services.antifake_fraud_ingest import maybe_ingest_from_call_verdict

            maybe_ingest_from_call_verdict(
                verdict,
                caller_id=(extra or {}).get("caller_id"),
                display_name=(extra or {}).get("display_name"),
                user_id=user_id,
            )
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


@router.post(
    "/check/audio",
    status_code=202,
    response_model=None,
    summary="Upload audio for antifake analysis",
    description="Multipart file upload (max 25MB). Returns job_id; poll GET /jobs/{job_id}.",
    responses=_MEDIA_UPLOAD_OPENAPI,
)
async def antifake_check_audio(
    request: Request,
    file: Annotated[UploadFile, File(...)],
    current_user: dict = Depends(get_current_user),
):
    return await _enqueue_media_job(user=current_user, request=request, job_type="audio", upload=file)


@router.post(
    "/check/video",
    status_code=202,
    response_model=None,
    summary="Upload video for antifake / deepfake probe",
    description="Multipart file upload (max 25MB). Probe hint only — see F-02 DoD.",
    responses=_MEDIA_UPLOAD_OPENAPI,
)
async def antifake_check_video(
    request: Request,
    file: Annotated[UploadFile, File(...)],
    current_user: dict = Depends(get_current_user),
):
    return await _enqueue_media_job(user=current_user, request=request, job_type="video", upload=file)


@router.post(
    "/check/document",
    status_code=202,
    response_model=None,
    summary="Upload document for antifake analysis",
    responses=_MEDIA_UPLOAD_OPENAPI,
)
async def antifake_check_document(
    request: Request,
    file: Annotated[UploadFile, File(...)],
    current_user: dict = Depends(get_current_user),
):
    return await _enqueue_media_job(user=current_user, request=request, job_type="document", upload=file)


@router.post(
    "/call/analyze",
    status_code=202,
    response_model=None,
    summary="Analyze call recording with optional caller metadata",
    description="Multipart audio + optional caller_id/display_name for spoof heuristics.",
    responses=_MEDIA_UPLOAD_OPENAPI,
)
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


def _parse_since_param(raw: Optional[str]) -> Optional[datetime]:
    if not raw:
        return None
    try:
        normalized = raw.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid since timestamp") from exc


@router.get("/call-directory")
async def antifake_call_directory(
    request: Request,
    since: Optional[str] = Query(None, description="ISO8601 — delta sync (C-09)"),
    current_user: dict = Depends(get_current_user),
):
    """Numbers for iOS Call Directory extension (C-03 / af-4-09)."""
    _require_premium(current_user, request)
    return get_call_directory_payload(since=_parse_since_param(since))


@router.post("/report")
async def antifake_report_scam_number(
    request: Request,
    body: ReportScamRequest,
    current_user: dict = Depends(get_current_user),
):
    """I-02 / I-08: scam report after completed check → moderation queue."""
    _require_premium(current_user, request)
    user_id = int(current_user["id"])
    check_rate_limit(
        user_id=user_id,
        bucket="reports",
        limit=REPORTS_LIMIT_PER_HOUR,
        window_sec=3600,
    )

    from app.services.antifake_reports_store import create_report
    from app.services.antifake_whitelist_store import is_whitelisted

    row = _require_completed_job(body.job_id, user_id)
    job_verdict, job_confidence = _job_verdict_fields(row)
    if job_verdict == "likely_real":
        raise HTTPException(status_code=400, detail="cannot_report_likely_real")

    if is_whitelisted(user_id, body.phone):
        raise HTTPException(
            status_code=400,
            detail={"error": "whitelisted", "message": "Number is in your trusted contacts"},
        )

    try:
        report = create_report(
            user_id=user_id,
            phone=body.phone,
            job_id=body.job_id,
            label=body.label,
            note=body.note,
            report_type="scam",
            job_verdict=job_verdict,
            job_confidence=job_confidence,
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="invalid_phone") from None

    return {
        "id": report["id"],
        "status": report["status"],
        "message": "Report submitted for moderation",
    }


@router.post("/appeal")
async def antifake_appeal_scam_number(
    request: Request,
    body: AppealScamRequest,
    current_user: dict = Depends(get_current_user),
):
    """I-06: appeal «не мошенник» after completed check."""
    _require_premium(current_user, request)
    user_id = int(current_user["id"])
    check_rate_limit(
        user_id=user_id,
        bucket="reports",
        limit=REPORTS_LIMIT_PER_HOUR,
        window_sec=3600,
    )

    from app.services.antifake_reports_store import create_report

    row = _require_completed_job(body.job_id, user_id)
    job_verdict, job_confidence = _job_verdict_fields(row)

    try:
        report = create_report(
            user_id=user_id,
            phone=body.phone,
            job_id=body.job_id,
            label=None,
            note=body.note,
            report_type="appeal",
            job_verdict=job_verdict,
            job_confidence=job_confidence,
            auto_moderate=False,
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="invalid_phone") from None

    return {
        "id": report["id"],
        "status": report["status"],
        "message": "Appeal submitted for review",
    }


@router.get("/whitelist")
async def antifake_list_whitelist(
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    """I-05: list trusted numbers for this user."""
    _require_premium(current_user, request)
    from app.services.antifake_whitelist_store import list_phones

    return {"phones": list_phones(int(current_user["id"]))}


@router.post("/whitelist")
async def antifake_add_whitelist(
    request: Request,
    body: WhitelistMutateRequest,
    current_user: dict = Depends(get_current_user),
):
    """I-05: add trusted numbers."""
    _require_premium(current_user, request)
    from app.services.antifake_whitelist_store import add_phones

    added = add_phones(int(current_user["id"]), body.phones)
    return {"added": added}


@router.delete("/whitelist")
async def antifake_remove_whitelist(
    request: Request,
    body: WhitelistMutateRequest,
    current_user: dict = Depends(get_current_user),
):
    """I-05: remove trusted numbers."""
    _require_premium(current_user, request)
    from app.services.antifake_whitelist_store import remove_phone

    removed = sum(
        1 for phone in body.phones if remove_phone(int(current_user["id"]), phone)
    )
    return {"removed": removed}


@router.get("/reports/pending")
async def antifake_reports_pending(
    request: Request,
    limit: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(get_current_user),
):
    """I-02: moderation queue (internal smoke only)."""
    _require_premium(current_user, request)
    _require_internal_smoke(request)
    from app.services.antifake_reports_store import list_pending

    return {"reports": list_pending(limit=limit)}


@router.post("/reports/{report_id}/moderate")
async def antifake_moderate_report(
    report_id: str,
    request: Request,
    body: ModerateReportRequest,
    current_user: dict = Depends(get_current_user),
):
    """I-02 / I-03: approve or reject pending report."""
    _require_premium(current_user, request)
    _require_internal_smoke(request)
    from app.services.antifake_reports_store import get_report, moderate_report

    row = get_report(report_id)
    if not row:
        raise HTTPException(status_code=404, detail="report_not_found")
    updated = moderate_report(report_id, action=body.action, moderator="ops")
    return updated


@router.post("/family/push-token")
async def antifake_register_family_push_token(
    request: Request,
    body: FamilyPushTokenRequest,
    current_user: dict = Depends(get_current_user),
):
    """L-01: register APNs token for parent antifake alerts."""
    _require_premium(current_user, request)
    from app.services.antifake_family_store import register_push_token

    register_push_token(int(current_user["id"]), body.token, body.platform)
    return {"registered": True}


@router.get("/family/reports")
async def antifake_family_shared_reports(
    request: Request,
    limit: int = Query(30, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    """L-03: approved scam reports shared within family."""
    _require_premium(current_user, request)
    from app.services.antifake_family_store import (
        is_family_member,
        list_family_shared_reports,
        resolve_primary_family_id,
    )

    user_id = int(current_user["id"])
    family_id = resolve_primary_family_id(user_id)
    if not family_id or not is_family_member(user_id, family_id):
        return {"family_id": None, "reports": []}
    return {
        "family_id": family_id,
        "reports": list_family_shared_reports(family_id, limit=limit),
    }


@router.post("/family/cd-status")
async def antifake_report_cd_status(
    request: Request,
    body: FamilyCDStatusRequest,
    current_user: dict = Depends(get_current_user),
):
    """L-05: member reports Call Directory sync status for parent dashboard."""
    _require_premium(current_user, request)
    from app.services.antifake_family_store import resolve_primary_family_id, upsert_cd_status

    user_id = int(current_user["id"])
    family_id = resolve_primary_family_id(user_id)
    if not family_id:
        raise HTTPException(status_code=400, detail="no_family")
    upsert_cd_status(
        user_id=user_id,
        family_id=family_id,
        extension_enabled=body.extension_enabled,
        synced_count=body.synced_count,
    )
    return {"saved": True}


@router.get("/family/cd-status")
async def antifake_family_cd_status(
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    """L-05: parents see Call Directory status of family members."""
    _require_premium(current_user, request)
    from app.services.antifake_family_store import (
        get_member_role,
        is_family_member,
        list_family_cd_status,
        resolve_primary_family_id,
    )

    user_id = int(current_user["id"])
    family_id = resolve_primary_family_id(user_id)
    if not family_id or not is_family_member(user_id, family_id):
        return {"family_id": None, "members": []}

    role = get_member_role(user_id, family_id) or ""
    if role not in ("parent",) and not _is_family_owner(user_id, family_id):
        raise HTTPException(status_code=403, detail="parents_only")

    return {
        "family_id": family_id,
        "members": list_family_cd_status(family_id),
    }


def _is_family_owner(user_id: int, family_id: str) -> bool:
    from sqlalchemy import text

    from app.database.database import engine

    with engine.connect() as conn:
        row = conn.execute(
            text(
                """
                SELECT 1 FROM families
                WHERE id = :fid AND owner_user_id = :uid LIMIT 1
                """
            ),
            {"fid": family_id, "uid": int(user_id)},
        ).first()
    return row is not None
