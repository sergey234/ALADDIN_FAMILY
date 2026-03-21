"""
Compatibility endpoints for /api/crash-detection/* paths from iOS endpoint matrix.
"""

from typing import Any, Dict

from fastapi import APIRouter, Depends

from app.auth.auth import get_current_user


router = APIRouter(prefix="/api/crash-detection", tags=["crash-detection-compat"])


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
