# -*- coding: utf-8 -*-
"""
Улучшения для валидации параметров
"""

import re
import ipaddress
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

class ParameterValidator:
    """Класс для валидации параметров"""
    
    @staticmethod
    def validate_ip_address(ip: str) -> bool:
        """
        Валидация IP адреса.
        
        Args:
            ip: IP адрес для проверки
            
        Returns:
            bool: True если IP валидный
            
        Raises:
            ValueError: Если IP невалидный
        """
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            raise ValueError(f"Невалидный IP адрес: {ip}")
    
    @staticmethod
    def validate_user_age(age: Optional[int]) -> bool:
        """
        Валидация возраста пользователя.
        
        Args:
            age: Возраст пользователя
            
        Returns:
            bool: True если возраст валидный
            
        Raises:
            ValueError: Если возраст невалидный
        """
        if age is None:
            return True
        if not isinstance(age, int):
            raise ValueError(f"Возраст должен быть числом: {age}")
        if age < 0 or age > 150:
            raise ValueError(f"Возраст должен быть от 0 до 150: {age}")
        return True
    
    @staticmethod
    def validate_event_data(event_data: Dict[str, Any]) -> bool:
        """
        Валидация данных события.
        
        Args:
            event_data: Данные события
            
        Returns:
            bool: True если данные валидные
            
        Raises:
            ValueError: Если данные невалидные
        """
        if not isinstance(event_data, dict):
            raise ValueError(f"event_data должен быть словарем: {type(event_data)}")
        
        if not event_data:
            raise ValueError("event_data не может быть пустым")
        
        # Проверяем обязательные поля
        required_fields = ['source_ip']
        for field in required_fields:
            if field not in event_data:
                raise ValueError(f"Отсутствует обязательное поле: {field}")
        
        # Валидируем IP если есть
        if 'source_ip' in event_data:
            ParameterValidator.validate_ip_address(event_data['source_ip'])
        
        return True
    
    @staticmethod
    def validate_confidence(confidence: float) -> bool:
        """
        Валидация значения уверенности.
        
        Args:
            confidence: Значение уверенности (0.0 - 1.0)
            
        Returns:
            bool: True если значение валидное
            
        Raises:
            ValueError: Если значение невалидное
        """
        if not isinstance(confidence, (int, float)):
            raise ValueError(f"Уверенность должна быть числом: {type(confidence)}")
        
        if not 0.0 <= confidence <= 1.0:
            raise ValueError(f"Уверенность должна быть от 0.0 до 1.0: {confidence}")
        
        return True

# Декоратор для автоматической валидации
def validate_parameters(**validators):
    """
    Декоратор для валидации параметров метода.
    
    Args:
        **validators: Словарь с валидаторами для каждого параметра
        
    Example:
        @validate_parameters(
            event_data=ParameterValidator.validate_event_data,
            user_age=ParameterValidator.validate_user_age
        )
        def detect_intrusion(self, event_data, user_id=None, user_age=None):
            pass
    """
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            # Получаем имена параметров функции
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(self, *args, **kwargs)
            bound_args.apply_defaults()
            
            # Валидируем каждый параметр
            for param_name, validator in validators.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    validator(value)
            
            return func(self, *args, **kwargs)
        return wrapper
    return decorator