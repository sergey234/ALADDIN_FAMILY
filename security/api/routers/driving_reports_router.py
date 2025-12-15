#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📊 Driving Reports Router
API endpoints для Driving Reports Agent

Дата создания: 12 декабря 2025
Версия: 1.0.0
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

# Импорт агента
try:
    from security.ai_agents.driving_reports_agent import (
        DrivingReportsAgent,
        DrivingViolation
    )
except ImportError:
    # Для локальной разработки
    DrivingReportsAgent = None
    DrivingViolation = None

router = APIRouter(prefix="/api/driving-reports", tags=["driving-reports"])

# Singleton агента
_agent_instance: Optional[DrivingReportsAgent] = None


def get_agent() -> DrivingReportsAgent:
    """Получить экземпляр агента (singleton)"""
    global _agent_instance
    if _agent_instance is None:
        # Конфигурация из переменных окружения
        import os
        config = {
            "speed_limit": float(os.getenv("DRIVING_SPEED_LIMIT", "60.0")),
            "hard_braking_threshold": float(os.getenv("DRIVING_HARD_BRAKING_THRESHOLD", "0.4")),
            "hard_acceleration_threshold": float(os.getenv("DRIVING_HARD_ACCELERATION_THRESHOLD", "0.4")),
            "sharp_turn_threshold": float(os.getenv("DRIVING_SHARP_TURN_THRESHOLD", "0.5")),
            "notify_parents": os.getenv("DRIVING_NOTIFY_PARENTS", "true").lower() == "true"
        }
        _agent_instance = DrivingReportsAgent(config=config)
    return _agent_instance


# MARK: - Pydantic Models

class StartMonitoringRequest(BaseModel):
    """Запрос на запуск мониторинга"""
    user_id: str = Field(..., description="ID пользователя")


class StopMonitoringRequest(BaseModel):
    """Запрос на остановку мониторинга"""
    user_id: str = Field(..., description="ID пользователя")


class DrivingEventRequest(BaseModel):
    """Запрос на запись события вождения"""
    user_id: str = Field(..., description="ID пользователя")
    event_type: str = Field(..., description="Тип события (start, stop, violation, location, speed)")
    speed: Optional[float] = Field(None, description="Скорость (км/ч)")
    location: Optional[Dict[str, Any]] = Field(None, description="Местоположение")
    violation_type: Optional[str] = Field(None, description="Тип нарушения (speeding, phone_use, hard_braking, etc.)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Дополнительные данные")


class GenerateReportRequest(BaseModel):
    """Запрос на генерацию отчета"""
    user_id: str = Field(..., description="ID пользователя")
    start_date: Optional[str] = Field(None, description="Начальная дата (ISO format)")
    end_date: Optional[str] = Field(None, description="Конечная дата (ISO format)")
    period: str = Field("week", description="Период (day, week, month)")


# MARK: - API Endpoints

