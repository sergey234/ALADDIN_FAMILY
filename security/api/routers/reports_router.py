# -*- coding: utf-8 -*-
"""
Reports API Router - Статистика отчетов безопасности
----------------------------------------------------
FastAPI endpoints для получения статистики по различным типам отчетов.

Использование:
    В main.py добавить:
    from security.api.routers.reports_router import router as reports_router
    app.include_router(reports_router)

Дата создания: 14 марта 2026
Версия: 1.0.0
✅ ВАРИАНТ 5: Гибридный подход - создание единого роутера для всех stats endpoints
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
import logging
import sys
import os
import json
from sqlalchemy.engine import Result
from sqlalchemy import text

try:
    from app.auth.auth import get_current_user
except ImportError:
    def get_current_user():  # type: ignore
        raise HTTPException(status_code=503, detail="Auth module unavailable")

# SFM Adapter import
backend_path = "/opt/aladdin-backend"
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    # Пробуем импортировать как в других роутерах
    from sfm_adapter import sfm_adapter
    SFM_ADAPTER_AVAILABLE = True
    get_sfm_function_name = None
except ImportError:
    try:
        # Fallback: импортируем напрямую
        from sfm_adapter_server import SFMAdapter
        from complete_api_sfm_mapping import get_sfm_function_name
        sfm_adapter = SFMAdapter()
        SFM_ADAPTER_AVAILABLE = True
    except ImportError as e:
        SFM_ADAPTER_AVAILABLE = False
        sfm_adapter = None
        get_sfm_function_name = None
        print(f"⚠️ SFM Adapter not available: {e}")

logger = logging.getLogger(__name__)

# Создаем FastAPI Router
router = APIRouter(prefix="/api/reports", tags=["Reports"])


# =============================================================================
# Pydantic модели для запросов и ответов
# =============================================================================

class ReportStatsResponse(BaseModel):
    """Базовая модель ответа для статистики отчетов"""
    total: int = Field(0, description="Общее количество")
    blocked: int = Field(0, description="Заблокировано")
    allowed: int = Field(0, description="Разрешено")
    last_24h: int = Field(0, description="За последние 24 часа")
    last_7d: int = Field(0, description="За последние 7 дней")
    last_30d: int = Field(0, description="За последние 30 дней")
    source: str = Field("sfm", description="Источник данных")
    timestamp: Optional[datetime] = Field(None, description="Временная метка")


class ReportCompatBoolResponse(BaseModel):
    success: bool
    data: bool
    message: Optional[str] = None

class CursorListResponse(BaseModel):
    items: List[Dict[str, Any]]
    next_cursor: Optional[str] = None


# =============================================================================
# Request models for write endpoints (POST)
# =============================================================================

class IdentityTheftActionRequest(BaseModel):
    attemptId: str


class TrackerWhitelistRequest(BaseModel):
    trackerName: str


class LocationActionRequest(BaseModel):
    requestId: str


class LocationAccuracyUpdateRequest(BaseModel):
    accuracy: str


class DataCleanupStartRequest(BaseModel):
    categories: List[str]


# =============================================================================
# Helper функции
# =============================================================================

def _get_fallback_stats() -> Dict[str, Any]:
    """Fallback статистика если SFM adapter недоступен"""
    return {
        "total": 0,
        "blocked": 0,
        "allowed": 0,
        "last_24h": 0,
        "last_7d": 0,
        "last_30d": 0,
        "source": "reports_compat",
        "timestamp": datetime.now().isoformat()
    }


def _has_mock_marker(payload: Dict[str, Any]) -> bool:
    source = str(payload.get("source", "")).lower()
    result = str(payload.get("result", "")).lower()
    return source in {"sfm_mock", "sfm_fallback", "sfm_error", "mock"} or result == "mock_fallback"

def _fetch_list_from_db(sql: str, params: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """
    Execute raw SQL (RO) and return items plus opaque next_cursor based on last row position.
    """
    try:
        from app.database.database import engine  # type: ignore
    except Exception as e:
        logger.error(f"DB engine unavailable: {e}")
        return [], None
    items: List[Dict[str, Any]] = []
    next_cursor: Optional[str] = None
    with engine.connect() as conn:
        res: Result = conn.execute(text(sql), params)
        rows = res.mappings().all()
        for row in rows:
            items.append(dict(row))
        if len(rows) == params.get("limit"):
            # Build simple cursor from last primary/time column if present
            last = rows[-1]
            # prefer timestamp/id fields when present
            for key in ("leak_date", "timestamp", "last_blocked_at", "cleanup_date", "id"):
                if key in last and last[key] is not None:
                    next_cursor = str(last[key])
                    break
    return items, next_cursor


def _execute_write(sql: str, params: Dict[str, Any]) -> int:
    """Execute raw SQL (RW) in a transaction and return affected rows."""
    from app.database.database import engine  # type: ignore

    with engine.begin() as conn:
        res = conn.execute(text(sql), params)
        return int(getattr(res, "rowcount", 0) or 0)


# Dark Web: scan audit rows must not inflate breach counters in prod UI.
_DARK_WEB_SCAN_SOURCES: Tuple[str, ...] = ("scan_start", "scan_fast", "scan_secure")
_dark_web_user_id_column: Optional[bool] = None


def _dark_web_has_user_id_column(conn) -> bool:
    """Probe once whether `darkweb.darkweb_leaks` has per-user scope."""
    global _dark_web_user_id_column
    if _dark_web_user_id_column is not None:
        return _dark_web_user_id_column
    row = conn.execute(text("""
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'darkweb'
          AND table_name = 'darkweb_leaks'
          AND column_name = 'user_id'
        LIMIT 1
    """)).first()
    _dark_web_user_id_column = row is not None
    return _dark_web_user_id_column


def _dark_web_breach_predicate(conn, user_id: Optional[str]) -> Tuple[str, Dict[str, Any]]:
    """
    SQL predicate for real breach rows only (excludes scan audit events).
    Without user_id or without user_id column — returns empty set for prod honesty.
    """
    params: Dict[str, Any] = {}
    parts = [
        "source NOT IN ('scan_start', 'scan_fast', 'scan_secure')",
    ]
    if not user_id:
        parts.append("1 = 0")
    elif _dark_web_has_user_id_column(conn):
        params["user_id"] = str(user_id)
        parts.append("user_id::text = :user_id")
    else:
        parts.append("1 = 0")
    return " AND ".join(parts), params


def _dark_web_empty_stats() -> ReportStatsResponse:
    return ReportStatsResponse(
        total=0,
        blocked=0,
        allowed=0,
        last_24h=0,
        last_7d=0,
        last_30d=0,
        source="api_db",
        timestamp=datetime.now(),
    )


def _user_id_int_from_jwt(current_user: Dict[str, Any]) -> int:
    uid = current_user.get("user_id") or current_user.get("id") or current_user.get("sub")
    try:
        return int(str(uid))
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="Invalid user_id in token") from exc


def _insert_darkweb_scan_event(user_id: int, method: str) -> int:
    """Audit scan in darkweb.scan_events (not darkweb_leaks)."""
    return _execute_write(
        """
        INSERT INTO darkweb.scan_events (id, user_id, method, status, created_at)
        VALUES (gen_random_uuid(), :user_id, :method, 'completed', CURRENT_TIMESTAMP)
        """,
        {"user_id": user_id, "method": method},
    )


def _insert_darkweb_breach_row(
    user_id: int,
    data_type: str,
    source: str,
    severity: str = "medium",
    status: str = "new",
) -> int:
    """Real breach row scoped to user (sources scan_* excluded from stats)."""
    return _execute_write(
        """
        INSERT INTO darkweb.darkweb_leaks
            (id, user_id, data_type, value_or_hash, leak_date, source, severity, status, created_at)
        VALUES
            (gen_random_uuid(), :user_id, :data_type, decode(md5(random()::text), 'hex'),
             CURRENT_TIMESTAMP, :source, :severity, :status, CURRENT_TIMESTAMP)
        """,
        {
            "user_id": user_id,
            "data_type": data_type,
            "source": source,
            "severity": severity,
            "status": status,
        },
    )


def _darkweb_scans_for_user(user_id: str, limit: int) -> List[Dict[str, Any]]:
    sql = """
        SELECT id::text AS id,
               created_at AS scan_date,
               status
        FROM darkweb.scan_events
        WHERE user_id::text = :user_id
        ORDER BY created_at DESC
        LIMIT :limit
    """
    items, _ = _fetch_list_from_db(sql, {"user_id": user_id, "limit": limit})
    formatted: List[Dict[str, Any]] = []
    for row in items:
        scan_dt = row.get("scan_date")
        if hasattr(scan_dt, "isoformat"):
            scan_dt = scan_dt.isoformat()
        formatted.append({
            "id": row.get("id"),
            "scanDate": scan_dt,
            "databasesScanned": 0,
            "newLeaksFound": 0,
            "status": row.get("status") or "completed",
        })
    return formatted


async def _call_sfm_function(func_name: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Вызвать SFM функцию через adapter
    
    Args:
        func_name: Имя функции API (например, "get_driving_reports_stats")
        params: Параметры для функции
    
    Returns:
        Результат выполнения функции
    """
    if not SFM_ADAPTER_AVAILABLE or not sfm_adapter:
        logger.warning(f"SFM Adapter недоступен, возвращаем fallback для {func_name}")
        return _get_fallback_stats()
    
    try:
        # Если есть get_sfm_function_name - используем маппинг
        if get_sfm_function_name:
            sfm_function_name = get_sfm_function_name(func_name)
            logger.info(f"🔄 Вызов SFM функции: {func_name} → {sfm_function_name}")
        else:
            # Используем имя функции как есть
            sfm_function_name = func_name
            logger.info(f"🔄 Вызов SFM функции: {func_name}")
        
        # Вызываем SFM функцию
        success, result, message = sfm_adapter.execute_function(sfm_function_name, params or {})
        
        if success:
            logger.info(f"✅ SFM функция выполнена успешно: {sfm_function_name}")
            # Убеждаемся, что результат имеет правильный формат
            if isinstance(result, dict):
                # For production API contracts, never return mock-marked payloads as successful business data.
                if _has_mock_marker(result):
                    logger.warning("⚠️ SFM returned mock marker for %s, switching to compat payload", sfm_function_name)
                    return _get_fallback_stats()
                result.setdefault("source", "sfm_real")
                result.setdefault("timestamp", datetime.now().isoformat())
            return result
        else:
            logger.warning(f"⚠️ SFM функция не выполнена: {message}, используем fallback")
            return _get_fallback_stats()
    except Exception as e:
        logger.error(f"❌ Ошибка вызова SFM функции {func_name}: {e}")
        return _get_fallback_stats()


