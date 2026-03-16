# -*- coding: utf-8 -*-
"""
User Profile Sync API Router
-----------------------------
FastAPI endpoints для синхронизации профиля пользователя между устройствами.

Использование:
    В main.py добавить:
    from security.api.routers.user_profile_sync_router import router as user_profile_router
    app.include_router(user_profile_router)

Дата создания: 11 февраля 2026
Версия: 1.0.0
"""

from datetime import datetime
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, HTTPException, Query, Path, Depends
from pydantic import BaseModel, Field
import logging
import sys
import os

# ✅ BUILD 122: Импорт get_current_user для авторизации
try:
    from app.auth.auth import get_current_user
except ImportError:
    try:
        from auth.auth import get_current_user
    except ImportError:
        get_current_user = None
        print("⚠️ get_current_user not available")

# SFM Adapter import
backend_path = "/opt/aladdin-backend"
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    from app.security.sfm_singleton import get_sfm
    SFM_AVAILABLE = True
except ImportError as e:
    try:
        from sfm_singleton import get_sfm
        SFM_AVAILABLE = True
    except ImportError:
        SFM_AVAILABLE = False
        get_sfm = None
        print(f"⚠️ SFM not available: {e}")

try:
    from sfm_adapter import sfm_adapter
    SFM_ADAPTER_AVAILABLE = True
except ImportError as e:
    SFM_ADAPTER_AVAILABLE = False
    sfm_adapter = None
    print(f"SFM Adapter not available: {e}")

logger = logging.getLogger(__name__)

# Создаем FastAPI Router
router = APIRouter(prefix="/api/user/profile", tags=["User Profile"])


# =============================================================================
# Pydantic модели для запросов и ответов
# =============================================================================

class UserProfileResponse(BaseModel):
    """Ответ с профилем пользователя"""
    userId: str = Field(..., description="ID пользователя")
    name: str = Field(..., description="Имя пользователя")
    email: Optional[str] = Field(None, description="Email")
    phone: Optional[str] = Field(None, description="Телефон")
    avatar: Optional[str] = Field(None, description="URL аватара")
    registrationDate: str = Field(..., description="Дата регистрации (ISO)")
    lastModified: datetime = Field(..., description="Время последнего изменения")
    deviceId: Optional[str] = Field(None, description="ID устройства последнего изменения")
    version: int = Field(1, description="Версия для оптимистичной блокировки", ge=1)


class UpdateUserProfileRequest(BaseModel):
    """Запрос на обновление профиля"""
    userId: str = Field(..., description="ID пользователя")
    name: Optional[str] = Field(None, description="Имя пользователя", max_length=100)
    email: Optional[str] = Field(None, description="Email", max_length=255)
    phone: Optional[str] = Field(None, description="Телефон", max_length=20)
    avatar: Optional[str] = Field(None, description="URL аватара")
    deviceId: Optional[str] = Field(None, description="ID устройства")
    version: Optional[int] = Field(None, description="Версия для оптимистичной блокировки", ge=1)


class SyncUserProfileRequest(BaseModel):
    """Запрос на синхронизацию профиля"""
    userId: str = Field(..., description="ID пользователя")
    deviceId: str = Field(..., description="ID устройства")
    lastSyncTimestamp: Optional[datetime] = Field(None, description="Время последней синхронизации")


class SyncUserProfileResponse(BaseModel):
    """Ответ на синхронизацию профиля"""
    userId: str = Field(..., description="ID пользователя")
    profile: UserProfileResponse = Field(..., description="Профиль пользователя")
    conflicts: List[Dict[str, Any]] = Field(default_factory=list, description="Список конфликтов")
    lastSyncTimestamp: datetime = Field(..., description="Время синхронизации")


class ProfileHistoryEntry(BaseModel):
    """Запись в истории изменений профиля"""
    historyId: str = Field(..., description="ID записи истории")
    userId: str = Field(..., description="ID пользователя")
    changedBy: str = Field(..., description="ID пользователя, который внес изменения")
    changes: Dict[str, Any] = Field(..., description="Словарь изменений (поле -> старое значение -> новое значение)")
    timestamp: datetime = Field(..., description="Время изменения")
    deviceId: Optional[str] = Field(None, description="ID устройства")


