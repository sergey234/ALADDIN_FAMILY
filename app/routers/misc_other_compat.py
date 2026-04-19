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

logger = logging.getLogger(__name__)

router = APIRouter(tags=["misc-other-compat"])

_devices_ddl_checked = False

# Rate limit для bind (PIN слабее токена): окно и лимит неудач на пользователя.
_BIND_FAIL_LOCK = threading.Lock()
_BIND_FAIL_TIMES: Dict[str, List[float]] = {}
_BIND_WINDOW_SEC = 600.0
_BIND_MAX_FAILS = 10

PAIRING_PIN_TTL_MINUTES = 15


def _bind_rate_check(user_key: str) -> None:
    now = time.time()
    with _BIND_FAIL_LOCK:
        arr = [t for t in _BIND_FAIL_TIMES.get(user_key, []) if now - t < _BIND_WINDOW_SEC]
        _BIND_FAIL_TIMES[user_key] = arr
        if len(arr) >= _BIND_MAX_FAILS:
            logger.warning("device_bind_rate_limited", extra={"user_key": user_key})
            raise HTTPException(
                status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many pairing attempts. Try again later.",
            )


def _bind_rate_record_fail(user_key: str) -> None:
    now = time.time()
    with _BIND_FAIL_LOCK:
        arr = [t for t in _BIND_FAIL_TIMES.get(user_key, []) if now - t < _BIND_WINDOW_SEC]
        arr.append(now)
        _BIND_FAIL_TIMES[user_key] = arr


def _normalize_pin_digits(pin: Optional[str]) -> Optional[str]:
    if not pin:
        return None
    digits = re.sub(r"\D+", "", pin)
    if len(digits) < 6:
        return None
    return digits[:6]


def _pairing_token_sha256(token: str) -> str:
    return hashlib.sha256(token.strip().encode("utf-8")).hexdigest()


