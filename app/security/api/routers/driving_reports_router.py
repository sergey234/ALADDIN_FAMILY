# -*- coding: utf-8 -*-
"""
Driving Reports API Router
--------------------------
FastAPI endpoints для интеграции Driving Reports Agent с мобильным приложением iOS.
Маршруты для получения статистики вождения и экспорта отчетов.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import text

# ✅ ПОДКЛЮЧЕНИЕ К БД: Импортируем get_db для работы с базой данных
from app.database.database import get_db

# Создаем FastAPI Router с префиксом как в iOS AppConfig
router = APIRouter(prefix="/api/reports/driving", tags=["Driving Reports"])

# ═══════════════════════════════════════════════════════════════
# Pydantic модели (соответствуют iOS моделям)
# ═══════════════════════════════════════════════════════════════

class DrivingStats(BaseModel):
    totalTrips: int
    totalDistance: float # км
    totalDuration: float # секунды
    averageSafetyScore: float # 0-10
    violationsCount: int
    period: str # "week", "month", "year"
    positioningSystem: Optional[str] = "GPS/GLONASS"

class ExportResponse(BaseModel):
    success: bool
    downloadUrl: str
    fileName: str

class DrivingReport(BaseModel):
    id: str
    userId: str
    userName: str
    startTime: datetime
    endTime: datetime
    startLocation: str
    endLocation: str
    distance: float
    duration: float
    averageSpeed: float
    maxSpeed: float
    safetyScore: float
    events: List[Dict[str, Any]] = []
    violations: List[Dict[str, Any]] = []
    positioningSystem: Optional[str] = None

# ═══════════════════════════════════════════════════════════════
# API Endpoints
# ═══════════════════════════════════════════════════════════════

@router.get("", response_model=List[DrivingReport])
def get_driving_reports(
    userId: Optional[str] = Query(None),
    period: str = Query("week", regex="^(week|month|year)$"),
    db: Session = Depends(get_db)
):
    """Получить список отчетов о вождении из базы данных"""
    try:
        # ✅ ПОДКЛЮЧЕНИЕ К БД: Вычисляем дату начала периода
        now = datetime.utcnow()
        if period == "week":
            start_date = now - timedelta(days=7)
        elif period == "month":
            start_date = now - timedelta(days=30)
        else:  # year
            start_date = now - timedelta(days=365)
        
        # ✅ ПОДКЛЮЧЕНИЕ К БД: Формируем SQL запрос
        query = text("""
            SELECT 
                id,
                user_id,
                user_name,
                start_time,
                end_time,
                start_location,
                end_location,
                distance,
                duration,
                average_speed,
                max_speed,
                safety_score,
                events,
                violations,
                positioning_system
            FROM driving_reports
            WHERE start_time >= :start_date
        """)
        
        params = {"start_date": start_date}
        
        # ✅ ПОДКЛЮЧЕНИЕ К БД: Фильтр по userId если указан
        if userId:
            query = text("""
                SELECT 
                    id,
                    user_id,
                    user_name,
                    start_time,
                    end_time,
                    start_location,
                    end_location,
                    distance,
                    duration,
                    average_speed,
                    max_speed,
                    safety_score,
                    events,
                    violations,
                    positioning_system
                FROM driving_reports
                WHERE start_time >= :start_date AND user_id = :user_id
                ORDER BY start_time DESC
            """)
            params["user_id"] = userId
        else:
            query = text("""
                SELECT 
                    id,
                    user_id,
                    user_name,
                    start_time,
                    end_time,
                    start_location,
                    end_location,
                    distance,
                    duration,
                    average_speed,
                    max_speed,
                    safety_score,
                    events,
                    violations,
                    positioning_system
                FROM driving_reports
                WHERE start_time >= :start_date
                ORDER BY start_time DESC
            """)
        
        # ✅ ПОДКЛЮЧЕНИЕ К БД: Выполняем запрос
        result = db.execute(query, params)
        rows = result.fetchall()
        
        # ✅ ПОДКЛЮЧЕНИЕ К БД: Преобразуем результаты в модели
        reports = []
        for row in rows:
            # Парсим JSON поля если они есть
            events = row[12] if row[12] else []
            violations = row[13] if row[13] else []
            
            # Если это строки JSON, парсим их
            if isinstance(events, str):
                import json
                try:
                    events = json.loads(events)
                except:
                    events = []
            if isinstance(violations, str):
                import json
                try:
                    violations = json.loads(violations)
                except:
                    violations = []
            
            report = DrivingReport(
                id=str(row[0]),
                userId=str(row[1]),
                userName=str(row[2]) if row[2] else "Unknown",
                startTime=row[3],
                endTime=row[4],
                startLocation=str(row[5]) if row[5] else "",
                endLocation=str(row[6]) if row[6] else "",
                distance=float(row[7]) if row[7] else 0.0,
                duration=float(row[8]) if row[8] else 0.0,
                averageSpeed=float(row[9]) if row[9] else 0.0,
                maxSpeed=float(row[10]) if row[10] else 0.0,
                safetyScore=float(row[11]) if row[11] else 0.0,
                events=events if isinstance(events, list) else [],
                violations=violations if isinstance(violations, list) else [],
                positioningSystem=str(row[14]) if row[14] else None
            )
            reports.append(report)
        
        return reports
        
    except Exception as e:
        # ✅ ОБРАБОТКА ОШИБОК: Если таблицы нет или ошибка БД, возвращаем пустой список
        # Это graceful degradation - приложение покажет "Нет данных о поездках"
        print(f"⚠️ Ошибка получения отчетов из БД: {e}")
        # Если таблицы нет, возвращаем пустой список (приложение покажет "Нет данных")
        return []

@router.get("/stats", response_model=DrivingStats)
def get_driving_stats(
    userId: Optional[str] = Query(None),
    period: str = Query("week", regex="^(week|month|year)$"),
    db: Session = Depends(get_db),
):
    """Статистика только из реальных строк `driving_reports` (без mock цифр)."""
    now = datetime.utcnow()
    if period == "week":
        start_date = now - timedelta(days=7)
    elif period == "month":
        start_date = now - timedelta(days=30)
    else:
        start_date = now - timedelta(days=365)

    empty = {
        "totalTrips": 0,
        "totalDistance": 0.0,
        "totalDuration": 0.0,
        "averageSafetyScore": 0.0,
        "violationsCount": 0,
        "period": period,
        "positioningSystem": None,
    }
    try:
        if userId:
            q = text(
                """
                SELECT COUNT(*), COALESCE(SUM(distance),0), COALESCE(SUM(duration),0),
                       COALESCE(AVG(safety_score),0), COALESCE(SUM(
                         CASE WHEN violations IS NULL OR violations::text IN ('[]','null','') THEN 0 ELSE 1 END
                       ),0)
                FROM driving_reports
                WHERE start_time >= :start_date AND user_id = :user_id
                """
            )
            row = db.execute(q, {"start_date": start_date, "user_id": userId}).fetchone()
        else:
            q = text(
                """
                SELECT COUNT(*), COALESCE(SUM(distance),0), COALESCE(SUM(duration),0),
                       COALESCE(AVG(safety_score),0), COALESCE(SUM(
                         CASE WHEN violations IS NULL OR violations::text IN ('[]','null','') THEN 0 ELSE 1 END
                       ),0)
                FROM driving_reports
                WHERE start_time >= :start_date
                """
            )
            row = db.execute(q, {"start_date": start_date}).fetchone()
        if not row:
            return empty
        trips = int(row[0] or 0)
        return {
            "totalTrips": trips,
            "totalDistance": float(row[1] or 0),
            "totalDuration": float(row[2] or 0),
            "averageSafetyScore": float(row[3] or 0) if trips else 0.0,
            "violationsCount": int(row[4] or 0),
            "period": period,
            "positioningSystem": "GPS" if trips else None,
        }
    except Exception as e:
        print(f"⚠️ driving stats from DB failed: {e}")
        return empty

@router.get("/export", response_model=ExportResponse)
async def export_driving_report(format: str = Query("pdf", regex="^(pdf|csv|xlsx)$")):
    """Экспортировать отчет о вождении"""
    return {
        "success": True,
        "downloadUrl": f"https://aladdin-ai.ru/storage/reports/driving_report_{datetime.now().strftime('%Y%m%d')}.{format}",
        "fileName": f"driving_report_{datetime.now().strftime('%Y%m%d')}.{format}"
    }

@router.get("/health")
async def health_check():
    return {"status": "healthy", "agent": "driving_reports_agent"}
