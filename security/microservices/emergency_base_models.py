#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Базовые модели для системы экстренного реагирования
Применение Single Responsibility принципа
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Tuple, Any, Dict
import asyncio
import logging

# Настройка логирования
logger = logging.getLogger(__name__)


class EmergencyType(Enum):
    """Типы экстренных ситуаций"""
    MEDICAL = "medical"
    FIRE = "fire"
    POLICE = "police"
    SECURITY = "security"
    ACCIDENT = "accident"
    NATURAL_DISASTER = "natural"
    TECHNICAL = "technical"
    PERSONAL = "personal"


class EmergencySeverity(Enum):
    """Уровни серьезности экстренных ситуаций"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    LIFE_THREATENING = "life"


class ResponseStatus(Enum):
    """Статусы ответа на экстренную ситуацию"""
    PENDING = "pending"
    DISPATCHED = "dispatched"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CANCELLED = "cancelled"


class EmergencyService(Enum):
    """Типы служб экстренного реагирования"""
    POLICE = "police"
    FIRE = "fire"
    MEDICAL = "medical"
    SECURITY = "security"


@dataclass
class EmergencyLocation:
    """Местоположение экстренной ситуации"""
    address: str
    coordinates: Tuple[float, float]
    description: Optional[str] = None
    is_verified: bool = False
    accuracy: float = 0.0


@dataclass
class EmergencyContact:
    """Контакт для экстренного реагирования"""
    contact_id: str
    name: str
    phone: str
    email: Optional[str] = None
    relationship: str = "family"
    priority: int = 1
    is_available: bool = True


@dataclass
class EmergencyEvent:
    """Событие экстренной ситуации"""
    event_id: str
    emergency_type: EmergencyType
    severity: EmergencySeverity
    location: Dict[str, Any]
    description: str
    user_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    status: ResponseStatus = ResponseStatus.PENDING
    resolved_at: Optional[datetime] = None
    additional_info: Optional[Dict[str, Any]] = None


@dataclass
class EmergencyResponse:
    """Ответ службы экстренного реагирования"""
    response_id: str
    event_id: str
    service_type: EmergencyService
    service_name: str
    service_phone: str
    message: str
    status: str = "dispatched"
    dispatched_at: datetime = field(default_factory=datetime.now)
    arrived_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_arrival: Optional[float] = None
    additional_info: Optional[Dict[str, Any]] = None


@dataclass
class EmergencyConfiguration:
    """Конфигурация системы экстренного реагирования"""
    max_contacts: int = 10
    notification_channels: List[str] = field(default_factory=lambda: ["sms", "push"])
    auto_call_services: bool = True
    response_timeout: int = 300  # секунды
    location_accuracy_threshold: float = 100.0  # метры
    enable_ml_analysis: bool = True
    enable_risk_analysis: bool = True
    cleanup_old_data_days: int = 30


@dataclass
class EmergencyServiceConfig:
    """Конфигурация службы экстренного реагирования"""
    service_name: str
    contact_info: str
    response_time_minutes: int
    is_active: bool = True
    
    def __init__(self, service_name: str, contact_info: str, response_time_minutes: int = 15):
        self.service_name = service_name
        self.contact_info = contact_info
        self.response_time_minutes = response_time_minutes
        self.is_active = True
    
    async def health_check(self) -> Dict[str, Any]:
        """Проверка здоровья службы"""
        try:
            return {
                "service_name": self.service_name,
                "status": "healthy" if self.is_active else "inactive",
                "response_time": self.response_time_minutes,
                "contact_info": self.contact_info,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Ошибка health check для {self.service_name}: {e}")
            return {
                "service_name": self.service_name,
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def update_config(self, new_config: Dict[str, Any]) -> Dict[str, Any]:
        """Обновление конфигурации службы"""
        try:
            for key, value in new_config.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            
            logger.info(f"Конфигурация службы {self.service_name} обновлена")
            return {"status": "success", "updated_config": self.__dict__}
        except Exception as e:
            logger.error(f"Ошибка обновления конфигурации {self.service_name}: {e}")
            return {"status": "error", "error": str(e)}

class EmergencyBaseModelManager:
    """
    Менеджер для управления базовыми моделями экстренного реагирования
    """
    
    def __init__(self):
        self.services: Dict[str, EmergencyServiceConfig] = {}
        self.health_status = "healthy"
        self.logger = logging.getLogger(f"{__name__}.EmergencyBaseModelManager")
    
    async def initialize(self):
        """Инициализация менеджера"""
        try:
            # Создаем базовые службы
            default_services = [
                ("police", "112", 5),
                ("fire", "101", 3),
                ("medical", "103", 4),
                ("security", "internal", 2)
            ]
            
            for service_name, contact, response_time in default_services:
                service_config = EmergencyServiceConfig(service_name, contact, response_time)
                self.services[service_name] = service_config
            
            self.logger.info("Менеджер базовых моделей инициализирован")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка инициализации: {e}")
            return False
    
    async def add_service(self, service_config: EmergencyServiceConfig) -> Dict[str, Any]:
        """Добавление новой службы"""
        try:
            self.services[service_config.service_name] = service_config
            self.logger.info(f"Служба {service_config.service_name} добавлена")
            return {"status": "success", "service_name": service_config.service_name}
        except Exception as e:
            self.logger.error(f"Ошибка добавления службы: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_service(self, service_name: str) -> Optional[EmergencyServiceConfig]:
        """Получение службы по имени"""
        return self.services.get(service_name)
    
    async def health_check_all_services(self) -> Dict[str, Any]:
        """Проверка здоровья всех служб"""
        try:
            health_results = {}
            for service_name, service in self.services.items():
                health_results[service_name] = await service.health_check()
            
            self.health_status = "healthy"
            return {
                "status": "success",
                "services_health": health_results,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Ошибка проверки здоровья служб: {e}")
            self.health_status = "unhealthy"
            return {"status": "error", "error": str(e)}
    
    async def get_all_services(self) -> List[Dict[str, Any]]:
        """Получение информации о всех службах"""
        return [
            {
                "service_name": service.service_name,
                "contact_info": service.contact_info,
                "response_time": service.response_time_minutes,
                "is_active": service.is_active
            }
            for service in self.services.values()
        ]
    phone: str
    response_time_minutes: int
    is_available: bool = True
    coverage_area: Optional[Dict[str, Any]] = None
    specializations: List[str] = field(default_factory=list)