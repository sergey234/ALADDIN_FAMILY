# -*- coding: utf-8 -*-
"""
Parental Control API Router
--------------------------
Временные (mock + light integration) endpoints, обеспечивающие мобильные приложения
данными по родительскому контролю до полноценной интеграции с бекендом.
"""

from datetime import datetime
from typing import Dict, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from security.family.parental_controls import ParentalControls
from security.family.advanced_parental_controls import AdvancedParentalControls
from security.types.security_types import (
    FamilyProfileManager,
    ChildProtection,
    ElderlyProtection,
    FamilyRole,
    AgeGroup,
)

# ═══════════════════════════════════════════════════════════════
# Вспомогательные классы для изоляции от тяжелых зависимостей
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
        self.families: Dict[str, _DummyFamily] = {
            "family_001": _DummyFamily(
                {
                    "child_masha": _DummyMember(
                        member_id="child_masha",
                        name="Маша",
                        role=FamilyRole.CHILD,
                        age_group=AgeGroup.CHILD,
                    )
                }
            )
        }


class _DummyChildProtection(ChildProtection):
    def __init__(self) -> None:
        super().__init__()


class _DummyElderlyProtection(ElderlyProtection):
    def __init__(self) -> None:
        super().__init__()


# Инициализация менеджеров один раз на процесс
_parental_controls = ParentalControls(
    family_profile_manager=_DummyFamilyProfileManager(),
    child_protection=_DummyChildProtection(),
    elderly_protection=_DummyElderlyProtection(),
)

_advanced_controls = AdvancedParentalControls()

# ═══════════════════════════════════════════════════════════════
# Статические данные (mock) для быстрой отдачи реальных структур
# ═══════════════════════════════════════════════════════════════

_DEFAULT_CHILD_ID = "child_masha"

_CHILDREN_STATS: Dict[str, Dict[str, object]] = {
    "child_masha": {
        "websites_blocked": 128,
        "apps_blocked": 32,
        "search_queries_blocked": 74,
        "active_filters": 4,
        "today_usage": "1ч 22мин",
        "today_limit": "2ч",
        "remaining": "38мин",
        "schedules_count": 3,
        "current_location": "Дом",
        "last_update": "2025-11-09T09:30:00+03:00",
        "geofences_count": 5,
        "events_today": 2,
        "sites_tracked": 342,
        "apps_tracked": 28,
        "contacts_tracked": 12,
        "messages_monitored": True,
    },
    "child_petya": {
        "websites_blocked": 96,
        "apps_blocked": 24,
        "search_queries_blocked": 51,
        "active_filters": 3,
        "today_usage": "58мин",
        "today_limit": "1ч 30мин",
        "remaining": "32мин",
        "schedules_count": 2,
        "current_location": "Школа",
        "last_update": "2025-11-09T12:15:00+03:00",
        "geofences_count": 3,
        "events_today": 1,
        "sites_tracked": 218,
        "apps_tracked": 19,
        "contacts_tracked": 8,
        "messages_monitored": True,
    },
}

_BYPASS_STATS: Dict[str, Dict[str, object]] = {
    "child_masha": {
        "today": 2,
        "week": 6,
        "blocked": 2,
        "incognito": 3,
        "tor": 1,
        "proxy": 2,
        "message": "Защита активна. Попытки обхода заблокированы автоматически.",
    },
    "child_petya": {
        "today": 1,
        "week": 3,
        "blocked": 1,
        "incognito": 2,
        "tor": 0,
        "proxy": 1,
        "message": "Обнаружены разовые попытки использования прокси.",
    },
}


def _resolve_child_id(child_id: Optional[str]) -> str:
    if child_id and child_id in _CHILDREN_STATS:
        return child_id
    return _DEFAULT_CHILD_ID


async def _ensure_protection_session(child_id: str) -> None:
    """Гарантирует, что AdvancedParentalControls знает про ребёнка."""
    if child_id not in _advanced_controls.active_children:
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
async def get_parental_control_stats(childId: Optional[str] = Query(None, alias="childId")):
    """Возвращает агрегированную статистику для карточек родительского контроля."""
    child_id = _resolve_child_id(childId)
    data = _CHILDREN_STATS.get(child_id, _CHILDREN_STATS[_DEFAULT_CHILD_ID])

    # active_filters ограничиваем количеством реальных правил
    active_filters = min(
        int(data.get("active_filters", 0)),
        max(len(_parental_controls.control_rules), 1),
    )

    # Последнее обновление, если не задано, используем текущий момент
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


@bypass_router.get("/bypass/stats", response_model=BypassStatsResponse)
async def get_bypass_stats(childId: Optional[str] = Query(None, alias="childId")):
    """Возвращает статистику попыток обхода (incognito/Tor/Proxy)."""
    child_id = _resolve_child_id(childId)
    await _ensure_protection_session(child_id)

    data = _BYPASS_STATS.get(child_id, _BYPASS_STATS[_DEFAULT_CHILD_ID])
    report = _advanced_controls.get_protection_report(child_id)

    blocked_attempts = int(report.get("total_blocked_attempts") or data.get("blocked", 0))

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


# ═══════════════════════════════════════════════════════════════
# Системные эндпоинты (опционально)
# ═══════════════════════════════════════════════════════════════


@router.get("/status")
async def get_parental_manager_status():
    """Технический эндпоинт для проверки состояния менеджера."""
    status = _parental_controls.get_status()
    return {
        "name": status.get("name"),
        "active_rules": status.get("active_rules"),
        "total_control_rules": status.get("total_control_rules"),
        "modern_features": status.get("modern_features"),
    }


@bypass_router.get("/bypass/status")
async def get_bypass_manager_status():
    """Служебный эндпоинт для диагностики AdvancedParentalControls."""
    active_children = {
        child_id: {
            "protection_level": info.get("protection_level"),
            "blocked_attempts": info.get("blocked_attempts", 0),
        }
        for child_id, info in _advanced_controls.active_children.items()
    }

    return {
        "active_children": active_children,
        "total_active": len(active_children),
    }
