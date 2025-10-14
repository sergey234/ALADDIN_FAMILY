#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ParentalControlBot - Бот родительского контроля
function_89: Критически важный бот для семейной безопасности

Этот модуль предоставляет интеллектуального бота для родительского контроля,
включающего:
- Мониторинг активности детей в интернете
- Блокировка нежелательного контента
- Контроль времени использования устройств
- Отслеживание местоположения
- Уведомления о подозрительной активности
- Настройка возрастных ограничений
- Контроль приложений и игр
- Мониторинг социальных сетей
- Безопасное общение
- Образовательный контент

Основные возможности:
1. Умная фильтрация контента
2. Контроль времени использования
3. Геолокация и безопасные зоны
4. Мониторинг социальных сетей
5. Блокировка опасных приложений
6. Образовательные рекомендации
7. Родительские уведомления
8. Настройка возрастных ограничений
9. Контроль покупок в приложениях
10. Анализ поведения детей

Технические детали:
- Использует ML для анализа контента
- Применяет геофенсинг для контроля местоположения
- Интегрирует с браузерами и приложениями
- Использует NLP для анализа текста
- Применяет компьютерное зрение для анализа изображений
- Интегрирует с образовательными платформами
- Использует криптографию для защиты данных
- Применяет поведенческий анализ
- Интегрирует с социальными сетями
- Использует рекомендательные системы