class ProfileHistoryResponse(BaseModel):
    """История изменений профиля"""
    history: List[ProfileHistoryEntry] = Field(..., description="Список изменений")
    total: int = Field(..., description="Общее количество записей")


class PrivacySettingsResponse(BaseModel):
    """Ответ с настройками приватности"""
    userId: str = Field(..., description="ID пользователя")
    profileVisibility: str = Field("private", description="Видимость профиля: public, private, friends")
    showEmail: bool = Field(False, description="Показывать email")
    showPhone: bool = Field(False, description="Показывать телефон")
    showLocation: bool = Field(False, description="Показывать местоположение")
    allowDataSharing: bool = Field(False, description="Разрешить обмен данными")
    lastModified: datetime = Field(..., description="Время последнего изменения")
    deviceId: Optional[str] = Field(None, description="ID устройства последнего изменения")
    version: int = Field(1, description="Версия для оптимистичной блокировки", ge=1)


class UpdatePrivacySettingsRequest(BaseModel):
    """Запрос на обновление настроек приватности"""
    userId: str = Field(..., description="ID пользователя")
    profileVisibility: Optional[str] = Field(None, description="Видимость профиля: public, private, friends")
    showEmail: Optional[bool] = Field(None, description="Показывать email")
    showPhone: Optional[bool] = Field(None, description="Показывать телефон")
    showLocation: Optional[bool] = Field(None, description="Показывать местоположение")
    allowDataSharing: Optional[bool] = Field(None, description="Разрешить обмен данными")
    deviceId: Optional[str] = Field(None, description="ID устройства")
    version: Optional[int] = Field(None, description="Версия для оптимистичной блокировки", ge=1)


# =============================================================================
# API Endpoints
# =============================================================================

