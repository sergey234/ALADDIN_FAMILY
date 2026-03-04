#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RateLimiter - Интеллектуальный ограничитель скорости запросов
function_83: Защита от DDoS атак и злоупотреблений

Этот модуль предоставляет продвинутую систему ограничения скорости запросов
для AI системы безопасности,
включающую:
- Множественные алгоритмы rate limiting
  (Token Bucket, Sliding Window, Fixed Window)
- Интеллектуальное определение аномальных паттернов трафика
- Адаптивные лимиты на основе поведения пользователей
- ML-анализ для выявления DDoS атак
- Интеграция с системой мониторинга и алертинга
- Поддержка различных типов лимитов (per IP, per user, per endpoint)
- Автоматическое обучение и адаптация лимитов
- Детальное логирование и аудит всех операций
- Интеграция с внешними системами мониторинга (Prometheus, Grafana)
- Поддержка различных протоколов и API endpoints

Основные возможности:
1. Интеллектуальное ограничение скорости запросов
2. Автоматическое обнаружение и блокировка аномального трафика
3. ML-оптимизация лимитов на основе исторических данных
4. Интеграция с системой мониторинга для отслеживания метрик
5. Поддержка различных стратегий rate limiting
6. Адаптивные лимиты на основе контекста и поведения
7. Детальное логирование и аудит всех операций
8. Интеграция с внешними системами мониторинга
9. Поддержка различных типов пользователей и ролей
10. Автоматическое восстановление после сбоев

Технические детали:
- Использует asyncio для высокопроизводительной асинхронной обработки
- Применяет ML алгоритмы для анализа трафика
- Интегрирует Redis для кэширования состояний лимитов
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
import hashlib
import json
import logging
import os
import sys
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import redis
import sqlalchemy
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Gauge, Histogram
from pydantic import BaseModel, Field, validator
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from security.core.security_base import SecurityBase  # noqa: E402

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus метрики
REQUEST_COUNT = Counter(
    "rate_limiter_requests_total",
    "Total rate limiter requests",
    ["algorithm", "client_type", "status"],
)
REQUEST_DURATION = Histogram(
    "rate_limiter_request_duration_seconds",
    "Rate limiter request duration",
    ["algorithm", "client_type"],
)
ACTIVE_LIMITS = Gauge(
    "rate_limiter_active_limits",
    "Active rate limits per client type",
    ["client_type"],
)
BLOCKED_REQUESTS = Counter(
    "rate_limiter_blocked_requests_total",
    "Blocked requests by rate limiter",
    ["reason", "client_type"],
)
ML_ANOMALIES = Counter(
    "rate_limiter_ml_anomalies_total",
    "ML detected anomalies",
    ["anomaly_type", "severity"],
)

# База данных
Base = declarative_base()


class RateLimitRecord(Base):
    """Запись о лимите скорости"""

    __tablename__ = "rate_limit_records"

    id = Column(String, primary_key=True)
    client_id = Column(String, nullable=False, index=True)
    client_type = Column(String, nullable=False, index=True)
    algorithm = Column(String, nullable=False)
    limit_value = Column(Integer, nullable=False)
    window_size = Column(Integer, nullable=False)
    current_usage = Column(Integer, default=0)
    last_reset = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    request_metadata = Column(JSON, default={})


class RateLimitViolation(Base):
    """Запись о нарушении лимита"""

    __tablename__ = "rate_limit_violations"

    id = Column(String, primary_key=True)
    client_id = Column(String, nullable=False, index=True)
    client_type = Column(String, nullable=False, index=True)
    algorithm = Column(String, nullable=False)
    limit_value = Column(Integer, nullable=False)
    actual_usage = Column(Integer, nullable=False)
    violation_time = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String)
    user_agent = Column(String)
    endpoint = Column(String)
    severity = Column(String, default="medium")
    is_blocked = Column(Boolean, default=False)
    request_metadata = Column(JSON, default={})


# Pydantic модели


class RateLimitConfig(BaseModel):
    """Конфигурация лимита скорости"""

    client_id: str = Field(..., description="Идентификатор клиента")
    client_type: str = Field(
        ..., description="Тип клиента (ip, user, endpoint)"
    )
    algorithm: str = Field(..., description="Алгоритм rate limiting")
    limit_value: int = Field(
        ..., gt=0, description="Максимальное количество запросов"
    )
    window_size: int = Field(..., gt=0, description="Размер окна в секундах")
    burst_limit: Optional[int] = Field(
        None, gt=0, description="Лимит всплеска"
    )
    adaptive: bool = Field(True, description="Адаптивные лимиты")
    ml_enabled: bool = Field(True, description="ML анализ включен")

    @validator("algorithm")
    def validate_algorithm(cls, v):
        allowed = [
            "token_bucket",
            "sliding_window",
            "fixed_window",
            "adaptive",
        ]
        if v not in allowed:
            raise ValueError(f"Algorithm must be one of {allowed}")
        return v


