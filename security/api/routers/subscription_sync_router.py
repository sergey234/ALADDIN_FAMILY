# -*- coding: utf-8 -*-
"""
Subscription Sync API Router (REAL IMPLEMENTATION)
----------------------------
FastAPI endpoints для синхронизации тарифов и подписок между устройствами.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, HTTPException, Query, Path, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import logging
import sys
import os

from app.database.database import get_db
from app.services.audit_service import AuditService
from app.repositories import SubscriptionRepository

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

from app.auth.auth import get_current_user

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


# =============================================================================
# API Endpoints
# =============================================================================

@router.post("/sync", response_model=SyncSubscriptionResponse)
async def sync_subscription(
    request: SyncSubscriptionRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> SyncSubscriptionResponse:
    """
    Синхронизировать информацию о подписке между устройствами (REAL DB)
    """
    try:
        repo = SubscriptionRepository(db)
        subscription = repo.get_subscription_by_user_device(request.userId, request.deviceId)
        
        if not subscription:
            # Create default free subscription if not exists
            subscription = repo.create_subscription({
                "user_id": request.userId,
                "device_id": request.deviceId,
                "level": "free",
                "status": "active",
                "start_date": datetime.now()
            })
            AuditService.log_event(db, "created", subscription.id, request.userId, request.deviceId)

        resp_sub = SubscriptionResponse(
            userId=subscription.user_id,
            subscriptionType=subscription.level,
            status=subscription.status,
            startDate=subscription.start_date,
            endDate=subscription.end_date,
            autoRenewal=subscription.auto_renew,
            lastModified=subscription.updated_at,
            deviceId=subscription.device_id,
            version=subscription.version
        )
        
        AuditService.log_event(db, "sync", subscription.id, request.userId, request.deviceId)
        
        return SyncSubscriptionResponse(
            userId=request.userId,
            subscription=resp_sub,
            conflicts=[],
            lastSyncTimestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"Error syncing subscription: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка синхронизации подписки: {str(e)}")


@router.post("/update", response_model=SubscriptionResponse)
async def update_subscription(
    request: UpdateSubscriptionRequest,
    db: Session = Depends(get_db)
) -> SubscriptionResponse:
    """
    Обновить информацию о подписке (REAL DB)
    """
    try:
        repo = SubscriptionRepository(db)
        subscription = repo.get_subscription_by_user_device(request.userId, request.deviceId or "migrated")
        
        if not subscription:
            raise HTTPException(status_code=404, detail="Подписка не найдена")

        old_values = {"level": subscription.level, "status": subscription.status}
        
        updates = {}
        if request.subscriptionType: updates["level"] = request.subscriptionType
        if request.status: updates["status"] = request.status
        if request.endDate: updates["end_date"] = request.endDate
        
        subscription = repo.update_subscription(subscription.id, updates)
        
        AuditService.log_event(
            db, "updated", subscription.id, request.userId, request.deviceId,
            old_values=old_values, new_values=updates
        )

        return SubscriptionResponse(
            userId=subscription.user_id,
            subscriptionType=subscription.level,
            status=subscription.status,
            startDate=subscription.start_date,
            endDate=subscription.end_date,
            autoRenewal=subscription.auto_renew,
            lastModified=subscription.updated_at,
            deviceId=subscription.device_id,
            version=subscription.version
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating subscription: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка обновления подписки: {str(e)}")


@router.get("/status", response_model=SubscriptionStatusResponse)
async def get_subscription_status(
    userId: str = Query(..., description="ID пользователя"),
    db: Session = Depends(get_db)
) -> SubscriptionStatusResponse:
    """
    Получить статус подписки (REAL DB)
    """
    try:
        repo = SubscriptionRepository(db)
        # Check all devices for this user
        subscription = db.query(repo.Subscription).filter(repo.Subscription.user_id == userId).first()
        
        if not subscription:
            return SubscriptionStatusResponse(
                userId=userId,
                isActive=False,
                daysRemaining=0,
                canRenew=False,
                lastModified=datetime.now()
            )
        
        is_active = subscription.status == "active" or subscription.status == "trial"
        days_remaining = None
        if subscription.end_date:
            days_remaining = (subscription.end_date - datetime.now()).days
        
        return SubscriptionStatusResponse(
            userId=userId,
            isActive=is_active,
            daysRemaining=max(0, days_remaining) if days_remaining is not None else None,
            canRenew=True,
            lastModified=subscription.updated_at
        )
    except Exception as e:
        logger.error(f"Error getting subscription status: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения статуса подписки: {str(e)}")
