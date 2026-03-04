#!/usr/bin/env python3
"""
ALADDIN VPN - Graceful Degradation System
Система graceful degradation для VPN системы

Автор: ALADDIN Security Team
Версия: 1.0.0
Дата: 01.10.2025
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
from enum import Enum
from contextlib import asynccontextmanager
from functools import wraps


# Настройка логирования
logger = logging.getLogger(__name__)

# ============================================================================
# УРОВНИ ДЕГРАДАЦИИ
# ============================================================================


class DegradationLevel(Enum):
    """Уровни деградации системы"""
    FULL = "full"                    # Полная функциональность
    REDUCED = "reduced"              # Сниженная функциональность
    MINIMAL = "minimal"              # Минимальная функциональность
    EMERGENCY = "emergency"          # Аварийный режим
    OFFLINE = "offline"              # Система недоступна


class ServiceStatus(Enum):
    """Статусы сервисов"""
    HEALTHY = "healthy"              # Сервис работает нормально
    DEGRADED = "degraded"            # Сервис работает с ограничениями
    UNHEALTHY = "unhealthy"          # Сервис работает нестабильно
    DOWN = "down"                    # Сервис недоступен

# ============================================================================
# КОНФИГУРАЦИЯ ДЕГРАДАЦИИ
# ============================================================================

@dataclass
class ServiceConfig:
    """Конфигурация сервиса для graceful degradation"""
    name: str
    priority: int = 1  # 1 = высший приоритет
    fallback_function: Optional[Callable] = None
    degraded_function: Optional[Callable] = None
    health_check: Optional[Callable] = None
    timeout: float = 5.0
    retry_count: int = 3
    cooldown: float = 30.0  # Время до следующей попытки
    dependencies: List[str] = field(default_factory=list)
    required_for_levels: List[DegradationLevel] = field(default_factory=lambda: [DegradationLevel.FULL])

@dataclass
class DegradationRule:
    """Правило деградации"""
    condition: Callable[[Dict[str, Any]], bool]
    target_level: DegradationLevel
    message: str
    auto_recovery: bool = True
    recovery_condition: Optional[Callable[[Dict[str, Any]], bool]] = None

# ============================================================================
# ОСНОВНОЙ КЛАСС GRACEFUL DEGRADATION
# ============================================================================


class GracefulDegradationManager:
    """Менеджер graceful degradation"""

    def __init__(self):
        self.services: Dict[str, ServiceConfig] = {}
        self.service_status: Dict[str, ServiceStatus] = {}
        self.degradation_rules: List[DegradationRule] = []
        self.current_level = DegradationLevel.FULL
        self.last_health_check = {}
        self.service_metrics: Dict[str, Dict[str, Any]] = {}
        self.fallback_responses: Dict[str, Any] = {}

        # Настройки мониторинга
        self.health_check_interval = 30.0
        self.metrics_window = 300.0  # 5 минут
        self._monitoring_task = None
        self._is_monitoring = False

    def register_service(self, config: ServiceConfig):
        """Регистрация сервиса"""
        self.services[config.name] = config
        self.service_status[config.name] = ServiceStatus.HEALTHY
        self.service_metrics[config.name] = {
            "success_count": 0,
            "failure_count": 0,
            "response_times": [],
            "last_success": None,
            "last_failure": None
        }
        logger.info(f"Registered service: {config.name}")

    def add_degradation_rule(self, rule: DegradationRule):
        """Добавление правила деградации"""
        self.degradation_rules.append(rule)
        logger.info(f"Added degradation rule: {rule.message}")

    def get_service_status(self, service_name: str) -> ServiceStatus:
        """Получение статуса сервиса"""
        return self.service_status.get(service_name, ServiceStatus.DOWN)

    def is_service_available(self, service_name: str) -> bool:
        """Проверка доступности сервиса"""
        status = self.get_service_status(service_name)
        return status in [ServiceStatus.HEALTHY, ServiceStatus.DEGRADED]

    def get_current_level(self) -> DegradationLevel:
        """Получение текущего уровня деградации"""
        return self.current_level

    def can_use_service(self, service_name: str) -> bool:
        """Проверка возможности использования сервиса"""
        if service_name not in self.services:
            return False

        service = self.services[service_name]
        current_level = self.get_current_level()

        # Проверяем, требуется ли сервис для текущего уровня
        if current_level not in service.required_for_levels:
            return False

        # Проверяем статус сервиса
        return self.is_service_available(service_name)

    async def execute_service(self, service_name: str, func: Callable, *args, **kwargs) -> Any:
        """Выполнение сервиса с graceful degradation"""
        if not self.can_use_service(service_name):
            return await self._handle_service_unavailable(service_name, func, *args, **kwargs)

        service = self.services[service_name]
        start_time = time.time()

        try:
            # Выполняем основную функцию
            if asyncio.iscoroutinefunction(func):
                result = await asyncio.wait_for(func(*args, **kwargs), timeout=service.timeout)
            else:
                result = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(None, func, *args, **kwargs),
                    timeout=service.timeout
                )

            # Обновляем метрики успеха
            self._update_success_metrics(service_name, time.time() - start_time)
            return result

        except asyncio.TimeoutError:
            self._update_failure_metrics(service_name, "timeout")
            logger.warning(f"Service {service_name} timed out")
            return await self._handle_service_failure(service_name, func, *args, **kwargs)

        except Exception as e:
            self._update_failure_metrics(service_name, str(e))
            logger.error(f"Service {service_name} failed: {e}")
            return await self._handle_service_failure(service_name, func, *args, **kwargs)

    async def _handle_service_unavailable(self, service_name: str, func: Callable, *args, **kwargs) -> Any:
        """Обработка недоступного сервиса"""
        service = self.services[service_name]

        # Пытаемся использовать fallback функцию
        if service.fallback_function:
            try:
                if asyncio.iscoroutinefunction(service.fallback_function):
                    return await service.fallback_function(*args, **kwargs)
                else:
                    return service.fallback_function(*args, **kwargs)
            except Exception as e:
                logger.error(f"Fallback function for {service_name} failed: {e}")

        # Возвращаем кэшированный ответ, если есть
        if service_name in self.fallback_responses:
            logger.info(f"Using cached response for {service_name}")
            return self.fallback_responses[service_name]

        # Возвращаем дефолтный ответ
        return self._get_default_response(service_name)

    async def _handle_service_failure(self, service_name: str, func: Callable, *args, **kwargs) -> Any:
        """Обработка сбоя сервиса"""
        service = self.services[service_name]

        # Пытаемся использовать degraded функцию
        if service.degraded_function:
            try:
                if asyncio.iscoroutinefunction(service.degraded_function):
                    return await service.degraded_function(*args, **kwargs)
                else:
                    return service.degraded_function(*args, **kwargs)
            except Exception as e:
                logger.error(f"Degraded function for {service_name} failed: {e}")

        # Пытаемся использовать fallback функцию
        return await self._handle_service_unavailable(service_name, func, *args, **kwargs)

    def _get_default_response(self, service_name: str) -> Any:
        """Получение дефолтного ответа для сервиса"""
        default_responses = {
            "vpn_connection": {"status": "unavailable", "message": "VPN service temporarily unavailable"},
            "security_check": {"status": "bypassed", "message": "Security check temporarily disabled"},
            "monitoring": {"status": "offline", "message": "Monitoring service unavailable"},
            "database": {"status": "error", "message": "Database service unavailable"},
            "cache": {"status": "offline", "message": "Cache service unavailable"}
        }

        return default_responses.get(service_name, {"status": "error", "message": "Service unavailable"})

    def _update_success_metrics(self, service_name: str, response_time: float):
        """Обновление метрик успеха"""
        metrics = self.service_metrics[service_name]
        metrics["success_count"] += 1
        metrics["last_success"] = time.time()
        metrics["response_times"].append(response_time)

        # Ограничиваем размер списка времен ответа
        if len(metrics["response_times"]) > 100:
            metrics["response_times"] = metrics["response_times"][-100:]

        # Обновляем статус сервиса
        if self.service_status[service_name] != ServiceStatus.HEALTHY:
            self.service_status[service_name] = ServiceStatus.HEALTHY
            logger.info(f"Service {service_name} recovered")

    def _update_failure_metrics(self, service_name: str, error: str):
        """Обновление метрик сбоя"""
        metrics = self.service_metrics[service_name]
        metrics["failure_count"] += 1
        metrics["last_failure"] = time.time()

        # Обновляем статус сервиса
        failure_rate = metrics["failure_count"] / (metrics["success_count"] + metrics["failure_count"])
        if failure_rate > 0.5:
            self.service_status[service_name] = ServiceStatus.UNHEALTHY
        else:
            self.service_status[service_name] = ServiceStatus.DEGRADED

    async def check_service_health(self, service_name: str) -> bool:
        """Проверка здоровья сервиса"""
        if service_name not in self.services:
            return False

        service = self.services[service_name]
        if not service.health_check:
            return True

        try:
            if asyncio.iscoroutinefunction(service.health_check):
                result = await asyncio.wait_for(service.health_check(), timeout=service.timeout)
            else:
                result = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(None, service.health_check),
                    timeout=service.timeout
                )

            return bool(result)

        except Exception as e:
            logger.error(f"Health check failed for {service_name}: {e}")
            return False

    async def evaluate_degradation_level(self):
        """Оценка уровня деградации"""
        system_metrics = self._collect_system_metrics()

        for rule in self.degradation_rules:
            if rule.condition(system_metrics):
                if rule.target_level != self.current_level:
                    logger.warning(f"Degradation level changed to {rule.target_level}: {rule.message}")
                    self.current_level = rule.target_level
                return

        # Если все правила не сработали, проверяем возможность восстановления
        if self.current_level != DegradationLevel.FULL:
            if self._can_recover():
                logger.info("System recovered to full functionality")
                self.current_level = DegradationLevel.FULL

    def _collect_system_metrics(self) -> Dict[str, Any]:
        """Сбор системных метрик"""
        metrics = {
            "current_level": self.current_level,
            "service_status": dict(self.service_status),
            "service_metrics": dict(self.service_metrics),
            "timestamp": time.time()
        }

        # Добавляем метрики производительности
        for service_name, service_metrics in self.service_metrics.items():
            if service_metrics["response_times"]:
                metrics[f"{service_name}_avg_response_time"] = (
                    sum(service_metrics["response_times"]) /
                    len(service_metrics["response_times"])
                )
                metrics[f"{service_name}_success_rate"] = (
                    service_metrics["success_count"] /
                    (service_metrics["success_count"] + service_metrics["failure_count"])
                )

        return metrics

    def _can_recover(self) -> bool:
        """Проверка возможности восстановления"""
        # Проверяем, что все критичные сервисы работают
        for service_name, service in self.services.items():
            if DegradationLevel.FULL in service.required_for_levels:
                if not self.is_service_available(service_name):
                    return False

        return True

    async def start_monitoring(self):
        """Запуск мониторинга"""
        if self._is_monitoring:
            return

        self._is_monitoring = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Started graceful degradation monitoring")

    async def stop_monitoring(self):
        """Остановка мониторинга"""
        if not self._is_monitoring:
            return

        self._is_monitoring = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass

        logger.info("Stopped graceful degradation monitoring")

    async def _monitoring_loop(self):
        """Цикл мониторинга"""
        while self._is_monitoring:
            try:
                # Проверяем здоровье всех сервисов
                for service_name in self.services:
                    health = await self.check_service_health(service_name)
                    if not health and self.service_status[service_name] != ServiceStatus.DOWN:
                        self.service_status[service_name] = ServiceStatus.DOWN
                        logger.warning(f"Service {service_name} is down")

                # Оцениваем уровень деградации
                await self.evaluate_degradation_level()

                # Ждем следующую проверку
                await asyncio.sleep(self.health_check_interval)

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)  # Короткая пауза при ошибке

# ============================================================================
# ДЕКОРАТОРЫ
# ============================================================================


def graceful_degradation(service_name: str, manager: GracefulDegradationManager = None):
    """Декоратор для graceful degradation"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if manager:
                return await manager.execute_service(service_name, func, *args, **kwargs)
            else:
                return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            if manager:
                # Для синхронных функций создаем новый event loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return loop.run_until_complete(manager.execute_service(service_name, func, *args, **kwargs))
                finally:
                    loop.close()
            else:
                return func(*args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator

# ============================================================================
# КОНТЕКСТНЫЕ МЕНЕДЖЕРЫ
# ============================================================================

@asynccontextmanager
async def degradation_context(manager: GracefulDegradationManager):
    """Контекстный менеджер для graceful degradation"""
    await manager.start_monitoring()
    try:
        yield manager
    finally:
        await manager.stop_monitoring()

# ============================================================================
# ПРЕДУСТАНОВЛЕННЫЕ ПРАВИЛА ДЕГРАДАЦИИ
# ============================================================================


def create_default_degradation_rules() -> List[DegradationRule]:
    """Создание предустановленных правил деградации"""
    rules = [
        # Правило для высокой нагрузки на CPU
        DegradationRule(
            condition=lambda metrics: any(
                metrics.get(f"{service}_avg_response_time", 0) > 5.0
                for service in ["vpn_connection", "security_check", "monitoring"]
            ),
            target_level=DegradationLevel.REDUCED,
            message="High response times detected, reducing functionality",
            auto_recovery=True
        ),

        # Правило для недоступности критичных сервисов
        DegradationRule(
            condition=lambda metrics: any(
                metrics["service_status"].get(service) == ServiceStatus.DOWN
                for service in ["vpn_connection", "security_check"]
            ),
            target_level=DegradationLevel.MINIMAL,
            message="Critical services unavailable, minimal functionality only",
            auto_recovery=True
        ),

        # Правило для множественных сбоев
        DegradationRule(
            condition=lambda metrics: sum(
                1 for status in metrics["service_status"].values()
                if status in [ServiceStatus.UNHEALTHY, ServiceStatus.DOWN]
            ) >= 3,
            target_level=DegradationLevel.EMERGENCY,
            message="Multiple service failures, emergency mode activated",
            auto_recovery=True
        ),

        # Правило для полной недоступности
        DegradationRule(
            condition=lambda metrics: all(
                status == ServiceStatus.DOWN
                for status in metrics["service_status"].values()
            ),
            target_level=DegradationLevel.OFFLINE,
            message="All services down, system offline",
            auto_recovery=False
        )
    ]

    return rules

# ============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================================


def create_default_manager() -> GracefulDegradationManager:
    """Создание менеджера с предустановленными настройками"""
    manager = GracefulDegradationManager()

    # Добавляем предустановленные правила
    for rule in create_default_degradation_rules():
        manager.add_degradation_rule(rule)

    return manager


def get_degradation_status(manager: GracefulDegradationManager) -> Dict[str, Any]:
    """Получение статуса деградации"""
    return {
        "current_level": manager.get_current_level().value,
        "service_status": {name: status.value for name, status in manager.service_status.items()},
        "service_metrics": manager.service_metrics,
        "timestamp": time.time()
    }

# ============================================================================
# ЭКСПОРТ
# ============================================================================

__all__ = [
    # Основные классы
    "GracefulDegradationManager", "ServiceConfig", "DegradationRule",

    # Перечисления
    "DegradationLevel", "ServiceStatus",

    # Декораторы
    "graceful_degradation",

    # Контекстные менеджеры
    "degradation_context",

    # Предустановленные правила
    "create_default_degradation_rules", "create_default_manager",

    # Вспомогательные функции
    "get_degradation_status"
]
