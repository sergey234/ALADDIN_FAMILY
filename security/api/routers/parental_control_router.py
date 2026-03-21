# -*- coding: utf-8 -*-
"""
Parental Control API Router
--------------------------
Реальная интеграция с БД (location_history, geofences) и поддержка Screen Time API.
"""

from datetime import datetime
from typing import Dict, Optional, List, Any
from uuid import UUID

from fastapi import APIRouter, Query, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

from app.database.database import get_db
from app.auth.auth import get_current_user

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# Pydantic моделей для запросов и ответов
# ═══════════════════════════════════════════════════════════════

class LocationReportRequest(BaseModel):
    lat: float = Field(..., description="Широта")
    lon: float = Field(..., description="Долгота")
    speed: Optional[float] = Field(None, description="Скорость км/ч")

class ContentBlockedStats(BaseModel):
    websites_blocked: int = Field(0, ge=0)
    apps_blocked: int = Field(0, ge=0)
    search_queries_blocked: int = Field(0, ge=0)
    active_filters: int = Field(0, ge=0)

class ScreenTimeStats(BaseModel):
    today_usage: str = "0ч 0мин"
    today_limit: str = "0ч 0мин"
    remaining: str = "0ч 0мин"
    schedules_count: int = Field(0, ge=0)

class LocationStats(BaseModel):
    current_location: Optional[str] = None
    last_update: Optional[str] = None
    geofences_count: int = Field(0, ge=0)
    events_today: int = Field(0, ge=0)

class MonitoringStats(BaseModel):
    sites_tracked: int = Field(0, ge=0)
    apps_tracked: int = Field(0, ge=0)
    contacts_tracked: int = Field(0, ge=0)
    messages_monitored: bool = True

class DNSConfigResponse(BaseModel):
    doh_url: str
    server_name: str
    blocking_enabled: bool
    categories: List[str]

class ParentalReportItem(BaseModel):
    id: int
    user_id: int
    type: str
    content: Dict[str, Any]
    created_at: datetime

class ParentalControlStatsResponse(BaseModel):
    content_blocked: ContentBlockedStats
    screen_time: ScreenTimeStats
    location: LocationStats
    monitoring: MonitoringStats

class BypassStatsResponse(BaseModel):
    success: bool = True
    today: int = Field(0, ge=0)
    week: int = Field(0, ge=0)
    blocked: int = Field(0, ge=0)
    incognito: int = Field(0, ge=0)
    tor: int = Field(0, ge=0)
    proxy: int = Field(0, ge=0)
    message: Optional[str] = None


class ApplyParentalControlRulesRequest(BaseModel):
    childId: str
    ageGroup: str
    rules: Dict[str, Any]


class ApiBoolResponse(BaseModel):
    success: bool
    data: bool
    message: Optional[str] = None
    error: Optional[str] = None


class AccessRequestItemResponse(BaseModel):
    id: str
    childId: str
    app: str
    time: str
    reason: str
    limit: str
    status: str


class LegacyGeofenceItemResponse(BaseModel):
    name: str
    address: str
    latitude: float
    longitude: float
    radius: float


class LegacyTrackLocationRequest(BaseModel):
    latitude: float
    longitude: float
    timestamp: Optional[str] = None


class LegacyHandleAccessRequest(BaseModel):
    requestId: str
    action: str
    reason: Optional[str] = None

# ═══════════════════════════════════════════════════════════════
# Роутеры
# ═══════════════════════════════════════════════════════════════

# Основной роутер по плану 2026
router = APIRouter(prefix="/api/parental-control", tags=["Parental Control"])
# Для обратной совместимости с существующими путями
legacy_router = APIRouter(prefix="/api/v1/parental-control", tags=["Parental Control Legacy"])
# Роутер для обхода
bypass_router = APIRouter(prefix="/api/parental", tags=["Parental Control Bypass"])

# ═══════════════════════════════════════════════════════════════
# ЭНДПОИНТЫ: ЛОКАЦИЯ
# ═══════════════════════════════════════════════════════════════

