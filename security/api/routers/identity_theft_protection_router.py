# -*- coding: utf-8 -*-
"""
Identity Theft Protection API Router
-------------------------------------
FastAPI endpoints для интеграции Identity Theft Protection с мобильным приложением iOS.

Использование:
    В main.py добавить:
    from security.api.routers.identity_theft_protection_router import router as identity_theft_router
    app.include_router(identity_theft_router)

Дата создания: 10 декабря 2025
Версия: 1.0.0
"""

from datetime import datetime
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, HTTPException, Query, Header, Depends
from pydantic import BaseModel, Field, validator
import logging
import os
import re

# Импорты агента
try:
    from security.ai_agents.russian_identity_theft_protection_agent import (
        RussianIdentityTheftProtectionAgent,
        FraudRecord,
        IdentityTheftAlert
    )
except ImportError:
    RussianIdentityTheftProtectionAgent = None
    FraudRecord = None
    IdentityTheftAlert = None

logger = logging.getLogger(__name__)

# Создаем FastAPI Router
router = APIRouter(prefix="/api/identity-theft", tags=["Identity Theft Protection"])

# Глобальный экземпляр агента (инициализируется при первом запросе)
_agent_instance: Optional[RussianIdentityTheftProtectionAgent] = None


def get_agent() -> RussianIdentityTheftProtectionAgent:
    """
    Получение экземпляра агента (singleton)

    Returns:
        Экземпляр RussianIdentityTheftProtectionAgent

    Raises:
        HTTPException: Если агент не может быть инициализирован
    """
    global _agent_instance
    if _agent_instance is None:
        if RussianIdentityTheftProtectionAgent is None:
            raise HTTPException(
                status_code=503,
                detail="Identity Theft Protection Agent не доступен. Проверьте установку модуля."
            )

        config = {
            "nbki_api_key": os.getenv("NBKI_API_KEY", ""),
            "okb_api_key": os.getenv("OKB_API_KEY", ""),
            "fraud_database_path": os.getenv("FRAUD_DATABASE_PATH", ""),
            "cache_ttl": int(os.getenv("IDENTITY_THEFT_CACHE_TTL", "86400")),
            "monitoring_interval": int(os.getenv("IDENTITY_THEFT_MONITORING_INTERVAL", "24"))
        }

        try:
            _agent_instance = RussianIdentityTheftProtectionAgent(config)
            logger.info("✅ Identity Theft Protection Agent инициализирован")
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации агента: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Ошибка инициализации агента: {str(e)}"
            )

    return _agent_instance


# ═══════════════════════════════════════════════════════════════
# Pydantic модели для запросов и ответов
# ═══════════════════════════════════════════════════════════════


class MonitorSNILSRequest(BaseModel):
    """Запрос на мониторинг СНИЛС"""
    user_id: str = Field(..., description="ID пользователя")
    snils: str = Field(..., description="СНИЛС для мониторинга")

    @validator('snils')
    def validate_snils(cls, v):
        """Валидация формата СНИЛС"""
        # Удаляем дефисы и пробелы
        snils_clean = re.sub(r'[-\s]', '', v)
        # Проверяем что это 11 цифр
        if not re.match(r'^\d{11}$', snils_clean):
            raise ValueError('СНИЛС должен содержать 11 цифр')
        return snils_clean


class MonitorSNILSResponse(BaseModel):
    """Ответ на мониторинг СНИЛС"""
    success: bool = Field(..., description="Успешность операции")
    snils_hash: Optional[str] = Field(None, description="Хеш СНИЛС")
    fraud_matches: int = Field(0, description="Количество совпадений в базе мошенников")
    suspicious_activity: bool = Field(False, description="Обнаружена подозрительная активность")
    risk_score: float = Field(0.0, ge=0.0, le=1.0, description="Оценка риска (0.0 - 1.0)")
    severity: str = Field("low", description="Уровень серьезности (low/medium/high/critical)")
    checked_at: str = Field(..., description="Время проверки (ISO 8601)")
    error: Optional[str] = Field(None, description="Описание ошибки, если есть")
    message: Optional[str] = Field(None, description="Дополнительное сообщение")


class MonitorCreditRequest(BaseModel):
    """Запрос на мониторинг кредитного отчета"""
    user_id: str = Field(..., description="ID пользователя")


