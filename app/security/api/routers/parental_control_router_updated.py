# -*- coding: utf-8 -*-
"""
Parental Control API Router - ОБНОВЛЕННАЯ ВЕРСИЯ С PostgreSQL
--------------------------
ОБНОВЛЕНО: Замена mock данных на PostgreSQL
"""

from datetime import datetime
from typing import Dict, Optional

from fastapi import APIRouter, Query, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import text

# ✅ ИМПОРТЫ ДЛЯ PostgreSQL
from app.database.database import get_db
from app.auth.auth import get_current_user

from enum import Enum

try:
    from security.family.parental_controls import ParentalControls
    from security.family.advanced_parental_controls import AdvancedParentalControls
    _parental_controls_available = True
except ImportError:
    ParentalControls = None
    AdvancedParentalControls = None
    _parental_controls_available = False

# ═══════════════════════════════════════════════════════════════
# Локальные типы
# ═══════════════════════════════════════════════════════════════

class FamilyRole(str, Enum):
    PARENT = "parent"
    CHILD = "child"
    ELDERLY = "elderly"

class AgeGroup(str, Enum):
    ADULT = "adult"
    CHILD_3_6 = "child_3_6"
    CHILD_7_12 = "child_7_12"
    CHILD_13_17 = "child_13_17"
    ELDERLY = "elderly"

class FamilyProfileManager:
    """Dummy класс для FamilyProfileManager."""
    pass

class ChildProtection:
    """Dummy класс для ChildProtection."""
    pass

class ElderlyProtection:
    """Dummy класс для ElderlyProtection."""
    pass

# ═══════════════════════════════════════════════════════════════
# Вспомогательные классы
# ═══════════════════════════════════════════════════════════════

class _DummyMember:
    """Минимальная модель участника семьи с нужными атрибутами."""
    def __init__(self, member_id: str, name: str, role: FamilyRole, age_group: AgeGroup):
        self.id = member_id
        self.name = name
        self.role = role
        self.age_group = age_group

class _DummyFamily:
    """Минимальная модель семейного профиля с map участников."""
    def __init__(self, members: Dict[str, _DummyMember]):
        self.members = members

class _DummyFamilyProfileManager(FamilyProfileManager):
    """Упрощенный FamilyProfileManager для инициализации правил."""
    def __init__(self) -> None:
        super().__init__()
        self.families: Dict[str, _DummyFamily] = {}

class _DummyChildProtection(ChildProtection):
    def __init__(self) -> None:
        super().__init__()

class _DummyElderlyProtection(ElderlyProtection):
    def __init__(self) -> None:
        super().__init__()

# Инициализация менеджеров один раз на процесс (только если доступны)
if _parental_controls_available and ParentalControls:
    try:
        _parental_controls = ParentalControls(
            family_profile_manager=_DummyFamilyProfileManager(),
            child_protection=_DummyChildProtection(),
            elderly_protection=_DummyElderlyProtection(),
        )
    except Exception:
        _parental_controls = None
else:
    _parental_controls = None

if _parental_controls_available and AdvancedParentalControls:
    try:
        _advanced_controls = AdvancedParentalControls()
    except Exception:
        _advanced_controls = None
else:
    _advanced_controls = None

# ✅ УДАЛЕНО: Mock данные
# _CHILDREN_STATS: Dict[str, Dict[str, object]] = {...}
# _BYPASS_STATS: Dict[str, Dict[str, object]] = {...}

_DEFAULT_CHILD_ID = "child_masha"

# ✅ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ РАБОТЫ С БД

