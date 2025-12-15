# -*- coding: utf-8 -*-
"""
Roadside Assistance API Router
---------------------------------
FastAPI endpoints для интеграции Roadside Assistance Agent с мобильным приложением iOS.

Использование:
    В main.py добавить:
    from security.api.routers.roadside_assistance_router import router as roadside_assistance_router
    app.include_router(roadside_assistance_router)

Дата создания: 14 декабря 2025
Версия: 1.0.0
"""

from datetime import datetime
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field, validator
import logging
import os

# Импорты агента
try:
    from security.ai_agents.roadside_assistance_agent import (
        RoadsideAssistanceAgent,
        ProblemType,
        AssistanceStatus,
        Location,
        VehicleInfo,
        AssistanceRequest
    )
except ImportError:
    RoadsideAssistanceAgent = None
    ProblemType = None
    AssistanceStatus = None
    Location = None
    VehicleInfo = None
    AssistanceRequest = None

logger = logging.getLogger(__name__)

# Создаем FastAPI Router
router = APIRouter(prefix="/api/roadside-assistance", tags=["Roadside Assistance"])

# Глобальный экземпляр агента (инициализируется при первом запросе)
_agent_instance: Optional[RoadsideAssistanceAgent] = None


def get_agent() -> RoadsideAssistanceAgent:
    """
    Получение экземпляра агента (singleton)

    Returns:
        Экземпляр RoadsideAssistanceAgent

    Raises:
        HTTPException: Если агент не может быть инициализирован
    """
    global _agent_instance
    if _agent_instance is None:
        if RoadsideAssistanceAgent is None:
            raise HTTPException(
                status_code=503,
                detail="Roadside Assistance Agent не доступен. Проверьте установку модуля."
            )

        config = {
            "default_partner": os.getenv("ROADSIDE_DEFAULT_PARTNER", "manual"),
            "status_check_interval_seconds": int(os.getenv("ROADSIDE_STATUS_CHECK_INTERVAL", "30")),
            "max_wait_time_minutes": int(os.getenv("ROADSIDE_MAX_WAIT_TIME", "120")),
            "enable_auto_status_check": os.getenv("ROADSIDE_AUTO_STATUS_CHECK", "true").lower() == "true",
            "rosgosstrah_api_key": os.getenv("ROADSIDE_ROSGOSSTRAH_API_KEY", ""),
            "alfastrahovanie_api_key": os.getenv("ROADSIDE_ALFASTRAHOVANIE_API_KEY", ""),
            "ingosstrah_api_key": os.getenv("ROADSIDE_INGOSSTRAH_API_KEY", ""),
            "reso_api_key": os.getenv("ROADSIDE_RESO_API_KEY", "")
        }

        try:
            _agent_instance = RoadsideAssistanceAgent(config)
            logger.info("✅ Roadside Assistance Agent инициализирован")
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации агента: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Ошибка инициализации агента: {str(e)}"
            )

    return _agent_instance


# Pydantic модели для запросов и ответов

class LocationRequest(BaseModel):
    """Запрос с местоположением"""
    latitude: float = Field(..., description="Широта", ge=-90, le=90)
    longitude: float = Field(..., description="Долгота", ge=-180, le=180)
    address: Optional[str] = Field(None, description="Адрес (опционально)")
    accuracy: Optional[float] = Field(None, description="Точность в метрах (опционально)")

    def to_location(self) -> Location:
        """Преобразование в Location объект"""
        return Location(
            latitude=self.latitude,
            longitude=self.longitude,
            address=self.address,
            accuracy=self.accuracy
        )


class VehicleInfoRequest(BaseModel):
    """Информация о транспортном средстве"""
    make: Optional[str] = Field(None, description="Марка (Toyota, BMW и т.д.)")
    model: Optional[str] = Field(None, description="Модель (Camry, X5 и т.д.)")
    year: Optional[int] = Field(None, description="Год выпуска", ge=1900, le=2100)
    color: Optional[str] = Field(None, description="Цвет")
    license_plate: Optional[str] = Field(None, description="Номерной знак")
    vin: Optional[str] = Field(None, description="VIN номер")

    def to_vehicle_info(self) -> VehicleInfo:
        """Преобразование в VehicleInfo объект"""
        return VehicleInfo(
            make=self.make,
            model=self.model,
            year=self.year,
            color=self.color,
            license_plate=self.license_plate,
            vin=self.vin
        )


class CallAssistanceRequest(BaseModel):
    """Запрос на вызов помощи"""
    user_id: str = Field(..., description="ID пользователя")
    problem_type: str = Field(..., description="Тип проблемы (towing, jump_start, tire_change, lockout, fuel_delivery и т.д.)")
    location: LocationRequest = Field(..., description="Местоположение")
    description: Optional[str] = Field(None, description="Описание проблемы")
    vehicle_info: Optional[VehicleInfoRequest] = Field(None, description="Информация о транспортном средстве")
    partner: Optional[str] = Field(None, description="Партнер (rosgosstrah, alfastrahovanie и т.д., опционально)")

    @validator('problem_type')
    def validate_problem_type(cls, v):
        """Проверка типа проблемы"""
        valid_types = [pt.value for pt in ProblemType] if ProblemType else []
        if v not in valid_types:
            raise ValueError(f"Недопустимый тип проблемы. Допустимые: {', '.join(valid_types)}")
        return v


