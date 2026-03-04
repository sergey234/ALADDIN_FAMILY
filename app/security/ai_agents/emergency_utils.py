#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Утилиты для системы экстренного реагирования
Применение DRY принципа - импорт всех специализированных утилит
"""

import re
import hashlib
import uuid
import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

# Импортируем все специализированные утилиты
try:
    from .emergency_validators import (
        PhoneValidator, EmailValidator, CoordinateValidator,
        EmergencyTypeValidator, SeverityValidator, DescriptionValidator
    )
except ImportError:
    # Fallback определения
    class PhoneValidator:
        @staticmethod
        def validate(phone: str) -> bool:
            return bool(re.match(r'^\+?[1-9]\d{1,14}$', phone))
    
    class EmailValidator:
        @staticmethod
        def validate(email: str) -> bool:
            return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))

try:
    from ..microservices.emergency_formatters import (
        EmergencyMessageFormatter, EmergencyDataFormatter
    )
except ImportError:
    # Fallback определения
    class EmergencyMessageFormatter:
        @staticmethod
        def format_emergency_message(data: Dict[str, Any]) -> str:
            return f"Emergency: {data.get('type', 'Unknown')} - {data.get('description', 'No description')}"

try:
    from .emergency_location_utils import (
        LocationDistanceCalculator, LocationServiceFinder,
        LocationValidator, LocationClusterAnalyzer
    )
except ImportError:
    # Fallback определения
    class LocationDistanceCalculator:
        @staticmethod
        def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
            # Простая формула расстояния
            return ((lat2 - lat1) ** 2 + (lon2 - lon1) ** 2) ** 0.5

try:
    from .emergency_time_utils import (
        TimePeriodAnalyzer, ResponseTimeCalculator,
        TimeBasedRiskAnalyzer, EmergencyTimeUtils
    )
except ImportError:
    # Fallback определения
    class EmergencyTimeUtils:
        @staticmethod
        def get_current_timestamp() -> str:
            return datetime.datetime.now().isoformat()

try:
    from .emergency_security_utils import (
        InputSanitizer, SecurityValidator, DataHasher,
        SecurityLogger, EmergencySecurityUtils
    )
except ImportError:
    # Fallback определения
    class InputSanitizer:
        @staticmethod
        def sanitize_input(text: str) -> str:
            return re.sub(r'[<>"\']', '', text)

try:
    from .emergency_id_generator import EmergencyIDGenerator
except ImportError:
    # Fallback определения
    class EmergencyIDGenerator:
        @staticmethod
        def generate_id() -> str:
            return str(uuid.uuid4())

@dataclass
class EmergencyUtils:
    """
    Основной класс утилит для экстренного реагирования
    """
    
    def __init__(self):
        self.phone_validator = PhoneValidator()
        self.email_validator = EmailValidator()
        self.location_calculator = LocationDistanceCalculator()
        self.time_utils = EmergencyTimeUtils()
        self.input_sanitizer = InputSanitizer()
        self.id_generator = EmergencyIDGenerator()
    
    def validate_emergency_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Валидация данных экстренной ситуации"""
        result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Проверка обязательных полей
        required_fields = ["type", "description", "location"]
        for field in required_fields:
            if field not in data or not data[field]:
                result["is_valid"] = False
                result["errors"].append(f"Missing required field: {field}")
        
        # Валидация телефона
        if "phone" in data and data["phone"]:
            if not self.phone_validator.validate(data["phone"]):
                result["warnings"].append("Invalid phone number format")
        
        # Валидация email
        if "email" in data and data["email"]:
            if not self.email_validator.validate(data["email"]):
                result["warnings"].append("Invalid email format")
        
        # Валидация координат
        if "coordinates" in data and data["coordinates"]:
            coords = data["coordinates"]
            if not isinstance(coords, dict) or "lat" not in coords or "lon" not in coords:
                result["warnings"].append("Invalid coordinates format")
        
        return result
    
    def sanitize_emergency_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Очистка данных экстренной ситуации"""
        sanitized = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = self.input_sanitizer.sanitize_input(value)
            else:
                sanitized[key] = value
        
        return sanitized
    
    def calculate_response_priority(self, data: Dict[str, Any]) -> int:
        """Расчет приоритета ответа (1-10, где 10 - максимальный)"""
        priority = 5  # Базовый приоритет
        
        # Увеличиваем приоритет на основе ключевых слов
        text = str(data).lower()
        if any(word in text for word in ["fire", "explosion", "bomb"]):
            priority += 3
        elif any(word in text for word in ["medical", "heart", "stroke"]):
            priority += 2
        elif any(word in text for word in ["police", "crime", "robbery"]):
            priority += 2
        
        # Увеличиваем приоритет на основе серьезности
        if "critical" in text or "urgent" in text:
            priority += 2
        elif "high" in text or "serious" in text:
            priority += 1
        
        return min(priority, 10)
    
    def generate_emergency_id(self) -> str:
        """Генерация уникального ID для экстренной ситуации"""
        return self.id_generator.generate_id()
    
    def format_emergency_message(self, data: Dict[str, Any]) -> str:
        """Форматирование сообщения об экстренной ситуации"""
        return EmergencyMessageFormatter.format_emergency_message(data)
    
    def calculate_distance_to_services(self, emergency_location: Dict[str, float], 
                                      service_locations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Расчет расстояния до служб экстренного реагирования"""
        results = []
        
        for service in service_locations:
            if "coordinates" in service and "lat" in service["coordinates"] and "lon" in service["coordinates"]:
                distance = self.location_calculator.calculate_distance(
                    emergency_location["lat"], emergency_location["lon"],
                    service["coordinates"]["lat"], service["coordinates"]["lon"]
                )
                
                results.append({
                    "service": service.get("name", "Unknown"),
                    "distance": distance,
                    "coordinates": service["coordinates"]
                })
        
        # Сортируем по расстоянию
        results.sort(key=lambda x: x["distance"])
        return results
    
    def get_emergency_timestamp(self) -> str:
        """Получение временной метки экстренной ситуации"""
        return self.time_utils.get_current_timestamp()
    
    def create_emergency_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Создание сводки экстренной ситуации"""
        return {
            "id": self.generate_emergency_id(),
            "timestamp": self.get_emergency_timestamp(),
            "type": data.get("type", "Unknown"),
            "severity": data.get("severity", "Medium"),
            "priority": self.calculate_response_priority(data),
            "location": data.get("location", {}),
            "description": data.get("description", ""),
            "status": "pending"
        }

class EmergencyUtilsManager:
    """
    Менеджер утилит экстренного реагирования
    """
    
    def __init__(self):
        self.utils = EmergencyUtils()
        self.emergency_log: List[Dict[str, Any]] = []
    
    def process_emergency(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка экстренной ситуации"""
        # Валидация данных
        validation_result = self.utils.validate_emergency_data(data)
        
        if not validation_result["is_valid"]:
            return {
                "success": False,
                "error": "Invalid emergency data",
                "details": validation_result["errors"]
            }
        
        # Очистка данных
        sanitized_data = self.utils.sanitize_emergency_data(data)
        
        # Создание сводки
        summary = self.utils.create_emergency_summary(sanitized_data)
        
        # Добавление в лог
        self.emergency_log.append(summary)
        
        return {
            "success": True,
            "emergency_id": summary["id"],
            "summary": summary,
            "warnings": validation_result["warnings"]
        }
    
    def get_emergency_log(self) -> List[Dict[str, Any]]:
        """Получение лога экстренных ситуаций"""
        return self.emergency_log
    
    def get_emergency_by_id(self, emergency_id: str) -> Optional[Dict[str, Any]]:
        """Получение экстренной ситуации по ID"""
        for emergency in self.emergency_log:
            if emergency["id"] == emergency_id:
                return emergency
        return None

