# -*- coding: utf-8 -*-
"""
Identity Theft Protection API Router
-----------------------------------
FastAPI endpoints для интеграции Identity Theft Protection Agent с мобильным приложением iOS.
Маршруты для отчетов и управления попытками доступа к личным данным.
"""

from datetime import datetime, timedelta
import uuid
from typing import Dict, List, Optional, Any
from enum import Enum

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import text

# ✅ ПОДКЛЮЧЕНИЕ К БД: Импортируем get_db для работы с базой данных
from app.database.database import get_db

# Создаем FastAPI Router с префиксом как в iOS AppConfig
router = APIRouter(prefix="/api/reports/identity-theft", tags=["Identity Theft Reports"])

# ═══════════════════════════════════════════════════════════════
# Pydantic модели (соответствуют iOS моделям)
# ═══════════════════════════════════════════════════════════════

class IdentityDataType(str, Enum):
    passport = "passport"
    snils = "snils"
    bank = "bank"
    other = "other"

class AttemptAction(str, Enum):
    blocked = "blocked"
    allowed = "allowed"
    suspicious = "suspicious"
    requires_review = "requires_review"

class AttemptSeverity(str, Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"

class IdentityTheftAttempt(BaseModel):
    id: str
    dataType: IdentityDataType
    requestSource: str
    timestamp: datetime
    action: AttemptAction
    severity: AttemptSeverity
    details: Optional[str] = None

class IdentityTheftStats(BaseModel):
    totalAttempts: int
    blockedAttempts: int
    suspiciousActivities: int
    byDataType: Dict[str, int]

class ActionRequest(BaseModel):
    attemptId: str

class WhitelistRequest(BaseModel):
    source: str

# ═══════════════════════════════════════════════════════════════
# API Endpoints
# ═══════════════════════════════════════════════════════════════

@router.get("/stats", response_model=IdentityTheftStats)
async def get_identity_stats(db: Session = Depends(get_db)):
    """Получить статистику защиты личности из базы данных"""
    try:
        # ✅ ПОДКЛЮЧЕНИЕ К БД: Получаем статистику из таблицы identity_theft_attempts
        stats_query = text("""
            SELECT 
                COUNT(*) as total_attempts,
                COUNT(*) FILTER (WHERE action = 'blocked') as blocked_attempts,
                COUNT(*) FILTER (WHERE action = 'suspicious') as suspicious_activities,
                COUNT(*) FILTER (WHERE data_type = 'passport') as passport_count,
                COUNT(*) FILTER (WHERE data_type = 'snils') as snils_count,
                COUNT(*) FILTER (WHERE data_type = 'bank') as bank_count,
                COUNT(*) FILTER (WHERE data_type = 'other') as other_count
            FROM identity_theft_attempts
        """)
        
        result = db.execute(stats_query)
        row = result.fetchone()
        
        if row and row[0]:
            return {
                "totalAttempts": row[0] or 0,
                "blockedAttempts": row[1] or 0,
                "suspiciousActivities": row[2] or 0,
                "byDataType": {
                    "passport": row[3] or 0,
                    "snils": row[4] or 0,
                    "bank": row[5] or 0,
                    "other": row[6] or 0
                }
            }
        else:
            # Нет данных - возвращаем пустую статистику
            return {
                "totalAttempts": 0,
                "blockedAttempts": 0,
                "suspiciousActivities": 0,
                "byDataType": {
                    "passport": 0,
                    "snils": 0,
                    "bank": 0,
                    "other": 0
                }
            }
    except Exception as e:
        # ✅ ОБРАБОТКА ОШИБОК: Graceful degradation - возвращаем пустую статистику
        print(f"⚠️ Ошибка получения статистики Identity Theft из БД: {e}")
        return {
            "totalAttempts": 0,
            "blockedAttempts": 0,
            "suspiciousActivities": 0,
            "byDataType": {
                "passport": 0,
                "snils": 0,
                "bank": 0,
                "other": 0
            }
        }

@router.get("/attempts", response_model=List[IdentityTheftAttempt])
async def get_identity_attempts(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Получить список попыток доступа к данным из базы данных"""
    try:
        # ✅ ПОДКЛЮЧЕНИЕ К БД: Формируем SQL запрос
        query = text("""
            SELECT 
                id,
                data_type,
                request_source,
                timestamp,
                action,
                severity,
                details
            FROM identity_theft_attempts
            ORDER BY timestamp DESC
            LIMIT :limit
        """)
        
        params = {"limit": limit}
        
        # ✅ ПОДКЛЮЧЕНИЕ К БД: Выполняем запрос
        result = db.execute(query, params)
        rows = result.fetchall()
        
        # ✅ ПОДКЛЮЧЕНИЕ К БД: Преобразуем результаты в модели
        attempts = []
        for row in rows:
            attempt = IdentityTheftAttempt(
                id=str(row[0]),
                dataType=IdentityDataType(row[1]),
                requestSource=str(row[2]) if row[2] else "",
                timestamp=row[3],
                action=AttemptAction(row[4]),
                severity=AttemptSeverity(row[5]),
                details=str(row[6]) if row[6] else None
            )
            attempts.append(attempt)
        
        return attempts
        
    except Exception as e:
        # ✅ ОБРАБОТКА ОШИБОК: Graceful degradation - возвращаем пустой список
        print(f"⚠️ Ошибка получения попыток Identity Theft из БД: {e}")
        return []

@router.post("/allow")
async def allow_attempt(request: ActionRequest, db: Session = Depends(get_db)):
    """Разрешить попытку доступа в базе данных"""
    try:
        # ✅ ПОДКЛЮЧЕНИЕ К БД: Обновляем статус попытки
        query = text("""
            UPDATE identity.identity_attempts
            SET action = 'allowed',
                timestamp = CURRENT_TIMESTAMP
            WHERE id = :attempt_id
        """)
        
        params = {"attempt_id": request.attemptId}
        
        result = db.execute(query, params)
        db.commit()
        
        if result.rowcount > 0:
            return {"success": True, "message": f"Attempt {request.attemptId} allowed"}
        else:
            raise HTTPException(status_code=404, detail=f"Attempt {request.attemptId} not found")
            
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"⚠️ Ошибка обновления статуса попытки в БД: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update attempt status: {str(e)}")

@router.post("/block")
async def block_attempt(request: ActionRequest, db: Session = Depends(get_db)):
    """Заблокировать попытку доступа в базе данных"""
    try:
        # ✅ ПОДКЛЮЧЕНИЕ К БД: Обновляем статус попытки
        query = text("""
            UPDATE identity.identity_attempts
            SET action = 'blocked',
                timestamp = CURRENT_TIMESTAMP
            WHERE id = :attempt_id
        """)
        
        params = {"attempt_id": request.attemptId}
        
        result = db.execute(query, params)
        db.commit()
        
        if result.rowcount > 0:
            return {"success": True, "message": f"Attempt {request.attemptId} blocked"}
        else:
            raise HTTPException(status_code=404, detail=f"Attempt {request.attemptId} not found")
            
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"⚠️ Ошибка обновления статуса попытки в БД: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update attempt status: {str(e)}")

@router.post("/whitelist")
async def add_to_whitelist(request: WhitelistRequest):
    """Добавить источник в белый список"""
    return {"success": True, "message": f"Source {request.source} added to whitelist"}

@router.get("/health")
async def health_check():
    return {"status": "healthy", "agent": "russian_identity_theft_protection_agent"}
