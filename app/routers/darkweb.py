"""
Dark Web API — explicit routers (B1-02 / dw-*). No wildcard. No mock.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field

from app.auth.auth import get_current_user
from app.services.darkweb_premium import user_has_darkweb_access
from app.services.darkweb_service import (
    check_identifiers,
    get_leaks,
    get_scans,
    get_stats,
    resolve_leak,
    start_scan,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/darkweb", tags=["darkweb"])


class CheckRequest(BaseModel):
    email: Optional[str] = Field(default=None, max_length=320)
    phone: Optional[str] = Field(default=None, max_length=32)


class ResolveRequest(BaseModel):
    leak_id: str = Field(..., min_length=1, max_length=64)
    status: Optional[str] = Field(default="resolved")


def _user_id(user: Dict[str, Any]) -> int:
    uid = user.get("id") or user.get("user_id") or user.get("sub")
    try:
        return int(str(uid))
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="invalid_user_id") from exc


def _require_premium(user: Dict[str, Any], request: Request) -> None:
    smoke_secret = request.headers.get("X-Aladdin-Smoke")
    if not user_has_darkweb_access(user, smoke_secret=smoke_secret):
        raise HTTPException(
            status_code=403,
            detail={
                "error": "premium_required",
                "message": "Dark Web monitoring requires Premium subscription",
                "premium_required": True,
            },
        )


def _handle_service_error(exc: Exception) -> None:
    if isinstance(exc, ValueError):
        detail = str(exc)
        if detail.startswith("mock_"):
            raise HTTPException(status_code=503, detail=detail) from exc
        if detail in ("leak_not_found", "email_or_phone_required"):
            raise HTTPException(status_code=404 if detail == "leak_not_found" else 422, detail=detail) from exc
        raise HTTPException(status_code=503, detail=detail) from exc
    raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/stats")
async def darkweb_stats(
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    _require_premium(current_user, request)
    try:
        result = get_stats(_user_id(current_user))
    except Exception as exc:
        _handle_service_error(exc)
    logger.info("darkweb_stats user=%s total=%s source=%s", current_user.get("id"), result.get("totalLeaks"), result.get("source"))
    return result


@router.get("/breaches")
async def darkweb_breaches(
    request: Request,
    status: Optional[str] = Query(default=None),
    severity: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    """SEC-P2-01: canonical breaches list (alias of /leaks for legacy clients)."""
    _require_premium(current_user, request)
    try:
        result = get_leaks(_user_id(current_user), status=status, severity=severity, limit=limit)
    except Exception as exc:
        _handle_service_error(exc)
    return result


@router.get("/leaks")
async def darkweb_leaks(
    request: Request,
    status: Optional[str] = Query(default=None),
    severity: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    _require_premium(current_user, request)
    try:
        result = get_leaks(_user_id(current_user), status=status, severity=severity, limit=limit)
    except Exception as exc:
        _handle_service_error(exc)
    return result


@router.get("/scans")
async def darkweb_scans(
    request: Request,
    limit: int = Query(default=20, ge=1, le=50),
    current_user: dict = Depends(get_current_user),
):
    _require_premium(current_user, request)
    try:
        result = get_scans(_user_id(current_user), limit=limit)
    except Exception as exc:
        _handle_service_error(exc)
    return result


@router.post("/scan/start")
async def darkweb_scan_start(
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    _require_premium(current_user, request)
    try:
        result = start_scan(_user_id(current_user))
    except Exception as exc:
        _handle_service_error(exc)
    logger.info("darkweb_scan_start user=%s scan_id=%s", current_user.get("id"), result.get("scan_id"))
    return result


@router.post("/check")
async def darkweb_check(
    request: Request,
    body: CheckRequest,
    current_user: dict = Depends(get_current_user),
):
    _require_premium(current_user, request)
    try:
        result = check_identifiers(_user_id(current_user), email=body.email, phone=body.phone)
    except Exception as exc:
        _handle_service_error(exc)
    logger.info(
        "darkweb_check user=%s found=%s source=%s",
        current_user.get("id"),
        result.get("found_count"),
        result.get("source"),
    )
    return result


@router.post("/resolve")
async def darkweb_resolve(
    request: Request,
    body: ResolveRequest,
    current_user: dict = Depends(get_current_user),
):
    _require_premium(current_user, request)
    try:
        result = resolve_leak(_user_id(current_user), body.leak_id, status=body.status or "resolved")
    except Exception as exc:
        _handle_service_error(exc)
    return result
