#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модели для системы экстренного реагирования
Применение DRY принципа - импорт всех специализированных моделей
"""

import json
import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

# Импортируем базовые модели
try:
    from security.microservices.emergency_base_models import (
        EmergencyType, EmergencySeverity, ResponseStatus, EmergencyService,
        EmergencyLocation, EmergencyContact, EmergencyEvent, EmergencyResponse,
        EmergencyConfiguration, EmergencyServiceConfig
    )
except ImportError:
    # Fallback определения если импорт не удался
    class EmergencyType(Enum):
        FIRE = "fire"
        MEDICAL = "medical"
        POLICE = "police"
        NATURAL_DISASTER = "natural_disaster"
        TECHNICAL = "technical"
    
    class EmergencySeverity(Enum):
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
        CRITICAL = "critical"
    
    class ResponseStatus(Enum):
        PENDING = "pending"
        IN_PROGRESS = "in_progress"
        COMPLETED = "completed"
        CANCELLED = "cancelled"

# Импортируем модели статистики
try:
    from .emergency_statistics_models import (
        EmergencyStatistics, EmergencyTrends, EmergencyPerformanceMetrics,
        EmergencyRiskMetrics, EmergencyNotificationMetrics, EmergencyServiceMetrics,
        EmergencySystemHealth, EmergencyReport, EmergencyMetricsCalculator
    )
except ImportError:
    # Fallback определения
    @dataclass
    class EmergencyStatistics:
        total_emergencies: int = 0
        resolved_emergencies: int = 0
        average_response_time: float = 0.0
        success_rate: float = 0.0

@dataclass
class EmergencyAIModel:
    """
    AI модель для анализа экстренных ситуаций
    """
    model_id: str
    model_name: str
    version: str
    accuracy: float
    last_trained: datetime.datetime
    is_active: bool = True
    
    def __init__(self, model_id: str, model_name: str, version: str = "1.0", accuracy: float = 0.95):
        self.model_id = model_id
        self.model_name = model_name
        self.version = version
        self.accuracy = accuracy
        self.last_trained = datetime.datetime.now()
        self.is_active = True
    
    def predict_emergency_type(self, data: Dict[str, Any]) -> EmergencyType:
        """Предсказание типа экстренной ситуации"""
        # Простая логика предсказания на основе данных
        if "fire" in str(data).lower():
            return EmergencyType.FIRE
        elif "medical" in str(data).lower() or "health" in str(data).lower():
            return EmergencyType.MEDICAL
        elif "police" in str(data).lower() or "crime" in str(data).lower():
            return EmergencyType.POLICE
        else:
            return EmergencyType.TECHNICAL
    
    def predict_severity(self, data: Dict[str, Any]) -> EmergencySeverity:
        """Предсказание серьезности ситуации"""
        # Простая логика на основе ключевых слов
        text = str(data).lower()
        if any(word in text for word in ["critical", "urgent", "emergency", "danger"]):
            return EmergencySeverity.CRITICAL
        elif any(word in text for word in ["high", "serious", "important"]):
            return EmergencySeverity.HIGH
        elif any(word in text for word in ["medium", "moderate"]):
            return EmergencySeverity.MEDIUM
        else:
            return EmergencySeverity.LOW
    
    def get_model_info(self) -> Dict[str, Any]:
        """Получение информации о модели"""
        return {
            "model_id": self.model_id,
            "model_name": self.model_name,
            "version": self.version,
            "accuracy": self.accuracy,
            "last_trained": self.last_trained.isoformat(),
            "is_active": self.is_active
        }
    
    def update_accuracy(self, new_accuracy: float):
        """Обновление точности модели"""
        self.accuracy = new_accuracy
        self.last_trained = datetime.datetime.now()

class EmergencyModelManager:
    """
    Менеджер для управления AI моделями экстренного реагирования
    """
    
    def __init__(self):
        self.models: Dict[str, EmergencyAIModel] = {}
        self.active_model: Optional[str] = None
    
    def add_model(self, model: EmergencyAIModel):
        """Добавление новой модели"""
        self.models[model.model_id] = model
        if not self.active_model:
            self.active_model = model.model_id
    
    def get_model(self, model_id: str) -> Optional[EmergencyAIModel]:
        """Получение модели по ID"""
        return self.models.get(model_id)
    
    def set_active_model(self, model_id: str) -> bool:
        """Установка активной модели"""
        if model_id in self.models:
            self.active_model = model_id
            return True
        return False
    
    def predict_emergency(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Предсказание экстренной ситуации с использованием активной модели"""
        if not self.active_model or self.active_model not in self.models:
            return {"error": "No active model available"}
        
        model = self.models[self.active_model]
        emergency_type = model.predict_emergency_type(data)
        severity = model.predict_severity(data)
        
        return {
            "emergency_type": emergency_type.value,
            "severity": severity.value,
            "confidence": model.accuracy,
            "model_used": model.model_id,
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    def get_all_models(self) -> List[Dict[str, Any]]:
        """Получение информации о всех моделях"""
        return [model.get_model_info() for model in self.models.values()]
    
    def get_active_model_info(self) -> Optional[Dict[str, Any]]:
        """Получение информации об активной модели"""
        if self.active_model and self.active_model in self.models:
            return self.models[self.active_model].get_model_info()
        return None

# Создаем алиасы для обратной совместимости
EmergencyLocation = EmergencyLocation
EmergencyContact = EmergencyContact
EmergencyEvent = EmergencyEvent
EmergencyResponse = EmergencyResponse
EmergencyStatistics = EmergencyStatistics
EmergencyConfiguration = EmergencyConfiguration
EmergencyServiceConfig = EmergencyServiceConfig

# Экспортируем все основные классы
__all__ = [
    # Базовые модели
    'EmergencyType',
    'EmergencySeverity', 
    'ResponseStatus',
    'EmergencyService',
    'EmergencyLocation',
    'EmergencyContact',
    'EmergencyEvent',
    'EmergencyResponse',
    'EmergencyConfiguration',
    'EmergencyServiceConfig',
    
    # Модели статистики
    'EmergencyStatistics',
    'EmergencyTrends',
    'EmergencyPerformanceMetrics',
    'EmergencyRiskMetrics',
    'EmergencyNotificationMetrics',
    'EmergencyServiceMetrics',
    'EmergencySystemHealth',
    'EmergencyReport',
    'EmergencyMetricsCalculator'
]