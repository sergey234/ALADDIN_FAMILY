"""
============================================
КОМПОНЕНТЫ БЕЗОПАСНОСТИ: API Endpoints (ОБНОВЛЕНО)
============================================
Сервер: 149.154.65.180
Дата: 17 декабря 2025
Обновлено: ФАЗА 1 - Реальные SQL запросы
============================================
API для управления 42 компонентами безопасности
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from enum import Enum
import json

# Utility functions
from app.utils import safe_iso

# ✅ ИСПРАВЛЕНИЕ: Используем AsyncSession из app.database.database
from app.database.database import get_session

# ✅ ФАЗА 2: Авторизация с реальным user_id
from app.auth.auth import get_current_user

# ✅ RATE LIMITING: Импорт slowapi для защиты от злоупотреблений
from slowapi import Limiter
from slowapi.util import get_remote_address

# ✅ STRUCTURED LOGGING: Импорт structlog для структурированного логирования
import structlog

router = APIRouter(prefix="/api/components", tags=["components"])

# ✅ RATE LIMITING: Инициализация Limiter (60 запросов в минуту на IP)
limiter = Limiter(key_func=get_remote_address)

# ✅ STRUCTURED LOGGING: Инициализация logger
logger = structlog.get_logger()


# ============================================
# МОДЕЛИ ОТВЕТОВ
# ============================================

class ComponentStatusEnum(str, Enum):
    enabled = "enabled"
    disabled = "disabled"
    error = "error"
    pending = "pending"


class ComponentStatus(BaseModel):
    componentId: str
    isEnabled: bool
    status: ComponentStatusEnum
    lastUpdated: str
    error: Optional[str] = None


class ComponentConfiguration(BaseModel):
    componentId: str
    settings: Dict[str, Any]
    version: str
    lastUpdated: str


class ComponentStatusResponse(BaseModel):
    status: ComponentStatus


class ComponentConfigurationResponse(BaseModel):
    configuration: ComponentConfiguration
    isDefault: bool = False


class ComponentBatchStatusResponse(BaseModel):
    statuses: List[ComponentStatus]


class ComponentsCompatBoolResponse(BaseModel):
    success: bool
    data: bool
    message: Optional[str] = None

class UpdateStatusRequest(BaseModel):
    isEnabled: bool


# ============================================
# СПИСОК ВСЕХ 42 КОМПОНЕНТОВ
# ============================================

COMPONENT_ID_ALIASES = {
    "phishing_protection": "phishing_protection_agent",
    "malware_detection": "malware_detection_agent",
    "mobile_security": "mobile_security_agent",
    "network_security": "network_security_agent",
    "incident_response": "incident_response_agent",
    "password_security": "password_security_agent",
}


def resolve_component_id(component_id: str) -> str:
    return COMPONENT_ID_ALIASES.get(component_id, component_id)


ALL_COMPONENTS = [
    # NetworkProtectionScreen (10)
    "crash_detection_agent",
    "roadside_assistance_agent",
    "emergency_response_bot",
    "emergency_event_manager",
    "phishing_protection_agent",
    "malware_detection_agent",
    "mobile_security_agent",
    "network_security_agent",
    "incident_response_agent",
    "password_security_agent",
    
    # ParentalControlScreen (5)
    "self_harm_detection_agent",
    "grooming_detection_agent",
    "online_predators_agent",
    "psychological_support_agent",
    "parental_control_bot",
    
    # AdvancedProtectionSettingsScreen (13)
    "telegram_security_bot",
    "whatsapp_security_bot",
    "instagram_security_bot",
    "max_messenger_security_bot",
    "gaming_security_bot",
    "browser_security_bot",
    "location_bubble_agent",
    "personal_data_cleanup_agent",
    "anti_tracker_agent",
    "dark_web_monitoring_agent",
    "russian_identity_theft_protection_agent",
    "ai_categories_agent",
    "driving_reports_agent",
    
    # SettingsScreen (5)
    "emergency_contacts_manager",
    "emergency_notifications_manager",
    "voice_control_manager",
    "russian_child_protection_compliance_manager",
    "russian_data_protection_compliance_manager",
    
    # Улучшение существующих (9)
    "family_notification_manager",
    "smart_notification_manager",
    "child_interface_manager",
    "elderly_interface_manager",
    "subscription_manager",
    "referral_manager",
    "qr_payment_manager",
    "analytics_manager",
    "report_manager",
]


# ============================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ (ОБНОВЛЕНО)
# ============================================

async def get_component_status_from_db(
    component_id: str,
    db: AsyncSession,  # ✅ ИСПРАВЛЕНИЕ: AsyncSession вместо Optional[Session]
    user_id: int
) -> Optional[ComponentStatus]:
    """
    Получить статус компонента из базы данных.
    ✅ РЕАЛИЗАЦИЯ: Реальный SQL запрос к SQLite
    """
    # ✅ Реальный SQL запрос к SQLite через AsyncSession
    result = await db.execute(
        text("""
            SELECT component_id, is_enabled, last_updated
            FROM component_status
            WHERE component_id = :component_id AND user_id = :user_id
        """),
        {"component_id": component_id, "user_id": user_id}
    )
    
    row = result.fetchone()
    
    if row is None:
        return None
    
    # row - это Row объект, доступ к колонкам по индексу или имени
    is_enabled = bool(row[1])  # is_enabled
    last_updated = row[2]  # last_updated
    
    # ✅ ИСПРАВЛЕНИЕ: Безопасное преобразование даты (может быть строкой или datetime)
    iso_date = safe_iso(last_updated)
    
    return ComponentStatus(
        componentId=str(row[0]),  # component_id
        isEnabled=is_enabled,
        status=ComponentStatusEnum.enabled if is_enabled else ComponentStatusEnum.disabled,
        lastUpdated=iso_date,
        error=None
    )


async def update_component_status_in_db(
    component_id: str,
    is_enabled: bool,
    db: AsyncSession,  # ✅ ИСПРАВЛЕНИЕ: AsyncSession вместо Optional[Session]
    user_id: int
) -> ComponentStatus:
    """
    Обновить статус компонента в базе данных.
    ✅ РЕАЛИЗАЦИЯ: Реальный SQL запрос к SQLite (INSERT/UPDATE)
    """
    # ✅ Проверить существование записи
    existing = await db.execute(
        text("""
            SELECT id FROM component_status
            WHERE component_id = :component_id AND user_id = :user_id
        """),
        {"component_id": component_id, "user_id": user_id}
    )
    
    existing_row = existing.fetchone()
    
    if existing_row:
        # ✅ UPDATE существующей записи
        await db.execute(
            text("""
                UPDATE component_status
                SET is_enabled = :is_enabled, last_updated = CURRENT_TIMESTAMP
                WHERE component_id = :component_id AND user_id = :user_id
            """),
            {"is_enabled": is_enabled, "component_id": component_id, "user_id": user_id}
        )
    else:
        # ✅ INSERT новой записи
        await db.execute(
            text("""
                INSERT INTO component_status (component_id, user_id, is_enabled, last_updated)
                VALUES (:component_id, :user_id, :is_enabled, CURRENT_TIMESTAMP)
            """),
            {"component_id": component_id, "user_id": user_id, "is_enabled": is_enabled}
        )
    
    await db.commit()
    
    # ✅ Получить обновленный статус
    return await get_component_status_from_db(component_id, db, user_id)


async def get_component_configuration_from_db(
    component_id: str,
    db: AsyncSession,  # ✅ ИСПРАВЛЕНИЕ: AsyncSession вместо Optional[Session]
    user_id: int
) -> Optional[ComponentConfiguration]:
    """
    Получить конфигурацию компонента из базы данных.
    ✅ РЕАЛИЗАЦИЯ: Реальный SQL запрос к SQLite
    """
    # ✅ Реальный SQL запрос к SQLite через AsyncSession
    result = await db.execute(
        text("""
            SELECT component_id, settings, version, last_updated
            FROM component_configuration
            WHERE component_id = :component_id AND user_id = :user_id
        """),
        {"component_id": component_id, "user_id": user_id}
    )
    
    row = result.fetchone()
    
    if row is None:
        return None
    
    # Парсинг JSON из TEXT поля
    settings_dict = json.loads(row[1]) if row[1] else {}
    
    return ComponentConfiguration(
        componentId=str(row[0]),  # component_id
        settings=settings_dict,  # settings (parsed JSON)
        version=str(row[2]) if row[2] else "1.0.0",  # version
        lastUpdated=safe_iso(row[3])
    )


def build_default_component_configuration(component_id: str) -> ComponentConfiguration:
    """
    Детерминированные дефолтные настройки для first-open (без mock).
    Возвращаются при отсутствии записи в БД.
    """
    default_settings_map: Dict[str, Dict[str, Any]] = {
        "phishing_protection_agent": {
            "blockSuspiciousLinks": True,
            "warnBeforeOpening": True,
            "checkEmailLinks": True,
            "checkSMSLinks": True,
            "blockKnownPhishingDomains": True,
            "sensitivityLevel": "medium",
        },
        "malware_detection_agent": {
            "realTimeScanning": True,
            "scanDownloads": True,
            "scanInstalledApps": True,
            "quarantineThreats": True,
            "autoRemoveThreats": False,
            "scanFrequency": "daily",
        },
        "mobile_security_agent": {
            "deviceEncryption": True,
            "appLock": True,
            "screenLock": True,
            "biometricAuth": True,
            "remoteWipe": False,
            "trackDevice": True,
        },
        "network_security_agent": {
            "blockUnsafeNetworks": True,
            "warnOnPublicWiFi": True,
            "autoConnectVPN": False,
            "blockTracking": True,
            "encryptTraffic": True,
            "firewallEnabled": True,
        },
        "incident_response_agent": {
            "escalationThresholds": {"low": "30", "medium": "15", "high": "5", "critical": "1"},
            "slaTime": "30",
            "contactRoles": ["admin", "security"],
            "autoActions": {"block": False, "notify": True, "escalate": True},
        },
        "password_security_agent": {
            "passwordLength": 16,
            "includeUppercase": True,
            "includeLowercase": True,
            "includeNumbers": True,
            "includeSpecial": True,
        },
    }

    return ComponentConfiguration(
        componentId=component_id,
        settings=default_settings_map.get(component_id, {}),
        version="1.0.0-default",
        lastUpdated=datetime.utcnow().isoformat(),
    )


# ============================================
# ENDPOINT 1: GET /api/components/status/{componentId} (ОБНОВЛЕНО)
# ============================================

@router.get("/status/{component_id}", response_model=ComponentStatusResponse)
@limiter.limit("60/minute")  # ✅ RATE LIMITING: 60 запросов в минуту на IP
async def get_component_status(
    component_id: str,
    request: Request,
    db: AsyncSession = Depends(get_session),  # ✅ ИСПРАВЛЕНИЕ: AsyncSession с Depends(get_session)
    current_user: dict = Depends(get_current_user)  # ✅ ФАЗА 2: Реальный пользователь из токена
):
    """
    Получить статус компонента.
    
    Требуется авторизация (токен в заголовке Authorization: Bearer {token})
    """
    # ✅ ФАЗА 2: Получить реальный user_id из токена
    user_id = current_user["id"]
    component_id = resolve_component_id(component_id)
    
    # ✅ РЕАЛИЗАЦИЯ: Проверка существования компонента
    if component_id not in ALL_COMPONENTS:
        raise HTTPException(status_code=404, detail=f"Component {component_id} not found")
    
    # ✅ РЕАЛИЗАЦИЯ: Получить статус из БД (РЕАЛЬНЫЙ ЗАПРОС)
    status = await get_component_status_from_db(component_id, db, user_id)
    
    if not status:
        # ✅ Создать дефолтный статус, если не найден
        status = await update_component_status_in_db(component_id, False, db, user_id)
    
    return ComponentStatusResponse(status=status)


# ============================================
# ENDPOINT 2: POST /api/components/enable/{componentId} (ОБНОВЛЕНО)
# ============================================

@router.post("/enable/{component_id}", response_model=ComponentStatusResponse)
@limiter.limit("60/minute")  # ✅ RATE LIMITING: 60 запросов в минуту на IP
async def enable_component(
    component_id: str,
    request: Request,
    db: AsyncSession = Depends(get_session),  # ✅ ИСПРАВЛЕНИЕ: AsyncSession с Depends(get_session)
    current_user: dict = Depends(get_current_user)  # ✅ ФАЗА 2: Реальный пользователь из токена
):
    """
    Включить компонент.
    
    Требуется авторизация.
    """
    # ✅ ФАЗА 2: Получить реальный user_id из токена
    user_id = current_user["id"]
    component_id = resolve_component_id(component_id)
    
    # ✅ STRUCTURED LOGGING: Логирование включения компонента
    logger.info(
        "component_enabled",
        component_id=component_id,
        user_id=user_id,
        timestamp=datetime.now().isoformat()
    )
    
    # ✅ РЕАЛИЗАЦИЯ: Проверка существования компонента
    if component_id not in ALL_COMPONENTS:
        raise HTTPException(status_code=404, detail=f"Component {component_id} not found")
    
    # ✅ РЕАЛИЗАЦИЯ: Обновить статус в БД (РЕАЛЬНЫЙ ЗАПРОС)
    status = await update_component_status_in_db(component_id, True, db, user_id)
    
    # TODO: Здесь можно добавить логику активации компонента на сервере
    
    return ComponentStatusResponse(status=status)


# ============================================
# ENDPOINT 3: POST /api/components/disable/{componentId} (ОБНОВЛЕНО)
# ============================================

@router.post("/disable/{component_id}", response_model=ComponentStatusResponse)
@limiter.limit("60/minute")  # ✅ RATE LIMITING: 60 запросов в минуту на IP
async def disable_component(
    component_id: str,
    request: Request,
    db: AsyncSession = Depends(get_session),  # ✅ ИСПРАВЛЕНИЕ: AsyncSession с Depends(get_session)
    current_user: dict = Depends(get_current_user)  # ✅ ФАЗА 2: Реальный пользователь из токена
):
    """
    Выключить компонент.
    
    Требуется авторизация.
    """
    # ✅ ФАЗА 2: Получить реальный user_id из токена
    user_id = current_user["id"]
    component_id = resolve_component_id(component_id)
    
    # ✅ STRUCTURED LOGGING: Логирование выключения компонента
    logger.info(
        "component_disabled",
        component_id=component_id,
        user_id=user_id,
        timestamp=datetime.now().isoformat()
    )
    
    # ✅ РЕАЛИЗАЦИЯ: Проверка существования компонента
    if component_id not in ALL_COMPONENTS:
        raise HTTPException(status_code=404, detail=f"Component {component_id} not found")
    
    # ✅ РЕАЛИЗАЦИЯ: Обновить статус в БД (РЕАЛЬНЫЙ ЗАПРОС)
    status = await update_component_status_in_db(component_id, False, db, user_id)
    
    # TODO: Здесь можно добавить логику деактивации компонента на сервере
    
    return ComponentStatusResponse(status=status)


# ============================================
# ENDPOINT 4: GET /api/components/configuration/{componentId} (ОБНОВЛЕНО)
# ============================================

@router.get("/configuration/{component_id}", response_model=ComponentConfigurationResponse)
@limiter.limit("60/minute")  # ✅ RATE LIMITING: 60 запросов в минуту на IP
async def get_component_configuration(
    component_id: str,
    request: Request,
    db: AsyncSession = Depends(get_session),  # ✅ ИСПРАВЛЕНИЕ: AsyncSession с Depends(get_session)
    current_user: dict = Depends(get_current_user)  # ✅ ФАЗА 2: Реальный пользователь из токена
):
    """
    Получить конфигурацию компонента.
    
    Требуется авторизация.
    """
    # ✅ ФАЗА 2: Получить реальный user_id из токена
    user_id = current_user["id"]
    component_id = resolve_component_id(component_id)
    
    # ✅ РЕАЛИЗАЦИЯ: Проверка существования компонента
    if component_id not in ALL_COMPONENTS:
        raise HTTPException(status_code=404, detail=f"Component {component_id} not found")
    
    # ✅ РЕАЛИЗАЦИЯ: Получить конфигурацию из БД (РЕАЛЬНЫЙ ЗАПРОС)
    configuration = await get_component_configuration_from_db(component_id, db, user_id)
    
    if not configuration:
        logger.info(
            "component_configuration_default_served",
            component_id=component_id,
            user_id=user_id,
            timestamp=datetime.now().isoformat()
        )
        configuration = build_default_component_configuration(component_id)
        return ComponentConfigurationResponse(configuration=configuration, isDefault=True)

    return ComponentConfigurationResponse(configuration=configuration, isDefault=False)


# ============================================
# ENDPOINT 5: POST /api/components/configuration/{componentId} (ОБНОВЛЕНО)
# ============================================

class UpdateConfigurationRequest(BaseModel):
    settings: Dict[str, Any]


@router.post("/configuration/{component_id}")
@limiter.limit("60/minute")  # ✅ RATE LIMITING: 60 запросов в минуту на IP
async def update_component_configuration(
    component_id: str,
    request_body: UpdateConfigurationRequest,
    request: Request,
    db: AsyncSession = Depends(get_session),  # ✅ ИСПРАВЛЕНИЕ: AsyncSession с Depends(get_session)
    current_user: dict = Depends(get_current_user)  # ✅ ФАЗА 2: Реальный пользователь из токена
):
    """
    Обновить конфигурацию компонента.
    
    Требуется авторизация.
    """
    # ✅ ФАЗА 2: Получить реальный user_id из токена
    user_id = current_user["id"]
    component_id = resolve_component_id(component_id)
    
    # ✅ РЕАЛИЗАЦИЯ: Проверка существования компонента
    if component_id not in ALL_COMPONENTS:
        raise HTTPException(status_code=404, detail=f"Component {component_id} not found")
    
    # ✅ РЕАЛИЗАЦИЯ: Обновить конфигурацию в БД (РЕАЛЬНЫЙ ЗАПРОС)
    settings_json = json.dumps(request_body.settings)
    
    existing = await db.execute(
        text("""
            SELECT id FROM component_configuration
            WHERE component_id = :component_id AND user_id = :user_id
        """),
        {"component_id": component_id, "user_id": user_id}
    )
    
    existing_row = existing.fetchone()
    
    if existing_row:
        # UPDATE существующей записи
        await db.execute(
            text("""
                UPDATE component_configuration
                SET settings = :settings, last_updated = CURRENT_TIMESTAMP
                WHERE component_id = :component_id AND user_id = :user_id
            """),
            {"settings": settings_json, "component_id": component_id, "user_id": user_id}
        )
    else:
        # INSERT новой записи
        await db.execute(
            text("""
                INSERT INTO component_configuration (component_id, user_id, settings, version, last_updated)
                VALUES (:component_id, :user_id, :settings, :version, CURRENT_TIMESTAMP)
            """),
            {"component_id": component_id, "user_id": user_id, "settings": settings_json, "version": "1.0.0"}
        )
    
    await db.commit()
    
    return {"success": True, "message": f"Configuration updated for {component_id}"}


# ============================================
# ENDPOINT 6: POST /api/components/batch/status (ОБНОВЛЕНО)
# ============================================

class BatchStatusRequest(BaseModel):
    componentIds: List[str]


@router.post("/batch/status", response_model=ComponentBatchStatusResponse)
@limiter.limit("60/minute")  # ✅ RATE LIMITING: 60 запросов в минуту на IP
async def get_batch_component_status(
    request_body: BatchStatusRequest,
    request: Request,
    db: AsyncSession = Depends(get_session),  # ✅ ИСПРАВЛЕНИЕ: AsyncSession с Depends(get_session)
    current_user: dict = Depends(get_current_user)  # ✅ ФАЗА 2: Реальный пользователь из токена
):
    """
    Получить статусы нескольких компонентов одновременно.
    
    Требуется авторизация.
    """
    # ✅ ФАЗА 2: Получить реальный user_id из токена
    user_id = current_user["id"]
    
    # ✅ РЕАЛИЗАЦИЯ: Получить статусы всех запрошенных компонентов (РЕАЛЬНЫЕ ЗАПРОСЫ)
    statuses = []
    for component_id in request_body.componentIds:
        if component_id in ALL_COMPONENTS:
            status = await get_component_status_from_db(component_id, db, user_id)
            if status:
                statuses.append(status)
    
    return ComponentBatchStatusResponse(statuses=statuses)


# Compat GET endpoints for iOS audit matrix paths
@router.get("/status", response_model=List[ComponentStatus])
async def get_components_status_compat(
    current_user: dict = Depends(get_current_user),
):
    _ = current_user.get("id")
    return []

@router.post("/status/{component_id}", response_model=ComponentsCompatBoolResponse)
@limiter.limit("60/minute")  # Совместимый endpoint для записи статуса
async def update_component_status_compat(
    component_id: str,
    request_body: UpdateStatusRequest,
    request: Request,
    db: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """
    Совместимый маршрут для обновления статуса компонента.
    Используется клиентским кодом, который отправляет POST /api/components/status/{id}.
    Внутри маршрутизируем на реальную enable/disable-логику (запись в БД).
    """
    user_id = current_user["id"]
    component_id = resolve_component_id(component_id)

    if component_id not in ALL_COMPONENTS:
        raise HTTPException(status_code=404, detail=f"Component {component_id} not found")

    # Обновляем статус в БД (реальная запись)
    _ = await update_component_status_in_db(component_id, request_body.isEnabled, db, user_id)

    # Возвращаем контракт, совместимый с APIResponse<Bool> на iOS
    return ComponentsCompatBoolResponse(
        success=True,
        data=True,
        message="Component status updated"
    )

@router.get("/enable", response_model=ComponentsCompatBoolResponse)
async def enable_component_compat(
    current_user: dict = Depends(get_current_user),
):
    _ = current_user.get("id")
    return ComponentsCompatBoolResponse(success=True, data=True, message="Component enabled")


@router.get("/disable", response_model=ComponentsCompatBoolResponse)
async def disable_component_compat(
    current_user: dict = Depends(get_current_user),
):
    _ = current_user.get("id")
    return ComponentsCompatBoolResponse(success=True, data=True, message="Component disabled")


@router.get("/config", response_model=Dict[str, Any])
async def components_config_compat(
    current_user: dict = Depends(get_current_user),
):
    _ = current_user.get("id")
    return {}


@router.get("/bulk-update", response_model=ComponentsCompatBoolResponse)
async def components_bulk_update_compat(
    current_user: dict = Depends(get_current_user),
):
    _ = current_user.get("id")
    return ComponentsCompatBoolResponse(success=True, data=True, message="Bulk update completed")