@router.post("/start", summary="Запуск мониторинга вождения")
async def start_monitoring(request: StartMonitoringRequest):
    """
    Запустить мониторинг вождения для пользователя
    """
    try:
        agent = get_agent()
        result = agent.start_monitoring(request.user_id)

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop", summary="Остановка мониторинга вождения")
async def stop_monitoring(request: StopMonitoringRequest):
    """
    Остановить мониторинг вождения для пользователя
    """
    try:
        agent = get_agent()
        result = agent.stop_monitoring(request.user_id)

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/event", summary="Запись события вождения")
async def record_event(request: DrivingEventRequest):
    """
    Записать событие вождения (скорость, нарушение, местоположение)
    """
    try:
        agent = get_agent()

        # Преобразование violation_type в Enum
        violation_type_enum = None
        if request.violation_type:
            try:
                violation_type_enum = DrivingViolation(request.violation_type)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Неизвестный тип нарушения: {request.violation_type}"
                )

        result = agent.record_driving_event(
            user_id=request.user_id,
            event_type=request.event_type,
            speed=request.speed,
            location=request.location,
            violation_type=violation_type_enum,
            metadata=request.metadata
        )

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return {"status": "success", "data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate", summary="Генерация отчета о вождении")
async def generate_report(request: GenerateReportRequest):
    """
    Генерация отчета о вождении за период (день, неделя, месяц)
    """
    try:
        agent = get_agent()

        # Преобразование дат
        start_date = None
        end_date = None

        if request.start_date:
            try:
                start_date = datetime.fromisoformat(request.start_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Неверный формат start_date (используйте ISO format)")

        if request.end_date:
            try:
                end_date = datetime.fromisoformat(request.end_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Неверный формат end_date (используйте ISO format)")

        result = agent.generate_report(
            user_id=request.user_id,
            start_date=start_date,
            end_date=end_date,
            period=request.period
        )

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return {"status": "success", "data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report/{report_id}", summary="Получение отчета по ID")
async def get_report(report_id: str):
    """
    Получить отчет о вождении по ID
    """
    try:
        agent = get_agent()

        if report_id not in agent.reports:
            raise HTTPException(status_code=404, detail="Отчет не найден")

        return {"status": "success", "data": agent.reports[report_id]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/weekly/{user_id}", summary="Недельный отчет")
async def get_weekly_report(user_id: str):
    """
    Получить недельный отчет о вождении для пользователя
    """
    try:
        agent = get_agent()
        result = agent.generate_report(user_id=user_id, period="week")

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return {"status": "success", "data": result.get("report", {})}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/monthly/{user_id}", summary="Месячный отчет")
async def get_monthly_report(user_id: str):
    """
    Получить месячный отчет о вождении для пользователя
    """
    try:
        agent = get_agent()
        result = agent.generate_report(user_id=user_id, period="month")

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return {"status": "success", "data": result.get("report", {})}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/safety-score/{user_id}", summary="Оценка безопасности вождения")
async def get_safety_score(
    user_id: str,
    start_date: Optional[str] = Query(None, description="Начальная дата (ISO format)"),
    end_date: Optional[str] = Query(None, description="Конечная дата (ISO format)")
):
    """
    Получить оценку безопасности вождения для пользователя
    """
    try:
        agent = get_agent()

        # Преобразование дат
        start_date_obj = None
        end_date_obj = None

        if start_date:
            try:
                start_date_obj = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Неверный формат start_date")

        if end_date:
            try:
                end_date_obj = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Неверный формат end_date")

        result = agent.calculate_safety_score(
            user_id=user_id,
            start_date=start_date_obj,
            end_date=end_date_obj
        )

        if result is None:
            raise HTTPException(status_code=400, detail="Не удалось рассчитать оценку безопасности")

        return {"status": "success", "data": result.to_dict()}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/violations/{user_id}", summary="Статистика нарушений")
async def get_violations_statistics(
    user_id: str,
    period: str = Query("week", description="Период (day, week, month)")
):
    """
    Получить статистику нарушений для пользователя
    """
    try:
        agent = get_agent()
        result = agent.get_violations_statistics(user_id=user_id, period=period)

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return {"status": "success", "data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations/{user_id}", summary="Рекомендации по улучшению")
async def get_recommendations(user_id: str):
    """
    Получить рекомендации по улучшению безопасности вождения
    """
    try:
        agent = get_agent()
        recommendations = agent.get_recommendations(user_id=user_id)

        return {"status": "success", "data": {"user_id": user_id, "recommendations": recommendations}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", summary="Health check")
async def health_check():
    """
    Проверка работоспособности сервиса
    """
    try:
        agent = get_agent()
        return {
            "status": "healthy",
            "service": "driving_reports_agent",
            "version": "1.0.0",
            "active_monitoring": len(agent.active_monitoring),
            "total_events": sum(len(events) for events in agent.driving_events.values()),
            "total_violations": sum(len(violations) for violations in agent.violations.values())
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