@router.get("", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: dict = Depends(get_current_user) if get_current_user else Depends(lambda: None)
) -> UserProfileResponse:
    """
    ✅ BUILD 122: Получить профиль текущего пользователя из токена
    
    Использует реальный SFM через get_authentication_manager_profile
    """
    if not get_current_user:
        raise HTTPException(
            status_code=501,
            detail="Авторизация не настроена на сервере"
        )
    
    if current_user is None:
        raise HTTPException(
            status_code=401,
            detail="Требуется авторизация"
        )
    
    try:
        user_id = current_user.get("id") or current_user.get("user_id") or current_user.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=400,
                detail="Не удалось определить ID пользователя из токена"
            )
        
        # ✅ BUILD 122: Используем реальный SFM через get_authentication_manager_profile
        if SFM_AVAILABLE and get_sfm:
            try:
                sfm = get_sfm()
                result = sfm.execute_function("get_authentication_manager_profile", {"user_id": user_id})
                
                # Проверяем что это не mock ответ
                if isinstance(result, dict) and result.get("source") == "sfm_mock":
                    logger.warning(f"SFM returned mock response for user_id: {user_id}, using fallback")
                elif isinstance(result, dict) and "id" in result:
                    # ✅ Реальный ответ от SFM
                    return UserProfileResponse(
                        userId=result.get("id", user_id),
                        name=result.get("name", "Пользователь"),
                        email=result.get("email"),
                        phone=result.get("phone"),
                        avatar=result.get("avatar"),
                        registrationDate=result.get("registrationDate", datetime.now().isoformat()),
                        lastModified=datetime.now(),
                        deviceId=result.get("deviceId"),
                        version=result.get("version", 1)
                    )
            except Exception as e:
                logger.error(f"SFM execution error: {e}, using fallback")
        
        # Fallback: возвращаем базовый профиль из токена
        return UserProfileResponse(
            userId=user_id,
            name=current_user.get("email", "Пользователь").split("@")[0] if current_user.get("email") else "Пользователь",
            email=current_user.get("email"),
            phone=None,
            avatar=None,
            registrationDate=datetime.now().isoformat(),
            lastModified=datetime.now(),
            deviceId=current_user.get("device_id"),
            version=1
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения профиля: {str(e)}")


@router.post("/sync", response_model=SyncUserProfileResponse)
async def sync_user_profile(
    request: SyncUserProfileRequest
) -> SyncUserProfileResponse:
    """
    Синхронизировать профиль пользователя между устройствами
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.sync_user_profile(**request.dict())
                if result:
                    return SyncUserProfileResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback: возвращаем mock данные
        profile = UserProfileResponse(
            userId=request.userId,
            name="Пользователь",
            email=None,
            phone=None,
            avatar=None,
            registrationDate=datetime.now().isoformat(),
            lastModified=datetime.now(),
            deviceId=request.deviceId,
            version=1
        )
        return SyncUserProfileResponse(
            userId=request.userId,
            profile=profile,
            conflicts=[],
            lastSyncTimestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"Error syncing user profile: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка синхронизации профиля: {str(e)}")


@router.post("/update", response_model=UserProfileResponse)
async def update_user_profile(
    request: UpdateUserProfileRequest
) -> UserProfileResponse:
    """
    Обновить профиль пользователя
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.update_user_profile(**request.dict())
                if result:
                    return UserProfileResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback: возвращаем обновленные mock данные
        return UserProfileResponse(
            userId=request.userId,
            name=request.name or "Пользователь",
            email=request.email,
            phone=request.phone,
            avatar=request.avatar,
            registrationDate=datetime.now().isoformat(),
            lastModified=datetime.now(),
            deviceId=request.deviceId,
            version=(request.version or 1) + 1
        )
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка обновления профиля: {str(e)}")


@router.get("/history", response_model=ProfileHistoryResponse)
async def get_user_profile_history(
    userId: str = Query(..., description="ID пользователя"),
    limit: int = Query(50, description="Максимальное количество записей", ge=1, le=100)
) -> ProfileHistoryResponse:
    """
    Получить историю изменений профиля пользователя
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.get_user_profile_history(userId=userId, limit=limit)
                if result:
                    return ProfileHistoryResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback: возвращаем пустую историю
        return ProfileHistoryResponse(
            history=[],
            total=0
        )
    except Exception as e:
        logger.error(f"Error getting profile history: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения истории: {str(e)}")


@router.get("/privacy", response_model=PrivacySettingsResponse)
async def get_user_privacy_settings(
    userId: str = Query(..., description="ID пользователя")
) -> PrivacySettingsResponse:
    """
    Получить настройки приватности пользователя
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.get_user_privacy_settings(userId=userId)
                if result:
                    return PrivacySettingsResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback: возвращаем настройки по умолчанию
        return PrivacySettingsResponse(
            userId=userId,
            profileVisibility="private",
            showEmail=False,
            showPhone=False,
            showLocation=False,
            allowDataSharing=False,
            lastModified=datetime.now(),
            deviceId=None,
            version=1
        )
    except Exception as e:
        logger.error(f"Error getting privacy settings: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения настроек приватности: {str(e)}")


@router.post("/privacy/update", response_model=PrivacySettingsResponse)
async def update_user_privacy_settings(
    request: UpdatePrivacySettingsRequest
) -> PrivacySettingsResponse:
    """
    Обновить настройки приватности пользователя
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.update_user_privacy_settings(**request.dict())
                if result:
                    return PrivacySettingsResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback: возвращаем обновленные настройки
        return PrivacySettingsResponse(
            userId=request.userId,
            profileVisibility=request.profileVisibility or "private",
            showEmail=request.showEmail if request.showEmail is not None else False,
            showPhone=request.showPhone if request.showPhone is not None else False,
            showLocation=request.showLocation if request.showLocation is not None else False,
            allowDataSharing=request.allowDataSharing if request.allowDataSharing is not None else False,
            lastModified=datetime.now(),
            deviceId=request.deviceId,
            version=(request.version or 1) + 1
        )
    except Exception as e:
        logger.error(f"Error updating privacy settings: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка обновления настроек приватности: {str(e)}")
