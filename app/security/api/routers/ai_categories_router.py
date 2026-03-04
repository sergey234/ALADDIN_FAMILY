# -*- coding: utf-8 -*-
"""
AI Categories API Router
------------------------
FastAPI endpoints для интеграции AI Categories Agent с мобильным приложением iOS.
Маршруты для отчетов по категориям контента и управления доступом.
"""

from datetime import datetime, timedelta
import uuid
from typing import Dict, List, Optional, Any
from enum import Enum

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

# Создаем FastAPI Router с префиксом как в iOS AppConfig
router = APIRouter(prefix="/api/reports/ai-categories", tags=["AI Categories Reports"])

# ═══════════════════════════════════════════════════════════════
# Pydantic модели (соответствуют iOS моделям)
# ═══════════════════════════════════════════════════════════════

class ContentCategory(str, Enum):
    education = "education"
    games = "games"
    entertainment = "entertainment"
    adult = "adult"
    violence = "violence"
    other = "other"

class AICategoryReport(BaseModel):
    id: str
    childId: Optional[str] = None
    childName: Optional[str] = None
    category: ContentCategory
    sitesCount: int
    blockedCount: int

class AICategoriesStats(BaseModel):
    totalCategorized: int
    totalBlocked: int
    accuracy: float # 0-100%
    byCategory: Dict[str, int]
    blockedByCategory: Dict[str, int]

class ActionRequest(BaseModel):
    categoryId: str
    action: str # "allow" | "block"

# ═══════════════════════════════════════════════════════════════
# API Endpoints
# ═══════════════════════════════════════════════════════════════

@router.get("/stats", response_model=AICategoriesStats)
async def get_ai_stats():
    """Получить статистику категоризации AI"""
    return {
        "totalCategorized": 1250,
        "totalBlocked": 42,
        "accuracy": 99.2,
        "byCategory": {
            "education": 450,
            "games": 320,
            "entertainment": 280,
            "adult": 15,
            "violence": 5,
            "other": 180
        },
        "blockedByCategory": {
            "adult": 15,
            "violence": 5,
            "games": 12,
            "other": 10
        }
    }

@router.get("/reports", response_model=List[AICategoryReport])
async def get_ai_reports(childId: Optional[str] = None):
    """Получить отчеты по категориям для ребенка"""
    reports = []
    categories = list(ContentCategory)
    
    for i, cat in enumerate(categories):
        reports.append({
            "id": f"report_{i}",
            "childId": childId or "child_1",
            "childName": "Александр" if not childId else "Александр",
            "category": cat,
            "sitesCount": 100 + (i * 20),
            "blockedCount": 5 + i
        })
    return reports

@router.post("/allow")
async def allow_category(request: ActionRequest):
    """Разрешить доступ к категории"""
    return {"success": True, "message": f"Category {request.categoryId} allowed"}

@router.post("/block")
async def block_category(request: ActionRequest):
    """Заблокировать доступ к категории"""
    return {"success": True, "message": f"Category {request.categoryId} blocked"}

@router.get("/health")
async def health_check():
    return {"status": "healthy", "agent": "ai_categories_agent"}
