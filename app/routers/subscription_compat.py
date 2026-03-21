"""
Compatibility endpoints for /api/subscription/* paths from iOS endpoint matrix.
"""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends

from app.auth.auth import get_current_user


router = APIRouter(prefix="/api/subscription", tags=["subscription-compat"])


@router.get("/tariffs", response_model=List[Dict[str, Any]])
async def subscription_tariffs(
    current_user: dict = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    _ = current_user.get("id")
    return []


@router.get("/subscribe", response_model=Dict[str, Any])
async def subscription_subscribe(
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _ = current_user.get("id")
    return {"success": True, "subscribed": True}


@router.get("/activate", response_model=Dict[str, Any])
async def subscription_activate(
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _ = current_user.get("id")
    return {"success": True, "activated": True}


@router.get("/activation/activate", response_model=Dict[str, Any])
async def subscription_activation_activate(
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _ = current_user.get("id")
    return {"success": True, "activation": "started"}


@router.get("/activation/verify", response_model=Dict[str, Any])
async def subscription_activation_verify(
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _ = current_user.get("id")
    return {"success": True, "activation": "verified"}
