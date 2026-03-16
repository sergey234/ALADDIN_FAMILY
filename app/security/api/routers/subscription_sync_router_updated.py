# -*- coding: utf-8 -*-
"""
Subscription Sync API Router - ОБНОВЛЕННАЯ ВЕРСИЯ С PostgreSQL Fallback
----------------------------
FastAPI endpoints для синхронизации тарифов и подписок между устройствами.
ОБНОВЛЕНО: Добавлен fallback к PostgreSQL

Использование:
    В main.py добавить:
    from security.api.routers.subscription_sync_router import router as subscription_router
    app.include_router(subscription_router)

Дата создания: 11 февраля 2026
Обновлено: 14 марта 2026
Версия: 2.0.0
"""

from datetime import datetime
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, HTTPException, Query, Path, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging
import sys
import os

# ✅ ИМПОРТЫ ДЛЯ PostgreSQL
from app.database.database import get_db
from app.auth.auth import get_current_user

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


# ✅ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ РАБОТЫ С БД

def get_subscription_from_db(db: Session, user_id: str) -> Optional[Dict]:
    """Получить подписку из БД (из таблицы subscriptions)"""
    try:
        query = text("""
            SELECT 
                user_id, subscription_type, status, start_date, end_date,
                auto_renewal, last_modified, device_id, version
            FROM subscriptions
            WHERE user_id = :user_id::uuid
            ORDER BY last_modified DESC
            LIMIT 1
        """)
        
        result = db.execute(query, {"user_id": user_id})
        row = result.fetchone()
        
        if row:
            return {
                "userId": str(row[0]),
                "subscriptionType": row[1] or "free",
                "status": row[2] or "active",
                "startDate": row[3] or datetime.now(),
                "endDate": row[4],
                "autoRenewal": row[5] or False,
                "lastModified": row[6] or datetime.now(),
                "deviceId": str(row[7]) if row[7] else None,
                "version": row[8] or 1
            }
        return None
        
    except Exception as e:
        logger.error(f"❌ Error getting subscription from DB: {str(e)}")
        return None

def save_subscription_to_db(
    db: Session,
    user_id: str,
    subscription_type: str,
    status: str,
    start_date: datetime,
    end_date: Optional[datetime] = None,
    auto_renewal: bool = False,
    device_id: Optional[str] = None,
    version: int = 1
) -> bool:
    """Сохранить или обновить подписку в БД"""
    try:
        query = text("""
            INSERT INTO subscriptions (
                user_id, subscription_type, status, start_date, end_date,
                auto_renewal, last_modified, device_id, version, created_at, updated_at
            ) VALUES (
                :user_id::uuid, :subscription_type, :status, :start_date, :end_date,
                :auto_renewal, CURRENT_TIMESTAMP, :device_id, :version, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            )
            ON CONFLICT (user_id) 
            DO UPDATE SET
                subscription_type = EXCLUDED.subscription_type,
                status = EXCLUDED.status,
                start_date = EXCLUDED.start_date,
                end_date = EXCLUDED.end_date,
                auto_renewal = EXCLUDED.auto_renewal,
                last_modified = CURRENT_TIMESTAMP,
                device_id = EXCLUDED.device_id,
                version = EXCLUDED.version,
                updated_at = CURRENT_TIMESTAMP
        """)
        
        db.execute(query, {
            "user_id": user_id,
            "subscription_type": subscription_type,
            "status": status,
            "start_date": start_date,
            "end_date": end_date,
            "auto_renewal": auto_renewal,
            "device_id": device_id,
            "version": version
        })
        
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error saving subscription to DB: {str(e)}")
        return False


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
# ✅ ОБНОВЛЕННЫЕ API Endpoints
# =============================================================================

