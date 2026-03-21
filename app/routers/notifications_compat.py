"""
Compatibility endpoints for /api/notifications/* paths from iOS endpoint matrix.
"""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends

from app.auth.auth import get_current_user


router = APIRouter(prefix="/api/notifications", tags=["notifications-compat"])


@router.get("/stats", response_model=Dict[str, Any])
async def notifications_stats(
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _ = current_user.get("id")
    return {"total": 0, "unread": 0}


@router.get("/categories", response_model=List[Dict[str, Any]])
async def notifications_categories(
    current_user: dict = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    _ = current_user.get("id")
    return []


@router.get("/archive", response_model=Dict[str, Any])
async def notifications_archive(
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _ = current_user.get("id")
    return {"success": True}


@router.get("/bulk-mark-read", response_model=Dict[str, Any])
async def notifications_bulk_mark_read(
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _ = current_user.get("id")
    return {"success": True, "updated": 0}
