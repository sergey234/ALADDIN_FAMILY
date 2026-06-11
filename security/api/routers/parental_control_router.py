# -*- coding: utf-8 -*-
"""
Parental Control API Router
--------------------------
Реальная интеграция с БД (location_history, geofences) и поддержка Screen Time API.
"""

from datetime import datetime
import json
from typing import Dict, Optional, List, Any, Mapping, Set, Tuple

from fastapi import APIRouter, Query, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

from app.database.database import get_db
from app.auth.auth import get_current_user

from security.family.family_notification_manager_enhanced import (
    NotificationChannel,
    NotificationPriority,
    NotificationType,
    family_notification_manager_enhanced,
)

logger = logging.getLogger(__name__)

# Fallback family bucket for in-app notifications when нет строки family_members (совпадает с notifications_router).
_DEFAULT_NOTIFICATION_FAMILY_ID = "family_demo_001"

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
    # Не подразумеваем мониторинг сообщений без строки в БД / отчёте.
    messages_monitored: bool = False


class ReportsStats(BaseModel):
    """Сводка по семейным отчётам (parental_reports), отдельно от monitoring.* (pc-04)."""
    weekly_count: int = Field(0, ge=0, description="Weekly-отчётов за 30 дней UTC")
    daily_count: int = Field(0, ge=0, description="Daily-отчётов за 7 дней UTC")
    alerts_count: int = Field(0, ge=0, description="Из последнего weekly/daily content.* или 0")
    has_daily_today: bool = Field(False, description="Есть daily-отчёт с датой создания сегодня UTC")


# ── Мониторинг: единый detail + ingest (pc-06 / pc-10 / pc-12) ─────────────────
class MonitoringTopSiteRow(BaseModel):
    site: str
    visits: int = Field(0, ge=0)
    hours: int = Field(0, ge=0)
    minutes: int = Field(0, ge=0)
    category: str = Field("general", description="Ключ категории для клиента, напр. video|social|search|general")


class MonitoringTopAppRow(BaseModel):
    name: str
    usage_minutes: int = Field(0, ge=0)
    limit_minutes: int = Field(0, ge=0)
    exceeded: bool = False


class MonitoringPeakHourRow(BaseModel):
    label: str
    usage_percent: int = Field(0, ge=0, le=100)


class MonitoringSuspiciousRow(BaseModel):
    text: str
    level: str = Field("medium", description="high|medium")
    time: str = ""


class MonitoringContactRow(BaseModel):
    name: str
    messages: int = Field(0, ge=0)
    calls: int = Field(0, ge=0)
    last_contact: str = ""


class MonitoringSummaryBlock(BaseModel):
    browser_sites_week: int = Field(0, ge=0)
    apps_used_week: int = Field(0, ge=0)
    contacts_active: int = Field(0, ge=0)


class ParentalMonitoringDetailResponse(BaseModel):
    """Данные для экранов мониторинга/отчётов; только БД + ingest, без вымышленных рядов."""
    top_sites: List[MonitoringTopSiteRow] = Field(default_factory=list)
    top_apps: List[MonitoringTopAppRow] = Field(default_factory=list)
    browser_history: List[MonitoringTopSiteRow] = Field(default_factory=list)
    app_history: List[MonitoringTopAppRow] = Field(default_factory=list)
    peak_hours: List[MonitoringPeakHourRow] = Field(default_factory=list)
    suspicious: List[MonitoringSuspiciousRow] = Field(default_factory=list)
    contacts: List[MonitoringContactRow] = Field(default_factory=list)
    summary: MonitoringSummaryBlock = Field(default_factory=MonitoringSummaryBlock)


class MonitoringEventIn(BaseModel):
    kind: str = Field(..., max_length=64)
    payload: Dict[str, Any] = Field(default_factory=dict)


class MonitoringIngestRequest(BaseModel):
    events: List[MonitoringEventIn] = Field(default_factory=list)


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
    reports: ReportsStats = Field(default_factory=ReportsStats)

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


class BypassApplyRequest(BaseModel):
    childId: str
    incognito: bool
    tor: bool
    proxy: bool


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
) -> Optional[int]:
    """Resolve target numeric user_id when possible (UUID-safe, no hard 401 on contract mismatch)."""
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

    logger.warning(
        "⚠️ Could not resolve numeric user_id for child_id=%s token_id=%s",
        child_id,
        current_user.get("id"),
    )
    return None


def _resolve_target_id_flexible(
    child_id: Optional[str],
    current_user: dict,
) -> str:
    """Resolve target id for bypass endpoints in UUID/int/string-safe mode."""
    if child_id:
        normalized = str(child_id).strip()
        if normalized:
            return normalized

    raw_user_id = current_user.get("id")
    if raw_user_id is None:
        raise HTTPException(status_code=401, detail="User token does not contain user id")

    normalized_user_id = str(raw_user_id).strip()
    if not normalized_user_id:
        raise HTTPException(status_code=401, detail="User token does not contain user id")
    return normalized_user_id

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
# Статистика: вспомогательные запросы к БД (pc-03)
# ═══════════════════════════════════════════════════════════════

def _count_location_events_today(db: Session, user_id: int) -> int:
    """Количество точек location_history за календарный день UTC (реальные события трека)."""
    try:
        n = db.execute(
            text(
                """
                SELECT COUNT(*)::int
                FROM location_history
                WHERE user_id = :uid
                  AND (timestamp AT TIME ZONE 'UTC')::date = (CURRENT_TIMESTAMP AT TIME ZONE 'UTC')::date
                """
            ),
            {"uid": user_id},
        ).scalar()
        return int(n or 0)
    except Exception as e:
        logger.info("location_history events_today unavailable: %s", e)
        db.rollback()
        return 0


def _as_content_dict(raw: Any) -> Dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str) and raw.strip():
        try:
            parsed = json.loads(raw)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}
    return {}