class MonitorCreditResponse(BaseModel):
    """Ответ на мониторинг кредитного отчета"""
    success: bool = Field(..., description="Успешность операции")
    nbki_available: bool = Field(False, description="Доступен ли НБКИ API")
    okb_available: bool = Field(False, description="Доступен ли ОКБ API")
    suspicious_changes: int = Field(0, description="Количество подозрительных изменений")
    risk_score: float = Field(0.0, ge=0.0, le=1.0, description="Оценка риска (0.0 - 1.0)")
    severity: str = Field("low", description="Уровень серьезности")
    checked_at: str = Field(..., description="Время проверки (ISO 8601)")
    error: Optional[str] = Field(None, description="Описание ошибки, если есть")
    message: Optional[str] = Field(None, description="Дополнительное сообщение")


class CheckFraudDatabaseRequest(BaseModel):
    """Запрос на проверку в базе мошенников"""
    snils: Optional[str] = Field(None, description="СНИЛС для проверки")
    passport_series: Optional[str] = Field(None, description="Серия паспорта")
    passport_number: Optional[str] = Field(None, description="Номер паспорта")

    @validator('snils')
    def validate_snils(cls, v):
        """Валидация формата СНИЛС (если указан)"""
        if v is None:
            return v
        snils_clean = re.sub(r'[-\s]', '', v)
        if not re.match(r'^\d{11}$', snils_clean):
            raise ValueError('СНИЛС должен содержать 11 цифр')
        return snils_clean

    @validator('passport_series')
    def validate_passport_series(cls, v):
        """Валидация серии паспорта (если указана)"""
        if v is None:
            return v
        series_clean = re.sub(r'[\s]', '', v)
        if not re.match(r'^\d{4}$', series_clean):
            raise ValueError('Серия паспорта должна содержать 4 цифры')
        return series_clean

    @validator('passport_number')
    def validate_passport_number(cls, v):
        """Валидация номера паспорта (если указан)"""
        if v is None:
            return v
        number_clean = re.sub(r'[\s]', '', v)
        if not re.match(r'^\d{6}$', number_clean):
            raise ValueError('Номер паспорта должен содержать 6 цифр')
        return number_clean


class FraudRecordResponse(BaseModel):
    """Ответ с записью из базы мошенников"""
    id: str = Field(..., description="ID записи")
    snils: Optional[str] = Field(None, description="СНИЛС (захеширован)")
    passport_series: Optional[str] = Field(None, description="Серия паспорта (захеширована)")
    passport_number: Optional[str] = Field(None, description="Номер паспорта (захеширован)")
    fraud_type: str = Field(..., description="Тип мошенничества")
    detected_at: str = Field(..., description="Дата обнаружения")
    description: Optional[str] = Field(None, description="Описание")


class CheckFraudDatabaseResponse(BaseModel):
    """Ответ на проверку в базе мошенников"""
    success: bool = Field(..., description="Успешность операции")
    matches: List[FraudRecordResponse] = Field(default_factory=list, description="Найденные записи")
    matches_count: int = Field(0, description="Количество совпадений")
    checked_at: str = Field(..., description="Время проверки (ISO 8601)")
    error: Optional[str] = Field(None, description="Описание ошибки, если есть")


class DetectIdentityTheftRequest(BaseModel):
    """Запрос на обнаружение кражи личности"""
    user_id: str = Field(..., description="ID пользователя")
    snils: Optional[str] = Field(None, description="СНИЛС для проверки")

    @validator('snils')
    def validate_snils(cls, v):
        """Валидация формата СНИЛС (если указан)"""
        if v is None:
            return v
        snils_clean = re.sub(r'[-\s]', '', v)
        if not re.match(r'^\d{11}$', snils_clean):
            raise ValueError('СНИЛС должен содержать 11 цифр')
        return snils_clean


class DetectIdentityTheftResponse(BaseModel):
    """Ответ на обнаружение кражи личности"""
    success: bool = Field(..., description="Успешность операции")
    user_id: str = Field(..., description="ID пользователя")
    risk_score: float = Field(0.0, ge=0.0, le=1.0, description="Общая оценка риска")
    severity: str = Field("low", description="Уровень серьезности")
    alert_type: str = Field("", description="Тип алерта")
    indicators: Dict[str, bool] = Field(default_factory=dict, description="Индикаторы риска")
    recommendations: List[str] = Field(default_factory=list, description="Рекомендации")
    detected_at: str = Field(..., description="Время обнаружения (ISO 8601)")
    error: Optional[str] = Field(None, description="Описание ошибки, если есть")


