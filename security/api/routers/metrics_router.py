# -*- coding: utf-8 -*-
"""
Metrics Upload API Router
-------------------------
FastAPI endpoint для загрузки метрик из iOS приложения.

Использование:
    В main.py добавить:
    from security.api.routers.metrics_router import router as metrics_router
    app.include_router(metrics_router)

Дата создания: 12 февраля 2026
Версия: 1.0.0
"""

from datetime import datetime
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

# Создаем FastAPI Router
router = APIRouter(prefix="/api/metrics", tags=["Metrics"])


# =============================================================================
# Pydantic модели для запросов и ответов
# =============================================================================

class MetricData(BaseModel):
    """Данные одной метрики"""
    type: str = Field(..., description="Тип метрики (user_action, api_call, error, alert, health)")
    timestamp: float = Field(..., description="Временная метка метрики")
    action: Optional[str] = Field(None, description="Действие пользователя (для user_action)")
    parameters: Optional[str] = Field(None, description="Параметры метрики в JSON формате")
    endpoint: Optional[str] = Field(None, description="API endpoint (для api_call)")
    method: Optional[str] = Field(None, description="HTTP метод (для api_call)")
    responseTime: Optional[float] = Field(None, description="Время ответа (для api_call)")
    statusCode: Optional[int] = Field(None, description="HTTP статус код (для api_call)")
    success: Optional[bool] = Field(None, description="Успешность запроса (для api_call)")
    errorType: Optional[str] = Field(None, description="Тип ошибки (для error)")
    errorMessage: Optional[str] = Field(None, description="Сообщение об ошибке (для error)")
    context: Optional[Dict[str, Any]] = Field(None, description="Контекст ошибки (для error)")
    alertId: Optional[str] = Field(None, description="ID алерта (для alert)")
    alertType: Optional[str] = Field(None, description="Тип алерта (для alert)")
    severity: Optional[str] = Field(None, description="Серьезность алерта (для alert)")
    message: Optional[str] = Field(None, description="Сообщение алерта (для alert)")
    status: Optional[str] = Field(None, description="Статус здоровья (для health)")
    uptime: Optional[float] = Field(None, description="Время работы (для health)")
    activeComponents: Optional[int] = Field(None, description="Активные компоненты (для health)")
    totalComponents: Optional[int] = Field(None, description="Всего компонентов (для health)")
    issues: Optional[List[str]] = Field(None, description="Проблемы (для health)")


class MetricsUploadRequest(BaseModel):
    """Запрос на загрузку метрик"""
    deviceId: str = Field(..., description="ID устройства")
    appVersion: str = Field(..., description="Версия приложения")
    platform: str = Field(..., description="Платформа (ios, android)")
    metrics: List[MetricData] = Field(..., description="Список метрик")


class MetricsUploadResponse(BaseModel):
    """Ответ на загрузку метрик"""
    success: bool = Field(..., description="Успешность загрузки")
    uploadedCount: int = Field(..., description="Количество загруженных метрик")
    message: Optional[str] = Field(None, description="Сообщение")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Временная метка обработки")


# =============================================================================
# Endpoints
# =============================================================================

@router.post("/upload", response_model=MetricsUploadResponse)
async def upload_metrics(request: MetricsUploadRequest) -> MetricsUploadResponse:
    """
    Загрузка метрик из мобильного приложения.
    
    Принимает метрики производительности, действий пользователя, ошибок и других событий
    из iOS/Android приложения для анализа и мониторинга.
    
    Args:
        request: Запрос с метриками
        
    Returns:
        MetricsUploadResponse: Результат загрузки
        
    Raises:
        HTTPException: При ошибке обработки
    """
    try:
        # Логируем получение метрик
        logger.info(
            f"📊 Получены метрики от устройства {request.deviceId}: {len(request.metrics)} метрик"
        )
        
        # В будущем здесь можно добавить:
        # 1. Сохранение метрик в БД
        # 2. Анализ метрик
        # 3. Генерация алертов при проблемах
        # 4. Агрегация метрик для дашборда
        
        # Пока просто подтверждаем получение
        uploaded_count = len(request.metrics)
        
        logger.info(
            f"✅ Метрики успешно обработаны: {uploaded_count} метрик от {request.deviceId}"
        )
        
        return MetricsUploadResponse(
            success=True,
            uploadedCount=uploaded_count,
            message=f"Успешно загружено {uploaded_count} метрик",
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"❌ Ошибка при обработке метрик: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка обработки метрик: {str(e)}"
        )