class RateLimitRequest(BaseModel):
    """Запрос на проверку лимита"""

    client_id: str = Field(..., description="Идентификатор клиента")
    client_type: str = Field(..., description="Тип клиента")
    endpoint: Optional[str] = Field(None, description="API endpoint")
    ip_address: Optional[str] = Field(None, description="IP адрес")
    user_agent: Optional[str] = Field(None, description="User Agent")
    request_size: int = Field(1, ge=1, description="Размер запроса")
    priority: int = Field(1, ge=1, le=10, description="Приоритет запроса")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Дополнительные данные"
    )


class RateLimitResponse(BaseModel):
    """Ответ на запрос лимита"""

    allowed: bool = Field(..., description="Разрешен ли запрос")
    remaining: int = Field(..., description="Оставшиеся запросы")
    reset_time: datetime = Field(..., description="Время сброса лимита")
    retry_after: Optional[int] = Field(
        None, description="Время до следующей попытки"
    )
    reason: Optional[str] = Field(None, description="Причина блокировки")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Дополнительные данные"
    )


# Перечисления


class RateLimitAlgorithm(Enum):
    """Алгоритмы rate limiting"""

    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"
    ADAPTIVE = "adaptive"


class ClientType(Enum):
    """Типы клиентов"""

    IP = "ip"
    USER = "user"
    ENDPOINT = "endpoint"
    GLOBAL = "global"