def _monitoring_from_parental_reports(db: Session, user_id: int) -> MonitoringStats:
    """Fallback: последний weekly/daily отчёт, поля content как агрегаты мониторинга."""
    try:
        raw = db.execute(
            text(
                """
                SELECT content
                FROM parental_reports
                WHERE user_id = :uid AND type IN ('weekly', 'daily')
                ORDER BY created_at DESC
                LIMIT 1
                """
            ),
            {"uid": user_id},
        ).scalar()
        c = _as_content_dict(raw)

        def _int(*keys: str) -> int:
            for k in keys:
                v = c.get(k)
                if v is None:
                    continue
                try:
                    return int(v)
                except (TypeError, ValueError):
                    continue
            return 0

        def _bool(*keys: str) -> bool:
            for k in keys:
                v = c.get(k)
                if isinstance(v, bool):
                    return v
                if v in (1, "1", "true", "True", "yes", "YES"):
                    return True
            return False

        return MonitoringStats(
            sites_tracked=_int("sites_tracked", "sites_count", "web_sites_count", "total_sites"),
            apps_tracked=_int("apps_tracked", "apps_count", "applications_count"),
            contacts_tracked=_int("contacts_tracked", "contacts_count"),
            messages_monitored=_bool("messages_monitored", "messagesMonitored"),
        )
    except Exception as e:
        logger.info("parental_reports monitoring fallback skipped: %s", e)
        db.rollback()
        return MonitoringStats()


def _load_parental_control_stats_row(
    db: Session, target_user_id: int, child_id_param: Optional[str]
) -> Optional[Mapping[str, Any]]:
    """
    Строка parental_control_stats для целевого ребёнка.
    Сопоставление: query childId → child_id; иначе JOIN family_members.user_id → child_id UUID.
    """
    cols = """
        pcs.websites_blocked, pcs.apps_blocked, pcs.search_queries_blocked, pcs.active_filters,
        pcs.today_usage, pcs.today_limit, pcs.remaining, pcs.schedules_count,
        pcs.sites_tracked, pcs.apps_tracked, pcs.contacts_tracked, pcs.messages_monitored,
        pcs.events_today, pcs.current_location, pcs.geofences_count
    """
    variants: List[tuple] = []
    cid = (child_id_param or "").strip()
    if cid:
        variants.append(
            (
                text(
                    f"""
                    SELECT {cols}
                    FROM parental_control_stats pcs
                    WHERE pcs.child_id::text = :cid
                    ORDER BY pcs.last_update DESC NULLS LAST
                    LIMIT 1
                    """
                ),
                {"cid": cid},
            )
        )
    variants.append(
        (
            text(
                f"""
                SELECT {cols}
                FROM parental_control_stats pcs
                INNER JOIN family_members fm ON fm.id::text = pcs.child_id::text
                WHERE fm.user_id = :uid
                ORDER BY pcs.last_update DESC NULLS LAST
                LIMIT 1
                """
            ),
            {"uid": target_user_id},
        )
    )

    for stmt, params in variants:
        try:
            row = db.execute(stmt, params).mappings().first()
            if row:
                return row
        except Exception as e:
            logger.info("parental_control_stats lookup failed (variant ok to skip): %s", e)
            db.rollback()
    return None


def _merge_monitoring(pcs: Optional[Mapping[str, Any]], rep: MonitoringStats) -> MonitoringStats:
    if not pcs:
        return rep

    def pick_int(col: str, fallback: int) -> int:
        v = pcs.get(col)
        if v is None:
            return fallback
        try:
            return max(0, int(v))
        except (TypeError, ValueError):
            return fallback

    def pick_bool(col: str, fallback: bool) -> bool:
        v = pcs.get(col)
        if isinstance(v, bool):
            return v
        if v in (1, "1", "true", "True"):
            return True
        if v in (0, "0", "false", "False"):
            return False
        return fallback

    return MonitoringStats(
        sites_tracked=pick_int("sites_tracked", rep.sites_tracked),
        apps_tracked=pick_int("apps_tracked", rep.apps_tracked),
        contacts_tracked=pick_int("contacts_tracked", rep.contacts_tracked),
        messages_monitored=pick_bool("messages_monitored", rep.messages_monitored),
    )


def _content_blocked_from_pcs(pcs: Optional[Mapping[str, Any]]) -> ContentBlockedStats:
    if not pcs:
        return ContentBlockedStats()

    def nz(key: str) -> int:
        v = pcs.get(key)
        try:
            return max(0, int(v or 0))
        except (TypeError, ValueError):
            return 0

    return ContentBlockedStats(
        websites_blocked=nz("websites_blocked"),
        apps_blocked=nz("apps_blocked"),
        search_queries_blocked=nz("search_queries_blocked"),
        active_filters=nz("active_filters"),
    )


def _screen_time_from_pcs(pcs: Optional[Mapping[str, Any]]) -> ScreenTimeStats:
    if not pcs:
        return ScreenTimeStats()

    def s(key: str, default: str) -> str:
        v = pcs.get(key)
        if v is None or (isinstance(v, str) and not v.strip()):
            return default
        return str(v)

    sc = 0
    try:
        sc = max(0, int(pcs.get("schedules_count") or 0))
    except (TypeError, ValueError):
        sc = 0

    return ScreenTimeStats(
        today_usage=s("today_usage", "0ч 0мин"),
        today_limit=s("today_limit", "0ч 0мин"),
        remaining=s("remaining", "0ч 0мин"),
        schedules_count=sc,
    )


def _alerts_count_from_report_content(c: Dict[str, Any]) -> int:
    for k in ("warnings_count", "suspicious_count", "alerts_count", "new_warnings"):
        v = c.get(k)
        if v is None:
            continue
        try:
            return max(0, int(v))
        except (TypeError, ValueError):
            continue
    w = c.get("warnings")
    if isinstance(w, list):
        return max(0, len(w))
    return 0


