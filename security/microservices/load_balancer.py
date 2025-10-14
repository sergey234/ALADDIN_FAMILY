#!/usr/bin/env python3
"""
LoadBalancer - Микросервис балансировки нагрузки

Высокопроизводительный и безопасный балансировщик нагрузки
с поддержкой множественных алгоритмов, мониторинга и метрик.

Автор: ALADDIN Security System
Версия: 2.0.0
Лицензия: MIT
"""

import asyncio
import logging
import os
import statistics

# Импорт базовых классов
import sys
import time
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import aiohttp
import redis
import uvicorn
from fastapi import FastAPI
from prometheus_client import Counter, Gauge, Histogram, generate_latest
from pydantic import BaseModel, Field
from sqlalchemy import (
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

# from core.base import ComponentStatus, CoreBase, SecurityLevel
# Неиспользуемые импорты

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus метрики
REQUEST_COUNT = Counter(
    "load_balancer_requests_total",
    "Total load balancer requests",
    ["algorithm", "service", "status"],
)

REQUEST_DURATION = Histogram(
    "load_balancer_request_duration_seconds",
    "Load balancer request duration",
    ["algorithm", "service"],
)

ACTIVE_CONNECTIONS = Gauge(
    "load_balancer_active_connections",
    "Active connections per service",
    ["service"],
)

SERVICE_HEALTH = Gauge(
    "load_balancer_service_health", "Service health score", ["service"]
)

ALGORITHM_EFFICIENCY = Gauge(
    "load_balancer_algorithm_efficiency",
    "Algorithm efficiency score",
    ["algorithm"],
)

# База данных
Base = declarative_base()


class ServiceEndpoint(Base):
    """Модель сервиса в базе данных"""

    __tablename__ = "service_endpoints"

    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    url = Column(String(500), nullable=False)
    port = Column(Integer, nullable=False)
    protocol = Column(String(10), default="http")
    weight = Column(Integer, default=1)
    max_connections = Column(Integer, default=100)
    health_check_url = Column(String(200), default="/health")
    health_check_interval = Column(Integer, default=30)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class LoadBalancingSession(Base):
    """Модель сессии балансировки"""

    __tablename__ = "load_balancing_sessions"

    id = Column(String(50), primary_key=True)
    service_id = Column(String(50), nullable=False)
    algorithm = Column(String(50), nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    status = Column(String(20), default="active")
    response_time = Column(Float)
    success = Column(Boolean, default=True)


class LoadBalancingMetrics(Base):
    """Модель метрик балансировки"""

    __tablename__ = "load_balancing_metrics"

    id = Column(String(50), primary_key=True)
    service_id = Column(String(50), nullable=False)
    algorithm = Column(String(50), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    avg_response_time = Column(Float)
    throughput = Column(Float)
    error_rate = Column(Float)
    cpu_usage = Column(Float)
    memory_usage = Column(Float)


# Enums
class LoadBalancingAlgorithm(Enum):
    """Алгоритмы балансировки нагрузки"""

    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_RESPONSE_TIME = "least_response_time"
    IP_HASH = "ip_hash"
    RANDOM = "random"
    ADAPTIVE = "adaptive"


class ServiceStatus(Enum):
    """Статусы сервисов"""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    OVERLOADED = "overloaded"


class HealthCheckType(Enum):
    """Типы проверки здоровья"""

    HTTP = "http"
    HTTPS = "https"
    TCP = "tcp"
    CUSTOM = "custom"


# Pydantic модели
class ServiceRequest(BaseModel):
    """Запрос на регистрацию сервиса"""

    name: str = Field(
        ..., min_length=1, max_length=100, description="Уникальное имя сервиса"
    )
    url: str = Field(
        ..., min_length=1, max_length=500, description="URL сервиса"
    )
    port: int = Field(..., ge=1, le=65535, description="Порт сервиса")
    protocol: str = Field(default="http", description="Протокол сервиса")
    weight: int = Field(default=1, ge=1, le=100, description="Вес сервиса")
    max_connections: int = Field(
        default=100,
        ge=1,
        le=10000,
        description="Максимальное количество соединений",
    )
    health_check_url: str = Field(
        default="/health", description="URL для проверки здоровья"
    )
    health_check_interval: int = Field(
        default=30,
        ge=5,
        le=300,
        description="Интервал проверки здоровья в секундах",
    )


class LoadBalancingRequest(BaseModel):
    """Запрос на балансировку нагрузки"""

    service_name: str = Field(..., description="Имя сервиса для балансировки")
    algorithm: Optional[LoadBalancingAlgorithm] = Field(
        default=LoadBalancingAlgorithm.ROUND_ROBIN,
        description="Алгоритм балансировки",
    )
    client_ip: Optional[str] = Field(
        default=None, description="IP адрес клиента"
    )
    session_id: Optional[str] = Field(default=None, description="ID сессии")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Дополнительные метаданные"
    )


class LoadBalancingResponse(BaseModel):
    """Ответ балансировщика нагрузки"""

    service_url: str = Field(..., description="URL выбранного сервиса")
    service_id: str = Field(..., description="ID выбранного сервиса")
    algorithm_used: LoadBalancingAlgorithm = Field(
        ..., description="Использованный алгоритм"
    )
    session_id: str = Field(..., description="ID сессии")
    load_factor: float = Field(..., description="Коэффициент нагрузки")
    health_score: float = Field(..., description="Оценка здоровья сервиса")
    response_time: Optional[float] = Field(
        default=None, description="Время отклика в секундах"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Время ответа"
    )


class HealthCheckResponse(BaseModel):
    """Ответ проверки здоровья сервиса"""

    service_id: str = Field(..., description="ID сервиса")
    is_healthy: bool = Field(..., description="Статус здоровья")
    response_time: float = Field(..., description="Время отклика")
    status_code: Optional[int] = Field(
        default=None, description="HTTP статус код"
    )
    error_message: Optional[str] = Field(
        default=None, description="Сообщение об ошибке"
    )
    metrics: Dict[str, Any] = Field(
        default_factory=dict, description="Дополнительные метрики"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Время проверки"
    )


# Интерфейсы
class LoadBalancingAlgorithmInterface(ABC):
    """Интерфейс алгоритма балансировки нагрузки"""

    @abstractmethod
    async def select_service(
        self, services: List[ServiceEndpoint], request: LoadBalancingRequest
    ) -> Optional[ServiceEndpoint]:
        """Выбор сервиса для обработки запроса"""
        pass

    @abstractmethod
    def get_algorithm_name(self) -> str:
        """Получение имени алгоритма"""
        pass


class HealthCheckInterface(ABC):
    """Интерфейс проверки здоровья сервиса"""

    @abstractmethod
    async def check_health(
        self, service: ServiceEndpoint
    ) -> HealthCheckResponse:
        """Проверка здоровья сервиса"""
        pass


class MetricsCollectorInterface(ABC):
    """Интерфейс сбора метрик"""

    @abstractmethod
    async def collect_metrics(self, service_id: str) -> Dict[str, Any]:
        """Сбор метрик сервиса"""
        pass


# Алгоритмы балансировки
class RoundRobinAlgorithm(LoadBalancingAlgorithmInterface):
    """Алгоритм Round Robin"""

    def __init__(self):
        self.current_index = 0

    async def select_service(
        self, services: List[ServiceEndpoint], request: LoadBalancingRequest
    ) -> Optional[ServiceEndpoint]:
        """Выбор сервиса по принципу Round Robin"""
        if not services:
            return None

        active_services = [s for s in services if s.is_active]
        if not active_services:
            return None

        service = active_services[self.current_index % len(active_services)]
        self.current_index += 1
        return service

    def get_algorithm_name(self) -> str:
        return "round_robin"


class LeastConnectionsAlgorithm(LoadBalancingAlgorithmInterface):
    """Алгоритм наименьших соединений"""

    def __init__(self):
        self.connection_counts: Dict[str, int] = {}

    async def select_service(
        self, services: List[ServiceEndpoint], request: LoadBalancingRequest
    ) -> Optional[ServiceEndpoint]:
        """Выбор сервиса с наименьшим количеством соединений"""
        if not services:
            return None

        active_services = [s for s in services if s.is_active]
        if not active_services:
            return None

        # Находим сервис с минимальным количеством соединений
        min_connections = float("inf")
        selected_service = None

        for service in active_services:
            connections = self.connection_counts.get(service.id, 0)
            if connections < min_connections:
                min_connections = connections
                selected_service = service

        if selected_service:
            self.connection_counts[selected_service.id] = (
                self.connection_counts.get(selected_service.id, 0) + 1
            )

        return selected_service

    def get_algorithm_name(self) -> str:
        return "least_connections"


# Основной класс LoadBalancer
class LoadBalancer:
    """Основной класс балансировщика нагрузки"""

    def __init__(
        self,
        database_url: str = "sqlite:///load_balancer.db",
        redis_url: str = "redis://localhost:6379",
        health_check_timeout: int = 5,
        max_retries: int = 3,
    ):
        """
        Инициализация балансировщика нагрузки

        Args:
            database_url: URL базы данных
            redis_url: URL Redis
            health_check_timeout: Таймаут проверки здоровья
            max_retries: Максимальное количество попыток
        """
        self.database_url = database_url
        self.redis_url = redis_url
        self.health_check_timeout = health_check_timeout
        self.max_retries = max_retries

        # Инициализация компонентов
        self.engine = None
        self.session_factory = None
        self.redis_client = None
        self.http_client = None

        # Алгоритмы балансировки
        self.algorithms: Dict[str, LoadBalancingAlgorithmInterface] = {
            LoadBalancingAlgorithm.ROUND_ROBIN.value: RoundRobinAlgorithm(),
            LoadBalancingAlgorithm.LEAST_CONNECTIONS.value: (
                LeastConnectionsAlgorithm()
            ),
        }

        # Сервисы
        self.services: Dict[str, List[ServiceEndpoint]] = {}
        self.current_algorithm = LoadBalancingAlgorithm.ROUND_ROBIN

        # Логирование
        self.logger = logging.getLogger(__name__)

        # Метрики
        self.metrics_enabled = True
        self.metrics_collection_interval = 30
        self.metrics_task = None

    async def initialize(self) -> bool:
        """Инициализация балансировщика"""
        try:
            # Инициализация базы данных
            self.engine = create_engine(self.database_url)
            Base.metadata.create_all(self.engine)
            self.session_factory = sessionmaker(bind=self.engine)

            # Инициализация Redis
            self.redis_client = redis.Redis.from_url(self.redis_url)

            # Инициализация HTTP клиента
            self.http_client = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.health_check_timeout)
            )

            # Загрузка сервисов из базы данных
            await self._load_services()

            # Запуск сбора метрик
            if self.metrics_enabled:
                self.metrics_task = asyncio.create_task(
                    self._start_metrics_collection()
                )

            self.logger.info("LoadBalancer успешно инициализирован")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка инициализации LoadBalancer: {e}")
            return False

    async def _load_services(self) -> None:
        """Загрузка сервисов из базы данных"""
        try:
            with self.session_factory() as session:
                services = (
                    session.query(ServiceEndpoint)
                    .filter(ServiceEndpoint.is_active is True)
                    .all()
                )

                for service in services:
                    if service.name not in self.services:
                        self.services[service.name] = []
                    self.services[service.name].append(service)

                self.logger.info(
                    f"Загружено {len(services)} активных сервисов"
                )

        except Exception as e:
            self.logger.error(f"Ошибка загрузки сервисов: {e}")

    async def _start_metrics_collection(self) -> None:
        """Запуск сбора метрик"""
        while True:
            try:
                await self._collect_all_metrics()
                await asyncio.sleep(self.metrics_collection_interval)
            except Exception as e:
                self.logger.error(f"Ошибка сбора метрик: {e}")
                await asyncio.sleep(5)

    async def _collect_all_metrics(self) -> None:
        """Сбор метрик всех сервисов"""
        try:
            with self.session_factory() as session:
                # Получаем метрики из базы данных
                metrics = (
                    session.query(LoadBalancingMetrics)
                    .filter(
                        LoadBalancingMetrics.timestamp
                        >= datetime.utcnow() - timedelta(minutes=5)
                    )
                    .all()
                )

                # Группируем метрики по сервисам
                service_metrics = {}
                for metric in metrics:
                    if metric.service_id not in service_metrics:
                        service_metrics[metric.service_id] = {
                            "response_times": [],
                            "throughput_values": [],
                            "error_rates": [],
                        }
                    service_metrics[metric.service_id][
                        "response_times"
                    ].append(metric.avg_response_time)
                    service_metrics[metric.service_id][
                        "throughput_values"
                    ].append(metric.throughput)
                    service_metrics[metric.service_id]["error_rates"].append(
                        metric.error_rate
                    )

                # Обновление метрик сервисов
                for service_id, metrics_data in service_metrics.items():
                    if metrics_data["response_times"]:
                        avg_response_time = statistics.mean(
                            metrics_data["response_times"]
                        )

                        # Обновление сервиса
                        service = next(
                            (
                                s
                                for s in self.services.get("default", [])
                                if s.id == service_id
                            ),
                            None,
                        )
                        if service:
                            # Обновляем метрики Prometheus
                            SERVICE_HEALTH.labels(service=service.name).set(
                                100 - avg_response_time
                            )

        except Exception as e:
            self.logger.error(f"Ошибка сбора метрик: {e}")

    async def register_service(self, service_request: ServiceRequest) -> bool:
        """Регистрация нового сервиса"""
        try:
            service_id = str(uuid.uuid4())

            service = ServiceEndpoint(
                id=service_id,
                name=service_request.name,
                url=service_request.url,
                port=service_request.port,
                protocol=service_request.protocol,
                weight=service_request.weight,
                max_connections=service_request.max_connections,
                health_check_url=service_request.health_check_url,
                health_check_interval=service_request.health_check_interval,
            )

            with self.session_factory() as session:
                session.add(service)
                session.commit()

            # Добавляем в кэш (отсоединяем от сессии)
            if service_request.name not in self.services:
                self.services[service_request.name] = []

            # Создаем копию объекта без привязки к сессии
            from sqlalchemy.orm import make_transient

            make_transient(service)
            self.services[service_request.name].append(service)

            self.logger.info(f"Сервис {service_request.name} зарегистрирован")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка регистрации сервиса: {e}")
            return False

    async def unregister_service(self, service_id: str) -> bool:
        """Отмена регистрации сервиса"""
        try:
            with self.session_factory() as session:
                service = (
                    session.query(ServiceEndpoint)
                    .filter(ServiceEndpoint.id == service_id)
                    .first()
                )

                if service:
                    service.is_active = False
                    session.commit()

                    # Удаляем из кэша
                    for service_list in self.services.values():
                        service_list[:] = [
                            s for s in service_list if s.id != service_id
                        ]

                    self.logger.info(f"Сервис {service_id} отключен")
                    return True

                return False

        except Exception as e:
            self.logger.error(f"Ошибка отключения сервиса {service_id}: {e}")
            return False

    async def balance_load(
        self, request: LoadBalancingRequest
    ) -> Optional[LoadBalancingResponse]:
        """
        Балансировка нагрузки для запроса

        Args:
            request: Запрос на балансировку

        Returns:
            Ответ с выбранным сервисом
        """
        try:
            # Получаем доступные сервисы
            available_services = self.services.get(request.service_name, [])
            if not available_services:
                self.logger.warning(
                    f"Нет доступных сервисов для {request.service_name}"
                )
                return None

            # Выбираем алгоритм
            algorithm = self.algorithms.get(
                request.algorithm.value
                if request.algorithm
                else self.current_algorithm.value
            )

            if not algorithm:
                self.logger.error(f"Алгоритм {request.algorithm} не найден")
                return None

            # Выбираем сервис
            selected_service = await algorithm.select_service(
                available_services, request
            )

            if not selected_service:
                self.logger.warning("Не удалось выбрать сервис")
                return None

            # Создаем ответ
            session_id = request.session_id or str(uuid.uuid4())

            response = LoadBalancingResponse(
                service_url=(
                    f"{selected_service.protocol}://"
                    f"{selected_service.url}:{selected_service.port}"
                ),
                service_id=selected_service.id,
                algorithm_used=request.algorithm or self.current_algorithm,
                session_id=session_id,
                load_factor=1.0,  # Упрощенная реализация
                health_score=100.0,  # Упрощенная реализация
                response_time=None,
                timestamp=datetime.utcnow(),
            )

            # Обновляем метрики
            REQUEST_COUNT.labels(
                algorithm=algorithm.get_algorithm_name(),
                service=selected_service.name,
                status="success",
            ).inc()

            return response

        except Exception as e:
            self.logger.error(f"Ошибка балансировки нагрузки: {e}")
            return None

    async def check_service_health(
        self, service_id: str
    ) -> Optional[HealthCheckResponse]:
        """Проверка здоровья сервиса"""
        try:
            # Находим сервис
            service = None
            for service_list in self.services.values():
                for s in service_list:
                    if s.id == service_id:
                        service = s
                        break
                if service:
                    break

            if not service:
                return None

            # Выполняем проверку здоровья
            start_time = time.time()

            try:
                health_url = (
                    f"{service.protocol}://{service.url}:"
                    f"{service.port}{service.health_check_url}"
                )

                async with self.http_client.get(health_url) as response:
                    response_time = time.time() - start_time

                    is_healthy = response.status == 200

                    return HealthCheckResponse(
                        service_id=service_id,
                        is_healthy=is_healthy,
                        response_time=response_time,
                        status_code=response.status,
                        error_message=(
                            None if is_healthy else f"HTTP {response.status}"
                        ),
                        metrics={},
                        timestamp=datetime.utcnow(),
                    )

            except Exception as e:
                response_time = time.time() - start_time

                return HealthCheckResponse(
                    service_id=service_id,
                    is_healthy=False,
                    response_time=response_time,
                    status_code=None,
                    error_message=str(e),
                    metrics={},
                    timestamp=datetime.utcnow(),
                )

        except Exception as e:
            self.logger.error(
                f"Ошибка проверки здоровья сервиса {service_id}: {e}"
            )
            return None

    def set_algorithm(self, algorithm: LoadBalancingAlgorithm) -> bool:
        """Установка алгоритма балансировки нагрузки"""
        try:
            if algorithm.value in self.algorithms:
                self.current_algorithm = algorithm
                self.logger.info(f"Алгоритм изменен на {algorithm.value}")
                return True
            else:
                self.logger.error(
                    f"Алгоритм {algorithm.value} не поддерживается"
                )
                return False
        except Exception as e:
            self.logger.error(f"Ошибка установки алгоритма: {e}")
            return False

    async def get_metrics(self) -> Dict[str, Any]:
        """Получение метрик балансировщика"""
        try:
            metrics = {
                "total_services": sum(
                    len(services) for services in self.services.values()
                ),
                "active_services": sum(
                    len([s for s in services if s.is_active])
                    for services in self.services.values()
                ),
                "current_algorithm": self.current_algorithm.value,
                "available_algorithms": list(self.algorithms.keys()),
                "metrics_enabled": self.metrics_enabled,
            }

            return metrics

        except Exception as e:
            self.logger.error(f"Ошибка получения метрик: {e}")
            return {}

    async def shutdown(self) -> None:
        """Завершение работы балансировщика"""
        try:
            # Останавливаем сбор метрик
            if self.metrics_task:
                self.metrics_task.cancel()
                try:
                    await self.metrics_task
                except asyncio.CancelledError:
                    pass

            # Закрываем HTTP клиент
            if self.http_client:
                await self.http_client.close()

            # Закрываем соединения с базой данных
            if self.engine:
                self.engine.dispose()

            self.logger.info("LoadBalancer завершил работу")

        except Exception as e:
            self.logger.error(f"Ошибка завершения работы: {e}")


