"""
Location Bubble API — explicit routers (B1-05 / loc-*). No wildcard. No mock.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field

from app.auth.auth import get_current_user
from app.services.location_bubble_premium import user_has_location_bubble_access
from app.services.location_bubble_service import (
    allow_request,
    block_request,
    generate_bubble,
    get_history,
    get_requests,
    get_settings,
    get_stats,
    set_settings,
    update_accuracy,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/location-bubble", tags=["location-bubble"])


class GenerateRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    person_id: Optional[str] = Field(default="self", max_length=64)
    radius: Optional[int] = Field(default=None, ge=50, le=5000)


class SettingsRequest(BaseModel):
    person_id: str = Field(..., min_length=1, max_length=64)
    default_radius_m: int = Field(default=500, ge=50, le=5000)
    enabled: bool = True


class RequestAction(BaseModel):
    request_id: str = Field(..., min_length=1, max_length=64)


class AccuracyRequest(BaseModel):
    accuracy: str = Field(..., pattern="^(high|medium|low)$")


def _user_id(user: Dict[str, Any]) -> int:
    uid = user.get("id") or user.get("user_id") or user.get("sub")
    try:
        return int(str(uid))
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="invalid_user_id") from exc


def _require_premium(user: Dict[str, Any], request: Request) -> None:
    smoke_secret = request.headers.get("X-Aladdin-Smoke")
    if not user_has_location_bubble_access(user, smoke_secret=smoke_secret):
        raise HTTPException(
            status_code=403,
            detail={
                "error": "premium_required",
                "message": "Location bubble requires Premium subscription",
                "premium_required": True,
            },
        )


def _handle_service_error(exc: Exception) -> None:
    if isinstance(exc, ValueError):
        detail = str(exc)
        if detail.startswith("mock_"):
            raise HTTPException(status_code=503, detail=detail) from exc
        if detail.endswith("_not_found"):
            status = 404
        elif detail in ("agent_unavailable", "user_scope_unavailable"):
            status = 503
        else:
            status = 422
        raise HTTPException(status_code=status, detail=detail) from exc
    raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/stats")
async def location_stats(
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    _require_premium(current_user, request)
    try:
        return get_stats(_user_id(current_user))
    except Exception as exc:
        _handle_service_error(exc)


@router.get("/requests")
async def location_requests(
    request: Request,
    limit: int = Query(default=50, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    _require_premium(current_user, request)
    try:
        return get_requests(_user_id(current_user), limit=limit)
    except Exception as exc:
        _handle_service_error(exc)


@router.post("/generate")
async def location_generate(
    request: Request,
    body: GenerateRequest,
    current_user: dict = Depends(get_current_user),
):
    _require_premium(current_user, request)
    try:
        result = generate_bubble(
            _user_id(current_user),
            latitude=body.latitude,
            longitude=body.longitude,
            person_id=body.person_id or "self",
            radius=body.radius,
        )
    except Exception as exc:
        _handle_service_error(exc)
    logger.info(
        "location_bubble_generate user=%s source=%s radius=%s",
        current_user.get("id"),
        result.get("source"),
        result.get("radius"),
    )
    return result


@router.get("/settings")
async def location_settings_all(
    request: Request,
    person_id: Optional[str] = Query(default=None),
    current_user: dict = Depends(get_current_user),
):
    _require_premium(current_user, request)
    try:
        return get_settings(_user_id(current_user), person_id=person_id)
    except Exception as exc:
        _handle_service_error(exc)


@router.post("/settings")
async def location_settings_set(
    request: Request,
    body: SettingsRequest,
    current_user: dict = Depends(get_current_user),
):
    _require_premium(current_user, request)
    try:
        return set_settings(
            _user_id(current_user),
            person_id=body.person_id,
            default_radius_m=body.default_radius_m,
            enabled=body.enabled,
        )
    except Exception as exc:
        _handle_service_error(exc)


@router.get("/history")
async def location_history(
    request: Request,
    limit: int = Query(default=20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    _require_premium(current_user, request)
    try:
        return get_history(_user_id(current_user), limit=limit)
    except Exception as exc:
        _handle_service_error(exc)


@router.post("/allow")
async def location_allow(
    request: Request,
    body: RequestAction,
    current_user: dict = Depends(get_current_user),
):
    _require_premium(current_user, request)
    try:
        return allow_request(_user_id(current_user), body.request_id)
    except Exception as exc:
        _handle_service_error(exc)


@router.post("/block")
async def location_block(
    request: Request,
    body: RequestAction,
    current_user: dict = Depends(get_current_user),
):
    _require_premium(current_user, request)
    try:
        return block_request(_user_id(current_user), body.request_id)
    except Exception as exc:
        _handle_service_error(exc)


@router.post("/update-accuracy")
async def location_update_accuracy(
    request: Request,
    body: AccuracyRequest,
    current_user: dict = Depends(get_current_user),
):
    _require_premium(current_user, request)
    try:
        return update_accuracy(_user_id(current_user), body.accuracy)
    except Exception as exc:
        _handle_service_error(exc)