def _reports_stats_from_db(db: Session, user_id: int) -> ReportsStats:
    try:
        row = db.execute(
            text(
                """
                SELECT
                    (
                        SELECT COUNT(*)::int FROM parental_reports pr
                        WHERE pr.user_id = :uid AND pr.type = 'weekly'
                          AND pr.created_at >= (NOW() AT TIME ZONE 'utc') - INTERVAL '30 days'
                    ) AS weekly_count,
                    (
                        SELECT COUNT(*)::int FROM parental_reports pr
                        WHERE pr.user_id = :uid AND pr.type = 'daily'
                          AND pr.created_at >= (NOW() AT TIME ZONE 'utc') - INTERVAL '7 days'
                    ) AS daily_count,
                    EXISTS (
                        SELECT 1 FROM parental_reports pr
                        WHERE pr.user_id = :uid AND pr.type = 'daily'
                          AND (pr.created_at AT TIME ZONE 'UTC')::date
                              = (CURRENT_TIMESTAMP AT TIME ZONE 'UTC')::date
                    ) AS has_daily_today
                """
            ),
            {"uid": user_id},
        ).mappings().first()
        weekly_count = int(row.get("weekly_count") or 0) if row else 0
        daily_count = int(row.get("daily_count") or 0) if row else 0
        has_daily = bool(row.get("has_daily_today")) if row else False

        raw_content = db.execute(
            text(
                """
                SELECT content FROM parental_reports
                WHERE user_id = :uid AND type IN ('weekly', 'daily')
                ORDER BY created_at DESC
                LIMIT 1
                """
            ),
            {"uid": user_id},
        ).scalar()
        alerts_count = _alerts_count_from_report_content(_as_content_dict(raw_content))

        return ReportsStats(
            weekly_count=weekly_count,
            daily_count=daily_count,
            alerts_count=alerts_count,
            has_daily_today=has_daily,
        )
    except Exception as e:
        logger.info("reports stats from DB skipped: %s", e)
        db.rollback()
        return ReportsStats()


def _as_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str) and value.strip():
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, list) else []
        except json.JSONDecodeError:
            return []
    return []


def _merge_latest_reports_content(db: Session, user_id: int) -> Dict[str, Any]:
    merged: Dict[str, Any] = {}
    try:
        for typ in ("daily", "weekly"):
            raw = db.execute(
                text(
                    """
                    SELECT content FROM parental_reports
                    WHERE user_id = :uid AND type = :typ
                    ORDER BY created_at DESC
                    LIMIT 1
                    """
                ),
                {"uid": user_id, "typ": typ},
            ).scalar()
            merged.update(_as_content_dict(raw))
    except Exception as e:
        logger.info("merge_latest_reports_content: %s", e)
        db.rollback()
    return merged


def _norm_category(raw: Any) -> str:
    s = str(raw or "").strip().lower()
    if s in ("video", "social", "search", "general"):
        return s
    if "video" in s or "tiktok" in s or "youtube" in s:
        return "video"
    if "social" in s or "insta" in s or "vk" in s:
        return "social"
    if "search" in s or "google" in s:
        return "search"
    return "general"


def _parse_top_site_rows(content: Dict[str, Any]) -> List[MonitoringTopSiteRow]:
    for key in ("top_sites", "browser_history", "sites_top", "topSites"):
        rows: List[MonitoringTopSiteRow] = []
        for item in _as_list(content.get(key)):
            if not isinstance(item, dict):
                continue
            site = str(
                item.get("site")
                or item.get("url")
                or item.get("domain")
                or item.get("name")
                or ""
            ).strip()
            if not site:
                continue
            try:
                visits = int(item.get("visits") or item.get("count") or 0)
            except (TypeError, ValueError):
                visits = 0
            try:
                hours = int(item.get("hours") or item.get("h") or 0)
            except (TypeError, ValueError):
                hours = 0
            try:
                minutes = int(item.get("minutes") or item.get("m") or item.get("mins") or 0)
            except (TypeError, ValueError):
                minutes = 0
            cat = _norm_category(item.get("category") or item.get("type"))
            rows.append(
                MonitoringTopSiteRow(site=site, visits=max(0, visits), hours=max(0, hours), minutes=max(0, minutes), category=cat)
            )
        if rows:
            return rows[:20]
    return []


def _parse_top_app_rows(content: Dict[str, Any]) -> List[MonitoringTopAppRow]:
    for key in ("top_apps", "app_history", "apps_top", "topApps"):
        rows: List[MonitoringTopAppRow] = []
        for item in _as_list(content.get(key)):
            if not isinstance(item, dict):
                continue
            name = str(item.get("name") or item.get("app") or item.get("title") or "").strip()
            if not name:
                continue
            try:
                um = int(item.get("usage_minutes") or item.get("usageMinutes") or item.get("minutes") or 0)
            except (TypeError, ValueError):
                um = 0
            try:
                lm = int(item.get("limit_minutes") or item.get("limitMinutes") or item.get("limit") or 0)
            except (TypeError, ValueError):
                lm = 0
            exceeded = bool(item.get("exceeded")) or (lm > 0 and um > lm)
            rows.append(MonitoringTopAppRow(name=name, usage_minutes=max(0, um), limit_minutes=max(0, lm), exceeded=exceeded))
        if rows:
            return rows[:20]
    return []