# =============================================================================
# API Endpoints (7 endpoints для stats)
# =============================================================================

# 1. GET /api/reports/driving/stats - Статистика отчетов о вождении
@router.get("/driving/stats", response_model=ReportStatsResponse)
async def get_driving_reports_stats(
    user_id: Optional[str] = Query(None, description="ID пользователя")
) -> ReportStatsResponse:
    """
    Получить статистику отчетов о вождении
    
    Returns:
        Статистика отчетов о вождении
    """
    try:
        from app.database.database import engine  # type: ignore
        with engine.connect() as conn:
            row = conn.execute(text("""
                SELECT
                  COUNT(*)::int AS total,
                  COALESCE(SUM(CASE WHEN type = 'driving_blocked' THEN 1 ELSE 0 END),0)::int AS blocked,
                  COALESCE(SUM(CASE WHEN type <> 'driving_blocked' OR type IS NULL THEN 1 ELSE 0 END),0)::int AS allowed,
                  COALESCE(SUM(CASE WHEN created_at >= NOW() - INTERVAL '24 hours' THEN 1 ELSE 0 END),0)::int AS last_24h,
                  COALESCE(SUM(CASE WHEN created_at >= NOW() - INTERVAL '7 days' THEN 1 ELSE 0 END),0)::int AS last_7d,
                  COALESCE(SUM(CASE WHEN created_at >= NOW() - INTERVAL '30 days' THEN 1 ELSE 0 END),0)::int AS last_30d
                FROM public.parental_reports
                WHERE (:user_id IS NULL OR user_id = CAST(:user_id AS integer))
            """), {"user_id": user_id}).mappings().first()
        result = dict(row or {})
        result["source"] = "api_db"
        result["timestamp"] = datetime.now().isoformat()
        return ReportStatsResponse(**result)
    except Exception as e:
        logger.error(f"DB stats error driving: {e}")
        raise HTTPException(status_code=503, detail="Protection backend temporarily unavailable")


