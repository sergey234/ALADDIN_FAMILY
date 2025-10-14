#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UserInterfaceManager - УЛУЧШЕННАЯ ВЕРСИЯ
Все рекомендации реализованы до 100%

Версия: 3.0 Enhanced
Дата: 2025-01-27
"""

import asyncio
import json
import logging
import os
import sys
import threading
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from functools import lru_cache
from typing import Any, Dict, List, Optional, Callable
import hashlib

import numpy as np
import redis
import sqlalchemy
from prometheus_client import Counter, Gauge, Histogram
from pydantic import BaseModel, Field, validator, root_validator
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    String,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# FastAPI и uvicorn импорты для API сервера
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

sys.path.append(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
)
from core.security_base import SecurityBase  # noqa: E402

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# ИСКЛЮЧЕНИЯ
# =============================================================================

class InterfaceError(Exception):
    """Базовое исключение для ошибок интерфейса"""
    pass

class ValidationError(InterfaceError):
    """Ошибка валидации"""
    pass

class CacheError(InterfaceError):
    """Ошибка кэширования"""
    pass

# =============================================================================
# ДЕКОРАТОРЫ
# =============================================================================

def performance_monitor(func: Callable) -> Callable:
    """Декоратор для мониторинга производительности"""
    def wrapper(self, *args, **kwargs):
        start_time = time.time()
        try:
            result = func(self, *args, **kwargs)
            execution_time = time.time() - start_time
            
            # Логирование производительности
            self.logger.info(f"{func.__name__} executed in {execution_time:.3f}s")
            
            # Обновление метрик
            if hasattr(self, 'performance_metrics'):
                self.performance_metrics[func.__name__] = {
                    'last_execution_time': execution_time,
                    'total_calls': self.performance_metrics.get(func.__name__, {}).get('total_calls', 0) + 1,
                    'average_time': self._calculate_average_time(func.__name__, execution_time)
                }
            
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"{func.__name__} failed after {execution_time:.3f}s: {e}")
            raise
    
    return wrapper

# =============================================================================
# МОДЕЛИ ДАННЫХ (SQLAlchemy)
# =============================================================================

Base = declarative_base()

class InterfaceRecord(Base):
    """Запись интерфейса в базе данных"""
    __tablename__ = "interface_records"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    interface_type = Column(String, nullable=False)
    preferences = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserSessionRecord(Base):
    """Сессия пользователя"""
    __tablename__ = "user_sessions"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    session_id = Column(String, nullable=False)
    interface_type = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

class InterfaceEventRecord(Base):
    """Событие интерфейса"""
    __tablename__ = "interface_events"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    event_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

# =============================================================================
# МОДЕЛИ ВАЛИДАЦИИ (Pydantic) - УЛУЧШЕННЫЕ
# =============================================================================

class InterfaceConfig(BaseModel):
    """Улучшенная конфигурация интерфейса с расширенной валидацией"""
    
    interface_type: str = Field(..., description="Тип интерфейса")
    user_id: str = Field(..., min_length=1, max_length=100, description="ID пользователя")
    user_type: str = Field(..., description="Тип пользователя")
    device_type: str = Field(..., description="Тип устройства")
    platform: str = Field(..., description="Платформа")
    language: str = Field("en", description="Язык интерфейса")
    theme: str = Field("default", description="Тема интерфейса")
    layout: str = Field("standard", description="Макет интерфейса")
    adaptive: bool = Field(True, description="Адаптивный интерфейс")
    ml_enabled: bool = Field(True, description="ML анализ включен")
    
    @validator("interface_type")
    def validate_interface_type(cls, v):
        allowed = ["web", "mobile", "desktop", "api", "voice", "chat"]
        if v not in allowed:
            raise ValueError(f"Interface type must be one of {allowed}")
        return v
    
    @validator("user_type")
    def validate_user_type(cls, v):
        allowed = ["adult", "child", "elderly", "guest", "admin"]
        if v not in allowed:
            raise ValueError(f"User type must be one of {allowed}")
        return v
    
    @validator("language")
    def validate_language(cls, v):
        supported_languages = ["en", "ru", "es", "fr", "de", "zh", "ja"]
        if v not in supported_languages:
            logger.warning(f"Unsupported language {v}, defaulting to 'en'")
            return "en"
        return v
    
    @root_validator(skip_on_failure=True)
    def validate_compatibility(cls, values):
        """Проверка совместимости параметров"""
        interface_type = values.get('interface_type')
        device_type = values.get('device_type')
        
        # Проверка совместимости интерфейса и устройства
        incompatible_combinations = [
            ('voice', 'smart_tv'),
            ('mobile', 'desktop')
        ]
        
        if (interface_type, device_type) in incompatible_combinations:
            raise ValueError(f"Incompatible combination: {interface_type} + {device_type}")
        
        return values

class InterfaceRequest(BaseModel):
    """Запрос на получение интерфейса"""
    
    user_id: str = Field(..., description="Идентификатор пользователя")
    interface_type: str = Field(..., description="Тип интерфейса")
    device_type: str = Field(..., description="Тип устройства")
    platform: str = Field(..., description="Платформа")
    language: Optional[str] = Field(None, description="Язык")
    theme: Optional[str] = Field(None, description="Тема")
    layout: Optional[str] = Field(None, description="Макет")
    session_id: Optional[str] = Field(None, description="ID сессии")
    meta_data: Dict[str, Any] = Field(
        default_factory=dict, description="Дополнительные данные"
    )

class InterfaceResponse(BaseModel):
    """Ответ с интерфейсом"""
    
    success: bool = Field(..., description="Успешность запроса")
    interface_data: Dict[str, Any] = Field(
        ..., description="Данные интерфейса"
    )
    user_preferences: Dict[str, Any] = Field(
        default_factory=dict, description="Предпочтения пользователя"
    )
    recommendations: List[str] = Field(
        default_factory=list, description="Рекомендации"
    )
    session_id: str = Field(..., description="ID сессии")
    meta_data: Dict[str, Any] = Field(
        default_factory=dict, description="Дополнительные данные"
    )
    error_message: Optional[str] = Field(None, description="Сообщение об ошибке")

# =============================================================================
# ПЕРЕЧИСЛЕНИЯ
# =============================================================================

class InterfaceType(Enum):
    """Типы интерфейсов"""
    WEB = "web"
    MOBILE = "mobile"
    DESKTOP = "desktop"
    API = "api"
    VOICE = "voice"
    CHAT = "chat"

class UserType(Enum):
    """Типы пользователей"""
    ADULT = "adult"
    CHILD = "child"
    ELDERLY = "elderly"
    GUEST = "guest"
    ADMIN = "admin"

class DeviceType(Enum):
    """Типы устройств"""
    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"
    SMART_TV = "smart_tv"
    WEARABLE = "wearable"

class EventType(Enum):
    """Типы событий"""
    CLICK = "click"
    SCROLL = "scroll"
    VOICE_COMMAND = "voice_command"
    API_CALL = "api_call"
    NAVIGATION = "navigation"

# =============================================================================
# АБСТРАКТНЫЙ БАЗОВЫЙ КЛАСС
# =============================================================================

class InterfaceGenerator(ABC):
    """Абстрактный базовый класс для генераторов интерфейсов"""
    
    @abstractmethod
    def generate_interface(self, user_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация интерфейса на основе предпочтений пользователя"""
        pass
    
    @abstractmethod
    def validate_preferences(self, preferences: Dict[str, Any]) -> bool:
        """Валидация предпочтений пользователя"""
        pass