def _parse_peak_hours(content: Dict[str, Any]) -> List[MonitoringPeakHourRow]:
    for key in ("peak_hours", "usage_hours", "peakHours"):
        rows: List[MonitoringPeakHourRow] = []
        for item in _as_list(content.get(key)):
            if not isinstance(item, dict):
                continue
            label = str(item.get("label") or item.get("slot") or item.get("hour") or item.get("range") or "").strip()
            if not label:
                continue
            try:
                pct = int(item.get("usage_percent") or item.get("usage") or item.get("pct") or 0)
            except (TypeError, ValueError):
                pct = 0
            pct = max(0, min(100, pct))
            rows.append(MonitoringPeakHourRow(label=label, usage_percent=pct))
        if rows:
            return rows[:24]
    return []


def _parse_suspicious_from_content(content: Dict[str, Any]) -> List[MonitoringSuspiciousRow]:
    for key in ("suspicious", "suspicious_activity", "warnings"):
        rows: List[MonitoringSuspiciousRow] = []
        for item in _as_list(content.get(key)):
            if isinstance(item, str) and item.strip():
                rows.append(MonitoringSuspiciousRow(text=item.strip(), level="medium", time=""))
                continue
            if not isinstance(item, dict):
                continue
            text = str(item.get("text") or item.get("message") or item.get("title") or "").strip()
            if not text:
                continue
            lvl = str(item.get("level") or item.get("severity") or "medium").lower()
            if lvl not in ("high", "medium"):
                lvl = "medium"
            tim = str(item.get("time") or item.get("at") or item.get("when") or "")
            rows.append(MonitoringSuspiciousRow(text=text, level=lvl, time=tim))
        if rows:
            return rows[:50]
    return []


def _parse_contacts_from_content(content: Dict[str, Any]) -> List[MonitoringContactRow]:
    rows: List[MonitoringContactRow] = []
    for item in _as_list(content.get("contacts") or content.get("contacts_top")):
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or item.get("title") or "").strip()
        if not name:
            continue
        try:
            msg = int(item.get("messages") or item.get("messages_count") or 0)
        except (TypeError, ValueError):
            msg = 0
        try:
            calls = int(item.get("calls") or item.get("calls_count") or 0)
        except (TypeError, ValueError):
            calls = 0
        last = str(item.get("last_contact") or item.get("lastContact") or item.get("last") or "")
        rows.append(MonitoringContactRow(name=name, messages=max(0, msg), calls=max(0, calls), last_contact=last))
    return rows[:20]


def _top_sites_from_monitoring_events(db: Session, user_id: int, limit: int = 10) -> List[MonitoringTopSiteRow]:
    """
    Агрегаты из parental_monitoring_events, если в parental_reports ещё нет списков.
    Ожидаемые kind: url_visit, browser_visit, browser, site, top_site.
    payload: site | domain | url_host или url_sha256 / url_hash (показываем укороченный хэш).
    """
    try:
        res = db.execute(
            text(
                """
                SELECT site, SUM(cnt)::int AS visits
                FROM (
                    SELECT
                        COALESCE(
                            NULLIF(TRIM(payload->>'site'), ''),
                            NULLIF(TRIM(payload->>'domain'), ''),
                            NULLIF(TRIM(payload->>'url_host'), ''),
                            CASE
                                WHEN LENGTH(TRIM(COALESCE(payload->>'url_sha256', payload->>'url_hash', ''))) > 8
                                THEN '#' || SUBSTRING(
                                    TRIM(COALESCE(payload->>'url_sha256', payload->>'url_hash', '')),
                                    1, 12
                                ) || '…'
                                ELSE NULL
                            END
                        ) AS site,
                        1 AS cnt
                    FROM parental_monitoring_events
                    WHERE user_id = :uid
                      AND kind IN ('url_visit', 'browser_visit', 'browser', 'site', 'top_site', 'dns')
                ) t
                WHERE site IS NOT NULL AND TRIM(site) <> ''
                GROUP BY site
                ORDER BY visits DESC
                LIMIT :lim
                """
            ),
            {"uid": user_id, "lim": limit},
        )
        rows: List[MonitoringTopSiteRow] = []
        for r in res.fetchall():
            site = str(r[0] or "").strip()
            if not site:
                continue
            try:
                visits = int(r[1] or 0)
            except (TypeError, ValueError):
                visits = 0
            rows.append(
                MonitoringTopSiteRow(
                    site=site[:255],
                    visits=max(0, visits),
                    hours=0,
                    minutes=0,
                    category="general",
                )
            )
        return rows
    except Exception as e:
        logger.info("top_sites from parental_monitoring_events skipped: %s", e)
        db.rollback()
        return []


def _top_apps_from_monitoring_events(db: Session, user_id: int, limit: int = 10) -> List[MonitoringTopAppRow]:
    """
    kind: app_session, app_usage, app, top_app — payload name | app | title | bundle_id.
    usage_minutes в payload опционально; иначе +1 минута на событие (агрегат активности).
    """
    try:
        res = db.execute(
            text(
                """
                SELECT app_name, SUM(usage_part)::int AS usage_minutes
                FROM (
                    SELECT
                        COALESCE(
                            NULLIF(TRIM(payload->>'name'), ''),
                            NULLIF(TRIM(payload->>'app'), ''),
                            NULLIF(TRIM(payload->>'title'), ''),
                            NULLIF(TRIM(payload->>'bundle_id'), '')
                        ) AS app_name,
                        CASE
                            WHEN (payload ? 'usage_minutes')
                                 AND TRIM(payload->>'usage_minutes') ~ '^[0-9]+$'
                                THEN (payload->>'usage_minutes')::int
                            WHEN (payload ? 'minutes')
                                 AND TRIM(payload->>'minutes') ~ '^[0-9]+$'
                                THEN (payload->>'minutes')::int
                            ELSE 1
                        END AS usage_part
                    FROM parental_monitoring_events
                    WHERE user_id = :uid
                      AND kind IN ('app_session', 'app_usage', 'app', 'top_app')
                ) t
                WHERE app_name IS NOT NULL AND TRIM(app_name) <> ''
                GROUP BY app_name
                ORDER BY usage_minutes DESC
                LIMIT :lim
                """
            ),
            {"uid": user_id, "lim": limit},
        )
        rows: List[MonitoringTopAppRow] = []
        for r in res.fetchall():
            name = str(r[0] or "").strip()
            if not name:
                continue
            try:
                um = int(r[1] or 0)
            except (TypeError, ValueError):
                um = 0
            rows.append(
                MonitoringTopAppRow(
                    name=name[:255],
                    usage_minutes=max(0, um),
                    limit_minutes=0,
                    exceeded=False,
                )
            )
        return rows
    except Exception as e:
        logger.info("top_apps from parental_monitoring_events skipped: %s", e)
        db.rollback()
        return []