Автор: ALADDIN Security System
Версия: 2.0
Дата: 2025-01-27
Лицензия: MIT
"""

import asyncio
import base64
import hashlib
import json
import logging
import os

# Внутренние импорты
import sys
import threading
import time
from collections import defaultdict
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple

# Внешние зависимости
import redis
import sqlalchemy
import structlog
from prometheus_client import Counter, Gauge
from pydantic import BaseModel, Field, validator
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from core.base import SecurityBase
from security.bots.components.advanced_logger import (
    AdvancedLogger,
    LogContext,
    LogLevel,
)

# Компоненты
from security.bots.components.cache_manager import CacheManager, CacheStrategy
from security.bots.components.config_manager import (
    ConfigFormat,
    ConfigManager,
    ParentalControlConfig,
)
from security.bots.components.encryption_manager import (
    EncryptedData,
    EncryptionAlgorithm,
    EncryptionManager,
)
from security.bots.components.performance_optimizer import (
    PerformanceMetric,
    PerformanceOptimizer,
    performance_monitor,
)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# База данных
Base = declarative_base()


class ContentCategory(Enum):
    """Категории контента"""

    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    SOCIAL = "social"
    GAMING = "gaming"
    SHOPPING = "shopping"
    NEWS = "news"
    ADULT = "adult"
    VIOLENCE = "violence"
    DRUGS = "drugs"
    GAMBLING = "gambling"
    UNKNOWN = "unknown"


class AgeGroup(Enum):
    """Возрастные группы"""

    TODDLER = "toddler"  # 2-4 года
    PRESCHOOL = "preschool"  # 4-6 лет
    ELEMENTARY = "elementary"  # 6-12 лет
    TEEN = "teen"  # 12-18 лет
    ADULT = "adult"  # 18+ лет


class DeviceType(Enum):
    """Типы устройств"""

    MOBILE = "mobile"
    TABLET = "tablet"
    DESKTOP = "desktop"
    SMART_TV = "smart_tv"
    GAMING_CONSOLE = "gaming_console"
    SMART_WATCH = "smart_watch"


class ControlAction(Enum):
    """Действия контроля"""

    ALLOW = "allow"
    BLOCK = "block"
    WARN = "warn"
    RESTRICT = "restrict"
    MONITOR = "monitor"


class ChildProfile(Base):
    """Профиль ребенка"""

    __tablename__ = "child_profiles"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    age_group = Column(String, nullable=False)
    parent_id = Column(String, nullable=False)
    device_ids = Column(JSON)
    restrictions = Column(JSON)
    time_limits = Column(JSON)
    safe_zones = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class ContentFilter(Base):
    """Фильтры контента"""

    __tablename__ = "content_filters"

    id = Column(String, primary_key=True)
    child_id = Column(String, nullable=False)
    category = Column(String, nullable=False)
    keywords = Column(JSON)
    domains = Column(JSON)
    action = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ActivityLog(Base):
    """Лог активности"""

    __tablename__ = "activity_logs"

    id = Column(String, primary_key=True)
    child_id = Column(String, nullable=False)
    device_id = Column(String, nullable=False)
    activity_type = Column(String, nullable=False)
    content_url = Column(String)
    content_category = Column(String)
    duration = Column(Integer)  # секунды
    timestamp = Column(DateTime, default=datetime.utcnow)
    location = Column(JSON)
    risk_score = Column(Float, default=0.0)


class ContentAnalysisResult(BaseModel):
    """Результат анализа контента"""

    url: str
    category: ContentCategory
    risk_score: float
    age_appropriate: bool
    keywords: List[str] = Field(default_factory=list)
    action: ControlAction
    reason: str


class ActivityAlert(BaseModel):
    """Оповещение о активности"""

    child_id: str
    alert_type: str
    severity: str
    message: str
    timestamp: datetime
    action_required: bool = False
    data: Dict[str, Any] = Field(default_factory=dict)


# ==================== ВАЛИДАЦИОННЫЕ МОДЕЛИ ====================


class ChildProfileData(BaseModel):
    """Валидационная модель для данных профиля ребенка"""

    name: str
    age: int
    parent_id: str
    time_limits: Optional[Dict[str, int]] = Field(default_factory=dict)
    restrictions: Optional[Dict[str, bool]] = Field(default_factory=dict)
    safe_zones: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    device_ids: Optional[List[str]] = Field(default_factory=list)

    @validator("name")
    def validate_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError("Имя должно содержать минимум 2 символа")
        return v.strip()

    @validator("age")
    def validate_age(cls, v):
        if not isinstance(v, int) or not 0 <= v <= 18:
            raise ValueError("Возраст должен быть целым числом от 0 до 18 лет")
        return v

    @validator("parent_id")
    def validate_parent_id(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError("ID родителя должен содержать минимум 3 символа")
        return v.strip()

    @validator("time_limits")
    def validate_time_limits(cls, v):
        if v:
            for device_type, minutes in v.items():
                if not isinstance(minutes, int) or minutes < 0:
                    raise ValueError(
                        f"Лимит времени для {device_type} должен быть "
                        f"неотрицательным числом"
                    )
        return v or {}


class ContentAnalysisRequest(BaseModel):
    """Валидационная модель для запроса анализа контента"""

    url: str
    child_id: str

    @validator("url")
    def validate_url(cls, v):
        if not v or not v.startswith(("http://", "https://")):
            raise ValueError("URL должен начинаться с http:// или https://")
        return v.strip()

    @validator("child_id")
    def validate_child_id(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError("ID ребенка должен содержать минимум 3 символа")
        return v.strip()


class TimeLimitData(BaseModel):
    """Валидационная модель для данных лимитов времени"""

    device_type: str
    minutes: int

    @validator("device_type")
    def validate_device_type(cls, v):
        valid_types = [
            "mobile",
            "tablet",
            "desktop",
            "smart_tv",
            "gaming_console",
            "smart_watch",
        ]
        if v not in valid_types:
            raise ValueError(
                f'Тип устройства должен быть одним из: '
                f'{", ".join(valid_types)}'
            )
        return v

    @validator("minutes")
    def validate_minutes(cls, v):
        if not isinstance(v, int) or v < 0 or v > 1440:  # Макс 24 часа
            raise ValueError(
                "Лимит времени должен быть от 0 до 1440 минут (24 часа)"
            )
        return v


class AlertData(BaseModel):
    """Валидационная модель для данных алерта"""

    child_id: str
    alert_type: str
    severity: str
    message: str
    data: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @validator("alert_type")
    def validate_alert_type(cls, v):
        valid_types = [
            "time_violation",
            "content_blocked",
            "suspicious_activity",
            "location_alert",
            "emergency",
        ]
        if v not in valid_types:
            raise ValueError(
                f'Тип алерта должен быть одним из: {", ".join(valid_types)}'
            )
        return v

    @validator("severity")
    def validate_severity(cls, v):
        valid_severities = ["low", "medium", "high", "critical"]
        if v not in valid_severities:
            raise ValueError(
                f'Уровень серьезности должен быть одним из: '
                f'{", ".join(valid_severities)}'
            )
        return v

    @validator("message")
    def validate_message(cls, v):
        if not v or len(v.strip()) < 5:
            raise ValueError("Сообщение должно содержать минимум 5 символов")
        return v.strip()


# ==================== ДЕКОРАТОРЫ ДЛЯ ОБРАБОТКИ ОШИБОК ====================


def error_handler(operation_name: str = "unknown"):
    """Декоратор для обработки ошибок с контекстом"""

    def decorator(func):
        @wraps(func)
        async def async_wrapper(self, *args, **kwargs):
            try:
                return await func(self, *args, **kwargs)
            except Exception as e:
                self._log_error_with_context(
                    e,
                    operation_name,
                    function_name=func.__name__,
                    args_count=len(args),
                    kwargs_keys=list(kwargs.keys()),
                    operation=operation_name,
                )
                raise

        @wraps(func)
        def sync_wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                self._log_error_with_context(
                    e,
                    operation_name,
                    function_name=func.__name__,
                    args_count=len(args),
                    kwargs_keys=list(kwargs.keys()),
                    operation=operation_name,
                )
                raise

        return (
            async_wrapper
            if asyncio.iscoroutinefunction(func)
            else sync_wrapper
        )

    return decorator


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Декоратор для повторных попыток при ошибках"""

    def decorator(func):
        @wraps(func)
        async def async_wrapper(self, *args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(self, *args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        self._log_with_context(
                            "warning",
                            f"Попытка {attempt + 1} неудачна, "
                            f"повтор через {delay}с",
                            function_name=func.__name__,
                            attempt=attempt + 1,
                            max_retries=max_retries,
                            error=str(e),
                        )
                        await asyncio.sleep(delay)
                    else:
                        self._log_error_with_context(
                            e,
                            f"{func.__name__}_retry_failed",
                            function_name=func.__name__,
                            attempts=max_retries,
                            operation="retry_on_failure",
                        )
            raise last_exception

        @wraps(func)
        def sync_wrapper(self, *args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        self._log_with_context(
                            "warning",
                            f"Попытка {attempt + 1} неудачна, "
                            f"повтор через {delay}с",
                            function_name=func.__name__,
                            attempt=attempt + 1,
                            max_retries=max_retries,
                            error=str(e),
                        )
                        time.sleep(delay)
                    else:
                        self._log_error_with_context(
                            e,
                            f"{func.__name__}_retry_failed",
                            function_name=func.__name__,
                            attempts=max_retries,
                            operation="retry_on_failure",
                        )
            raise last_exception

        return (
            async_wrapper
            if asyncio.iscoroutinefunction(func)
            else sync_wrapper
        )

    return decorator


# Prometheus метрики
content_blocks_total = Counter(
    "content_blocks_total",
    "Total number of content blocks",
    ["category", "age_group"],
)

time_limit_violations = Counter(
    "time_limit_violations_total",
    "Total number of time limit violations",
    ["child_id", "device_type"],
)

suspicious_activities = Counter(
    "suspicious_activities_total",
    "Total number of suspicious activities",
    ["child_id", "activity_type"],
)

active_children = Gauge(
    "active_children", "Number of children currently monitored"
)


class ParentalControlBot(SecurityBase):
    """
    Интеллектуальный бот родительского контроля

    Предоставляет комплексную систему родительского контроля с поддержкой:
    - Умной фильтрации контента
    - Контроля времени использования
    - Геолокации и безопасных зон
    - Мониторинга социальных сетей
    - Блокировки опасных приложений
    - Образовательных рекомендаций
    """

    def __init__(
        self,
        name: str = "ParentalControlBot",
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Инициализация ParentalControlBot

        Args:
            name: Имя бота
            config: Конфигурация
        """
        super().__init__(name, config)

        # Конфигурация по умолчанию
        self.default_config = {
            "redis_url": "redis://localhost:6379/0",
            "database_url": "sqlite:///parental_control_bot.db",
            "content_analysis_enabled": True,
            "location_tracking_enabled": True,
            "social_media_monitoring": True,
            "educational_recommendations": True,
            "ml_enabled": True,
            "adaptive_learning": True,
            "real_time_monitoring": True,
            "bedtime_mode": True,
            "emergency_alerts": True,
            "cleanup_interval": 300,
            "metrics_enabled": True,
            "logging_enabled": True,
        }

        # Объединение конфигураций
        self.config = {**self.default_config, **(config or {})}

        # Инициализация компонентов
        self.redis_client: Optional[redis.Redis] = None
        self.db_engine: Optional[sqlalchemy.Engine] = None
        self.db_session: Optional[sqlalchemy.orm.Session] = None
        self.child_profiles: Dict[str, ChildProfile] = {}
        self.active_monitoring: Dict[str, bool] = {}
        self.ml_model: Optional[IsolationForest] = None
        self.scaler: Optional[StandardScaler] = None

        # Статистика
        self.stats = {
            "total_children": 0,
            "active_children": 0,
            "content_blocks": 0,
            "time_violations": 0,
            "suspicious_activities": 0,
            "educational_recommendations": 0,
        }

        # Потоки
        self.monitoring_thread: Optional[threading.Thread] = None
        self.running = False

        # Блокировки
        self.lock = threading.RLock()

        # Инициализация менеджера конфигурации
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()

        # Обновляем конфигурацию из переданных параметров
        if config:
            for key, value in config.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
                elif key.startswith("database_"):
                    db_key = key.replace("database_", "")
                    if hasattr(self.config.database, db_key):
                        setattr(self.config.database, db_key, value)
                elif key.startswith("redis_"):
                    redis_key = key.replace("redis_", "")
                    if hasattr(self.config.redis, redis_key):
                        setattr(self.config.redis, redis_key, value)
                elif key.startswith("security_"):
                    security_key = key.replace("security_", "")
                    if hasattr(self.config.security, security_key):
                        setattr(self.config.security, security_key, value)
                elif key.startswith("monitoring_"):
                    monitoring_key = key.replace("monitoring_", "")
                    if hasattr(self.config.monitoring, monitoring_key):
                        setattr(self.config.monitoring, monitoring_key, value)
                elif key.startswith("notification_"):
                    notification_key = key.replace("notification_", "")
                    if hasattr(self.config.notification, notification_key):
                        setattr(
                            self.config.notification, notification_key, value
                        )
                elif key.startswith("cache_"):
                    cache_key = key.replace("cache_", "")
                    if hasattr(self.config.cache, cache_key):
                        setattr(self.config.cache, cache_key, value)
                elif key.startswith("logging_"):
                    logging_key = key.replace("logging_", "")
                    if hasattr(self.config.logging, logging_key):
                        setattr(self.config.logging, logging_key, value)

        # Инициализация кэш-менеджера
        self.cache_manager = CacheManager(
            logger=self.logger,
            max_size=self.config.cache.max_size,
            max_memory_mb=self.config.cache.max_memory_mb,
            strategy=CacheStrategy.LRU,
            default_ttl=timedelta(seconds=self.config.cache.default_ttl),
        )

        # Инициализация расширенного логгера
        self.advanced_logger = AdvancedLogger(
            name=f"parental_control_bot_{name}",
            log_level=LogLevel.INFO,
            log_file=self.config.logging.log_file,
            enable_console=self.config.logging.enable_console,
            enable_file=self.config.logging.enable_file,
            enable_metrics=self.config.logging.enable_metrics,
        )

        # Инициализация менеджера шифрования
        self.encryption_manager = EncryptionManager(
            logger=self.logger,
            master_password=self.config.security.encryption_master_password,
            default_algorithm=EncryptionAlgorithm.AES_256_GCM,
            key_rotation_days=(
                self.config.security.encryption_key_rotation_days
            ),
        )

        # Инициализация оптимизатора производительности
        self.performance_optimizer = PerformanceOptimizer(
            max_connections=self.config.database.pool_size
        )

        # Настройка улучшенного логирования
        self._setup_enhanced_logging()

        self.logger.info(f"ParentalControlBot {name} инициализирован")

    def _setup_enhanced_logging(self) -> None:
        """Настройка улучшенного логирования с контекстом"""
        try:
            # Настройка structlog
            structlog.configure(
                processors=[
                    structlog.stdlib.filter_by_level,
                    structlog.stdlib.add_logger_name,
                    structlog.stdlib.add_log_level,
                    structlog.stdlib.PositionalArgumentsFormatter(),
                    structlog.processors.TimeStamper(fmt="iso"),
                    structlog.processors.StackInfoRenderer(),
                    structlog.processors.format_exc_info,
                    structlog.processors.UnicodeDecoder(),
                    structlog.processors.JSONRenderer(),
                ],
                context_class=dict,
                logger_factory=structlog.stdlib.LoggerFactory(),
                wrapper_class=structlog.stdlib.BoundLogger,
                cache_logger_on_first_use=True,
            )

            # Создание контекстного логгера
            self.context_logger = structlog.get_logger().bind(
                component="parental_control_bot",
                bot_name=self.name,
                version="2.5",
            )

            # Настройка уровней логирования
            log_level = self.config.logging.level
            logging.basicConfig(
                level=getattr(logging, log_level.upper()),
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            )

        except Exception as e:
            # Fallback к стандартному логированию
            self.context_logger = self.logger
            self.logger.warning(f"Не удалось настроить enhanced logging: {e}")

    def _log_with_context(self, level: str, message: str, **kwargs) -> None:
        """Логирование с контекстом"""
        try:
            log_method = getattr(self.context_logger, level.lower())
            log_method(message, **kwargs)
        except Exception:
            # Fallback к стандартному логированию
            getattr(self.logger, level.lower())(
                f"{message} | Context: {kwargs}"
            )

    def _log_error_with_context(
        self, error: Exception, context: str, **kwargs
    ) -> None:
        """Логирование ошибок с контекстом"""
        try:
            self.context_logger.error(
                f"Ошибка в {context}: {str(error)}",
                error_type=type(error).__name__,
                error_message=str(error),
                context=context,
                **kwargs,
                exc_info=True,
            )
        except Exception:
            self.logger.error(
                f"Ошибка в {context}: {error} | Context: {kwargs}",
                exc_info=True,
            )

    async def start(self) -> bool:
        """Запуск бота родительского контроля"""
        try:
            with self.lock:
                if self.running:
                    self.logger.warning("ParentalControlBot уже запущен")
                    return True

                # Инициализация базы данных
                await self._setup_database()

                # Инициализация Redis
                await self._setup_redis()

                # Инициализация ML модели
                if self.config.monitoring.ml_enabled:
                    await self._setup_ml_model()

                # Загрузка профилей детей
                await self._load_child_profiles()

                # Запуск расширенного логирования
                await self.start_advanced_logging()

                # Запуск оптимизатора производительности
                self.performance_optimizer.start()

                # Запуск мониторинга
                self.running = True
                self.monitoring_thread = threading.Thread(
                    target=self._monitoring_worker
                )
                self.monitoring_thread.daemon = True
                self.monitoring_thread.start()

                self.logger.info("ParentalControlBot запущен успешно")
                return True

        except Exception as e:
            self._log_error_with_context(
                e,
                "start",
                operation="bot_startup",
                config_keys=list(self.config.to_dict().keys()),
            )
            return False

    async def stop(self) -> bool:
        """Остановка бота родительского контроля"""
        try:
            with self.lock:
                if not self.running:
                    self.logger.warning("ParentalControlBot уже остановлен")
                    return True

                self.running = False

                # Ожидание завершения потоков
                if (
                    self.monitoring_thread
                    and self.monitoring_thread.is_alive()
                ):
                    self.monitoring_thread.join(timeout=5)

                # Закрытие соединений
                if self.db_session:
                    self.db_session.close()

                if self.redis_client:
                    self.redis_client.close()

                # Остановка расширенного логирования
                await self.stop_advanced_logging()

                # Остановка оптимизатора производительности
                self.performance_optimizer.stop()

                self.logger.info("ParentalControlBot остановлен")
                return True

        except Exception as e:
            self.logger.error(f"Ошибка остановки ParentalControlBot: {e}")
            return False

    async def _setup_database(self) -> None:
        """Настройка базы данных"""
        try:
            database_url = self.config.database.url
            self.db_engine = create_engine(database_url)
            Base.metadata.create_all(self.db_engine)

            Session = sessionmaker(bind=self.db_engine)
            self.db_session = Session()

            self.logger.info("База данных ParentalControlBot настроена")

        except Exception as e:
            self.logger.error(f"Ошибка настройки базы данных: {e}")
            raise

    async def _setup_redis(self) -> None:
        """Настройка Redis"""
        try:
            redis_url = self.config.redis.url
            self.redis_client = redis.from_url(
                redis_url, decode_responses=True
            )

            # Тест соединения
            self.redis_client.ping()

            self.logger.info("Redis для ParentalControlBot настроен")

        except Exception as e:
            self.logger.error(f"Ошибка настройки Redis: {e}")
            raise

    async def _setup_ml_model(self) -> None:
        """Настройка ML модели для анализа контента"""
        try:
            self.ml_model = IsolationForest(
                contamination=0.1, random_state=42, n_estimators=100
            )
            self.scaler = StandardScaler()

            self.logger.info("ML модель ParentalControlBot настроена")

        except Exception as e:
            self.logger.error(f"Ошибка настройки ML модели: {e}")

    async def _load_child_profiles(self) -> None:
        """Загрузка профилей детей"""
        try:
            if self.db_session:
                profiles = self.db_session.query(ChildProfile).all()

                for profile in profiles:
                    self.child_profiles[profile.id] = profile
                    self.active_monitoring[profile.id] = True

                self.stats["total_children"] = len(self.child_profiles)
                self.stats["active_children"] = len(
                    [p for p in self.child_profiles.values() if p]
                )

                self.logger.info(
                    "Загружено {} профилей детей".format(
                        len(self.child_profiles)
                    )
                )

        except Exception as e:
            self.logger.error(f"Ошибка загрузки профилей детей: {e}")

    def _monitoring_worker(self) -> None:
        """Фоновый процесс мониторинга"""
        while self.running:
            try:
                time.sleep(1)  # Проверка каждую секунду

                # Обновление статистики
                self._update_stats()

                # Проверка нарушений времени
                self._check_time_violations()

                # Проверка подозрительной активности
                self._check_suspicious_activities()

            except Exception as e:
                self.logger.error(f"Ошибка в процессе мониторинга: {e}")

    def _update_stats(self) -> None:
        """Обновление статистики"""
        try:
            with self.lock:
                self.stats["active_children"] = len(
                    [p for p in self.child_profiles.values() if p]
                )
                active_children.set(self.stats["active_children"])

        except Exception as e:
            self.logger.error(f"Ошибка обновления статистики: {e}")

    def _check_time_violations(self) -> None:
        """Проверка нарушений времени использования"""
        try:
            for child_id, profile in self.child_profiles.items():
                if not self.active_monitoring.get(child_id, False):
                    continue

                # Проверка дневных лимитов
                daily_usage = self._get_daily_usage(child_id)
                time_limits = profile.time_limits or {}

                for device_type, limit_minutes in time_limits.items():
                    if daily_usage.get(device_type, 0) > limit_minutes:
                        self._handle_time_violation(
                            child_id,
                            device_type,
                            daily_usage[device_type],
                            limit_minutes,
                        )

        except Exception as e:
            self.logger.error(f"Ошибка проверки нарушений времени: {e}")

    def _check_suspicious_activities(self) -> None:
        """Проверка подозрительной активности"""
        try:
            # Здесь должна быть логика анализа подозрительной активности
            # Пока что заглушка
            pass

        except Exception as e:
            self.logger.error(
                f"Ошибка проверки подозрительной активности: {e}"
            )

    def _get_daily_usage(self, child_id: str) -> Dict[str, int]:
        """Получение дневного использования устройств"""
        try:
            if not self.db_session:
                return {}

            today = datetime.now().date()
            logs = (
                self.db_session.query(ActivityLog)
                .filter(
                    ActivityLog.child_id == child_id,
                    ActivityLog.timestamp >= today,
                )
                .all()
            )

            usage = defaultdict(int)
            for log in logs:
                device_type = log.device_id.split("_")[
                    0
                ]  # Предполагаем формат device_type_id
                usage[device_type] += log.duration or 0

            return dict(usage)

        except Exception as e:
            self.logger.error(f"Ошибка получения дневного использования: {e}")
            return {}

    def _handle_time_violation(
        self, child_id: str, device_type: str, current_usage: int, limit: int
    ) -> None:
        """Обработка нарушения времени использования"""
        try:
            # Создание оповещения
            alert = ActivityAlert(
                child_id=child_id,
                alert_type="time_violation",
                severity="medium",
                message=(
                    f"Превышен лимит времени использования {device_type}: "
                    f"{current_usage}м > {limit}м"
                ),
                timestamp=datetime.now(),
                action_required=True,
                data={
                    "device_type": device_type,
                    "current_usage": current_usage,
                    "limit": limit,
                },
            )

            # Отправка уведомления родителям
            self._send_parent_notification(alert)

            # Обновление статистики
            self.stats["time_violations"] += 1
            time_limit_violations.labels(
                child_id=child_id, device_type=device_type
            ).inc()

            self.logger.warning(
                f"Нарушение времени для {child_id}: {device_type}"
            )

        except Exception as e:
            self.logger.error(f"Ошибка обработки нарушения времени: {e}")

    def _send_parent_notification(self, alert: ActivityAlert) -> None:
        """Отправка уведомления родителям"""
        try:
            # Здесь должна быть интеграция с системой уведомлений
            # Пока что логируем
            self.logger.info(f"Уведомление родителям: {alert.message}")

            # Сохранение в Redis
            if self.redis_client:
                alert_data = {
                    "child_id": alert.child_id,
                    "alert_type": alert.alert_type,
                    "severity": alert.severity,
                    "message": alert.message,
                    "timestamp": alert.timestamp.isoformat(),
                    "action_required": alert.action_required,
                    "data": alert.data,
                }
                self.redis_client.lpush(
                    "parental_alerts", json.dumps(alert_data)
                )

        except Exception as e:
            self.logger.error(f"Ошибка отправки уведомления родителям: {e}")

    @error_handler("add_child_profile")
    @performance_monitor(PerformanceMetric.RESPONSE_TIME)
    async def add_child_profile(self, child_data: Dict[str, Any]) -> str:
        """Добавление профиля ребенка с валидацией данных"""
        try:
            # Валидация входных данных
            validated_data = ChildProfileData(**child_data)

            with self.lock:
                # Генерация ID
                child_id = self._generate_child_id()

                # Создание профиля с валидированными данными
                profile = ChildProfile(
                    id=child_id,
                    name=validated_data.name,
                    age=validated_data.age,
                    age_group=child_data.get(
                        "age_group",
                        self._determine_age_group(validated_data.age),
                    ),
                    parent_id=validated_data.parent_id,
                    device_ids=validated_data.device_ids,
                    restrictions=validated_data.restrictions,
                    time_limits=validated_data.time_limits,
                    safe_zones=validated_data.safe_zones,
                )

                # Сохранение в базу данных
                if self.db_session:
                    self.db_session.add(profile)
                    self.db_session.commit()

                # Добавление в память
                self.child_profiles[child_id] = profile
                self.active_monitoring[child_id] = True

                # Обновление статистики
                self.stats["total_children"] += 1
                self.stats["active_children"] += 1

                self._log_with_context(
                    "info",
                    "Профиль ребенка добавлен",
                    child_id=child_id,
                    child_name=validated_data.name,
                    child_age=validated_data.age,
                    parent_id=validated_data.parent_id,
                    operation="add_child_profile",
                )
                return child_id

        except Exception as e:
            self._log_error_with_context(
                e,
                "add_child_profile",
                child_data_keys=list(child_data.keys()) if child_data else [],
                operation="add_child_profile",
            )
            raise

    def _generate_child_id(self) -> str:
        """Генерация уникального ID ребенка"""
        timestamp = str(int(time.time() * 1000))
        random_part = hashlib.md5(
            f"{timestamp}{time.time()}".encode()
        ).hexdigest()[:8]
        return f"CHILD_{timestamp}_{random_part}"

    def _determine_age_group(self, age: int) -> str:
        """Определение возрастной группы"""
        if age <= 4:
            return AgeGroup.TODDLER.value
        elif age <= 6:
            return AgeGroup.PRESCHOOL.value
        elif age <= 12:
            return AgeGroup.ELEMENTARY.value
        elif age <= 18:
            return AgeGroup.TEEN.value
        else:
            return AgeGroup.ADULT.value

    @error_handler("analyze_content")
    @performance_monitor(PerformanceMetric.RESPONSE_TIME)
    @retry_on_failure(max_retries=2, delay=0.5)
    async def analyze_content(
        self, url: str, child_id: str
    ) -> ContentAnalysisResult:
        """Анализ контента для ребенка с валидацией данных и кэшированием"""
        try:
            # Валидация входных данных
            request_data = ContentAnalysisRequest(url=url, child_id=child_id)

            # Генерация ключа кэша
            cache_key = self.cache_manager.generate_key(
                "content_analysis",
                url=request_data.url,
                child_id=request_data.child_id,
            )

            # Попытка получить из кэша
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                self._log_with_context(
                    "info",
                    "Результат анализа контента получен из кэша",
                    url=url,
                    child_id=child_id,
                    cache_key=cache_key,
                )
                return ContentAnalysisResult(**cached_result)

            # Базовый анализ URL
            category = self._categorize_url(request_data.url)
            risk_score = self._calculate_risk_score(request_data.url, category)
            age_appropriate = self._is_age_appropriate(
                category, request_data.child_id
            )

            # Определение действия
            action = self._determine_action(
                category, risk_score, age_appropriate, child_id
            )

            # Обновление статистики
            if action == ControlAction.BLOCK:
                self.stats["content_blocks"] += 1
                profile = self.child_profiles.get(child_id)
                if profile:
                    content_blocks_total.labels(
                        category=category.value, age_group=profile.age_group
                    ).inc()

            result = ContentAnalysisResult(
                url=url,
                category=category,
                risk_score=risk_score,
                age_appropriate=age_appropriate,
                action=action,
                reason=self._get_action_reason(action, category, risk_score),
            )

            # Сохранение в кэш (TTL 30 минут для анализа контента)
            await self.cache_manager.set(
                cache_key,
                result.__dict__,
                ttl=timedelta(seconds=1800),  # 30 минут
            )

            # Логирование активности
            await self._log_activity(
                child_id, "content_access", url, category, result
            )

            return result

        except Exception as e:
            self.logger.error(f"Ошибка анализа контента: {e}")
            # Возвращаем безопасный результат
            return ContentAnalysisResult(
                url=url,
                category=ContentCategory.UNKNOWN,
                risk_score=1.0,
                age_appropriate=False,
                action=ControlAction.BLOCK,
                reason="Ошибка анализа контента",
            )

    def _categorize_url(self, url: str) -> ContentCategory:
        """Категоризация URL"""
        try:
            url_lower = url.lower()

            # Простая категоризация по ключевым словам
            if any(
                word in url_lower
                for word in ["youtube", "video", "entertainment"]
            ):
                return ContentCategory.ENTERTAINMENT
            elif any(
                word in url_lower
                for word in ["facebook", "instagram", "twitter", "social"]
            ):
                return ContentCategory.SOCIAL
            elif any(word in url_lower for word in ["game", "gaming", "play"]):
                return ContentCategory.GAMING
            elif any(
                word in url_lower
                for word in ["shop", "buy", "store", "amazon"]
            ):
                return ContentCategory.SHOPPING
            elif any(
                word in url_lower for word in ["news", "article", "blog"]
            ):
                return ContentCategory.NEWS
            elif any(word in url_lower for word in ["adult", "xxx", "porn"]):
                return ContentCategory.ADULT
            elif any(
                word in url_lower for word in ["violence", "fight", "war"]
            ):
                return ContentCategory.VIOLENCE
            elif any(
                word in url_lower for word in ["drug", "alcohol", "smoke"]
            ):
                return ContentCategory.DRUGS
            elif any(
                word in url_lower for word in ["gambling", "casino", "bet"]
            ):
                return ContentCategory.GAMBLING
            elif any(
                word in url_lower
                for word in ["edu", "learn", "school", "course"]
            ):
                return ContentCategory.EDUCATIONAL
            else:
                return ContentCategory.UNKNOWN

        except Exception as e:
            self.logger.error(f"Ошибка категоризации URL: {e}")
            return ContentCategory.UNKNOWN

    def _calculate_risk_score(
        self, url: str, category: ContentCategory
    ) -> float:
        """Расчет риска контента"""
        try:
            base_scores = {
                ContentCategory.EDUCATIONAL: 0.1,
                ContentCategory.ENTERTAINMENT: 0.3,
                ContentCategory.SOCIAL: 0.5,
                ContentCategory.GAMING: 0.4,
                ContentCategory.SHOPPING: 0.6,
                ContentCategory.NEWS: 0.2,
                ContentCategory.ADULT: 1.0,
                ContentCategory.VIOLENCE: 0.9,
                ContentCategory.DRUGS: 0.95,
                ContentCategory.GAMBLING: 0.8,
                ContentCategory.UNKNOWN: 0.7,
            }

            return base_scores.get(category, 0.5)

        except Exception as e:
            self.logger.error(f"Ошибка расчета риска: {e}")
            return 0.5

    def _is_age_appropriate(
        self, category: ContentCategory, child_id: str
    ) -> bool:
        """Проверка соответствия возрасту"""
        try:
            profile = self.child_profiles.get(child_id)
            if not profile:
                return False

            age_group = profile.age_group

            # Правила соответствия возрасту
            age_rules = {
                AgeGroup.TODDLER.value: [
                    ContentCategory.EDUCATIONAL,
                    ContentCategory.ENTERTAINMENT,
                ],
                AgeGroup.PRESCHOOL.value: [
                    ContentCategory.EDUCATIONAL,
                    ContentCategory.ENTERTAINMENT,
                    ContentCategory.GAMING,
                ],
                AgeGroup.ELEMENTARY.value: [
                    ContentCategory.EDUCATIONAL,
                    ContentCategory.ENTERTAINMENT,
                    ContentCategory.GAMING,
                    ContentCategory.SOCIAL,
                ],
                AgeGroup.TEEN.value: [
                    ContentCategory.EDUCATIONAL,
                    ContentCategory.ENTERTAINMENT,
                    ContentCategory.GAMING,
                    ContentCategory.SOCIAL,
                    ContentCategory.NEWS,
                    ContentCategory.SHOPPING,
                ],
                AgeGroup.ADULT.value: [cat for cat in ContentCategory],
            }

            allowed_categories = age_rules.get(age_group, [])
            return category in allowed_categories

        except Exception as e:
            self.logger.error(f"Ошибка проверки соответствия возрасту: {e}")
            return False

    def _determine_action(
        self,
        category: ContentCategory,
        risk_score: float,
        age_appropriate: bool,
        child_id: str,
    ) -> ControlAction:
        """Определение действия по контенту"""
        try:
            profile = self.child_profiles.get(child_id)
            if not profile:
                return ControlAction.BLOCK

            # Высокий риск - блокировка
            if risk_score >= 0.8:
                return ControlAction.BLOCK

            # Не подходит по возрасту - блокировка
            if not age_appropriate:
                return ControlAction.BLOCK

            # Средний риск - предупреждение
            if risk_score >= 0.5:
                return ControlAction.WARN

            # Низкий риск - разрешение
            return ControlAction.ALLOW

        except Exception as e:
            self.logger.error(f"Ошибка определения действия: {e}")
            return ControlAction.BLOCK

    def _get_action_reason(
        self,
        action: ControlAction,
        category: ContentCategory,
        risk_score: float,
    ) -> str:
        """Получение причины действия"""
        try:
            if action == ControlAction.BLOCK:
                if risk_score >= 0.8:
                    return f"Высокий риск контента ({risk_score:.2f})"
                else:
                    return "Контент не подходит по возрасту"
            elif action == ControlAction.WARN:
                return f"Средний риск контента ({risk_score:.2f})"
            else:
                return "Контент безопасен"

        except Exception as e:
            self.logger.error(f"Ошибка получения причины действия: {e}")
            return "Неизвестная причина"

    async def _log_activity(
        self,
        child_id: str,
        activity_type: str,
        content_url: str,
        category: ContentCategory,
        result: ContentAnalysisResult,
    ) -> None:
        """Логирование активности"""
        try:
            if not self.db_session:
                return

            log = ActivityLog(
                id=self._generate_activity_id(),
                child_id=child_id,
                device_id="unknown",  # Должно передаваться извне
                activity_type=activity_type,
                content_url=content_url,
                content_category=category.value,
                duration=0,  # Для доступа к контенту
                risk_score=result.risk_score,
            )

            self.db_session.add(log)
            self.db_session.commit()

        except Exception as e:
            self.logger.error(f"Ошибка логирования активности: {e}")

    def _generate_activity_id(self) -> str:
        """Генерация ID активности"""
        timestamp = str(int(time.time() * 1000))
        random_part = hashlib.md5(
            f"{timestamp}{time.time()}".encode()
        ).hexdigest()[:8]
        return f"ACT_{timestamp}_{random_part}"

    async def get_child_status(
        self, child_id: str
    ) -> Optional[Dict[str, Any]]:
        """Получение статуса ребенка с кэшированием"""
        try:
            # Генерация ключа кэша
            cache_key = self.cache_manager.generate_key(
                "child_status", child_id=child_id
            )

            # Попытка получить из кэша
            cached_status = await self.cache_manager.get(cache_key)
            if cached_status:
                self._log_with_context(
                    "info",
                    "Статус ребенка получен из кэша",
                    child_id=child_id,
                    cache_key=cache_key,
                )
                return cached_status

            profile = self.child_profiles.get(child_id)
            if not profile:
                return None

            # Получение дневной статистики
            daily_usage = self._get_daily_usage(child_id)

            status = {
                "child_id": child_id,
                "name": profile.name,
                "age": profile.age,
                "age_group": profile.age_group,
                "is_monitored": self.active_monitoring.get(child_id, False),
                "daily_usage": daily_usage,
                "time_limits": profile.time_limits or {},
                "restrictions": profile.restrictions or {},
                "safe_zones": profile.safe_zones or [],
                "last_update": (
                    profile.updated_at.isoformat()
                    if profile.updated_at
                    else None
                ),
            }

            # Сохранение в кэш (TTL 5 минут для статуса)
            await self.cache_manager.set(
                cache_key, status, ttl=timedelta(seconds=300)  # 5 минут
            )

            return status

        except Exception as e:
            self.logger.error(f"Ошибка получения статуса ребенка: {e}")
            return None

    async def get_status(self) -> Dict[str, Any]:
        """Получение статуса бота"""
        try:
            return {
                "name": self.name,
                "status": "running" if self.running else "stopped",
                "config": self.config,
                "stats": self.stats,
                "children_monitored": len(self.child_profiles),
                "active_monitoring": len(
                    [m for m in self.active_monitoring.values() if m]
                ),
                "ml_enabled": self.config.monitoring.ml_enabled,
                "last_update": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Ошибка получения статуса: {e}")
            return {"error": str(e)}

    # ==================== МЕТОДЫ УПРАВЛЕНИЯ КЭШЕМ ====================

    async def clear_cache(self) -> bool:
        """Очистка всего кэша"""
        try:
            result = await self.cache_manager.clear()
            self._log_with_context("info", "Кэш очищен")
            return result
        except Exception as e:
            self._log_error_with_context(e, "clear_cache")
            return False

    async def invalidate_child_cache(self, child_id: str) -> int:
        """Инвалидация кэша для конкретного ребенка"""
        try:
            # Инвалидация статуса ребенка
            status_pattern = f"child_status|{child_id}*"
            status_count = await self.cache_manager.invalidate_pattern(
                status_pattern
            )

            # Инвалидация анализа контента для ребенка
            content_pattern = f"content_analysis|*|{child_id}"
            content_count = await self.cache_manager.invalidate_pattern(
                content_pattern
            )

            total_count = status_count + content_count
            self._log_with_context(
                "info",
                f"Инвалидирован кэш для ребенка {child_id}",
                child_id=child_id,
                invalidated_count=total_count,
            )
            return total_count
        except Exception as e:
            self._log_error_with_context(
                e, "invalidate_child_cache", child_id=child_id
            )
            return 0

    async def get_cache_stats(self) -> Dict[str, Any]:
        """Получение статистики кэша"""
        try:
            stats = await self.cache_manager.get_stats()
            memory_usage = await self.cache_manager.get_memory_usage()

            return {
                "cache_stats": {
                    "total_entries": stats.total_entries,
                    "hit_count": stats.hit_count,
                    "miss_count": stats.miss_count,
                    "hit_ratio": stats.hit_ratio,
                    "eviction_count": stats.eviction_count,
                },
                "memory_usage": memory_usage,
                "strategy": self.cache_manager.strategy.value,
                "max_size": self.cache_manager.max_size,
                "max_memory_mb": self.cache_manager.max_memory_bytes
                // (1024 * 1024),
            }
        except Exception as e:
            self._log_error_with_context(e, "get_cache_stats")
            return {"error": str(e)}

    async def cleanup_expired_cache(self) -> int:
        """Очистка истекших записей кэша"""
        try:
            count = await self.cache_manager.cleanup_expired()
            if count > 0:
                self._log_with_context(
                    "info",
                    f"Очищено {count} истекших записей кэша",
                    expired_count=count,
                )
            return count
        except Exception as e:
            self._log_error_with_context(e, "cleanup_expired_cache")
            return 0

    async def warm_up_cache(self) -> bool:
        """Прогрев кэша часто используемыми данными"""
        try:
            self._log_with_context("info", "Начинаем прогрев кэша")

            # Прогрев статусов всех детей
            for child_id in self.child_profiles.keys():
                await self.get_child_status(child_id)

            # Прогрев популярных URL для анализа
            popular_urls = [
                "https://youtube.com",
                "https://google.com",
                "https://wikipedia.org",
                "https://khanacademy.org",
            ]

            for url in popular_urls:
                for child_id in list(self.child_profiles.keys())[
                    :3
                ]:  # Первые 3 ребенка
                    await self.analyze_content(url, child_id)

            self._log_with_context("info", "Прогрев кэша завершен")
            return True
        except Exception as e:
            self._log_error_with_context(e, "warm_up_cache")
            return False

    # ==================== РАСШИРЕННОЕ ЛОГИРОВАНИЕ ====================

    def _create_log_context(
        self, operation: str, child_id: Optional[str] = None, **kwargs
    ) -> LogContext:
        """Создание контекста для логирования"""
        return LogContext(
            component="parental_control_bot",
            operation=operation,
            child_id=child_id,
            **kwargs,
        )

    def log_operation_start(
        self, operation: str, child_id: Optional[str] = None, **kwargs
    ) -> LogContext:
        """Логирование начала операции"""
        context = self._create_log_context(operation, child_id, **kwargs)
        self.advanced_logger.log_operation_start(
            operation, "parental_control_bot", child_id=child_id, **kwargs
        )
        return context

    def log_operation_end(
        self, context: LogContext, duration: float, success: bool = True
    ):
        """Логирование завершения операции"""
        self.advanced_logger.log_operation_end(context, duration, success)

    def log_security_event(
        self,
        event_type: str,
        severity: str,
        child_id: Optional[str] = None,
        **kwargs,
    ):
        """Логирование события безопасности"""
        self.advanced_logger.log_security_event(
            event_type, severity, child_id, **kwargs
        )

    def log_user_action(
        self, action: str, child_id: str, user_id: str, **kwargs
    ):
        """Логирование действия пользователя"""
        self.advanced_logger.log_user_action(
            action, child_id, user_id, **kwargs
        )

    def log_performance_metric(
        self,
        operation: str,
        duration: float,
        child_id: Optional[str] = None,
        **kwargs,
    ):
        """Логирование метрики производительности"""
        self.advanced_logger.log_performance(
            operation,
            "parental_control_bot",
            duration,
            child_id=child_id,
            **kwargs,
        )

    def log_content_analysis(
        self, url: str, child_id: str, result: str, **kwargs
    ):
        """Логирование анализа контента"""
        context = self._create_log_context("content_analysis", child_id)
        self.advanced_logger.info(
            f"Анализ контента: {url} -> {result}",
            context,
            url=url,
            result=result,
            **kwargs,
        )

    def log_time_violation(
        self, child_id: str, device_type: str, duration: int, limit: int
    ):
        """Логирование нарушения времени"""
        self.log_security_event(
            "time_violation",
            "medium",
            child_id=child_id,
            device_type=device_type,
            duration=duration,
            limit=limit,
        )

    def log_content_block(
        self, child_id: str, url: str, category: str, reason: str
    ):
        """Логирование блокировки контента"""
        self.log_security_event(
            "content_block",
            "high",
            child_id=child_id,
            url=url,
            category=category,
            reason=reason,
        )

    def log_suspicious_activity(
        self, child_id: str, activity_type: str, details: Dict[str, Any]
    ):
        """Логирование подозрительной активности"""
        self.log_security_event(
            "suspicious_activity",
            "high",
            child_id=child_id,
            activity_type=activity_type,
            details=details,
        )

    def log_emergency_alert(
        self, child_id: str, alert_type: str, message: str, **kwargs
    ):
        """Логирование экстренного алерта"""
        self.log_security_event(
            "emergency_alert",
            "critical",
            child_id=child_id,
            alert_type=alert_type,
            message=message,
            **kwargs,
        )

    def log_system_health(self, component: str, status: str, **kwargs):
        """Логирование состояния системы"""
        self.advanced_logger.log_system_event(
            f"Система {component}: {status}",
            component,
            status=status,
            **kwargs,
        )

    def log_cache_operation(
        self, operation: str, key: str, hit: bool, **kwargs
    ):
        """Логирование операций кэша"""
        context = self._create_log_context("cache_operation")
        self.advanced_logger.debug(
            f"Кэш {operation}: {key} ({'hit' if hit else 'miss'})",
            context,
            operation=operation,
            key=key,
            hit=hit,
            **kwargs,
        )

    def log_database_operation(
        self, operation: str, table: str, duration: float, **kwargs
    ):
        """Логирование операций базы данных"""
        self.log_performance_metric(
            f"db_{operation}", duration, table=table, **kwargs
        )

    def log_api_request(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        duration: float,
        **kwargs,
    ):
        """Логирование API запросов"""
        context = self._create_log_context("api_request")
        self.advanced_logger.info(
            f"API {method} {endpoint} -> {status_code}",
            context,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            duration=duration,
            **kwargs,
        )

    def log_ml_prediction(
        self,
        model: str,
        input_data: Dict[str, Any],
        prediction: Any,
        confidence: float,
    ):
        """Логирование ML предсказаний"""
        context = self._create_log_context("ml_prediction")
        self.advanced_logger.info(
            f"ML предсказание: {model}",
            context,
            model=model,
            prediction=prediction,
            confidence=confidence,
            input_size=len(str(input_data)),
        )

    def log_configuration_change(
        self, parameter: str, old_value: Any, new_value: Any, user_id: str
    ):
        """Логирование изменений конфигурации"""
        context = self._create_log_context("config_change", user_id=user_id)
        self.advanced_logger.warning(
            f"Изменение конфигурации: {parameter}",
            context,
            parameter=parameter,
            old_value=old_value,
            new_value=new_value,
            user_id=user_id,
        )

    def get_logging_metrics(self) -> Dict[str, Any]:
        """Получение метрик логирования"""
        return self.advanced_logger.get_metrics()

    async def export_logs(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        level: Optional[LogLevel] = None,
        component: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Экспорт логов с фильтрацией"""
        return self.advanced_logger.export_logs(
            start_time, end_time, level, component
        )

    async def cleanup_logs(self, days: int = 30):
        """Очистка старых логов"""
        self.advanced_logger.cleanup_old_logs(days)

    def set_log_level(self, level: LogLevel):
        """Изменение уровня логирования"""
        self.advanced_logger.set_log_level(level)

    async def start_advanced_logging(self):
        """Запуск расширенного логирования"""
        await self.advanced_logger.start_buffer_processor()

    async def stop_advanced_logging(self):
        """Остановка расширенного логирования"""
        await self.advanced_logger.stop_buffer_processor()

    # ==================== МЕТОДЫ ШИФРОВАНИЯ ====================

    async def encrypt_child_data(
        self, child_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Шифрование данных ребенка"""
        try:
            encrypted_data = {}

            # Поля, которые нужно зашифровать
            sensitive_fields = [
                "name",
                "parent_id",
                "safe_zones",
                "restrictions",
            ]

            for key, value in data.items():
                if key in sensitive_fields and value is not None:
                    # Шифрование чувствительного поля
                    encrypted_field = (
                        await self.encryption_manager.encrypt_sensitive_field(
                            key, value, child_id
                        )
                    )
                    encrypted_data[f"{key}_encrypted"] = {
                        "data": base64.b64encode(encrypted_field.data).decode(
                            "utf-8"
                        ),
                        "key_id": encrypted_field.key_id,
                        "algorithm": encrypted_field.algorithm.value,
                        "iv": (
                            base64.b64encode(encrypted_field.iv).decode(
                                "utf-8"
                            )
                            if encrypted_field.iv
                            else None
                        ),
                        "tag": (
                            base64.b64encode(encrypted_field.tag).decode(
                                "utf-8"
                            )
                            if encrypted_field.tag
                            else None
                        ),
                        "metadata": encrypted_field.metadata,
                    }
                else:
                    # Обычные поля остаются без изменений
                    encrypted_data[key] = value

            return encrypted_data

        except Exception as e:
            self._log_error_with_context(
                e, "encrypt_child_data", child_id=child_id
            )
            return data  # Возвращаем исходные данные при ошибке

    async def decrypt_child_data(
        self, child_id: str, encrypted_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Расшифровка данных ребенка"""
        try:
            decrypted_data = {}

            for key, value in encrypted_data.items():
                if key.endswith("_encrypted") and isinstance(value, dict):
                    # Расшифровка чувствительного поля
                    try:
                        encrypted_field = EncryptedData(
                            data=base64.b64decode(value["data"]),
                            key_id=value["key_id"],
                            algorithm=EncryptionAlgorithm(value["algorithm"]),
                            iv=(
                                base64.b64decode(value["iv"])
                                if value["iv"]
                                else None
                            ),
                            tag=(
                                base64.b64decode(value["tag"])
                                if value["tag"]
                                else None
                            ),
                            metadata=value.get("metadata"),
                        )

                        field_name, decrypted_value = (
                            await self.encryption_manager
                            .decrypt_sensitive_field(
                                encrypted_field
                            )
                        )

                        # Убираем суффикс _encrypted
                        original_key = key.replace("_encrypted", "")
                        decrypted_data[original_key] = decrypted_value

                    except Exception as e:
                        self.logger.warning(
                            f"Не удалось расшифровать поле {key}: {e}"
                        )
                        decrypted_data[key] = value
                else:
                    # Обычные поля остаются без изменений
                    decrypted_data[key] = value

            return decrypted_data

        except Exception as e:
            self._log_error_with_context(
                e, "decrypt_child_data", child_id=child_id
            )
            return encrypted_data  # Возвращаем исходные данные при ошибке

    async def encrypt_profile(self, profile: "ChildProfile") -> "ChildProfile":
        """Шифрование профиля ребенка"""
        try:
            # Создаем копию профиля
            encrypted_profile = ChildProfile(
                id=profile.id,
                name=profile.name,  # Имя незашифрованным для поиска
                age=profile.age,
                age_group=profile.age_group,
                parent_id=profile.parent_id,  # ID родителя незашифрованным
                device_ids=profile.device_ids,
                restrictions=profile.restrictions,
                time_limits=profile.time_limits,
                safe_zones=profile.safe_zones,
                created_at=profile.created_at,
                updated_at=profile.updated_at,
            )

            # Шифруем чувствительные данные
            if profile.safe_zones:
                encrypted_zones = []
                for zone in profile.safe_zones:
                    if isinstance(zone, dict):
                        encrypted_zone = (
                            await self.encryption_manager.encrypt_data(zone)
                        )
                        encrypted_zones.append(
                            {
                                "encrypted_data": base64.b64encode(
                                    encrypted_zone.data
                                ).decode("utf-8"),
                                "key_id": encrypted_zone.key_id,
                                "algorithm": encrypted_zone.algorithm.value,
                                "iv": (
                                    base64.b64encode(encrypted_zone.iv).decode(
                                        "utf-8"
                                    )
                                    if encrypted_zone.iv
                                    else None
                                ),
                                "tag": (
                                    base64.b64encode(
                                        encrypted_zone.tag
                                    ).decode("utf-8")
                                    if encrypted_zone.tag
                                    else None
                                ),
                            }
                        )
                    else:
                        encrypted_zones.append(zone)
                encrypted_profile.safe_zones = encrypted_zones

            return encrypted_profile

        except Exception as e:
            self._log_error_with_context(
                e, "encrypt_profile", child_id=profile.id
            )
            return profile  # Возвращаем исходный профиль при ошибке

    async def decrypt_profile(
        self, encrypted_profile: "ChildProfile"
    ) -> "ChildProfile":
        """Расшифровка профиля ребенка"""
        try:
            # Создаем копию профиля
            decrypted_profile = ChildProfile(
                id=encrypted_profile.id,
                name=encrypted_profile.name,
                age=encrypted_profile.age,
                age_group=encrypted_profile.age_group,
                parent_id=encrypted_profile.parent_id,
                device_ids=encrypted_profile.device_ids,
                restrictions=encrypted_profile.restrictions,
                time_limits=encrypted_profile.time_limits,
                safe_zones=encrypted_profile.safe_zones,
                created_at=encrypted_profile.created_at,
                updated_at=encrypted_profile.updated_at,
            )

            # Расшифровываем чувствительные данные
            if encrypted_profile.safe_zones:
                decrypted_zones = []
                for zone in encrypted_profile.safe_zones:
                    if isinstance(zone, dict) and "encrypted_data" in zone:
                        try:
                            encrypted_data = EncryptedData(
                                data=base64.b64decode(zone["encrypted_data"]),
                                key_id=zone["key_id"],
                                algorithm=EncryptionAlgorithm(
                                    zone["algorithm"]
                                ),
                                iv=(
                                    base64.b64decode(zone["iv"])
                                    if zone["iv"]
                                    else None
                                ),
                                tag=(
                                    base64.b64decode(zone["tag"])
                                    if zone["tag"]
                                    else None
                                ),
                            )

                            decrypted_zone = (
                                await self.encryption_manager.decrypt_data(
                                    encrypted_data
                                )
                            )
                            decrypted_zones.append(decrypted_zone)

                        except Exception as e:
                            self.logger.warning(
                                f"Не удалось расшифровать зону: {e}"
                            )
                            decrypted_zones.append(zone)
                    else:
                        decrypted_zones.append(zone)
                decrypted_profile.safe_zones = decrypted_zones

            return decrypted_profile

        except Exception as e:
            self._log_error_with_context(
                e, "decrypt_profile", child_id=encrypted_profile.id
            )
            return encrypted_profile  # Возвращаем исходный профиль при ошибке

    async def encrypt_alert_data(
        self, alert: "ActivityAlert"
    ) -> "ActivityAlert":
        """Шифрование данных алерта"""
        try:
            # Создаем копию алерта
            encrypted_alert = ActivityAlert(
                id=alert.id,
                child_id=alert.child_id,
                alert_type=alert.alert_type,
                severity=alert.severity,
                message=alert.message,
                timestamp=alert.timestamp,
                action_required=alert.action_required,
                data=alert.data,
            )

            # Шифруем чувствительные данные в data
            if alert.data and isinstance(alert.data, dict):
                encrypted_data = await self.encryption_manager.encrypt_data(
                    alert.data
                )
                encrypted_alert.data = {
                    "encrypted_data": base64.b64encode(
                        encrypted_data.data
                    ).decode("utf-8"),
                    "key_id": encrypted_data.key_id,
                    "algorithm": encrypted_data.algorithm.value,
                    "iv": (
                        base64.b64encode(encrypted_data.iv).decode("utf-8")
                        if encrypted_data.iv
                        else None
                    ),
                    "tag": (
                        base64.b64encode(encrypted_data.tag).decode("utf-8")
                        if encrypted_data.tag
                        else None
                    ),
                }

            return encrypted_alert

        except Exception as e:
            self._log_error_with_context(
                e, "encrypt_alert_data", alert_id=alert.id
            )
            return alert  # Возвращаем исходный алерт при ошибке

    async def decrypt_alert_data(
        self, encrypted_alert: "ActivityAlert"
    ) -> "ActivityAlert":
        """Расшифровка данных алерта"""
        try:
            # Создаем копию алерта
            decrypted_alert = ActivityAlert(
                id=encrypted_alert.id,
                child_id=encrypted_alert.child_id,
                alert_type=encrypted_alert.alert_type,
                severity=encrypted_alert.severity,
                message=encrypted_alert.message,
                timestamp=encrypted_alert.timestamp,
                action_required=encrypted_alert.action_required,
                data=encrypted_alert.data,
            )

            # Расшифровываем данные
            if (
                encrypted_alert.data
                and isinstance(encrypted_alert.data, dict)
                and "encrypted_data" in encrypted_alert.data
            ):
                try:
                    encrypted_data = EncryptedData(
                        data=base64.b64decode(
                            encrypted_alert.data["encrypted_data"]
                        ),
                        key_id=encrypted_alert.data["key_id"],
                        algorithm=EncryptionAlgorithm(
                            encrypted_alert.data["algorithm"]
                        ),
                        iv=(
                            base64.b64decode(encrypted_alert.data["iv"])
                            if encrypted_alert.data["iv"]
                            else None
                        ),
                        tag=(
                            base64.b64decode(encrypted_alert.data["tag"])
                            if encrypted_alert.data["tag"]
                            else None
                        ),
                    )

                    decrypted_data = (
                        await self.encryption_manager.decrypt_data(
                            encrypted_data
                        )
                    )
                    decrypted_alert.data = decrypted_data

                except Exception as e:
                    self.logger.warning(
                        f"Не удалось расшифровать данные алерта: {e}"
                    )
                    decrypted_alert.data = encrypted_alert.data

            return decrypted_alert

        except Exception as e:
            self._log_error_with_context(
                e, "decrypt_alert_data", alert_id=encrypted_alert.id
            )
            return encrypted_alert  # Возвращаем исходный алерт при ошибке

    def hash_parent_password(self, password: str) -> Tuple[str, bytes]:
        """Хэширование пароля родителя"""
        return self.encryption_manager.hash_password(password)

    def verify_parent_password(
        self, password: str, stored_hash: str, salt: bytes
    ) -> bool:
        """Проверка пароля родителя"""
        return self.encryption_manager.verify_password(
            password, stored_hash, salt
        )

    async def encrypt_file(
        self, file_path: str, output_path: Optional[str] = None
    ) -> str:
        """Шифрование файла"""
        return await self.encryption_manager.encrypt_file(
            file_path, output_path
        )

    async def decrypt_file(
        self, encrypted_file_path: str, output_path: Optional[str] = None
    ) -> str:
        """Расшифровка файла"""
        return await self.encryption_manager.decrypt_file(
            encrypted_file_path, output_path
        )

    def get_encryption_stats(self) -> Dict[str, Any]:
        """Получение статистики шифрования"""
        return self.encryption_manager.get_encryption_stats()

    async def rotate_encryption_keys(self) -> bool:
        """Ротация ключей шифрования"""
        try:
            await self.encryption_manager._rotate_key()
            self.logger.info("Ключи шифрования повернуты")
            return True
        except Exception as e:
            self._log_error_with_context(e, "rotate_encryption_keys")
            return False

    async def cleanup_expired_keys(self) -> int:
        """Очистка истекших ключей"""
        return await self.encryption_manager.cleanup_expired_keys()

    async def export_encryption_key(self, key_id: str, password: str) -> str:
        """Экспорт ключа шифрования"""
        return await self.encryption_manager.export_key(key_id, password)

    async def import_encryption_key(
        self, exported_key: str, password: str
    ) -> str:
        """Импорт ключа шифрования"""
        return await self.encryption_manager.import_key(exported_key, password)

    # ==================== МЕТОДЫ КОНФИГУРАЦИИ ====================

    def get_config(self) -> ParentalControlConfig:
        """Получить текущую конфигурацию."""
        return self.config

    def update_config(self, config_updates: Dict[str, Any]) -> bool:
        """
        Обновить конфигурацию.

        Args:
            config_updates: Словарь с обновлениями конфигурации

        Returns:
            True если обновление успешно
        """
        try:
            for key, value in config_updates.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
                elif key.startswith("database_"):
                    db_key = key.replace("database_", "")
                    if hasattr(self.config.database, db_key):
                        setattr(self.config.database, db_key, value)
                elif key.startswith("redis_"):
                    redis_key = key.replace("redis_", "")
                    if hasattr(self.config.redis, redis_key):
                        setattr(self.config.redis, redis_key, value)
                elif key.startswith("security_"):
                    security_key = key.replace("security_", "")
                    if hasattr(self.config.security, security_key):
                        setattr(self.config.security, security_key, value)
                elif key.startswith("monitoring_"):
                    monitoring_key = key.replace("monitoring_", "")
                    if hasattr(self.config.monitoring, monitoring_key):
                        setattr(self.config.monitoring, monitoring_key, value)
                elif key.startswith("notification_"):
                    notification_key = key.replace("notification_", "")
                    if hasattr(self.config.notification, notification_key):
                        setattr(
                            self.config.notification, notification_key, value
                        )
                elif key.startswith("cache_"):
                    cache_key = key.replace("cache_", "")
                    if hasattr(self.config.cache, cache_key):
                        setattr(self.config.cache, cache_key, value)
                elif key.startswith("logging_"):
                    logging_key = key.replace("logging_", "")
                    if hasattr(self.config.logging, logging_key):
                        setattr(self.config.logging, logging_key, value)

            self.logger.info("Конфигурация обновлена")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка обновления конфигурации: {e}")
            return False

    def save_config(
        self, config_path: str, format: ConfigFormat = ConfigFormat.YAML
    ) -> bool:
        """
        Сохранить конфигурацию в файл.

        Args:
            config_path: Путь для сохранения
            format: Формат файла

        Returns:
            True если сохранение успешно
        """
        try:
            success = self.config_manager.save_config(
                self.config, config_path, format
            )
            if success:
                self.logger.info(f"Конфигурация сохранена в {config_path}")
            return success
        except Exception as e:
            self.logger.error(f"Ошибка сохранения конфигурации: {e}")
            return False

    def load_config(self, config_path: str) -> bool:
        """
        Загрузить конфигурацию из файла.

        Args:
            config_path: Путь к файлу конфигурации

        Returns:
            True если загрузка успешна
        """
        try:
            self.config = self.config_manager.load_config(config_path)
            self.logger.info(f"Конфигурация загружена из {config_path}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка загрузки конфигурации: {e}")
            return False

    def validate_config(self) -> List[str]:
        """
        Валидировать текущую конфигурацию.

        Returns:
            Список ошибок валидации
        """
        return self.config_manager.validate_config(self.config)

    def get_config_schema(self) -> Dict[str, Any]:
        """
        Получить схему конфигурации.

        Returns:
            JSON схема конфигурации
        """
        return self.config_manager.get_config_schema()

    def reload_config(self) -> bool:
        """
        Перезагрузить конфигурацию из файла.

        Returns:
            True если перезагрузка успешна
        """
        try:
            if (
                hasattr(self, "config_manager")
                and self.config_manager.config_path
            ):
                self.config = self.config_manager.load_config()
                self.logger.info("Конфигурация перезагружена")
                return True
            else:
                self.logger.warning("Путь к конфигурации не установлен")
                return False
        except Exception as e:
            self.logger.error(f"Ошибка перезагрузки конфигурации: {e}")
            return False

    def export_config(
        self, output_path: str, format: ConfigFormat = ConfigFormat.YAML
    ) -> bool:
        """
        Экспортировать конфигурацию в файл.

        Args:
            output_path: Путь для экспорта
            format: Формат файла

        Returns:
            True если экспорт успешен
        """
        try:
            success = self.config_manager.save_config(
                self.config, output_path, format
            )
            if success:
                self.logger.info(
                    f"Конфигурация экспортирована в {output_path}"
                )
            return success
        except Exception as e:
            self.logger.error(f"Ошибка экспорта конфигурации: {e}")
            return False

    def get_config_summary(self) -> Dict[str, Any]:
        """
        Получить краткую сводку конфигурации.

        Returns:
            Словарь с основными настройками
        """
        return {
            "bot_name": self.config.bot_name,
            "version": self.config.version,
            "debug": self.config.debug,
            "database_url": self.config.database.url,
            "redis_url": self.config.redis.url,
            "encryption_enabled": bool(
                self.config.security.encryption_master_password
            ),
            "content_analysis_enabled": (
                self.config.monitoring.content_analysis_enabled
            ),
            "ml_enabled": self.config.monitoring.ml_enabled,
            "email_notifications": self.config.notification.email_enabled,
            "sms_notifications": self.config.notification.sms_enabled,
            "cache_size": self.config.cache.max_size,
            "log_level": self.config.logging.level,
            "cleanup_interval": self.config.cleanup_interval,
        }

    # ==================== МЕТОДЫ ПРОИЗВОДИТЕЛЬНОСТИ ====================

    def get_performance_stats(self) -> Dict[str, Any]:
        """Получить статистику производительности."""
        return self.performance_optimizer.get_performance_stats()

    def get_slow_queries(self, threshold: float = 1.0) -> List[Dict[str, Any]]:
        """Получить список медленных запросов."""
        return self.performance_optimizer.get_slow_queries(threshold)

    def optimize_memory(self) -> Dict[str, Any]:
        """Оптимизировать использование памяти."""
        return self.performance_optimizer.optimize_memory()

    def cleanup_performance_cache(self) -> int:
        """Очистить кэш производительности."""
        return self.performance_optimizer.cleanup_cache()

    def get_connection_from_pool(self) -> Optional[Any]:
        """Получить соединение из пула."""
        return self.performance_optimizer.get_connection()

    def return_connection_to_pool(self, connection: Any) -> None:
        """Вернуть соединение в пул."""
        self.performance_optimizer.return_connection(connection)

    def cache_performance_data(
        self, key: str, data: Any, ttl: int = 300
    ) -> None:
        """Кэшировать данные для производительности."""
        self.performance_optimizer.cache_data(key, data, ttl)

    def get_cached_performance_data(self, key: str) -> Optional[Any]:
        """Получить кэшированные данные производительности."""
        return self.performance_optimizer.get_cached_data(key)

    def execute_async_task(self, func: Callable, *args, **kwargs) -> Any:
        """Выполнить задачу асинхронно в пуле потоков."""
        return self.performance_optimizer.execute_async(func, *args, **kwargs)

    def execute_isolated_task(self, func: Callable, *args, **kwargs) -> Any:
        """Выполнить задачу в изолированном процессе."""
        return self.performance_optimizer.execute_isolated(
            func, *args, **kwargs
        )

    def get_performance_summary(self) -> Dict[str, Any]:
        """Получить сводку производительности."""
        stats = self.get_performance_stats()
        slow_queries = self.get_slow_queries()
        memory_info = self.optimize_memory()

        return {
            "performance_stats": stats,
            "slow_queries_count": len(slow_queries),
            "memory_optimization": memory_info,
            "cache_size": len(self.performance_optimizer.data_cache),
            "connection_pool_size": len(
                self.performance_optimizer.connection_pool.connections
            ),
            "available_connections": len(
                self.performance_optimizer.connection_pool
                .available_connections
            ),
        }


# Функция тестирования
async def test_parental_control_bot():
    """Тестирование ParentalControlBot"""
    print("🧪 Тестирование ParentalControlBot...")

    # Создание бота
    bot = ParentalControlBot("TestParentalBot")

    try:
        # Запуск
        await bot.start()
        print("✅ ParentalControlBot запущен")

        # Добавление профиля ребенка
        child_data = {
            "name": "Test Child",
            "age": 10,
            "parent_id": "parent_123",
            "time_limits": {"mobile": 120, "desktop": 180},
            "restrictions": {"adult_content": True, "social_media": False},
        }

        child_id = await bot.add_child_profile(child_data)
        print(f"✅ Профиль ребенка добавлен: {child_id}")

        # Анализ контента
        result = await bot.analyze_content(
            "https://youtube.com/watch?v=test", child_id
        )
        print(f"✅ Анализ контента: {result.action.value} - {result.reason}")

        # Получение статуса ребенка
        status = await bot.get_child_status(child_id)
        print(f"✅ Статус ребенка: {status['name']} - {status['age_group']}")

        # Получение общего статуса
        bot_status = await bot.get_status()
        print(f"✅ Статус бота: {bot_status['status']}")

    finally:
        # Остановка
        await bot.stop()
        print("✅ ParentalControlBot остановлен")


# ==================== НОВЫЕ МЕТОДЫ С ВАЛИДАЦИЕЙ ====================


async def create_alert_with_validation(
    bot: ParentalControlBot, alert_data: Dict[str, Any]
) -> Optional[ActivityAlert]:
    """Создание алерта с валидацией данных"""
    try:
        # Валидация входных данных
        validated_data = AlertData(**alert_data)

        # Создание алерта с валидированными данными
        alert = ActivityAlert(
            child_id=validated_data.child_id,
            alert_type=validated_data.alert_type,
            severity=validated_data.severity,
            message=validated_data.message,
            timestamp=datetime.now(),
            action_required=validated_data.severity in ["high", "critical"],
            data=validated_data.data,
        )

        # Отправка уведомления
        bot._send_parent_notification(alert)

        bot.logger.info(
            f"Алерт создан: {validated_data.alert_type} "
            f"для {validated_data.child_id}"
        )
        return alert

    except Exception as e:
        bot.logger.error(f"Ошибка создания алерта: {e}")
        return None


async def set_time_limit_with_validation(
    bot: ParentalControlBot, child_id: str, device_type: str, minutes: int
) -> bool:
    """Установка лимита времени с валидацией"""
    try:
        # Валидация данных
        time_data = TimeLimitData(device_type=device_type, minutes=minutes)

        # Проверка существования профиля
        if child_id not in bot.child_profiles:
            bot.logger.error(f"Профиль ребенка {child_id} не найден")
            return False

        # Обновление лимитов
        profile = bot.child_profiles[child_id]
        if not profile.time_limits:
            profile.time_limits = {}

        profile.time_limits[time_data.device_type] = time_data.minutes
        profile.updated_at = datetime.now()

        # Сохранение в БД
        if bot.db_session:
            bot.db_session.commit()

        bot.logger.info(
            f"Лимит времени установлен: {time_data.device_type} = "
            f"{time_data.minutes}м для {child_id}"
        )
        return True

    except Exception as e:
        bot.logger.error(f"Ошибка установки лимита времени: {e}")
        return False


def validate_child_data(
    child_data: Dict[str, Any]
) -> Tuple[bool, Optional[str]]:
    """Валидация данных ребенка без создания профиля"""
    try:
        ChildProfileData(**child_data)
        return True, None
    except Exception as e:
        return False, str(e)


def validate_content_request(
    url: str, child_id: str
) -> Tuple[bool, Optional[str]]:
    """Валидация запроса анализа контента"""
    try:
        ContentAnalysisRequest(url=url, child_id=child_id)
        return True, None
    except Exception as e:
        return False, str(e)


# Запуск тестов при прямом выполнении
if __name__ == "__main__":
    asyncio.run(test_parental_control_bot())
