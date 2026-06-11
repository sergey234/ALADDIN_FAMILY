"""
Identity Theft API — explicit routers (B1-03 / id-*). Detect, not stats-only.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field

from app.auth.auth import get_current_user
from app.services.identity_theft_premium import user_has_identity_access
from app.services.identity_theft_service import (
    allow_attempt,
    block_attempt,
    check_fraud,
    detect_theft,
    get_attempts,
    get_stats,
    monitor_credit,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/identity-theft", tags=["identity-theft"])


class DetectRequest(BaseModel):
    snils: Optional[str] = Field(default=None, max_length=32)
    snils_hash: Optional[str] = Field(default=None, max_length=128)


class CheckFraudRequest(BaseModel):
    snils_hash: Optional[str] = Field(default=None, max_length=128)
    passport_series_hash: Optional[str] = Field(default=None, max_length=128)
    passport_number_hash: Optional[str] = Field(default=None, max_length=128)


class AttemptActionRequest(BaseModel):
    attempt_id: str = Field(..., min_length=1, max_length=64)


def _user_id(user: Dict[str, Any]) -> int:
    uid = user.get("id") or user.get("user_id") or user.get("sub")
    try:
        return int(str(uid))
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="invalid_user_id") from exc


def _require_premium(user: Dict[str, Any], request: Request) -> None:
    smoke_secret = request.headers.get("X-Aladdin-Smoke")
    if not user_has_identity_access(user, smoke_secret=smoke_secret):
        raise HTTPException(
            status_code=403,
            detail={
                "error": "premium_required",
                "message": "Identity theft protection requires Premium subscription",
                "premium_required": True,
            },
        )


def _handle_service_error(exc: Exception) -> None:
    if isinstance(exc, ValueError):
        detail = str(exc)
        if detail.startswith("mock_"):
            raise HTTPException(status_code=503, detail=detail) from exc
        status = 404 if detail.endswith("_not_found") else 422
        raise HTTPException(status_code=status, detail=detail) from exc
    raise HTTPException(status_code=503, detail=str(exc)) from exc


def _validate_verdict(payload: Dict[str, Any]) -> Dict[str, Any]:
    verdict = payload.get("verdict")
    if verdict not in ("likely_fake", "uncertain", "likely_real"):
        raise HTTPException(status_code=503, detail="invalid_verdict_contract")
    source = str(payload.get("source", ""))
    if source in ("sfm_mock", "mock", "sfm_stub"):
        raise HTTPException(status_code=503, detail="mock_source_rejected")
    return payload


@router.get("/stats")
async def identity_stats(
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    _require_premium(current_user, request)
    try:
        return get_stats(_user_id(current_user))
    except Exception as exc:
        _handle_service_error(exc)


@router.get("/attempts")
async def identity_attempts(
    request: Request,
    limit: int = Query(default=20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    _require_premium(current_user, request)
    try:
        return get_attempts(_user_id(current_user), limit=limit)
    except Exception as exc:
        _handle_service_error(exc)


@router.post("/detect")
async def identity_detect(
    request: Request,
    body: DetectRequest,
    current_user: dict = Depends(get_current_user),
):
    _require_premium(current_user, request)
    if not body.snils and not body.snils_hash:
        raise HTTPException(status_code=422, detail="snils_or_hash_required")
    try:
        result = _validate_verdict(
            detect_theft(
                _user_id(current_user),
                snils=body.snils,
                snils_hash=body.snils_hash,
            )
        )
    except HTTPException:
        raise
    except Exception as exc:
        _handle_service_error(exc)
    logger.info(
        "identity_detect user=%s verdict=%s source=%s",
        current_user.get("id"),
        result.get("verdict"),
        result.get("source"),
    )
    return result


@router.post("/monitor/credit")
async def identity_monitor_credit(
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    _require_premium(current_user, request)
    try:
        return _validate_verdict(monitor_credit(_user_id(current_user)))
    except HTTPException:
        raise
    except Exception as exc:
        _handle_service_error(exc)


@router.post("/monitor-credit", include_in_schema=True)
async def identity_monitor_credit_legacy_alias(
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    """SEC-P2-02: canonical alias for legacy POST /monitor-credit."""
    return await identity_monitor_credit(request, current_user)


@router.post("/check/fraud")
async def identity_check_fraud(
    request: Request,
    body: CheckFraudRequest,
    current_user: dict = Depends(get_current_user),
):
    _require_premium(current_user, request)
    try:
        return _validate_verdict(
            check_fraud(
                _user_id(current_user),
                snils_hash=body.snils_hash,
                passport_series_hash=body.passport_series_hash,
                passport_number_hash=body.passport_number_hash,
            )
        )
    except HTTPException:
        raise
    except Exception as exc:
        _handle_service_error(exc)


@router.post("/allow")
async def identity_allow(
    request: Request,
    body: AttemptActionRequest,
    current_user: dict = Depends(get_current_user),
):
    _require_premium(current_user, request)
    try:
        return allow_attempt(_user_id(current_user), body.attempt_id)
    except Exception as exc:
        _handle_service_error(exc)


@router.post("/block")
async def identity_block(
    request: Request,
    body: AttemptActionRequest,
    current_user: dict = Depends(get_current_user),
):
    _require_premium(current_user, request)
    try:
        return block_attempt(_user_id(current_user), body.attempt_id)
    except Exception as exc:
        _handle_service_error(exc)
