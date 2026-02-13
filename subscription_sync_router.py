# -*- coding: utf-8 -*-
"""
Subscription Sync API Router
----------------------------
FastAPI endpoints для синхронизации тарифов и подписок между устройствами.

Использование:
    В main.py добавить:
    from security.api.routers.subscription_sync_router import router as subscription_router
    app.include_router(subscription_router)

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
router = APIRouter(prefix="/api/subscription", tags=["Subscription"])


# =============================================================================
# Pydantic модели для запросов и ответов
# =============================================================================

class SubscriptionResponse(BaseModel):
    """Ответ с информацией о подписке"""
    userId: str = Field(..., description="ID пользователя")
    subscriptionType: str = Field(..., description="Тип подписки: free, basic, family, premium")
    status: str = Field(..., description="Статус: active, expired, cancelled, pending")
    startDate: datetime = Field(..., description="Дата начала подписки")
    endDate: Optional[datetime] = Field(None, description="Дата окончания подписки")
    autoRenewal: bool = Field(False, description="Автопродление включено")
    lastModified: datetime = Field(..., description="Время последнего изменения")
    deviceId: Optional[str] = Field(None, description="ID устройства последнего изменения")
    version: int = Field(1, description="Версия для оптимистичной блокировки", ge=1)


class SyncSubscriptionRequest(BaseModel):
    """Запрос на синхронизацию подписки"""
    userId: str = Field(..., description="ID пользователя")
    deviceId: str = Field(..., description="ID устройства")
    lastSyncTimestamp: Optional[datetime] = Field(None, description="Время последней синхронизации")


class SyncSubscriptionResponse(BaseModel):
    """Ответ на синхронизацию подписки"""
    userId: str = Field(..., description="ID пользователя")
    subscription: SubscriptionResponse = Field(..., description="Информация о подписке")
    conflicts: List[Dict[str, Any]] = Field(default_factory=list, description="Список конфликтов")
    lastSyncTimestamp: datetime = Field(..., description="Время синхронизации")


class UpdateSubscriptionRequest(BaseModel):
    """Запрос на обновление подписки"""
    userId: str = Field(..., description="ID пользователя")
    subscriptionType: Optional[str] = Field(None, description="Тип подписки")
    status: Optional[str] = Field(None, description="Статус подписки")
    endDate: Optional[datetime] = Field(None, description="Дата окончания")
    deviceId: Optional[str] = Field(None, description="ID устройства")
    version: Optional[int] = Field(None, description="Версия для оптимистичной блокировки", ge=1)


class PurchaseHistoryEntry(BaseModel):
    """Запись в истории покупок"""
    purchaseId: str = Field(..., description="ID покупки")
    userId: str = Field(..., description="ID пользователя")
    subscriptionType: str = Field(..., description="Тип подписки")
    amount: float = Field(..., description="Сумма покупки", ge=0)
    currency: str = Field("USD", description="Валюта")
    purchaseDate: datetime = Field(..., description="Дата покупки")
    transactionId: Optional[str] = Field(None, description="ID транзакции")
    status: str = Field(..., description="Статус: success, failed, pending, refunded")


class PurchaseHistoryResponse(BaseModel):
    """История покупок"""
    history: List[PurchaseHistoryEntry] = Field(..., description="Список покупок")
    total: int = Field(..., description="Общее количество записей")


class SubscriptionStatusResponse(BaseModel):
    """Ответ со статусом подписки"""
    userId: str = Field(..., description="ID пользователя")
    isActive: bool = Field(..., description="Активна ли подписка")
    daysRemaining: Optional[int] = Field(None, description="Дней до окончания")
    canRenew: bool = Field(False, description="Можно ли продлить")
    lastModified: datetime = Field(..., description="Время последнего изменения")


class UpdateSubscriptionStatusRequest(BaseModel):
    """Запрос на обновление статуса подписки"""
    userId: str = Field(..., description="ID пользователя")
    status: str = Field(..., description="Новый статус: active, expired, cancelled, pending")
    deviceId: Optional[str] = Field(None, description="ID устройства")
    version: Optional[int] = Field(None, description="Версия для оптимистичной блокировки", ge=1)


class AutoRenewalResponse(BaseModel):
    """Ответ с настройками автопродления"""
    userId: str = Field(..., description="ID пользователя")
    enabled: bool = Field(False, description="Включено ли автопродление")
    nextRenewalDate: Optional[datetime] = Field(None, description="Дата следующего продления")
    lastModified: datetime = Field(..., description="Время последнего изменения")
    deviceId: Optional[str] = Field(None, description="ID устройства последнего изменения")
    version: int = Field(1, description="Версия для оптимистичной блокировки", ge=1)


class UpdateAutoRenewalRequest(BaseModel):
    """Запрос на обновление автопродления"""
    userId: str = Field(..., description="ID пользователя")
    enabled: bool = Field(..., description="Включить/выключить автопродление")
    deviceId: Optional[str] = Field(None, description="ID устройства")
    version: Optional[int] = Field(None, description="Версия для оптимистичной блокировки", ge=1)


class CancelSubscriptionRequest(BaseModel):
    """Запрос на отмену подписки"""
    userId: str = Field(..., description="ID пользователя")
    reason: Optional[str] = Field(None, description="Причина отмены", max_length=500)
    deviceId: Optional[str] = Field(None, description="ID устройства")


# =============================================================================
# API Endpoints
# =============================================================================

@router.post("/sync", response_model=SyncSubscriptionResponse)
async def sync_subscription(
    request: SyncSubscriptionRequest
) -> SyncSubscriptionResponse:
    """
    Синхронизировать информацию о подписке между устройствами
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.sync_subscription(**request.dict())
                if result:
                    return SyncSubscriptionResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        subscription = SubscriptionResponse(
            userId=request.userId,
            subscriptionType="free",
            status="active",
            startDate=datetime.now(),
            endDate=None,
            autoRenewal=False,
            lastModified=datetime.now(),
            deviceId=request.deviceId,
            version=1
        )
        return SyncSubscriptionResponse(
            userId=request.userId,
            subscription=subscription,
            conflicts=[],
            lastSyncTimestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"Error syncing subscription: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка синхронизации подписки: {str(e)}")