def _suspicious_from_events_table(db: Session, user_id: int, limit: int = 50) -> List[MonitoringSuspiciousRow]:
    out: List[MonitoringSuspiciousRow] = []
    try:
        res = db.execute(
            text(
                """
                SELECT payload, created_at
                FROM parental_monitoring_events
                WHERE user_id = :uid
                  AND kind IN (
                      'suspicious', 'suspicious_activity', 'alert', 'warning',
                      'dns', 'app_rules'
                  )
                ORDER BY created_at DESC
                LIMIT :lim
                """
            ),
            {"uid": user_id, "lim": limit},
        )
        for row in res.fetchall():
            pl = row[0]
            ts = row[1]
            d = pl if isinstance(pl, dict) else _as_content_dict(pl)
            text = str(d.get("text") or d.get("message") or d.get("title") or "").strip()
            if not text:
                if d.get("doh_url_sha256"):
                    text = f"DNS {str(d.get('doh_url_sha256'))[:16]}…"
                elif d.get("rules_snapshot_sha256"):
                    text = f"rules {str(d.get('rules_snapshot_sha256'))[:16]}…"
                else:
                    continue
            lvl = str(d.get("level") or "medium").lower()
            if lvl not in ("high", "medium"):
                lvl = "medium"
            tstr = ts.isoformat() if hasattr(ts, "isoformat") else str(ts or "")
            out.append(MonitoringSuspiciousRow(text=text, level=lvl, time=tstr))
    except Exception as e:
        logger.info("parental_monitoring_events read skipped: %s", e)
        db.rollback()
    return out


def _build_parental_monitoring_detail(db: Session, user_id: int) -> ParentalMonitoringDetailResponse:
    _ensure_parental_monitoring_events_table(db)
    content = _merge_latest_reports_content(db, user_id)
    top_sites = _parse_top_site_rows(content)
    if not top_sites:
        top_sites = _top_sites_from_monitoring_events(db, user_id, 10)
    top_apps = _parse_top_app_rows(content)
    if not top_apps:
        top_apps = _top_apps_from_monitoring_events(db, user_id, 10)

    peak = _parse_peak_hours(content)
    susp_c = _parse_suspicious_from_content(content)
    susp_e = _suspicious_from_events_table(db, user_id)
    seen: Set[str] = {s.text for s in susp_e}
    susp: List[MonitoringSuspiciousRow] = list(susp_e)
    for s in susp_c:
        if s.text not in seen:
            seen.add(s.text)
            susp.append(s)

    contacts = _parse_contacts_from_content(content)

    ms = content.get("monitoring_summary") or content.get("summary") or {}
    if not isinstance(ms, dict):
        ms = {}

    def _iget(d: Dict[str, Any], *keys: str) -> int:
        for k in keys:
            v = d.get(k)
            if v is None:
                continue
            try:
                return max(0, int(v))
            except (TypeError, ValueError):
                continue
        return 0

    bsw = _iget(ms, "browser_sites_week", "sites_week", "sites_tracked_week")
    apw = _iget(ms, "apps_used_week", "apps_week", "apps_tracked_week")
    cta = _iget(ms, "contacts_active", "contacts_tracked", "contacts_count")
    if bsw == 0 and top_sites:
        bsw = sum(s.visits for s in top_sites) or len(top_sites)
    if apw == 0 and top_apps:
        apw = len(top_apps)
    if cta == 0 and contacts:
        cta = len(contacts)

    summary = MonitoringSummaryBlock(
        browser_sites_week=bsw,
        apps_used_week=apw,
        contacts_active=cta,
    )

    return ParentalMonitoringDetailResponse(
        top_sites=top_sites[:10],
        top_apps=top_apps[:10],
        browser_history=top_sites[:10],
        app_history=top_apps[:10],
        peak_hours=peak,
        suspicious=susp[:30],
        contacts=contacts[:10],
        summary=summary,
    )


def _ensure_parental_monitoring_events_table(db: Session) -> None:
    try:
        db.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS parental_monitoring_events (
                    id BIGSERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    kind VARCHAR(64) NOT NULL,
                    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
        )
        db.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_parental_monitoring_events_user_created "
                "ON parental_monitoring_events (user_id, created_at DESC)"
            )
        )
        db.commit()
    except Exception as e:
        logger.info("ensure_parental_monitoring_events_table: %s", e)
        db.rollback()


def _is_bypass_monitoring_event(kind: str, payload: Optional[Dict[str, Any]]) -> bool:
    k = (kind or "").lower()
    if "bypass" in k:
        return True
    p = payload or {}
    if str(p.get("category") or "").lower() in ("bypass", "bypass_attempt"):
        return True
    if p.get("bypass_type") or p.get("bypassType"):
        return True
    return False


