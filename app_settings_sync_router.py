# -*- coding: utf-8 -*-
"""
App Settings Sync API Router
----------------------------
FastAPI endpoints для синхронизации настроек приложения между устройствами.

Использование:
    В main.py добавить:
    from security.api.routers.app_settings_sync_router import router as app_settings_router
    app.include_router(app_settings_router)

Дата создания: 11 февраля 2026
Версия: 1.0.0
"""

from datetime import datetime
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, HTTPException, Query, Path
from pydantic import BaseModel, Field
import logging
import sys
import os

# SFM Adapter import
backend_path = "/opt/aladdin-backend"
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    from sfm_adapter import sfm_adapter
    SFM_ADAPTER_AVAILABLE = True
except ImportError as e:
    SFM_ADAPTER_AVAILABLE = False
    sfm_adapter = None
    print(f"SFM Adapter not available: {e}")

logger = logging.getLogger(__name__)

# Создаем FastAPI Router
router = APIRouter(prefix="/api/settings", tags=["App Settings"])


# =============================================================================
# Pydantic модели для запросов и ответов
# =============================================================================

class AppSettingsResponse(BaseModel):
    """Ответ с настройками приложения"""
    userId: str = Field(..., description="ID пользователя")
    theme: str = Field("system", description="Тема: light, dark, system")
    language: str = Field("ru", description="Язык: ru, en")
    notificationsEnabled: bool = Field(True, description="Уведомления включены")
    biometryEnabled: bool = Field(False, description="Биометрия включена")
    lastModified: datetime = Field(..., description="Время последнего изменения")
    deviceId: Optional[str] = Field(None, description="ID устройства последнего изменения")
    version: int = Field(1, description="Версия для оптимистичной блокировки", ge=1)


class SyncAppSettingsRequest(BaseModel):
    """Запрос на синхронизацию настроек"""
    userId: str = Field(..., description="ID пользователя")
    deviceId: str = Field(..., description="ID устройства")
    lastSyncTimestamp: Optional[datetime] = Field(None, description="Время последней синхронизации")


class SyncAppSettingsResponse(BaseModel):
    """Ответ на синхронизацию настроек"""
    userId: str = Field(..., description="ID пользователя")
    settings: AppSettingsResponse = Field(..., description="Настройки приложения")
    conflicts: List[Dict[str, Any]] = Field(default_factory=list, description="Список конфликтов")
    lastSyncTimestamp: datetime = Field(..., description="Время синхронизации")


class UpdateAppSettingsRequest(BaseModel):
    """Запрос на обновление настроек"""
    userId: str = Field(..., description="ID пользователя")
    theme: Optional[str] = Field(None, description="Тема: light, dark, system")
    language: Optional[str] = Field(None, description="Язык: ru, en")
    notificationsEnabled: Optional[bool] = Field(None, description="Уведомления включены")
    biometryEnabled: Optional[bool] = Field(None, description="Биометрия включена")
    deviceId: Optional[str] = Field(None, description="ID устройства")
    version: Optional[int] = Field(None, description="Версия для оптимистичной блокировки", ge=1)


class ThemeSettingsResponse(BaseModel):
    """Ответ с настройками темы"""
    userId: str = Field(..., description="ID пользователя")
    theme: str = Field("system", description="Тема: light, dark, system")
    lastModified: datetime = Field(..., description="Время последнего изменения")
    deviceId: Optional[str] = Field(None, description="ID устройства последнего изменения")
    version: int = Field(1, description="Версия для оптимистичной блокировки", ge=1)


class UpdateThemeSettingsRequest(BaseModel):
    """Запрос на обновление темы"""
    userId: str = Field(..., description="ID пользователя")
    theme: str = Field(..., description="Тема: light, dark, system")
    deviceId: Optional[str] = Field(None, description="ID устройства")
    version: Optional[int] = Field(None, description="Версия для оптимистичной блокировки", ge=1)


class LanguageSettingsResponse(BaseModel):
    """Ответ с настройками языка"""
    userId: str = Field(..., description="ID пользователя")
    language: str = Field("ru", description="Язык: ru, en")
    lastModified: datetime = Field(..., description="Время последнего изменения")
    deviceId: Optional[str] = Field(None, description="ID устройства последнего изменения")
    version: int = Field(1, description="Версия для оптимистичной блокировки", ge=1)


class UpdateLanguageSettingsRequest(BaseModel):
    """Запрос на обновление языка"""
    userId: str = Field(..., description="ID пользователя")
    language: str = Field(..., description="Язык: ru, en")
    deviceId: Optional[str] = Field(None, description="ID устройства")
    version: Optional[int] = Field(None, description="Версия для оптимистичной блокировки", ge=1)