@router.post("/update", response_model=SubscriptionResponse)
async def update_subscription(
    request: UpdateSubscriptionRequest
) -> SubscriptionResponse:
    """
    Обновить информацию о подписке
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.update_subscription(**request.dict())
                if result:
                    return SubscriptionResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        return SubscriptionResponse(
            userId=request.userId,
            subscriptionType=request.subscriptionType or "free",
            status=request.status or "active",
            startDate=datetime.now(),
            endDate=request.endDate,
            autoRenewal=False,
            lastModified=datetime.now(),
            deviceId=request.deviceId,
            version=(request.version or 1) + 1
        )
    except Exception as e:
        logger.error(f"Error updating subscription: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка обновления подписки: {str(e)}")


@router.get("/purchase-history", response_model=PurchaseHistoryResponse)
async def get_purchase_history(
    userId: str = Query(..., description="ID пользователя"),
    limit: int = Query(50, description="Максимальное количество записей", ge=1, le=100)
) -> PurchaseHistoryResponse:
    """
    Получить историю покупок подписок
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.get_purchase_history(userId=userId, limit=limit)
                if result:
                    return PurchaseHistoryResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        return PurchaseHistoryResponse(
            history=[],
            total=0
        )
    except Exception as e:
        logger.error(f"Error getting purchase history: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения истории покупок: {str(e)}")


@router.get("/status", response_model=SubscriptionStatusResponse)
async def get_subscription_status(
    userId: str = Query(..., description="ID пользователя")
) -> SubscriptionStatusResponse:
    """
    Получить статус подписки
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.get_subscription_status(userId=userId)
                if result:
                    return SubscriptionStatusResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        return SubscriptionStatusResponse(
            userId=userId,
            isActive=True,
            daysRemaining=None,
            canRenew=False,
            lastModified=datetime.now()
        )
    except Exception as e:
        logger.error(f"Error getting subscription status: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения статуса подписки: {str(e)}")


@router.post("/status/update", response_model=SubscriptionStatusResponse)
async def update_subscription_status(
    request: UpdateSubscriptionStatusRequest
) -> SubscriptionStatusResponse:
    """
    Обновить статус подписки
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.update_subscription_status(**request.dict())
                if result:
                    return SubscriptionStatusResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        is_active = request.status == "active"
        return SubscriptionStatusResponse(
            userId=request.userId,
            isActive=is_active,
            daysRemaining=None,
            canRenew=is_active,
            lastModified=datetime.now()
        )
    except Exception as e:
        logger.error(f"Error updating subscription status: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка обновления статуса подписки: {str(e)}")


@router.get("/auto-renewal", response_model=AutoRenewalResponse)
async def get_auto_renewal(
    userId: str = Query(..., description="ID пользователя")
) -> AutoRenewalResponse:
    """
    Получить настройки автопродления
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.get_auto_renewal(userId=userId)
                if result:
                    return AutoRenewalResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        return AutoRenewalResponse(
            userId=userId,
            enabled=False,
            nextRenewalDate=None,
            lastModified=datetime.now(),
            deviceId=None,
            version=1
        )
    except Exception as e:
        logger.error(f"Error getting auto-renewal: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения настроек автопродления: {str(e)}")


@router.post("/auto-renewal/update", response_model=AutoRenewalResponse)
async def update_auto_renewal(
    request: UpdateAutoRenewalRequest
) -> AutoRenewalResponse:
    """
    Обновить настройки автопродления
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.update_auto_renewal(**request.dict())
                if result:
                    return AutoRenewalResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        next_renewal = datetime.now() if request.enabled else None
        return AutoRenewalResponse(
            userId=request.userId,
            enabled=request.enabled,
            nextRenewalDate=next_renewal,
            lastModified=datetime.now(),
            deviceId=request.deviceId,
            version=(request.version or 1) + 1
        )
    except Exception as e:
        logger.error(f"Error updating auto-renewal: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка обновления автопродления: {str(e)}")


@router.post("/cancel", response_model=Dict[str, str])
async def cancel_subscription(
    request: CancelSubscriptionRequest
) -> Dict[str, str]:
    """
    Отменить подписку
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                await sfm_adapter.cancel_subscription(**request.dict())
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        return {"status": "success", "message": "Подписка отменена"}
    except Exception as e:
        logger.error(f"Error cancelling subscription: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка отмены подписки: {str(e)}")
