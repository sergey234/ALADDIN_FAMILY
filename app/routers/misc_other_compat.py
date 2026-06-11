"""
Compatibility endpoints for remaining /api/* paths in 'other' cluster.
"""

from __future__ import annotations

import hashlib
import logging
import re
import secrets
import threading
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.auth.auth import get_current_user
from app.database.database import get_db
from app.services.user_malware_threats import apply_quarantine_action, fetch_threats_envelope

logger = logging.getLogger(__name__)

router = APIRouter(tags=["misc-other-compat"])

def _uid_str(user: dict) -> str:
    raw = user.get("id")
    return str(raw) if raw is not None else ""


def _now_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


class QuarantineActionBody(BaseModel):
    """Тело как у iOS `QuarantineActionRequest` (camelCase в JSON)."""

    threatId: str = Field(..., min_length=1, max_length=256)
    action: str = Field(..., min_length=1, max_length=64)
    filePath: Optional[str] = Field(None, max_length=4096)


@router.get("/api/malware/threats", response_model=Dict[str, Any], include_in_schema=False)
async def malware_threats(
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Список угроз в формате iOS `ThreatsListResponse` (PostgreSQL `user_malware_threats`).
    Query `status` фильтрует элементы `threats` (active | quarantined | resolved); счётчики — по всем записям пользователя.
    """
    uid = _uid_str(current_user)
    if not uid:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid user context")
    try:
        return fetch_threats_envelope(db, uid, status)
    except SQLAlchemyError as e:
        logger.exception("malware_threats_list_failed: %s", e)
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Threats list unavailable",
        )


@router.get("/api/malware/quarantine/action", response_model=Dict[str, Any])
async def malware_quarantine_action_get(
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Легаси GET; iOS использует POST. Оставлен для совместимости и OpenAPI."""
    _ = current_user.get("id")
    return {"success": True, "message": None, "threat": None}


@router.post("/api/malware/quarantine/action", response_model=Dict[str, Any])
async def malware_quarantine_action_post(
    body: QuarantineActionBody,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Действие по карантину как у iOS `quarantineFileAsync` (POST + JSON).
    Обновляет строки в `user_malware_threats` (источник правды на сервере).
    """
    uid = _uid_str(current_user)
    if not uid:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid user context")
    if body.action not in ("quarantine", "restore", "remove"):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="action must be one of: quarantine, restore, remove",
        )
    try:
        return apply_quarantine_action(
            db, uid, body.threatId, body.action, body.filePath
        )
    except SQLAlchemyError as e:
        logger.exception("malware_quarantine_action_failed: %s", e)
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Quarantine action unavailable",
        )


@router.get("/api/protection/quarantine/action", response_model=Dict[str, Any])
async def protection_quarantine_action_get(
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _ = current_user.get("id")
    return {"success": True, "message": None, "threat": None}


@router.post("/api/protection/quarantine/action", response_model=Dict[str, Any])
async def protection_quarantine_action_post(
    body: QuarantineActionBody,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    uid = _uid_str(current_user)
    if not uid:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid user context")
    if body.action not in ("quarantine", "restore", "remove"):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="action must be one of: quarantine, restore, remove",
        )
    try:
        return apply_quarantine_action(
            db, uid, body.threatId, body.action, body.filePath
        )
    except SQLAlchemyError as e:
        logger.exception("protection_quarantine_action_failed: %s", e)
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Quarantine action unavailable",
        )


@router.get("/api/protection/threats", response_model=Dict[str, Any])
async def protection_threats(
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    uid = _uid_str(current_user)
    if not uid:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid user context")
    try:
        return fetch_threats_envelope(db, uid, status)
    except SQLAlchemyError as e:
        logger.exception("protection_threats_list_failed: %s", e)
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Threats list unavailable",
        )


@router.get("/api/protection/threats/test", response_model=Dict[str, Any])
async def protection_threats_test(
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _ = current_user.get("id")
    return {"success": True}



@router.get("/api/location/geofences", response_model=List[Dict[str, Any]])
async def location_geofences(
    current_user: dict = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    _ = current_user.get("id")
    return []


@router.get("/api/payments/qr/status/test", response_model=Dict[str, Any])
async def payments_qr_status_test(
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _ = current_user.get("id")
    return {"status": "ok"}


@router.get("/api/test", response_model=Dict[str, Any])
async def api_test() -> Dict[str, Any]:
    return {"status": "ok"}
