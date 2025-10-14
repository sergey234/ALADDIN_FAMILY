# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Service Mesh Manager
Менеджер сервисной сетки для микросервисной архитектуры

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
"""

import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from core.base import ComponentStatus, SecurityBase


class ServiceStatus(Enum):
    """Статусы сервисов"""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    STARTING = "starting"
    STOPPING = "stopping"
    UNKNOWN = "unknown"


class ServiceType(Enum):
    """Типы сервисов"""

    SECURITY = "security"
    AI_AGENT = "ai_agent"
    BOT = "bot"
    INTERFACE = "interface"
    DATABASE = "database"
    CACHE = "cache"
    API = "api"
    MONITORING = "monitoring"


class LoadBalancingStrategy(Enum):
    """Стратегии балансировки нагрузки"""

    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_RESPONSE_TIME = "least_response_time"
    RANDOM = "random"


@dataclass
class ServiceEndpoint:
    """Конечная точка сервиса"""

    service_id: str
    host: str
    port: int
    protocol: str
    path: str
    weight: int = 1
    health_check_url: Optional[str] = None
    last_health_check: Optional[datetime] = None
    is_healthy: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return asdict(self)

    def get_url(self) -> str:
        """Получение полного URL"""
        return f"{self.protocol}://{self.host}:{self.port}{self.path}"


@dataclass
class ServiceInfo:
    """Информация о сервисе"""

    service_id: str
    name: str
    description: str
    service_type: ServiceType
    version: str
    endpoints: List[ServiceEndpoint]
    dependencies: List[str]
    health_check_interval: int = 30
    timeout: int = 30
    retry_count: int = 3
    status: ServiceStatus = ServiceStatus.UNKNOWN
    created_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_updated is None:
            self.last_updated = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        data = asdict(self)
        data["service_type"] = self.service_type.value
        data["status"] = self.status.value
        data["created_at"] = (
            self.created_at.isoformat()
            if self.created_at
            else None if self.created_at else None
        )
        data["last_updated"] = (
            self.last_updated.isoformat() if self.last_updated else None
        )
        return data


@dataclass
class ServiceRequest:
    """Запрос к сервису"""

    request_id: str
    service_id: str
    method: str
    path: str
    headers: Dict[str, str]
    body: Optional[Any] = None
    timeout: int = 30
    retry_count: int = 0
    created_at: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        data = asdict(self)
        data["created_at"] = (
            self.created_at.isoformat() if self.created_at else None
        )
        return data


@dataclass
class ServiceResponse:
    """Ответ от сервиса"""

    request_id: str
    service_id: str
    status_code: int
    headers: Dict[str, str]
    body: Optional[Any] = None
    response_time: float = 0.0
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        data = asdict(self)
        data["created_at"] = (
            self.created_at.isoformat() if self.created_at else None
        )
        return data


class ServiceMeshManager(SecurityBase):
    """Менеджер сервисной сетки для микросервисной архитектуры"""

    def __init__(
        self,
        name: str = "ServiceMeshManager",
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(name, config)

        # Конфигурация сервисной сетки
        self.mesh_config = {
            "discovery_interval": 30,  # секунд
            "health_check_interval": 30,  # секунд
            "load_balancing_strategy": LoadBalancingStrategy.ROUND_ROBIN,
            "circuit_breaker_threshold": 5,
            "circuit_breaker_timeout": 60,  # секунд
            "request_timeout": 30,  # секунд
            "max_retries": 3,
            "enable_service_discovery": True,
            "enable_health_checks": True,
            "enable_load_balancing": True,
            "enable_circuit_breaker": True,
            "enable_metrics": True,
            "enable_tracing": True,
        }

        # Обновление конфигурации
        if config:
            self.mesh_config.update(config)

        # Реестр сервисов
        self.services: Dict[str, ServiceInfo] = {}
        self.service_endpoints: Dict[str, List[ServiceEndpoint]] = {}
        self.service_health: Dict[str, ServiceStatus] = {}
        self.service_metrics: Dict[str, Dict[str, Any]] = {}

        # Балансировка нагрузки
        self.load_balancers: Dict[str, Dict[str, Any]] = {}
        self.round_robin_counters: Dict[str, int] = {}

        # Circuit Breaker
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}

        # Очереди и пулы
        self.request_queue: List[ServiceRequest] = []
        self.response_queue: List[ServiceResponse] = []
        self.thread_pool = ThreadPoolExecutor(max_workers=20)

        # Мониторинг
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None

        # Блокировки
        self.services_lock = threading.RLock()
        self.queue_lock = threading.RLock()

        # Метрики
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.average_response_time = 0.0

        self.log_activity("ServiceMeshManager инициализирован")

    def initialize(self) -> bool:
        """Инициализация менеджера сервисной сетки"""
        try:
            self.log_activity("Инициализация ServiceMeshManager")
            self.status = ComponentStatus.INITIALIZING

            # Регистрация базовых сервисов
            self._register_basic_services()

            # Запуск мониторинга
            if self.mesh_config["enable_service_discovery"]:
                self._start_monitoring()

            self.status = ComponentStatus.RUNNING
            self.log_activity("ServiceMeshManager успешно инициализирован")
            return True

        except Exception as e:
            self.log_activity(
                f"Ошибка инициализации ServiceMeshManager: {e}", "error"
            )
            self.status = ComponentStatus.ERROR
            return False

    def _register_basic_services(self):
        """Регистрация базовых сервисов"""
        try:
            # Базовые сервисы безопасности
            basic_services = [
                {
                    "service_id": "security_core",
                    "name": "Security Core Service",
                    "description": "Основной сервис безопасности",
                    "service_type": ServiceType.SECURITY,
                    "version": "1.0.0",
                    "endpoints": [
                        ServiceEndpoint(
                            service_id="security_core",
                            host="localhost",
                            port=8001,
                            protocol="http",
                            path="/api/v1/security",
                            health_check_url="/health",
                        )
                    ],
                    "dependencies": [],
                },
                {
                    "service_id": "ai_agent_manager",
                    "name": "AI Agent Manager",
                    "description": "Менеджер AI агентов",
                    "service_type": ServiceType.AI_AGENT,
                    "version": "1.0.0",
                    "endpoints": [
                        ServiceEndpoint(
                            service_id="ai_agent_manager",
                            host="localhost",
                            port=8002,
                            protocol="http",
                            path="/api/v1/ai-agents",
                            health_check_url="/health",
                        )
                    ],
                    "dependencies": ["security_core"],
                },
                {
                    "service_id": "bot_manager",
                    "name": "Bot Manager",
                    "description": "Менеджер ботов безопасности",
                    "service_type": ServiceType.BOT,
                    "version": "1.0.0",
                    "endpoints": [
                        ServiceEndpoint(
                            service_id="bot_manager",
                            host="localhost",
                            port=8003,
                            protocol="http",
                            path="/api/v1/bots",
                            health_check_url="/health",
                        )
                    ],
                    "dependencies": ["security_core"],
                },
            ]

            for service_data in basic_services:
                service = ServiceInfo(**service_data)
                self.register_service(service)

            self.log_activity(
                f"Зарегистрировано {len(basic_services)} базовых сервисов"
            )

        except Exception as e:
            self.log_activity(
                f"Ошибка регистрации базовых сервисов: {e}", "error"
            )

    def register_service(self, service: ServiceInfo) -> bool:
        """Регистрация нового сервиса"""
        try:
            with self.services_lock:
                self.services[service.service_id] = service
                self.service_endpoints[service.service_id] = service.endpoints
                self.service_health[service.service_id] = ServiceStatus.UNKNOWN
                self.service_metrics[service.service_id] = {
                    "requests_count": 0,
                    "success_count": 0,
                    "error_count": 0,
                    "average_response_time": 0.0,
                    "last_request": None,
                }

                # Инициализация балансировщика нагрузки
                if self.mesh_config["enable_load_balancing"]:
                    self._initialize_load_balancer(service.service_id)

                # Инициализация Circuit Breaker
                if self.mesh_config["enable_circuit_breaker"]:
                    self._initialize_circuit_breaker(service.service_id)

                self.log_activity(
                    f"Сервис {service.service_id} зарегистрирован"
                )
                return True

        except Exception as e:
            self.log_activity(
                f"Ошибка регистрации сервиса {service.service_id}: {e}",
                "error",
            )
            return False

    def unregister_service(self, service_id: str) -> bool:
        """Отмена регистрации сервиса"""
        try:
            with self.services_lock:
                if service_id in self.services:
                    del self.services[service_id]
                    del self.service_endpoints[service_id]
                    del self.service_health[service_id]
                    del self.service_metrics[service_id]

                    # Очистка балансировщика нагрузки
                    if service_id in self.load_balancers:
                        del self.load_balancers[service_id]

                    # Очистка Circuit Breaker
                    if service_id in self.circuit_breakers:
                        del self.circuit_breakers[service_id]

                    # Очистка счетчиков
                    if service_id in self.round_robin_counters:
                        del self.round_robin_counters[service_id]

                    self.log_activity(f"Сервис {service_id} отменен")
                    return True
                else:
                    self.log_activity(
                        f"Сервис {service_id} не найден", "warning"
                    )
                    return False

        except Exception as e:
            self.log_activity(
                f"Ошибка отмены регистрации сервиса {service_id}: {e}", "error"
            )
            return False

    def _initialize_load_balancer(self, service_id: str):
        """Инициализация балансировщика нагрузки"""
        try:
            strategy = self.mesh_config["load_balancing_strategy"]
            self.load_balancers[service_id] = {
                "strategy": strategy,
                "endpoints": self.service_endpoints[service_id].copy(),
                "weights": [
                    ep.weight for ep in self.service_endpoints[service_id]
                ],
                "last_used": 0,
            }

            # Инициализация счетчика для Round Robin
            if strategy == LoadBalancingStrategy.ROUND_ROBIN:
                self.round_robin_counters[service_id] = 0

        except Exception as e:
            self.log_activity(
                f"Ошибка инициализации балансировщика для {service_id}: {e}",
                "error",
            )

    def _initialize_circuit_breaker(self, service_id: str):
        """Инициализация Circuit Breaker"""
        try:
            self.circuit_breakers[service_id] = {
                "state": "closed",  # closed, open, half-open
                "failure_count": 0,
                "last_failure_time": None,
                "threshold": self.mesh_config["circuit_breaker_threshold"],
                "timeout": self.mesh_config["circuit_breaker_timeout"],
            }

        except Exception as e:
            self.log_activity(
                f"Ошибка инициализации Circuit Breaker для {service_id}: {e}",
                "error",
            )

    def _start_monitoring(self):
        """Запуск мониторинга сервисов"""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop, daemon=True
        )
        self.monitoring_thread.start()
        self.log_activity("Мониторинг сервисов запущен")

    def _monitoring_loop(self):
        """Цикл мониторинга сервисов"""
        while self.monitoring_active:
            try:
                # Проверка здоровья сервисов
                if self.mesh_config["enable_health_checks"]:
                    self._perform_health_checks()

                # Обновление метрик
                if self.mesh_config["enable_metrics"]:
                    self._update_metrics()

                # Ожидание до следующей проверки
                time.sleep(self.mesh_config["discovery_interval"])

            except Exception as e:
                self.log_activity(f"Ошибка в цикле мониторинга: {e}", "error")
                time.sleep(5)  # Пауза при ошибке

    def _perform_health_checks(self):
        """Выполнение проверок здоровья сервисов"""
        try:
            for service_id, service in self.services.items():
                if service.health_check_interval > 0:
                    # Проверка времени последней проверки
                    last_check = service.last_updated
                    if (
                        last_check
                        and (datetime.now() - last_check).seconds
                        >= service.health_check_interval
                    ):
                        self._check_service_health(service_id)

        except Exception as e:
            self.log_activity(
                f"Ошибка проверки здоровья сервисов: {e}", "error"
            )

    def _check_service_health(self, service_id: str):
        """Проверка здоровья конкретного сервиса"""
        try:
            if service_id not in self.service_endpoints:
                return

            endpoints = self.service_endpoints[service_id]
            healthy_endpoints = 0

            for endpoint in endpoints:
                if endpoint.health_check_url:
                    # Имитация проверки здоровья
                    is_healthy = self._simulate_health_check(endpoint)
                    endpoint.is_healthy = is_healthy
                    endpoint.last_health_check = datetime.now()

                    if is_healthy:
                        healthy_endpoints += 1

            # Обновление статуса сервиса
            if healthy_endpoints == 0:
                self.service_health[service_id] = ServiceStatus.UNHEALTHY
            elif healthy_endpoints < len(endpoints):
                self.service_health[service_id] = ServiceStatus.DEGRADED
            else:
                self.service_health[service_id] = ServiceStatus.HEALTHY

            # Обновление времени последней проверки
            if service_id in self.services:
                self.services[service_id].last_updated = datetime.now()

        except Exception as e:
            self.log_activity(
                f"Ошибка проверки здоровья сервиса {service_id}: {e}", "error"
            )
            self.service_health[service_id] = ServiceStatus.UNHEALTHY

    def _simulate_health_check(self, endpoint: ServiceEndpoint) -> bool:
        """Имитация проверки здоровья конечной точки"""
        try:
            # Имитация HTTP запроса к health check endpoint
            # В реальной реализации здесь был бы HTTP запрос
            import random

            return random.random() > 0.1  # 90% вероятность успеха

        except Exception:
            return False

    def _update_metrics(self):
        """Обновление метрик сервисов"""
        try:
            for service_id in self.services:
                if service_id in self.service_metrics:
                    metrics = self.service_metrics[service_id]

                    # Обновление среднего времени отклика
                    if metrics["requests_count"] > 0:
                        metrics["average_response_time"] = (
                            metrics.get("total_response_time", 0)
                            / metrics["requests_count"]
                        )

                    # Обновление процента успешных запросов
                    if metrics["requests_count"] > 0:
                        metrics["success_rate"] = (
                            metrics["success_count"]
                            / metrics["requests_count"]
                            * 100
                        )

        except Exception as e:
            self.log_activity(f"Ошибка обновления метрик: {e}", "error")

    def get_service_endpoint(
        self, service_id: str
    ) -> Optional[ServiceEndpoint]:
        """Получение конечной точки сервиса с балансировкой нагрузки"""
        try:
            if service_id not in self.service_endpoints:
                return None

            endpoints = self.service_endpoints[service_id]
            if not endpoints:
                return None

            # Проверка Circuit Breaker
            if self.mesh_config["enable_circuit_breaker"]:
                if not self._is_circuit_breaker_closed(service_id):
                    return None

            # Фильтрация здоровых конечных точек
            healthy_endpoints = [ep for ep in endpoints if ep.is_healthy]
            if not healthy_endpoints:
                return None

            # Выбор конечной точки по стратегии балансировки
            strategy = self.mesh_config["load_balancing_strategy"]

            if strategy == LoadBalancingStrategy.ROUND_ROBIN:
                return self._round_robin_selection(
                    service_id, healthy_endpoints
                )
            elif strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
                return self._least_connections_selection(
                    service_id, healthy_endpoints
                )
            elif strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
                return self._weighted_round_robin_selection(
                    service_id, healthy_endpoints
                )
            elif strategy == LoadBalancingStrategy.LEAST_RESPONSE_TIME:
                return self._least_response_time_selection(
                    service_id, healthy_endpoints
                )
            elif strategy == LoadBalancingStrategy.RANDOM:
                return self._random_selection(healthy_endpoints)
            else:
                return healthy_endpoints[0]

        except Exception as e:
            self.log_activity(
                f"Ошибка получения конечной точки сервиса {service_id}: {e}",
                "error",
            )
            return None

    def _round_robin_selection(
        self, service_id: str, endpoints: List[ServiceEndpoint]
    ) -> Optional[ServiceEndpoint]:
        """Выбор конечной точки по алгоритму Round Robin"""
        try:
            if service_id not in self.round_robin_counters:
                self.round_robin_counters[service_id] = 0

            index = self.round_robin_counters[service_id] % len(endpoints)
            self.round_robin_counters[service_id] += 1

            return endpoints[index]

        except Exception as e:
            self.log_activity(
                f"Ошибка Round Robin выбора для {service_id}: {e}", "error"
            )
            return endpoints[0] if endpoints else None

    def _least_connections_selection(
        self, service_id: str, endpoints: List[ServiceEndpoint]
    ) -> Optional[ServiceEndpoint]:
        """Выбор конечной точки с наименьшим количеством соединений"""
        try:
            # Имитация подсчета соединений
            min_connections = float("inf")
            selected_endpoint = endpoints[0]

            for endpoint in endpoints:
                # Имитация количества соединений
                connections = hash(endpoint.host + str(endpoint.port)) % 100
                if connections < min_connections:
                    min_connections = connections
                    selected_endpoint = endpoint

            return selected_endpoint

        except Exception as e:
            self.log_activity(
                f"Ошибка Least Connections выбора для {service_id}: {e}",
                "error",
            )
            return endpoints[0] if endpoints else None

    def _weighted_round_robin_selection(
        self, service_id: str, endpoints: List[ServiceEndpoint]
    ) -> Optional[ServiceEndpoint]:
        """Выбор конечной точки по взвешенному Round Robin"""
        try:
            if service_id not in self.round_robin_counters:
                self.round_robin_counters[service_id] = 0

            # Вычисление весов
            total_weight = sum(ep.weight for ep in endpoints)
            if total_weight == 0:
                return endpoints[0]

            # Выбор по весу
            current_weight = 0
            counter = self.round_robin_counters[service_id]

            for endpoint in endpoints:
                current_weight += endpoint.weight
                if counter < current_weight:
                    self.round_robin_counters[service_id] += 1
                    return endpoint

            # Fallback
            self.round_robin_counters[service_id] += 1
            return endpoints[0]

        except Exception as e:
            self.log_activity(
                f"Ошибка Weighted Round Robin выбора для {service_id}: {e}",
                "error",
            )
            return endpoints[0] if endpoints else None

    def _least_response_time_selection(
        self, service_id: str, endpoints: List[ServiceEndpoint]
    ) -> Optional[ServiceEndpoint]:
        """Выбор конечной точки с наименьшим временем отклика"""
        try:
            min_response_time = float("inf")
            selected_endpoint = endpoints[0]

            for endpoint in endpoints:
                # Имитация времени отклика
                response_time = hash(endpoint.host + str(endpoint.port)) % 1000
                if response_time < min_response_time:
                    min_response_time = response_time
                    selected_endpoint = endpoint

            return selected_endpoint

        except Exception as e:
            self.log_activity(
                f"Ошибка Least Response Time выбора для {service_id}: {e}",
                "error",
            )
            return endpoints[0] if endpoints else None

    def _random_selection(
        self, endpoints: List[ServiceEndpoint]
    ) -> Optional[ServiceEndpoint]:
        """Случайный выбор конечной точки"""
        try:
            import random

            return random.choice(endpoints)

        except Exception as e:
            self.log_activity(f"Ошибка случайного выбора: {e}", "error")
            return endpoints[0] if endpoints else None

    def _is_circuit_breaker_closed(self, service_id: str) -> bool:
        """Проверка состояния Circuit Breaker"""
        try:
            if service_id not in self.circuit_breakers:
                return True

            cb = self.circuit_breakers[service_id]

            if cb["state"] == "closed":
                return True
            elif cb["state"] == "open":
                # Проверка таймаута
                if cb["last_failure_time"]:
                    time_since_failure = (
                        datetime.now() - cb["last_failure_time"]
                    ).seconds
                    if time_since_failure >= cb["timeout"]:
                        cb["state"] = "half-open"
                        return True
                return False
            elif cb["state"] == "half-open":
                return True

            return True

        except Exception as e:
            self.log_activity(
                f"Ошибка проверки Circuit Breaker для {service_id}: {e}",
                "error",
            )
            return True

    def _update_circuit_breaker(self, service_id: str, success: bool):
        """Обновление состояния Circuit Breaker"""
        try:
            if service_id not in self.circuit_breakers:
                return

            cb = self.circuit_breakers[service_id]

            if success:
                if cb["state"] == "half-open":
                    cb["state"] = "closed"
                    cb["failure_count"] = 0
            else:
                cb["failure_count"] += 1
                cb["last_failure_time"] = datetime.now()

                if cb["failure_count"] >= cb["threshold"]:
                    cb["state"] = "open"

        except Exception as e:
            self.log_activity(
                f"Ошибка обновления Circuit Breaker для {service_id}: {e}",
                "error",
            )

    def send_request(
        self,
        service_id: str,
        method: str,
        path: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Any] = None,
    ) -> Optional[ServiceResponse]:
        """Отправка запроса к сервису"""
        try:
            # Получение конечной точки
            endpoint = self.get_service_endpoint(service_id)
            if not endpoint:
                self.log_activity(
                    f"Не удалось получить конечную точку для сервиса {service_id}",
                    "error",
                )
                return None

            # Создание запроса
            request_id = f"{service_id}_{int(time.time() * 1000)}"
            request = ServiceRequest(
                request_id=request_id,
                service_id=service_id,
                method=method,
                path=path,
                headers=headers or {},
                body=body,
            )

            # Отправка запроса
            start_time = time.time()
            response = self._execute_request(request, endpoint)
            response_time = time.time() - start_time

            if response:
                response.response_time = response_time

                # Обновление метрик
                self._update_request_metrics(service_id, response)

                # Обновление Circuit Breaker
                if self.mesh_config["enable_circuit_breaker"]:
                    self._update_circuit_breaker(
                        service_id, response.status_code < 400
                    )

            return response

        except Exception as e:
            self.log_activity(
                f"Ошибка отправки запроса к сервису {service_id}: {e}", "error"
            )
            return None

    def _execute_request(
        self, request: ServiceRequest, endpoint: ServiceEndpoint
    ) -> Optional[ServiceResponse]:
        """Выполнение HTTP запроса"""
        try:
            # Имитация HTTP запроса
            # В реальной реализации здесь был бы HTTP клиент

            # Имитация ответа
            import random

            status_code = 200 if random.random() > 0.1 else 500
            error_message = (
                None if status_code < 400 else "Internal Server Error"
            )

            response = ServiceResponse(
                request_id=request.request_id,
                service_id=request.service_id,
                status_code=status_code,
                headers={"Content-Type": "application/json"},
                body={"message": "Success"} if status_code < 400 else None,
                error_message=error_message,
            )

            return response

        except Exception as e:
            self.log_activity(
                f"Ошибка выполнения запроса {request.request_id}: {e}", "error"
            )
            return None

    def _update_request_metrics(
        self, service_id: str, response: ServiceResponse
    ):
        """Обновление метрик запросов"""
        try:
            if service_id not in self.service_metrics:
                return

            metrics = self.service_metrics[service_id]
            metrics["requests_count"] += 1
            metrics["last_request"] = datetime.now()

            if response.status_code < 400:
                metrics["success_count"] += 1
                self.successful_requests += 1
            else:
                metrics["error_count"] += 1
                self.failed_requests += 1

            # Обновление общего времени отклика
            if "total_response_time" not in metrics:
                metrics["total_response_time"] = 0
            metrics["total_response_time"] += response.response_time

            # Обновление общих метрик
            self.total_requests += 1
            self.average_response_time = (
                self.average_response_time * (self.total_requests - 1)
                + response.response_time
            ) / self.total_requests

        except Exception as e:
            self.log_activity(
                f"Ошибка обновления метрик для {service_id}: {e}", "error"
            )

    def get_service_status(self, service_id: str) -> Optional[Dict[str, Any]]:
        """Получение статуса сервиса"""
        try:
            if service_id not in self.services:
                return None

            service = self.services[service_id]
            health = self.service_health.get(service_id, ServiceStatus.UNKNOWN)
            metrics = self.service_metrics.get(service_id, {})

            return {
                "service_id": service_id,
                "name": service.name,
                "status": health.value,
                "endpoints": [ep.to_dict() for ep in service.endpoints],
                "metrics": metrics,
                "dependencies": service.dependencies,
                "created_at": (
                    service.created_at.isoformat()
                    if service.created_at
                    else None
                ),
                "last_updated": (
                    service.last_updated.isoformat()
                    if service.last_updated
                    else None
                ),
            }

        except Exception as e:
            self.log_activity(
                f"Ошибка получения статуса сервиса {service_id}: {e}", "error"
            )
            return None

    def get_mesh_status(self) -> Dict[str, Any]:
        """Получение статуса сервисной сетки"""
        try:
            total_services = len(self.services)
            healthy_services = len(
                [
                    s
                    for s in self.service_health.values()
                    if s == ServiceStatus.HEALTHY
                ]
            )
            unhealthy_services = len(
                [
                    s
                    for s in self.service_health.values()
                    if s == ServiceStatus.UNHEALTHY
                ]
            )
            degraded_services = len(
                [
                    s
                    for s in self.service_health.values()
                    if s == ServiceStatus.DEGRADED
                ]
            )

            return {
                "mesh_name": self.name,
                "status": self.status.value,
                "total_services": total_services,
                "healthy_services": healthy_services,
                "unhealthy_services": unhealthy_services,
                "degraded_services": degraded_services,
                "total_requests": self.total_requests,
                "successful_requests": self.successful_requests,
                "failed_requests": self.failed_requests,
                "average_response_time": self.average_response_time,
                "configuration": self.mesh_config,
                "services": [
                    self.get_service_status(sid)
                    for sid in self.services.keys()
                ],
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            self.log_activity(
                f"Ошибка получения статуса сервисной сетки: {e}", "error"
            )
            return {}

    def stop(self) -> bool:
        """Остановка менеджера сервисной сетки"""
        try:
            self.log_activity("Остановка ServiceMeshManager")

            # Остановка мониторинга
            self.monitoring_active = False
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                self.monitoring_thread.join(timeout=5)

            # Закрытие пула потоков
            self.thread_pool.shutdown(wait=True)

            # Очистка данных
            with self.services_lock:
                self.services.clear()
                self.service_endpoints.clear()
                self.service_health.clear()
                self.service_metrics.clear()
                self.load_balancers.clear()
                self.circuit_breakers.clear()
                self.round_robin_counters.clear()

            self.status = ComponentStatus.STOPPED
            self.log_activity("ServiceMeshManager успешно остановлен")
            return True

        except Exception as e:
            self.log_activity(
                f"Ошибка остановки ServiceMeshManager: {e}", "error"
            )
            return False

    def get_status(self) -> Dict[str, Any]:
        """Получение статуса менеджера"""
        return {
            "name": self.name,
            "status": self.status.value,
            "security_level": self.security_level.value,
            "monitoring_active": self.monitoring_active,
            "total_services": len(self.services),
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "average_response_time": self.average_response_time,
            "configuration": self.mesh_config,
        }