# Создаем алиасы для обратной совместимости
EmergencyValidator = type('EmergencyValidator', (), {
    'validate_phone_number': staticmethod(PhoneValidator.validate),
    'validate_email': staticmethod(EmailValidator.validate),
    'validate_coordinates': staticmethod(CoordinateValidator.validate),
    'validate_emergency_type': staticmethod(EmergencyTypeValidator.validate),
    'validate_severity': staticmethod(SeverityValidator.validate),
    'validate_emergency_description': staticmethod(DescriptionValidator.validate)
})

EmergencyMessageFormatter = EmergencyMessageFormatter
EmergencyLocationUtils = type('EmergencyLocationUtils', (), {
    'calculate_distance': staticmethod(LocationDistanceCalculator.calculate_distance),
    'is_location_in_radius': staticmethod(LocationDistanceCalculator.is_location_in_radius),
    'find_nearest_services': staticmethod(LocationServiceFinder.find_nearest_services),
    'validate_location_accuracy': staticmethod(LocationValidator.validate_location_accuracy)
})

EmergencyTimeUtils = EmergencyTimeUtils
EmergencySecurityUtils = EmergencySecurityUtils
EmergencyIDGenerator = EmergencyIDGenerator
EmergencyDataExporter = EmergencyDataFormatter

# Экспортируем все основные классы
__all__ = [
    'EmergencyValidator',
    'EmergencyMessageFormatter', 
    'EmergencyLocationUtils',
    'EmergencyTimeUtils',
    'EmergencySecurityUtils',
    'EmergencyIDGenerator',
    'EmergencyDataExporter',
    'PhoneValidator',
    'EmailValidator',
    'CoordinateValidator',
    'EmergencyTypeValidator',
    'SeverityValidator',
    'DescriptionValidator',
    'LocationDistanceCalculator',
    'LocationServiceFinder',
    'LocationValidator',
    'LocationClusterAnalyzer',
    'TimePeriodAnalyzer',
    'ResponseTimeCalculator',
    'TimeBasedRiskAnalyzer',
    'InputSanitizer',
    'SecurityValidator',
    'DataHasher',
    'SecurityLogger'
]