def _ensure_family_devices_table(db: Session) -> None:
    """
    Таблица для iOS: POST/GET /api/devices (контракт DeviceResponse).
    Отдельная схема от возможных legacy-таблиц: aladdin_family_devices.
    """
    global _devices_ddl_checked
    if _devices_ddl_checked:
        return
    db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS aladdin_family_devices (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                owner_label TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'protected',
                last_active TEXT NOT NULL DEFAULT '',
                pairing_token TEXT,
                short_pin TEXT,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            """
        )
    )
    db.execute(
        text(
            "CREATE INDEX IF NOT EXISTS idx_aladdin_family_devices_user_id "
            "ON aladdin_family_devices(user_id);"
        )
    )
    db.execute(
        text(
            "ALTER TABLE aladdin_family_devices "
            "ADD COLUMN IF NOT EXISTS pairing_token_sha256 VARCHAR(64);"
        )
    )
    db.execute(
        text(
            "CREATE INDEX IF NOT EXISTS idx_aladdin_family_devices_pairing_sha256 "
            "ON aladdin_family_devices(pairing_token_sha256);"
        )
    )
    # Backfill SHA256 for pending rows created до появления колонки (идемпотентность 409 по токену).
    pending = db.execute(
        text(
            """
            SELECT id, pairing_token
            FROM aladdin_family_devices
            WHERE pairing_token IS NOT NULL
              AND pairing_token <> ''
              AND (pairing_token_sha256 IS NULL OR pairing_token_sha256 = '')
            """
        )
    ).fetchall()
    for rid, ptok in pending:
        if not ptok:
            continue
        h = _pairing_token_sha256(str(ptok))
        db.execute(
            text(
                "UPDATE aladdin_family_devices SET pairing_token_sha256 = :h WHERE id = :id"
            ),
            {"h": h, "id": rid},
        )
    db.commit()
    _devices_ddl_checked = True


class AddDeviceBody(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    type: str = Field(..., min_length=1, max_length=32)
    owner: str = Field(..., min_length=1, max_length=200)


class BindDeviceBody(BaseModel):
    """Гибрид: токен из QR/ссылки или только PIN (6 цифр в TTL)."""

    token: Optional[str] = Field(None, max_length=512)
    pin: Optional[str] = Field(None, max_length=32)


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


@router.get("/api/malware/quarantine/action", response_model=Dict[str, Any])
async def malware_quarantine_action(
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _ = current_user.get("id")
    return {"success": True}


@router.get("/api/malware/threats", response_model=List[Dict[str, Any]])
async def malware_threats(
    current_user: dict = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    _ = current_user.get("id")
    return []


@router.get("/api/protection/quarantine/action", response_model=Dict[str, Any])
async def protection_quarantine_action(
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _ = current_user.get("id")
    return {"success": True}


@router.get("/api/protection/threats", response_model=List[Dict[str, Any]])
async def protection_threats(
    current_user: dict = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    _ = current_user.get("id")
    return []


@router.get("/api/protection/threats/test", response_model=Dict[str, Any])
async def protection_threats_test(
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _ = current_user.get("id")
    return {"success": True}


@router.get("/api/devices", response_model=List[Dict[str, Any]])
def devices_list(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    uid = _uid_str(current_user)
    if not uid:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid user context")
    try:
        _ensure_family_devices_table(db)
        result = db.execute(
            text(
                """
                SELECT id, name, owner_label AS owner, type, status, last_active,
                       pairing_token, short_pin
                FROM aladdin_family_devices
                WHERE user_id = :uid
                ORDER BY created_at DESC
                """
            ),
            {"uid": uid},
        )
        out: List[Dict[str, Any]] = []
        for row in result.mappings().all():
            item = dict(row)
            if item.get("pairing_token") is None:
                item.pop("pairing_token", None)
            if item.get("short_pin") is None:
                item.pop("short_pin", None)
            item.pop("pairing_token_sha256", None)
            out.append(item)
        return out
    except SQLAlchemyError as e:
        logger.exception("devices_list_failed: %s", e)
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Devices list unavailable",
        )


@router.post("/api/devices", response_model=Dict[str, Any])
def devices_create(
    body: AddDeviceBody,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    uid = _uid_str(current_user)
    if not uid:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid user context")
    dev_id = str(uuid.uuid4())
    pairing_token = secrets.token_urlsafe(32)
    token_sha = _pairing_token_sha256(pairing_token)
    short_pin = f"{secrets.randbelow(1_000_000):06d}"
    now = _now_iso()
    t = body.type.strip().lower()
    if t not in {"iphone", "ipad", "mac", "android"}:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid device type",
        )
    try:
        _ensure_family_devices_table(db)
        db.execute(
            text(
                """
                INSERT INTO aladdin_family_devices
                (id, user_id, name, type, owner_label, status, last_active, pairing_token, short_pin, pairing_token_sha256)
                VALUES (:id, :uid, :name, :type, :owner, 'protected', :now, :ptoken, :spin, :ptoken_sha)
                """
            ),
            {
                "id": dev_id,
                "uid": uid,
                "name": body.name.strip(),
                "type": t,
                "owner": body.owner.strip(),
                "now": now,
                "ptoken": pairing_token,
                "spin": short_pin,
                "ptoken_sha": token_sha,
            },
        )
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        logger.exception("devices_create_failed: %s", e)
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not save device",
        )
    return {
        "id": dev_id,
        "name": body.name.strip(),
        "owner": body.owner.strip(),
        "type": t,
        "status": "protected",
        "last_active": now,
        "pairing_token": pairing_token,
        "short_pin": short_pin,
    }


@router.post("/api/devices/bind", response_model=Dict[str, Any])
def devices_bind(
    request: Request,
    body: BindDeviceBody,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Сопряжение: по секретному `pairing_token` (QR/ссылка) или по `short_pin` внутри TTL.
    Токен не привязан к user_id создателя: достаточно знать секрет (как у бытовых pairing-кодов).
    """
    uid = _uid_str(current_user)
    if not uid:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid user context")
    rate_key = f"{uid}:{request.client.host if request.client else 'unknown'}"
    token = (body.token or "").strip() if body.token else ""
    pin = _normalize_pin_digits(body.pin) if body.pin else None
    if not token and not pin:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="token or pin required",
        )

    _bind_rate_check(rate_key)

    try:
        _ensure_family_devices_table(db)
        now = _now_iso()
        res = None
        token_hash = _pairing_token_sha256(token) if token else None

        if token:
            res = db.execute(
                text(
                    """
                    UPDATE aladdin_family_devices
                    SET pairing_token = NULL,
                        short_pin = NULL,
                        last_active = :now,
                        pairing_token_sha256 = COALESCE(pairing_token_sha256, :th)
                    WHERE pairing_token = :token AND pairing_token IS NOT NULL
                    """
                ),
                {"token": token, "now": now, "th": token_hash},
            )
        elif pin:
            rowm = db.execute(
                text(
                    f"""
                    SELECT id, pairing_token
                    FROM aladdin_family_devices
                    WHERE short_pin = :pin
                      AND pairing_token IS NOT NULL
                      AND created_at > (NOW() AT TIME ZONE 'utc' - INTERVAL '{PAIRING_PIN_TTL_MINUTES} minutes')
                    LIMIT 1
                    """
                ),
                {"pin": pin},
            ).mappings().first()
            if rowm:
                rid = rowm["id"]
                ptok = rowm.get("pairing_token") or ""
                th_pin = _pairing_token_sha256(str(ptok)) if ptok else None
                res = db.execute(
                    text(
                        """
                        UPDATE aladdin_family_devices
                        SET pairing_token = NULL,
                            short_pin = NULL,
                            last_active = :now,
                            pairing_token_sha256 = COALESCE(pairing_token_sha256, :th)
                        WHERE id = :id
                        """
                    ),
                    {"now": now, "th": th_pin, "id": rid},
                )
            else:
                res = None

        if res is None or res.rowcount == 0:
            db.rollback()
            if token and token_hash:
                used = db.execute(
                    text(
                        """
                        SELECT 1 FROM aladdin_family_devices
                        WHERE pairing_token_sha256 = :th
                          AND pairing_token IS NULL
                        LIMIT 1
                        """
                    ),
                    {"th": token_hash},
                ).scalar()
                if used:
                    logger.info(
                        "device_bind_conflict",
                        extra={"mode": "token", "user": uid},
                    )
                    raise HTTPException(
                        status.HTTP_409_CONFLICT,
                        detail="Pairing token already used",
                    )
            _bind_rate_record_fail(rate_key)
            logger.info(
                "device_bind_miss",
                extra={"mode": "token" if token else "pin", "user": uid},
            )
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="Pairing not found, expired, or already used",
            )
        db.commit()
        logger.info("device_bind_ok", extra={"mode": "token" if token else "pin", "user": uid})
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.exception("devices_bind_failed: %s", e)
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Bind unavailable",
        )
    return {"success": True, "data": True, "message": "Device bound", "error": None}


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