class AssistanceStatusResponse(BaseModel):
    """Ответ со статусом помощи"""
    status: str = Field(..., description="Статус помощи")
    request_id: str = Field(..., description="ID запроса")
    user_id: str = Field(..., description="ID пользователя")
    partner: str = Field(..., description="Партнер")
    problem_type: str = Field(..., description="Тип проблемы")
    location: Dict[str, Any] = Field(..., description="Местоположение")
    description: Optional[str] = Field(None, description="Описание проблемы")
    vehicle_info: Optional[Dict[str, Any]] = Field(None, description="Информация о транспортном средстве")
    service_provider: Optional[Dict[str, Any]] = Field(None, description="Информация о службе помощи")
    partner_request_id: Optional[str] = Field(None, description="ID запроса у партнера")
    created_at: Optional[str] = Field(None, description="Время создания")
    updated_at: Optional[str] = Field(None, description="Время последнего обновления")
    completed_at: Optional[str] = Field(None, description="Время завершения")
    estimated_arrival: Optional[str] = Field(None, description="Ожидаемое время прибытия")
    cost: Optional[float] = Field(None, description="Стоимость услуги")
    notes: Optional[str] = Field(None, description="Дополнительные заметки")


class CallAssistanceResponse(BaseModel):
    """Ответ на вызов помощи"""
    status: str = Field(..., description="Статус ответа")
    request: AssistanceStatusResponse = Field(..., description="Информация о запросе")
    message: Optional[str] = Field(None, description="Сообщение")


class CancelRequestResponse(BaseModel):
    """Ответ на отмену запроса"""
    status: str = Field(..., description="Статус ответа")
    cancelled: bool = Field(..., description="Запрос отменен")
    message: Optional[str] = Field(None, description="Сообщение")


# API Endpoints

@router.post("/call", summary="Вызов помощи на дороге", response_model=CallAssistanceResponse)
async def call_assistance(
    request: CallAssistanceRequest,
    agent: RoadsideAssistanceAgent = Depends(get_agent)
) -> CallAssistanceResponse:
    """
    Вызов помощи на дороге

    Типы проблем:
    - towing - Буксировка
    - jump_start - Запуск двигателя
    - tire_change - Замена колеса
    - lockout - Открытие замка
    - fuel_delivery - Доставка топлива
    - battery_replacement - Замена аккумулятора
    - windshield_repair - Ремонт лобового стекла
    - other - Другое
    """
    try:
        # Преобразование типов
        problem_type = ProblemType(request.problem_type)
        location = request.location.to_location()
        vehicle_info = request.vehicle_info.to_vehicle_info() if request.vehicle_info else None

        # Вызов помощи
        assistance_request = agent.call_assistance(
            user_id=request.user_id,
            problem_type=problem_type,
            location=location,
            description=request.description,
            vehicle_info=vehicle_info,
            partner=request.partner
        )

        return CallAssistanceResponse(
            status="success",
            request=AssistanceStatusResponse(**assistance_request.to_dict()),
            message="Запрос на помощь создан успешно"
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка при вызове помощи: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{request_id}", summary="Получить статус помощи", response_model=AssistanceStatusResponse)
async def get_status(
    request_id: str,
    agent: RoadsideAssistanceAgent = Depends(get_agent)
) -> AssistanceStatusResponse:
    """
    Получить статус запроса на помощь

    Статусы:
    - pending - Запрос создан, ожидает диспетчера
    - dispatched - Диспетчер назначил службу помощи
    - on_way - Служба помощи в пути
    - arrived - Служба помощи прибыла на место
    - in_progress - Помощь оказывается
    - completed - Помощь оказана, проблема решена
    - cancelled - Запрос отменен
    - failed - Ошибка при оказании помощи
    """
    try:
        assistance_request = agent.get_status(request_id)

        if not assistance_request:
            raise HTTPException(status_code=404, detail=f"Запрос {request_id} не найден")

        return AssistanceStatusResponse(**assistance_request.to_dict())

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении статуса: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cancel/{request_id}", summary="Отменить запрос на помощь", response_model=CancelRequestResponse)
async def cancel_request(
    request_id: str,
    agent: RoadsideAssistanceAgent = Depends(get_agent)
) -> CancelRequestResponse:
    """
    Отменить запрос на помощь

    Запрос можно отменить только если он еще не завершен или не отменен ранее.
    """
    try:
        cancelled = agent.cancel_request(request_id)

        if not cancelled:
            return CancelRequestResponse(
                status="error",
                cancelled=False,
                message="Не удалось отменить запрос. Возможно, он уже завершен или отменен."
            )

        return CancelRequestResponse(
            status="success",
            cancelled=True,
            message="Запрос успешно отменен"
        )

    except Exception as e:
        logger.error(f"Ошибка при отмене запроса: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", summary="Получить историю запросов", response_model=List[AssistanceStatusResponse])
async def get_history(
    user_id: str = Query(..., description="ID пользователя"),
    limit: int = Query(10, ge=1, le=100, description="Максимальное количество запросов"),
    agent: RoadsideAssistanceAgent = Depends(get_agent)
) -> List[AssistanceStatusResponse]:
    """
    Получить историю запросов на помощь пользователя

    Возвращает список последних запросов пользователя, отсортированных по дате создания (новые первыми).
    """
    try:
        history = agent.get_history(user_id, limit)

        return [AssistanceStatusResponse(**req.to_dict()) for req in history]

    except Exception as e:
        logger.error(f"Ошибка при получении истории: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", summary="Проверка работоспособности агента")
async def health_check(
    agent: RoadsideAssistanceAgent = Depends(get_agent)
) -> Dict[str, Any]:
    """
    Проверка работоспособности Roadside Assistance Agent

    Returns:
        Статус агента
    """
    return {
        "status": "healthy",
        "agent": "RoadsideAssistanceAgent",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }
