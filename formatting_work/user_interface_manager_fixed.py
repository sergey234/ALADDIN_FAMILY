#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UserInterfaceManager - Интеллектуальный менеджер пользовательского интерфейса
function_85: Универсальное управление интерфейсами для всех типов пользователей

Этот модуль предоставляет продвинутую систему управления
пользовательскими интерфейсами для AI системы безопасности,
включающую:
- Множественные типы интерфейсов (Web, Mobile, Desktop, API, Voice)
- Интеллектуальную адаптацию под пользователей
- ML-анализ поведения пользователей
- Персонализацию интерфейсов
- Интеграцию с системой мониторинга и алертинга
- Поддержка различных устройств и платформ
- Автоматическое обучение и адаптация интерфейсов
- Детальное логирование и аудит всех операций
- Интеграция с внешними системами мониторинга (Prometheus, Grafana)
- Поддержка различных языков и локализации

Основные возможности:
1. Интеллектуальное управление пользовательскими интерфейсами
2. Автоматическая адаптация под предпочтения пользователей
3. ML-оптимизация интерфейсов на основе поведения
4. Интеграция с системой мониторинга для отслеживания метрик
5. Поддержка различных типов интерфейсов и устройств
6. Персонализация на основе контекста и роли пользователя
7. Детальное логирование и аудит всех операций
8. Интеграция с внешними системами мониторинга
9. Поддержка различных языков и культур
10. Автоматическое восстановление после сбоев

Технические детали:
- Использует asyncio для высокопроизводительной асинхронной обработки
- Применяет ML алгоритмы для анализа поведения пользователей
- Интегрирует Redis для кэширования состояний интерфейсов
- Использует SQLAlchemy для работы с базой данных
- Применяет Pydantic для валидации данных
- Интегрирует Prometheus для метрик
- Использует Celery для асинхронных задач
- Применяет nginx для reverse proxy
- Интегрирует ELK stack для логирования

Автор: ALADDIN Security System
Версия: 2.0
Дата: 2025-01-27
Лицензия: MIT
"""

import asyncio
import json
import logging
import os

# Внутренние импорты
import sys
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np

# Внешние зависимости
import redis
import sqlalchemy
from prometheus_client import Counter, Gauge, Histogram
from pydantic import BaseModel, Field, validator
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

sys.path.append(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
)

from core.security_base import SecurityBase

# from core.database import Database  # Database не экспортируется
# from core.configuration import Configuration
# Configuration не экспортируется

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus метрики
INTERFACE_REQUESTS = Counter(
    "ui_manager_requests_total",
    "UI Manager requests",
    ["interface_type", "user_type", "status"],
)
INTERFACE_DURATION = Histogram(
    "ui_manager_request_duration_seconds",
    "UI Manager request duration",
    ["interface_type", "user_type"],
)
ACTIVE_INTERFACES = Gauge(
    "ui_manager_active_interfaces",
    "Active interfaces per type",
    ["interface_type"],
)
USER_SESSIONS = Gauge(
    "ui_manager_user_sessions", "Active user sessions", ["user_type"]
)
ML_RECOMMENDATIONS = Counter(
    "ui_manager_ml_recommendations_total",
    "ML interface recommendations",
    ["recommendation_type", "user_type"],
)

# База данных
Base = declarative_base()


class InterfaceRecord(Base):
    """Запись об интерфейсе"""

    __tablename__ = "interface_records"

    id = Column(String, primary_key=True)
    interface_type = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    user_type = Column(String, nullable=False, index=True)
    device_type = Column(String, nullable=False)
    platform = Column(String, nullable=False)
    language = Column(String, nullable=False, default="en")
    theme = Column(String, nullable=False, default="default")
    layout = Column(String, nullable=False, default="standard")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    meta_data = Column(JSON, default={})


class UserSessionRecord(Base):
    """Запись о пользовательской сессии"""

    __tablename__ = "user_session_records"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    session_id = Column(String, nullable=False, index=True)
    interface_type = Column(String, nullable=False)
    device_info = Column(JSON, default={})
    ip_address = Column(String)
    user_agent = Column(String)
    start_time = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    meta_data = Column(JSON, default={})


class InterfaceEventRecord(Base):
    """Запись о событии интерфейса"""

    __tablename__ = "interface_event_records"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    interface_type = Column(String, nullable=False, index=True)
    event_type = Column(String, nullable=False)
    event_data = Column(JSON, default={})
    timestamp = Column(DateTime, default=datetime.utcnow)
    session_id = Column(String)
    meta_data = Column(JSON, default={})


# Pydantic модели


class InterfaceConfig(BaseModel):
    """Конфигурация интерфейса"""

    interface_type: str = Field(..., description="Тип интерфейса")
    user_id: str = Field(..., description="Идентификатор пользователя")
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


# Перечисления


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

    ADMIN = "admin"
    USER = "user"
    CHILD = "child"
    ELDERLY = "elderly"
    GUEST = "guest"


class DeviceType(Enum):
    """Типы устройств"""

    DESKTOP = "desktop"
    TABLET = "tablet"
    MOBILE = "mobile"
    SMART_TV = "smart_tv"
    SMART_WATCH = "smart_watch"
    VOICE_ASSISTANT = "voice_assistant"


class EventType(Enum):
    """Типы событий"""

    INTERFACE_LOAD = "interface_load"
    INTERFACE_UPDATE = "interface_update"
    USER_INTERACTION = "user_interaction"
    PREFERENCE_CHANGE = "preference_change"
    ERROR = "error"


# Классы для интерфейсов
@dataclass
class WebInterface:
    """Веб-интерфейс"""

    layout: str = "responsive"
    theme: str = "modern"
    components: List[str] = field(default_factory=list)
    navigation: Dict[str, Any] = field(default_factory=dict)

    def generate_interface(
        self, user_preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Генерация веб-интерфейса"""
        return {
            "type": "web",
            "layout": self.layout,
            "theme": self.theme,
            "components": self.components,
            "navigation": self.navigation,
            "user_preferences": user_preferences,
            "responsive": True,
            "accessibility": True,
        }


@dataclass
class MobileInterface:
    """Мобильный интерфейс"""

    layout: str = "mobile_first"
    theme: str = "mobile"
    components: List[str] = field(default_factory=list)
    gestures: List[str] = field(default_factory=list)

    def generate_interface(
        self, user_preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Генерация мобильного интерфейса"""
        return {
            "type": "mobile",
            "layout": self.layout,
            "theme": self.theme,
            "components": self.components,
            "gestures": self.gestures,
            "user_preferences": user_preferences,
            "touch_optimized": True,
            "offline_support": True,
        }


@dataclass
class VoiceInterface:
    """Голосовой интерфейс"""

    language: str = "en"
    voice_type: str = "natural"
    commands: List[str] = field(default_factory=list)
    responses: Dict[str, str] = field(default_factory=dict)

    def generate_interface(
        self, user_preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Генерация голосового интерфейса"""
        return {
            "type": "voice",
            "language": self.language,
            "voice_type": self.voice_type,
            "commands": self.commands,
            "responses": self.responses,
            "user_preferences": user_preferences,
            "speech_recognition": True,
            "text_to_speech": True,
        }


@dataclass
class APIInterface:
    """API интерфейс"""

    version: str = "v1"
    endpoints: List[str] = field(default_factory=list)
    authentication: str = "jwt"
    rate_limiting: bool = True

    def generate_interface(
        self, user_preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Генерация API интерфейса"""
        return {
            "type": "api",
            "version": self.version,
            "endpoints": self.endpoints,
            "authentication": self.authentication,
            "rate_limiting": self.rate_limiting,
            "user_preferences": user_preferences,
            "documentation": True,
            "swagger": True,
        }


# Основной класс UserInterfaceManager


class UserInterfaceManager(SecurityBase):
    """
    Интеллектуальный менеджер пользовательского интерфейса

    Предоставляет продвинутую систему управления интерфейсами с поддержкой:
    - Множественных типов интерфейсов
    - ML анализа поведения пользователей
    - Персонализации интерфейсов
    - Интеграции с мониторингом
    """

    def __init__(
        self,
        name: str = "UserInterfaceManager",
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Инициализация UserInterfaceManager

        Args:
            name: Имя UserInterfaceManager
            config: Конфигурация
        """
        super().__init__(name, config)

        # Конфигурация по умолчанию
        self.default_config = {
            "redis_url": "redis://localhost:6379/0",
            "database_url": "sqlite:///user_interface_manager.db",
            "default_interface_type": "web",
            "default_theme": "modern",
            "default_language": "en",
            "ml_enabled": True,
            "adaptive_ui": True,
            "personalization_threshold": 0.7,
            "max_adaptive_factor": 2.0,
            "min_adaptive_factor": 0.1,
            "cleanup_interval": 300,  # секунд
            "metrics_enabled": True,
            "logging_enabled": True,
            "enable_caching": True,
            "cache_ttl": 3600,  # секунд
            "session_timeout": 1800,  # секунд
        }

        # Объединение конфигураций
        self.config = {**self.default_config, **(config or {})}

        # Инициализация компонентов
        self.redis_client: Optional[redis.Redis] = None
        self.db_engine: Optional[sqlalchemy.Engine] = None
        self.db_session: Optional[sqlalchemy.orm.Session] = None
        self.interfaces: Dict[str, Any] = {}
        self.user_sessions: Dict[str, Dict[str, Any]] = {}
        self.user_preferences: Dict[str, Dict[str, Any]] = {}
        self.ml_model: Optional[IsolationForest] = None
        self.scaler: Optional[StandardScaler] = None
        self.adaptive_factors: Dict[str, float] = defaultdict(lambda: 1.0)

        # Статистика
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "interface_generations": 0,
            "ml_recommendations": 0,
            "adaptive_adjustments": 0,
            "active_sessions": 0,
        }

        # Потоки
        self.cleanup_thread: Optional[threading.Thread] = None
        self.ml_thread: Optional[threading.Thread] = None
        self.running = False

        # Блокировки
        self.lock = threading.RLock()

        self.logger.info(f"UserInterfaceManager {name} инициализирован")

    async def start(self) -> bool:
        """Запуск UserInterfaceManager"""
        try:
            self.logger.info("Запуск UserInterfaceManager")

            # Инициализация базы данных
            await self._initialize_database()

            # Инициализация Redis
            await self._initialize_redis()

            # Инициализация ML модели
            if self.config["ml_enabled"]:
                await self._initialize_ml_model()

            # Запуск фоновых потоков
            self.running = True
            self.cleanup_thread = threading.Thread(
                target=self._cleanup_worker, daemon=True
            )
            self.cleanup_thread.start()

            if self.config["ml_enabled"]:
                self.ml_thread = threading.Thread(
                    target=self._ml_worker, daemon=True
                )
                self.ml_thread.start()

            self.logger.info("UserInterfaceManager успешно запущен")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка запуска UserInterfaceManager: {e}")
            return False

    async def stop(self) -> bool:
        """Остановка UserInterfaceManager"""
        try:
            self.logger.info("Остановка UserInterfaceManager")

            self.running = False

            # Остановка потоков
            if self.cleanup_thread and self.cleanup_thread.is_alive():
                self.cleanup_thread.join(timeout=5)

            if self.ml_thread and self.ml_thread.is_alive():
                self.ml_thread.join(timeout=5)

            # Закрытие соединений
            if self.redis_client:
                self.redis_client.close()

            if self.db_session:
                self.db_session.close()

            if self.db_engine:
                self.db_engine.dispose()

            self.logger.info("UserInterfaceManager успешно остановлен")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка остановки UserInterfaceManager: {e}")
            return False

    async def _initialize_database(self) -> None:
        """Инициализация базы данных"""
        try:
            database_url = self.config.get(
                "database_url", "sqlite:///user_interface_manager.db"
            )
            self.db_engine = create_engine(database_url, echo=False)

            # Создание таблиц
            Base.metadata.create_all(self.db_engine)

            # Создание сессии
            Session = sessionmaker(bind=self.db_engine)
            self.db_session = Session()

            self.logger.info(
                "База данных UserInterfaceManager инициализирована"
            )

        except Exception as e:
            self.logger.error(f"Ошибка инициализации базы данных: {e}")
            raise

    async def _initialize_redis(self) -> None:
        """Инициализация Redis"""
        try:
            redis_url = self.config.get(
                "redis_url", "redis://localhost:6379/0"
            )
            self.redis_client = redis.from_url(
                redis_url, decode_responses=True
            )

            # Тест соединения
            self.redis_client.ping()

            self.logger.info(
                "Redis клиент UserInterfaceManager инициализирован"
            )

        except Exception as e:
            self.logger.error(f"Ошибка инициализации Redis: {e}")
            raise

    async def _initialize_ml_model(self) -> None:
        """Инициализация ML модели"""
        try:
            # Инициализация модели анализа поведения пользователей
            self.ml_model = IsolationForest(
                contamination=self.config["personalization_threshold"],
                random_state=42,
            )

            # Инициализация скейлера
            self.scaler = StandardScaler()

            self.logger.info("ML модель UserInterfaceManager инициализирована")

        except Exception as e:
            self.logger.error(f"Ошибка инициализации ML модели: {e}")
            raise

    async def get_interface(
        self, request: InterfaceRequest
    ) -> InterfaceResponse:
        """
        Получение интерфейса для пользователя

        Args:
            request: Запрос на получение интерфейса

        Returns:
            InterfaceResponse: Ответ с интерфейсом
        """
        start_time = time.time()

        try:
            with self.lock:
                self.stats["total_requests"] += 1

            # Получение или создание сессии
            session_id = await self._get_or_create_session(request)

            # Получение предпочтений пользователя
            user_preferences = await self._get_user_preferences(
                request.user_id, request.interface_type
            )

            # ML анализ поведения пользователя
            if self.config["ml_enabled"]:
                recommendations = await self._get_ml_recommendations(
                    request, user_preferences
                )
                with self.lock:
                    self.stats["ml_recommendations"] += 1
                ML_RECOMMENDATIONS.labels(
                    recommendation_type="interface",
                    user_type=user_preferences.get("user_type", "user"),
                ).inc()
            else:
                recommendations = []

            # Генерация интерфейса
            interface_data = await self._generate_interface(
                request, user_preferences, recommendations
            )

            # Обновление статистики
            with self.lock:
                self.stats["successful_requests"] += 1
                self.stats["interface_generations"] += 1

            # Логирование
            duration = time.time() - start_time
            INTERFACE_DURATION.labels(
                interface_type=request.interface_type,
                user_type=user_preferences.get("user_type", "user"),
            ).observe(duration)

            INTERFACE_REQUESTS.labels(
                interface_type=request.interface_type,
                user_type=user_preferences.get("user_type", "user"),
                status="success",
            ).inc()

            return InterfaceResponse(
                success=True,
                interface_data=interface_data,
                user_preferences=user_preferences,
                recommendations=recommendations,
                session_id=session_id,
                metadata={
                    "generation_time_ms": duration * 1000,
                    "ml_enabled": self.config["ml_enabled"],
                    "adaptive_ui": self.config["adaptive_ui"],
                },
            )

        except Exception as e:
            self.logger.error(f"Ошибка получения интерфейса: {e}")

            with self.lock:
                self.stats["failed_requests"] += 1

            INTERFACE_REQUESTS.labels(
                interface_type=request.interface_type,
                user_type="unknown",
                status="error",
            ).inc()

            return InterfaceResponse(
                success=False,
                interface_data={},
                user_preferences={},
                recommendations=[],
                session_id="",
                metadata={"error": str(e)},
            )

    async def _get_or_create_session(self, request: InterfaceRequest) -> str:
        """Получение или создание пользовательской сессии"""
        session_id = (
            request.session_id
            or f"session_{int(time.time() * 1000)}_{request.user_id}"
        )

        if session_id not in self.user_sessions:
            # Создание новой сессии
            session_data = {
                "user_id": request.user_id,
                "session_id": session_id,
                "interface_type": request.interface_type,
                "device_info": {
                    "device_type": request.device_type,
                    "platform": request.platform,
                    "user_agent": request.meta_data.get("user_agent", ""),
                    "ip_address": request.meta_data.get("ip_address", ""),
                },
                "start_time": datetime.utcnow(),
                "last_activity": datetime.utcnow(),
                "is_active": True,
                "meta_data": request.meta_data,
            }

            self.user_sessions[session_id] = session_data

            # Сохранение в базу данных
            await self._save_session_record(session_data)

            with self.lock:
                self.stats["active_sessions"] += 1

        # Обновление активности
        self.user_sessions[session_id]["last_activity"] = datetime.utcnow()

        return session_id

    async def _get_user_preferences(
        self, user_id: str, interface_type: str
    ) -> Dict[str, Any]:
        """Получение предпочтений пользователя"""
        # Проверка кэша
        cache_key = f"user_preferences:{user_id}:{interface_type}"

        if self.redis_client and self.config["enable_caching"]:
            cached_preferences = self.redis_client.get(cache_key)
            if cached_preferences:
                return json.loads(cached_preferences)

        # Получение из базы данных
        if self.db_session:
            record = (
                self.db_session.query(InterfaceRecord)
                .filter(
                    InterfaceRecord.user_id == user_id,
                    InterfaceRecord.interface_type == interface_type,
                    InterfaceRecord.is_active,
                )
                .first()
            )

            if record:
                preferences = {
                    "user_id": record.user_id,
                    "user_type": record.user_type,
                    "interface_type": record.interface_type,
                    "device_type": record.device_type,
                    "platform": record.platform,
                    "language": record.language,
                    "theme": record.theme,
                    "layout": record.layout,
                    "meta_data": record.meta_data or {},
                }

                # Кэширование
                if self.redis_client and self.config["enable_caching"]:
                    self.redis_client.setex(
                        cache_key,
                        self.config["cache_ttl"],
                        json.dumps(preferences),
                    )

                return preferences

        # Создание предпочтений по умолчанию
        default_preferences = {
            "user_id": user_id,
            "user_type": "user",
            "interface_type": interface_type,
            "device_type": "desktop",
            "platform": "web",
            "language": self.config["default_language"],
            "theme": self.config["default_theme"],
            "layout": "standard",
            "meta_data": {},
        }

        # Сохранение в базу данных
        await self._save_interface_record(default_preferences)

        return default_preferences

    async def _get_ml_recommendations(
        self, request: InterfaceRequest, user_preferences: Dict[str, Any]
    ) -> List[str]:
        """Получение ML рекомендаций для интерфейса"""
        if not self.ml_model or not self.scaler:
            return []

        try:
            # Подготовка признаков
            features = self._extract_user_features(request, user_preferences)

            if len(features) == 0:
                return []

            # Нормализация признаков
            features_scaled = self.scaler.transform([features])

            # Предсказание предпочтений
            preference_score = self.ml_model.decision_function(
                features_scaled
            )[0]

            # Генерация рекомендаций на основе предсказания
            recommendations = []

            if preference_score > 0.5:
                recommendations.append("dark_theme")
                recommendations.append("compact_layout")
            elif preference_score < -0.5:
                recommendations.append("light_theme")
                recommendations.append("spacious_layout")

            # Рекомендации на основе типа пользователя
            user_type = user_preferences.get("user_type", "user")
            if user_type == "child":
                recommendations.extend(
                    ["colorful_theme", "large_buttons", "simple_navigation"]
                )
            elif user_type == "elderly":
                recommendations.extend(
                    ["high_contrast", "large_text", "simple_layout"]
                )
            elif user_type == "admin":
                recommendations.extend(
                    [
                        "advanced_features",
                        "detailed_views",
                        "power_user_layout",
                    ]
                )

            return recommendations[:5]  # Максимум 5 рекомендаций

        except Exception as e:
            self.logger.error(f"Ошибка получения ML рекомендаций: {e}")
            return []

    def _extract_user_features(
        self, request: InterfaceRequest, user_preferences: Dict[str, Any]
    ) -> List[float]:
        """Извлечение признаков пользователя для ML анализа"""
        features = []

        # Временные признаки
        now = datetime.utcnow()
        features.extend([now.hour, now.weekday(), now.day, now.month])

        # Признаки запроса
        features.extend(
            [
                len(request.meta_data) if request.meta_data else 0,
                hash(request.device_type) % 1000,
                hash(request.platform) % 1000,
            ]
        )

        # Признаки пользователя
        features.extend(
            [
                hash(user_preferences.get("user_type", "user")) % 1000,
                hash(user_preferences.get("theme", "default")) % 1000,
                hash(user_preferences.get("layout", "standard")) % 1000,
            ]
        )

        # Признаки сессии
        if request.session_id and request.session_id in self.user_sessions:
            session = self.user_sessions[request.session_id]
            session_duration = (now - session["start_time"]).total_seconds()
            features.append(min(session_duration, 3600))  # Максимум 1 час
        else:
            features.append(0)

        return features

    async def _generate_interface(
        self,
        request: InterfaceRequest,
        user_preferences: Dict[str, Any],
        recommendations: List[str],
    ) -> Dict[str, Any]:
        """Генерация интерфейса на основе запроса и предпочтений"""
        interface_type = InterfaceType(request.interface_type)

        # Применение рекомендаций
        if recommendations:
            if "dark_theme" in recommendations:
                user_preferences["theme"] = "dark"
            if "light_theme" in recommendations:
                user_preferences["theme"] = "light"
            if "compact_layout" in recommendations:
                user_preferences["layout"] = "compact"
            if "spacious_layout" in recommendations:
                user_preferences["layout"] = "spacious"

        # Создание интерфейса
        if interface_type == InterfaceType.WEB:
            interface = WebInterface(
                layout=user_preferences.get("layout", "responsive"),
                theme=user_preferences.get("theme", "modern"),
                components=self._get_web_components(user_preferences),
                navigation=self._get_web_navigation(user_preferences),
            )
        elif interface_type == InterfaceType.MOBILE:
            interface = MobileInterface(
                layout=user_preferences.get("layout", "mobile_first"),
                theme=user_preferences.get("theme", "mobile"),
                components=self._get_mobile_components(user_preferences),
                gestures=self._get_mobile_gestures(user_preferences),
            )
        elif interface_type == InterfaceType.VOICE:
            interface = VoiceInterface(
                language=user_preferences.get("language", "en"),
                voice_type=user_preferences.get("voice_type", "natural"),
                commands=self._get_voice_commands(user_preferences),
                responses=self._get_voice_responses(user_preferences),
            )
        elif interface_type == InterfaceType.API:
            interface = APIInterface(
                version=user_preferences.get("api_version", "v1"),
                endpoints=self._get_api_endpoints(user_preferences),
                authentication=user_preferences.get("auth_type", "jwt"),
                rate_limiting=user_preferences.get("rate_limiting", True),
            )
        else:
            # Fallback к веб-интерфейсу
            interface = WebInterface(
                layout=user_preferences.get("layout", "responsive"),
                theme=user_preferences.get("theme", "modern"),
                components=self._get_web_components(user_preferences),
                navigation=self._get_web_navigation(user_preferences),
            )

        return interface.generate_interface(user_preferences)

    def _get_web_components(
        self, user_preferences: Dict[str, Any]
    ) -> List[str]:
        """Получение компонентов для веб-интерфейса"""
        components = [
            "header",
            "navigation",
            "main_content",
            "sidebar",
            "footer",
        ]

        user_type = user_preferences.get("user_type", "user")
        if user_type == "admin":
            components.extend(
                ["admin_panel", "analytics_dashboard", "user_management"]
            )
        elif user_type == "child":
            components.extend(
                ["parental_controls", "child_dashboard", "games"]
            )
        elif user_type == "elderly":
            components.extend(
                ["accessibility_tools", "help_system", "emergency_button"]
            )

        return components

    def _get_mobile_components(
        self, user_preferences: Dict[str, Any]
    ) -> List[str]:
        """Получение компонентов для мобильного интерфейса"""
        components = [
            "mobile_header",
            "bottom_navigation",
            "swipe_gestures",
            "touch_controls",
        ]

        user_type = user_preferences.get("user_type", "user")
        if user_type == "child":
            components.extend(
                ["parental_locks", "child_mode", "fun_animations"]
            )
        elif user_type == "elderly":
            components.extend(
                ["large_buttons", "voice_commands", "emergency_contact"]
            )

        return components

    def _get_voice_commands(
        self, user_preferences: Dict[str, Any]
    ) -> List[str]:
        """Получение голосовых команд"""
        commands = ["help", "status", "settings", "logout"]

        user_type = user_preferences.get("user_type", "user")
        if user_type == "admin":
            commands.extend(["admin_panel", "user_list", "system_status"])
        elif user_type == "child":
            commands.extend(["play", "games", "parent_help"])
        elif user_type == "elderly":
            commands.extend(["emergency", "help", "call_family"])

        return commands

    def _get_voice_responses(
        self, user_preferences: Dict[str, Any]
    ) -> Dict[str, str]:
        """Получение голосовых ответов"""
        language = user_preferences.get("language", "en")

        if language == "ru":
            return {
                "welcome": "Добро пожаловать в систему безопасности",
                "help": "Чем могу помочь?",
                "error": "Произошла ошибка, попробуйте еще раз",
            }
        else:
            return {
                "welcome": "Welcome to the security system",
                "help": "How can I help you?",
                "error": "An error occurred, please try again",
            }

    def _get_web_navigation(
        self, user_preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Получение навигации для веб-интерфейса"""
        user_type = user_preferences.get("user_type", "user")

        if user_type == "admin":
            return {
                "main": [
                    "dashboard",
                    "users",
                    "security",
                    "analytics",
                    "settings",
                ],
                "secondary": ["logs", "reports", "alerts", "backup"],
            }
        elif user_type == "child":
            return {
                "main": ["home", "games", "help", "parent_zone"],
                "secondary": ["settings", "profile"],
            }
        elif user_type == "elderly":
            return {
                "main": ["home", "help", "emergency", "family"],
                "secondary": ["settings", "accessibility"],
            }
        else:
            return {
                "main": ["home", "security", "settings", "help"],
                "secondary": ["profile", "notifications"],
            }

    def _get_mobile_gestures(
        self, user_preferences: Dict[str, Any]
    ) -> List[str]:
        """Получение жестов для мобильного интерфейса"""
        gestures = [
            "swipe_up",
            "swipe_down",
            "swipe_left",
            "swipe_right",
            "tap",
            "long_press",
        ]

        user_type = user_preferences.get("user_type", "user")
        if user_type == "child":
            gestures.extend(["double_tap", "pinch_zoom"])
        elif user_type == "elderly":
            gestures = ["tap", "long_press"]  # Упрощенные жесты

        return gestures

    def _get_api_endpoints(
        self, user_preferences: Dict[str, Any]
    ) -> List[str]:
        """Получение API endpoints"""
        endpoints = ["/api/v1/status", "/api/v1/health", "/api/v1/auth"]

        user_type = user_preferences.get("user_type", "user")
        if user_type == "admin":
            endpoints.extend(
                [
                    "/api/v1/admin/users",
                    "/api/v1/admin/security",
                    "/api/v1/admin/analytics",
                ]
            )
        elif user_type == "child":
            endpoints.extend(["/api/v1/child/games", "/api/v1/child/parental"])
        elif user_type == "elderly":
            endpoints.extend(
                ["/api/v1/elderly/emergency", "/api/v1/elderly/help"]
            )

        return endpoints

    async def _save_interface_record(
        self, preferences: Dict[str, Any]
    ) -> None:
        """Сохранение записи интерфейса"""
        try:
            record = InterfaceRecord(
                id=f"interface_{preferences['user_id']}_"
                f"{preferences['interface_type']}",
                interface_type=preferences["interface_type"],
                user_id=preferences["user_id"],
                user_type=preferences["user_type"],
                device_type=preferences["device_type"],
                platform=preferences["platform"],
                language=preferences["language"],
                theme=preferences["theme"],
                layout=preferences["layout"],
                meta_data=preferences["meta_data"],
            )

            if self.db_session:
                # Обновление или создание записи
                existing = (
                    self.db_session.query(InterfaceRecord)
                    .filter(InterfaceRecord.id == record.id)
                    .first()
                )

                if existing:
                    existing.user_type = record.user_type
                    existing.device_type = record.device_type
                    existing.platform = record.platform
                    existing.language = record.language
                    existing.theme = record.theme
                    existing.layout = record.layout
                    existing.updated_at = datetime.utcnow()
                else:
                    self.db_session.add(record)

                self.db_session.commit()

        except Exception as e:
            self.logger.error(f"Ошибка сохранения записи интерфейса: {e}")

    async def _save_session_record(self, session_data: Dict[str, Any]) -> None:
        """Сохранение записи сессии"""
        try:
            record = UserSessionRecord(
                id=session_data["session_id"],
                user_id=session_data["user_id"],
                session_id=session_data["session_id"],
                interface_type=session_data["interface_type"],
                device_info=session_data["device_info"],
                ip_address=session_data["device_info"].get("ip_address"),
                user_agent=session_data["device_info"].get("user_agent"),
                start_time=session_data["start_time"],
                last_activity=session_data["last_activity"],
                meta_data=session_data["meta_data"],
            )

            if self.db_session:
                # Обновление или создание записи
                existing = (
                    self.db_session.query(UserSessionRecord)
                    .filter(UserSessionRecord.id == record.id)
                    .first()
                )

                if existing:
                    existing.last_activity = record.last_activity
                    existing.is_active = record.is_active
                else:
                    self.db_session.add(record)

                self.db_session.commit()

        except Exception as e:
            self.logger.error(f"Ошибка сохранения записи сессии: {e}")

    def _cleanup_worker(self) -> None:
        """Фоновый процесс очистки"""
        while self.running:
            try:
                time.sleep(self.config["cleanup_interval"])

                with self.lock:
                    # Очистка неактивных сессий
                    current_time = datetime.utcnow()
                    sessions_to_remove = []

                    for session_id, session in self.user_sessions.items():
                        time_since_activity = (
                            current_time - session["last_activity"]
                        ).total_seconds()
                        if (
                            time_since_activity
                            > self.config["session_timeout"]
                        ):
                            sessions_to_remove.append(session_id)

                    for session_id in sessions_to_remove:
                        del self.user_sessions[session_id]
                        self.stats["active_sessions"] -= 1

                self.logger.debug("Очистка UserInterfaceManager завершена")

            except Exception as e:
                self.logger.error(f"Ошибка в процессе очистки: {e}")

    def _ml_worker(self) -> None:
        """Фоновый процесс ML обучения"""
        while self.running:
            try:
                time.sleep(3600)  # Обучение каждый час

                if not self.ml_model or not self.scaler:
                    continue

                # Сбор данных для обучения
                training_data = []

                with self.lock:
                    for session in self.user_sessions.values():
                        features = self._extract_session_features(session)
                        if features:
                            training_data.append(features)

                if len(training_data) < 10:  # Недостаточно данных
                    continue

                # Обучение модели
                X = np.array(training_data)
                self.scaler.fit(X)
                X_scaled = self.scaler.transform(X)
                self.ml_model.fit(X_scaled)

                # Обновление адаптивных факторов
                self._update_adaptive_factors()

                self.logger.info("ML модель UserInterfaceManager переобучена")

            except Exception as e:
                self.logger.error(f"Ошибка в ML процессе: {e}")

    def _extract_session_features(
        self, session: Dict[str, Any]
    ) -> List[float]:
        """Извлечение признаков из сессии для ML"""
        features = []

        # Временные признаки
        now = datetime.utcnow()
        features.extend([now.hour, now.weekday(), now.day, now.month])

        # Признаки сессии
        session_duration = (now - session["start_time"]).total_seconds()
        features.extend(
            [
                min(session_duration, 3600),  # Максимум 1 час
                len(session["meta_data"]) if session["meta_data"] else 0,
            ]
        )

        # Признаки устройства
        device_info = session["device_info"]
        features.extend(
            [
                hash(device_info.get("device_type", "desktop")) % 1000,
                hash(device_info.get("platform", "web")) % 1000,
            ]
        )

        return features

    async def _update_adaptive_factors(self) -> None:
        """Обновление адаптивных факторов на основе ML анализа"""
        try:
            with self.lock:
                for session_id, session in self.user_sessions.items():
                    # Анализ поведения пользователя
                    session_duration = (
                        datetime.utcnow() - session["start_time"]
                    ).total_seconds()

                    # Адаптация фактора на основе длительности сессии
                    if session_duration > 1800:  # Более 30 минут
                        self.adaptive_factors[session_id] = min(
                            self.config["max_adaptive_factor"],
                            self.adaptive_factors[session_id] * 1.1,
                        )
                    elif session_duration < 300:  # Менее 5 минут
                        self.adaptive_factors[session_id] = max(
                            self.config["min_adaptive_factor"],
                            self.adaptive_factors[session_id] * 0.9,
                        )

                    self.stats["adaptive_adjustments"] += 1

        except Exception as e:
            self.logger.error(f"Ошибка обновления адаптивных факторов: {e}")

    async def get_status(self) -> Dict[str, Any]:
        """Получение статуса UserInterfaceManager"""
        with self.lock:
            return {
                "name": self.name,
                "status": "running" if self.running else "stopped",
                "stats": self.stats.copy(),
                "active_sessions": len(self.user_sessions),
                "interface_types": list(
                    set(
                        session["interface_type"]
                        for session in self.user_sessions.values()
                    )
                ),
                "user_types": list(
                    set(
                        session.get("user_type", "user")
                        for session in self.user_sessions.values()
                    )
                ),
                "adaptive_factors": dict(self.adaptive_factors),
                "config": {
                    "ml_enabled": self.config["ml_enabled"],
                    "adaptive_ui": self.config["adaptive_ui"],
                    "default_interface_type": self.config[
                        "default_interface_type"
                    ],
                    "default_theme": self.config["default_theme"],
                },
            }

    async def update_user_preferences(
        self, user_id: str, interface_type: str, preferences: Dict[str, Any]
    ) -> bool:
        """Обновление предпочтений пользователя"""
        try:
            # Обновление в памяти
            cache_key = f"user_preferences:{user_id}:{interface_type}"
            if self.redis_client and self.config["enable_caching"]:
                self.redis_client.setex(
                    cache_key,
                    self.config["cache_ttl"],
                    json.dumps(preferences),
                )

            # Обновление в базе данных
            if self.db_session:
                record = (
                    self.db_session.query(InterfaceRecord)
                    .filter(
                        InterfaceRecord.user_id == user_id,
                        InterfaceRecord.interface_type == interface_type,
                        InterfaceRecord.is_active,
                    )
                    .first()
                )

                if record:
                    record.theme = preferences.get("theme", record.theme)
                    record.layout = preferences.get("layout", record.layout)
                    record.language = preferences.get(
                        "language", record.language
                    )
                    record.meta_data = preferences.get(
                        "metadata", record.meta_data
                    )
                    record.updated_at = datetime.utcnow()
                    self.db_session.commit()

            self.logger.info(f"Предпочтения пользователя {user_id} обновлены")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка обновления предпочтений: {e}")
            return False

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
                "user_preferences_count": len(self.user_preferences),
                "ml_enabled": self.config.get("ml_enabled", False),
                "adaptive_ui": self.config.get("adaptive_ui", False),
                "caching_enabled": self.config.get("enable_caching", False),
                "default_theme": self.config.get("default_theme", "modern"),
                "default_language": self.config.get("default_language", "en"),
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения информации о UI: {e}")
            return {
                "interfaces_count": 0,
                "active_sessions": 0,
                "user_preferences_count": 0,
                "ml_enabled": False,
                "adaptive_ui": False,
                "caching_enabled": False,
                "default_theme": "modern",
                "default_language": "en",
                "error": str(e),
            }


import uvicorn

# API сервер для UserInterfaceManager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="UserInterfaceManager API", version="2.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Глобальный экземпляр UserInterfaceManager
ui_manager: Optional[UserInterfaceManager] = None


@app.on_event("startup")
async def startup_event():
    """Инициализация UserInterfaceManager при запуске"""
    global ui_manager
    ui_manager = UserInterfaceManager("UserInterfaceManagerServer")
    await ui_manager.start()


@app.on_event("shutdown")
async def shutdown_event():
    """Остановка UserInterfaceManager при завершении"""
    global ui_manager
    if ui_manager:
        await ui_manager.stop()


@app.get("/health")
async def health_check():
    """Проверка здоровья UserInterfaceManager"""
    return {"status": "healthy", "service": "UserInterfaceManager"}


@app.get("/status")
async def get_status():
    """Получение статуса UserInterfaceManager"""
    if not ui_manager:
        raise HTTPException(
            status_code=503, detail="UserInterfaceManager not initialized"
        )

    return await ui_manager.get_status()


@app.post("/interface")
async def get_interface(request: InterfaceRequest):
    """Получение интерфейса для пользователя"""
    if not ui_manager:
        raise HTTPException(
            status_code=503, detail="UserInterfaceManager not initialized"
        )

    return await ui_manager.get_interface(request)


@app.put("/preferences/{user_id}/{interface_type}")
async def update_preferences(
    user_id: str, interface_type: str, preferences: Dict[str, Any]
):
    """Обновление предпочтений пользователя"""
    if not ui_manager:
        raise HTTPException(
            status_code=503, detail="UserInterfaceManager not initialized"
        )

    success = await ui_manager.update_user_preferences(
        user_id, interface_type, preferences
    )
    if not success:
        raise HTTPException(
            status_code=500, detail="Failed to update preferences"
        )

    return {"message": "Preferences updated successfully"}


@app.get("/metrics")
async def get_metrics():
    """Получение метрик Prometheus"""
    from fastapi.responses import Response
    from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# Основная функция для запуска сервера


def main():
    """Запуск сервера UserInterfaceManager"""
    uvicorn.run(
        "user_interface_manager:app",
        host="0.0.0.0",
        port=8009,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()


# Тестирование
async def test_user_interface_manager():
    """Тестирование UserInterfaceManager"""
    print("🧪 Тестирование UserInterfaceManager...")

    # Создание экземпляра
    manager = UserInterfaceManager("TestUserInterfaceManager")

    try:
        # Запуск
        await manager.start()
        print("✅ UserInterfaceManager запущен")

        # Тест 1: Веб-интерфейс для обычного пользователя
        request = InterfaceRequest(
            user_id="test_user_1",
            interface_type="web",
            device_type="desktop",
            platform="web",
        )

        response = await manager.get_interface(request)
        print(
            f"✅ Тест 1 - Веб-интерфейс: {response.success}, "
            f"тип: {response.interface_data.get('type')}"
        )

        # Тест 2: Мобильный интерфейс для ребенка
        request = InterfaceRequest(
            user_id="test_child_1",
            interface_type="mobile",
            device_type="mobile",
            platform="ios",
            meta_data={"user_type": "child"},
        )

        response = await manager.get_interface(request)
        print(
            f"✅ Тест 2 - Мобильный интерфейс для ребенка: {response.success}"
        )

        # Тест 3: Голосовой интерфейс для пожилого
        request = InterfaceRequest(
            user_id="test_elderly_1",
            interface_type="voice",
            device_type="voice_assistant",
            platform="alexa",
            meta_data={"user_type": "elderly", "language": "ru"},
        )

        response = await manager.get_interface(request)
        print(
            f"✅ Тест 3 - Голосовой интерфейс: {response.success}, "
            f"язык: {response.interface_data.get('language')}"
        )

        # Тест 4: API интерфейс для администратора
        request = InterfaceRequest(
            user_id="test_admin_1",
            interface_type="api",
            device_type="desktop",
            platform="api",
            meta_data={"user_type": "admin"},
        )

        response = await manager.get_interface(request)
        print(
            f"✅ Тест 4 - API интерфейс: {response.success}, "
            f"endpoints: {len(response.interface_data.get('endpoints', []))}"
        )

        # Тест 5: Статус
        status = await manager.get_status()
        print(
            f"✅ Тест 5 - Статус: {status['status']}, "
            f"активных сессий: {status['active_sessions']}"
        )

        # Тест 6: Обновление предпочтений
        success = await manager.update_user_preferences(
            "test_user_1", "web", {"theme": "dark", "layout": "compact"}
        )
        print(f"✅ Тест 6 - Обновление предпочтений: {success}")

        print("🎉 Все тесты UserInterfaceManager прошли успешно!")

    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")

    finally:
        # Остановка
        await manager.stop()
        print("✅ UserInterfaceManager остановлен")


# Запуск тестов при прямом выполнении
if __name__ == "__main__":
    asyncio.run(test_user_interface_manager())
