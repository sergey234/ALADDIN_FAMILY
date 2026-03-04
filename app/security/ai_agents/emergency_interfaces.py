#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Интерфейсы для системы экстренного реагирования
Применение SOLID принципов - Interface Segregation
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


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
    """Уровни серьезности экстренной ситуации"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    LIFE_THREATENING = "life"


class ResponseStatus(Enum):
    """Статусы реагирования"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class EmergencyService(Enum):
    """Экстренные службы"""

    AMBULANCE = "ambulance"
    FIRE_DEPARTMENT = "fire"
    POLICE = "police"
    SECURITY = "security"


class EmergencyInterface(ABC):
    """Базовый интерфейс для экстренного реагирования"""

    def __init__(self, service_name: str, priority: int = 1):
        """Инициализация интерфейса экстренного реагирования"""
        self.service_name = service_name
        self.priority = priority
        self.is_active = False
        self.response_time = 0.0

    @abstractmethod
    def handle_emergency(self, emergency_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Обработка экстренной ситуации"""
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Получение статуса службы"""
        pass


class EmergencyResponseInterface(ABC):
    """Интерфейс для системы реагирования на экстренные ситуации"""

    def __init__(self, response_id: str, emergency_type: EmergencyType):
        """Инициализация системы реагирования"""
        self.response_id = response_id
        self.emergency_type = emergency_type
        self.status = ResponseStatus.PENDING
        self.created_at = None

    @abstractmethod
    def process_emergency(self, data: Dict[str, Any]) -> bool:
        """Обработка экстренной ситуации"""
        pass

    @abstractmethod
    def get_response_info(self) -> Dict[str, Any]:
        """Получение информации о реагировании"""
        pass


class EmergencyNotificationInterface(ABC):
    """Интерфейс для уведомлений о экстренных ситуациях"""

    def __init__(self, notification_type: str):
        """Инициализация системы уведомлений"""
        self.notification_type = notification_type
        self.is_enabled = True
        self.recipients = []

    @abstractmethod
    def send_notification(self, message: str, recipients: List[str]) -> bool:
        """Отправка уведомления"""
        pass

    @abstractmethod
    def get_notification_status(self) -> Dict[str, Any]:
        """Получение статуса уведомлений"""
        pass
    POLICE = "police"
    EMERGENCY = "emergency"
    GAS_SERVICE = "gas"
    ELECTRIC_SERVICE = "electric"


class IEmergencyAnalyzer(ABC):
    """Интерфейс анализатора экстренных ситуаций"""

    @abstractmethod
    def analyze_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ экстренного события"""
        pass

    @abstractmethod
    def predict_risk(
        self, location: Tuple[float, float], time_of_day: int
    ) -> Dict[str, Any]:
        """Предсказание риска"""
        pass


class IEmergencyNotifier(ABC):
    """Интерфейс уведомлений"""

    @abstractmethod
    def send_notification(self, contact_id: str, message: str) -> bool:
        """Отправить уведомление"""
        pass

    @abstractmethod
    def notify_emergency_contacts(self, event_id: str) -> bool:
        """Уведомить экстренные контакты"""
        pass


class IEmergencyServiceCaller(ABC):
    """Интерфейс вызова экстренных служб"""

    @abstractmethod
    def call_service(
        self, service: EmergencyService, location: Tuple[float, float]
    ) -> bool:
        """Вызвать экстренную службу"""
        pass

    @abstractmethod
    def get_service_status(self, service: EmergencyService) -> Dict[str, Any]:
        """Получить статус службы"""
        pass


class IEmergencyDataManager(ABC):
    """Интерфейс управления данными экстренных ситуаций"""

    @abstractmethod
    def save_event(self, event_data: Dict[str, Any]) -> bool:
        """Сохранить событие"""
        pass

    @abstractmethod
    def get_events(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Получить события с фильтрами"""
        pass

    @abstractmethod
    def update_event_status(
        self, event_id: str, status: ResponseStatus
    ) -> bool:
        """Обновить статус события"""
        pass


class IEmergencyLocationTracker(ABC):
    """Интерфейс трекера местоположения"""

    @abstractmethod
    def get_current_location(self) -> Optional[Tuple[float, float]]:
        """Получить текущее местоположение"""
        pass

    @abstractmethod
    def validate_location(self, coordinates: Tuple[float, float]) -> bool:
        """Проверить валидность координат"""
        pass


class IEmergencyMLPredictor(ABC):
    """Интерфейс ML предсказаний"""

    @abstractmethod
    def train_model(self, training_data: List[Dict[str, Any]]) -> bool:
        """Обучить модель"""
        pass

    @abstractmethod
    def predict_emergency_probability(self, features: List[float]) -> float:
        """Предсказать вероятность экстренной ситуации"""
        pass

    @abstractmethod
    def detect_anomalies(
        self, events: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Обнаружить аномалии"""
        pass


class IEmergencyResourceOptimizer(ABC):
    """Интерфейс оптимизации ресурсов"""

    @abstractmethod
    def optimize_allocation(
        self,
        current_resources: Dict[str, int],
        predicted_demand: Dict[str, int],
    ) -> Dict[str, Any]:
        """Оптимизировать распределение ресурсов"""
        pass

    @abstractmethod
    def predict_demand(
        self, historical_data: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Предсказать спрос на ресурсы"""
        pass


class IEmergencyPatternAnalyzer(ABC):
    """Интерфейс анализа паттернов"""

    @abstractmethod
    def analyze_patterns(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Анализировать паттерны событий"""
        pass

    @abstractmethod
    def generate_recommendations(self, patterns: Dict[str, Any]) -> List[str]:
        """Генерировать рекомендации"""
        pass