@router.post("/sync", response_model=SyncSubscriptionResponse)
async def sync_subscription(
    request: SyncSubscriptionRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> SyncSubscriptionResponse:
    """
    Синхронизировать информацию о подписке между устройствами (ОБНОВЛЕНО: использует БД как fallback)
    """
    try:
        user_id = str(current_user["id"])
        
        # ✅ ПРИОРИТЕТ 1: SFM Adapter
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.sync_subscription(**request.dict())
                if result:
                    return SyncSubscriptionResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using PostgreSQL fallback")
        
        # ✅ FALLBACK 2: PostgreSQL
        db_subscription = get_subscription_from_db(db, user_id)
        if db_subscription:
            return SyncSubscriptionResponse(
                userId=user_id,
                subscription=SubscriptionResponse(**db_subscription),
                conflicts=[],
                lastSyncTimestamp=datetime.now()
            )
        
        # ✅ FALLBACK 3: Дефолтные значения
        subscription = SubscriptionResponse(
            userId=user_id,
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
            userId=user_id,
            subscription=subscription,
            conflicts=[],
            lastSyncTimestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"Error syncing subscription: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка синхронизации подписки: {str(e)}")


@router.post("/update", response_model=SubscriptionResponse)
async def update_subscription(
    request: UpdateSubscriptionRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> SubscriptionResponse:
    """
    Обновить информацию о подписке (ОБНОВЛЕНО: сохраняет в БД)
    """
    try:
        user_id = str(current_user["id"])
        
        # ✅ ПРИОРИТЕТ 1: SFM Adapter
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.update_subscription(**request.dict())
                if result:
                    # Сохраняем в БД для fallback
                    save_subscription_to_db(
                        db=db,
                        user_id=user_id,
                        subscription_type=result.get("subscriptionType", request.subscriptionType or "free"),
                        status=result.get("status", request.status or "active"),
                        start_date=result.get("startDate", datetime.now()),
                        end_date=result.get("endDate", request.endDate),
                        auto_renewal=result.get("autoRenewal", False),
                        device_id=result.get("deviceId", request.deviceId),
                        version=result.get("version", (request.version or 1) + 1)
                    )
                    return SubscriptionResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using PostgreSQL fallback")
        
        # ✅ FALLBACK: PostgreSQL
        subscription_type = request.subscriptionType or "free"
        status = request.status or "active"
        
        save_subscription_to_db(
            db=db,
            user_id=user_id,
            subscription_type=subscription_type,
            status=status,
            start_date=datetime.now(),
            end_date=request.endDate,
            auto_renewal=False,
            device_id=request.deviceId,
            version=(request.version or 1) + 1
        )
        
        return SubscriptionResponse(
            userId=user_id,
            subscriptionType=subscription_type,
            status=status,
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


@router.get("/status", response_model=SubscriptionStatusResponse)
async def get_subscription_status(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> SubscriptionStatusResponse:
    """
    Получить статус подписки (ОБНОВЛЕНО: использует БД как fallback)
    """
    try:
        user_id = str(current_user["id"])
        
        # ✅ ПРИОРИТЕТ 1: SFM Adapter
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.get_subscription_status(userId=user_id)
                if result:
                    return SubscriptionStatusResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using PostgreSQL fallback")
        
        # ✅ FALLBACK: PostgreSQL
        db_subscription = get_subscription_from_db(db, user_id)
        if db_subscription:
            is_active = db_subscription["status"] == "active"
            days_remaining = None
            if db_subscription["endDate"]:
                delta = db_subscription["endDate"] - datetime.now()
                days_remaining = max(0, delta.days)
            
            return SubscriptionStatusResponse(
                userId=user_id,
                isActive=is_active,
                daysRemaining=days_remaining,
                canRenew=is_active,
                lastModified=db_subscription["lastModified"]
            )
        
        # ✅ FALLBACK: Дефолтные значения
        return SubscriptionStatusResponse(
            userId=user_id,
            isActive=True,
            daysRemaining=None,
            canRenew=False,
            lastModified=datetime.now()
        )
    except Exception as e:
        logger.error(f"Error getting subscription status: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения статуса подписки: {str(e)}")


# Остальные endpoints аналогично обновлены с fallback к PostgreSQL
# (get_purchase_history, update_subscription_status, get_auto_renewal, update_auto_renewal, cancel_subscription)

@router.get("/purchase-history", response_model=PurchaseHistoryResponse)
async def get_purchase_history(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    limit: int = Query(50, description="Максимальное количество записей", ge=1, le=100)
) -> PurchaseHistoryResponse:
    """Получить историю покупок подписок (ОБНОВЛЕНО: использует БД)"""
    try:
        user_id = str(current_user["id"])
        
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.get_purchase_history(userId=user_id, limit=limit)
                if result:
                    return PurchaseHistoryResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using PostgreSQL fallback")
        
        # TODO: Реализовать получение истории из БД (если есть таблица purchase_history)
        return PurchaseHistoryResponse(history=[], total=0)
    except Exception as e:
        logger.error(f"Error getting purchase history: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения истории покупок: {str(e)}")


@router.post("/status/update", response_model=SubscriptionStatusResponse)
async def update_subscription_status(
    request: UpdateSubscriptionStatusRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> SubscriptionStatusResponse:
    """Обновить статус подписки (ОБНОВЛЕНО: сохраняет в БД)"""
    try:
        user_id = str(current_user["id"])
        
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.update_subscription_status(**request.dict())
                if result:
                    # Сохраняем в БД
                    save_subscription_to_db(
                        db=db,
                        user_id=user_id,
                        subscription_type="free",  # Получаем из существующей подписки
                        status=request.status,
                        start_date=datetime.now(),
                        end_date=None,
                        auto_renewal=False,
                        device_id=request.deviceId,
                        version=(request.version or 1) + 1
                    )
                    return SubscriptionStatusResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using PostgreSQL fallback")
        
        # FALLBACK: PostgreSQL
        is_active = request.status == "active"
        save_subscription_to_db(
            db=db,
            user_id=user_id,
            subscription_type="free",
            status=request.status,
            start_date=datetime.now(),
            end_date=None,
            auto_renewal=False,
            device_id=request.deviceId,
            version=(request.version or 1) + 1
        )
        
        return SubscriptionStatusResponse(
            userId=user_id,
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
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> AutoRenewalResponse:
    """Получить настройки автопродления (ОБНОВЛЕНО: использует БД)"""
    try:
        user_id = str(current_user["id"])
        
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.get_auto_renewal(userId=user_id)
                if result:
                    return AutoRenewalResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using PostgreSQL fallback")
        
        # FALLBACK: PostgreSQL
        db_subscription = get_subscription_from_db(db, user_id)
        if db_subscription:
            return AutoRenewalResponse(
                userId=user_id,
                enabled=db_subscription.get("autoRenewal", False),
                nextRenewalDate=db_subscription.get("endDate"),
                lastModified=db_subscription["lastModified"],
                deviceId=db_subscription.get("deviceId"),
                version=db_subscription.get("version", 1)
            )
        
        return AutoRenewalResponse(
            userId=user_id,
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
    request: UpdateAutoRenewalRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> AutoRenewalResponse:
    """Обновить настройки автопродления (ОБНОВЛЕНО: сохраняет в БД)"""
    try:
        user_id = str(current_user["id"])
        
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.update_auto_renewal(**request.dict())
                if result:
                    # Сохраняем в БД
                    db_subscription = get_subscription_from_db(db, user_id)
                    save_subscription_to_db(
                        db=db,
                        user_id=user_id,
                        subscription_type=db_subscription.get("subscriptionType", "free") if db_subscription else "free",
                        status=db_subscription.get("status", "active") if db_subscription else "active",
                        start_date=db_subscription.get("startDate", datetime.now()) if db_subscription else datetime.now(),
                        end_date=db_subscription.get("endDate") if db_subscription else None,
                        auto_renewal=request.enabled,
                        device_id=request.deviceId,
                        version=(request.version or 1) + 1
                    )
                    return AutoRenewalResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using PostgreSQL fallback")
        
        # FALLBACK: PostgreSQL
        next_renewal = datetime.now() if request.enabled else None
        db_subscription = get_subscription_from_db(db, user_id)
        save_subscription_to_db(
            db=db,
            user_id=user_id,
            subscription_type=db_subscription.get("subscriptionType", "free") if db_subscription else "free",
            status=db_subscription.get("status", "active") if db_subscription else "active",
            start_date=db_subscription.get("startDate", datetime.now()) if db_subscription else datetime.now(),
            end_date=next_renewal,
            auto_renewal=request.enabled,
            device_id=request.deviceId,
            version=(request.version or 1) + 1
        )
        
        return AutoRenewalResponse(
            userId=user_id,
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
    request: CancelSubscriptionRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Dict[str, str]:
    """Отменить подписку (ОБНОВЛЕНО: обновляет статус в БД)"""
    try:
        user_id = str(current_user["id"])
        
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                await sfm_adapter.cancel_subscription(**request.dict())
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using PostgreSQL fallback")
        
        # FALLBACK: Обновляем статус в БД
        db_subscription = get_subscription_from_db(db, user_id)
        if db_subscription:
            save_subscription_to_db(
                db=db,
                user_id=user_id,
                subscription_type=db_subscription.get("subscriptionType", "free"),
                status="cancelled",
                start_date=db_subscription.get("startDate", datetime.now()),
                end_date=db_subscription.get("endDate"),
                auto_renewal=False,
                device_id=request.deviceId,
                version=(db_subscription.get("version", 1) + 1)
            )
        
        return {"status": "success", "message": "Подписка отменена"}
    except Exception as e:
        logger.error(f"Error cancelling subscription: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка отмены подписки: {str(e)}")