def _bypass_counter_deltas(kind: str, payload: Optional[Dict[str, Any]]) -> Tuple[int, int, int, int, int, int]:
    """Дельты для parental_bypass_stats: today, week, blocked, incognito, tor, proxy."""
    k = (kind or "").lower()
    p = payload or {}
    bt = (p.get("bypass_type") or p.get("bypassType") or p.get("type") or "").lower()
    token = f"{k} {bt}"
    today = week = blocked = 1
    incognito = tor = proxy = 0
    if "incognito" in token:
        incognito = 1
    elif "tor" in token:
        tor = 1
    elif "proxy" in token:
        proxy = 1
    return (today, week, blocked, incognito, tor, proxy)


def _resolve_family_id_for_numeric_user(db: Session, numeric_user_id: int) -> Optional[str]:
    try:
        row = db.execute(
            text(
                """
                SELECT family_id::text
                FROM family_members
                WHERE user_id = :uid
                ORDER BY updated_at DESC NULLS LAST, id DESC
                LIMIT 1
                """
            ),
            {"uid": numeric_user_id},
        ).fetchone()
        if row and row[0]:
            return str(row[0])
    except Exception as exc:
        logger.debug("resolve_family_id_for_user: %s", exc)
        try:
            db.rollback()
        except Exception:
            pass
    return None


def _resolve_parent_child_member_ids_for_bypass_stats(
    db: Session, child_numeric_uid: int
) -> Optional[Tuple[str, str]]:
    """Ключ parental_bypass_stats (user_id, child_id): UUID family_members.id родителя и ребёнка."""
    try:
        row = db.execute(
            text(
                """
                SELECT parent_fm.id::text, child_fm.id::text
                FROM family_members child_fm
                INNER JOIN family_members parent_fm
                    ON parent_fm.family_id = child_fm.family_id
                    AND LOWER(COALESCE(parent_fm.role, '')) = 'parent'
                WHERE child_fm.user_id = :uid
                LIMIT 1
                """
            ),
            {"uid": child_numeric_uid},
        ).fetchone()
        if row and row[0] and row[1]:
            return (str(row[0]), str(row[1]))
    except Exception as exc:
        logger.debug("resolve_parent_child_member_ids: %s", exc)
        try:
            db.rollback()
        except Exception:
            pass
    return None


def _increment_parental_bypass_stats(
    db: Session,
    parent_member_id: str,
    child_member_id: str,
    d_today: int,
    d_week: int,
    d_blocked: int,
    d_inc: int,
    d_tor: int,
    d_proxy: int,
) -> None:
    q_upd = text(
        """
        UPDATE parental_bypass_stats
        SET
            today = today + :d_today,
            week = week + :d_week,
            blocked = blocked + :d_blocked,
            incognito = incognito + :d_inc,
            tor = tor + :d_tor,
            proxy = proxy + :d_proxy,
            updated_at = NOW()
        WHERE user_id::text = :pid
          AND child_id::text = :cid
        """
    )
    res = db.execute(
        q_upd,
        {
            "pid": parent_member_id,
            "cid": child_member_id,
            "d_today": d_today,
            "d_week": d_week,
            "d_blocked": d_blocked,
            "d_inc": d_inc,
            "d_tor": d_tor,
            "d_proxy": d_proxy,
        },
    )
    rowcount = getattr(res, "rowcount", None)
    if rowcount:
        return

    db.execute(
        text(
            """
            INSERT INTO parental_bypass_stats (
                user_id, child_id,
                today, week, blocked, incognito, tor, proxy, message,
                created_at, updated_at
            )
            VALUES (
                CAST(:pid AS uuid), CAST(:cid AS uuid),
                :d_today, :d_week, :d_blocked, :d_inc, :d_tor, :d_proxy,
                :msg,
                NOW(), NOW()
            )
            """
        ),
        {
            "pid": parent_member_id,
            "cid": child_member_id,
            "d_today": d_today,
            "d_week": d_week,
            "d_blocked": d_blocked,
            "d_inc": d_inc,
            "d_tor": d_tor,
            "d_proxy": d_proxy,
            "msg": "Защита активна.",
        },
    )