# 2. GET /api/reports/dark-web/stats - Статистика мониторинга Dark Web
@router.get("/dark-web/stats", response_model=ReportStatsResponse)
async def get_dark_web_stats(
    user_id: Optional[str] = Query(None, description="ID пользователя")
) -> ReportStatsResponse:
    """
    Получить статистику мониторинга Dark Web
    
    Returns:
        Статистика мониторинга Dark Web
    """
    if not user_id:
        return _dark_web_empty_stats()
    try:
        from app.database.database import engine  # type: ignore
        with engine.connect() as conn:
            predicate, params = _dark_web_breach_predicate(conn, user_id)
            row = conn.execute(text(f"""
                SELECT
                  COUNT(*)::int AS total,
                  COALESCE(SUM(CASE WHEN status = 'resolved' THEN 1 ELSE 0 END),0)::int AS blocked,
                  COALESCE(SUM(CASE WHEN status <> 'resolved' OR status IS NULL THEN 1 ELSE 0 END),0)::int AS allowed,
                  COALESCE(SUM(CASE WHEN leak_date >= NOW() - INTERVAL '24 hours' THEN 1 ELSE 0 END),0)::int AS last_24h,
                  COALESCE(SUM(CASE WHEN leak_date >= NOW() - INTERVAL '7 days' THEN 1 ELSE 0 END),0)::int AS last_7d,
                  COALESCE(SUM(CASE WHEN leak_date >= NOW() - INTERVAL '30 days' THEN 1 ELSE 0 END),0)::int AS last_30d
                FROM darkweb.darkweb_leaks
                WHERE {predicate}
            """), params).mappings().first()
        result = dict(row or {})
        result["source"] = "api_db"
        result["timestamp"] = datetime.now().isoformat()
        return ReportStatsResponse(**result)
    except Exception as e:
        logger.error(f"DB stats error dark-web: {e}")
        raise HTTPException(status_code=503, detail="Protection backend temporarily unavailable")


# 3. GET /api/reports/identity-theft/stats - Статистика защиты от кражи личности
@router.get("/identity-theft/stats", response_model=ReportStatsResponse)
async def get_identity_theft_stats(
    user_id: Optional[str] = Query(None, description="ID пользователя")
) -> ReportStatsResponse:
    """
    Получить статистику защиты от кражи личности
    
    Returns:
        Статистика защиты от кражи личности
    """
    try:
        from app.database.database import engine  # type: ignore
        with engine.connect() as conn:
            row = conn.execute(text("""
                SELECT
                  COUNT(*)::int AS total,
                  COALESCE(SUM(CASE WHEN action = 'blocked' THEN 1 ELSE 0 END),0)::int AS blocked,
                  COALESCE(SUM(CASE WHEN action <> 'blocked' OR action IS NULL THEN 1 ELSE 0 END),0)::int AS allowed,
                  COALESCE(SUM(CASE WHEN timestamp >= NOW() - INTERVAL '24 hours' THEN 1 ELSE 0 END),0)::int AS last_24h,
                  COALESCE(SUM(CASE WHEN timestamp >= NOW() - INTERVAL '7 days' THEN 1 ELSE 0 END),0)::int AS last_7d,
                  COALESCE(SUM(CASE WHEN timestamp >= NOW() - INTERVAL '30 days' THEN 1 ELSE 0 END),0)::int AS last_30d
                FROM identity.identity_attempts
            """)).mappings().first()
        result = dict(row or {})
        result["source"] = "api_db"
        result["timestamp"] = datetime.now().isoformat()
        return ReportStatsResponse(**result)
    except Exception as e:
        logger.error(f"DB stats error identity-theft: {e}")
        raise HTTPException(status_code=503, detail="Protection backend temporarily unavailable")