class AlertResponse(BaseModel):
    """Ответ с алертом"""
    id: str = Field(..., description="ID алерта")
    user_id: str = Field(..., description="ID пользователя")
    alert_type: str = Field(..., description="Тип алерта")
    severity: str = Field(..., description="Уровень серьезности")
    risk_score: float = Field(..., description="Оценка риска")
    detected_at: str = Field(..., description="Время обнаружения")
    description: str = Field(..., description="Описание")
    recommendations: List[str] = Field(default_factory=list, description="Рекомендации")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Дополнительные данные")


class AlertsResponse(BaseModel):
    """Ответ со списком алертов"""
    success: bool = Field(..., description="Успешность операции")
    alerts: List[AlertResponse] = Field(default_factory=list, description="Список алертов")
    total_alerts: int = Field(0, description="Общее количество алертов")
    error: Optional[str] = Field(None, description="Описание ошибки, если есть")


class MonitoringStatusResponse(BaseModel):
    """Ответ со статусом мониторинга"""
    success: bool = Field(..., description="Успешность операции")
    is_monitoring: bool = Field(False, description="Активен ли мониторинг")
    user_id: Optional[str] = Field(None, description="ID пользователя")
    snils_monitored: bool = Field(False, description="Мониторится ли СНИЛС")
    credit_monitored: bool = Field(False, description="Мониторится ли кредитный отчет")
    last_check: Optional[str] = Field(None, description="Время последней проверки")
    status: Optional[Dict[str, Any]] = Field(None, description="Детальный статус")
    error: Optional[str] = Field(None, description="Описание ошибки, если есть")


class StopMonitoringRequest(BaseModel):
    """Запрос на остановку мониторинга"""
    user_id: str = Field(..., description="ID пользователя")


class StopMonitoringResponse(BaseModel):
    """Ответ на остановку мониторинга"""
    success: bool = Field(..., description="Успешность операции")
    user_id: str = Field(..., description="ID пользователя")
    error: Optional[str] = Field(None, description="Описание ошибки, если есть")


class ConsentRequest(BaseModel):
    """Запрос на предоставление согласия"""
    user_id: str = Field(..., description="ID пользователя")
    consent_types: Dict[str, bool] = Field(..., description="Типы согласий: snils, passport, credit")
    duration_days: int = Field(365, ge=1, le=3650, description="Длительность согласия в днях (1-3650)")

    @validator('consent_types')
    def validate_consent_types(cls, v):
        """Валидация типов согласий"""
        allowed_types = {"snils", "passport", "credit"}
        for key in v.keys():
            if key not in allowed_types:
                raise ValueError(f'Неизвестный тип согласия: {key}. Разрешены: {allowed_types}')
        return v


class ConsentResponse(BaseModel):
    """Ответ на предоставление согласия"""
    success: bool = Field(..., description="Успешность операции")
    user_id: str = Field(..., description="ID пользователя")
    consents: Dict[str, bool] = Field(..., description="Предоставленные согласия")
    expires_at: str = Field(..., description="Дата истечения (ISO 8601)")
    error: Optional[str] = Field(None, description="Описание ошибки, если есть")


class RevokeConsentRequest(BaseModel):
    """Запрос на отзыв согласия"""
    user_id: str = Field(..., description="ID пользователя")


class RevokeConsentResponse(BaseModel):
    """Ответ на отзыв согласия"""
    success: bool = Field(..., description="Успешность операции")
    user_id: str = Field(..., description="ID пользователя")
    message: str = Field(..., description="Сообщение об успешном отзыве")
    error: Optional[str] = Field(None, description="Описание ошибки, если есть")


class CreditFreezeInstructionsResponse(BaseModel):
    """Ответ с инструкциями по заморозке кредитной истории"""
    success: bool = Field(..., description="Успешность операции")
    title: Optional[str] = Field(None, description="Заголовок инструкции")
    description: Optional[str] = Field(None, description="Описание")
    instructions: Optional[List[Dict[str, Any]]] = Field(None, description="Пошаговые инструкции")
    benefits: Optional[List[str]] = Field(None, description="Преимущества заморозки")
    important_notes: Optional[List[str]] = Field(None, description="Важные заметки")
    error: Optional[str] = Field(None, description="Описание ошибки, если есть")
    message: Optional[str] = Field(None, description="Дополнительное сообщение")