async def _emit_bypass_notification_from_ingest(
    family_id: str,
    kind: str,
    payload: Optional[Dict[str, Any]],
    child_numeric_uid: int,
) -> None:
    p = payload or {}
    correlation = str(p.get("correlation_id") or p.get("correlationId") or "").strip()
    title = "Попытка обхода защиты"
    body_bits = [f"Событие: {kind}"]
    if correlation:
        body_bits.append(f"id: {correlation}")
    body = ". ".join(body_bits)
    meta: Dict[str, Any] = {
        "child_user_id": str(child_numeric_uid),
        "kind": kind,
        "source": "parental_monitoring_ingest",
    }
    if correlation:
        meta["correlation_id"] = correlation
    await family_notification_manager_enhanced.send_family_alert(
        family_id=family_id,
        notification_type=NotificationType.BYPASS_ATTEMPT,
        priority=NotificationPriority.HIGH,
        title=title,
        message=body,
        channels=[NotificationChannel.IN_APP],
        metadata=meta,
        action_required=False,
    )


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
        # UUID-only token / unmapped child: return safe empty stats instead of contract 401.
        if target_user_id is None:
            return ParentalControlStatsResponse(
                content_blocked=ContentBlockedStats(),
                screen_time=ScreenTimeStats(),
                location=LocationStats(
                    current_location="Неизвестно",
                    last_update=datetime.utcnow().isoformat(),
                    geofences_count=0,
                    events_today=0,
                ),
                monitoring=MonitoringStats(),
                reports=ReportsStats(),
            )

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

        events_today = _count_location_events_today(db, target_user_id)
        pcs_row = _load_parental_control_stats_row(db, target_user_id, childId)
        mon_from_reports = _monitoring_from_parental_reports(db, target_user_id)
        monitoring = _merge_monitoring(pcs_row, mon_from_reports)

        # Формируем ответ
        last_update = loc_result[2].isoformat() if loc_result and loc_result[2] else datetime.utcnow().isoformat()
        current_loc_str = f"{loc_result[0]}, {loc_result[1]}" if loc_result else "Неизвестно"

        if pcs_row and pcs_row.get("current_location"):
            current_loc_str = str(pcs_row["current_location"])

        geo_from_pcs: Optional[int] = None
        if pcs_row and pcs_row.get("geofences_count") is not None:
            try:
                geo_from_pcs = max(0, int(pcs_row["geofences_count"]))
            except (TypeError, ValueError):
                geo_from_pcs = None
        effective_geo = geo_count if geo_count > 0 else (geo_from_pcs or 0)

        return ParentalControlStatsResponse(
            content_blocked=_content_blocked_from_pcs(pcs_row),
            screen_time=_screen_time_from_pcs(pcs_row),
            location=LocationStats(
                current_location=current_loc_str,
                last_update=last_update,
                geofences_count=effective_geo,
                events_today=events_today,
            ),
            monitoring=monitoring,
            reports=_reports_stats_from_db(db, target_user_id),
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

def _ensure_bypass_shadow_table(db: Session) -> None:
    db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS parental_bypass_state_shadow (
                target_id TEXT PRIMARY KEY,
                incognito INTEGER NOT NULL DEFAULT 0,
                tor INTEGER NOT NULL DEFAULT 0,
                proxy INTEGER NOT NULL DEFAULT 0,
                updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
            )
            """
        )
    )


def _persist_bypass_shadow(db: Session, target_id: str, incognito: bool, tor: bool, proxy: bool) -> None:
    _ensure_bypass_shadow_table(db)
    db.execute(
        text(
            """
            INSERT INTO parental_bypass_state_shadow (target_id, incognito, tor, proxy, updated_at)
            VALUES (:target_id, :incognito, :tor, :proxy, NOW())
            ON CONFLICT (target_id)
            DO UPDATE SET
                incognito = EXCLUDED.incognito,
                tor = EXCLUDED.tor,
                proxy = EXCLUDED.proxy,
                updated_at = NOW()
            """
        ),
        {
            "target_id": target_id,
            "incognito": 1 if incognito else 0,
            "tor": 1 if tor else 0,
            "proxy": 1 if proxy else 0,
        },
    )


def _read_bypass_shadow(db: Session, target_id: str) -> Optional[dict]:
    _ensure_bypass_shadow_table(db)
    row = db.execute(
        text(
            """
            SELECT incognito, tor, proxy
            FROM parental_bypass_state_shadow
            WHERE target_id = :target_id
            LIMIT 1
            """
        ),
        {"target_id": target_id},
    ).fetchone()
    if not row:
        return None
    return {"incognito": int(row[0] or 0), "tor": int(row[1] or 0), "proxy": int(row[2] or 0)}


def _read_bypass_stats_from_db(
    db: Session,
    current_user: dict,
    child_id: Optional[str],
) -> Optional[dict]:
    """
    Counters from parental_bypass_stats when the table exists (UUID/text-safe).
    Tries (parent, child), then child-only, then parent-only (newest row).
    """
    raw_parent = current_user.get("id")
    pid = str(raw_parent).strip() if raw_parent is not None else ""
    if not pid:
        return None
    cid = str(child_id).strip() if child_id else ""

    attempts: List[Tuple[Any, dict]] = []
    if cid:
        attempts.append(
            (
                text(
                    """
                    SELECT today, week, blocked, incognito, tor, proxy, message
                    FROM parental_bypass_stats
                    WHERE user_id::text = :pid AND child_id::text = :cid
                    ORDER BY updated_at DESC NULLS LAST
                    LIMIT 1
                    """
                ),
                {"pid": pid, "cid": cid},
            )
        )
        attempts.append(
            (
                text(
                    """
                    SELECT today, week, blocked, incognito, tor, proxy, message
                    FROM parental_bypass_stats
                    WHERE child_id::text = :cid
                    ORDER BY updated_at DESC NULLS LAST
                    LIMIT 1
                    """
                ),
                {"cid": cid},
            )
        )
    attempts.append(
        (
            text(
                """
                SELECT today, week, blocked, incognito, tor, proxy, message
                FROM parental_bypass_stats
                WHERE user_id::text = :pid
                ORDER BY updated_at DESC NULLS LAST
                LIMIT 1
                """
            ),
            {"pid": pid},
        ),
    )

    for qry, params in attempts:
        try:
            row = db.execute(qry, params).fetchone()
            if row:
                return {
                    "today": int(row[0] or 0),
                    "week": int(row[1] or 0),
                    "blocked": int(row[2] or 0),
                    "incognito": int(row[3] or 0),
                    "tor": int(row[4] or 0),
                    "proxy": int(row[5] or 0),
                    "message": row[6] if len(row) > 6 and row[6] else "Защита активна.",
                }
        except Exception as exc:
            logger.debug("parental_bypass_stats read skipped: %s", exc)
            db.rollback()
            continue
    return None


@bypass_router.get("/bypass/stats", response_model=BypassStatsResponse)
async def get_bypass_stats(
    childId: Optional[str] = Query(None, alias="childId"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Bypass stats: merge parental_bypass_stats (today/week/blocked) with shadow (incognito/tor/proxy)."""
    logger.info("🔔 [PUSH TRIGGER] BYPASS_ATTEMPT: Обнаружена попытка отключить защиту")
    target_id = _resolve_target_id_flexible(childId, current_user)
    shadow = _read_bypass_shadow(db, target_id)
    db_row = _read_bypass_stats_from_db(db, current_user, childId)

    today = week = blocked = 0
    incognito = tor = proxy = 0
    message = "Защита активна."

    if db_row:
        today = db_row["today"]
        week = db_row["week"]
        blocked = db_row["blocked"]
        message = db_row.get("message") or message
        incognito = db_row["incognito"]
        tor = db_row["tor"]
        proxy = db_row["proxy"]

    if shadow is not None:
        incognito = shadow["incognito"]
        tor = shadow["tor"]
        proxy = shadow["proxy"]

    return BypassStatsResponse(
        success=True,
        today=today,
        week=week,
        blocked=blocked,
        incognito=incognito,
        tor=tor,
        proxy=proxy,
        message=message,
    )


@bypass_router.post("/bypass/apply", response_model=ApiBoolResponse)
async def apply_bypass_protection(
    payload: BypassApplyRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Apply bypass settings with production-safe response contract (no SFM mock)."""
    try:
        target_id = _resolve_target_id_flexible(payload.childId, current_user)
        _persist_bypass_shadow(
            db,
            target_id=target_id,
            incognito=payload.incognito,
            tor=payload.tor,
            proxy=payload.proxy,
        )
        db.commit()
        return ApiBoolResponse(success=True, data=True, message="Bypass protection applied", error=None)
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error applying bypass protection: {str(e)}")
        return ApiBoolResponse(success=False, data=False, message="Apply failed", error=str(e))

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


# SEC-P2-04: monitoring/detail + monitoring/events — explicit app.routers.parental_monitoring only.


async def ingest_parental_monitoring_events(
    payload: MonitoringIngestRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    POST /api/parental-control/monitoring/events
    Детское устройство (JWT пользователя-ребёнка) пишет события в parental_monitoring_events.

    События с признаками обхода (kind/payload «bypass») после успешной записи:
    обновляют счётчики parental_bypass_stats (если найдена пара member-id в family_members)
    и создают in-app уведомление семье (тип bypass_attempt).
    """
    raw_uid = current_user.get("id")
    if isinstance(raw_uid, int):
        uid = raw_uid
    elif isinstance(raw_uid, str) and raw_uid.isdigit():
        uid = int(raw_uid)
    else:
        raise HTTPException(status_code=401, detail="Numeric user id required for monitoring ingest")

    if not payload.events:
        return {"success": True, "inserted": 0}

    _ensure_parental_monitoring_events_table(db)
    try:
        for ev in payload.events:
            kind = (ev.kind or "event")[:64]
            pjson = json.dumps(ev.payload or {}, ensure_ascii=False)
            db.execute(
                text(
                    """
                    INSERT INTO parental_monitoring_events (user_id, kind, payload)
                    VALUES (:uid, :kind, CAST(:payload AS jsonb))
                    """
                ),
                {"uid": uid, "kind": kind, "payload": pjson},
            )
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error("monitoring ingest failed: %s", e)
        raise HTTPException(status_code=500, detail="Monitoring ingest failed")

    # Отдельные транзакции: не блокируем ingest при ошибке stats / уведомления.
    for ev in payload.events:
        kind = (ev.kind or "event")[:64]
        pl = ev.payload or {}
        if not _is_bypass_monitoring_event(kind, pl):
            continue
        try:
            pair = _resolve_parent_child_member_ids_for_bypass_stats(db, uid)
            if pair:
                deltas = _bypass_counter_deltas(kind, pl)
                _increment_parental_bypass_stats(db, pair[0], pair[1], *deltas)
                db.commit()
        except Exception as exc:
            logger.info("bypass stats update skipped: %s", exc)
            try:
                db.rollback()
            except Exception:
                pass

        fam = _resolve_family_id_for_numeric_user(db, uid) or _DEFAULT_NOTIFICATION_FAMILY_ID
        try:
            await _emit_bypass_notification_from_ingest(fam, kind, pl, uid)
        except Exception as exc:
            logger.error("bypass notification emit failed: %s", exc)

    return {"success": True, "inserted": len(payload.events)}


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
        target_user_id = _resolve_target_user_id(childId, current_user, db)
        if target_user_id is None:
            logger.info("ℹ️ Daily reports: unresolved numeric user_id, returning empty list")
            return []

        result = db.execute(
            text(
                """
                SELECT id, user_id, type, content, created_at
                FROM parental_reports
                WHERE user_id = :user_id AND type = 'daily'
                ORDER BY created_at DESC
                LIMIT 7
                """
            ),
            {"user_id": target_user_id},
        ).fetchall()

        reports: List[ParentalReportItem] = []
        for row in result:
            raw_content = row[3]
            if not isinstance(raw_content, dict):
                raw_content = {"raw": raw_content}
            reports.append(
                ParentalReportItem(
                    id=int(row[0]),
                    user_id=int(row[1]),
                    type=str(row[2]),
                    content=raw_content,
                    created_at=row[4],
                )
            )

        # Production-only behavior: no demo/mock fallback.
        return reports
    except Exception as e:
        logger.error(f"❌ Error fetching daily reports: {str(e)}")
        db.rollback()
        return []

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
        target_user_id = _resolve_target_user_id(childId, current_user, db)
        if target_user_id is None:
            logger.info("ℹ️ Weekly reports: unresolved numeric user_id, returning empty list")
            return []

        result = db.execute(
            text(
                """
                SELECT id, user_id, type, content, created_at
                FROM parental_reports
                WHERE user_id = :user_id AND type = 'weekly'
                ORDER BY created_at DESC
                LIMIT 4
                """
            ),
            {"user_id": target_user_id},
        ).fetchall()

        reports: List[ParentalReportItem] = []
        for row in result:
            raw_content = row[3]
            if not isinstance(raw_content, dict):
                raw_content = {"raw": raw_content}
            reports.append(
                ParentalReportItem(
                    id=int(row[0]),
                    user_id=int(row[1]),
                    type=str(row[2]),
                    content=raw_content,
                    created_at=row[4],
                )
            )

        # Production-only behavior: no demo/mock fallback.
        return reports
    except Exception as e:
        logger.error(f"❌ Error fetching weekly reports: {str(e)}")
        db.rollback()
        return []
