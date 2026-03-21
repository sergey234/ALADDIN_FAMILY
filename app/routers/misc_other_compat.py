"""
Compatibility endpoints for remaining /api/* paths in 'other' cluster.
"""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends

from app.auth.auth import get_current_user


router = APIRouter(tags=["misc-other-compat"])


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
async def devices_list(
    current_user: dict = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    _ = current_user.get("id")
    return []


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