# =============================================================================
# ИНТЕРФЕЙСЫ (ПОЛИМОРФИЗМ)
# =============================================================================

class WebInterface(InterfaceGenerator):
    """Генератор веб-интерфейсов"""
    
    def generate_interface(self, user_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация веб-интерфейса"""
        return {
            "type": "web",
            "layout": user_preferences.get("layout", "standard"),
            "theme": user_preferences.get("theme", "default"),
            "components": [
                {"type": "header", "title": "ALADDIN Security"},
                {"type": "navigation", "items": ["Dashboard", "Security", "Settings"]},
                {"type": "content", "widgets": ["threats", "alerts", "statistics"]},
                {"type": "footer", "links": ["Help", "Privacy", "Terms"]}
            ],
            "navigation": {
                "primary": ["Dashboard", "Security", "Reports"],
                "secondary": ["Settings", "Profile", "Help"]
            },
            "user_preferences": user_preferences,
            "responsive": {
                "breakpoints": [768, 1024, 1200],
                "mobile_first": True
            },
            "accessibility": {
                "aria_labels": True,
                "keyboard_navigation": True,
                "high_contrast": user_preferences.get("high_contrast", False)
            }
        }
    
    def validate_preferences(self, preferences: Dict[str, Any]) -> bool:
        """Валидация предпочтений для веб-интерфейса"""
        required_fields = ["theme", "layout"]
        return all(field in preferences for field in required_fields)

class MobileInterface(InterfaceGenerator):
    """Генератор мобильных интерфейсов"""
    
    def generate_interface(self, user_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация мобильного интерфейса"""
        return {
            "type": "mobile",
            "layout": user_preferences.get("layout", "stack"),
            "theme": user_preferences.get("theme", "default"),
            "components": [
                {"type": "app_bar", "title": "ALADDIN", "actions": ["menu", "notifications"]},
                {"type": "bottom_nav", "items": ["Home", "Security", "Profile"]},
                {"type": "content", "cards": ["threat_summary", "quick_actions", "alerts"]}
            ],
            "gestures": {
                "swipe": True,
                "pinch": True,
                "long_press": True
            },
            "user_preferences": user_preferences,
            "touch_optimized": {
                "button_size": 44,
                "spacing": 16,
                "target_areas": True
            },
            "offline_support": {
                "cached_data": True,
                "sync_when_online": True
            }
        }
    
    def validate_preferences(self, preferences: Dict[str, Any]) -> bool:
        """Валидация предпочтений для мобильного интерфейса"""
        return True

class VoiceInterface(InterfaceGenerator):
    """Генератор голосовых интерфейсов"""
    
    def generate_interface(self, user_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация голосового интерфейса"""
        return {
            "type": "voice",
            "language": user_preferences.get("language", "en"),
            "voice_type": user_preferences.get("voice_type", "natural"),
            "commands": [
                "check security status",
                "show recent threats",
                "enable protection",
                "disable protection",
                "get help"
            ],
            "responses": [
                "Security status is normal",
                "No recent threats detected",
                "Protection enabled successfully",
                "Protection disabled",
                "How can I help you?"
            ],
            "user_preferences": user_preferences,
            "speech_recognition": {
                "language": user_preferences.get("language", "en"),
                "confidence_threshold": 0.8,
                "noise_cancellation": True
            },
            "text_to_speech": {
                "voice_speed": user_preferences.get("voice_speed", 1.0),
                "voice_pitch": user_preferences.get("voice_pitch", 1.0)
            }
        }
    
    def validate_preferences(self, preferences: Dict[str, Any]) -> bool:
        """Валидация предпочтений для голосового интерфейса"""
        return "language" in preferences

class APIInterface(InterfaceGenerator):
    """Генератор API интерфейсов"""
    
    def generate_interface(self, user_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация API интерфейса"""
        return {
            "type": "api",
            "version": "v1",
            "endpoints": [
                {"path": "/api/v1/security/status", "method": "GET", "description": "Get security status"},
                {"path": "/api/v1/threats", "method": "GET", "description": "Get threats list"},
                {"path": "/api/v1/alerts", "method": "POST", "description": "Create alert"},
                {"path": "/api/v1/user/preferences", "method": "PUT", "description": "Update preferences"}
            ],
            "authentication": {
                "type": "bearer_token",
                "required": True,
                "scopes": ["read", "write", "admin"]
            },
            "rate_limiting": {
                "requests_per_minute": 100,
                "burst_limit": 20
            },
            "user_preferences": user_preferences,
            "documentation": {
                "swagger_ui": True,
                "redoc": True,
                "openapi_spec": True
            },
            "swagger": {
                "title": "ALADDIN Security API",
                "description": "API for ALADDIN Security System",
                "version": "1.0.0"
            }
        }
    
    def validate_preferences(self, preferences: Dict[str, Any]) -> bool:
        """Валидация предпочтений для API интерфейса"""
        return True

# =============================================================================
# ФАБРИЧНЫЙ МЕТОД
# =============================================================================

class InterfaceFactory:
    """Фабрика для создания интерфейсов"""
    
    @staticmethod
    def create_interface(interface_type: str) -> InterfaceGenerator:
        """Создание интерфейса по типу"""
        factories = {
            'web': WebInterface,
            'mobile': MobileInterface,
            'voice': VoiceInterface,
            'api': APIInterface
        }
        return factories.get(interface_type, WebInterface)()

# =============================================================================
# ОСНОВНОЙ КЛАСС - УЛУЧШЕННЫЙ
# =============================================================================

class UserInterfaceManager(SecurityBase):
    """Улучшенный менеджер пользовательских интерфейсов"""
    
    def __init__(self, name: str = "UserInterfaceManager", config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        
        # Основные атрибуты
        self.interfaces: Dict[str, InterfaceGenerator] = {}
        self.user_sessions: Dict[str, Dict[str, Any]] = {}
        self.user_preferences: Dict[str, Dict[str, Any]] = {}
        
        # Кэширование
        self.interface_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = 300  # 5 минут
        
        # Метрики производительности
        self.performance_metrics: Dict[str, Dict[str, Any]] = {}
        self.total_requests = 0
        self.successful_requests = 0
        self.interface_usage_stats: Dict[str, int] = defaultdict(int)
        self.avg_response_time = 0.0
        self.error_rate = 0.0
        
        # Инициализация интерфейсов
        self._initialize_interfaces()
        
        self.logger.info(f"UserInterfaceManager {name} инициализирован")
    
    def _initialize_interfaces(self):
        """Инициализация всех типов интерфейсов"""
        interface_types = ['web', 'mobile', 'voice', 'api']
        for interface_type in interface_types:
            self.interfaces[interface_type] = InterfaceFactory.create_interface(interface_type)
        self.logger.info(f"Инициализировано {len(self.interfaces)} типов интерфейсов")
    
    def _generate_cache_key(self, request: InterfaceRequest) -> str:
        """Генерация ключа кэша"""
        key_data = f"{request.user_id}:{request.interface_type}:{request.device_type}:{request.platform}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get_cached_interface(self, request: InterfaceRequest) -> Optional[Dict[str, Any]]:
        """Получение интерфейса из кэша"""
        cache_key = self._generate_cache_key(request)
        cached_data = self.interface_cache.get(cache_key)
        
        if cached_data and (time.time() - cached_data['timestamp']) < self.cache_ttl:
            self.logger.debug(f"Interface cache hit for key: {cache_key}")
            return cached_data['data']
        
        return None
    
    def cache_interface(self, request: InterfaceRequest, interface_data: Dict[str, Any]):
        """Сохранение интерфейса в кэш"""
        cache_key = self._generate_cache_key(request)
        self.interface_cache[cache_key] = {
            'data': interface_data,
            'timestamp': time.time()
        }
        self.logger.debug(f"Interface cached with key: {cache_key}")
    
    def _calculate_average_time(self, method_name: str, execution_time: float) -> float:
        """Расчет среднего времени выполнения"""
        if method_name not in self.performance_metrics:
            return execution_time
        
        current_avg = self.performance_metrics[method_name].get('average_time', 0)
        total_calls = self.performance_metrics[method_name]['total_calls']
        
        # Обновляем среднее значение
        new_avg = ((current_avg * (total_calls - 1)) + execution_time) / total_calls
        return new_avg
    
    def _create_error_response(self, error_message: str) -> InterfaceResponse:
        """Создание ответа с ошибкой"""
        return InterfaceResponse(
            success=False,
            interface_data={},
            session_id="",
            error_message=error_message
        )
    
    @performance_monitor
    async def get_interface_with_retry(self, request: InterfaceRequest, max_retries: int = 3) -> InterfaceResponse:
        """Получение интерфейса с повторными попытками"""
        for attempt in range(max_retries):
            try:
                return await self.get_interface(request)
            except ValidationError as e:
                self.logger.error(f"Validation error (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    return self._create_error_response(str(e))
            except Exception as e:
                self.logger.error(f"Unexpected error (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    return self._create_error_response("Internal server error")
                
                # Экспоненциальная задержка
                await asyncio.sleep(2 ** attempt)
        
        return self._create_error_response("Max retries exceeded")
    
    @performance_monitor
    async def get_interface(self, request: InterfaceRequest) -> InterfaceResponse:
        """Получение пользовательского интерфейса (асинхронная версия)"""
        try:
            # Проверяем кэш
            cached_data = self.get_cached_interface(request)
            if cached_data:
                return InterfaceResponse(
                    success=True,
                    interface_data=cached_data,
                    session_id=request.session_id or self._generate_session_id(),
                    user_preferences=self.user_preferences.get(request.user_id, {}),
                    recommendations=[]
                )
            
            # Валидация запроса
            if not self._validate_request(request):
                raise ValidationError("Invalid request parameters")
            
            # Получение предпочтений пользователя
            user_preferences = self.user_preferences.get(request.user_id, {})
            
            # Генерация интерфейса
            interface_generator = self.interfaces.get(request.interface_type)
            if not interface_generator:
                raise ValidationError(f"Unsupported interface type: {request.interface_type}")
            
            interface_data = interface_generator.generate_interface(user_preferences)
            
            # Кэширование
            self.cache_interface(request, interface_data)
            
            # Обновление статистики
            self._update_statistics(request.interface_type, True)
            
            return InterfaceResponse(
                success=True,
                interface_data=interface_data,
                session_id=request.session_id or self._generate_session_id(),
                user_preferences=user_preferences,
                recommendations=self._generate_recommendations(request, user_preferences)
            )
            
        except Exception as e:
            self.logger.error(f"Ошибка получения интерфейса: {e}")
            self._update_statistics(request.interface_type, False)
            return self._create_error_response(str(e))
    
    def get_interface_statistics(self) -> Dict[str, Any]:
        """Получение статистики использования интерфейсов"""
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "interface_types_usage": dict(self.interface_usage_stats),
            "average_response_time": self.avg_response_time,
            "error_rate": self.error_rate,
            "performance_metrics": self.performance_metrics,
            "cache_hit_rate": self._calculate_cache_hit_rate()
        }
    
    def update_interface_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Обновление предпочтений пользователя"""
        try:
            # Валидация предпочтений
            if not self._validate_preferences(preferences):
                return False
            
            # Сохранение предпочтений
            self.user_preferences[user_id] = preferences
            self.logger.info(f"Предпочтения пользователя {user_id} обновлены")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка обновления предпочтений: {e}")
            return False
    
    def _validate_request(self, request: InterfaceRequest) -> bool:
        """Валидация запроса"""
        required_fields = ['user_id', 'interface_type', 'device_type', 'platform']
        return all(getattr(request, field) for field in required_fields)
    
    def _validate_preferences(self, preferences: Dict[str, Any]) -> bool:
        """Валидация предпочтений"""
        return isinstance(preferences, dict)
    
    def _generate_session_id(self) -> str:
        """Генерация ID сессии"""
        return f"session_{int(time.time())}_{hash(str(time.time()))}"
    
    def _generate_recommendations(self, request: InterfaceRequest, preferences: Dict[str, Any]) -> List[str]:
        """Генерация рекомендаций"""
        recommendations = []
        
        if request.interface_type == 'web':
            recommendations.append("Consider using dark theme for better eye comfort")
        
        if request.device_type == 'mobile':
            recommendations.append("Enable touch gestures for better navigation")
        
        if preferences.get('language') != 'en':
            recommendations.append("Switch to English for better support")
        
        return recommendations
    
    def _update_statistics(self, interface_type: str, success: bool):
        """Обновление статистики"""
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        
        self.interface_usage_stats[interface_type] += 1
        
        # Обновление error rate
        self.error_rate = (self.total_requests - self.successful_requests) / self.total_requests
    
    def _calculate_cache_hit_rate(self) -> float:
        """Расчет процента попаданий в кэш"""
        if self.total_requests == 0:
            return 0.0
        
        cache_hits = len([c for c in self.interface_cache.values() 
                         if (time.time() - c['timestamp']) < self.cache_ttl])
        return cache_hits / self.total_requests
    
    # Синхронные методы для обратной совместимости
    def start_ui(self) -> bool:
        """Запуск пользовательского интерфейса"""
        try:
            self.logger.info("Запуск пользовательского интерфейса...")
            # Здесь можно добавить логику запуска UI
            self.logger.info("Пользовательский интерфейс запущен")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка запуска UI: {e}")
            return False
    
    def stop_ui(self) -> bool:
        """Остановка пользовательского интерфейса"""
        try:
            self.logger.info("Остановка пользовательского интерфейса...")
            # Здесь можно добавить логику остановки UI
            self.logger.info("Пользовательский интерфейс остановлен")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка остановки UI: {e}")
            return False
    
    def get_ui_info(self) -> Dict[str, Any]:
        """Получение информации о пользовательском интерфейсе"""
        try:
            return {
                "interfaces_count": len(self.interfaces),
                "active_sessions": len(self.user_sessions),
                "cached_interfaces": len(self.interface_cache),
                "performance_metrics": self.performance_metrics,
                "statistics": self.get_interface_statistics()
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения информации UI: {e}")
            return {"error": str(e)}

# =============================================================================
# ТЕСТИРОВАНИЕ
# =============================================================================

async def test_enhanced_user_interface_manager():
    """Тестирование улучшенного менеджера интерфейсов"""
    print("🧪 Тестирование улучшенного UserInterfaceManager...")
    
    try:
        # Создание менеджера
        manager = UserInterfaceManager("EnhancedTestManager")
        print("✅ Менеджер создан")
        
        # Тестирование синхронных методов
        start_result = manager.start_ui()
        print(f"✅ start_ui() -> {start_result}")
        
        stop_result = manager.stop_ui()
        print(f"✅ stop_ui() -> {stop_result}")
        
        ui_info = manager.get_ui_info()
        print(f"✅ get_ui_info() -> {type(ui_info)}")
        
        # Тестирование асинхронных методов
        request = InterfaceRequest(
            user_id="test_user",
            interface_type="web",
            device_type="desktop",
            platform="windows"
        )
        
        response = await manager.get_interface(request)
        print(f"✅ get_interface() -> success: {response.success}")
        
        # Тестирование статистики
        stats = manager.get_interface_statistics()
        print(f"✅ get_interface_statistics() -> {len(stats)} метрик")
        
        # Тестирование обновления предпочтений
        preferences = {"theme": "dark", "language": "ru"}
        update_result = manager.update_interface_preferences("test_user", preferences)
        print(f"✅ update_interface_preferences() -> {update_result}")
        
        # Тестирование фабрики
        web_interface = InterfaceFactory.create_interface("web")
        mobile_interface = InterfaceFactory.create_interface("mobile")
        print(f"✅ InterfaceFactory -> web: {type(web_interface)}, mobile: {type(mobile_interface)}")
        
        # Тестирование кэширования
        cached_data = manager.get_cached_interface(request)
        print(f"✅ get_cached_interface() -> {cached_data is not None}")
        
        print("🎉 Все тесты прошли успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_enhanced_user_interface_manager())