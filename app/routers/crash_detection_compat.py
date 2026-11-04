"""
Compatibility endpoints for /api/crash-detection/* paths from iOS endpoint matrix.
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.auth.auth import get_current_user


router = APIRouter(prefix="/api/crash-detection", tags=["crash-detection-compat"])


class CrashDetectionSettingsUpdateRequest(BaseModel):
    """iOS sends g-force threshold (2.0 / 3.0 / 4.0), not a 0…1 ratio."""

    user_id: Optional[str] = Field(default=None, alias="userId")
    sensitivity: float = Field(default=3.0, ge=0.5, le=10.0)
    geofence_radius: float = Field(default=1000.0, ge=0.0, alias="geofenceRadius")

    class Config:
        allow_population_by_field_name = True


@router.get("/setup", response_model=Dict[str, Any])
async def crash_detection_setup(
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _ = current_user.get("id")
    return {"success": True, "configured": True}


@router.get("/alert", response_model=Dict[str, Any])
async def crash_detection_alert(
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _ = current_user.get("id")
    return {"success": True, "alertSent": False}


@router.get("/settings/update", response_model=Dict[str, Any])
async def crash_detection_settings_update(
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _ = current_user.get("id")
    return {"success": True, "updated": True}


@router.post("/settings/update", response_model=Dict[str, Any])
async def crash_detection_settings_update_post(
    body: CrashDetectionSettingsUpdateRequest,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    user_id = body.user_id or str(current_user.get("id") or "")
    return {
        "success": True,
        "data": True,
        "updated": True,
        "userId": user_id,
        "sensitivity": body.sensitivity,
        "geofenceRadius": body.geofence_radius,
    }


@router.post("/start", response_model=Dict[str, Any])
async def crash_detection_start(
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """iOS calls this after settings; monitoring runs on-device. Ack only — no SFM."""
    _ = current_user.get("id")
    return {"success": True, "data": True, "started": True}


@router.post("/stop", response_model=Dict[str, Any])
async def crash_detection_stop(
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _ = current_user.get("id")
    return {"success": True, "data": True, "stopped": True}


@router.get("/status", response_model=Dict[str, Any])
async def crash_detection_status(
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _ = current_user.get("id")
    return {"success": True, "data": True, "monitoring": False}