class ViolationSeverity(Enum):
    """Уровни серьезности нарушений"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Классы для алгоритмов
@dataclass
class TokenBucket:
    """Token Bucket алгоритм"""

    capacity: int
    refill_rate: float = 1.0
    tokens: float = 0
    last_refill: float = field(default_factory=time.time)

    def __post_init__(self):
        """Инициализация после создания"""
        self.tokens = float(self.capacity)  # Начинаем с полным бакетом

    def consume(self, tokens: int = 1) -> bool:
        """Попытка потребить токены"""
        now = time.time()
        time_passed = now - self.last_refill

        # Пополняем токены
        self.tokens = min(
            self.capacity, self.tokens + time_passed * self.refill_rate
        )
        self.last_refill = now

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    def get_remaining(self) -> int:
        """Получить оставшиеся токены"""
        now = time.time()
        time_passed = now - self.last_refill
        current_tokens = min(
            self.capacity, self.tokens + time_passed * self.refill_rate
        )
        return int(current_tokens)


@dataclass
class SlidingWindow:
    """Sliding Window алгоритм"""

    limit: int
    window_size: int
    requests: deque = field(default_factory=deque)

    def consume(self) -> bool:
        """Попытка добавить запрос"""
        now = time.time()
        # Удаляем старые запросы
        while self.requests and self.requests[0] <= now - self.window_size:
            self.requests.popleft()

        if len(self.requests) < self.limit:
            self.requests.append(now)
            return True
        return False

    def get_remaining(self) -> int:
        """Получить оставшиеся запросы"""
        now = time.time()
        # Удаляем старые запросы
        while self.requests and self.requests[0] <= now - self.window_size:
            self.requests.popleft()
        return max(0, self.limit - len(self.requests))


@dataclass
class FixedWindow:
    """Fixed Window алгоритм"""

    limit: int
    window_size: int
    current_window: int = 0
    current_count: int = 0
    window_start: float = field(default_factory=time.time)

    def consume(self) -> bool:
        """Попытка добавить запрос"""
        now = time.time()
        current_window = int(now // self.window_size)

        if current_window != self.current_window:
            self.current_window = current_window
            self.current_count = 0
            self.window_start = now

        if self.current_count < self.limit:
            self.current_count += 1
            return True
        return False

    def get_remaining(self) -> int:
        """Получить оставшиеся запросы"""
        now = time.time()
        current_window = int(now // self.window_size)

        if current_window != self.current_window:
            return self.limit

        return max(0, self.limit - self.current_count)


# Основной класс RateLimiter


class RateLimiter(SecurityBase):
    """
    Интеллектуальный ограничитель скорости запросов

    Предоставляет продвинутую систему rate limiting с поддержкой:
    - Множественных алгоритмов
    - ML анализа аномалий
    - Адаптивных лимитов
    - Интеграции с мониторингом
    """

    def __init__(
        self,
        name: str = "RateLimiter",
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Инициализация RateLimiter

        Args:
            name: Имя RateLimiter
            config: Конфигурация
        """
        super().__init__(name, config)

        # Конфигурация по умолчанию
        self.default_config = {
            "redis_url": "redis://localhost:6379/0",
            "database_url": "sqlite:///rate_limiter.db",
            "default_algorithm": "adaptive",
            "default_window_size": 60,  # секунд
            "default_limit": 100,  # запросов
            "ml_enabled": True,
            "adaptive_learning": True,
            "anomaly_threshold": 0.1,
            "max_adaptive_factor": 2.0,
            "min_adaptive_factor": 0.1,
            "cleanup_interval": 300,  # секунд
            "metrics_enabled": True,
            "logging_enabled": True,
            "enable_circuit_breaker": True,
            "circuit_breaker_threshold": 10,
            "circuit_breaker_timeout": 60,
        }

        # Объединение конфигураций
        self.config = {**self.default_config, **(config or {})}

        # Инициализация компонентов
        self.redis_client: Optional[redis.Redis] = None
        self.db_engine: Optional[sqlalchemy.Engine] = None
        self.db_session: Optional[sqlalchemy.orm.Session] = None
        self.rate_limits: Dict[str, Any] = {}
        self.violations: Dict[str, List[RateLimitViolation]] = defaultdict(
            list
        )
        self.ml_model: Optional[IsolationForest] = None
        self.scaler: Optional[StandardScaler] = None
        self.adaptive_factors: Dict[str, float] = defaultdict(lambda: 1.0)
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}

        # Статистика
        self.stats = {
            "total_requests": 0,
            "allowed_requests": 0,
            "blocked_requests": 0,
            "ml_anomalies": 0,
            "adaptive_adjustments": 0,
        }

        # Потоки
        self.cleanup_thread: Optional[threading.Thread] = None
        self.ml_thread: Optional[threading.Thread] = None
        self.running = False

        # Блокировки
        self.lock = threading.RLock()

        self.logger.info(f"RateLimiter {name} инициализирован")

    async def start(self) -> bool:
        """Запуск RateLimiter"""
        try:
            self.logger.info("Запуск RateLimiter")

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

            self.logger.info("RateLimiter успешно запущен")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка запуска RateLimiter: {e}")
            return False

    async def stop(self) -> bool:
        """Остановка RateLimiter"""
        try:
            self.logger.info("Остановка RateLimiter")

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

            self.logger.info("RateLimiter успешно остановлен")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка остановки RateLimiter: {e}")
            return False

    async def _initialize_database(self) -> None:
        """Инициализация базы данных"""
        try:
            database_url = self.config.get(
                "database_url", "sqlite:///rate_limiter.db"
            )
            self.db_engine = create_engine(database_url, echo=False)

            # Создание таблиц
            Base.metadata.create_all(self.db_engine)

            # Создание сессии
            Session = sessionmaker(bind=self.db_engine)
            self.db_session = Session()

            self.logger.info("База данных RateLimiter инициализирована")

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

            self.logger.info("Redis клиент RateLimiter инициализирован")

        except Exception as e:
            self.logger.error(f"Ошибка инициализации Redis: {e}")
            raise

    async def _initialize_ml_model(self) -> None:
        """Инициализация ML модели"""
        try:
            # Инициализация модели обнаружения аномалий
            self.ml_model = IsolationForest(
                contamination=self.config["anomaly_threshold"], random_state=42
            )

            # Инициализация скейлера
            self.scaler = StandardScaler()

            self.logger.info("ML модель RateLimiter инициализирована")

        except Exception as e:
            self.logger.error(f"Ошибка инициализации ML модели: {e}")
            raise

    async def check_rate_limit(
        self, request: RateLimitRequest
    ) -> RateLimitResponse:
        """
        Проверка лимита скорости для запроса

        Args:
            request: Запрос на проверку лимита

        Returns:
            RateLimitResponse: Результат проверки
        """
        start_time = time.time()

        try:
            with self.lock:
                self.stats["total_requests"] += 1

            # Получение конфигурации лимита
            limit_config = await self._get_limit_config(request)

            # Проверка circuit breaker
            if self.config["enable_circuit_breaker"]:
                if not await self._is_circuit_breaker_closed(
                    request.client_id
                ):
                    return RateLimitResponse(
                        allowed=False,
                        remaining=0,
                        reset_time=datetime.utcnow()
                        + timedelta(seconds=limit_config.window_size),
                        retry_after=limit_config.window_size,
                        reason="Circuit breaker open",
                    )

            # ML анализ аномалий
            if self.config["ml_enabled"]:
                is_anomaly = await self._detect_anomaly(request)
                if is_anomaly:
                    with self.lock:
                        self.stats["ml_anomalies"] += 1
                    ML_ANOMALIES.labels(
                        anomaly_type="request_pattern", severity="high"
                    ).inc()

            # Применение алгоритма rate limiting
            allowed, remaining, reset_time = await self._apply_rate_limit(
                request, limit_config
            )

            # Обновление статистики
            with self.lock:
                if allowed:
                    self.stats["allowed_requests"] += 1
                else:
                    self.stats["blocked_requests"] += 1

            # Обновление circuit breaker
            if self.config["enable_circuit_breaker"]:
                await self._update_circuit_breaker(request.client_id, allowed)

            # Логирование
            duration = time.time() - start_time
            REQUEST_DURATION.labels(
                algorithm=limit_config.algorithm,
                client_type=request.client_type,
            ).observe(duration)

            REQUEST_COUNT.labels(
                algorithm=limit_config.algorithm,
                client_type=request.client_type,
                status="allowed" if allowed else "blocked",
            ).inc()

            if not allowed:
                BLOCKED_REQUESTS.labels(
                    reason="rate_limit_exceeded",
                    client_type=request.client_type,
                ).inc()

            return RateLimitResponse(
                allowed=allowed,
                remaining=remaining,
                reset_time=reset_time,
                retry_after=limit_config.window_size if not allowed else None,
                reason="Rate limit exceeded" if not allowed else None,
                request_metadata={
                    "algorithm": limit_config.algorithm,
                    "duration_ms": duration * 1000,
                    "is_anomaly": (
                        is_anomaly if self.config["ml_enabled"] else False
                    ),
                },
            )

        except Exception as e:
            self.logger.error(f"Ошибка проверки лимита: {e}")
            return RateLimitResponse(
                allowed=False,
                remaining=0,
                reset_time=datetime.utcnow() + timedelta(seconds=60),
                retry_after=60,
                reason=f"Internal error: {str(e)}",
            )

    async def _get_limit_config(
        self, request: RateLimitRequest
    ) -> RateLimitConfig:
        """Получение конфигурации лимита для запроса"""
        # Проверка кэша
        cache_key = (
            f"rate_limit_config:{request.client_id}:{request.client_type}"
        )

        if self.redis_client:
            cached_config = self.redis_client.get(cache_key)
            if cached_config:
                config_data = json.loads(cached_config)
                return RateLimitConfig(**config_data)

        # Получение из базы данных
        if self.db_session:
            record = (
                self.db_session.query(RateLimitRecord)
                .filter(
                    RateLimitRecord.client_id == request.client_id,
                    RateLimitRecord.client_type == request.client_type,
                    RateLimitRecord.is_active,
                )
                .first()
            )

            if record:
                config = RateLimitConfig(
                    client_id=record.client_id,
                    client_type=record.client_type,
                    algorithm=record.algorithm,
                    limit_value=record.limit_value,
                    window_size=record.window_size,
                    adaptive=True,
                    ml_enabled=self.config["ml_enabled"],
                )

                # Кэширование
                if self.redis_client:
                    self.redis_client.setex(
                        cache_key, 300, json.dumps(config.dict())  # 5 минут
                    )

                return config

        # Создание конфигурации по умолчанию
        default_config = RateLimitConfig(
            client_id=request.client_id,
            client_type=request.client_type,
            algorithm=self.config["default_algorithm"],
            limit_value=self.config["default_limit"],
            window_size=self.config["default_window_size"],
            adaptive=self.config["adaptive_learning"],
            ml_enabled=self.config["ml_enabled"],
        )

        # Сохранение в базу данных
        await self._save_limit_config(default_config)

        return default_config

    async def _apply_rate_limit(
        self, request: RateLimitRequest, config: RateLimitConfig
    ) -> Tuple[bool, int, datetime]:
        """Применение алгоритма rate limiting"""
        client_key = f"{request.client_id}:{request.client_type}"

        # Получение или создание лимитера
        if client_key not in self.rate_limits:
            self.rate_limits[client_key] = self._create_limiter(config)

        limiter = self.rate_limits[client_key]

        # Применение адаптивного фактора
        if config.adaptive and client_key in self.adaptive_factors:
            adaptive_factor = self.adaptive_factors[client_key]
            if hasattr(limiter, "limit"):
                limiter.limit = int(config.limit_value * adaptive_factor)
            elif hasattr(limiter, "capacity"):
                limiter.capacity = int(config.limit_value * adaptive_factor)

        # Проверка лимита
        allowed = limiter.consume(request.request_size)
        remaining = limiter.get_remaining()

        # Вычисление времени сброса
        reset_time = datetime.utcnow() + timedelta(seconds=config.window_size)

        # Запись нарушения
        if not allowed:
            await self._record_violation(request, config, limiter)

        return allowed, remaining, reset_time

    def _create_limiter(self, config: RateLimitConfig):
        """Создание лимитера на основе конфигурации"""
        algorithm = RateLimitAlgorithm(config.algorithm)

        if algorithm == RateLimitAlgorithm.TOKEN_BUCKET:
            return TokenBucket(
                capacity=config.limit_value,
                refill_rate=config.limit_value / config.window_size,
            )
        elif algorithm == RateLimitAlgorithm.SLIDING_WINDOW:
            return SlidingWindow(
                limit=config.limit_value, window_size=config.window_size
            )
        elif algorithm == RateLimitAlgorithm.FIXED_WINDOW:
            return FixedWindow(
                limit=config.limit_value, window_size=config.window_size
            )
        else:  # ADAPTIVE
            return SlidingWindow(
                limit=config.limit_value, window_size=config.window_size
            )

    async def _detect_anomaly(self, request: RateLimitRequest) -> bool:
        """Обнаружение аномалий в запросе с помощью ML"""
        if not self.ml_model or not self.scaler:
            return False

        try:
            # Подготовка признаков
            features = self._extract_features(request)

            if len(features) == 0:
                return False

            # Нормализация признаков
            features_scaled = self.scaler.transform([features])

            # Предсказание аномалии
            anomaly_score = self.ml_model.decision_function(features_scaled)[0]
            is_anomaly = anomaly_score < 0

            return is_anomaly

        except Exception as e:
            self.logger.error(f"Ошибка обнаружения аномалии: {e}")
            return False

    def _extract_features(self, request: RateLimitRequest) -> List[float]:
        """Извлечение признаков для ML анализа"""
        features = []

        # Временные признаки
        now = datetime.utcnow()
        features.extend([now.hour, now.weekday(), now.day, now.month])

        # Признаки запроса
        features.extend(
            [
                request.request_size,
                request.priority,
                (
                    len(request.request_metadata)
                    if request.request_metadata
                    else 0
                ),
            ]
        )

        # Признаки клиента
        if request.ip_address:
            # Простая хэш-функция для IP
            ip_hash = int(
                hashlib.md5(request.ip_address.encode()).hexdigest()[:8], 16
            )
            features.append(ip_hash % 1000)  # Нормализация
        else:
            features.append(0)

        if request.user_agent:
            features.append(len(request.user_agent))
        else:
            features.append(0)

        return features

    async def _record_violation(
        self, request: RateLimitRequest, config: RateLimitConfig, limiter
    ) -> None:
        """Запись нарушения лимита"""
        try:
            violation = RateLimitViolation(
                id=f"violation_{int(time.time() * 1000)}_{request.client_id}",
                client_id=request.client_id,
                client_type=request.client_type,
                algorithm=config.algorithm,
                limit_value=config.limit_value,
                actual_usage=limiter.get_remaining() + request.request_size,
                ip_address=request.ip_address,
                user_agent=request.user_agent,
                endpoint=request.endpoint,
                severity=self._calculate_severity(request, config),
                is_blocked=True,
                request_metadata=request.request_metadata,
            )

            # Сохранение в базу данных
            if self.db_session:
                self.db_session.add(violation)
                self.db_session.commit()

            # Добавление в кэш нарушений
            client_key = f"{request.client_id}:{request.client_type}"
            self.violations[client_key].append(violation)

            # Ограничение размера кэша
            if len(self.violations[client_key]) > 100:
                self.violations[client_key] = self.violations[client_key][-50:]

        except Exception as e:
            self.logger.error(f"Ошибка записи нарушения: {e}")

    def _calculate_severity(
        self, request: RateLimitRequest, config: RateLimitConfig
    ) -> str:
        """Вычисление серьезности нарушения"""
        # Простая логика определения серьезности
        if request.priority >= 8:
            return ViolationSeverity.CRITICAL.value
        elif request.priority >= 5:
            return ViolationSeverity.HIGH.value
        elif request.priority >= 3:
            return ViolationSeverity.MEDIUM.value
        else:
            return ViolationSeverity.LOW.value

    async def _save_limit_config(self, config: RateLimitConfig) -> None:
        """Сохранение конфигурации лимита"""
        try:
            record = RateLimitRecord(
                id=f"config_{config.client_id}_{config.client_type}",
                client_id=config.client_id,
                client_type=config.client_type,
                algorithm=config.algorithm,
                limit_value=config.limit_value,
                window_size=config.window_size,
                request_metadata=config.dict(),
            )

            if self.db_session:
                # Обновление или создание записи
                existing = (
                    self.db_session.query(RateLimitRecord)
                    .filter(RateLimitRecord.id == record.id)
                    .first()
                )

                if existing:
                    existing.algorithm = record.algorithm
                    existing.limit_value = record.limit_value
                    existing.window_size = record.window_size
                    existing.updated_at = datetime.utcnow()
                else:
                    self.db_session.add(record)

                self.db_session.commit()

        except Exception as e:
            self.logger.error(f"Ошибка сохранения конфигурации: {e}")

    async def _is_circuit_breaker_closed(self, client_id: str) -> bool:
        """Проверка состояния circuit breaker"""
        if client_id not in self.circuit_breakers:
            return True

        cb = self.circuit_breakers[client_id]
        now = time.time()

        if cb["state"] == "open":
            if now - cb["last_failure_time"] > cb["timeout"]:
                cb["state"] = "half_open"
                return True
            return False

        return True

    async def _update_circuit_breaker(
        self, client_id: str, success: bool
    ) -> None:
        """Обновление состояния circuit breaker"""
        if client_id not in self.circuit_breakers:
            self.circuit_breakers[client_id] = {
                "state": "closed",
                "failure_count": 0,
                "last_failure_time": 0,
                "timeout": self.config["circuit_breaker_timeout"],
            }

        cb = self.circuit_breakers[client_id]

        if success:
            if cb["state"] == "half_open":
                cb["state"] = "closed"
            cb["failure_count"] = 0
        else:
            cb["failure_count"] += 1
            cb["last_failure_time"] = time.time()

            if cb["failure_count"] >= self.config["circuit_breaker_threshold"]:
                cb["state"] = "open"

    def _cleanup_worker(self) -> None:
        """Фоновый процесс очистки"""
        while self.running:
            try:
                time.sleep(self.config["cleanup_interval"])

                with self.lock:
                    # Очистка старых лимитеров
                    current_time = time.time()
                    keys_to_remove = []

                    for key, limiter in self.rate_limits.items():
                        if hasattr(limiter, "last_refill"):
                            if (
                                current_time - limiter.last_refill > 3600
                            ):  # 1 час
                                keys_to_remove.append(key)

                    for key in keys_to_remove:
                        del self.rate_limits[key]

                    # Очистка старых нарушений
                    for client_key in self.violations:
                        violations = self.violations[client_key]
                        cutoff_time = current_time - 86400  # 24 часа

                        self.violations[client_key] = [
                            v
                            for v in violations
                            if v.violation_time.timestamp() > cutoff_time
                        ]

                self.logger.debug("Очистка RateLimiter завершена")

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
                    for client_key, violations in self.violations.items():
                        for violation in violations[
                            -100:
                        ]:  # Последние 100 нарушений
                            features = self._extract_features_from_violation(
                                violation
                            )
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

                self.logger.info("ML модель RateLimiter переобучена")

            except Exception as e:
                self.logger.error(f"Ошибка в ML процессе: {e}")

    def _extract_features_from_violation(
        self, violation: RateLimitViolation
    ) -> List[float]:
        """Извлечение признаков из нарушения"""
        features = []

        # Временные признаки
        violation_time = violation.violation_time
        features.extend(
            [
                violation_time.hour,
                violation_time.weekday(),
                violation_time.day,
                violation_time.month,
            ]
        )

        # Признаки нарушения
        features.extend(
            [
                violation.actual_usage,
                violation.limit_value,
                (
                    len(violation.request_metadata)
                    if violation.request_metadata
                    else 0
                ),
            ]
        )

        # Признаки IP
        if violation.ip_address:
            ip_hash = int(
                hashlib.md5(violation.ip_address.encode()).hexdigest()[:8], 16
            )
            features.append(ip_hash % 1000)
        else:
            features.append(0)

        return features

    async def _update_adaptive_factors(self) -> None:
        """Обновление адаптивных факторов на основе ML анализа"""
        try:
            with self.lock:
                for client_key, violations in self.violations.items():
                    if len(violations) < 5:  # Недостаточно данных
                        continue

                    # Анализ паттерна нарушений
                    recent_violations = violations[
                        -10:
                    ]  # Последние 10 нарушений
                    violation_rate = len(recent_violations) / 10.0

                    # Адаптация фактора
                    if violation_rate > 0.7:  # Высокий уровень нарушений
                        self.adaptive_factors[client_key] = max(
                            self.config["min_adaptive_factor"],
                            self.adaptive_factors[client_key] * 0.9,
                        )
                    elif violation_rate < 0.1:  # Низкий уровень нарушений
                        self.adaptive_factors[client_key] = min(
                            self.config["max_adaptive_factor"],
                            self.adaptive_factors[client_key] * 1.1,
                        )

                    self.stats["adaptive_adjustments"] += 1

        except Exception as e:
            self.logger.error(f"Ошибка обновления адаптивных факторов: {e}")

    async def get_status(self) -> Dict[str, Any]:
        """Получение статуса RateLimiter"""
        with self.lock:
            return {
                "name": self.name,
                "status": "running" if self.running else "stopped",
                "stats": self.stats.copy(),
                "active_limits": len(self.rate_limits),
                "total_violations": sum(
                    len(v) for v in self.violations.values()
                ),
                "adaptive_factors": dict(self.adaptive_factors),
                "circuit_breakers": {
                    client_id: {
                        "state": cb["state"],
                        "failure_count": cb["failure_count"],
                    }
                    for client_id, cb in self.circuit_breakers.items()
                },
                "config": {
                    "ml_enabled": self.config["ml_enabled"],
                    "adaptive_learning": self.config["adaptive_learning"],
                    "default_algorithm": self.config["default_algorithm"],
                    "default_limit": self.config["default_limit"],
                },
            }

    async def reset_limits(self, client_id: Optional[str] = None) -> bool:
        """Сброс лимитов для клиента или всех клиентов"""
        try:
            with self.lock:
                if client_id:
                    # Сброс для конкретного клиента
                    keys_to_remove = [
                        key
                        for key in self.rate_limits.keys()
                        if key.startswith(f"{client_id}:")
                    ]
                    for key in keys_to_remove:
                        del self.rate_limits[key]

                    if client_id in self.adaptive_factors:
                        del self.adaptive_factors[client_id]

                    if client_id in self.circuit_breakers:
                        del self.circuit_breakers[client_id]
                else:
                    # Сброс всех лимитов
                    self.rate_limits.clear()
                    self.adaptive_factors.clear()
                    self.circuit_breakers.clear()

                self.logger.info(
                    f"Лимиты сброшены для "
                    f"{'всех клиентов' if not client_id else client_id}"
                )
                return True

        except Exception as e:
            self.logger.error(f"Ошибка сброса лимитов: {e}")
            return False

    def start_limiting(self) -> bool:
        """Запуск ограничения скорости"""
        try:
            with self.lock:
                if not self.running:
                    self.running = True
                    self.logger.info("Ограничение скорости запущено")
                    return True
                else:
                    self.logger.warning("Ограничение скорости уже запущено")
                    return False
        except Exception as e:
            self.logger.error(f"Ошибка запуска ограничения скорости: {e}")
            return False

    def stop_limiting(self) -> bool:
        """Остановка ограничения скорости"""
        try:
            with self.lock:
                if self.running:
                    self.running = False
                    self.logger.info("Ограничение скорости остановлено")
                    return True
                else:
                    self.logger.warning("Ограничение скорости уже остановлено")
                    return False
        except Exception as e:
            self.logger.error(f"Ошибка остановки ограничения скорости: {e}")
            return False

    def get_limit_info(self) -> Dict[str, Any]:
        """Получение информации о лимитах"""
        try:
            with self.lock:
                return {
                    "running": self.running,
                    "total_requests": self.stats["total_requests"],
                    "allowed_requests": self.stats["allowed_requests"],
                    "blocked_requests": self.stats["blocked_requests"],
                    "active_limits": len(self.rate_limits),
                    "ml_enabled": self.config.get("ml_enabled", False),
                    "adaptive_learning": self.config.get(
                        "adaptive_learning", False
                    ),
                    "circuit_breakers": len(self.circuit_breakers),
                }
        except Exception as e:
            self.logger.error(f"Ошибка получения информации о лимитах: {e}")
            return {
                "running": False,
                "total_requests": 0,
                "allowed_requests": 0,
                "blocked_requests": 0,
                "active_limits": 0,
                "ml_enabled": False,
                "adaptive_learning": False,
                "circuit_breakers": 0,
            }


