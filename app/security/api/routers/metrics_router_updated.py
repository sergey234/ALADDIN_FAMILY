# -*- coding: utf-8 -*-
"""
Metrics Upload API Router - ОБНОВЛЕННАЯ ВЕРСИЯ С PostgreSQL
-------------------------
FastAPI endpoint для загрузки метрик из iOS приложения.
ОБНОВЛЕНО: Сохранение метрик в PostgreSQL

Использование:
    В main.py добавить:
    from security.api.routers.metrics_router import router as metrics_router
    app.include_router(metrics_router)

Дата создания: 12 февраля 2026
Обновлено: 14 марта 2026
Версия: 2.0.0
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
import json
import uuid

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

# ✅ ИМПОРТЫ ДЛЯ PostgreSQL
from app.database.database import get_db
from app.auth.auth import get_current_user

logger = logging.getLogger(__name__)

# Создаем FastAPI Router
router = APIRouter(prefix="/api/metrics", tags=["Metrics"])


# =============================================================================
# Pydantic модели для запросов и ответов
# =============================================================================

class MetricData(BaseModel):
    """Данные одной метрики"""
    type: str = Field(..., description="Тип метрики (event, api_call, alert, system_health, component_status)")
    timestamp: float = Field(..., description="Временная метка метрики")
    action: Optional[str] = Field(None, description="Действие пользователя (для event)")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Параметры метрики")
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
    status: Optional[str] = Field(None, description="Статус здоровья (для system_health)")
    uptime: Optional[float] = Field(None, description="Время работы (для system_health)")
    activeComponents: Optional[int] = Field(None, description="Активные компоненты (для system_health)")
    totalComponents: Optional[int] = Field(None, description="Всего компонентов (для system_health)")
    issues: Optional[List[str]] = Field(None, description="Проблемы (для system_health)")


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


# ✅ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ РАБОТЫ С БД

def save_metric_to_db(
    db: Session,
    user_id: Optional[str],
    device_id: str,
    app_version: str,
    platform: str,
    metric: MetricData
) -> str:
    """Сохранить метрику в БД"""
    try:
        metric_id = str(uuid.uuid4())
        
        # Преобразуем данные в JSON для JSONB
        parameters_json = json.dumps(metric.parameters) if metric.parameters else None
        context_json = json.dumps(metric.context) if metric.context else None
        issues_json = json.dumps(metric.issues) if metric.issues else None
        
        # Преобразуем timestamp из float в datetime
        metric_timestamp = datetime.fromtimestamp(metric.timestamp)
        
        query = text("""
            INSERT INTO analytics_metrics (
                id, user_id, device_id, app_version, platform,
                metric_type, timestamp, action, parameters, endpoint, method,
                response_time, status_code, success, error_type, error_message, context,
                alert_id, alert_type, severity, message, status, uptime,
                active_components, total_components, issues, created_at
            ) VALUES (
                :id, :user_id::uuid, :device_id, :app_version, :platform,
                :metric_type, :timestamp, :action, :parameters::jsonb, :endpoint, :method,
                :response_time, :status_code, :success, :error_type, :error_message, :context::jsonb,
                :alert_id, :alert_type, :severity, :message, :status, :uptime,
                :active_components, :total_components, :issues::text[], :created_at
            )
        """)
        
        db.execute(query, {
            "id": metric_id,
            "user_id": user_id,
            "device_id": device_id,
            "app_version": app_version,
            "platform": platform,
            "metric_type": metric.type,
            "timestamp": metric_timestamp,
            "action": metric.action,
            "parameters": parameters_json,
            "endpoint": metric.endpoint,
            "method": metric.method,
            "response_time": metric.responseTime,
            "status_code": metric.statusCode,
            "success": metric.success,
            "error_type": metric.errorType,
            "error_message": metric.errorMessage,
            "context": context_json,
            "alert_id": metric.alertId,
            "alert_type": metric.alertType,
            "severity": metric.severity,
            "message": metric.message,
            "status": metric.status,
            "uptime": metric.uptime,
            "active_components": metric.activeComponents,
            "total_components": metric.totalComponents,
            "issues": issues_json,
            "created_at": datetime.utcnow()
        })
        
        db.commit()
        return metric_id
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error saving metric to DB: {str(e)}")
        raise


# =============================================================================
# Endpoints
# =============================================================================

@router.post("/upload", response_model=MetricsUploadResponse)
async def upload_metrics(
    request: MetricsUploadRequest,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
) -> MetricsUploadResponse:
    """
    Загрузка метрик из мобильного приложения (ОБНОВЛЕНО: сохраняет в БД).
    
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
        # Получаем user_id из токена (может быть None для системных метрик)
        user_id = None
        if current_user:
            user_id = str(current_user.get("id") or current_user.get("sub") or current_user.get("user_id"))
        
        # Логируем получение метрик
        logger.info(
            f"📊 Получены метрики от устройства {request.deviceId}: {len(request.metrics)} метрик"
        )
        
        # ✅ СОХРАНЯЕМ МЕТРИКИ В БД
        saved_count = 0
        errors = []
        
        for metric in request.metrics:
            try:
                save_metric_to_db(
                    db=db,
                    user_id=user_id,
                    device_id=request.deviceId,
                    app_version=request.appVersion,
                    platform=request.platform,
                    metric=metric
                )
                saved_count += 1
            except Exception as e:
                logger.error(f"❌ Ошибка сохранения метрики: {str(e)}")
                errors.append(str(e))
                # Продолжаем обработку остальных метрик
        
        if saved_count == 0 and len(errors) > 0:
            # Если не удалось сохранить ни одной метрики
            raise HTTPException(
                status_code=500,
                detail=f"Не удалось сохранить метрики: {', '.join(errors[:3])}"
            )
        
        logger.info(
            f"✅ Метрики успешно обработаны: {saved_count}/{len(request.metrics)} метрик от {request.deviceId}"
        )
        
        message = f"Успешно загружено {saved_count} метрик"
        if len(errors) > 0:
            message += f" ({len(errors)} ошибок)"
        
        return MetricsUploadResponse(
            success=True,
            uploadedCount=saved_count,
            message=message,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка при обработке метрик: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка обработки метрик: {str(e)}"
        )