class NotificationSettingsAppResponse(BaseModel):
    """Ответ с настройками уведомлений приложения"""
    userId: str = Field(..., description="ID пользователя")
    enabled: bool = Field(True, description="Уведомления включены")
    pushEnabled: bool = Field(True, description="Push-уведомления включены")
    emailEnabled: bool = Field(False, description="Email-уведомления включены")
    lastModified: datetime = Field(..., description="Время последнего изменения")
    deviceId: Optional[str] = Field(None, description="ID устройства последнего изменения")
    version: int = Field(1, description="Версия для оптимистичной блокировки", ge=1)


class UpdateNotificationSettingsAppRequest(BaseModel):
    """Запрос на обновление настроек уведомлений"""
    userId: str = Field(..., description="ID пользователя")
    enabled: Optional[bool] = Field(None, description="Уведомления включены")
    pushEnabled: Optional[bool] = Field(None, description="Push-уведомления включены")
    emailEnabled: Optional[bool] = Field(None, description="Email-уведомления включены")
    deviceId: Optional[str] = Field(None, description="ID устройства")
    version: Optional[int] = Field(None, description="Версия для оптимистичной блокировки", ge=1)


class BiometrySettingsResponse(BaseModel):
    """Ответ с настройками биометрии"""
    userId: str = Field(..., description="ID пользователя")
    enabled: bool = Field(False, description="Биометрия включена")
    type: Optional[str] = Field(None, description="Тип биометрии: face, touch, none")
    lastModified: datetime = Field(..., description="Время последнего изменения")
    deviceId: Optional[str] = Field(None, description="ID устройства последнего изменения")
    version: int = Field(1, description="Версия для оптимистичной блокировки", ge=1)


class UpdateBiometrySettingsRequest(BaseModel):
    """Запрос на обновление настроек биометрии"""
    userId: str = Field(..., description="ID пользователя")
    enabled: bool = Field(..., description="Биометрия включена")
    type: Optional[str] = Field(None, description="Тип биометрии: face, touch, none")
    deviceId: Optional[str] = Field(None, description="ID устройства")
    version: Optional[int] = Field(None, description="Версия для оптимистичной блокировки", ge=1)


# =============================================================================
# API Endpoints
# =============================================================================

@router.post("/sync", response_model=SyncAppSettingsResponse)
async def sync_app_settings(
    request: SyncAppSettingsRequest
) -> SyncAppSettingsResponse:
    """
    Синхронизировать настройки приложения между устройствами
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.sync_app_settings(**request.dict())
                if result:
                    return SyncAppSettingsResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        settings = AppSettingsResponse(
            userId=request.userId,
            theme="system",
            language="ru",
            notificationsEnabled=True,
            biometryEnabled=False,
            lastModified=datetime.now(),
            deviceId=request.deviceId,
            version=1
        )
        return SyncAppSettingsResponse(
            userId=request.userId,
            settings=settings,
            conflicts=[],
            lastSyncTimestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"Error syncing app settings: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка синхронизации настроек: {str(e)}")


@router.post("/update", response_model=AppSettingsResponse)
async def update_app_settings(
    request: UpdateAppSettingsRequest
) -> AppSettingsResponse:
    """
    Обновить настройки приложения
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.update_app_settings(**request.dict())
                if result:
                    return AppSettingsResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        return AppSettingsResponse(
            userId=request.userId,
            theme=request.theme or "system",
            language=request.language or "ru",
            notificationsEnabled=request.notificationsEnabled if request.notificationsEnabled is not None else True,
            biometryEnabled=request.biometryEnabled if request.biometryEnabled is not None else False,
            lastModified=datetime.now(),
            deviceId=request.deviceId,
            version=(request.version or 1) + 1
        )
    except Exception as e:
        logger.error(f"Error updating app settings: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка обновления настроек: {str(e)}")


@router.get("/theme", response_model=ThemeSettingsResponse)
async def get_theme_settings(
    userId: str = Query(..., description="ID пользователя")
) -> ThemeSettingsResponse:
    """
    Получить настройки темы
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.get_theme_settings(userId=userId)
                if result:
                    return ThemeSettingsResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        return ThemeSettingsResponse(
            userId=userId,
            theme="system",
            lastModified=datetime.now(),
            deviceId=None,
            version=1
        )
    except Exception as e:
        logger.error(f"Error getting theme settings: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения настроек темы: {str(e)}")


@router.post("/theme/update", response_model=ThemeSettingsResponse)
async def update_theme_settings(
    request: UpdateThemeSettingsRequest
) -> ThemeSettingsResponse:
    """
    Обновить настройки темы
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.update_theme_settings(**request.dict())
                if result:
                    return ThemeSettingsResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        return ThemeSettingsResponse(
            userId=request.userId,
            theme=request.theme,
            lastModified=datetime.now(),
            deviceId=request.deviceId,
            version=(request.version or 1) + 1
        )
    except Exception as e:
        logger.error(f"Error updating theme settings: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка обновления настроек темы: {str(e)}")