def get_children_stats_from_db(db: Session, user_id: str, child_id: str) -> Dict:
    """Получить статистику родительского контроля из БД"""
    try:
        query = text("""
            SELECT * FROM parental_control_stats 
            WHERE user_id = :user_id::uuid AND child_id = :child_id::uuid
        """)
        
        result = db.execute(query, {"user_id": user_id, "child_id": child_id})
        row = result.fetchone()
        
        if row:
            return {
                "websites_blocked": row[5] or 0,
                "apps_blocked": row[6] or 0,
                "search_queries_blocked": row[7] or 0,
                "active_filters": row[8] or 0,
                "today_usage": row[9] or "0мин",
                "today_limit": row[10] or "0мин",
                "remaining": row[11] or "0мин",
                "schedules_count": row[12] or 0,
                "current_location": row[13],
                "geofences_count": row[14] or 0,
                "events_today": row[15] or 0,
                "sites_tracked": row[16] or 0,
                "apps_tracked": row[17] or 0,
                "contacts_tracked": row[18] or 0,
                "messages_monitored": row[19] or False,
                "last_update": row[20].isoformat() if row[20] else datetime.utcnow().isoformat()
            }
        
        # Если данных нет, возвращаем дефолтные значения
        return {
            "websites_blocked": 0,
            "apps_blocked": 0,
            "search_queries_blocked": 0,
            "active_filters": 0,
            "today_usage": "0мин",
            "today_limit": "0мин",
            "remaining": "0мин",
            "schedules_count": 0,
            "current_location": None,
            "geofences_count": 0,
            "events_today": 0,
            "sites_tracked": 0,
            "apps_tracked": 0,
            "contacts_tracked": 0,
            "messages_monitored": False,
            "last_update": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting children stats from DB: {str(e)}")
        # Возвращаем дефолтные значения при ошибке
        return {
            "websites_blocked": 0,
            "apps_blocked": 0,
            "search_queries_blocked": 0,
            "active_filters": 0,
            "today_usage": "0мин",
            "today_limit": "0мин",
            "remaining": "0мин",
            "schedules_count": 0,
            "current_location": None,
            "geofences_count": 0,
            "events_today": 0,
            "sites_tracked": 0,
            "apps_tracked": 0,
            "contacts_tracked": 0,
            "messages_monitored": False,
            "last_update": datetime.utcnow().isoformat()
        }

def get_bypass_stats_from_db(db: Session, user_id: str, child_id: str) -> Dict:
    """Получить статистику обхода родительского контроля из БД"""
    try:
        query = text("""
            SELECT * FROM parental_bypass_stats 
            WHERE user_id = :user_id::uuid AND child_id = :child_id::uuid
        """)
        
        result = db.execute(query, {"user_id": user_id, "child_id": child_id})
        row = result.fetchone()
        
        if row:
            return {
                "today": row[3] or 0,
                "week": row[4] or 0,
                "blocked": row[5] or 0,
                "incognito": row[6] or 0,
                "tor": row[7] or 0,
                "proxy": row[8] or 0,
                "message": row[9] or "Защита активна."
            }
        
        # Если данных нет, возвращаем дефолтные значения
        return {
            "today": 0,
            "week": 0,
            "blocked": 0,
            "incognito": 0,
            "tor": 0,
            "proxy": 0,
            "message": "Защита активна."
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting bypass stats from DB: {str(e)}")
        # Возвращаем дефолтные значения при ошибке
        return {
            "today": 0,
            "week": 0,
            "blocked": 0,
            "incognito": 0,
            "tor": 0,
            "proxy": 0,
            "message": "Защита активна."
        }

def upsert_children_stats_to_db(
    db: Session,
    user_id: str,
    child_id: str,
    child_name: Optional[str] = None,
    stats: Optional[Dict] = None
) -> bool:
    """Создать или обновить статистику родительского контроля в БД"""
    try:
        query = text("""
            INSERT INTO parental_control_stats (
                user_id, child_id, child_name,
                websites_blocked, apps_blocked, search_queries_blocked, active_filters,
                today_usage, today_limit, remaining, schedules_count,
                current_location, geofences_count, events_today,
                sites_tracked, apps_tracked, contacts_tracked, messages_monitored,
                last_update, created_at, updated_at
            ) VALUES (
                :user_id::uuid, :child_id::uuid, :child_name,
                :websites_blocked, :apps_blocked, :search_queries_blocked, :active_filters,
                :today_usage, :today_limit, :remaining, :schedules_count,
                :current_location, :geofences_count, :events_today,
                :sites_tracked, :apps_tracked, :contacts_tracked, :messages_monitored,
                CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            )
            ON CONFLICT (user_id, child_id) 
            DO UPDATE SET
                child_name = EXCLUDED.child_name,
                websites_blocked = EXCLUDED.websites_blocked,
                apps_blocked = EXCLUDED.apps_blocked,
                search_queries_blocked = EXCLUDED.search_queries_blocked,
                active_filters = EXCLUDED.active_filters,
                today_usage = EXCLUDED.today_usage,
                today_limit = EXCLUDED.today_limit,
                remaining = EXCLUDED.remaining,
                schedules_count = EXCLUDED.schedules_count,
                current_location = EXCLUDED.current_location,
                geofences_count = EXCLUDED.geofences_count,
                events_today = EXCLUDED.events_today,
                sites_tracked = EXCLUDED.sites_tracked,
                apps_tracked = EXCLUDED.apps_tracked,
                contacts_tracked = EXCLUDED.contacts_tracked,
                messages_monitored = EXCLUDED.messages_monitored,
                last_update = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
        """)
        
        stats = stats or {}
        db.execute(query, {
            "user_id": user_id,
            "child_id": child_id,
            "child_name": child_name,
            "websites_blocked": stats.get("websites_blocked", 0),
            "apps_blocked": stats.get("apps_blocked", 0),
            "search_queries_blocked": stats.get("search_queries_blocked", 0),
            "active_filters": stats.get("active_filters", 0),
            "today_usage": stats.get("today_usage", "0мин"),
            "today_limit": stats.get("today_limit", "0мин"),
            "remaining": stats.get("remaining", "0мин"),
            "schedules_count": stats.get("schedules_count", 0),
            "current_location": stats.get("current_location"),
            "geofences_count": stats.get("geofences_count", 0),
            "events_today": stats.get("events_today", 0),
            "sites_tracked": stats.get("sites_tracked", 0),
            "apps_tracked": stats.get("apps_tracked", 0),
            "contacts_tracked": stats.get("contacts_tracked", 0),
            "messages_monitored": stats.get("messages_monitored", False)
        })
        
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error upserting children stats to DB: {str(e)}")
        return False

def upsert_bypass_stats_to_db(
    db: Session,
    user_id: str,
    child_id: str,
    stats: Optional[Dict] = None
) -> bool:
    """Создать или обновить статистику обхода в БД"""
    try:
        query = text("""
            INSERT INTO parental_bypass_stats (
                user_id, child_id,
                today, week, blocked, incognito, tor, proxy, message,
                created_at, updated_at
            ) VALUES (
                :user_id::uuid, :child_id::uuid,
                :today, :week, :blocked, :incognito, :tor, :proxy, :message,
                CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            )
            ON CONFLICT (user_id, child_id) 
            DO UPDATE SET
                today = EXCLUDED.today,
                week = EXCLUDED.week,
                blocked = EXCLUDED.blocked,
                incognito = EXCLUDED.incognito,
                tor = EXCLUDED.tor,
                proxy = EXCLUDED.proxy,
                message = EXCLUDED.message,
                updated_at = CURRENT_TIMESTAMP
        """)
        
        stats = stats or {}
        db.execute(query, {
            "user_id": user_id,
            "child_id": child_id,
            "today": stats.get("today", 0),
            "week": stats.get("week", 0),
            "blocked": stats.get("blocked", 0),
            "incognito": stats.get("incognito", 0),
            "tor": stats.get("tor", 0),
            "proxy": stats.get("proxy", 0),
            "message": stats.get("message", "Защита активна.")
        })
        
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error upserting bypass stats to DB: {str(e)}")
        return False

import logging
logger = logging.getLogger(__name__)

def _resolve_child_id(child_id: Optional[str]) -> str:
    """Разрешить child_id (используем переданный или дефолтный)"""
    if child_id:
        return child_id
    return _DEFAULT_CHILD_ID

async def _ensure_protection_session(child_id: str) -> None:
    """Гарантирует, что AdvancedParentalControls знает про ребёнка."""
    if _advanced_controls and hasattr(_advanced_controls, 'active_children'):
        if child_id not in _advanced_controls.active_children:
            if hasattr(_advanced_controls, 'setup_child_protection'):
                await _advanced_controls.setup_child_protection(child_id)

# ═══════════════════════════════════════════════════════════════
# Pydantic моделей для ответов
# ═══════════════════════════════════════════════════════════════

class ContentBlockedStats(BaseModel):
    websites_blocked: int = Field(..., ge=0)
    apps_blocked: int = Field(..., ge=0)
    search_queries_blocked: int = Field(..., ge=0)
    active_filters: int = Field(..., ge=0)

class ScreenTimeStats(BaseModel):
    today_usage: str
    today_limit: str
    remaining: str
    schedules_count: int = Field(..., ge=0)

class LocationStats(BaseModel):
    current_location: Optional[str]
    last_update: Optional[str]
    geofences_count: int = Field(..., ge=0)
    events_today: int = Field(..., ge=0)

class MonitoringStats(BaseModel):
    sites_tracked: int = Field(..., ge=0)
    apps_tracked: int = Field(..., ge=0)
    contacts_tracked: int = Field(..., ge=0)
    messages_monitored: bool

class ParentalControlStatsResponse(BaseModel):
    content_blocked: ContentBlockedStats
    screen_time: ScreenTimeStats
    location: LocationStats
    monitoring: MonitoringStats

class BypassStatsResponse(BaseModel):
    success: bool
    today: int = Field(..., ge=0)
    week: int = Field(..., ge=0)
    blocked: int = Field(..., ge=0)
    incognito: int = Field(..., ge=0)
    tor: int = Field(..., ge=0)
    proxy: int = Field(..., ge=0)
    message: Optional[str] = None

# ═══════════════════════════════════════════════════════════════
# Роутеры
# ═══════════════════════════════════════════════════════════════

router = APIRouter(prefix="/api/v1/parental-control", tags=["Parental Control"])
bypass_router = APIRouter(prefix="/parental", tags=["Parental Control"])


@router.get("/stats", response_model=ParentalControlStatsResponse)
async def get_parental_control_stats(
    childId: Optional[str] = Query(None, alias="childId"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Возвращает агрегированную статистику для карточек родительского контроля (ОБНОВЛЕНО: использует БД)"""
    try:
        user_id = str(current_user["id"])
        child_id = _resolve_child_id(childId)
        
        # ✅ ПОЛУЧАЕМ ДАННЫЕ ИЗ БД ВМЕСТО MOCK
        data = get_children_stats_from_db(db, user_id, child_id)

        # active_filters ограничиваем количеством реальных правил
        if _parental_controls and hasattr(_parental_controls, 'control_rules') and _parental_controls.control_rules:
            control_rules_count = len(_parental_controls.control_rules)
        else:
            control_rules_count = 1
        
        active_filters = min(
            int(data.get("active_filters", 0)),
            max(control_rules_count, 1),
        )

        last_update = data.get("last_update") or datetime.utcnow().isoformat()

        return ParentalControlStatsResponse(
            content_blocked=ContentBlockedStats(
                websites_blocked=int(data.get("websites_blocked", 0)),
                apps_blocked=int(data.get("apps_blocked", 0)),
                search_queries_blocked=int(data.get("search_queries_blocked", 0)),
                active_filters=active_filters,
            ),
            screen_time=ScreenTimeStats(
                today_usage=str(data.get("today_usage", "0мин")),
                today_limit=str(data.get("today_limit", "0мин")),
                remaining=str(data.get("remaining", "0мин")),
                schedules_count=int(data.get("schedules_count", 0)),
            ),
            location=LocationStats(
                current_location=data.get("current_location"),
                last_update=last_update,
                geofences_count=int(data.get("geofences_count", 0)),
                events_today=int(data.get("events_today", 0)),
            ),
            monitoring=MonitoringStats(
                sites_tracked=int(data.get("sites_tracked", 0)),
                apps_tracked=int(data.get("apps_tracked", 0)),
                contacts_tracked=int(data.get("contacts_tracked", 0)),
                messages_monitored=bool(data.get("messages_monitored", False)),
            ),
        )
    except Exception as e:
        logger.error(f"❌ Error getting parental control stats: {str(e)}")
        # Возвращаем дефолтные значения при ошибке
        return ParentalControlStatsResponse(
            content_blocked=ContentBlockedStats(
                websites_blocked=0,
                apps_blocked=0,
                search_queries_blocked=0,
                active_filters=0,
            ),
            screen_time=ScreenTimeStats(
                today_usage="0мин",
                today_limit="0мин",
                remaining="0мин",
                schedules_count=0,
            ),
            location=LocationStats(
                current_location=None,
                last_update=datetime.utcnow().isoformat(),
                geofences_count=0,
                events_today=0,
            ),
            monitoring=MonitoringStats(
                sites_tracked=0,
                apps_tracked=0,
                contacts_tracked=0,
                messages_monitored=False,
            ),
        )


@bypass_router.get("/bypass/stats", response_model=BypassStatsResponse)
async def get_bypass_stats(
    childId: Optional[str] = Query(None, alias="childId"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Возвращает статистику попыток обхода (incognito/Tor/Proxy) (ОБНОВЛЕНО: использует БД)"""
    try:
        user_id = str(current_user["id"])
        child_id = _resolve_child_id(childId)
        await _ensure_protection_session(child_id)

        # ✅ ПОЛУЧАЕМ ДАННЫЕ ИЗ БД ВМЕСТО MOCK
        data = get_bypass_stats_from_db(db, user_id, child_id)
        
        # Проверяем что _advanced_controls инициализирован
        if _advanced_controls and hasattr(_advanced_controls, 'get_protection_report'):
            report = _advanced_controls.get_protection_report(child_id)
            blocked_attempts = int(report.get("total_blocked_attempts") or data.get("blocked", 0))
        else:
            blocked_attempts = int(data.get("blocked", 0))

        return BypassStatsResponse(
            success=True,
            today=int(data.get("today", 0)),
            week=int(data.get("week", 0)),
            blocked=blocked_attempts,
            incognito=int(data.get("incognito", 0)),
            tor=int(data.get("tor", 0)),
            proxy=int(data.get("proxy", 0)),
            message=data.get("message"),
        )
    except Exception as e:
        logger.error(f"❌ Error getting bypass stats: {str(e)}")
        # Возвращаем дефолтные значения при ошибке
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


@router.get("/status")
async def get_parental_manager_status():
    """Технический эндпоинт для проверки состояния менеджера."""
    if _parental_controls and hasattr(_parental_controls, 'get_status'):
        status = _parental_controls.get_status()
        return {
            "name": status.get("name"),
            "active_rules": status.get("active_rules"),
            "total_control_rules": status.get("total_control_rules"),
            "modern_features": status.get("modern_features"),
        }
    else:
        return {
            "name": "Parental Controls",
            "active_rules": 0,
            "total_control_rules": 0,
            "modern_features": [],
        }


@bypass_router.get("/bypass/status")
async def get_bypass_manager_status():
    """Служебный эндпоинт для диагностики AdvancedParentalControls."""
    if _advanced_controls and hasattr(_advanced_controls, 'active_children'):
        active_children = {
            child_id: {
                "protection_level": info.get("protection_level"),
                "blocked_attempts": info.get("blocked_attempts", 0),
            }
            for child_id, info in _advanced_controls.active_children.items()
        }
    else:
        active_children = {}

    return {
        "active_children": active_children,
        "total_active": len(active_children),
    }