# FastAPI приложение
app = FastAPI(
    title="LoadBalancer API",
    description="API для балансировки нагрузки",
    version="2.0.0",
)

# Глобальный экземпляр балансировщика
load_balancer = None


@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске"""
    global load_balancer
    load_balancer = LoadBalancer()
    await load_balancer.initialize()


@app.on_event("shutdown")
async def shutdown_event():
    """Завершение при остановке"""
    global load_balancer
    if load_balancer:
        await load_balancer.shutdown()


@app.get("/health")
async def health_check():
    """Проверка здоровья API"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}


@app.get("/metrics")
async def get_metrics():
    """Получение метрик Prometheus"""
    return generate_latest()


@app.post("/services", response_model=dict)
async def register_service(service_request: ServiceRequest):
    """Регистрация нового сервиса"""
    if not load_balancer:
        return {"error": "LoadBalancer не инициализирован"}

    success = await load_balancer.register_service(service_request)
    return {"success": success}


@app.delete("/services/{service_id}")
async def unregister_service(service_id: str):
    """Отмена регистрации сервиса"""
    if not load_balancer:
        return {"error": "LoadBalancer не инициализирован"}

    success = await load_balancer.unregister_service(service_id)
    return {"success": success}


@app.post("/balance", response_model=LoadBalancingResponse)
async def balance_load(request: LoadBalancingRequest):
    """Балансировка нагрузки"""
    if not load_balancer:
        return {"error": "LoadBalancer не инициализирован"}

    result = await load_balancer.balance_load(request)
    if not result:
        return {"error": "Не удалось выполнить балансировку"}

    return result


@app.get("/services/{service_id}/health")
async def check_service_health(service_id: str):
    """Проверка здоровья сервиса"""
    if not load_balancer:
        return {"error": "LoadBalancer не инициализирован"}

    result = await load_balancer.check_service_health(service_id)
    if not result:
        return {"error": "Сервис не найден"}

    return result


@app.get("/metrics/summary")
async def get_metrics_summary():
    """Получение сводки метрик"""
    if not load_balancer:
        return {"error": "LoadBalancer не инициализирован"}

    return await load_balancer.get_metrics()


if __name__ == "__main__":
    uvicorn.run("load_balancer:app", host="0.0.0.0", port=8006, reload=True)
