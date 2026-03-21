"""
Compatibility endpoints for /api/parental/* paths from iOS endpoint matrix.
"""

from typing import Any, Dict

from fastapi import APIRouter, Depends

from app.auth.auth import get_current_user


router = APIRouter(prefix="/api/parental", tags=["parental-compat"])


@router.get("/block", response_model=Dict[str, Any])
async def parental_block(
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _ = current_user.get("id")
    return {"success": True, "blocked": True}


@router.get("/control", response_model=Dict[str, Any])
async def parental_control(
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _ = current_user.get("id")
    return {"success": True, "controlEnabled": True}


@router.get("/limits", response_model=Dict[str, Any])
async def parental_limits(
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _ = current_user.get("id")
    return {"success": True, "dailyLimitMinutes": 0}