@router.get("/language", response_model=LanguageSettingsResponse)
async def get_language_settings(
    userId: str = Query(..., description="ID пользователя")
) -> LanguageSettingsResponse:
    """
    Получить настройки языка
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.get_language_settings(userId=userId)
                if result:
                    return LanguageSettingsResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        return LanguageSettingsResponse(
            userId=userId,
            language="ru",
            lastModified=datetime.now(),
            deviceId=None,
            version=1
        )
    except Exception as e:
        logger.error(f"Error getting language settings: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения настроек языка: {str(e)}")


@router.post("/language/update", response_model=LanguageSettingsResponse)
async def update_language_settings(
    request: UpdateLanguageSettingsRequest
) -> LanguageSettingsResponse:
    """
    Обновить настройки языка
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.update_language_settings(**request.dict())
                if result:
                    return LanguageSettingsResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        return LanguageSettingsResponse(
            userId=request.userId,
            language=request.language,
            lastModified=datetime.now(),
            deviceId=request.deviceId,
            version=(request.version or 1) + 1
        )
    except Exception as e:
        logger.error(f"Error updating language settings: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка обновления настроек языка: {str(e)}")


@router.get("/notifications", response_model=NotificationSettingsAppResponse)
async def get_notification_settings(
    userId: str = Query(..., description="ID пользователя")
) -> NotificationSettingsAppResponse:
    """
    Получить настройки уведомлений приложения
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.get_notification_settings_app(userId=userId)
                if result:
                    return NotificationSettingsAppResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        return NotificationSettingsAppResponse(
            userId=userId,
            enabled=True,
            pushEnabled=True,
            emailEnabled=False,
            lastModified=datetime.now(),
            deviceId=None,
            version=1
        )
    except Exception as e:
        logger.error(f"Error getting notification settings: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения настроек уведомлений: {str(e)}")


@router.post("/notifications/update", response_model=NotificationSettingsAppResponse)
async def update_notification_settings(
    request: UpdateNotificationSettingsAppRequest
) -> NotificationSettingsAppResponse:
    """
    Обновить настройки уведомлений приложения
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.update_notification_settings_app(**request.dict())
                if result:
                    return NotificationSettingsAppResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        return NotificationSettingsAppResponse(
            userId=request.userId,
            enabled=request.enabled if request.enabled is not None else True,
            pushEnabled=request.pushEnabled if request.pushEnabled is not None else True,
            emailEnabled=request.emailEnabled if request.emailEnabled is not None else False,
            lastModified=datetime.now(),
            deviceId=request.deviceId,
            version=(request.version or 1) + 1
        )
    except Exception as e:
        logger.error(f"Error updating notification settings: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка обновления настроек уведомлений: {str(e)}")


@router.get("/biometry", response_model=BiometrySettingsResponse)
async def get_biometry_settings(
    userId: str = Query(..., description="ID пользователя")
) -> BiometrySettingsResponse:
    """
    Получить настройки биометрии
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.get_biometry_settings(userId=userId)
                if result:
                    return BiometrySettingsResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        return BiometrySettingsResponse(
            userId=userId,
            enabled=False,
            type=None,
            lastModified=datetime.now(),
            deviceId=None,
            version=1
        )
    except Exception as e:
        logger.error(f"Error getting biometry settings: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения настроек биометрии: {str(e)}")


@router.post("/biometry/update", response_model=BiometrySettingsResponse)
async def update_biometry_settings(
    request: UpdateBiometrySettingsRequest
) -> BiometrySettingsResponse:
    """
    Обновить настройки биометрии
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.update_biometry_settings(**request.dict())
                if result:
                    return BiometrySettingsResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        return BiometrySettingsResponse(
            userId=request.userId,
            enabled=request.enabled,
            type=request.type,
            lastModified=datetime.now(),
            deviceId=request.deviceId,
            version=(request.version or 1) + 1
        )
    except Exception as e:
        logger.error(f"Error updating biometry settings: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка обновления настроек биометрии: {str(e)}")
