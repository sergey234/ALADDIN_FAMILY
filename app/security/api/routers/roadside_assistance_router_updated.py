# -*- coding: utf-8 -*-
"""
Roadside Assistance API Router - ОБНОВЛЕННАЯ ВЕРСИЯ С PostgreSQL
---------------------------------
FastAPI endpoints для интеграции Roadside Assistance Agent с мобильным приложением iOS.
ОБНОВЛЕНО: Сохранение запросов в PostgreSQL

Использование:
    В main.py добавить:
    from security.api.routers.roadside_assistance_router import router as roadside_assistance_router
    app.include_router(roadside_assistance_router)

Дата создания: 14 декабря 2025
Обновлено: 14 марта 2026
Версия: 2.0.0
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
import uuid

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging
import os

# ✅ ИМПОРТЫ ДЛЯ PostgreSQL
from app.database.database import get_db
from app.auth.auth import get_current_user

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


# ✅ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ РАБОТЫ С БД

def save_request_to_db(
    db: Session,
    user_id: str,
    request_id: str,
    problem_type: str,
    latitude: float,
    longitude: float,
    address: Optional[str] = None,
    description: Optional[str] = None,
    vehicle_make: Optional[str] = None,
    vehicle_model: Optional[str] = None,
    vehicle_year: Optional[int] = None,
    vehicle_color: Optional[str] = None,
    license_plate: Optional[str] = None,
    vin: Optional[str] = None,
    partner: Optional[str] = None,
    status: str = "pending"
) -> str:
    """Сохранить запрос помощи на дороге в БД"""
    try:
        db_request_id = str(uuid.uuid4())
        
        query = text("""
            INSERT INTO roadside_assistance_requests (
                id, user_id, request_id, problem_type, latitude, longitude, address,
                description, vehicle_make, vehicle_model, vehicle_year, vehicle_color,
                license_plate, vin, partner, status, created_at, updated_at
            ) VALUES (
                :id, :user_id::uuid, :request_id, :problem_type, :latitude, :longitude, :address,
                :description, :vehicle_make, :vehicle_model, :vehicle_year, :vehicle_color,
                :license_plate, :vin, :partner, :status, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            )
        """)
        
        db.execute(query, {
            "id": db_request_id,
            "user_id": user_id,
            "request_id": request_id,
            "problem_type": problem_type,
            "latitude": float(latitude),
            "longitude": float(longitude),
            "address": address,
            "description": description,
            "vehicle_make": vehicle_make,
            "vehicle_model": vehicle_model,
            "vehicle_year": vehicle_year,
            "vehicle_color": vehicle_color,
            "license_plate": license_plate,
            "vin": vin,
            "partner": partner,
            "status": status
        })
        
        db.commit()
        logger.info(f"✅ Roadside assistance request saved to DB: {request_id}")
        return db_request_id
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error saving roadside assistance request to DB: {str(e)}")
        raise

def update_request_status_in_db(
    db: Session,
    request_id: str,
    status: str,
    estimated_arrival: Optional[datetime] = None,
    actual_arrival: Optional[datetime] = None,
    completed_at: Optional[datetime] = None
) -> bool:
    """Обновить статус запроса в БД"""
    try:
        query_params = {"request_id": request_id, "status": status}
        
        if estimated_arrival:
            query_params["estimated_arrival"] = estimated_arrival
        if actual_arrival:
            query_params["actual_arrival"] = actual_arrival
        if completed_at:
            query_params["completed_at"] = completed_at
        
        query = text("""
            UPDATE roadside_assistance_requests 
            SET status = :status,
                estimated_arrival = :estimated_arrival,
                actual_arrival = :actual_arrival,
                completed_at = :completed_at,
                updated_at = CURRENT_TIMESTAMP
            WHERE request_id = :request_id
        """)
        
        db.execute(query, query_params)
        db.commit()
        logger.info(f"✅ Roadside assistance request status updated: {request_id} -> {status}")
        return True
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error updating roadside assistance request status: {str(e)}")
        return False

def get_request_from_db(db: Session, request_id: str) -> Optional[Dict]:
    """Получить запрос из БД"""
    try:
        query = text("""
            SELECT * FROM roadside_assistance_requests 
            WHERE request_id = :request_id
        """)
        
        result = db.execute(query, {"request_id": request_id})
        row = result.fetchone()
        
        if row:
            return {
                "id": str(row[0]),
                "user_id": str(row[1]),
                "request_id": row[2],
                "problem_type": row[3],
                "latitude": float(row[4]),
                "longitude": float(row[5]),
                "address": row[6],
                "description": row[7],
                "vehicle_make": row[8],
                "vehicle_model": row[9],
                "vehicle_year": row[10],
                "vehicle_color": row[11],
                "license_plate": row[12],
                "vin": row[13],
                "partner": row[14],
                "status": row[15],
                "estimated_arrival": row[16],
                "actual_arrival": row[17],
                "completed_at": row[18],
                "created_at": row[19],
                "updated_at": row[20]
            }
        return None
        
    except Exception as e:
        logger.error(f"❌ Error getting roadside assistance request from DB: {str(e)}")
        return None

def get_user_requests_from_db(db: Session, user_id: str, limit: int = 10) -> List[Dict]:
    """Получить историю запросов пользователя из БД"""
    try:
        query = text("""
            SELECT * FROM roadside_assistance_requests 
            WHERE user_id = :user_id::uuid
            ORDER BY created_at DESC
            LIMIT :limit
        """)
        
        result = db.execute(query, {"user_id": user_id, "limit": limit})
        rows = result.fetchall()
        
        requests = []
        for row in rows:
            requests.append({
                "id": str(row[0]),
                "user_id": str(row[1]),
                "request_id": row[2],
                "problem_type": row[3],
                "latitude": float(row[4]),
                "longitude": float(row[5]),
                "address": row[6],
                "description": row[7],
                "vehicle_make": row[8],
                "vehicle_model": row[9],
                "vehicle_year": row[10],
                "vehicle_color": row[11],
                "license_plate": row[12],
                "vin": row[13],
                "partner": row[14],
                "status": row[15],
                "estimated_arrival": row[16],
                "actual_arrival": row[17],
                "completed_at": row[18],
                "created_at": row[19],
                "updated_at": row[20]
            })
        
        return requests
        
    except Exception as e:
        logger.error(f"❌ Error getting user requests from DB: {str(e)}")
        return []


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


# ✅ ОБНОВЛЕННЫЕ API Endpoints

@router.post("/call", summary="Вызов помощи на дороге", response_model=CallAssistanceResponse)
async def call_assistance(
    request: CallAssistanceRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    agent: RoadsideAssistanceAgent = Depends(get_agent)
) -> CallAssistanceResponse:
    """
    Вызов помощи на дороге (ОБНОВЛЕНО: сохраняет в БД)

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
        user_id = str(current_user["id"])
        
        # Преобразование типов
        problem_type = ProblemType(request.problem_type)
        location = request.location.to_location()
        vehicle_info = request.vehicle_info.to_vehicle_info() if request.vehicle_info else None

        # Вызов помощи через агента
        assistance_request = agent.call_assistance(
            user_id=user_id,
            problem_type=problem_type,
            location=location,
            description=request.description,
            vehicle_info=vehicle_info,
            partner=request.partner
        )
        
        # ✅ СОХРАНЯЕМ ЗАПРОС В БД
        save_request_to_db(
            db=db,
            user_id=user_id,
            request_id=assistance_request.request_id,
            problem_type=request.problem_type,
            latitude=location.latitude,
            longitude=location.longitude,
            address=location.address,
            description=request.description,
            vehicle_make=vehicle_info.make if vehicle_info else None,
            vehicle_model=vehicle_info.model if vehicle_info else None,
            vehicle_year=vehicle_info.year if vehicle_info else None,
            vehicle_color=vehicle_info.color if vehicle_info else None,
            license_plate=vehicle_info.license_plate if vehicle_info else None,
            vin=vehicle_info.vin if vehicle_info else None,
            partner=request.partner,
            status=assistance_request.status.value if hasattr(assistance_request.status, 'value') else str(assistance_request.status)
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
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    agent: RoadsideAssistanceAgent = Depends(get_agent)
) -> AssistanceStatusResponse:
    """
    Получить статус запроса на помощь (ОБНОВЛЕНО: использует БД как fallback)

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
        # Сначала пытаемся получить из агента
        assistance_request = agent.get_status(request_id)
        
        if not assistance_request:
            # ✅ FALLBACK: Если агент не вернул, получаем из БД
            db_request = get_request_from_db(db, request_id)
            if db_request:
                # Преобразуем данные из БД в формат ответа
                return AssistanceStatusResponse(
                    status=db_request["status"],
                    request_id=db_request["request_id"],
                    user_id=db_request["user_id"],
                    partner=db_request["partner"] or "manual",
                    problem_type=db_request["problem_type"],
                    location={
                        "latitude": db_request["latitude"],
                        "longitude": db_request["longitude"],
                        "address": db_request["address"]
                    },
                    description=db_request["description"],
                    vehicle_info={
                        "make": db_request["vehicle_make"],
                        "model": db_request["vehicle_model"],
                        "year": db_request["vehicle_year"],
                        "color": db_request["vehicle_color"],
                        "license_plate": db_request["license_plate"],
                        "vin": db_request["vin"]
                    } if db_request["vehicle_make"] else None,
                    created_at=db_request["created_at"].isoformat() if db_request["created_at"] else None,
                    updated_at=db_request["updated_at"].isoformat() if db_request["updated_at"] else None,
                    completed_at=db_request["completed_at"].isoformat() if db_request["completed_at"] else None,
                    estimated_arrival=db_request["estimated_arrival"].isoformat() if db_request["estimated_arrival"] else None
                )
            else:
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
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    agent: RoadsideAssistanceAgent = Depends(get_agent)
) -> CancelRequestResponse:
    """
    Отменить запрос на помощь (ОБНОВЛЕНО: обновляет статус в БД)

    Запрос можно отменить только если он еще не завершен или не отменен ранее.
    """
    try:
        cancelled = agent.cancel_request(request_id)
        
        # ✅ ОБНОВЛЯЕМ СТАТУС В БД
        if cancelled:
            update_request_status_in_db(db, request_id, "cancelled")

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
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100, description="Максимальное количество запросов"),
    agent: RoadsideAssistanceAgent = Depends(get_agent)
) -> List[AssistanceStatusResponse]:
    """
    Получить историю запросов на помощь пользователя (ОБНОВЛЕНО: использует БД)

    Возвращает список последних запросов пользователя, отсортированных по дате создания (новые первыми).
    """
    try:
        user_id = str(current_user["id"])
        
        # ✅ ПОЛУЧАЕМ ИСТОРИЮ ИЗ БД
        db_requests = get_user_requests_from_db(db, user_id, limit)
        
        # Преобразуем данные из БД в формат ответа
        history = []
        for db_req in db_requests:
            history.append(AssistanceStatusResponse(
                status=db_req["status"],
                request_id=db_req["request_id"],
                user_id=db_req["user_id"],
                partner=db_req["partner"] or "manual",
                problem_type=db_req["problem_type"],
                location={
                    "latitude": db_req["latitude"],
                    "longitude": db_req["longitude"],
                    "address": db_req["address"]
                },
                description=db_req["description"],
                vehicle_info={
                    "make": db_req["vehicle_make"],
                    "model": db_req["vehicle_model"],
                    "year": db_req["vehicle_year"],
                    "color": db_req["vehicle_color"],
                    "license_plate": db_req["license_plate"],
                    "vin": db_req["vin"]
                } if db_req["vehicle_make"] else None,
                created_at=db_req["created_at"].isoformat() if db_req["created_at"] else None,
                updated_at=db_req["updated_at"].isoformat() if db_req["updated_at"] else None,
                completed_at=db_req["completed_at"].isoformat() if db_req["completed_at"] else None,
                estimated_arrival=db_req["estimated_arrival"].isoformat() if db_req["estimated_arrival"] else None
            ))

        return history

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
        "agent_available": agent is not None,
        "timestamp": datetime.utcnow().isoformat()
    }