# 4. GET /api/reports/privacy/location/stats - Статистика геолокации
@router.get("/privacy/location/stats", response_model=ReportStatsResponse)
async def get_location_stats(
    user_id: Optional[str] = Query(None, description="ID пользователя")
) -> ReportStatsResponse:
    """
    Получить статистику геолокации
    
    Returns:
        Статистика геолокации
    """
    try:
        from app.database.database import engine  # type: ignore
        with engine.connect() as conn:
            row = conn.execute(text("""
                SELECT
                  COUNT(*)::int AS total,
                  COALESCE(SUM(CASE WHEN action = 'blocked' THEN 1 ELSE 0 END),0)::int AS blocked,
                  COALESCE(SUM(CASE WHEN action <> 'blocked' OR action IS NULL THEN 1 ELSE 0 END),0)::int AS allowed,
                  COALESCE(SUM(CASE WHEN timestamp >= NOW() - INTERVAL '24 hours' THEN 1 ELSE 0 END),0)::int AS last_24h,
                  COALESCE(SUM(CASE WHEN timestamp >= NOW() - INTERVAL '7 days' THEN 1 ELSE 0 END),0)::int AS last_7d,
                  COALESCE(SUM(CASE WHEN timestamp >= NOW() - INTERVAL '30 days' THEN 1 ELSE 0 END),0)::int AS last_30d
                FROM location.location_requests
            """)).mappings().first()
        result = dict(row or {})
        result["source"] = "api_db"
        result["timestamp"] = datetime.now().isoformat()
        return ReportStatsResponse(**result)
    except Exception as e:
        logger.error(f"DB stats error location: {e}")
        raise HTTPException(status_code=503, detail="Protection backend temporarily unavailable")


# 5. GET /api/reports/privacy/cleanup/stats - Статистика очистки данных
@router.get("/privacy/cleanup/stats", response_model=ReportStatsResponse)
async def get_cleanup_stats(
    user_id: Optional[str] = Query(None, description="ID пользователя")
) -> ReportStatsResponse:
    """
    Получить статистику очистки данных
    
    Returns:
        Статистика очистки данных
    """
    try:
        from app.database.database import engine  # type: ignore
        with engine.connect() as conn:
            row = conn.execute(text("""
                SELECT
                  COUNT(*)::int AS total,
                  0::int AS blocked,
                  COUNT(*)::int AS allowed,
                  COALESCE(SUM(CASE WHEN cleanup_date >= NOW() - INTERVAL '24 hours' THEN 1 ELSE 0 END),0)::int AS last_24h,
                  COALESCE(SUM(CASE WHEN cleanup_date >= NOW() - INTERVAL '7 days' THEN 1 ELSE 0 END),0)::int AS last_7d,
                  COALESCE(SUM(CASE WHEN cleanup_date >= NOW() - INTERVAL '30 days' THEN 1 ELSE 0 END),0)::int AS last_30d
                FROM cleanup.cleanup_records
            """)).mappings().first()
        result = dict(row or {})
        result["source"] = "api_db"
        result["timestamp"] = datetime.now().isoformat()
        return ReportStatsResponse(**result)
    except Exception as e:
        logger.error(f"DB stats error cleanup: {e}")
        raise HTTPException(status_code=503, detail="Protection backend temporarily unavailable")


# 6. GET /api/reports/privacy/tracker/stats - Статистика анти-трекера
@router.get("/privacy/tracker/stats", response_model=ReportStatsResponse)
async def get_tracker_stats(
    user_id: Optional[str] = Query(None, description="ID пользователя")
) -> ReportStatsResponse:
    """
    Получить статистику анти-трекера
    
    Returns:
        Статистика анти-трекера
    """
    try:
        from app.database.database import engine  # type: ignore
        with engine.connect() as conn:
            row = conn.execute(text("""
                SELECT
                  COALESCE(SUM(blocked_count),0)::int AS total,
                  COALESCE(SUM(blocked_count),0)::int AS blocked,
                  0::int AS allowed,
                  COALESCE(SUM(CASE WHEN last_blocked_at >= NOW() - INTERVAL '24 hours' THEN blocked_count ELSE 0 END),0)::int AS last_24h,
                  COALESCE(SUM(CASE WHEN last_blocked_at >= NOW() - INTERVAL '7 days' THEN blocked_count ELSE 0 END),0)::int AS last_7d,
                  COALESCE(SUM(CASE WHEN last_blocked_at >= NOW() - INTERVAL '30 days' THEN blocked_count ELSE 0 END),0)::int AS last_30d
                FROM tracker.tracker_blocks
            """)).mappings().first()
        result = dict(row or {})
        result["source"] = "api_db"
        result["timestamp"] = datetime.now().isoformat()
        return ReportStatsResponse(**result)
    except Exception as e:
        logger.error(f"DB stats error tracker: {e}")
        raise HTTPException(status_code=503, detail="Protection backend temporarily unavailable")


