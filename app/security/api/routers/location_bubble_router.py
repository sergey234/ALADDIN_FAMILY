# -*- coding: utf-8 -*-
"""
Location Bubble API Router
-------------------------
FastAPI endpoints для интеграции Location Bubble Agent с мобильным приложением iOS.
Маршруты для отчетов и управления местоположением.
"""

from datetime import datetime, timedelta
import uuid
from typing import Dict, List, Optional, Any
from enum import Enum

from fastapi import APIRouter, HTTPException, Query, Depends, Body
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging
import os

# ✅ ПОДКЛЮЧЕНИЕ К БД: Импортируем get_db для работы с базой данных
from app.database.database import get_db

# Импорты агента
try:
    from security.ai_agents.location_bubble_agent import LocationBubbleAgent
except ImportError:
    LocationBubbleAgent = None

logger = logging.getLogger(__name__)

# Создаем FastAPI Router с префиксом как в iOS AppConfig
router = APIRouter(prefix="/api/reports/privacy/location", tags=["Location Bubble Reports"])

# ═══════════════════════════════════════════════════════════════
# Pydantic модели (соответствуют iOS моделям)
# ═══════════════════════════════════════════════════════════════

class LocationAccuracy(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"

class LocationRequestAction(str, Enum):
    blocked = "blocked"
    allowed = "allowed"
    modified = "modified"

class LocationStats(BaseModel):
    blockedRequests: int = Field(..., alias="blockedRequests")
    allowedRequests: int = Field(..., alias="allowedRequests")
    modifiedRequests: int = Field(..., alias="modifiedRequests")
    currentAccuracy: LocationAccuracy

class LocationRequest(BaseModel):
    id: str
    appName: str
    timestamp: datetime
    action: LocationRequestAction
    accuracy: Optional[LocationAccuracy] = None

class ActionRequest(BaseModel):
    requestId: str

class UpdateAccuracyRequest(BaseModel):
    accuracy: LocationAccuracy

# ═══════════════════════════════════════════════════════════════
# API Endpoints
# ═══════════════════════════════════════════════════════════════

@router.get("/stats", response_model=LocationStats)
async def get_location_stats(db: Session = Depends(get_db)):
    """Получить статистику Location Bubble из базы данных"""
    try:
        # ✅ ПОДКЛЮЧЕНИЕ К БД: Получаем статистику из таблицы location_requests
        stats_query = text("""
            SELECT 
                COUNT(*) FILTER (WHERE action = 'blocked') as blocked_requests,
                COUNT(*) FILTER (WHERE action = 'allowed') as allowed_requests,
                COUNT(*) FILTER (WHERE action = 'modified') as modified_requests,
                COALESCE(MODE() WITHIN GROUP (ORDER BY accuracy), 'medium') as current_accuracy
            FROM location_requests
        """)
        
        result = db.execute(stats_query)
        row = result.fetchone()
        
        if row:
            return {
                "blockedRequests": row[0] or 0,
                "allowedRequests": row[1] or 0,
                "modifiedRequests": row[2] or 0,
                "currentAccuracy": row[3] if row[3] else "medium"
            }
        else:
            # Нет данных - возвращаем пустую статистику
            return {
                "blockedRequests": 0,
                "allowedRequests": 0,
                "modifiedRequests": 0,
                "currentAccuracy": "medium"
            }
    except Exception as e:
        # ✅ ОБРАБОТКА ОШИБОК: Graceful degradation - возвращаем пустую статистику
        print(f"⚠️ Ошибка получения статистики Location Bubble из БД: {e}")
        return {
            "blockedRequests": 0,
            "allowedRequests": 0,
            "modifiedRequests": 0,
            "currentAccuracy": "medium"
        }

@router.get("/requests", response_model=List[LocationRequest])
async def get_location_requests(
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Получить историю запросов местоположения из базы данных"""
    try:
        # ✅ ПОДКЛЮЧЕНИЕ К БД: Формируем SQL запрос
        query = text("""
            SELECT 
                id,
                app_name,
                timestamp,
                action,
                accuracy
            FROM location_requests
            ORDER BY timestamp DESC
            LIMIT :limit
        """)
        
        params = {"limit": limit}
        
        # ✅ ПОДКЛЮЧЕНИЕ К БД: Выполняем запрос
        result = db.execute(query, params)
        rows = result.fetchall()
        
        # ✅ ПОДКЛЮЧЕНИЕ К БД: Преобразуем результаты в модели
        requests = []
        for row in rows:
            request = LocationRequest(
                id=str(row[0]),
                appName=str(row[1]) if row[1] else "",
                timestamp=row[2],
                action=LocationRequestAction(row[3]),
                accuracy=LocationAccuracy(row[4]) if row[4] else None
            )
            requests.append(request)
        
        return requests
        
    except Exception as e:
        # ✅ ОБРАБОТКА ОШИБОК: Graceful degradation - возвращаем пустой список
        print(f"⚠️ Ошибка получения запросов Location Bubble из БД: {e}")
        return []

@router.post("/allow")
async def allow_location(request: ActionRequest, db: Session = Depends(get_db)):
    """Разрешить запрос местоположения в базе данных"""
    try:
        # ✅ ПОДКЛЮЧЕНИЕ К БД: Обновляем статус запроса
        query = text("""
            UPDATE location.location_requests
            SET action = 'allowed',
                timestamp = CURRENT_TIMESTAMP
            WHERE id = :request_id
        """)
        
        params = {"request_id": request.requestId}
        
        result = db.execute(query, params)
        db.commit()
        
        logger.info(f"✅ Location allowed for request: {request.requestId}")
        
        if result.rowcount > 0:
            return {"success": True, "message": "Request allowed"}
        else:
            raise HTTPException(status_code=404, detail=f"Request {request.requestId} not found")
            
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"⚠️ Ошибка обновления статуса запроса в БД: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update request status: {str(e)}")

@router.post("/block")
async def block_location(request: ActionRequest, db: Session = Depends(get_db)):
    """Заблокировать запрос местоположения в базе данных"""
    try:
        # ✅ ПОДКЛЮЧЕНИЕ К БД: Обновляем статус запроса
        query = text("""
            UPDATE location.location_requests
            SET action = 'blocked',
                timestamp = CURRENT_TIMESTAMP
            WHERE id = :request_id
        """)
        
        params = {"request_id": request.requestId}
        
        result = db.execute(query, params)
        db.commit()
        
        logger.info(f"🚫 Location blocked for request: {request.requestId}")
        
        if result.rowcount > 0:
            return {"success": True, "message": "Request blocked"}
        else:
            raise HTTPException(status_code=404, detail=f"Request {request.requestId} not found")
            
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"⚠️ Ошибка обновления статуса запроса в БД: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update request status: {str(e)}")

@router.post("/update-accuracy")
async def update_accuracy(
    request: UpdateAccuracyRequest,
    db: Session = Depends(get_db),
):
    """Обновить настройки точности (write-path для честного freshness)."""
    try:
        # Insert a "modified" marker so `analytics_freshness` sees freshness updates
        # via `location.location_requests.timestamp`.
        result = db.execute(
            text("""
                INSERT INTO location.location_requests
                    (id, app_name, timestamp, action, accuracy)
                VALUES
                    (gen_random_uuid(), 'accuracy_update', CURRENT_TIMESTAMP, 'modified', :accuracy)
            """),
            {"accuracy": request.accuracy.value},
        )
        db.commit()

        logger.info(f"📍 Location accuracy updated to: {request.accuracy} (rowcount={result.rowcount})")
        return {
            "success": True,
            "data": (result.rowcount or 0) > 0,
            "message": f"Accuracy updated to {request.accuracy}",
        }
    except Exception as e:
        db.rollback()
        logger.error(f"⚠️ Ошибка обновления accuracy в БД: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update accuracy: {str(e)}")

@router.get("/health")
async def health_check():
    return {"status": "healthy", "agent": "location_bubble_agent"}