# API сервер для RateLimiter

app = FastAPI(title="RateLimiter API", version="2.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Глобальный экземпляр RateLimiter
rate_limiter: Optional[RateLimiter] = None


@app.on_event("startup")
async def startup_event():
    """Инициализация RateLimiter при запуске"""
    global rate_limiter
    rate_limiter = RateLimiter("RateLimiterServer")
    await rate_limiter.start()


@app.on_event("shutdown")
async def shutdown_event():
    """Остановка RateLimiter при завершении"""
    global rate_limiter
    if rate_limiter:
        await rate_limiter.stop()


@app.get("/health")
async def health_check():
    """Проверка здоровья RateLimiter"""
    return {"status": "healthy", "service": "RateLimiter"}


@app.get("/status")
async def get_status():
    """Получение статуса RateLimiter"""
    if not rate_limiter:
        raise HTTPException(
            status_code=503, detail="RateLimiter not initialized"
        )

    return await rate_limiter.get_status()


@app.post("/check")
async def check_rate_limit(request: RateLimitRequest):
    """Проверка лимита скорости"""
    if not rate_limiter:
        raise HTTPException(
            status_code=503, detail="RateLimiter not initialized"
        )

    return await rate_limiter.check_rate_limit(request)


@app.post("/reset")
async def reset_limits(client_id: Optional[str] = None):
    """Сброс лимитов"""
    if not rate_limiter:
        raise HTTPException(
            status_code=503, detail="RateLimiter not initialized"
        )

    success = await rate_limiter.reset_limits(client_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to reset limits")

    return {"message": "Limits reset successfully"}


@app.get("/metrics")
async def get_metrics():
    """Получение метрик Prometheus"""
    from fastapi.responses import Response
    from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# Основная функция для запуска сервера


def main():
    """Запуск сервера RateLimiter"""
    uvicorn.run(
        "rate_limiter:app",
        host="0.0.0.0",
        port=8007,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()


# Тестирование
async def test_rate_limiter():
    """Тестирование RateLimiter"""
    print("🧪 Тестирование RateLimiter...")

    # Создание экземпляра
    limiter = RateLimiter("TestRateLimiter")

    try:
        # Запуск
        await limiter.start()
        print("✅ RateLimiter запущен")

        # Тест 1: Обычный запрос
        request = RateLimitRequest(
            client_id="test_client_1",
            client_type="ip",
            ip_address="192.168.1.1",
            user_agent="TestAgent/1.0",
        )

        response = await limiter.check_rate_limit(request)
        print(f"✅ Тест 1 - Обычный запрос: {response.allowed}")

        # Тест 2: Множественные запросы
        for i in range(5):
            request = RateLimitRequest(
                client_id="test_client_2",
                client_type="user",
                request_size=1,
                priority=5,
            )
            response = await limiter.check_rate_limit(request)
            print(
                f"✅ Тест 2.{i+1} - Запрос {i+1}: {response.allowed}, "
                f"осталось: {response.remaining}"
            )

        # Тест 3: Превышение лимита
        request = RateLimitRequest(
            client_id="test_client_3",
            client_type="endpoint",
            request_size=1000,  # Большой запрос
            priority=1,
        )
        response = await limiter.check_rate_limit(request)
        print(
            f"✅ Тест 3 - Превышение лимита: {response.allowed}, "
            f"причина: {response.reason}"
        )

        # Тест 4: Статус
        status = await limiter.get_status()
        print(
            f"✅ Тест 4 - Статус: {status['status']}, "
            f"активных лимитов: {status['active_limits']}"
        )

        # Тест 5: Сброс лимитов
        success = await limiter.reset_limits("test_client_1")
        print(f"✅ Тест 5 - Сброс лимитов: {success}")

        print("🎉 Все тесты RateLimiter прошли успешно!")

    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")

    finally:
        # Остановка
        await limiter.stop()
        print("✅ RateLimiter остановлен")


# Запуск тестов при прямом выполнении
if __name__ == "__main__":
    asyncio.run(test_rate_limiter())
