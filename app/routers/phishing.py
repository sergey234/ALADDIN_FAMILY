"""
Phishing protection API — explicit routers (B1-07 / comp-01). No wildcard mock.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from app.auth.auth import get_current_user_optional
from app.services.phishing_service import (
    get_block_suspicious,
    get_exclusions,
    get_sensitivity,
    update_block_suspicious,
    update_sensitivity,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/phishing", tags=["phishing"])


class SensitivityUpdate(BaseModel):
    level: Optional[str] = None
    sensitivity_level: Optional[str] = None
    sensitivityLevel: Optional[str] = None
    blockSuspiciousLinks: Optional[bool] = None
    warnBeforeOpening: Optional[bool] = None
    checkEmailLinks: Optional[bool] = None
    checkSMSLinks: Optional[bool] = None
    blockKnownPhishingDomains: Optional[bool] = None


class BlockSuspiciousUpdate(BaseModel):
    enabled: Optional[bool] = None
    block_suspicious: Optional[bool] = None
    blockSuspiciousLinks: Optional[bool] = None


def _user_id(user: Optional[Dict[str, Any]]) -> Optional[int]:
    if not user:
        return None
    raw = user.get("id") or user.get("user_id") or user.get("sub")
    try:
        return int(str(raw))
    except (TypeError, ValueError):
        return None


def _handle_service_error(exc: Exception) -> None:
    if isinstance(exc, ValueError):
        detail = str(exc)
        if detail == "auth_required":
            raise HTTPException(status_code=401, detail=detail) from exc
        if detail.startswith("mock_"):
            raise HTTPException(status_code=503, detail=detail) from exc
        raise HTTPException(status_code=503, detail=detail) from exc
    raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/sensitivity")
async def phishing_get_sensitivity(
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    try:
        return get_sensitivity(_user_id(current_user))
    except Exception as exc:
        _handle_service_error(exc)


@router.put("/sensitivity")
async def phishing_update_sensitivity(
    body: SensitivityUpdate,
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    try:
        return update_sensitivity(_user_id(current_user), body.model_dump(exclude_none=True))
    except Exception as exc:
        _handle_service_error(exc)


@router.get("/block_suspicious")
async def phishing_get_block_suspicious(
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    try:
        return get_block_suspicious(_user_id(current_user))
    except Exception as exc:
        _handle_service_error(exc)


@router.put("/block_suspicious")
async def phishing_update_block_suspicious(
    body: BlockSuspiciousUpdate,
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    try:
        return update_block_suspicious(_user_id(current_user), body.model_dump(exclude_none=True))
    except Exception as exc:
        _handle_service_error(exc)


@router.get("/exclusions")
async def phishing_get_exclusions(
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    _ = current_user
    try:
        return get_exclusions(_user_id(current_user))
    except Exception as exc:
        _handle_service_error(exc)