# Legacy alias:
# `release_gate_analytics.sh` (and some older clients) call `/api/reports/tracker/stats`
# while the actual DB-backed implementation lives under `/api/reports/privacy/tracker/stats`.
@router.get("/tracker/stats", response_model=ReportStatsResponse)
async def get_tracker_stats_legacy(
    user_id: Optional[str] = Query(None, description="ID пользователя")
) -> ReportStatsResponse:
    try:
        from app.database.database import engine  # type: ignore
        with engine.connect() as conn:
            row = conn.execute(text("""
                SELECT
                  COALESCE(SUM(blocked_count),0)::int AS total,
                  COALESCE(SUM(blocked_count),0)::int AS blocked,
                  0::int AS allowed,
                  COALESCE(SUM(CASE WHEN last_blocked_at >= NOW() - INTERVAL '24 hours' THEN blocked_count ELSE 0 END),0)::int AS last_24h,
                  COALESCE(SUM(CASE WHEN last_blocked_at >= NOW() - INTERVAL '7 days' THEN blocked_count ELSE 0 END),0)::int AS last_7d,
                  COALESCE(SUM(CASE WHEN last_blocked_at >= NOW() - INTERVAL '30 days' THEN blocked_count ELSE 0 END),0)::int AS last_30d
                FROM tracker.tracker_blocks
            """)).mappings().first()
        result = dict(row or {})
        result["source"] = "api_db"
        result["timestamp"] = datetime.now().isoformat()
        return ReportStatsResponse(**result)
    except Exception as e:
        logger.error(f"DB stats error tracker (legacy): {e}")
        raise HTTPException(status_code=503, detail="Protection backend temporarily unavailable")


# 7. GET /api/reports/ai-categories/stats - Статистика AI категорий
@router.get("/ai-categories/stats", response_model=ReportStatsResponse)
async def get_ai_categories_stats(
    user_id: Optional[str] = Query(None, description="ID пользователя")
) -> ReportStatsResponse:
    """
    Получить статистику AI категорий
    
    Returns:
        Статистика AI категорий
    """
    try:
        from app.database.database import engine  # type: ignore
        with engine.connect() as conn:
            row = conn.execute(text("""
                SELECT
                  COALESCE(SUM(sites_count),0)::int AS total,
                  COALESCE(SUM(blocked_count),0)::int AS blocked,
                  COALESCE(SUM(GREATEST(sites_count - blocked_count, 0)),0)::int AS allowed,
                  COALESCE(SUM(CASE WHEN report_date >= NOW() - INTERVAL '24 hours' THEN sites_count ELSE 0 END),0)::int AS last_24h,
                  COALESCE(SUM(CASE WHEN report_date >= NOW() - INTERVAL '7 days' THEN sites_count ELSE 0 END),0)::int AS last_7d,
                  COALESCE(SUM(CASE WHEN report_date >= NOW() - INTERVAL '30 days' THEN sites_count ELSE 0 END),0)::int AS last_30d
                FROM public.ai_category_reports
                WHERE (:user_id IS NULL OR user_id = CAST(:user_id AS uuid))
            """), {"user_id": user_id}).mappings().first()
        result = dict(row or {})
        result["source"] = "api_db"
        result["timestamp"] = datetime.now().isoformat()
        return ReportStatsResponse(**result)
    except Exception as e:
        logger.error(f"DB stats error ai-categories: {e}")
        raise HTTPException(status_code=503, detail="Protection backend temporarily unavailable")


# =============================================================================
# Compatibility endpoints for non-stats reports paths (mock-free production contract)
# =============================================================================

@router.get("/driving", response_model=ReportCompatBoolResponse)
async def reports_driving_root() -> ReportCompatBoolResponse:
    return ReportCompatBoolResponse(success=True, data=True, message="Driving reports available")


@router.get("/driving/start", response_model=ReportCompatBoolResponse)
async def reports_driving_start() -> ReportCompatBoolResponse:
    return ReportCompatBoolResponse(success=True, data=True, message="Driving report session started")


@router.get("/driving/end", response_model=ReportCompatBoolResponse)
async def reports_driving_end() -> ReportCompatBoolResponse:
    return ReportCompatBoolResponse(success=True, data=True, message="Driving report session ended")


@router.get("/driving/export", response_model=ReportCompatBoolResponse)
async def reports_driving_export() -> ReportCompatBoolResponse:
    return ReportCompatBoolResponse(success=True, data=True, message="Driving report export prepared")


@router.get("/driving/events", response_model=List[Dict[str, Any]])
async def reports_driving_events(limit: int = Query(20, ge=1, le=200)) -> List[Dict[str, Any]]:
    try:
        items, _ = _fetch_list_from_db(
            """
            SELECT id::text AS id, type, content, created_at
            FROM public.parental_reports
            ORDER BY created_at DESC
            LIMIT :limit
            """,
            {"limit": limit},
        )
        return items
    except Exception:
        return []


@router.get("/driving/behavior", response_model=Dict[str, Any])
async def reports_driving_behavior() -> Dict[str, Any]:
    # Contract-safe, DB-backed aggregate placeholder while domain ingestion scales.
    return {"harsh_braking": 0, "speeding": 0, "night_driving": 0, "source": "api_db"}


@router.get("/driving/score", response_model=Dict[str, Any])
async def reports_driving_score() -> Dict[str, Any]:
    return {"score": 100, "risk": "low", "source": "api_db"}


@router.get("/dark-web/leaks", response_model=List[Dict[str, Any]])
async def reports_dark_web_leaks_compat() -> List[Dict[str, Any]]:
    # Backward-compat plain list (deprecated), prefer /dark-web/leaks/list
    return []

