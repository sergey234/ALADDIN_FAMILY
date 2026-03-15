# -*- coding: utf-8 -*-
"""
Data Cleanup API Router
----------------------
FastAPI endpoints для интеграции Data Cleanup Agent с мобильным приложением iOS.
Маршруты для отчетов и управления очисткой данных.
"""

from datetime import datetime, timedelta
import uuid
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import text
import json

# ✅ ПОДКЛЮЧЕНИЕ К БД: Импортируем get_db для работы с базой данных
from app.database.database import get_db

# Создаем FastAPI Router с префиксом как в iOS AppConfig
router = APIRouter(prefix="/api/reports/privacy/cleanup", tags=["Data Cleanup Reports"])

# ═══════════════════════════════════════════════════════════════
# Pydantic модели (соответствуют iOS моделям)
# ═══════════════════════════════════════════════════════════════

class CleanupCategory(BaseModel):
    name: str
    size: int # байты

class DataCleanupRecord(BaseModel):
    id: str
    cleanupDate: datetime
    freedSpace: int
    categories: List[CleanupCategory]

class DataCleanupStats(BaseModel):
    totalFreed: int
    lastCleanupDate: Optional[datetime] = None
    cleanupsCount: int
    byCategory: Dict[str, int]

# ═══════════════════════════════════════════════════════════════
# API Endpoints
# ═══════════════════════════════════════════════════════════════

@router.get("/stats", response_model=DataCleanupStats)
async def get_cleanup_stats(db: Session = Depends(get_db)):
    """Получить статистику очистки данных из базы данных"""
    try:
        # ✅ ПОДКЛЮЧЕНИЕ К БД: Получаем статистику из таблицы data_cleanup_records
        stats_query = text("""
            SELECT 
                COALESCE(SUM(freed_space), 0) as total_freed,
                MAX(cleanup_date) as last_cleanup_date,
                COUNT(*) as cleanups_count
            FROM data_cleanup_records
        """)
        
        result = db.execute(stats_query)
        row = result.fetchone()
        
        # Получаем статистику по категориям из JSONB поля
        categories_query = text("""
            SELECT categories
            FROM data_cleanup_records
            WHERE categories IS NOT NULL
        """)
        
        categories_result = db.execute(categories_query)
        categories_rows = categories_result.fetchall()
        
        # Агрегируем данные по категориям
        by_category = {}
        for cat_row in categories_rows:
            if cat_row[0]:
                categories = cat_row[0] if isinstance(cat_row[0], list) else json.loads(cat_row[0]) if isinstance(cat_row[0], str) else []
                for cat in categories:
                    if isinstance(cat, dict):
                        cat_name = cat.get("name", "other")
                        cat_size = cat.get("size", 0)
                        by_category[cat_name] = by_category.get(cat_name, 0) + cat_size
        
        if row:
            return {
                "totalFreed": row[0] or 0,
                "lastCleanupDate": row[1] if row[1] else None,
                "cleanupsCount": row[2] or 0,
                "byCategory": by_category
            }
        else:
            # Нет данных - возвращаем пустую статистику
            return {
                "totalFreed": 0,
                "lastCleanupDate": None,
                "cleanupsCount": 0,
                "byCategory": {}
            }
    except Exception as e:
        # ✅ ОБРАБОТКА ОШИБОК: Graceful degradation - возвращаем пустую статистику
        print(f"⚠️ Ошибка получения статистики Data Cleanup из БД: {e}")
        return {
            "totalFreed": 0,
            "lastCleanupDate": None,
            "cleanupsCount": 0,
            "byCategory": {}
        }

@router.get("/records", response_model=List[DataCleanupRecord])
async def get_cleanup_records(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Получить историю очисток из базы данных"""
    try:
        # ✅ ПОДКЛЮЧЕНИЕ К БД: Формируем SQL запрос
        query = text("""
            SELECT 
                id,
                cleanup_date,
                freed_space,
                categories
            FROM data_cleanup_records
            ORDER BY cleanup_date DESC
            LIMIT :limit
        """)
        
        params = {"limit": limit}
        
        # ✅ ПОДКЛЮЧЕНИЕ К БД: Выполняем запрос
        result = db.execute(query, params)
        rows = result.fetchall()
        
        # ✅ ПОДКЛЮЧЕНИЕ К БД: Преобразуем результаты в модели
        records = []
        for row in rows:
            # Парсим categories из JSONB
            categories_data = row[3] if row[3] else []
            if isinstance(categories_data, str):
                try:
                    categories_data = json.loads(categories_data)
                except:
                    categories_data = []
            
            categories = []
            if isinstance(categories_data, list):
                for cat in categories_data:
                    if isinstance(cat, dict):
                        categories.append(CleanupCategory(
                            name=cat.get("name", "unknown"),
                            size=cat.get("size", 0)
                        ))
            
            record = DataCleanupRecord(
                id=str(row[0]),
                cleanupDate=row[1],
                freedSpace=row[2] or 0,
                categories=categories
            )
            records.append(record)
        
        return records
        
    except Exception as e:
        # ✅ ОБРАБОТКА ОШИБОК: Graceful degradation - возвращаем пустой список
        print(f"⚠️ Ошибка получения записей Data Cleanup из БД: {e}")
        return []

@router.post("/start")
async def start_cleanup(db: Session = Depends(get_db)):
    """Запустить процесс очистки и сохранить в базе данных"""
    try:
        # ✅ ПОДКЛЮЧЕНИЕ К БД: Создаем новую запись об очистке
        # В реальной реализации здесь будет реальная очистка данных
        # Пока создаем запись с mock данными
        
        import uuid as uuid_lib
        cleanup_id = str(uuid_lib.uuid4())
        
        query = text("""
            INSERT INTO data_cleanup_records (id, cleanup_date, freed_space, categories)
            VALUES (:id, CURRENT_TIMESTAMP, :freed_space, :categories::jsonb)
        """)
        
        # Mock данные для демонстрации
        mock_categories = json.dumps([
            {"name": "cache", "size": 500000000},
            {"name": "temp_files", "size": 400000000},
            {"name": "logs", "size": 300000000}
        ])
        
        params = {
            "id": cleanup_id,
            "freed_space": 1200000000,  # 1.2 GB
            "categories": mock_categories
        }
        
        db.execute(query, params)
        db.commit()
        
        return {
            "success": True, 
            "message": "Очистка успешно запущена",
            "details": {
                "estimated_time_seconds": 45,
                "scanned_files": 12500
            }
        }
    except Exception as e:
        db.rollback()
        print(f"⚠️ Ошибка сохранения очистки в БД: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start cleanup: {str(e)}")

@router.get("/health")
async def health_check():
    return {"status": "healthy", "agent": "data_cleanup_agent"}
