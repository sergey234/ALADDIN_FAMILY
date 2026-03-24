"""
Compatibility and production endpoints for /api/network-protection/*.
"""

from typing import Any, Dict, List
import json

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.auth.auth import get_current_user
from app.database.database import get_session


router = APIRouter(prefix="/api/network-protection", tags=["network-protection-compat"])
limiter = Limiter(key_func=get_remote_address)


def _default_settings() -> Dict[str, Any]:
    return {
        "autoSelectServer": True,
        "autoConnectWiFi": True,
        "autoConnectMobile": False,
        "killSwitch": True,
        "dnsLeakProtection": True,
        "batteryOptimizationEnabled": True,
        "antivirusEnabled": True,
    }


class NetworkProtectionSettingsPatchRequest(BaseModel):
    autoSelectServer: bool
    autoConnectWiFi: bool
    autoConnectMobile: bool
    killSwitch: bool
    dnsLeakProtection: bool
    batteryOptimizationEnabled: bool
    antivirusEnabled: bool


async def _ensure_settings_table(db: AsyncSession) -> None:
    await db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS network_protection_settings (
                user_id TEXT PRIMARY KEY,
                settings_json TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
    )
    await db.commit()


@router.get("/status", response_model=Dict[str, Any])
async def network_protection_status(
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _ = current_user.get("id")
    return {"connected": False, "protectionEnabled": True}


@router.get("/stats", response_model=Dict[str, Any])
async def network_protection_stats(
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _ = current_user.get("id")
    return {"blockedThreats": 0, "safeRequests": 0}


@router.get("/settings", response_model=Dict[str, Any])
@limiter.limit("60/minute")
async def network_protection_settings(
    request: Request,
    db: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _ = request
    await _ensure_settings_table(db)
    user_id = str(current_user.get("id"))
    row = await db.execute(
        text("SELECT settings_json FROM network_protection_settings WHERE user_id = :user_id"),
        {"user_id": user_id},
    )
    found = row.fetchone()
    if not found:
        return _default_settings()
    try:
        decoded = json.loads(found[0])
        defaults = _default_settings()
        defaults.update(decoded if isinstance(decoded, dict) else {})
        return defaults
    except Exception:
        return _default_settings()


@router.patch("/settings", response_model=Dict[str, Any])
@limiter.limit("60/minute")
async def patch_network_protection_settings(
    payload: NetworkProtectionSettingsPatchRequest,
    request: Request,
    db: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _ = request
    await _ensure_settings_table(db)
    user_id = str(current_user.get("id"))
    payload_dict = payload.dict()
    settings_json = json.dumps(payload_dict)

    existing = await db.execute(
        text("SELECT user_id FROM network_protection_settings WHERE user_id = :user_id"),
        {"user_id": user_id},
    )
    if existing.fetchone():
        await db.execute(
            text(
                """
                UPDATE network_protection_settings
                SET settings_json = :settings_json, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = :user_id
                """
            ),
            {"settings_json": settings_json, "user_id": user_id},
        )
    else:
        await db.execute(
            text(
                """
                INSERT INTO network_protection_settings (user_id, settings_json, updated_at)
                VALUES (:user_id, :settings_json, CURRENT_TIMESTAMP)
                """
            ),
            {"user_id": user_id, "settings_json": settings_json},
        )
    await db.commit()
    return {"success": True, "settings": payload_dict}


@router.get("/servers", response_model=List[Dict[str, Any]])
async def network_protection_servers(
    current_user: dict = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    _ = current_user.get("id")
    return []


@router.get("/connect", response_model=Dict[str, Any])
async def network_protection_connect(
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _ = current_user.get("id")
    return {"success": True, "connected": True}


@router.get("/disconnect", response_model=Dict[str, Any])
async def network_protection_disconnect(
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _ = current_user.get("id")
    return {"success": True, "connected": False}


@router.get("/config", response_model=Dict[str, Any])
async def network_protection_config(
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _ = current_user.get("id")
    return {"mode": "standard"}