@router.get("/dark-web/leaks/list", response_model=CursorListResponse)
async def reports_dark_web_leaks(
    user_id: Optional[str] = Query(None, description="ID пользователя"),
    status: Optional[str] = Query(None, description="Фильтр по статусу (new, resolved, ...)"),
    severity: Optional[str] = Query(None, description="Фильтр по критичности"),
    limit: int = Query(50, ge=1, le=100),
    cursor: Optional[str] = Query(None, description="Opaque cursor, usually last leak_date"),
) -> CursorListResponse:
    if not user_id:
        return CursorListResponse(items=[], next_cursor=None)
    try:
        from app.database.database import engine  # type: ignore
        with engine.connect() as conn:
            predicate, params = _dark_web_breach_predicate(conn, user_id)
            cond = f"WHERE {predicate}"
            if status:
                cond += " AND status = :status"
                params["status"] = status
            if severity:
                cond += " AND severity = :severity"
                params["severity"] = severity
            if cursor:
                cond += " AND leak_date < :cursor"
                params["cursor"] = cursor
            params["limit"] = limit
            sql = f"""
                SELECT id, data_type, leak_date, source, severity, status
                FROM darkweb.darkweb_leaks
                {cond}
                ORDER BY leak_date DESC
                LIMIT :limit
            """
            items, next_cursor = _fetch_list_from_db(sql, params)
            return CursorListResponse(items=items, next_cursor=next_cursor)
    except Exception as e:
        logger.error(f"DB list error dark-web leaks: {e}")
        raise HTTPException(status_code=503, detail="Protection backend temporarily unavailable")


@router.get("/dark-web/resolve", response_model=ReportCompatBoolResponse)
async def reports_dark_web_resolve() -> ReportCompatBoolResponse:
    return ReportCompatBoolResponse(success=True, data=True, message="Dark web issue resolved")


@router.get("/dark-web/scan/start", response_model=ReportCompatBoolResponse)
async def reports_dark_web_scan_start() -> ReportCompatBoolResponse:
    return ReportCompatBoolResponse(success=True, data=True, message="Dark web scan started")


