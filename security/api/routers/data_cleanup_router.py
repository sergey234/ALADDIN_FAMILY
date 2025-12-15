# -*- coding: utf-8 -*-
"""
Personal Data Cleanup API Router
---------------------------------
FastAPI endpoints для интеграции Personal Data Cleanup Agent с мобильным приложением iOS.

Использование:
    В main.py добавить:
    from security.api.routers.data_cleanup_router import router as data_cleanup_router
    app.include_router(data_cleanup_router)

Дата создания: 13 декабря 2025
Версия: 1.0.0
"""

from datetime import datetime
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field, validator, EmailStr
import logging
import os

# Импорты агента
try:
    from security.ai_agents.personal_data_cleanup_agent import (
        PersonalDataCleanupAgent,
        UserData,
        FoundData,
        RemovalRequest,
        CleanupReport
    )
except ImportError:
    PersonalDataCleanupAgent = None
    UserData = None
    FoundData = None
    RemovalRequest = None
    CleanupReport = None

logger = logging.getLogger(__name__)

# Создаем FastAPI Router
router = APIRouter(prefix="/api/data-cleanup", tags=["Data Cleanup"])

# Глобальный экземпляр агента (инициализируется при первом запросе)
_agent_instance: Optional[PersonalDataCleanupAgent] = None


def get_agent() -> PersonalDataCleanupAgent:
    """
    Получение экземпляра агента (singleton)

    Returns:
        Экземпляр PersonalDataCleanupAgent

    Raises:
        HTTPException: Если агент не может быть инициализирован
    """
    global _agent_instance
    if _agent_instance is None:
        if PersonalDataCleanupAgent is None:
            raise HTTPException(
                status_code=503,
                detail="Personal Data Cleanup Agent не доступен. Проверьте установку модуля."
            )

        config = {
            "max_retries": int(os.getenv("DATA_CLEANUP_MAX_RETRIES", "3")),
            "retry_delay_days": int(os.getenv("DATA_CLEANUP_RETRY_DELAY_DAYS", "7")),
            "scan_timeout_seconds": int(os.getenv("DATA_CLEANUP_SCAN_TIMEOUT", "30")),
            "enable_auto_retry": os.getenv("DATA_CLEANUP_AUTO_RETRY", "true").lower() == "true"
        }

        try:
            _agent_instance = PersonalDataCleanupAgent(config)
            logger.info("✅ Personal Data Cleanup Agent инициализирован")
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации агента: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Ошибка инициализации агента: {str(e)}"
            )

    return _agent_instance


# Pydantic модели для запросов и ответов

class ScanRequest(BaseModel):
    """Запрос на сканирование брокерских сайтов"""
    user_id: str = Field(..., description="ID пользователя")
    email: Optional[EmailStr] = Field(None, description="Email для поиска")
    phone: Optional[str] = Field(None, description="Телефон для поиска")
    name: Optional[str] = Field(None, description="Имя для поиска")
    address: Optional[str] = Field(None, description="Адрес для поиска")
    date_of_birth: Optional[str] = Field(None, description="Дата рождения")

    @validator('*', pre=True)
    def validate_at_least_one_field(cls, v, values):
        """Проверка, что указан хотя бы один параметр для поиска"""
        if not any([values.get('email'), values.get('phone'), values.get('name')]):
            raise ValueError("Необходимо указать хотя бы один параметр: email, phone или name")
        return v

    class Config:
        schema_extra = {
            "example": {
                "user_id": "user123",
                "email": "user@example.com",
                "phone": "+79991234567",
                "name": "Иван Иванов",
                "address": "Москва, ул. Ленина, 1"
            }
        }


class RemoveRequest(BaseModel):
    """Запрос на удаление данных с сайтов"""
    user_id: str = Field(..., description="ID пользователя")
    sites: List[str] = Field(..., description="Список названий сайтов для удаления")
    email: Optional[EmailStr] = Field(None, description="Email")
    phone: Optional[str] = Field(None, description="Телефон")
    name: Optional[str] = Field(None, description="Имя")
    address: Optional[str] = Field(None, description="Адрес")
    date_of_birth: Optional[str] = Field(None, description="Дата рождения")

    class Config:
        schema_extra = {
            "example": {
                "user_id": "user123",
                "sites": ["Whitepages", "Spokeo", "2GIS"],
                "email": "user@example.com",
                "phone": "+79991234567",
                "name": "Иван Иванов"
            }
        }


# API Endpoints

@router.post("/scan", summary="Сканировать брокерские сайты на наличие данных")
async def scan_broker_sites(
    request: ScanRequest,
    agent: PersonalDataCleanupAgent = Depends(get_agent)
) -> Dict[str, Any]:
    """
    Сканирует брокерские сайты на наличие персональных данных пользователя

    Returns:
        Список сайтов, где найдены данные
    """
    try:
        user_data = UserData(
            email=request.email,
            phone=request.phone,
            name=request.name,
            address=request.address,
            date_of_birth=request.date_of_birth
        )

        found_data = agent.find_data_on_broker_sites(
            user_id=request.user_id,
            user_data=user_data
        )

        return {
            "status": "success",
            "user_id": request.user_id,
            "sites_found": len(found_data),
            "sites": [fd.to_dict() for fd in found_data]
        }

    except Exception as e:
        logger.error(f"Ошибка при сканировании: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/remove", summary="Отправить запросы на удаление данных")
