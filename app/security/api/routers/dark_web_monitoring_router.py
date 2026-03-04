# -*- coding: utf-8 -*-
"""
Dark Web Monitoring API Router
------------------------------
FastAPI endpoints для интеграции Dark Web Monitoring Agent с мобильным приложением iOS.
Маршруты для отчетов об утечках и управления сканированием.
"""

from datetime import datetime, timedelta
import uuid
from typing import Dict, List, Optional, Any
from enum import Enum

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

# Создаем FastAPI Router с префиксом как в iOS AppConfig
router = APIRouter(prefix="/api/reports/dark-web", tags=["Dark Web Reports"])

# ═══════════════════════════════════════════════════════════════
# Pydantic модели (соответствуют iOS моделям)
# ═══════════════════════════════════════════════════════════════

class LeakDataType(str, Enum):
    email = "email"
    password = "password"
    phone = "phone"
    bank = "bank"
    passport = "passport"
    snils = "snils"

class LeakSeverity(str, Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"

class LeakStatus(str, Enum):
    new = "new"
    in_progress = "in_progress"
    resolved = "resolved"
    ignored = "ignored"

class DarkWebLeak(BaseModel):
    id: str
    dataType: LeakDataType
    value: str
    fullValue: Optional[str] = None
    leakDate: datetime
    discoveryDate: datetime
    source: str
    severity: LeakSeverity
    status: LeakStatus
    recommendations: List[str]

class ScanStatus(str, Enum):
    completed = "completed"
    in_progress = "in_progress"
    failed = "failed"

class DarkWebScan(BaseModel):
    id: str
    scanDate: datetime
    databasesScanned: int
    newLeaksFound: int
    status: ScanStatus

class DarkWebStats(BaseModel):
    totalLeaks: int
    newLeaks: int
    resolvedLeaks: int
    criticalLeaks: int
    lastScanDate: Optional[datetime] = None

class ResolveRequest(BaseModel):
    leakId: str
    status: LeakStatus

# ═══════════════════════════════════════════════════════════════
# API Endpoints
# ═══════════════════════════════════════════════════════════════

@router.get("/stats", response_model=DarkWebStats)
async def get_dark_web_stats():
    """Получить статистику мониторинга Dark Web"""
    return {
        "totalLeaks": 24,
        "newLeaks": 5,
        "resolvedLeaks": 12,
        "criticalLeaks": 3,
        "lastScanDate": datetime.now() - timedelta(hours=12)
    }

@router.get("/leaks", response_model=List[DarkWebLeak])
async def get_leaks(status: Optional[LeakStatus] = None, limit: int = Query(50, ge=1, le=100)):
    """Получить список обнаруженных утечек"""
    leaks = [
        {
            "id": "leak_1",
            "dataType": "email",
            "value": "se***@list.ru",
            "fullValue": "sergey21-02-84@list.ru",
            "leakDate": datetime(2024, 5, 12),
            "discoveryDate": datetime.now() - timedelta(days=2),
            "source": "Adobe Data Breach 2024",
            "severity": "high",
            "status": "new",
            "recommendations": ["Смените пароль", "Включите 2FA"]
        },
        {
            "id": "leak_2",
            "dataType": "password",
            "value": "********",
            "leakDate": datetime(2023, 11, 20),
            "discoveryDate": datetime.now() - timedelta(days=10),
            "source": "Canva Leak",
            "severity": "critical",
            "status": "resolved",
            "recommendations": ["Пароль уже изменен"]
        }
    ]
    return leaks[:limit]

@router.get("/scans", response_model=List[DarkWebScan])
async def get_scans(limit: int = Query(10, ge=1, le=50)):
    """Получить историю сканирований"""
    return [
        {
            "id": str(uuid.uuid4()),
            "scanDate": datetime.now() - timedelta(days=1),
            "databasesScanned": 1250,
            "newLeaksFound": 0,
            "status": "completed"
        },
        {
            "id": str(uuid.uuid4()),
            "scanDate": datetime.now() - timedelta(days=7),
            "databasesScanned": 1100,
            "newLeaksFound": 2,
            "status": "completed"
        }
    ]

@router.post("/resolve")
async def resolve_leak(request: ResolveRequest):
    """Изменить статус утечки (решено/игнорировать)"""
    return {"success": True, "message": f"Leak {request.leakId} status updated to {request.status}"}

@router.post("/scan/start")
async def start_scan():
    """Запустить полное сканирование"""
    return {"success": True, "message": "Full scan started", "scanId": str(uuid.uuid4())}

@router.post("/scan/secure")
async def start_secure_scan():
    """Запустить защищенное сканирование"""
    return {"success": True, "message": "Secure scan started"}

@router.post("/scan/fast")
async def start_fast_scan():
    """Запустить быстрое сканирование"""
    return {"success": True, "message": "Fast scan started"}

@router.get("/health")
async def health_check():
    return {"status": "healthy", "agent": "dark_web_monitoring_agent"}