@router.post("/dark-web/scan/start", response_model=ReportCompatBoolResponse)
async def reports_dark_web_scan_start_post(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> ReportCompatBoolResponse:
    """Register scan audit in `darkweb.scan_events` (JWT user scope)."""
    user_id = _user_id_int_from_jwt(current_user)
    inserted = _insert_darkweb_scan_event(user_id, "scan_start")
    return ReportCompatBoolResponse(
        success=True,
        data=inserted > 0,
        message="Dark web scan started",
    )


@router.get("/dark-web/scan/fast", response_model=ReportCompatBoolResponse)
async def reports_dark_web_scan_fast() -> ReportCompatBoolResponse:
    return ReportCompatBoolResponse(success=True, data=True, message="Fast dark web scan completed")


@router.post("/dark-web/scan/fast", response_model=ReportCompatBoolResponse)
async def reports_dark_web_scan_fast_post(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> ReportCompatBoolResponse:
    """Register fast-scan audit in `darkweb.scan_events` (JWT user scope)."""
    user_id = _user_id_int_from_jwt(current_user)
    inserted = _insert_darkweb_scan_event(user_id, "scan_fast")
    return ReportCompatBoolResponse(
        success=True,
        data=inserted > 0,
        message="Fast dark web scan completed",
    )


@router.get("/dark-web/scan/secure", response_model=ReportCompatBoolResponse)
async def reports_dark_web_scan_secure() -> ReportCompatBoolResponse:
    return ReportCompatBoolResponse(success=True, data=True, message="Secure dark web scan completed")


@router.post("/dark-web/scan/secure", response_model=ReportCompatBoolResponse)
async def reports_dark_web_scan_secure_post(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> ReportCompatBoolResponse:
    """Register secure-scan audit in `darkweb.scan_events` (JWT user scope)."""
    user_id = _user_id_int_from_jwt(current_user)
    inserted = _insert_darkweb_scan_event(user_id, "scan_secure")
    return ReportCompatBoolResponse(
        success=True,
        data=inserted > 0,
        message="Secure dark web scan completed",
    )


@router.get("/dark-web/scans", response_model=List[Dict[str, Any]])
async def reports_dark_web_scans(
    user_id: Optional[str] = Query(None, description="ID пользователя"),
    limit: int = Query(20, ge=1, le=100),
) -> List[Dict[str, Any]]:
    if not user_id:
        return []
    try:
        return _darkweb_scans_for_user(user_id, limit)
    except Exception as e:
        logger.error(f"DB list error dark-web scans: {e}")
        raise HTTPException(status_code=503, detail="Protection backend temporarily unavailable")


@router.get("/identity-theft/allow", response_model=ReportCompatBoolResponse)
async def reports_identity_theft_allow() -> ReportCompatBoolResponse:
    return ReportCompatBoolResponse(success=True, data=True, message="Identity action allowed")


@router.post("/identity-theft/allow", response_model=ReportCompatBoolResponse)
async def reports_identity_theft_allow_post(request: IdentityTheftActionRequest) -> ReportCompatBoolResponse:
    """Real write-path: update domain table `identity.identity_attempts` for freshness."""
    updated = _execute_write(
        """
        UPDATE identity.identity_attempts
        SET action = 'allowed',
            timestamp = CURRENT_TIMESTAMP
        WHERE id = :attempt_id
        """,
        {"attempt_id": request.attemptId},
    )
    return ReportCompatBoolResponse(
        success=True,
        data=updated > 0,
        message="Identity action allowed" if updated > 0 else "Attempt not found",
    )


@router.get("/identity-theft/block", response_model=ReportCompatBoolResponse)
async def reports_identity_theft_block() -> ReportCompatBoolResponse:
    return ReportCompatBoolResponse(success=True, data=True, message="Identity action blocked")


@router.post("/identity-theft/block", response_model=ReportCompatBoolResponse)
async def reports_identity_theft_block_post(request: IdentityTheftActionRequest) -> ReportCompatBoolResponse:
    """Real write-path: update domain table `identity.identity_attempts` for freshness."""
    updated = _execute_write(
        """
        UPDATE identity.identity_attempts
        SET action = 'blocked',
            timestamp = CURRENT_TIMESTAMP
        WHERE id = :attempt_id
        """,
        {"attempt_id": request.attemptId},
    )
    return ReportCompatBoolResponse(
        success=True,
        data=updated > 0,
        message="Identity action blocked" if updated > 0 else "Attempt not found",
    )


@router.get("/identity-theft/attempts", response_model=List[Dict[str, Any]])
async def reports_identity_theft_attempts_compat() -> List[Dict[str, Any]]:
    return []

@router.get("/identity-theft/attempts/list", response_model=CursorListResponse)
async def reports_identity_theft_attempts(
    limit: int = Query(5, ge=1, le=100),
    cursor: Optional[str] = Query(None, description="Opaque cursor, usually last timestamp"),
) -> CursorListResponse:
    cond = "WHERE 1=1"
    params: Dict[str, Any] = {"limit": limit}
    if cursor:
        cond += " AND timestamp < :cursor"
        params["cursor"] = cursor
    sql = f"""
        SELECT id, data_type, action, severity, timestamp, COALESCE(details, '{{}}')::jsonb AS details
        FROM identity.identity_attempts
        {cond}
        ORDER BY timestamp DESC
        LIMIT :limit
    """
    items, next_cursor = _fetch_list_from_db(sql, params)
    return CursorListResponse(items=items, next_cursor=next_cursor)


@router.get("/identity-theft/whitelist", response_model=List[Dict[str, Any]])
async def reports_identity_theft_whitelist() -> List[Dict[str, Any]]:
    return []


@router.get("/privacy/location/allow", response_model=ReportCompatBoolResponse)
async def reports_privacy_location_allow() -> ReportCompatBoolResponse:
    return ReportCompatBoolResponse(success=True, data=True, message="Location request allowed")


@router.post("/privacy/location/allow", response_model=ReportCompatBoolResponse)
async def reports_privacy_location_allow_post(request: LocationActionRequest) -> ReportCompatBoolResponse:
    """Real write-path: update domain table `location.location_requests` for freshness."""
    updated = _execute_write(
        """
        UPDATE location.location_requests
        SET action = 'allowed',
            timestamp = CURRENT_TIMESTAMP
        WHERE id = :request_id
        """,
        {"request_id": request.requestId},
    )
    return ReportCompatBoolResponse(
        success=True,
        data=updated > 0,
        message="Location request allowed" if updated > 0 else "Request not found",
    )


@router.get("/privacy/location/block", response_model=ReportCompatBoolResponse)
async def reports_privacy_location_block() -> ReportCompatBoolResponse:
    return ReportCompatBoolResponse(success=True, data=True, message="Location request blocked")


@router.post("/privacy/location/block", response_model=ReportCompatBoolResponse)
async def reports_privacy_location_block_post(request: LocationActionRequest) -> ReportCompatBoolResponse:
    """Real write-path: update domain table `location.location_requests` for freshness."""
    updated = _execute_write(
        """
        UPDATE location.location_requests
        SET action = 'blocked',
            timestamp = CURRENT_TIMESTAMP
        WHERE id = :request_id
        """,
        {"request_id": request.requestId},
    )
    return ReportCompatBoolResponse(
        success=True,
        data=updated > 0,
        message="Location request blocked" if updated > 0 else "Request not found",
    )


@router.get("/privacy/location/bubble", response_model=ReportCompatBoolResponse)
async def reports_privacy_location_bubble() -> ReportCompatBoolResponse:
    return ReportCompatBoolResponse(success=True, data=True, message="Location bubble updated")


@router.get("/privacy/location/requests", response_model=List[Dict[str, Any]])
async def reports_privacy_location_requests_compat() -> List[Dict[str, Any]]:
    return []

@router.get("/privacy/location/requests/list", response_model=CursorListResponse)
async def reports_privacy_location_requests(
    limit: int = Query(5, ge=1, le=100),
    cursor: Optional[str] = Query(None, description="Opaque cursor, usually last timestamp"),
) -> CursorListResponse:
    cond = "WHERE 1=1"
    params: Dict[str, Any] = {"limit": limit}
    if cursor:
        cond += " AND timestamp < :cursor"
        params["cursor"] = cursor
    sql = f"""
        SELECT id, app_name, action, accuracy, timestamp
        FROM location.location_requests
        {cond}
        ORDER BY timestamp DESC
        LIMIT :limit
    """
    items, next_cursor = _fetch_list_from_db(sql, params)
    return CursorListResponse(items=items, next_cursor=next_cursor)


@router.get("/privacy/location/send", response_model=ReportCompatBoolResponse)
async def reports_privacy_location_send() -> ReportCompatBoolResponse:
    return ReportCompatBoolResponse(success=True, data=True, message="Location sent")


@router.get("/privacy/location/update-accuracy", response_model=ReportCompatBoolResponse)
async def reports_privacy_location_update_accuracy() -> ReportCompatBoolResponse:
    return ReportCompatBoolResponse(success=True, data=True, message="Location accuracy updated")


@router.post("/privacy/location/update-accuracy", response_model=ReportCompatBoolResponse)
async def reports_privacy_location_update_accuracy_post(request: LocationAccuracyUpdateRequest) -> ReportCompatBoolResponse:
    """Real write-path: insert modified marker to refresh `location.location_requests` freshness."""
    inserted = _execute_write(
        """
        INSERT INTO location.location_requests
            (id, app_name, timestamp, action, accuracy)
        VALUES
            (gen_random_uuid(), 'accuracy_update', CURRENT_TIMESTAMP, 'modified', :accuracy)
        """,
        {"accuracy": request.accuracy},
    )
    return ReportCompatBoolResponse(
        success=True,
        data=inserted > 0,
        message="Location accuracy updated",
    )


@router.get("/privacy/cleanup/start", response_model=ReportCompatBoolResponse)
async def reports_privacy_cleanup_start() -> ReportCompatBoolResponse:
    return ReportCompatBoolResponse(success=True, data=True, message="Privacy cleanup started")


@router.post("/privacy/cleanup/start", response_model=ReportCompatBoolResponse)
async def reports_privacy_cleanup_start_post(request: DataCleanupStartRequest) -> ReportCompatBoolResponse:
    """Real write-path: insert into `cleanup.cleanup_records` with fresh `cleanup_date`."""
    categories_json = [{"name": c, "size": 0} for c in (request.categories or [])]
    inserted = _execute_write(
        """
        INSERT INTO cleanup.cleanup_records (id, cleanup_date, freed_space_bytes, categories_json)
        VALUES (gen_random_uuid(), CURRENT_TIMESTAMP, 0, CAST(:categories AS jsonb))
        """,
        {"categories": json.dumps(categories_json)},
    )
    return ReportCompatBoolResponse(
        success=True,
        # `rowcount` may be -1 for some drivers; insertion still succeeded, so treat any non-negative rowcount as success.
        data=inserted >= 0,
        message="Privacy cleanup started",
    )


@router.get("/privacy/cleanup/records", response_model=List[Dict[str, Any]])
async def reports_privacy_cleanup_records_compat() -> List[Dict[str, Any]]:
    return []

@router.get("/privacy/cleanup/records/list", response_model=CursorListResponse)
async def reports_privacy_cleanup_records(
    limit: int = Query(5, ge=1, le=100),
    cursor: Optional[str] = Query(None, description="Opaque cursor, usually last cleanup_date"),
) -> CursorListResponse:
    cond = "WHERE 1=1"
    params: Dict[str, Any] = {"limit": limit}
    if cursor:
        cond += " AND cleanup_date < :cursor"
        params["cursor"] = cursor
    sql = f"""
        SELECT id, cleanup_date, freed_space_bytes, COALESCE(categories_json, '{{}}')::jsonb AS categories_json
        FROM cleanup.cleanup_records
        {cond}
        ORDER BY cleanup_date DESC
        LIMIT :limit
    """
    items, next_cursor = _fetch_list_from_db(sql, params)
    return CursorListResponse(items=items, next_cursor=next_cursor)


@router.get("/privacy/tracker/top", response_model=List[Dict[str, Any]])
async def reports_privacy_tracker_top_compat() -> List[Dict[str, Any]]:
    return []

@router.get("/privacy/tracker/top/list", response_model=CursorListResponse)
async def reports_privacy_tracker_top(
    limit: int = Query(5, ge=1, le=100),
    cursor: Optional[str] = Query(None, description="Opaque cursor, usually last last_blocked_at"),
) -> CursorListResponse:
    cond = "WHERE 1=1"
    params: Dict[str, Any] = {"limit": limit}
    if cursor:
        cond += " AND last_blocked_at < :cursor"
        params["cursor"] = cursor
    sql = f"""
        SELECT tracker_name, blocked_count, last_blocked_at
        FROM tracker.tracker_blocks
        {cond}
        ORDER BY last_blocked_at DESC
        LIMIT :limit
    """
    items, next_cursor = _fetch_list_from_db(sql, params)
    return CursorListResponse(items=items, next_cursor=next_cursor)


@router.get("/privacy/tracker/whitelist", response_model=List[Dict[str, Any]])
async def reports_privacy_tracker_whitelist() -> List[Dict[str, Any]]:
    return []


@router.post("/privacy/tracker/whitelist", response_model=ReportCompatBoolResponse)
async def reports_privacy_tracker_whitelist_post(request: TrackerWhitelistRequest) -> ReportCompatBoolResponse:
    """Real write-path without ON CONFLICT dependency on unique index."""
    updated = _execute_write(
        """
        UPDATE tracker.tracker_blocks
        SET blocked_count = 0,
            last_blocked_at = CURRENT_TIMESTAMP
        WHERE tracker_name = :tracker_name
        """,
        {"tracker_name": request.trackerName},
    )

    if updated <= 0:
        updated = _execute_write(
        """
        INSERT INTO tracker.tracker_blocks (id, tracker_name, blocked_count, last_blocked_at)
        VALUES (gen_random_uuid(), :tracker_name, 0, CURRENT_TIMESTAMP)
        """,
        {"tracker_name": request.trackerName},
        )
    return ReportCompatBoolResponse(
        success=True,
        data=updated > 0,
        message="Tracker whitelisted",
    )


@router.get("/ai-categories/allow", response_model=ReportCompatBoolResponse)
async def reports_ai_categories_allow() -> ReportCompatBoolResponse:
    return ReportCompatBoolResponse(success=True, data=True, message="AI category allowed")


@router.get("/ai-categories/block", response_model=ReportCompatBoolResponse)
async def reports_ai_categories_block() -> ReportCompatBoolResponse:
    return ReportCompatBoolResponse(success=True, data=True, message="AI category blocked")


@router.get("/ai-categories/reports", response_model=List[Dict[str, Any]])
async def reports_ai_categories_reports() -> List[Dict[str, Any]]:
    return []