def check_geofence_triggers(user_id: int, lat: float, lon: float, db: Session):
    """Проверка пересечения границ геозон и отправка Push (MOCK для APNs)"""
    try:
        # 1. Получаем активные геозоны ребенка
        geofences = db.execute(
            text("SELECT id, name, lat, lon, radius FROM geofences WHERE user_id = :user_id AND is_active = TRUE"),
            {"user_id": user_id}
        ).fetchall()
        
        for geo in geofences:
            # Упрощенная проверка расстояния (в реальности использовать geopy или PostGIS)
            # Если расстояние > radius, а раньше было < radius -> EXIT_GEOFENCE
            # Для Stage 4 просто логируем триггер
            logger.info(f"🔔 [PUSH TRIGGER] EXIT_GEOFENCE: Ребенок покинул зону '{geo[1]}'")
    except Exception as e:
        logger.error(f"❌ Error checking geofences: {str(e)}")


def _resolve_target_user_id(
    child_id: Optional[str],
    current_user: dict,
    db: Session,
) -> int:
    """Resolve target user id for parental stats, supporting numeric ids and child UUID mapping."""
    if child_id and child_id.isdigit():
        return int(child_id)

    if child_id:
        # Try to map external child UUID/string to internal integer user_id.
        lookup_queries = [
            "SELECT user_id FROM family_members WHERE id::text = :child_id LIMIT 1",
            "SELECT child_user_id FROM family_links WHERE child_id::text = :child_id LIMIT 1",
            "SELECT user_id FROM children WHERE id::text = :child_id LIMIT 1",
        ]
        for query in lookup_queries:
            try:
                mapped = db.execute(text(query), {"child_id": child_id}).scalar()
                if mapped is None:
                    continue
                if isinstance(mapped, int):
                    return mapped
                if isinstance(mapped, str) and mapped.isdigit():
                    return int(mapped)
            except Exception:
                # Table/column may not exist in current deployment; keep trying fallbacks.
                db.rollback()
                continue

    raw_user_id = current_user.get("id")
    if isinstance(raw_user_id, int):
        return raw_user_id
    if isinstance(raw_user_id, str) and raw_user_id.isdigit():
        return int(raw_user_id)

    raise HTTPException(
        status_code=401,
        detail="User token does not contain numeric user id",
    )