async def remove_data_from_sites(
    request: RemoveRequest,
    agent: PersonalDataCleanupAgent = Depends(get_agent)
) -> Dict[str, Any]:
    """
    Отправляет запросы на удаление данных с указанных сайтов

    Returns:
        Список созданных запросов на удаление
    """
    try:
        user_data = UserData(
            email=request.email,
            phone=request.phone,
            name=request.name,
            address=request.address,
            date_of_birth=request.date_of_birth
        )

        removal_requests = agent.remove_data_from_broker_sites(
            user_id=request.user_id,
            sites=request.sites,
            user_data=user_data
        )

        return {
            "status": "success",
            "user_id": request.user_id,
            "requests_created": len(removal_requests),
            "requests": [req.to_dict() for req in removal_requests]
        }

    except Exception as e:
        logger.error(f"Ошибка при удалении данных: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", summary="Получить статус удаления данных")
async def get_removal_status(
    user_id: str = Query(..., description="ID пользователя"),
    request_id: Optional[str] = Query(None, description="ID конкретного запроса"),
    agent: PersonalDataCleanupAgent = Depends(get_agent)
) -> Dict[str, Any]:
    """
    Получает текущий статус запросов на удаление данных

    Returns:
        Список запросов с актуальным статусом
    """
    try:
        requests = agent.track_removal_progress(
            user_id=user_id,
            request_id=request_id
        )

        return {
            "status": "success",
            "user_id": user_id,
            "total_requests": len(requests),
            "requests": [req.to_dict() for req in requests]
        }

    except Exception as e:
        logger.error(f"Ошибка при получении статуса: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report", summary="Получить отчет о процессе очистки")
async def get_cleanup_report(
    user_id: str = Query(..., description="ID пользователя"),
    agent: PersonalDataCleanupAgent = Depends(get_agent)
) -> Dict[str, Any]:
    """
    Генерирует отчет о процессе очистки данных

    Returns:
        Отчет с статистикой
    """
    try:
        report = agent.get_cleanup_report(user_id=user_id)

        return {
            "status": "success",
            "report": report.to_dict()
        }

    except Exception as e:
        logger.error(f"Ошибка при генерации отчета: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scan-status", summary="Получить статус последнего поиска")
async def get_scan_status(
    user_id: str = Query(..., description="ID пользователя"),
    agent: PersonalDataCleanupAgent = Depends(get_agent)
) -> Dict[str, Any]:
    """
    Получает статус последнего поиска данных для пользователя

    Returns:
        Статус поиска (когда был последний поиск, когда следующий, нужно ли напоминание)
    """
    try:
        status = agent.get_scan_status(user_id=user_id)
        return {
            "status": "success",
            "scan_status": status
        }
    except Exception as e:
        logger.error(f"Ошибка при получении статуса поиска: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/preferences", summary="Получить настройки пользователя")
async def get_user_preferences(
    user_id: str = Query(..., description="ID пользователя"),
    agent: PersonalDataCleanupAgent = Depends(get_agent)
) -> Dict[str, Any]:
    """
    Получает настройки пользователя для поиска данных

    Returns:
        Настройки пользователя (автоматический поиск, интервал)
    """
    try:
        preferences = agent.get_user_preferences(user_id=user_id)
        return {
            "status": "success",
            "preferences": preferences
        }
    except Exception as e:
        logger.error(f"Ошибка при получении настроек: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class UpdatePreferencesRequest(BaseModel):
    """Запрос на обновление настроек пользователя"""
    user_id: str = Field(..., description="ID пользователя")
    enable_auto_scan: Optional[bool] = Field(None, description="Включить автоматический поиск")
    scan_interval_days: Optional[int] = Field(None, description="Интервал поиска в днях (7-365)", ge=7, le=365)

    class Config:
        schema_extra = {
            "example": {
                "user_id": "user123",
                "enable_auto_scan": True,
                "scan_interval_days": 30
            }
        }


@router.post("/preferences", summary="Обновить настройки пользователя")
async def update_user_preferences(
    request: UpdatePreferencesRequest,
    agent: PersonalDataCleanupAgent = Depends(get_agent)
) -> Dict[str, Any]:
    """
    Обновляет настройки пользователя для поиска данных

    Returns:
        Обновленные настройки
    """
    try:
        preferences = agent.set_user_preferences(
            user_id=request.user_id,
            enable_auto_scan=request.enable_auto_scan,
            scan_interval_days=request.scan_interval_days
        )
        return {
            "status": "success",
            "preferences": preferences
        }
    except Exception as e:
        logger.error(f"Ошибка при обновлении настроек: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/periodic-scan", summary="Запустить периодический поиск (если нужно)")
async def trigger_periodic_scan(
    request: ScanRequest,
    agent: PersonalDataCleanupAgent = Depends(get_agent)
) -> Dict[str, Any]:
    """
    Запускает периодический поиск данных, если прошло достаточно времени

    Returns:
        Результат поиска или сообщение что поиск не требуется
    """
    try:
        user_data = UserData(
            email=request.email,
            phone=request.phone,
            name=request.name,
            address=request.address,
            date_of_birth=request.date_of_birth
        )

        found_data = agent.check_periodic_scan(
            user_id=request.user_id,
            user_data=user_data
        )

        if found_data is None:
            scan_status = agent.get_scan_status(request.user_id)
            return {
                "status": "skipped",
                "message": "Поиск не требуется. Еще не прошло достаточно времени с последнего поиска.",
                "scan_status": scan_status
            }

        return {
            "status": "success",
            "user_id": request.user_id,
            "sites_found": len(found_data),
            "sites": [fd.to_dict() for fd in found_data]
        }

    except Exception as e:
        logger.error(f"Ошибка при периодическом поиске: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", summary="Проверка работоспособности агента")
async def health_check(
    agent: PersonalDataCleanupAgent = Depends(get_agent)
) -> Dict[str, Any]:
    """
    Проверка работоспособности Personal Data Cleanup Agent

    Returns:
        Статус агента
    """
    return {
        "status": "healthy",
        "agent": "PersonalDataCleanupAgent",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }
