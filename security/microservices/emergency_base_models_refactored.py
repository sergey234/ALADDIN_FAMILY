#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Базовые модели для системы экстренного реагирования
Применение Single Responsibility принципа - только модели данных
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Tuple, Dict, Any
import asyncio
import logging

# Настройка логирования
logger = logging.getLogger(__name__)


class EmergencyType(Enum):
    """Типы экстренных ситуаций"""
    MEDICAL = "medical"           # Медицинская помощь
    FIRE = "fire"                # Пожар
    POLICE = "police"            # Полиция
    SECURITY = "security"        # Безопасность
    ACCIDENT = "accident"        # ДТП
    NATURAL_DISASTER = "natural" # Стихийное бедствие
    TECHNICAL = "technical"      # Техническая авария
    PERSONAL = "personal"        # Личная угроза


class EmergencySeverity(Enum):
    """Уровни серьезности экстренной ситуации"""
    LOW = "low"                  # Низкий
    MEDIUM = "medium"            # Средний
    HIGH = "high"                # Высокий
    CRITICAL = "critical"        # Критический
    LIFE_THREATENING = "life"    # Угрожающий жизни


class ResponseStatus(Enum):
    """Статусы реагирования"""
    PENDING = "pending"          # Ожидает
    IN_PROGRESS = "in_progress"  # В процессе
    COMPLETED = "completed"      # Завершено
    CANCELLED = "cancelled"      # Отменено
    FAILED = "failed"            # Неудачно


class EmergencyService(Enum):
    """Экстренные службы"""
    AMBULANCE = "ambulance"      # Скорая помощь
    FIRE_DEPARTMENT = "fire"     # Пожарная служба
    POLICE = "police"            # Полиция
    EMERGENCY = "emergency"      # Единая служба спасения
    GAS_SERVICE = "gas"          # Аварийная газовая служба
    ELECTRIC_SERVICE = "electric" # Аварийная электрослужба


@dataclass
class EmergencyContact:
    """Экстренный контакт"""
    contact_id: str
    name: str
    phone: str
    email: Optional[str] = None
    relationship: str = "family"
    priority: int = 1
    is_available: bool = True
    last_contacted: Optional[datetime] = None


@dataclass
class EmergencyLocation:
    """Местоположение экстренной ситуации"""
    location_id: str
    address: str
    coordinates: Tuple[float, float]
    description: str
    is_verified: bool = False
    accuracy: float = 0.0


@dataclass
class EmergencyEvent:
    """Экстренное событие"""
    event_id: str
    emergency_type: EmergencyType
    severity: EmergencySeverity
    location: EmergencyLocation
    reporter_id: str
    description: str
    timestamp: datetime
    status: ResponseStatus = ResponseStatus.PENDING
    assigned_services: List[EmergencyService] = field(default_factory=list)
    contacts_notified: List[str] = field(default_factory=list)
    resolution_notes: str = ""
    resolved_at: Optional[datetime] = None


@dataclass
class EmergencyResponse:
    """Ответ на экстренную ситуацию"""
    response_id: str
    event_id: str
    service: EmergencyService
    contact_phone: str
    estimated_arrival: Optional[datetime] = None
    actual_arrival: Optional[datetime] = None
    status: ResponseStatus = ResponseStatus.PENDING
    notes: str = ""


class EmergencyRefactoredModelManager:
    """
    Менеджер для управления рефакторенными моделями экстренного реагирования
    """
    
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.health_status = "healthy"
        self.logger = logging.getLogger(f"{__name__}.EmergencyRefactoredModelManager")
    
    async def initialize(self):
        """Инициализация менеджера"""
        try:
            # Инициализация базовых моделей
            self.models = {
                "emergency_types": [e.value for e in EmergencyType],
                "severity_levels": [e.value for e in EmergencySeverity],
                "response_statuses": [e.value for e in ResponseStatus],
                "services": [e.value for e in EmergencyService]
            }
            
            self.logger.info("Менеджер рефакторенных моделей инициализирован")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка инициализации: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Проверка здоровья менеджера"""
        try:
            return {
                "service_name": "emergency_refactored_models",
                "status": "healthy",
                "models_count": len(self.models),
                "available_models": list(self.models.keys()),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Ошибка health check: {e}")
            self.health_status = "unhealthy"
            return {
                "service_name": "emergency_refactored_models",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_emergency_types(self) -> List[str]:
        """Получение списка типов экстренных ситуаций"""
        return self.models.get("emergency_types", [])
    
    async def get_severity_levels(self) -> List[str]:
        """Получение списка уровней серьезности"""
        return self.models.get("severity_levels", [])
    
    async def get_response_statuses(self) -> List[str]:
        """Получение списка статусов ответа"""
        return self.models.get("response_statuses", [])
    
    async def get_services(self) -> List[str]:
        """Получение списка служб"""
        return self.models.get("services", [])
    
    async def validate_emergency_type(self, emergency_type: str) -> bool:
        """Валидация типа экстренной ситуации"""
        return emergency_type in self.models.get("emergency_types", [])
    
    async def validate_severity(self, severity: str) -> bool:
        """Валидация уровня серьезности"""
        return severity in self.models.get("severity_levels", [])
    
    async def get_model_info(self) -> Dict[str, Any]:
        """Получение информации о всех моделях"""
        return {
            "models": self.models,
            "health_status": self.health_status,
            "timestamp": datetime.now().isoformat()
        }
    
    async def update_models(self, new_models: Dict[str, Any]) -> Dict[str, Any]:
        """Обновление моделей"""
        try:
            self.models.update(new_models)
            self.logger.info(f"Модели обновлены: {list(new_models.keys())}")
            return {"status": "success", "updated_models": list(new_models.keys())}
        except Exception as e:
            self.logger.error(f"Ошибка обновления моделей: {e}")
            return {"status": "error", "error": str(e)}

# Экспорт всех моделей
__all__ = [
    'EmergencyType',
    'EmergencySeverity', 
    'ResponseStatus',
    'EmergencyService',
    'EmergencyContact',
    'EmergencyLocation',
    'EmergencyEvent',
    'EmergencyResponse'
]