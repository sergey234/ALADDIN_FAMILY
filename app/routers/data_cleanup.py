"""
Data Cleanup API — explicit routers (B1-04 / dc-*). No wildcard. No mock.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field

from app.auth.auth import get_current_user
from app.services.data_cleanup_premium import user_has_cleanup_access
from app.services.data_cleanup_service import get_records, get_stats, start_cleanup

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/data-cleanup", tags=["data-cleanup"])


class StartCleanupRequest(BaseModel):
    categories: List[str] = Field(default_factory=list, max_length=32)


def _user_id(user: Dict[str, Any]) -> int:
    uid = user.get("id") or user.get("user_id") or user.get("sub")
    try:
        return int(str(uid))
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="invalid_user_id") from exc


def _require_premium(user: Dict[str, Any], request: Request) -> None:
    smoke_secret = request.headers.get("X-Aladdin-Smoke")
    if not user_has_cleanup_access(user, smoke_secret=smoke_secret):
        raise HTTPException(
            status_code=403,
            detail={
                "error": "premium_required",
                "message": "Data cleanup requires Premium subscription",
                "premium_required": True,
            },
        )


def _handle_service_error(exc: Exception) -> None:
    if isinstance(exc, ValueError):
        detail = str(exc)
        if detail.startswith("mock_"):
            raise HTTPException(status_code=503, detail=detail) from exc
        raise HTTPException(status_code=503, detail=detail) from exc
    raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/stats")
async def cleanup_stats(
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    _require_premium(current_user, request)
    try:
        result = get_stats(_user_id(current_user))
    except Exception as exc:
        _handle_service_error(exc)
    logger.info(
        "data_cleanup_stats user=%s count=%s source=%s",
        current_user.get("id"),
        result.get("cleanupsCount"),
        result.get("source"),
    )
    return result


@router.get("/records")
async def cleanup_records(
    request: Request,
    limit: int = Query(default=20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    _require_premium(current_user, request)
    try:
        return get_records(_user_id(current_user), limit=limit)
    except Exception as exc:
        _handle_service_error(exc)


@router.post("/start")
async def cleanup_start(
    request: Request,
    body: StartCleanupRequest,
    current_user: dict = Depends(get_current_user),
):
    _require_premium(current_user, request)
    try:
        result = start_cleanup(_user_id(current_user), categories=body.categories)
    except Exception as exc:
        _handle_service_error(exc)
    logger.info(
        "data_cleanup_start user=%s job_id=%s source=%s",
        current_user.get("id"),
        result.get("job_id"),
        result.get("source"),
    )
    return result