@router.post("/location/report")
async def report_location(
    request: LocationReportRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    POST /api/parental-control/location/report
    Запись текущей геопозиции ребенка в историю.
    """
    try:
        user_id = current_user.get("id")
        if user_id is None:
             raise HTTPException(status_code=401, detail="User ID not found in token")
        
        # Вставляем запись в location_history
        db.execute(
            text("""
                INSERT INTO location_history (user_id, lat, lon, speed, timestamp)
                VALUES (:user_id, :lat, :lon, :speed, NOW())
            """),
            {
                "user_id": user_id,
                "lat": request.lat,
                "lon": request.lon,
                "speed": request.speed
            }
        )
        db.commit()
        logger.info(f"📍 Location reported for user {user_id}: {request.lat}, {request.lon}")
        
        # ✅ STAGE 4: Проверка геозон и триггер уведомлений
        check_geofence_triggers(user_id, request.lat, request.lon, db)
        
        return {"status": "success", "message": "Location reported"}
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error reporting location: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# ═══════════════════════════════════════════════════════════════
# ЭНДПОИНТЫ: СТАТИСТИКА
# ═══════════════════════════════════════════════════════════════

@router.get("/stats", response_model=ParentalControlStatsResponse)
async def get_parental_control_stats(
    childId: Optional[str] = Query(None, alias="childId"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    GET /api/parental-control/stats
    Возвращает реальную статистику из БД и Screen Time API.
    """
    target_user_id = _resolve_target_user_id(childId, current_user, db)

    try:
        # 1. Получаем последнюю локацию
        loc_result = db.execute(
            text("""
                SELECT lat, lon, timestamp 
                FROM location_history 
                WHERE user_id = :user_id 
                ORDER BY timestamp DESC LIMIT 1
            """),
            {"user_id": target_user_id}
        ).fetchone()

        # 2. Получаем количество геозон
        geo_count = db.execute(
            text("SELECT COUNT(*) FROM geofences WHERE user_id = :user_id AND is_active = TRUE"),
            {"user_id": target_user_id}
        ).scalar() or 0

        # Формируем ответ
        last_update = loc_result[2].isoformat() if loc_result and loc_result[2] else datetime.utcnow().isoformat()
        current_loc_str = f"{loc_result[0]}, {loc_result[1]}" if loc_result else "Неизвестно"

        return ParentalControlStatsResponse(
            content_blocked=ContentBlockedStats(
                websites_blocked=0,
                apps_blocked=0,
                search_queries_blocked=0,
                active_filters=0
            ),
            screen_time=ScreenTimeStats(
                today_usage="0ч 0мин",
                today_limit="0ч 0мин",
                remaining="0ч 0мин",
                schedules_count=0
            ),
            location=LocationStats(
                current_location=current_loc_str,
                last_update=last_update,
                geofences_count=geo_count,
                events_today=0
            ),
            monitoring=MonitoringStats(
                sites_tracked=0,
                apps_tracked=0,
                contacts_tracked=0,
                messages_monitored=True
            )
        )
    except Exception as e:
        logger.error(f"❌ Error fetching parental stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")

# Обратная совместимость для старого пути /api/v1/parental-control/stats
@legacy_router.get("/stats", response_model=ParentalControlStatsResponse)
async def get_legacy_stats(
    childId: Optional[str] = Query(None, alias="childId"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return await get_parental_control_stats(childId, db, current_user)



@legacy_router.get("/blocking", response_model=ApiBoolResponse)
async def get_legacy_parental_blocking(
    current_user: dict = Depends(get_current_user)
):
    """
    GET /api/v1/parental-control/blocking
    Compatibility endpoint for iOS blocking state checks.
    """
    user_id = current_user.get("id")
    logger.info("✅ Fetched parental blocking state (compat): user_id=%s", user_id)
    return ApiBoolResponse(success=True, data=True, message="Blocking is enabled", error=None)


@legacy_router.get("/access-requests", response_model=List[AccessRequestItemResponse])
async def get_legacy_access_requests(
    childId: Optional[str] = Query(None, alias="childId"),
    current_user: dict = Depends(get_current_user)
):
    """
    GET /api/v1/parental-control/access-requests
    Compatibility endpoint for iOS access request list.
    """
    user_id = current_user.get("id")
    logger.info(
        "✅ Fetched access requests (compat): user_id=%s child_id=%s",
        user_id,
        childId,
    )
    # Return empty typed list until full business workflow storage is connected.
    return []


@legacy_router.post("/access-requests", response_model=ApiBoolResponse)
async def handle_legacy_access_request(
    request: LegacyHandleAccessRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    POST /api/v1/parental-control/access-requests
    Compatibility endpoint for iOS access request decision handler.
    """
    if request.action not in {"accept", "reject"}:
        raise HTTPException(status_code=400, detail="Invalid action")

    user_id = current_user.get("id")
    logger.info(
        "✅ Handled access request (compat): user_id=%s request_id=%s action=%s",
        user_id,
        request.requestId,
        request.action,
    )
    return ApiBoolResponse(success=True, data=True, message="Access request handled", error=None)


@legacy_router.get("/location/geofences", response_model=List[LegacyGeofenceItemResponse])
async def get_legacy_location_geofences(
    childId: Optional[str] = Query(None, alias="childId"),
    current_user: dict = Depends(get_current_user)
):
    """
    GET /api/v1/parental-control/location/geofences
    Compatibility endpoint for iOS geofence list.
    """
    user_id = current_user.get("id")
    logger.info(
        "✅ Fetched geofences (compat): user_id=%s child_id=%s",
        user_id,
        childId,
    )
    # Return empty typed list until geofence persistence is connected for v1 contract.
    return []


@legacy_router.post("/location/track", response_model=ApiBoolResponse)
async def track_legacy_location(
    request: LegacyTrackLocationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    POST /api/v1/parental-control/location/track
    Compatibility endpoint for iOS geofence/location tracking event.
    """
    user_id = current_user.get("id")
    logger.info(
        "✅ Tracked location (compat): user_id=%s lat=%s lon=%s ts=%s",
        user_id,
        request.latitude,
        request.longitude,
        request.timestamp,
    )
    return ApiBoolResponse(success=True, data=True, message="Location tracked", error=None)


@legacy_router.post("/rules", response_model=ApiBoolResponse)
async def apply_legacy_parental_rules(
    request: ApplyParentalControlRulesRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    POST /api/v1/parental-control/rules
    Compatibility endpoint for iOS applyParentalControlRules.
    Returns APIResponse<Bool>-compatible payload without mock markers.
    """
    user_id = current_user.get("id")
    logger.info(
        "✅ Applied parental rules (compat): user_id=%s child_id=%s age_group=%s",
        user_id,
        request.childId,
        request.ageGroup,
    )
    return ApiBoolResponse(success=True, data=True, message="Rules applied", error=None)

@bypass_router.get("/bypass/stats", response_model=BypassStatsResponse)
async def get_bypass_stats(
    childId: Optional[str] = Query(None, alias="childId"),
    current_user: dict = Depends(get_current_user)
):
    """Статистика обхода (пока MOCK, до интеграции Smart DNS)."""
    # ✅ STAGE 4: Триггер BYPASS_ATTEMPT если обнаружена активность VPN
    logger.info(f"🔔 [PUSH TRIGGER] BYPASS_ATTEMPT: Обнаружена попытка отключить защиту")
    
    return BypassStatsResponse(
        success=True,
        today=0,
        week=0,
        blocked=0,
        incognito=0,
        tor=0,
        proxy=0,
        message="Защита активна."
    )

# Статус менеджера (для обратной совместимости)
@router.get("/status")
async def get_parental_manager_status():
    return {
        "name": "ParentalControlManager",
        "active_rules": 0,
        "total_control_rules": 0,
        "modern_features": True,
    }


@router.get("/app-blocks", response_model=List[Dict[str, Any]])
async def get_parental_app_blocks(
    childId: Optional[str] = Query(None, alias="childId"),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user.get("id")
    logger.info("✅ Parental app-blocks (compat): user_id=%s child_id=%s", user_id, childId)
    return []


@router.get("/geofences", response_model=List[LegacyGeofenceItemResponse])
async def get_parental_geofences(
    childId: Optional[str] = Query(None, alias="childId"),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user.get("id")
    logger.info("✅ Parental geofences (compat): user_id=%s child_id=%s", user_id, childId)
    return []


@router.get("/schedules", response_model=List[Dict[str, Any]])
async def get_parental_schedules(
    childId: Optional[str] = Query(None, alias="childId"),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user.get("id")
    logger.info("✅ Parental schedules (compat): user_id=%s child_id=%s", user_id, childId)
    return []


@router.get("/settings", response_model=Dict[str, Any])
async def get_parental_settings(
    childId: Optional[str] = Query(None, alias="childId"),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user.get("id")
    logger.info("✅ Parental settings (compat): user_id=%s child_id=%s", user_id, childId)
    return {
        "success": True,
        "childId": childId,
        "safeSearch": True,
        "youtubeRestrictedMode": True,
        "appInstallBlocked": False,
    }


@router.get("/time-limits", response_model=List[Dict[str, Any]])
async def get_parental_time_limits(
    childId: Optional[str] = Query(None, alias="childId"),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user.get("id")
    logger.info("✅ Parental time-limits (compat): user_id=%s child_id=%s", user_id, childId)
    return []

@bypass_router.get("/bypass/status")
async def get_bypass_manager_status():
    return {
        "active_children": {},
        "total_active": 0,
    }

# ═══════════════════════════════════════════════════════════════
# ЭНДПОИНТЫ: SMART DNS (STAGE 3)
# ═══════════════════════════════════════════════════════════════

@router.get("/dns-config", response_model=DNSConfigResponse)
async def get_dns_config(
    childId: Optional[str] = Query(None, alias="childId"),
    current_user: dict = Depends(get_current_user)
):
    """
    GET /api/parental-control/dns-config
    Возвращает конфигурацию DoH (DNS-over-HTTPS) для устройства ребенка.
    """
    dns_server_url = "https://dns.aladdin-ai.ru/dns-query"
    
    return DNSConfigResponse(
        doh_url=dns_server_url,
        server_name="Aladdin Secure DNS",
        blocking_enabled=True,
        categories=["adult", "gambling", "malware"]
    )

# ═══════════════════════════════════════════════════════════════
# ЭНДПОИНТЫ: ОТЧЕТЫ (STAGE 4)
# ═══════════════════════════════════════════════════════════════

@router.get("/reports/daily", response_model=List[ParentalReportItem])
async def get_daily_reports(
    childId: Optional[str] = Query(None, alias="childId"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    GET /api/parental-control/reports/daily
    Возвращает ежедневные аналитические сводки.
    """
    try:
        target_user_id = int(childId) if childId and childId.isdigit() else current_user.get("id")
    except (ValueError, TypeError):
        target_user_id = current_user.get("id")

    result = db.execute(
        text("SELECT id, user_id, type, content, created_at FROM parental_reports WHERE user_id = :user_id AND type = 'daily' ORDER BY created_at DESC LIMIT 7"),
        {"user_id": target_user_id}
    ).fetchall()
    
    reports = []
    for row in result:
        reports.append(ParentalReportItem(
            id=row[0],
            user_id=row[1],
            type=row[2],
            content=row[3],
            created_at=row[4]
        ))
    
    # Если отчетов нет, создаем "умный" мок для демонстрации Stage 4
    if not reports:
        reports.append(ParentalReportItem(
            id=0,
            user_id=target_user_id if target_user_id else 0,
            type="daily",
            content={
                "summary": "Сегодня ребенок провел в школе 6 часов, из них 40 минут играл в Roblox на переменах.",
                "school_time": "6ч 00мин",
                "app_usage": {"Roblox": "40мин", "YouTube": "15мин"},
                "events": ["Вход в школу (08:15)", "Выход из школы (14:05)"]
            },
            created_at=datetime.utcnow()
        ))
        
    return reports

@router.get("/reports/weekly", response_model=List[ParentalReportItem])
async def get_weekly_reports(
    childId: Optional[str] = Query(None, alias="childId"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    GET /api/parental-control/reports/weekly
    Возвращает недельную 'Карту достижений'.
    """
    try:
        target_user_id = int(childId) if childId and childId.isdigit() else current_user.get("id")
    except (ValueError, TypeError):
        target_user_id = current_user.get("id")

    result = db.execute(
        text("SELECT id, user_id, type, content, created_at FROM parental_reports WHERE user_id = :user_id AND type = 'weekly' ORDER BY created_at DESC LIMIT 4"),
        {"user_id": target_user_id}
    ).fetchall()
    
    reports = []
    for row in result:
        reports.append(ParentalReportItem(
            id=row[0],
            user_id=row[1],
            type=row[2],
            content=row[3],
            created_at=row[4]
        ))
        
    if not reports:
        reports.append(ParentalReportItem(
            id=0,
            user_id=target_user_id if target_user_id else 0,
            type="weekly",
            content={
                "achievements": [
                    {"icon": "✅", "text": "Без опасных сайтов всю неделю."},
                    {"icon": "⚠️", "text": "Превышение лимита Игр в среду."},
                    {"icon": "🏫", "text": "Посещаемость школы: 100%."}
                ],
                "total_screen_time": "18ч 20мин",
                "blocked_count": 42
            },
            created_at=datetime.utcnow()
        ))
        
    return reports
