"""
PROTECTION API — 9 canonical categories, PostgreSQL persist, SFM activate (B0 / W09).
"""
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.auth.auth import get_current_user
from app.services.protection_sfm_bridge import (
    activate_agents_for_category,
    deactivate_agents_for_category,
)
from app.services.protection_store import (
    CANONICAL_CATEGORIES,
    get_protection_settings,
    upsert_protection_settings,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/protection", tags=["protection"])
limiter = Limiter(key_func=get_remote_address)

ALL_CATEGORIES = list(CANONICAL_CATEGORIES)


class CategoryRequest(BaseModel):
    categoryId: str


class ProtectionSettings(BaseModel):
    enabledCategories: Dict[str, bool] = Field(default_factory=dict)
    globalLevel: int = 95


class ProtectionSettingsResponse(BaseModel):
    settings: ProtectionSettings
    lastUpdated: str
    version: str = "1.0.0"


class ProtectionStatusResponse(BaseModel):
    isProtected: bool
    level: int
    threatsBlocked: int
    lastScan: Optional[str] = None


class ThreatScenarioResponse(BaseModel):
    id: str
    name: str
    description: str
    icon: str
    requiredTariff: str
    protectionSteps: List[str]
    category: str


class ProtectionStatsResponse(BaseModel):
    totalThreats: int
    blockedThreats: int
    byCategory: Dict[str, int]


class APIResponse(BaseModel):
    success: bool
    data: Any = None
    message: Optional[str] = None


def _to_response_model(stored: Dict[str, Any]) -> ProtectionSettingsResponse:
    return ProtectionSettingsResponse(
        settings=ProtectionSettings(
            enabledCategories=stored["enabledCategories"],
            globalLevel=stored.get("globalLevel", 95),
        ),
        lastUpdated=stored.get("updated_at", datetime.now(timezone.utc).isoformat()),
        version="1.0.0",
    )


@router.get("/settings", response_model=ProtectionSettingsResponse)
@limiter.limit("60/minute")
async def get_protection_settings_endpoint(
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["id"]
    stored = get_protection_settings(user_id)
    return _to_response_model(stored)


@router.post("/settings", response_model=APIResponse)
@limiter.limit("60/minute")
async def update_protection_settings_endpoint(
    settings: ProtectionSettings,
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["id"]
    upsert_protection_settings(
        user_id,
        settings.enabledCategories,
        settings.globalLevel,
    )
    return APIResponse(success=True, data=True, message="Settings updated successfully")


@router.get("/status", response_model=ProtectionStatusResponse)
@limiter.limit("60/minute")
async def get_protection_status_endpoint(
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["id"]
    stored = get_protection_settings(user_id)
    enabled = sum(1 for v in stored["enabledCategories"].values() if v)
    return ProtectionStatusResponse(
        isProtected=enabled > 0,
        level=stored.get("globalLevel", 95),
        threatsBlocked=0,
        lastScan=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/threat-scenarios", response_model=List[ThreatScenarioResponse])
@limiter.limit("60/minute")
async def get_threat_scenarios_endpoint(
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    _ = current_user
    return []


@router.post("/enable", response_model=APIResponse)
@limiter.limit("60/minute")
async def enable_protection_category(
    request_body: CategoryRequest,
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["id"]
    category_id = request_body.categoryId

    if category_id not in ALL_CATEGORIES:
        raise HTTPException(status_code=404, detail=f"Category {category_id} not found")

    logger.info(
        "protection_category_enabled category_id=%s user_id=%s",
        category_id,
        user_id,
    )

    stored = get_protection_settings(user_id)
    stored["enabledCategories"][category_id] = True
    upsert_protection_settings(
        user_id,
        stored["enabledCategories"],
        stored.get("globalLevel", 95),
    )

    sfm_result = activate_agents_for_category(category_id)

    return APIResponse(
        success=True,
        data={"sfm": sfm_result},
        message=f"Category {category_id} enabled",
    )


@router.post("/disable", response_model=APIResponse)
@limiter.limit("60/minute")
async def disable_protection_category(
    request_body: CategoryRequest,
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["id"]
    category_id = request_body.categoryId

    if category_id not in ALL_CATEGORIES:
        raise HTTPException(status_code=404, detail=f"Category {category_id} not found")

    stored = get_protection_settings(user_id)
    stored["enabledCategories"][category_id] = False
    upsert_protection_settings(
        user_id,
        stored["enabledCategories"],
        stored.get("globalLevel", 95),
    )

    sfm_result = deactivate_agents_for_category(category_id)

    return APIResponse(
        success=True,
        data={"sfm": sfm_result},
        message=f"Category {category_id} disabled",
    )


@router.get("/stats", response_model=ProtectionStatsResponse)
@limiter.limit("60/minute")
async def get_protection_stats_endpoint(
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    _ = current_user
    return ProtectionStatsResponse(
        totalThreats=0,
        blockedThreats=0,
        byCategory={category: 0 for category in ALL_CATEGORIES},
    )


@router.post("/sync", response_model=APIResponse)
@limiter.limit("60/minute")
async def sync_protection_settings_endpoint(
    settings: ProtectionSettings,
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["id"]
    upsert_protection_settings(
        user_id,
        settings.enabledCategories,
        settings.globalLevel,
    )

    for category_id, enabled in settings.enabledCategories.items():
        if category_id not in ALL_CATEGORIES:
            continue
        if enabled:
            activate_agents_for_category(category_id)
        else:
            deactivate_agents_for_category(category_id)

    return APIResponse(success=True, data=True, message="Settings synchronized successfully")