class HealthResponse(BaseModel):
    """Ответ health check"""
    status: str = Field(..., description="Статус сервиса")
    agent_loaded: bool = Field(..., description="Загружен ли агент")
    timestamp: str = Field(..., description="Время проверки (ISO 8601)")


# ═══════════════════════════════════════════════════════════════
# Вспомогательные функции
# ═══════════════════════════════════════════════════════════════


def get_auth_token(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """
    Извлечение токена из заголовка Authorization

    TODO: Реализовать полноценную проверку JWT токена
    """
    if not authorization:
        return None

    # Формат: "Bearer <token>"
    if authorization.startswith("Bearer "):
        return authorization[7:]

    return authorization


def require_auth_dependency(authorization: Optional[str] = Header(None)) -> str:
    """
    Dependency для проверки авторизации

    Raises:
        HTTPException: Если токен отсутствует
    """
    token = get_auth_token(authorization)
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Authorization required. Provide Bearer token in Authorization header."
        )
    # TODO: Проверка валидности токена
    return token


# ═══════════════════════════════════════════════════════════════
# API Endpoints
# ═══════════════════════════════════════════════════════════════


@router.get("/health", response_model=HealthResponse, summary="Health check")
async def health_check(
    agent: RussianIdentityTheftProtectionAgent = Depends(get_agent)
):
    """
    Health check endpoint (без авторизации)

    Проверяет доступность сервиса и статус агента.
    """
    try:
        return HealthResponse(
            status="healthy",
            agent_loaded=True,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Ошибка health check: {e}")
        return HealthResponse(
            status="unhealthy",
            agent_loaded=False,
            timestamp=datetime.now().isoformat()
        )


@router.post("/monitor-snils", response_model=MonitorSNILSResponse, summary="Мониторинг СНИЛС")
async def monitor_snils(
    request: MonitorSNILSRequest,
    token: str = Depends(require_auth_dependency),
    agent: RussianIdentityTheftProtectionAgent = Depends(get_agent)
):
    """
    Запуск мониторинга СНИЛС на подозрительную активность.

    Требует авторизации и согласия пользователя на обработку СНИЛС (152-ФЗ).
    """
    try:
        result = agent.monitor_snils(
            snils=request.snils,
            user_id=request.user_id
        )

        if not result.get("success", False):
            # Возвращаем ошибку без исключения (например, нет согласия)
            return MonitorSNILSResponse(
                success=False,
                error=result.get("error", "unknown_error"),
                message=result.get("message", ""),
                checked_at=datetime.now().isoformat()
            )

        return MonitorSNILSResponse(
            success=True,
            snils_hash=result.get("snils_hash"),
            fraud_matches=result.get("fraud_matches", 0),
            suspicious_activity=result.get("suspicious_activity", False),
            risk_score=result.get("risk_score", 0.0),
            severity=result.get("severity", "low"),
            checked_at=result.get("checked_at", datetime.now().isoformat())
        )
    except Exception as e:
        logger.error(f"Ошибка мониторинга СНИЛС для {request.user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при мониторинге СНИЛС: {str(e)}"
        )


@router.post("/monitor-credit", response_model=MonitorCreditResponse, summary="Мониторинг кредитного отчета")
async def monitor_credit(
    request: MonitorCreditRequest,
    token: str = Depends(require_auth_dependency),
    agent: RussianIdentityTheftProtectionAgent = Depends(get_agent)
):
    """
    Запуск мониторинга кредитного отчета через НБКИ и ОКБ.

    Требует авторизации и согласия пользователя на доступ к кредитному отчету (152-ФЗ).
    """
    try:
        result = agent.monitor_credit_report(user_id=request.user_id)

        if not result.get("success", False):
            return MonitorCreditResponse(
                success=False,
                error=result.get("error", "unknown_error"),
                message=result.get("message", ""),
                checked_at=datetime.now().isoformat()
            )

        return MonitorCreditResponse(
            success=True,
            nbki_available=result.get("nbki_available", False),
            okb_available=result.get("okb_available", False),
            suspicious_changes=result.get("suspicious_changes", 0),
            risk_score=result.get("risk_score", 0.0),
            severity=result.get("severity", "low"),
            checked_at=result.get("checked_at", datetime.now().isoformat())
        )
    except Exception as e:
        logger.error(f"Ошибка мониторинга кредитного отчета для {request.user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при мониторинге кредитного отчета: {str(e)}"
        )


@router.post("/check", response_model=CheckFraudDatabaseResponse, summary="Проверка в базе мошенников")
async def check_fraud_database(
    request: CheckFraudDatabaseRequest,
    token: str = Depends(require_auth_dependency),
    agent: RussianIdentityTheftProtectionAgent = Depends(get_agent)
):
    """
    Проверка данных (СНИЛС или паспорт) в базе мошенников.

    Требует авторизации.
    """
    try:
        if not request.snils and not (request.passport_series and request.passport_number):
            raise HTTPException(
                status_code=400,
                detail="Необходимо указать СНИЛС или паспортные данные (серия и номер)"
            )

        fraud_records = agent.check_fraud_database(
            snils=request.snils,
            passport_series=request.passport_series,
            passport_number=request.passport_number
        )

        # Конвертация FraudRecord в Pydantic модели
        matches = [
            FraudRecordResponse(
                id=record.id,
                snils=record.snils,
                passport_series=record.passport_series,
                passport_number=record.passport_number,
                fraud_type=record.fraud_type,
                detected_at=record.detected_at,
                description=record.description
            )
            for record in fraud_records
        ]

        return CheckFraudDatabaseResponse(
            success=True,
            matches=matches,
            matches_count=len(matches),
            checked_at=datetime.now().isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка проверки в базе мошенников: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при проверке в базе мошенников: {str(e)}"
        )


@router.post("/detect", response_model=DetectIdentityTheftResponse, summary="Обнаружение кражи личности")
async def detect_identity_theft(
    request: DetectIdentityTheftRequest,
    token: str = Depends(require_auth_dependency),
    agent: RussianIdentityTheftProtectionAgent = Depends(get_agent)
):
    """
    Комплексное обнаружение кражи личности на основе всех доступных данных.

    Требует авторизации.
    """
    try:
        result = agent.detect_identity_theft(
            user_id=request.user_id,
            snils=request.snils
        )

        if not result.get("success", False):
            return DetectIdentityTheftResponse(
                success=False,
                user_id=request.user_id,
                error=result.get("error", "unknown_error"),
                detected_at=datetime.now().isoformat()
            )

        return DetectIdentityTheftResponse(
            success=True,
            user_id=result.get("user_id", request.user_id),
            risk_score=result.get("risk_score", 0.0),
            severity=result.get("severity", "low"),
            alert_type=result.get("alert_type", ""),
            indicators=result.get("indicators", {}),
            recommendations=result.get("recommendations", []),
            detected_at=result.get("detected_at", datetime.now().isoformat())
        )
    except Exception as e:
        logger.error(f"Ошибка обнаружения кражи личности для {request.user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обнаружении кражи личности: {str(e)}"
        )


@router.get("/alerts", response_model=AlertsResponse, summary="Получение алертов")
async def get_alerts(
    user_id: Optional[str] = Query(None, description="ID пользователя (опционально)"),
    token: str = Depends(require_auth_dependency),
    agent: RussianIdentityTheftProtectionAgent = Depends(get_agent)
):
    """
    Получение списка алертов о краже личности для пользователя или всех алертов.

    Требует авторизации.
    """
    try:
        alerts_data = agent.get_alerts(user_id)

        alerts = [
            AlertResponse(
                id=alert.get("id", ""),
                user_id=alert.get("user_id", ""),
                alert_type=alert.get("alert_type", ""),
                severity=alert.get("severity", "low"),
                risk_score=alert.get("risk_score", 0.0),
                detected_at=alert.get("detected_at", ""),
                description=alert.get("description", ""),
                recommendations=alert.get("recommendations", []),
                metadata=alert.get("metadata")
            )
            for alert in alerts_data
        ]

        return AlertsResponse(
            success=True,
            alerts=alerts,
            total_alerts=len(alerts)
        )
    except Exception as e:
        logger.error(f"Ошибка получения алертов для {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении алертов: {str(e)}"
        )


@router.get("/status", response_model=MonitoringStatusResponse, summary="Статус мониторинга")
async def get_monitoring_status(
    user_id: Optional[str] = Query(None, description="ID пользователя (опционально)"),
    token: str = Depends(require_auth_dependency),
    agent: RussianIdentityTheftProtectionAgent = Depends(get_agent)
):
    """
    Получение статуса мониторинга для пользователя.

    Требует авторизации.
    """
    try:
        result = agent.get_monitoring_status(user_id)

        status = result.get("status", {})

        return MonitoringStatusResponse(
            success=True,
            is_monitoring=result.get("is_monitoring", False),
            user_id=result.get("user_id", user_id),
            snils_monitored=status.get("snils_monitored", False) if status else False,
            credit_monitored=status.get("credit_monitored", False) if status else False,
            last_check=status.get("last_check") if status else None,
            status=status
        )
    except Exception as e:
        logger.error(f"Ошибка получения статуса для {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении статуса: {str(e)}"
        )


@router.post("/stop-monitoring", response_model=StopMonitoringResponse, summary="Остановка мониторинга")
async def stop_monitoring(
    request: StopMonitoringRequest,
    token: str = Depends(require_auth_dependency),
    agent: RussianIdentityTheftProtectionAgent = Depends(get_agent)
):
    """
    Остановка автоматического мониторинга для пользователя.

    Требует авторизации.
    """
    try:
        result = agent.stop_monitoring(request.user_id)

        return StopMonitoringResponse(
            success=result.get("success", True),
            user_id=result.get("user_id", request.user_id)
        )
    except Exception as e:
        logger.error(f"Ошибка остановки мониторинга для {request.user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при остановке мониторинга: {str(e)}"
        )


@router.post("/consent", response_model=ConsentResponse, summary="Предоставление согласия")
async def give_consent(
    request: ConsentRequest,
    token: str = Depends(require_auth_dependency),
    agent: RussianIdentityTheftProtectionAgent = Depends(get_agent)
):
    """
    Предоставление согласия на обработку персональных данных (152-ФЗ).

    Требует авторизации.
    """
    try:
        result = agent.give_consent(
            user_id=request.user_id,
            consent_types=request.consent_types,
            duration_days=request.duration_days
        )

        if not result.get("success", False):
            return ConsentResponse(
                success=False,
                user_id=request.user_id,
                consents={},
                expires_at="",
                error=result.get("error", "unknown_error")
            )

        return ConsentResponse(
            success=True,
            user_id=result.get("user_id", request.user_id),
            consents=result.get("consents", {}),
            expires_at=result.get("expires_at", "")
        )
    except Exception as e:
        logger.error(f"Ошибка предоставления согласия для {request.user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при предоставлении согласия: {str(e)}"
        )


@router.post("/revoke-consent", response_model=RevokeConsentResponse, summary="Отзыв согласия")
async def revoke_consent(
    request: RevokeConsentRequest,
    token: str = Depends(require_auth_dependency),
    agent: RussianIdentityTheftProtectionAgent = Depends(get_agent)
):
    """
    Отзыв согласия на обработку персональных данных (152-ФЗ).

    Требует авторизации.
    """
    try:
        result = agent.revoke_consent(request.user_id)

        if not result.get("success", False):
            return RevokeConsentResponse(
                success=False,
                user_id=request.user_id,
                message="",
                error=result.get("error", "unknown_error")
            )

        return RevokeConsentResponse(
            success=True,
            user_id=result.get("user_id", request.user_id),
            message=result.get("message", "Согласие успешно отозвано")
        )
    except Exception as e:
        logger.error(f"Ошибка отзыва согласия для {request.user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при отзыве согласия: {str(e)}"
        )


@router.get("/credit-freeze-instructions", response_model=CreditFreezeInstructionsResponse, summary="Инструкции по заморозке кредитной истории")
async def get_credit_freeze_instructions(
    user_id: str = Query(..., description="ID пользователя"),
    token: str = Depends(require_auth_dependency),
    agent: RussianIdentityTheftProtectionAgent = Depends(get_agent)
):
    """
    Получение инструкций по заморозке кредитной истории в НБКИ и ОКБ.

    Требует авторизации и согласия на доступ к информации о кредитной истории.

    ВАЖНО: Метод НЕ замораживает кредитную историю автоматически,
    а только предоставляет пошаговые инструкции для пользователя.
    """
    try:
        result = agent.get_credit_freeze_instructions(user_id)

        if not result.get("success", False):
            return CreditFreezeInstructionsResponse(
                success=False,
                error=result.get("error", "unknown_error"),
                message=result.get("message", "")
            )

        return CreditFreezeInstructionsResponse(
            success=True,
            title=result.get("title"),
            description=result.get("description"),
            instructions=result.get("instructions"),
            benefits=result.get("benefits"),
            important_notes=result.get("important_notes")
        )
    except Exception as e:
        logger.error(f"Ошибка получения инструкций по кредитному замку для {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении инструкций: {str(e)}"
        )
