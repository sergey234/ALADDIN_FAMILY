"""
Mobile security API — explicit routers (B1-09 / mob-01). No wildcard mock.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.auth.auth import get_current_user_optional
from app.services.mobile_security_service import (
    get_app_lock,
    get_biometric,
    run_device_scan,
    run_security_check,
    update_app_lock,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/mobile", tags=["mobile-security"])


class AppLockUpdate(BaseModel):
    enabled: Optional[bool] = None
    timeout_minutes: Optional[int] = Field(None, ge=1, le=120)
    screen_lock: Optional[bool] = None


class ScanRequest(BaseModel):
    device_id: Optional[str] = Field(None, max_length=128)


def _user_id(user: Optional[Dict[str, Any]]) -> Optional[int]:
    if not user:
        return None
    raw = user.get("id") or user.get("user_id") or user.get("sub")
    try:
        return int(str(raw))
    except (TypeError, ValueError):
        return None


def _resolve_device_id(explicit: Optional[str], user: Optional[Dict[str, Any]]) -> str:
    if explicit:
        return explicit
    if user and user.get("sub"):
        return str(user["sub"])
    return "mobile_device_default"


def _handle_service_error(exc: Exception) -> None:
    if isinstance(exc, ValueError):
        detail = str(exc)
        if detail == "auth_required":
            raise HTTPException(status_code=401, detail=detail) from exc
        if detail.startswith("mock_"):
            raise HTTPException(status_code=503, detail=detail) from exc
        raise HTTPException(status_code=503, detail=detail) from exc
    raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/app_lock")
async def mobile_get_app_lock(current_user: Optional[dict] = Depends(get_current_user_optional)):
    try:
        return get_app_lock(_user_id(current_user))
    except Exception as exc:
        _handle_service_error(exc)


@router.put("/app_lock")
async def mobile_update_app_lock(
    body: AppLockUpdate,
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    try:
        return update_app_lock(_user_id(current_user), body.model_dump(exclude_none=True))
    except Exception as exc:
        _handle_service_error(exc)


@router.get("/biometric")
async def mobile_get_biometric(current_user: Optional[dict] = Depends(get_current_user_optional)):
    try:
        return get_biometric(_user_id(current_user))
    except Exception as exc:
        _handle_service_error(exc)


@router.get("/security/check")
async def mobile_security_check_get(
    device_id: Optional[str] = Query(None, alias="deviceId"),
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    device = _resolve_device_id(device_id, current_user)
    try:
        return run_security_check(_user_id(current_user), device)
    except Exception as exc:
        _handle_service_error(exc)


@router.post("/security/check")
async def mobile_security_check_post(
    body: ScanRequest,
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    device = _resolve_device_id(body.device_id, current_user)
    try:
        return run_security_check(_user_id(current_user), device)
    except Exception as exc:
        _handle_service_error(exc)


@router.post("/scan")
async def mobile_device_scan(
    body: ScanRequest,
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    """App inventory / device scan (mob-02)."""
    device = _resolve_device_id(body.device_id, current_user)
    try:
        result = run_device_scan(_user_id(current_user), device)
    except Exception as exc:
        _handle_service_error(exc)
    logger.info(
        "mobile_scan device=%s scan_id=%s threats=%s source=%s",
        device,
        result.get("scan_id"),
        result.get("threats_found"),
        result.get("source"),
    )
    return result
