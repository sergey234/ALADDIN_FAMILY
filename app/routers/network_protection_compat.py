"""
Compatibility endpoints for /api/network-protection/* paths from iOS endpoint matrix.
"""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends

from app.auth.auth import get_current_user


router = APIRouter(prefix="/api/network-protection", tags=["network-protection-compat"])


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
async def network_protection_settings(
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _ = current_user.get("id")
    return {"autoConnect": False, "dnsProtection": True}


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
