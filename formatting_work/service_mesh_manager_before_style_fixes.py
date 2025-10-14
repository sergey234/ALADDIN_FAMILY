# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Service Mesh Manager
Менеджер сервисной сетки для микросервисной архитектуры

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
"""

import asyncio
import json
import logging
import threading
import time
import weakref
import gc
import psutil
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

from core.base import ComponentStatus, SecurityBase


# ============================================================================
# КОНФИГУРАЦИЯ CIRCUIT BREAKER
# ============================================================================


@dataclass
class CircuitBreakerConfig:
    """Конфигурация Circuit Breaker для сервиса"""

    failure_threshold: int = 5  # Количество ошибок для открытия
    success_threshold: int = 3  # Количество успехов для закрытия
    timeout: int = 60  # Таймаут в секундах
    half_open_max_calls: int = 3  # Максимум вызовов в half-open состоянии
    failure_rate_threshold: float = 0.5  # Порог процента ошибок (0.0-1.0)
    slow_call_threshold: int = 5  # Порог медленных вызовов в секундах
    slow_call_rate_threshold: float = 0.5  # Порог процента медленных вызовов
    max_wait_duration: int = 300  # Максимальное время ожидания в секундах
    sliding_window_size: int = 100  # Размер скользящего окна для расчета
    minimum_number_of_calls: int = 10  # Минимум вызовов для расчета

    def __post_init__(self):
        """Валидация конфигурации после инициализации"""
        if self.failure_threshold < 1:
            raise ValueError("failure_threshold должен быть >= 1")
        if self.success_threshold < 1:
            raise ValueError("success_threshold должен быть >= 1")
        if self.timeout < 1:
            raise ValueError("timeout должен быть >= 1")
        if not 0.0 <= self.failure_rate_threshold <= 1.0:
            raise ValueError("failure_rate_threshold должен быть 0.0-1.0")
        if not 0.0 <= self.slow_call_rate_threshold <= 1.0:
            raise ValueError("slow_call_rate_threshold должен быть 0.0-1.0")

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "failure_threshold": self.failure_threshold,
            "success_threshold": self.success_threshold,
            "timeout": self.timeout,
            "half_open_max_calls": self.half_open_max_calls,
            "failure_rate_threshold": self.failure_rate_threshold,
            "slow_call_threshold": self.slow_call_threshold,
            "slow_call_rate_threshold": self.slow_call_rate_threshold,
            "max_wait_duration": self.max_wait_duration,
            "sliding_window_size": self.sliding_window_size,
            "minimum_number_of_calls": self.minimum_number_of_calls,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CircuitBreakerConfig":
        """Создание из словаря"""
        return cls(**data)

    @classmethod
    def get_default_config(cls) -> "CircuitBreakerConfig":
        """Получение конфигурации по умолчанию"""
        return cls()

    @classmethod
    def get_aggressive_config(cls) -> "CircuitBreakerConfig":
        """Получение агрессивной конфигурации (быстрое открытие)"""
        return cls(
            failure_threshold=3,
            success_threshold=2,
            timeout=30,
            failure_rate_threshold=0.3,
            slow_call_threshold=3,
        )

    @classmethod
    def get_conservative_config(cls) -> "CircuitBreakerConfig":
        """Получение консервативной конфигурации (медленное открытие)"""
        return cls(
            failure_threshold=10,
            success_threshold=5,
            timeout=120,
            failure_rate_threshold=0.7,
            slow_call_threshold=10,
        )


# ============================================================================
# УЛУЧШЕННЫЙ CIRCUIT BREAKER
# ============================================================================


class CircuitBreakerState(Enum):
    """Состояния Circuit Breaker"""

    CLOSED = "closed"  # Закрыт - нормальная работа
    OPEN = "open"  # Открыт - блокирует вызовы
    HALF_OPEN = "half_open"  # Полуоткрыт - тестирует сервис


@dataclass
class CircuitBreakerMetrics:
    """Метрики Circuit Breaker"""

    service_id: str
    state: CircuitBreakerState
    failure_count: int = 0
    success_count: int = 0
    total_calls: int = 0
    failure_rate: float = 0.0
    slow_call_count: int = 0
    slow_call_rate: float = 0.0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    state_changes: int = 0
    calls_blocked: int = 0
    calls_allowed: int = 0

    def calculate_rates(self) -> None:
        """Расчет процентов ошибок и медленных вызовов"""
        if self.total_calls > 0:
            self.failure_rate = self.failure_count / self.total_calls
            self.slow_call_rate = self.slow_call_count / self.total_calls

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "service_id": self.service_id,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "total_calls": self.total_calls,
            "failure_rate": self.failure_rate,
            "slow_call_count": self.slow_call_count,
            "slow_call_rate": self.slow_call_rate,
            "last_failure_time": (
                self.last_failure_time.isoformat()
                if self.last_failure_time
                else None
            ),
            "last_success_time": (
                self.last_success_time.isoformat()
                if self.last_success_time
                else None
            ),
            "state_changes": self.state_changes,
            "calls_blocked": self.calls_blocked,
            "calls_allowed": self.calls_allowed,
        }


class EnhancedCircuitBreaker:
    """Улучшенный Circuit Breaker с конфигурацией"""

    def __init__(self, service_id: str, config: CircuitBreakerConfig):
        self.service_id = service_id
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.metrics = CircuitBreakerMetrics(service_id, self.state)
        self.call_history: List[Dict[str, Any]] = []
        self.half_open_calls = 0
        self.last_state_change = datetime.now()

    def can_execute(self) -> bool:
        """Проверка возможности выполнения вызова"""
        now = datetime.now()

        if self.state == CircuitBreakerState.CLOSED:
            return True

        elif self.state == CircuitBreakerState.OPEN:
            # Проверка таймаута
            time_since_failure = (now - self.last_state_change).total_seconds()
            if time_since_failure >= self.config.timeout:
                self._transition_to_half_open()
                return True
            return False

        elif self.state == CircuitBreakerState.HALF_OPEN:
            # В half-open состоянии ограничиваем количество вызовов
            return self.half_open_calls < self.config.half_open_max_calls

        return False

    def record_success(self, response_time: float) -> None:
        """Запись успешного вызова"""
        now = datetime.now()
        self.metrics.success_count += 1
        self.metrics.total_calls += 1
        self.metrics.last_success_time = now

        # Проверка на медленный вызов
        if response_time > self.config.slow_call_threshold:
            self.metrics.slow_call_count += 1

        # Добавление в историю
        self.call_history.append(
            {
                "timestamp": now,
                "success": True,
                "response_time": response_time,
                "slow": response_time > self.config.slow_call_threshold,
            }
        )

        # Обновление метрик
        self._update_metrics()

        # Переход в закрытое состояние из half-open
        if (
            self.state == CircuitBreakerState.HALF_OPEN
            and self.metrics.success_count >= self.config.success_threshold
        ):
            self._transition_to_closed()

        # Сброс счетчика half-open вызовов
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.half_open_calls += 1

    def record_failure(
        self, error: Exception, response_time: float = 0.0
    ) -> None:
        """Запись неудачного вызова"""
        now = datetime.now()
        self.metrics.failure_count += 1
        self.metrics.total_calls += 1
        self.metrics.last_failure_time = now

        # Добавление в историю
        self.call_history.append(
            {
                "timestamp": now,
                "success": False,
                "response_time": response_time,
                "error": str(error),
                "slow": response_time > self.config.slow_call_threshold,
            }
        )

        # Обновление метрик
        self._update_metrics()

        # Проверка условий для открытия Circuit Breaker
        if self._should_open_circuit():
            self._transition_to_open()

        # Сброс счетчика half-open вызовов
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.half_open_calls = 0

    def _should_open_circuit(self) -> bool:
        """Проверка условий для открытия Circuit Breaker"""
        if self.metrics.total_calls < self.config.minimum_number_of_calls:
            return False

        # Проверка по количеству ошибок
        if self.metrics.failure_count >= self.config.failure_threshold:
            return True

        # Проверка по проценту ошибок
        if (
            self.metrics.failure_rate >= self.config.failure_rate_threshold
            and self.metrics.total_calls >= self.config.minimum_number_of_calls
        ):
            return True

        # Проверка по проценту медленных вызовов
        if (
            self.metrics.slow_call_rate >= self.config.slow_call_rate_threshold
            and self.metrics.total_calls >= self.config.minimum_number_of_calls
        ):
            return True

        return False

    def _transition_to_open(self) -> None:
        """Переход в открытое состояние"""
        if self.state != CircuitBreakerState.OPEN:
            self.state = CircuitBreakerState.OPEN
            self.metrics.state = CircuitBreakerState.OPEN
            self.metrics.state_changes += 1
            self.last_state_change = datetime.now()
            self.half_open_calls = 0

    def _transition_to_half_open(self) -> None:
        """Переход в полуоткрытое состояние"""
        if self.state != CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.HALF_OPEN
            self.metrics.state = CircuitBreakerState.HALF_OPEN
            self.metrics.state_changes += 1
            self.last_state_change = datetime.now()
            self.half_open_calls = 0
            # Сброс счетчиков для тестирования
            self.metrics.failure_count = 0
            self.metrics.success_count = 0

    def _transition_to_closed(self) -> None:
        """Переход в закрытое состояние"""
        if self.state != CircuitBreakerState.CLOSED:
            self.state = CircuitBreakerState.CLOSED
            self.metrics.state = CircuitBreakerState.CLOSED
            self.metrics.state_changes += 1
            self.last_state_change = datetime.now()
            self.half_open_calls = 0

    def _update_metrics(self) -> None:
        """Обновление метрик"""
        self.metrics.calculate_rates()

        # Ограничение размера истории
        if len(self.call_history) > self.config.sliding_window_size:
            self.call_history = self.call_history[
                -self.config.sliding_window_size :
            ]

    def get_metrics(self) -> CircuitBreakerMetrics:
        """Получение метрик"""
        return self.metrics

    def get_state(self) -> CircuitBreakerState:
        """Получение текущего состояния"""
        return self.state

    def reset(self) -> None:
        """Сброс Circuit Breaker"""
        self.state = CircuitBreakerState.CLOSED
        self.metrics = CircuitBreakerMetrics(self.service_id, self.state)
        self.call_history.clear()
        self.half_open_calls = 0
        self.last_state_change = datetime.now()

    def is_open(self) -> bool:
        """Проверка открытого состояния"""
        return self.state == CircuitBreakerState.OPEN

    def is_closed(self) -> bool:
        """Проверка закрытого состояния"""
        return self.state == CircuitBreakerState.CLOSED

    def is_half_open(self) -> bool:
        """Проверка полуоткрытого состояния"""
        return self.state == CircuitBreakerState.HALF_OPEN


# ============================================================================
# ДЕТАЛЬНАЯ ДИАГНОСТИКА ЗДОРОВЬЯ
# ============================================================================


class HealthStatus(Enum):
    """Статусы здоровья сервиса"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Результат проверки здоровья сервиса"""

    service_id: str
    endpoint_url: str
    status: HealthStatus
    response_time: float
    timestamp: datetime

    # Детальная информация
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    headers: Optional[Dict[str, str]] = None

    # Метрики
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None
    disk_usage: Optional[float] = None
    active_connections: Optional[int] = None

    # Дополнительные проверки
    database_healthy: Optional[bool] = None
    cache_healthy: Optional[bool] = None
    external_services_healthy: Optional[bool] = None

    # Пользовательские метрики
    custom_metrics: Optional[Dict[str, Any]] = None

    def is_healthy(self) -> bool:
        """Проверка здорового состояния"""
        return self.status == HealthStatus.HEALTHY

    def is_degraded(self) -> bool:
        """Проверка деградированного состояния"""
        return self.status == HealthStatus.DEGRADED

    def is_unhealthy(self) -> bool:
        """Проверка нездорового состояния"""
        return self.status == HealthStatus.UNHEALTHY

    def get_health_score(self) -> float:
        """Расчет общего показателя здоровья (0.0-1.0)"""
        if self.status == HealthStatus.HEALTHY:
            base_score = 1.0
        elif self.status == HealthStatus.DEGRADED:
            base_score = 0.7
        elif self.status == HealthStatus.UNHEALTHY:
            base_score = 0.3
        else:
            base_score = 0.0

        # Корректировка по времени отклика
        if self.response_time > 0:
            if self.response_time < 100:  # < 100ms
                time_factor = 1.0
            elif self.response_time < 500:  # 100-500ms
                time_factor = 0.9
            elif self.response_time < 1000:  # 500ms-1s
                time_factor = 0.7
            else:  # > 1s
                time_factor = 0.5

            base_score *= time_factor

        return min(1.0, max(0.0, base_score))

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "service_id": self.service_id,
            "endpoint_url": self.endpoint_url,
            "status": self.status.value,
            "response_time": self.response_time,
            "timestamp": self.timestamp.isoformat(),
            "status_code": self.status_code,
            "error_message": self.error_message,
            "headers": self.headers,
            "memory_usage": self.memory_usage,
            "cpu_usage": self.cpu_usage,
            "disk_usage": self.disk_usage,
            "active_connections": self.active_connections,
            "database_healthy": self.database_healthy,
            "cache_healthy": self.cache_healthy,
            "external_services_healthy": self.external_services_healthy,
            "custom_metrics": self.custom_metrics,
            "health_score": self.get_health_score(),
        }


@dataclass
class ServiceHealthSummary:
    """Сводка здоровья сервиса"""

    service_id: str
    overall_status: HealthStatus
    last_check: datetime
    check_count: int = 0
    healthy_checks: int = 0
    degraded_checks: int = 0
    unhealthy_checks: int = 0
    avg_response_time: float = 0.0
    min_response_time: float = float("inf")
    max_response_time: float = 0.0
    uptime_percentage: float = 100.0
    last_error: Optional[str] = None

    def calculate_rates(self) -> None:
        """Расчет процентных показателей"""
        if self.check_count > 0:
            self.uptime_percentage = (
                self.healthy_checks / self.check_count
            ) * 100

    def add_check_result(self, result: HealthCheckResult) -> None:
        """Добавление результата проверки"""
        self.check_count += 1
        self.last_check = result.timestamp

        if result.is_healthy():
            self.healthy_checks += 1
            self.overall_status = HealthStatus.HEALTHY
        elif result.is_degraded():
            self.degraded_checks += 1
            if self.overall_status == HealthStatus.HEALTHY:
                self.overall_status = HealthStatus.DEGRADED
        else:
            self.unhealthy_checks += 1
            self.overall_status = HealthStatus.UNHEALTHY
            self.last_error = result.error_message

        # Обновление метрик времени отклика
        if result.response_time > 0:
            self.min_response_time = min(
                self.min_response_time, result.response_time
            )
            self.max_response_time = max(
                self.max_response_time, result.response_time
            )

            # Простой расчет среднего (можно улучшить)
            total_time = (
                self.avg_response_time * (self.check_count - 1)
                + result.response_time
            )
            self.avg_response_time = total_time / self.check_count

        self.calculate_rates()

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "service_id": self.service_id,
            "overall_status": self.overall_status.value,
            "last_check": self.last_check.isoformat(),
            "check_count": self.check_count,
            "healthy_checks": self.healthy_checks,
            "degraded_checks": self.degraded_checks,
            "unhealthy_checks": self.unhealthy_checks,
            "avg_response_time": self.avg_response_time,
            "min_response_time": (
                self.min_response_time
                if self.min_response_time != float("inf")
                else 0
            ),
            "max_response_time": self.max_response_time,
            "uptime_percentage": self.uptime_percentage,
            "last_error": self.last_error,
        }


# ============================================================================
# СИСТЕМА СОБЫТИЙ С ПАТТЕРНОМ OBSERVER
# ============================================================================

class EventType(Enum):
    """Типы событий Service Mesh"""
    SERVICE_REGISTERED = "service_registered"
    SERVICE_UNREGISTERED = "service_unregistered"
    SERVICE_HEALTH_CHANGED = "service_health_changed"
    CIRCUIT_BREAKER_OPENED = "circuit_breaker_opened"
    CIRCUIT_BREAKER_CLOSED = "circuit_breaker_closed"
    CIRCUIT_BREAKER_HALF_OPENED = "circuit_breaker_half_opened"
    LOAD_BALANCER_SWITCHED = "load_balancer_switched"
    METRICS_UPDATED = "metrics_updated"
    HEALTH_CHECK_FAILED = "health_check_failed"
    REQUEST_SENT = "request_sent"
    REQUEST_FAILED = "request_failed"
    REQUEST_TIMEOUT = "request_timeout"
    SYSTEM_STARTED = "system_started"
    SYSTEM_STOPPED = "system_stopped"
    CONFIGURATION_CHANGED = "configuration_changed"


@dataclass
class ServiceMeshEvent:
    """Событие Service Mesh"""
    event_type: EventType
    service_id: Optional[str]
    timestamp: datetime
    data: Dict[str, Any]
    source: str = "service_mesh_manager"

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "event_type": self.event_type.value,
            "service_id": self.service_id,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "source": self.source
        }


class EventObserver(ABC):
    """Абстрактный наблюдатель событий"""

    @abstractmethod
    def on_event(self, event: ServiceMeshEvent) -> None:
        """Обработка события"""
        pass

    @abstractmethod
    def get_observer_id(self) -> str:
        """Получение идентификатора наблюдателя"""
        pass


class EventManager:
    """Менеджер событий с паттерном Observer"""

    def __init__(self):
        self.observers: Dict[str, EventObserver] = {}
        self.event_history: List[ServiceMeshEvent] = []
        self.max_history_size: int = 1000
        self.enabled: bool = True

    def subscribe(self, observer: EventObserver) -> bool:
        """Подписка наблюдателя на события"""
        try:
            observer_id = observer.get_observer_id()
            if observer_id in self.observers:
                return False  # Уже подписан

            self.observers[observer_id] = observer
            return True

        except Exception:
            return False

    def unsubscribe(self, observer_id: str) -> bool:
        """Отписка наблюдателя от событий"""
        try:
            if observer_id in self.observers:
                del self.observers[observer_id]
                return True
            return False

        except Exception:
            return False

    def publish_event(self, event: ServiceMeshEvent) -> None:
        """Публикация события всем наблюдателям"""
        if not self.enabled:
            return

        try:
            # Сохранение в историю
            self.event_history.append(event)

            # Ограничение размера истории
            if len(self.event_history) > self.max_history_size:
                self.event_history = self.event_history[-self.max_history_size:]

            # Уведомление всех наблюдателей
            for observer in self.observers.values():
                try:
                    observer.on_event(event)
                except Exception as e:
                    # Логируем ошибку, но не прерываем уведомление других наблюдателей
                    print(f"Ошибка в наблюдателе {observer.get_observer_id()}: {e}")

        except Exception as e:
            print(f"Ошибка публикации события: {e}")

    def get_event_history(self, event_type: Optional[EventType] = None,
                         limit: int = 100) -> List[ServiceMeshEvent]:
        """Получение истории событий"""
        try:
            events = self.event_history

            if event_type:
                events = [e for e in events if e.event_type == event_type]

            return events[-limit:] if limit > 0 else events

        except Exception:
            return []

    def get_observers_count(self) -> int:
        """Получение количества наблюдателей"""
        return len(self.observers)

    def clear_history(self) -> None:
        """Очистка истории событий"""
        self.event_history.clear()

    def enable(self) -> None:
        """Включение системы событий"""
        self.enabled = True

    def disable(self) -> None:
        """Отключение системы событий"""
        self.enabled = False


class LoggingEventObserver(EventObserver):
    """Наблюдатель для логирования событий"""

    def __init__(self, logger_name: str = "service_mesh_events"):
        self.logger_name = logger_name
        self.event_count = 0

    def on_event(self, event: ServiceMeshEvent) -> None:
        """Логирование события"""
        self.event_count += 1
        print(f"[{self.logger_name}] Event #{self.event_count}: {event.event_type.value} "
              f"for service {event.service_id or 'system'}")

    def get_observer_id(self) -> str:
        return f"logging_observer_{self.logger_name}"


class MetricsEventObserver(EventObserver):
    """Наблюдатель для сбора метрик событий"""

    def __init__(self):
        self.event_metrics: Dict[EventType, int] = {}
        self.service_event_counts: Dict[str, int] = {}

    def on_event(self, event: ServiceMeshEvent) -> None:
        """Обновление метрик событий"""
        # Подсчет событий по типам
        event_type = event.event_type
        self.event_metrics[event_type] = self.event_metrics.get(event_type, 0) + 1

        # Подсчет событий по сервисам
        if event.service_id:
            self.service_event_counts[event.service_id] = (
                self.service_event_counts.get(event.service_id, 0) + 1
            )

    def get_observer_id(self) -> str:
        return "metrics_observer"

    def get_event_metrics(self) -> Dict[str, Any]:
        """Получение метрик событий"""
        return {
            "event_type_counts": {et.value: count for et, count in self.event_metrics.items()},
            "service_event_counts": self.service_event_counts,
            "total_events": sum(self.event_metrics.values())
        }


class AlertingEventObserver(EventObserver):
    """Наблюдатель для алертинга"""

    def __init__(self, alert_thresholds: Optional[Dict[EventType, int]] = None):
        self.alert_thresholds = alert_thresholds or {}
        self.event_counts: Dict[EventType, int] = {}
        self.alerts_sent: List[Dict[str, Any]] = []

    def on_event(self, event: ServiceMeshEvent) -> None:
        """Проверка на необходимость отправки алерта"""
        event_type = event.event_type

        # Подсчет событий
        self.event_counts[event_type] = self.event_counts.get(event_type, 0) + 1

        # Проверка порогов
        threshold = self.alert_thresholds.get(event_type)
        if threshold and self.event_counts[event_type] >= threshold:
            self._send_alert(event, self.event_counts[event_type])

    def _send_alert(self, event: ServiceMeshEvent, count: int) -> None:
        """Отправка алерта"""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event.event_type.value,
            "service_id": event.service_id,
            "count": count,
            "message": f"Alert: {event.event_type.value} occurred {count} times"
        }

        self.alerts_sent.append(alert)
        print(f"🚨 ALERT: {alert['message']}")

    def get_observer_id(self) -> str:
        return "alerting_observer"

    def get_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Получение алертов"""
        return self.alerts_sent[-limit:] if limit > 0 else self.alerts_sent


# ============================================================================
# КЛАССЫ ИСКЛЮЧЕНИЙ ДЛЯ SERVICE MESH
# ============================================================================


class ServiceMeshError(Exception):
    """Базовое исключение для Service Mesh Manager"""

    pass


class ServiceNotFoundError(ServiceMeshError):
    """Исключение: сервис не найден"""

    def __init__(self, service_id: str):
        self.service_id = service_id
        super().__init__(f"Сервис '{service_id}' не найден")


class ServiceAlreadyRegisteredError(ServiceMeshError):
    """Исключение: сервис уже зарегистрирован"""

    def __init__(self, service_id: str):
        self.service_id = service_id
        super().__init__(f"Сервис '{service_id}' уже зарегистрирован")


class CircuitBreakerOpenError(ServiceMeshError):
    """Исключение: Circuit Breaker открыт"""

    def __init__(self, service_id: str):
        self.service_id = service_id
        super().__init__(f"Circuit Breaker для сервиса '{service_id}' открыт")


class ServiceUnavailableError(ServiceMeshError):
    """Исключение: сервис недоступен"""

    def __init__(self, service_id: str, reason: str = ""):
        self.service_id = service_id
        self.reason = reason
        super().__init__(f"Сервис '{service_id}' недоступен: {reason}")


class InvalidServiceConfigurationError(ServiceMeshError):
    """Исключение: неверная конфигурация сервиса"""

    def __init__(self, service_id: str, field: str, value: str):
        self.service_id = service_id
        self.field = field
        self.value = value
        super().__init__(
            f"Неверная конфигурация сервиса '{service_id}': {field}='{value}'"
        )


class LoadBalancingError(ServiceMeshError):
    """Исключение: ошибка балансировки нагрузки"""

    def __init__(self, service_id: str, strategy: str):
        self.service_id = service_id
        self.strategy = strategy
        super().__init__(
            f"Ошибка балансировки нагрузки для сервиса '{service_id}' "
            f"(стратегия: {strategy})"
        )


class HealthCheckError(ServiceMeshError):
    """Исключение: ошибка проверки здоровья"""

    def __init__(self, service_id: str, error: str):
        self.service_id = service_id
        self.error = error
        super().__init__(
            f"Ошибка проверки здоровья сервиса '{service_id}': {error}"
        )


class MetricsCollectionError(ServiceMeshError):
    """Исключение: ошибка сбора метрик"""

    def __init__(self, service_id: str, error: str):
        self.service_id = service_id
        self.error = error
        super().__init__(
            f"Ошибка сбора метрик для сервиса '{service_id}': {error}"
        )


class CacheError(ServiceMeshError):
    """Базовое исключение для кэширования"""
    pass


class CacheKeyNotFoundError(CacheError):
    """Ключ не найден в кэше"""
    pass


class CacheExpiredError(CacheError):
    """Кэш истек"""
    pass


class CacheConfigurationError(CacheError):
    """Ошибка конфигурации кэша"""
    pass


class AsyncOperationError(ServiceMeshError):
    """Ошибка асинхронной операции"""
    pass


class AsyncTimeoutError(ServiceMeshError):
    """Ошибка таймаута асинхронной операции"""
    pass


# ============================================================================
# СТРУКТУРИРОВАННОЕ ЛОГИРОВАНИЕ
# ============================================================================

@dataclass
class LogConfig:
    """Конфигурация логирования"""
    level: str = "INFO"
    format: str = "json"  # json, text, structured
    include_timestamp: bool = True
    include_service_id: bool = True
    include_request_id: bool = True
    include_metrics: bool = True
    max_message_length: int = 1000
    enable_file_logging: bool = True
    log_file_path: str = "logs/service_mesh.log"
    enable_console_logging: bool = True
    enable_remote_logging: bool = False
    remote_logging_url: Optional[str] = None


class StructuredLogger:
    """Структурированный логгер для Service Mesh Manager"""

    def __init__(self, name: str, config: Optional[LogConfig] = None):
        self.name = name
        self.config = config or LogConfig()
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, self.config.level.upper()))

        # Очистка существующих обработчиков
        self.logger.handlers.clear()

        # Настройка форматирования
        self._setup_formatters()

        # Настройка обработчиков
        self._setup_handlers()

        # Контекстные данные
        self._context: Dict[str, Any] = {}
        self._context_lock = threading.Lock()

    def _setup_formatters(self) -> None:
        """Настройка форматтеров"""
        if self.config.format == "json":
            self.formatter = self._create_json_formatter()
        elif self.config.format == "text":
            self.formatter = self._create_text_formatter()
        else:  # structured
            self.formatter = self._create_structured_formatter()

    def _create_json_formatter(self) -> logging.Formatter:
        """Создание JSON форматтера"""
        class JSONFormatter(logging.Formatter):
            def format(self, record):
                log_data = {
                    "timestamp": datetime.fromtimestamp(record.created).isoformat(),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                    "module": record.module,
                    "function": record.funcName,
                    "line": record.lineno
                }

                # Добавление контекстных данных
                if hasattr(record, 'context'):
                    log_data.update(record.context)

                # Добавление исключения
                if record.exc_info:
                    log_data["exception"] = self.formatException(record.exc_info)

                return json.dumps(log_data, ensure_ascii=False, default=str)

        return JSONFormatter()

    def _create_text_formatter(self) -> logging.Formatter:
        """Создание текстового форматтера"""
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        if self.config.include_service_id:
            format_string = "%(asctime)s - %(name)s - %(levelname)s - [%(service_id)s] - %(message)s"
        return logging.Formatter(format_string)

    def _create_structured_formatter(self) -> logging.Formatter:
        """Создание структурированного форматтера"""
        class StructuredFormatter(logging.Formatter):
            def format(self, record):
                parts = [
                    f"[{record.levelname}]",
                    f"{record.name}",
                    f"{record.getMessage()}"
                ]

                # Добавление контекстных данных
                if hasattr(record, 'context') and record.context:
                    context_str = " ".join([f"{k}={v}" for k, v in record.context.items()])
                    parts.append(f"({context_str})")

                return " - ".join(parts)

        return StructuredFormatter()

    def _setup_handlers(self) -> None:
        """Настройка обработчиков"""
        # Консольный обработчик
        if self.config.enable_console_logging:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(self.formatter)
            self.logger.addHandler(console_handler)

        # Файловый обработчик
        if self.config.enable_file_logging:
            try:
                import os
                os.makedirs(os.path.dirname(self.config.log_file_path), exist_ok=True)

                file_handler = logging.FileHandler(self.config.log_file_path)
                file_handler.setFormatter(self.formatter)
                self.logger.addHandler(file_handler)
            except Exception as e:
                print(f"Ошибка настройки файлового логирования: {e}")

    def set_context(self, **kwargs) -> None:
        """Установка контекстных данных"""
        with self._context_lock:
            self._context.update(kwargs)

    def clear_context(self) -> None:
        """Очистка контекстных данных"""
        with self._context_lock:
            self._context.clear()

    def _create_log_record(self, level: int, message: str, **kwargs) -> logging.LogRecord:
        """Создание записи лога с контекстом"""
        # Создание базовой записи
        record = self.logger.makeRecord(
            self.name, level, "", 0, message, (), None
        )

        # Добавление контекстных данных
        with self._context_lock:
            record.context = {**self._context, **kwargs}

        return record

    def debug(self, message: str, **kwargs) -> None:
        """Логирование уровня DEBUG"""
        if self.logger.isEnabledFor(logging.DEBUG):
            record = self._create_log_record(logging.DEBUG, message, **kwargs)
            self.logger.handle(record)

    def info(self, message: str, **kwargs) -> None:
        """Логирование уровня INFO"""
        if self.logger.isEnabledFor(logging.INFO):
            record = self._create_log_record(logging.INFO, message, **kwargs)
            self.logger.handle(record)

    def warning(self, message: str, **kwargs) -> None:
        """Логирование уровня WARNING"""
        if self.logger.isEnabledFor(logging.WARNING):
            record = self._create_log_record(logging.WARNING, message, **kwargs)
            self.logger.handle(record)

    def error(self, message: str, **kwargs) -> None:
        """Логирование уровня ERROR"""
        if self.logger.isEnabledFor(logging.ERROR):
            record = self._create_log_record(logging.ERROR, message, **kwargs)
            self.logger.handle(record)

    def critical(self, message: str, **kwargs) -> None:
        """Логирование уровня CRITICAL"""
        if self.logger.isEnabledFor(logging.CRITICAL):
            record = self._create_log_record(logging.CRITICAL, message, **kwargs)
            self.logger.handle(record)

    def log_request(self, service_id: str, method: str, path: str,
                   status_code: int, response_time: float, **kwargs) -> None:
        """Логирование HTTP запроса"""
        self.info(
            f"HTTP {method} {path} -> {status_code}",
            service_id=service_id,
            method=method,
            path=path,
            status_code=status_code,
            response_time=response_time,
            **kwargs
        )

    def log_service_event(self, event_type: str, service_id: str, **kwargs) -> None:
        """Логирование события сервиса"""
        self.info(
            f"Service event: {event_type}",
            event_type=event_type,
            service_id=service_id,
            **kwargs
        )

    def log_metrics(self, metrics_type: str, **kwargs) -> None:
        """Логирование метрик"""
        self.debug(
            f"Metrics update: {metrics_type}",
            metrics_type=metrics_type,
            **kwargs
        )

    def log_error(self, error_type: str, error_message: str, **kwargs) -> None:
        """Логирование ошибки"""
        self.error(
            f"Error: {error_type} - {error_message}",
            error_type=error_type,
            error_message=error_message,
            **kwargs
        )


class ServiceMeshLogger:
    """Специализированный логгер для Service Mesh Manager"""

    def __init__(self, config: Optional[LogConfig] = None):
        self.config = config or LogConfig()
        self.logger = StructuredLogger("service_mesh_manager", self.config)
        self._request_counter = 0
        self._error_counter = 0

    def log_service_registration(self, service_id: str, service_name: str,
                               endpoints_count: int) -> None:
        """Логирование регистрации сервиса"""
        self.logger.log_service_event(
            "service_registered",
            service_id=service_id,
            service_name=service_name,
            endpoints_count=endpoints_count
        )

    def log_service_unregistration(self, service_id: str) -> None:
        """Логирование отмены регистрации сервиса"""
        self.logger.log_service_event(
            "service_unregistered",
            service_id=service_id
        )

    def log_health_check(self, service_id: str, status: str,
                        healthy_endpoints: int, total_endpoints: int) -> None:
        """Логирование проверки здоровья"""
        self.logger.log_service_event(
            "health_check",
            service_id=service_id,
            status=status,
            healthy_endpoints=healthy_endpoints,
            total_endpoints=total_endpoints
        )

    def log_circuit_breaker_event(self, service_id: str, state: str,
                                 failure_count: int, failure_rate: float) -> None:
        """Логирование события Circuit Breaker"""
        self.logger.log_service_event(
            "circuit_breaker",
            service_id=service_id,
            state=state,
            failure_count=failure_count,
            failure_rate=failure_rate
        )

    def log_request(self, service_id: str, method: str, path: str,
                   status_code: int, response_time: float,
                   request_id: Optional[str] = None) -> None:
        """Логирование HTTP запроса"""
        self._request_counter += 1
        self.logger.log_request(
            service_id=service_id,
            method=method,
            path=path,
            status_code=status_code,
            response_time=response_time,
            request_id=request_id or f"req_{self._request_counter}",
            request_number=self._request_counter
        )

    def log_metrics_update(self, service_id: str, metrics: Dict[str, Any]) -> None:
        """Логирование обновления метрик"""
        self.logger.log_metrics(
            "service_metrics",
            service_id=service_id,
            **metrics
        )

    def log_error(self, error_type: str, error_message: str,
                 service_id: Optional[str] = None, **kwargs) -> None:
        """Логирование ошибки"""
        self._error_counter += 1
        self.logger.log_error(
            error_type=error_type,
            error_message=error_message,
            service_id=service_id,
            error_number=self._error_counter,
            **kwargs
        )

    def log_system_event(self, event: str, **kwargs) -> None:
        """Логирование системного события"""
        self.logger.info(
            f"System event: {event}",
            event=event,
            **kwargs
        )

    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики логирования"""
        return {
            "total_requests": self._request_counter,
            "total_errors": self._error_counter,
            "config": asdict(self.config),
            "logger_name": self.logger.name
        }


# ============================================================================
# PROMETHEUS МЕТРИКИ
# ============================================================================

@dataclass
class PrometheusConfig:
    """Конфигурация Prometheus метрик"""
    enable_metrics: bool = True
    metrics_port: int = 9090
    metrics_path: str = "/metrics"
    namespace: str = "service_mesh"
    subsystem: str = "manager"
    enable_histograms: bool = True
    enable_gauges: bool = True
    enable_counters: bool = True
    enable_summaries: bool = True
    custom_labels: Dict[str, str] = None

    def __post_init__(self):
        if self.custom_labels is None:
            self.custom_labels = {}


class PrometheusMetrics:
    """Класс для работы с Prometheus метриками"""

    def __init__(self, config: PrometheusConfig):
        self.config = config
        self.metrics: Dict[str, Any] = {}
        self._lock = threading.Lock()

        if self.config.enable_metrics:
            self._initialize_metrics()

    def _initialize_metrics(self) -> None:
        """Инициализация Prometheus метрик"""
        try:
            # Counter метрики
            if self.config.enable_counters:
                self.metrics.update({
                    "requests_total": self._create_counter(
                        "requests_total", "Total number of requests",
                        ["service_id", "method", "status_code"]
                    ),
                    "errors_total": self._create_counter(
                        "errors_total", "Total number of errors",
                        ["service_id", "error_type"]
                    ),
                    "service_registrations_total": self._create_counter(
                        "service_registrations_total", "Total service registrations",
                        ["service_id", "service_type"]
                    ),
                    "circuit_breaker_opens_total": self._create_counter(
                        "circuit_breaker_opens_total", "Total circuit breaker opens",
                        ["service_id"]
                    ),
                    "health_check_failures_total": self._create_counter(
                        "health_check_failures_total", "Total health check failures",
                        ["service_id"]
                    )
                })

            # Gauge метрики
            if self.config.enable_gauges:
                self.metrics.update({
                    "services_active": self._create_gauge(
                        "services_active", "Number of active services"
                    ),
                    "circuit_breaker_state": self._create_gauge(
                        "circuit_breaker_state", "Circuit breaker state (0=closed, 1=open, 2=half_open)",
                        ["service_id"]
                    ),
                    "service_health_status": self._create_gauge(
                        "service_health_status", "Service health status (0=unhealthy, 1=healthy, 2=degraded)",
                        ["service_id"]
                    ),
                    "cache_size": self._create_gauge(
                        "cache_size", "Current cache size"
                    ),
                    "async_requests_active": self._create_gauge(
                        "async_requests_active", "Number of active async requests"
                    )
                })

            # Histogram метрики
            if self.config.enable_histograms:
                self.metrics.update({
                    "request_duration_seconds": self._create_histogram(
                        "request_duration_seconds", "Request duration in seconds",
                        ["service_id", "method"],
                        buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
                    ),
                    "response_size_bytes": self._create_histogram(
                        "response_size_bytes", "Response size in bytes",
                        ["service_id"],
                        buckets=[100, 1000, 10000, 100000, 1000000, 10000000]
                    )
                })

            # Summary метрики
            if self.config.enable_summaries:
                self.metrics.update({
                    "circuit_breaker_failure_rate": self._create_summary(
                        "circuit_breaker_failure_rate", "Circuit breaker failure rate",
                        ["service_id"]
                    ),
                    "cache_hit_rate": self._create_summary(
                        "cache_hit_rate", "Cache hit rate"
                    )
                })

        except Exception as e:
            print(f"Ошибка инициализации Prometheus метрик: {e}")

    def _create_counter(self, name: str, help_text: str, labels: List[str] = None) -> Dict[str, Any]:
        """Создание Counter метрики"""
        return {
            "type": "counter",
            "name": f"{self.config.namespace}_{self.config.subsystem}_{name}",
            "help": help_text,
            "labels": labels or [],
            "value": 0.0,
            "label_values": {}
        }

    def _create_gauge(self, name: str, help_text: str, labels: List[str] = None) -> Dict[str, Any]:
        """Создание Gauge метрики"""
        return {
            "type": "gauge",
            "name": f"{self.config.namespace}_{self.config.subsystem}_{name}",
            "help": help_text,
            "labels": labels or [],
            "value": 0.0,
            "label_values": {}
        }

    def _create_histogram(self, name: str, help_text: str, labels: List[str] = None,
                         buckets: List[float] = None) -> Dict[str, Any]:
        """Создание Histogram метрики"""
        return {
            "type": "histogram",
            "name": f"{self.config.namespace}_{self.config.subsystem}_{name}",
            "help": help_text,
            "labels": labels or [],
            "buckets": buckets or [0.1, 0.5, 1.0, 2.5, 5.0, 10.0],
            "observations": [],
            "label_values": {}
        }

    def _create_summary(self, name: str, help_text: str, labels: List[str] = None) -> Dict[str, Any]:
        """Создание Summary метрики"""
        return {
            "type": "summary",
            "name": f"{self.config.namespace}_{self.config.subsystem}_{name}",
            "help": help_text,
            "labels": labels or [],
            "observations": [],
            "label_values": {}
        }

    def increment_counter(self, metric_name: str, value: float = 1.0,
                        label_values: Dict[str, str] = None) -> None:
        """Увеличение Counter метрики"""
        try:
            if not self.config.enable_metrics or metric_name not in self.metrics:
                return

            with self._lock:
                metric = self.metrics[metric_name]
                if metric["type"] == "counter":
                    metric["value"] += value
                    if label_values:
                        metric["label_values"].update(label_values)

        except Exception as e:
            print(f"Ошибка увеличения counter метрики {metric_name}: {e}")

    def set_gauge(self, metric_name: str, value: float,
                  label_values: Dict[str, str] = None) -> None:
        """Установка значения Gauge метрики"""
        try:
            if not self.config.enable_metrics or metric_name not in self.metrics:
                return

            with self._lock:
                metric = self.metrics[metric_name]
                if metric["type"] == "gauge":
                    metric["value"] = value
                    if label_values:
                        metric["label_values"].update(label_values)

        except Exception as e:
            print(f"Ошибка установки gauge метрики {metric_name}: {e}")

    def observe_histogram(self, metric_name: str, value: float,
                         label_values: Dict[str, str] = None) -> None:
        """Добавление наблюдения в Histogram метрику"""
        try:
            if not self.config.enable_metrics or metric_name not in self.metrics:
                return

            with self._lock:
                metric = self.metrics[metric_name]
                if metric["type"] == "histogram":
                    metric["observations"].append(value)
                    if label_values:
                        metric["label_values"].update(label_values)

        except Exception as e:
            print(f"Ошибка добавления наблюдения в histogram {metric_name}: {e}")

    def observe_summary(self, metric_name: str, value: float,
                       label_values: Dict[str, str] = None) -> None:
        """Добавление наблюдения в Summary метрику"""
        try:
            if not self.config.enable_metrics or metric_name not in self.metrics:
                return

            with self._lock:
                metric = self.metrics[metric_name]
                if metric["type"] == "summary":
                    metric["observations"].append(value)
                    if label_values:
                        metric["label_values"].update(label_values)

        except Exception as e:
            print(f"Ошибка добавления наблюдения в summary {metric_name}: {e}")

    def get_metrics_text(self) -> str:
        """Получение метрик в формате Prometheus"""
        try:
            if not self.config.enable_metrics:
                return "# Prometheus metrics disabled\n"

            lines = []

            with self._lock:
                for metric_name, metric in self.metrics.items():
                    # Заголовок метрики
                    lines.append(f"# HELP {metric['name']} {metric['help']}")
                    lines.append(f"# TYPE {metric['name']} {metric['type']}")

                    if metric["type"] in ["counter", "gauge"]:
                        # Простые метрики
                        label_str = ""
                        if metric["label_values"]:
                            label_parts = [f'{k}="{v}"' for k, v in metric["label_values"].items()]
                            label_str = "{" + ",".join(label_parts) + "}"

                        lines.append(f"{metric['name']}{label_str} {metric['value']}")

                    elif metric["type"] == "histogram":
                        # Histogram метрики
                        if metric["observations"]:
                            observations = metric["observations"]
                            count = len(observations)
                            total = sum(observations)

                            # Bucket метрики
                            for bucket in metric["buckets"]:
                                bucket_count = sum(1 for obs in observations if obs <= bucket)
                                lines.append(f"{metric['name']}_bucket{{le=\"{bucket}\"}} {bucket_count}")

                            # Infinity bucket
                            lines.append(f"{metric['name']}_bucket{{le=\"+Inf\"}} {count}")

                            # Sum и count
                            lines.append(f"{metric['name']}_sum {total}")
                            lines.append(f"{metric['name']}_count {count}")

                    elif metric["type"] == "summary":
                        # Summary метрики
                        if metric["observations"]:
                            observations = metric["observations"]
                            count = len(observations)
                            total = sum(observations)

                            # Quantiles (приблизительные)
                            observations_sorted = sorted(observations)
                            quantiles = [0.5, 0.9, 0.95, 0.99]

                            for q in quantiles:
                                idx = int(q * (count - 1))
                                value = observations_sorted[idx] if count > 0 else 0
                                lines.append(f"{metric['name']}{{quantile=\"{q}\"}} {value}")

                            # Sum и count
                            lines.append(f"{metric['name']}_sum {total}")
                            lines.append(f"{metric['name']}_count {count}")

                    lines.append("")  # Пустая строка между метриками

            return "\n".join(lines)

        except Exception as e:
            return f"# Error generating metrics: {e}\n"

    def get_metrics_dict(self) -> Dict[str, Any]:
        """Получение метрик в виде словаря"""
        try:
            if not self.config.enable_metrics:
                return {"enabled": False}

            result = {"enabled": True, "metrics": {}}

            with self._lock:
                for metric_name, metric in self.metrics.items():
                    result["metrics"][metric_name] = {
                        "name": metric["name"],
                        "type": metric["type"],
                        "help": metric["help"],
                        "value": metric.get("value", 0.0),
                        "observations_count": len(metric.get("observations", [])),
                        "label_values": metric.get("label_values", {})
                    }

            return result

        except Exception as e:
            return {"enabled": False, "error": str(e)}

    def reset_metrics(self) -> None:
        """Сброс всех метрик"""
        try:
            with self._lock:
                for metric in self.metrics.values():
                    if metric["type"] in ["counter", "gauge"]:
                        metric["value"] = 0.0
                    elif metric["type"] in ["histogram", "summary"]:
                        metric["observations"] = []
                    metric["label_values"] = {}

        except Exception as e:
            print(f"Ошибка сброса метрик: {e}")


# ============================================================================
# АСИНХРОННАЯ ПОДДЕРЖКА
# ============================================================================

@dataclass
class AsyncConfig:
    """Конфигурация асинхронных операций"""
    max_concurrent_requests: int = 100
    request_timeout: float = 30.0
    connection_timeout: float = 10.0
    enable_connection_pooling: bool = True
    max_connections_per_service: int = 10
    keepalive_timeout: float = 60.0
    enable_retry: bool = True
    max_retries: int = 3
    retry_delay: float = 1.0
    retry_backoff_factor: float = 2.0


class AsyncConnectionPool:
    """Пул асинхронных соединений"""

    def __init__(self, max_connections: int = 10, keepalive_timeout: float = 60.0):
        self.max_connections = max_connections
        self.keepalive_timeout = keepalive_timeout
        self._connections: Dict[str, List[asyncio.StreamReader]] = {}
        self._connection_locks: Dict[str, asyncio.Lock] = {}
        self._last_used: Dict[str, datetime] = {}

    async def get_connection(self, service_id: str, endpoint: str) -> Optional[asyncio.StreamReader]:
        """Получение соединения из пула"""
        try:
            if service_id not in self._connections:
                self._connections[service_id] = []
                self._connection_locks[service_id] = asyncio.Lock()

            async with self._connection_locks[service_id]:
                # Поиск доступного соединения
                for conn in self._connections[service_id]:
                    if not conn.at_eof():
                        self._last_used[service_id] = datetime.now()
                        return conn

                # Создание нового соединения если есть место
                if len(self._connections[service_id]) < self.max_connections:
                    # Имитация создания соединения
                    conn = asyncio.StreamReader()
                    self._connections[service_id].append(conn)
                    self._last_used[service_id] = datetime.now()
                    return conn

            return None

        except Exception:
            return None

    async def return_connection(self, service_id: str, connection: asyncio.StreamReader) -> None:
        """Возврат соединения в пул"""
        try:
            if service_id in self._connections and connection in self._connections[service_id]:
                # Проверка на keepalive timeout
                if service_id in self._last_used:
                    time_since_use = (datetime.now() - self._last_used[service_id]).seconds
                    if time_since_use > self.keepalive_timeout:
                        self._connections[service_id].remove(connection)
                        return

                # Соединение остается в пуле
                pass

        except Exception:
            pass

    async def cleanup_expired_connections(self) -> int:
        """Очистка истекших соединений"""
        cleaned = 0
        current_time = datetime.now()

        for service_id, connections in self._connections.items():
            if service_id in self._last_used:
                time_since_use = (current_time - self._last_used[service_id]).seconds
                if time_since_use > self.keepalive_timeout:
                    # Удаление всех соединений для этого сервиса
                    cleaned += len(connections)
                    connections.clear()

        return cleaned

    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики пула соединений"""
        total_connections = sum(len(conns) for conns in self._connections.values())
        return {
            "total_connections": total_connections,
            "services_count": len(self._connections),
            "max_connections_per_service": self.max_connections,
            "keepalive_timeout": self.keepalive_timeout,
            "connections_by_service": {
                service_id: len(conns)
                for service_id, conns in self._connections.items()
            }
        }


class AsyncRequestManager:
    """Менеджер асинхронных запросов"""

    def __init__(self, config: AsyncConfig):
        self.config = config
        self.connection_pool = AsyncConnectionPool(
            max_connections=config.max_connections_per_service,
            keepalive_timeout=config.keepalive_timeout
        )
        self._semaphore = asyncio.Semaphore(config.max_concurrent_requests)
        self._active_requests: Dict[str, asyncio.Task] = {}
        self._request_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "timeout_requests": 0,
            "concurrent_requests": 0
        }

    async def send_async_request(self, service_id: str, method: str, path: str,
                               headers: Optional[Dict[str, str]] = None,
                               body: Optional[Any] = None) -> Optional["ServiceResponse"]:
        """Отправка асинхронного запроса"""
        request_id = f"{service_id}_{int(time.time() * 1000)}"

        async with self._semaphore:
            self._request_stats["total_requests"] += 1
            self._request_stats["concurrent_requests"] += 1

            try:
                # Создание задачи
                task = asyncio.create_task(
                    self._execute_async_request(service_id, method, path, headers, body, request_id)
                )
                self._active_requests[request_id] = task

                # Выполнение с таймаутом
                response = await asyncio.wait_for(
                    task, timeout=self.config.request_timeout
                )

                self._request_stats["successful_requests"] += 1
                return response

            except asyncio.TimeoutError:
                self._request_stats["timeout_requests"] += 1
                raise AsyncTimeoutError(f"Таймаут запроса к сервису {service_id}")

            except Exception as e:
                self._request_stats["failed_requests"] += 1
                raise AsyncOperationError(f"Ошибка асинхронного запроса: {e}")

            finally:
                self._request_stats["concurrent_requests"] -= 1
                if request_id in self._active_requests:
                    del self._active_requests[request_id]

    async def _execute_async_request(self, service_id: str, method: str, path: str,
                                   headers: Optional[Dict[str, str]], body: Optional[Any],
                                   request_id: str) -> "ServiceResponse":
        """Выполнение асинхронного запроса"""
        try:
            # Имитация асинхронного HTTP запроса
            await asyncio.sleep(0.1)  # Имитация сетевой задержки

            # Создание ответа
            response = ServiceResponse(
                request_id=request_id,
                service_id=service_id,
                status_code=200,
                headers=headers or {},
                body={"message": "Async response", "timestamp": datetime.now().isoformat()},
                response_time=0.1
            )

            return response

        except Exception as e:
            raise AsyncOperationError(f"Ошибка выполнения запроса: {e}")

    async def cancel_all_requests(self) -> int:
        """Отмена всех активных запросов"""
        cancelled = 0
        for request_id, task in self._active_requests.items():
            if not task.done():
                task.cancel()
                cancelled += 1

        # Ожидание завершения отмены
        if self._active_requests:
            await asyncio.gather(*self._active_requests.values(), return_exceptions=True)

        self._active_requests.clear()
        return cancelled

    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики асинхронных запросов"""
        stats = self._request_stats.copy()
        stats["active_requests"] = len(self._active_requests)
        stats["connection_pool_stats"] = self.connection_pool.get_statistics()
        return stats


# ============================================================================
# СИСТЕМА КЭШИРОВАНИЯ С TTL
# ============================================================================

@dataclass
class CacheEntry:
    """Запись кэша с TTL"""
    value: Any
    created_at: datetime
    ttl_seconds: int
    access_count: int = 0
    last_accessed: Optional[datetime] = None

    def is_expired(self) -> bool:
        """Проверка истечения TTL"""
        if self.last_accessed:
            return (datetime.now() - self.last_accessed).seconds > self.ttl_seconds
        return (datetime.now() - self.created_at).seconds > self.ttl_seconds

    def access(self) -> None:
        """Обновление статистики доступа"""
        self.access_count += 1
        self.last_accessed = datetime.now()


@dataclass
class CacheConfig:
    """Конфигурация кэша"""
    max_size: int = 1000
    default_ttl_seconds: int = 300  # 5 минут
    cleanup_interval_seconds: int = 60  # 1 минута
    enable_statistics: bool = True
    enable_compression: bool = False


class TTLCache:
    """Кэш с TTL (Time To Live)"""

    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()
        self._cache: Dict[str, CacheEntry] = {}
        self._access_order: List[str] = []
        self._statistics = {
            "hits": 0,
            "misses": 0,
            "expired": 0,
            "evictions": 0,
            "total_requests": 0
        }
        self._last_cleanup = datetime.now()

    def get(self, key: str) -> Any:
        """Получение значения из кэша"""
        self._statistics["total_requests"] += 1

        if key not in self._cache:
            self._statistics["misses"] += 1
            raise CacheKeyNotFoundError(f"Ключ '{key}' не найден в кэше")

        entry = self._cache[key]

        if entry.is_expired():
            del self._cache[key]
            if key in self._access_order:
                self._access_order.remove(key)
            self._statistics["expired"] += 1
            raise CacheExpiredError(f"Кэш для ключа '{key}' истек")

        # Обновление статистики доступа
        entry.access()

        # Обновление порядка доступа (LRU)
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)

        self._statistics["hits"] += 1
        return entry.value

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """Установка значения в кэш"""
        ttl = ttl_seconds or self.config.default_ttl_seconds

        # Проверка размера кэша
        if len(self._cache) >= self.config.max_size and key not in self._cache:
            self._evict_lru()

        entry = CacheEntry(
            value=value,
            created_at=datetime.now(),
            ttl_seconds=ttl
        )

        self._cache[key] = entry

        # Обновление порядка доступа
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)

    def delete(self, key: str) -> bool:
        """Удаление ключа из кэша"""
        if key in self._cache:
            del self._cache[key]
            if key in self._access_order:
                self._access_order.remove(key)
            return True
        return False

    def clear(self) -> None:
        """Очистка всего кэша"""
        self._cache.clear()
        self._access_order.clear()

    def cleanup_expired(self) -> int:
        """Очистка истекших записей"""
        expired_keys = []
        for key, entry in self._cache.items():
            if entry.is_expired():
                expired_keys.append(key)

        for key in expired_keys:
            del self._cache[key]
            if key in self._access_order:
                self._access_order.remove(key)

        self._statistics["expired"] += len(expired_keys)
        return len(expired_keys)

    def _evict_lru(self) -> None:
        """Удаление наименее используемой записи (LRU)"""
        if self._access_order:
            lru_key = self._access_order[0]
            del self._cache[lru_key]
            self._access_order.pop(0)
            self._statistics["evictions"] += 1

    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики кэша"""
        hit_rate = 0
        if self._statistics["total_requests"] > 0:
            hit_rate = (self._statistics["hits"] /
                       self._statistics["total_requests"]) * 100

        return {
            "size": len(self._cache),
            "max_size": self.config.max_size,
            "hit_rate": round(hit_rate, 2),
            "statistics": self._statistics.copy(),
            "oldest_entry": min(
                (entry.created_at for entry in self._cache.values()),
                default=None
            ),
            "newest_entry": max(
                (entry.created_at for entry in self._cache.values()),
                default=None
            )
        }

    def get_entry_info(self, key: str) -> Optional[Dict[str, Any]]:
        """Получение информации о записи кэша"""
        if key not in self._cache:
            return None

        entry = self._cache[key]
        return {
            "key": key,
            "created_at": entry.created_at,
            "ttl_seconds": entry.ttl_seconds,
            "access_count": entry.access_count,
            "last_accessed": entry.last_accessed,
            "is_expired": entry.is_expired(),
            "age_seconds": (datetime.now() - entry.created_at).seconds
        }


# ============================================================================
# ВАЛИДАТОР ВХОДНЫХ ДАННЫХ
# ============================================================================


class InputValidator:
    """Валидатор входных данных для Service Mesh Manager"""

    @staticmethod
    def validate_service_id(
        service_id: str, field_name: str = "service_id"
    ) -> str:
        """Валидация идентификатора сервиса"""
        if not service_id:
            raise InvalidServiceConfigurationError(
                service_id or "None", field_name, "пустой или None"
            )

        if not isinstance(service_id, str):
            raise InvalidServiceConfigurationError(
                str(service_id), field_name, f"не строка: {type(service_id)}"
            )

        if not service_id.strip():
            raise InvalidServiceConfigurationError(
                service_id, field_name, "пустая строка"
            )

        if len(service_id) > 100:
            raise InvalidServiceConfigurationError(
                service_id,
                field_name,
                f"слишком длинный: {len(service_id)} символов",
            )

        # Проверка на допустимые символы
        import re

        if not re.match(r"^[a-zA-Z0-9_-]+$", service_id):
            raise InvalidServiceConfigurationError(
                service_id, field_name, "содержит недопустимые символы"
            )

        return service_id.strip()

    @staticmethod
    def validate_string(
        value: str, field_name: str, min_length: int = 1, max_length: int = 255
    ) -> str:
        """Валидация строкового значения"""
        if not value:
            raise InvalidServiceConfigurationError(
                value or "None", field_name, "пустой или None"
            )

        if not isinstance(value, str):
            raise InvalidServiceConfigurationError(
                str(value), field_name, f"не строка: {type(value)}"
            )

        value = value.strip()

        if len(value) < min_length:
            raise InvalidServiceConfigurationError(
                value,
                field_name,
                f"слишком короткий: {len(value)} < {min_length}",
            )

        if len(value) > max_length:
            raise InvalidServiceConfigurationError(
                value,
                field_name,
                f"слишком длинный: {len(value)} > {max_length}",
            )

        return value

    @staticmethod
    def validate_http_method(method: str) -> str:
        """Валидация HTTP метода"""
        if not method:
            raise InvalidServiceConfigurationError(
                method or "None", "method", "пустой или None"
            )

        method = method.strip().upper()
        valid_methods = {
            "GET",
            "POST",
            "PUT",
            "DELETE",
            "PATCH",
            "HEAD",
            "OPTIONS",
        }

        if method not in valid_methods:
            raise InvalidServiceConfigurationError(
                method,
                "method",
                f"недопустимый метод. Допустимые: {valid_methods}",
            )

        return method

    @staticmethod
    def validate_path(path: str) -> str:
        """Валидация пути ресурса"""
        if not path:
            raise InvalidServiceConfigurationError(
                path or "None", "path", "пустой или None"
            )

        path = path.strip()

        if not path.startswith("/"):
            raise InvalidServiceConfigurationError(
                path, "path", "должен начинаться с '/'"
            )

        if len(path) > 1000:
            raise InvalidServiceConfigurationError(
                path, "path", f"слишком длинный: {len(path)} символов"
            )

        return path

    @staticmethod
    def validate_headers(headers: Optional[Dict[str, str]]) -> Dict[str, str]:
        """Валидация заголовков HTTP"""
        if headers is None:
            return {}

        if not isinstance(headers, dict):
            raise InvalidServiceConfigurationError(
                str(headers), "headers", f"не словарь: {type(headers)}"
            )

        validated_headers = {}
        for key, value in headers.items():
            if not isinstance(key, str) or not isinstance(value, str):
                raise InvalidServiceConfigurationError(
                    f"{key}: {value}",
                    "headers",
                    "ключи и значения должны быть строками",
                )

            if not key.strip() or not value.strip():
                raise InvalidServiceConfigurationError(
                    f"{key}: {value}", "headers", "пустые ключи или значения"
                )

            validated_headers[key.strip()] = value.strip()

        return validated_headers

    @staticmethod
    def validate_endpoints(
        endpoints: List["ServiceEndpoint"],
    ) -> List["ServiceEndpoint"]:
        """Валидация списка endpoints"""
        if endpoints is None:
            raise InvalidServiceConfigurationError(
                "None", "endpoints", "не может быть None"
            )

        if not isinstance(endpoints, list):
            raise InvalidServiceConfigurationError(
                str(endpoints), "endpoints", f"не список: {type(endpoints)}"
            )

        # Разрешаем пустой список для тестирования
        if len(endpoints) == 0:
            return []

        validated_endpoints = []
        for i, endpoint in enumerate(endpoints):
            if not isinstance(endpoint, ServiceEndpoint):
                raise InvalidServiceConfigurationError(
                    str(endpoint),
                    f"endpoints[{i}]",
                    f"не ServiceEndpoint: {type(endpoint)}",
                )

            # Валидация полей endpoint
            endpoint.service_id = InputValidator.validate_service_id(
                endpoint.service_id, f"endpoints[{i}].service_id"
            )
            endpoint.host = InputValidator.validate_string(
                endpoint.host, f"endpoints[{i}].host", 1, 253
            )
            endpoint.path = InputValidator.validate_path(endpoint.path)

            if not isinstance(endpoint.port, int) or not (
                1 <= endpoint.port <= 65535
            ):
                raise InvalidServiceConfigurationError(
                    str(endpoint.port),
                    f"endpoints[{i}].port",
                    f"недопустимый порт: {endpoint.port}",
                )

            if endpoint.protocol not in ["http", "https", "tcp", "udp"]:
                raise InvalidServiceConfigurationError(
                    endpoint.protocol,
                    f"endpoints[{i}].protocol",
                    f"недопустимый протокол: {endpoint.protocol}",
                )

            validated_endpoints.append(endpoint)

        return validated_endpoints


# ============================================================================
# КЛАССЫ ДЛЯ МЕТРИК ПРОИЗВОДИТЕЛЬНОСТИ
# ============================================================================


@dataclass
class PerformanceMetrics:
    """Метрики производительности для сервиса"""

    service_id: str
    timestamp: datetime

    # Основные метрики
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    timeout_requests: int = 0

    # Метрики времени
    min_response_time: float = float("inf")
    max_response_time: float = 0.0
    avg_response_time: float = 0.0
    p50_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0

    # Метрики пропускной способности
    requests_per_second: float = 0.0
    requests_per_minute: float = 0.0
    requests_per_hour: float = 0.0

    # Метрики ошибок
    error_rate: float = 0.0
    timeout_rate: float = 0.0
    success_rate: float = 0.0

    # Метрики Circuit Breaker
    circuit_breaker_opens: int = 0
    circuit_breaker_closes: int = 0
    circuit_breaker_half_opens: int = 0

    # Метрики балансировки нагрузки
    load_balancer_switches: int = 0
    endpoint_failures: int = 0

    # Метрики ресурсов
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    active_connections: int = 0

    # Метрики качества
    availability_percent: float = 100.0
    reliability_score: float = 1.0
    performance_score: float = 1.0

    def calculate_derived_metrics(self) -> None:
        """Вычисление производных метрик"""
        if self.total_requests > 0:
            self.error_rate = (
                self.failed_requests / self.total_requests
            ) * 100
            self.timeout_rate = (
                self.timeout_requests / self.total_requests
            ) * 100
            self.success_rate = (
                self.successful_requests / self.total_requests
            ) * 100

            # Расчет availability
            if self.total_requests > 0:
                self.availability_percent = self.success_rate

            # Расчет reliability score (0-1)
            self.reliability_score = self.success_rate / 100.0

            # Расчет performance score (0-1)
            if self.avg_response_time > 0:
                # Нормализация по времени отклика (чем меньше, тем лучше)
                self.performance_score = max(
                    0, 1.0 - (self.avg_response_time / 1000.0)
                )
            else:
                self.performance_score = 1.0

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для сериализации"""
        return {
            "service_id": self.service_id,
            "timestamp": self.timestamp.isoformat(),
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "timeout_requests": self.timeout_requests,
            "min_response_time": self.min_response_time,
            "max_response_time": self.max_response_time,
            "avg_response_time": self.avg_response_time,
            "p50_response_time": self.p50_response_time,
            "p95_response_time": self.p95_response_time,
            "p99_response_time": self.p99_response_time,
            "requests_per_second": self.requests_per_second,
            "requests_per_minute": self.requests_per_minute,
            "requests_per_hour": self.requests_per_hour,
            "error_rate": self.error_rate,
            "timeout_rate": self.timeout_rate,
            "success_rate": self.success_rate,
            "circuit_breaker_opens": self.circuit_breaker_opens,
            "circuit_breaker_closes": self.circuit_breaker_closes,
            "circuit_breaker_half_opens": self.circuit_breaker_half_opens,
            "load_balancer_switches": self.load_balancer_switches,
            "endpoint_failures": self.endpoint_failures,
            "memory_usage_mb": self.memory_usage_mb,
            "cpu_usage_percent": self.cpu_usage_percent,
            "active_connections": self.active_connections,
            "availability_percent": self.availability_percent,
            "reliability_score": self.reliability_score,
            "performance_score": self.performance_score,
        }


@dataclass
class SystemMetrics:
    """Системные метрики для всего Service Mesh"""

    timestamp: datetime

    # Общие метрики
    total_services: int = 0
    active_services: int = 0
    unhealthy_services: int = 0

    # Агрегированные метрики
    total_requests: int = 0
    total_successful_requests: int = 0
    total_failed_requests: int = 0

    # Системные метрики
    system_cpu_usage: float = 0.0
    system_memory_usage: float = 0.0
    system_load_average: float = 0.0

    # Метрики сети
    network_throughput_mbps: float = 0.0
    network_latency_ms: float = 0.0

    # Метрики качества системы
    overall_availability: float = 100.0
    overall_reliability: float = 1.0
    overall_performance: float = 1.0

    def calculate_system_metrics(
        self, service_metrics: List[PerformanceMetrics]
    ) -> None:
        """Вычисление системных метрик на основе метрик сервисов"""
        if not service_metrics:
            return

        self.total_services = len(service_metrics)
        self.active_services = len(
            [m for m in service_metrics if m.availability_percent > 95]
        )
        self.unhealthy_services = len(
            [m for m in service_metrics if m.availability_percent < 95]
        )

        self.total_requests = sum(m.total_requests for m in service_metrics)
        self.total_successful_requests = sum(
            m.successful_requests for m in service_metrics
        )
        self.total_failed_requests = sum(
            m.failed_requests for m in service_metrics
        )

        if self.total_requests > 0:
            self.overall_availability = (
                self.total_successful_requests / self.total_requests
            ) * 100
            self.overall_reliability = self.overall_availability / 100.0

        # Средняя производительность
        avg_performance = sum(
            m.performance_score for m in service_metrics
        ) / len(service_metrics)
        self.overall_performance = avg_performance

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для сериализации"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "total_services": self.total_services,
            "active_services": self.active_services,
            "unhealthy_services": self.unhealthy_services,
            "total_requests": self.total_requests,
            "total_successful_requests": self.total_successful_requests,
            "total_failed_requests": self.total_failed_requests,
            "system_cpu_usage": self.system_cpu_usage,
            "system_memory_usage": self.system_memory_usage,
            "system_load_average": self.system_load_average,
            "network_throughput_mbps": self.network_throughput_mbps,
            "network_latency_ms": self.network_latency_ms,
            "overall_availability": self.overall_availability,
            "overall_reliability": self.overall_reliability,
            "overall_performance": self.overall_performance,
        }


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


# ============================================================================
# КЛАССЫ ОПТИМИЗАЦИИ ПРОИЗВОДИТЕЛЬНОСТИ
# ============================================================================

@dataclass
class PerformanceConfig:
    """Конфигурация производительности"""
    # Asyncio настройки
    use_uvloop: bool = True
    max_concurrent_requests: int = 1000
    connection_pool_size: int = 100
    connection_timeout: float = 30.0
    keepalive_timeout: float = 60.0

    # Память
    enable_memory_optimization: bool = True
    max_memory_usage_mb: int = 512
    gc_threshold: int = 1000
    weak_ref_cleanup_interval: int = 300

    # Производительность
    enable_request_batching: bool = True
    batch_size: int = 50
    batch_timeout: float = 0.1
    enable_response_caching: bool = True
    cache_ttl_seconds: int = 60

    # Мониторинг
    enable_performance_monitoring: bool = True
    metrics_collection_interval: int = 5
    performance_alert_threshold: float = 0.8


@dataclass
class ConnectionPoolConfig:
    """Конфигурация пула соединений"""
    max_connections: int = 100
    max_connections_per_host: int = 30
    keepalive_timeout: float = 60.0
    enable_ssl: bool = False
    ssl_verify: bool = True
    connection_timeout: float = 30.0
    read_timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 1.0


class MemoryOptimizer:
    """Оптимизатор памяти"""

    def __init__(self, config: PerformanceConfig):
        self.config = config
        self._weak_refs: List[weakref.ref] = []
        self._gc_count = 0
        self._last_cleanup = time.time()
        self._memory_stats = {
            'peak_memory': 0,
            'current_memory': 0,
            'gc_runs': 0,
            'cleanup_runs': 0
        }

    def register_weak_ref(self, obj: Any) -> None:
        """Регистрация слабой ссылки для автоматической очистки"""
        if self.config.enable_memory_optimization:
            self._weak_refs.append(weakref.ref(obj, self._cleanup_callback))

    def _cleanup_callback(self, weak_ref: weakref.ref) -> None:
        """Callback для очистки слабых ссылок"""
        self._memory_stats['cleanup_runs'] += 1

    def optimize_memory(self) -> Dict[str, Any]:
        """Оптимизация памяти"""
        if not self.config.enable_memory_optimization:
            return self._memory_stats

        current_memory = self._get_memory_usage()
        self._memory_stats['current_memory'] = current_memory
        self._memory_stats['peak_memory'] = max(
            self._memory_stats['peak_memory'],
            current_memory
        )

        # Принудительная сборка мусора при превышении порога
        if current_memory > self.config.max_memory_usage_mb * 1024 * 1024:
            gc.collect()
            self._gc_count += 1
            self._memory_stats['gc_runs'] = self._gc_count

        # Очистка слабых ссылок
        if time.time() - self._last_cleanup > self.config.weak_ref_cleanup_interval:
            self._cleanup_weak_refs()
            self._last_cleanup = time.time()

        return self._memory_stats

    def _cleanup_weak_refs(self) -> None:
        """Очистка недействительных слабых ссылок"""
        self._weak_refs = [ref for ref in self._weak_refs if ref() is not None]

    def _get_memory_usage(self) -> int:
        """Получение текущего использования памяти в байтах"""
        try:
            process = psutil.Process()
            return process.memory_info().rss
        except Exception:
            return 0

    def get_memory_stats(self) -> Dict[str, Any]:
        """Получение статистики памяти"""
        return {
            **self._memory_stats,
            'memory_usage_mb': self._memory_stats['current_memory'] / 1024 / 1024,
            'peak_memory_mb': self._memory_stats['peak_memory'] / 1024 / 1024,
            'weak_refs_count': len(self._weak_refs)
        }


class PerformanceMonitor:
    """Монитор производительности"""

    def __init__(self, config: PerformanceConfig):
        self.config = config
        self._metrics: Dict[str, List[float]] = {
            'response_times': [],
            'throughput': [],
            'memory_usage': [],
            'cpu_usage': []
        }
        self._alerts: List[Dict[str, Any]] = []
        self._start_time = time.time()
        self._request_count = 0
        self._error_count = 0

    def record_request(self, response_time: float, memory_usage: float, cpu_usage: float) -> None:
        """Запись метрики запроса"""
        self._request_count += 1

        # Записываем метрики
        self._metrics['response_times'].append(response_time)
        self._metrics['memory_usage'].append(memory_usage)
        self._metrics['cpu_usage'].append(cpu_usage)

        # Ограничиваем размер массивов метрик
        max_metrics = 1000
        for key in self._metrics:
            if len(self._metrics[key]) > max_metrics:
                self._metrics[key] = self._metrics[key][-max_metrics:]

        # Проверяем пороги производительности
        self._check_performance_thresholds()

    def record_error(self) -> None:
        """Запись ошибки"""
        self._error_count += 1

    def _check_performance_thresholds(self) -> None:
        """Проверка порогов производительности"""
        if not self._metrics['response_times']:
            return

        avg_response_time = sum(self._metrics['response_times']) / len(self._metrics['response_times'])
        current_memory = self._metrics['memory_usage'][-1] if self._metrics['memory_usage'] else 0
        current_cpu = self._metrics['cpu_usage'][-1] if self._metrics['cpu_usage'] else 0

        # Проверяем пороги
        if avg_response_time > 5.0:  # 5 секунд
            self._create_alert('high_response_time', f'Average response time: {avg_response_time:.2f}s')

        if current_memory > self.config.max_memory_usage_mb * 1024 * 1024:
            self._create_alert('high_memory_usage', f'Memory usage: {current_memory / 1024 / 1024:.2f}MB')

        if current_cpu > 80.0:  # 80% CPU
            self._create_alert('high_cpu_usage', f'CPU usage: {current_cpu:.2f}%')

    def _create_alert(self, alert_type: str, message: str) -> None:
        """Создание алерта"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'type': alert_type,
            'message': message,
            'severity': 'warning'
        }
        self._alerts.append(alert)

        # Ограничиваем количество алертов
        if len(self._alerts) > 100:
            self._alerts = self._alerts[-100:]

    def get_performance_stats(self) -> Dict[str, Any]:
        """Получение статистики производительности"""
        uptime = time.time() - self._start_time

        stats = {
            'uptime': uptime,
            'total_requests': self._request_count,
            'total_errors': self._error_count,
            'error_rate': self._error_count / max(self._request_count, 1),
            'throughput': self._request_count / max(uptime, 1),
            'alerts_count': len(self._alerts),
            'recent_alerts': self._alerts[-10:] if self._alerts else []
        }

        # Статистика по метрикам
        for metric_name, values in self._metrics.items():
            if values:
                stats[f'{metric_name}_avg'] = sum(values) / len(values)
                stats[f'{metric_name}_min'] = min(values)
                stats[f'{metric_name}_max'] = max(values)
                stats[f'{metric_name}_count'] = len(values)
            else:
                stats[f'{metric_name}_avg'] = 0
                stats[f'{metric_name}_min'] = 0
                stats[f'{metric_name}_max'] = 0
                stats[f'{metric_name}_count'] = 0

        return stats

    def get_alerts(self) -> List[Dict[str, Any]]:
        """Получение алертов"""
        return self._alerts.copy()

    def clear_alerts(self) -> None:
        """Очистка алертов"""
        self._alerts.clear()


class RequestBatcher:
    """Батчер запросов для оптимизации производительности"""

    def __init__(self, batch_size: int = 50, batch_timeout: float = 0.1):
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self._pending_requests: List[Dict[str, Any]] = []
        self._batch_lock = asyncio.Lock()
        self._batch_task: Optional[asyncio.Task] = None
        self._shutdown = False

    async def add_request(self, request_data: Dict[str, Any]) -> asyncio.Future:
        """Добавление запроса в батч"""
        future = asyncio.Future()
        request_data['future'] = future

        async with self._batch_lock:
            self._pending_requests.append(request_data)

            if len(self._pending_requests) >= self.batch_size:
                await self._process_batch()
            elif not self._batch_task:
                self._batch_task = asyncio.create_task(self._batch_timer())

        return future

    async def _batch_timer(self) -> None:
        """Таймер для обработки батча по времени"""
        await asyncio.sleep(self.batch_timeout)
        async with self._batch_lock:
            if self._pending_requests:
                await self._process_batch()
            self._batch_task = None

    async def _process_batch(self) -> None:
        """Обработка батча запросов"""
        if not self._pending_requests:
            return

        batch = self._pending_requests.copy()
        self._pending_requests.clear()

        # Обрабатываем батч параллельно
        tasks = []
        for request_data in batch:
            task = asyncio.create_task(self._process_single_request(request_data))
            tasks.append(task)

        await asyncio.gather(*tasks, return_exceptions=True)

    async def _process_single_request(self, request_data: Dict[str, Any]) -> None:
        """Обработка одного запроса из батча"""
        try:
            # Здесь должна быть логика обработки запроса
            result = await self._execute_request(request_data)
            request_data['future'].set_result(result)
        except Exception as e:
            request_data['future'].set_exception(e)

    async def _execute_request(self, request_data: Dict[str, Any]) -> Any:
        """Выполнение запроса"""
        # Заглушка - в реальной реализации здесь будет логика запроса
        await asyncio.sleep(0.001)  # Имитация обработки
        return {"status": "processed", "data": request_data}

    async def shutdown(self) -> None:
        """Остановка батчера"""
        self._shutdown = True
        async with self._batch_lock:
            if self._pending_requests:
                await self._process_batch()
        if self._batch_task:
            self._batch_task.cancel()


# ============================================================================
# КЛАССЫ RATE LIMITING
# ============================================================================

@dataclass
class RateLimitConfig:
    """Конфигурация rate limiting"""
    # Общие настройки
    enable_rate_limiting: bool = True
    default_requests_per_minute: int = 100
    default_requests_per_hour: int = 1000
    default_requests_per_day: int = 10000

    # Настройки по сервисам
    service_specific_limits: Dict[str, Dict[str, int]] = None

    # Настройки по пользователям
    user_specific_limits: Dict[str, Dict[str, int]] = None

    # Настройки по IP адресам
    ip_specific_limits: Dict[str, Dict[str, int]] = None

    # Настройки алгоритма
    algorithm: str = "token_bucket"  # token_bucket, sliding_window, fixed_window
    burst_capacity: int = 10  # для token_bucket
    refill_rate: float = 1.0  # токенов в секунду

    # Настройки блокировки
    block_duration_seconds: int = 60
    max_block_duration_seconds: int = 3600  # 1 час

    # Настройки уведомлений
    enable_notifications: bool = True
    notification_threshold: float = 0.8  # 80% от лимита

    def __post_init__(self):
        if self.service_specific_limits is None:
            self.service_specific_limits = {}
        if self.user_specific_limits is None:
            self.user_specific_limits = {}
        if self.ip_specific_limits is None:
            self.ip_specific_limits = {}


@dataclass
class RateLimitInfo:
    """Информация о rate limit"""
    key: str
    limit_type: str  # service, user, ip
    requests_per_minute: int
    requests_per_hour: int
    requests_per_day: int
    current_requests: int = 0
    window_start: datetime = None
    is_blocked: bool = False
    block_until: Optional[datetime] = None
    last_request: Optional[datetime] = None

    def __post_init__(self):
        if self.window_start is None:
            self.window_start = datetime.now()
        if self.last_request is None:
            self.last_request = datetime.now()


class TokenBucket:
    """Реализация алгоритма Token Bucket для rate limiting"""

    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()

    def consume(self, tokens: int = 1) -> bool:
        """Попытка потребить токены"""
        now = time.time()
        time_passed = now - self.last_refill

        # Пополняем токены
        self.tokens = min(self.capacity, self.tokens + time_passed * self.refill_rate)
        self.last_refill = now

        # Проверяем, достаточно ли токенов
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    def get_available_tokens(self) -> float:
        """Получение доступных токенов"""
        now = time.time()
        time_passed = now - self.last_refill
        return min(self.capacity, self.tokens + time_passed * self.refill_rate)


class SlidingWindow:
    """Реализация алгоритма Sliding Window для rate limiting"""

    def __init__(self, window_size: int, max_requests: int):
        self.window_size = window_size  # в секундах
        self.max_requests = max_requests
        self.requests = []

    def is_allowed(self) -> bool:
        """Проверка, разрешен ли запрос"""
        now = time.time()
        window_start = now - self.window_size

        # Удаляем старые запросы
        self.requests = [req_time for req_time in self.requests if req_time > window_start]

        # Проверяем лимит
        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        return False

    def get_remaining_requests(self) -> int:
        """Получение оставшихся запросов"""
        now = time.time()
        window_start = now - self.window_size
        self.requests = [req_time for req_time in self.requests if req_time > window_start]
        return max(0, self.max_requests - len(self.requests))


class RateLimiter:
    """Основной класс rate limiting"""

    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.limiters: Dict[str, Union[TokenBucket, SlidingWindow]] = {}
        self.blocked_keys: Dict[str, datetime] = {}
        self.stats: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.RLock()

    def _get_key(self, limit_type: str, identifier: str) -> str:
        """Получение ключа для rate limiting"""
        return f"{limit_type}:{identifier}"

    def _get_limits(self, limit_type: str, identifier: str) -> Dict[str, int]:
        """Получение лимитов для идентификатора"""
        if limit_type == "service" and identifier in self.config.service_specific_limits:
            return self.config.service_specific_limits[identifier]
        elif limit_type == "user" and identifier in self.config.user_specific_limits:
            return self.config.user_specific_limits[identifier]
        elif limit_type == "ip" and identifier in self.config.ip_specific_limits:
            return self.config.ip_specific_limits[identifier]
        else:
            return {
                "per_minute": self.config.default_requests_per_minute,
                "per_hour": self.config.default_requests_per_hour,
                "per_day": self.config.default_requests_per_day
            }

    def _create_limiter(self, key: str, limit_type: str, identifier: str) -> Union[TokenBucket, SlidingWindow]:
        """Создание лимитера для ключа"""
        limits = self._get_limits(limit_type, identifier)

        if self.config.algorithm == "token_bucket":
            return TokenBucket(
                capacity=limits["per_minute"],
                refill_rate=limits["per_minute"] / 60.0
            )
        elif self.config.algorithm == "sliding_window":
            return SlidingWindow(
                window_size=60,  # 1 минута
                max_requests=limits["per_minute"]
            )
        else:  # fixed_window
            return SlidingWindow(
                window_size=60,
                max_requests=limits["per_minute"]
            )

    def is_allowed(self, limit_type: str, identifier: str, tokens: int = 1) -> bool:
        """Проверка, разрешен ли запрос"""
        if not self.config.enable_rate_limiting:
            return True

        key = self._get_key(limit_type, identifier)

        with self.lock:
            # Проверяем блокировку
            if key in self.blocked_keys:
                if datetime.now() < self.blocked_keys[key]:
                    return False
                else:
                    del self.blocked_keys[key]

            # Получаем или создаем лимитер
            if key not in self.limiters:
                self.limiters[key] = self._create_limiter(key, limit_type, identifier)
                self.stats[key] = {
                    "total_requests": 0,
                    "allowed_requests": 0,
                    "blocked_requests": 0,
                    "last_request": None
                }

            # Проверяем лимит
            limiter = self.limiters[key]

            if isinstance(limiter, TokenBucket):
                allowed = limiter.consume(tokens)
            else:  # SlidingWindow
                allowed = limiter.is_allowed()

            # Обновляем статистику
            self.stats[key]["total_requests"] += 1
            self.stats[key]["last_request"] = datetime.now()

            if allowed:
                self.stats[key]["allowed_requests"] += 1
            else:
                self.stats[key]["blocked_requests"] += 1

                # Блокируем ключ при превышении лимита
                if self.config.block_duration_seconds > 0:
                    block_until = datetime.now() + timedelta(seconds=self.config.block_duration_seconds)
                    self.blocked_keys[key] = block_until

            return allowed

    def get_remaining_requests(self, limit_type: str, identifier: str) -> int:
        """Получение оставшихся запросов"""
        key = self._get_key(limit_type, identifier)

        with self.lock:
            if key not in self.limiters:
                limits = self._get_limits(limit_type, identifier)
                return limits["per_minute"]

            limiter = self.limiters[key]

            if isinstance(limiter, TokenBucket):
                return int(limiter.get_available_tokens())
            else:  # SlidingWindow
                return limiter.get_remaining_requests()

    def get_stats(self, limit_type: str = None, identifier: str = None) -> Dict[str, Any]:
        """Получение статистики rate limiting"""
        with self.lock:
            if limit_type and identifier:
                key = self._get_key(limit_type, identifier)
                return self.stats.get(key, {})
            else:
                return {
                    "total_keys": len(self.limiters),
                    "blocked_keys": len(self.blocked_keys),
                    "stats": dict(self.stats)
                }

    def reset_limits(self, limit_type: str = None, identifier: str = None) -> None:
        """Сброс лимитов"""
        with self.lock:
            if limit_type and identifier:
                key = self._get_key(limit_type, identifier)
                if key in self.limiters:
                    del self.limiters[key]
                if key in self.stats:
                    del self.stats[key]
                if key in self.blocked_keys:
                    del self.blocked_keys[key]
            else:
                self.limiters.clear()
                self.stats.clear()
                self.blocked_keys.clear()

    def unblock_key(self, limit_type: str, identifier: str) -> None:
        """Разблокировка ключа"""
        key = self._get_key(limit_type, identifier)

        with self.lock:
            if key in self.blocked_keys:
                del self.blocked_keys[key]


# ============================================================================
# КЛАССЫ РАСШИРЕННОГО МОНИТОРИНГА И АЛЕРТИНГА
# ============================================================================

@dataclass
class MonitoringConfig:
    """Конфигурация мониторинга"""
    # Основные настройки
    enable_monitoring: bool = True
    monitoring_interval: int = 30  # секунд
    metrics_retention_days: int = 30

    # Настройки алертинга
    enable_alerting: bool = True
    alert_cooldown: int = 300  # 5 минут
    max_alerts_per_hour: int = 10

    # Пороги для алертов
    cpu_threshold: float = 80.0  # %
    memory_threshold: float = 85.0  # %
    disk_threshold: float = 90.0  # %
    response_time_threshold: float = 5.0  # секунд
    error_rate_threshold: float = 5.0  # %

    # Настройки уведомлений
    notification_channels: List[str] = None  # email, slack, webhook
    email_recipients: List[str] = None
    slack_webhook_url: str = None
    webhook_url: str = None

    # Настройки логирования
    log_level: str = "INFO"
    log_format: str = "json"  # json, text
    enable_audit_log: bool = True

    def __post_init__(self):
        if self.notification_channels is None:
            self.notification_channels = ["email"]
        if self.email_recipients is None:
            self.email_recipients = []


@dataclass
class AlertRule:
    """Правило алертинга"""
    name: str
    condition: str  # SQL-like условие
    severity: str  # critical, warning, info
    message: str
    enabled: bool = True
    cooldown: int = 300  # секунд
    notification_channels: List[str] = None

    def __post_init__(self):
        if self.notification_channels is None:
            self.notification_channels = ["email"]


@dataclass
class Alert:
    """Алерт"""
    id: str
    rule_name: str
    severity: str
    message: str
    timestamp: datetime
    service_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class SystemHealth:
    """Состояние системы"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, int]
    active_connections: int
    services_count: int
    healthy_services: int
    total_requests: int
    error_rate: float
    average_response_time: float

    def __post_init__(self):
        if self.network_io is None:
            self.network_io = {"bytes_sent": 0, "bytes_recv": 0}


class MetricsCollector:
    """Сборщик метрик"""

    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.metrics_history: List[Dict[str, Any]] = []
        self.lock = threading.RLock()

    def collect_system_metrics(self) -> SystemHealth:
        """Сбор системных метрик"""
        try:
            import psutil

            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)

            # Memory
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # Disk
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100

            # Network
            network_io = psutil.net_io_counters()
            network_data = {
                "bytes_sent": network_io.bytes_sent,
                "bytes_recv": network_io.bytes_recv
            }

            # Connections
            connections = len(psutil.net_connections())

            return SystemHealth(
                timestamp=datetime.now(),
                cpu_usage=cpu_percent,
                memory_usage=memory_percent,
                disk_usage=disk_percent,
                network_io=network_data,
                active_connections=connections,
                services_count=0,  # Будет заполнено извне
                healthy_services=0,  # Будет заполнено извне
                total_requests=0,  # Будет заполнено извне
                error_rate=0.0,  # Будет заполнено извне
                average_response_time=0.0  # Будет заполнено извне
            )

        except Exception:
            # Возвращаем пустые метрики в случае ошибки
            return SystemHealth(
                timestamp=datetime.now(),
                cpu_usage=0.0,
                memory_usage=0.0,
                disk_usage=0.0,
                network_io={"bytes_sent": 0, "bytes_recv": 0},
                active_connections=0,
                services_count=0,
                healthy_services=0,
                total_requests=0,
                error_rate=0.0,
                average_response_time=0.0
            )

    def collect_service_metrics(self, service_id: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Сбор метрик сервиса"""
        try:
            service_metrics = {
                "timestamp": datetime.now(),
                "service_id": service_id,
                "requests_count": metrics.get("total_requests", 0),
                "successful_requests": metrics.get("successful_requests", 0),
                "failed_requests": metrics.get("failed_requests", 0),
                "average_response_time": metrics.get("average_response_time", 0.0),
                "error_rate": metrics.get("error_rate", 0.0),
                "health_status": metrics.get("health_status", "unknown"),
                "circuit_breaker_state": metrics.get("circuit_breaker_state", "closed")
            }

            with self.lock:
                self.metrics_history.append(service_metrics)

                # Ограничиваем размер истории
                max_history = self.config.metrics_retention_days * 24 * 60 * 2  # 2 записи в минуту
                if len(self.metrics_history) > max_history:
                    self.metrics_history = self.metrics_history[-max_history:]

            return service_metrics

        except Exception as e:
            return {"error": str(e), "timestamp": datetime.now()}


class AlertManager:
    """Менеджер алертов"""

    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.alert_rules: List[AlertRule] = []
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.last_alert_times: Dict[str, datetime] = {}
        self.lock = threading.RLock()

        # Инициализация стандартных правил
        self._setup_default_rules()

    def _setup_default_rules(self) -> None:
        """Настройка стандартных правил алертинга"""
        default_rules = [
            AlertRule(
                name="high_cpu_usage",
                condition="cpu_usage > 80",
                severity="warning",
                message="High CPU usage detected: {cpu_usage}%",
                cooldown=300
            ),
            AlertRule(
                name="high_memory_usage",
                condition="memory_usage > 85",
                severity="warning",
                message="High memory usage detected: {memory_usage}%",
                cooldown=300
            ),
            AlertRule(
                name="high_disk_usage",
                condition="disk_usage > 90",
                severity="critical",
                message="High disk usage detected: {disk_usage}%",
                cooldown=600
            ),
            AlertRule(
                name="high_error_rate",
                condition="error_rate > 5",
                severity="warning",
                message="High error rate detected: {error_rate}%",
                cooldown=180
            ),
            AlertRule(
                name="slow_response_time",
                condition="average_response_time > 5",
                severity="warning",
                message="Slow response time detected: {average_response_time}s",
                cooldown=300
            ),
            AlertRule(
                name="service_down",
                condition="health_status == 'unhealthy'",
                severity="critical",
                message="Service {service_id} is down",
                cooldown=60
            )
        ]

        self.alert_rules.extend(default_rules)

    def add_alert_rule(self, rule: AlertRule) -> None:
        """Добавление правила алертинга"""
        with self.lock:
            self.alert_rules.append(rule)

    def remove_alert_rule(self, rule_name: str) -> None:
        """Удаление правила алертинга"""
        with self.lock:
            self.alert_rules = [r for r in self.alert_rules if r.name != rule_name]

    def evaluate_alerts(self, metrics: Dict[str, Any]) -> List[Alert]:
        """Оценка метрик на предмет алертов"""
        triggered_alerts = []

        with self.lock:
            for rule in self.alert_rules:
                if not rule.enabled:
                    continue

                # Проверяем cooldown
                last_alert = self.last_alert_times.get(rule.name)
                if last_alert and (datetime.now() - last_alert).seconds < rule.cooldown:
                    continue

                # Проверяем условие (упрощенная версия)
                if self._evaluate_condition(rule.condition, metrics):
                    alert = Alert(
                        id=f"{rule.name}_{int(time.time())}",
                        rule_name=rule.name,
                        severity=rule.severity,
                        message=self._format_message(rule.message, metrics),
                        timestamp=datetime.now(),
                        service_id=metrics.get("service_id"),
                        metadata=metrics
                    )

                    triggered_alerts.append(alert)
                    self.active_alerts[alert.id] = alert
                    self.alert_history.append(alert)
                    self.last_alert_times[rule.name] = datetime.now()

        return triggered_alerts

    def _evaluate_condition(self, condition: str, metrics: Dict[str, Any]) -> bool:
        """Оценка условия алерта (упрощенная версия)"""
        try:
            # Простая замена переменных и оценка
            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    condition = condition.replace(f"{key}", str(value))
                elif isinstance(value, str):
                    condition = condition.replace(f"{key}", f"'{value}'")

            # Простая оценка условий
            if ">" in condition:
                parts = condition.split(">")
                if len(parts) == 2:
                    left = float(parts[0].strip())
                    right = float(parts[1].strip())
                    return left > right
            elif "==" in condition:
                parts = condition.split("==")
                if len(parts) == 2:
                    left = parts[0].strip().strip("'\"")
                    right = parts[1].strip().strip("'\"")
                    return left == right

            return False

        except Exception:
            return False

    def _format_message(self, message: str, metrics: Dict[str, Any]) -> str:
        """Форматирование сообщения алерта"""
        try:
            return message.format(**metrics)
        except Exception:
            return message

    def resolve_alert(self, alert_id: str) -> bool:
        """Разрешение алерта"""
        with self.lock:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.resolved = True
                alert.resolved_at = datetime.now()
                del self.active_alerts[alert_id]
                return True
        return False

    def get_active_alerts(self) -> List[Alert]:
        """Получение активных алертов"""
        with self.lock:
            return list(self.active_alerts.values())

    def get_alert_history(self, hours: int = 24) -> List[Alert]:
        """Получение истории алертов"""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        with self.lock:
            return [
                alert for alert in self.alert_history
                if alert.timestamp > cutoff_time
            ]


class NotificationService:
    """Сервис уведомлений"""

    def __init__(self, config: MonitoringConfig):
        self.config = config

    def send_alert_notification(self, alert: Alert, channels: List[str] = None) -> bool:
        """Отправка уведомления об алерте"""
        if not channels:
            channels = alert.metadata.get("notification_channels", self.config.notification_channels)

        success = True

        for channel in channels:
            try:
                if channel == "email":
                    success &= self._send_email_notification(alert)
                elif channel == "slack":
                    success &= self._send_slack_notification(alert)
                elif channel == "webhook":
                    success &= self._send_webhook_notification(alert)
            except Exception as e:
                print(f"Error sending notification via {channel}: {e}")
                success = False

        return success

    def _send_email_notification(self, alert: Alert) -> bool:
        """Отправка email уведомления"""
        # Заглушка для email уведомлений
        print(f"EMAIL ALERT: {alert.severity.upper()} - {alert.message}")
        return True

    def _send_slack_notification(self, alert: Alert) -> bool:
        """Отправка Slack уведомления"""
        # Заглушка для Slack уведомлений
        print(f"SLACK ALERT: {alert.severity.upper()} - {alert.message}")
        return True

    def _send_webhook_notification(self, alert: Alert) -> bool:
        """Отправка webhook уведомления"""
        # Заглушка для webhook уведомлений
        print(f"WEBHOOK ALERT: {alert.severity.upper()} - {alert.message}")
        return True


class ServiceMeshManager(SecurityBase):
    """Менеджер сервисной сетки для микросервисной архитектуры"""

    def __init__(
        self,
        name: str = "ServiceMeshManager",
        config: Optional[Dict[str, Any]] = None,
        performance_config: Optional[PerformanceConfig] = None,
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

        # Расширенные метрики производительности
        self.performance_metrics: Dict[str, PerformanceMetrics] = {}
        self.metrics_history: List[PerformanceMetrics] = []
        self.system_metrics: Optional[SystemMetrics] = None
        self.metrics_collection_interval: int = 30  # секунд
        self.max_metrics_history: int = 1000  # максимальное количество записей

        # Детальная диагностика здоровья
        self.health_check_results: Dict[str, List[HealthCheckResult]] = {}
        self.health_summaries: Dict[str, ServiceHealthSummary] = {}
        self.max_health_history: int = 100  # максимум записей истории здоровья

        # Система событий с паттерном Observer
        self.event_manager = EventManager()
        self._setup_default_observers()

        # Система кэширования с TTL
        cache_config = CacheConfig(
            max_size=1000,
            default_ttl_seconds=300,  # 5 минут
            cleanup_interval_seconds=60,  # 1 минута
            enable_statistics=True
        )
        self.cache = TTLCache(cache_config)
        self.cache_enabled = True

        # Асинхронная поддержка
        async_config = AsyncConfig(
            max_concurrent_requests=100,
            request_timeout=30.0,
            connection_timeout=10.0,
            enable_connection_pooling=True,
            max_connections_per_service=10,
            keepalive_timeout=60.0,
            enable_retry=True,
            max_retries=3,
            retry_delay=1.0,
            retry_backoff_factor=2.0
        )
        self.async_manager = AsyncRequestManager(async_config)
        self.async_enabled = True
        self._async_loop: Optional[asyncio.AbstractEventLoop] = None
        self._async_thread: Optional[threading.Thread] = None

        # Структурированное логирование
        log_config = LogConfig(
            level="INFO",
            format="json",
            include_timestamp=True,
            include_service_id=True,
            include_request_id=True,
            include_metrics=True,
            enable_file_logging=True,
            log_file_path="logs/service_mesh.log",
            enable_console_logging=True
        )
        self.structured_logger = ServiceMeshLogger(log_config)
        self.logging_enabled = True

        # Prometheus метрики
        prometheus_config = PrometheusConfig(
            enable_metrics=True,
            metrics_port=9090,
            metrics_path="/metrics",
            namespace="service_mesh",
            subsystem="manager",
            enable_histograms=True,
            enable_gauges=True,
            enable_counters=True,
            enable_summaries=True,
            custom_labels={"environment": "production", "version": "1.0"}
        )
        self.prometheus_metrics = PrometheusMetrics(prometheus_config)
        self.prometheus_enabled = True

        # Балансировка нагрузки
        self.load_balancers: Dict[str, Dict[str, Any]] = {}
        self.round_robin_counters: Dict[str, int] = {}

        # Circuit Breaker
        # Улучшенные Circuit Breaker для каждого сервиса
        self.circuit_breakers: Dict[str, EnhancedCircuitBreaker] = {}
        self.circuit_breaker_configs: Dict[str, CircuitBreakerConfig] = {}

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

        # Оптимизация производительности
        self.performance_config = performance_config or PerformanceConfig()
        self.connection_pool_config = ConnectionPoolConfig()

        # Инициализация компонентов производительности
        self.memory_optimizer = MemoryOptimizer(self.performance_config)
        self.performance_monitor = PerformanceMonitor(self.performance_config)
        self.request_batcher = RequestBatcher(
            batch_size=self.performance_config.batch_size,
            batch_timeout=self.performance_config.batch_timeout
        )

        # Семафор для ограничения конкурентных запросов
        self._request_semaphore = asyncio.Semaphore(
            self.performance_config.max_concurrent_requests
        )

        # Задачи производительности
        self._performance_monitoring_task: Optional[asyncio.Task] = None
        self._memory_cleanup_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()

        # Rate Limiting
        self.rate_limit_config = RateLimitConfig()
        self.rate_limiter = RateLimiter(self.rate_limit_config)
        self.rate_limiting_enabled = True

        # Расширенный мониторинг и алертинг
        self.monitoring_config = MonitoringConfig()
        self.metrics_collector = MetricsCollector(self.monitoring_config)
        self.alert_manager = AlertManager(self.monitoring_config)
        self.notification_service = NotificationService(self.monitoring_config)
        self.monitoring_enabled = True
        self._monitoring_task: Optional[threading.Thread] = None

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

            # Запуск асинхронного цикла событий
            if self.async_enabled:
                self.start_async_loop()

            # Публикация события запуска системы
            self._publish_event(EventType.SYSTEM_STARTED, None, {
                "total_services": len(self.services),
                "monitoring_interval": self.mesh_config["discovery_interval"],
                "health_check_interval": self.mesh_config["health_check_interval"],
                "async_enabled": self.async_enabled
            })

            self.status = ComponentStatus.RUNNING
            self.log_activity("ServiceMeshManager успешно инициализирован")
            return True

        except Exception as e:
            self.log_activity(
                f"Ошибка инициализации ServiceMeshManager: {e}", "error"
            )
            self.status = ComponentStatus.ERROR
            return False

    def _register_basic_services(self) -> None:
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
        """Регистрация нового сервиса

        Args:
            service: Информация о сервисе для регистрации

        Returns:
            bool: True если сервис успешно зарегистрирован, False при ошибке

        Raises:
            ServiceAlreadyRegisteredError: Если сервис уже зарегистрирован
            InvalidServiceConfigurationError: Если конфигурация сервиса неверна
            ServiceMeshError: При других ошибках

        Example:
            >>> from security.microservices.service_mesh_manager import (
            ...     ServiceInfo, ServiceType, ServiceEndpoint
            ... )
            >>> endpoint = ServiceEndpoint(
            ...     'api_service', 'localhost', 8080, 'http', '/api'
            ... )
            >>> service = ServiceInfo(
            ...     'api_service', 'API Service', 'Description',
            ...     ServiceType.API, '1.0', [endpoint], []
            ... )
            >>> manager = ServiceMeshManager()
            >>> manager.initialize()
            >>> result = manager.register_service(service)
            >>> print(result)  # True
        """
        try:
            # Валидация входных данных с использованием валидатора
            service.service_id = InputValidator.validate_service_id(
                service.service_id
            )
            service.name = InputValidator.validate_string(
                service.name, "name", 1, 255
            )
            service.description = InputValidator.validate_string(
                service.description, "description", 0, 1000
            )
            service.version = InputValidator.validate_string(
                service.version, "version", 1, 50
            )
            service.endpoints = InputValidator.validate_endpoints(
                service.endpoints
            )

            # Валидация зависимостей
            if service.dependencies:
                if not isinstance(service.dependencies, list):
                    raise InvalidServiceConfigurationError(
                        str(service.dependencies),
                        "dependencies",
                        f"не список: {type(service.dependencies)}",
                    )

                for i, dep in enumerate(service.dependencies):
                    if not isinstance(dep, str) or not dep.strip():
                        raise InvalidServiceConfigurationError(
                            str(dep),
                            f"dependencies[{i}]",
                            "пустая строка или не строка",
                        )
                    service.dependencies[i] = dep.strip()

            with self.services_lock:
                # Проверка на дублирование
                if service.service_id in self.services:
                    raise ServiceAlreadyRegisteredError(service.service_id)
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
                    try:
                        self._initialize_load_balancer(service.service_id)
                    except Exception as e:
                        raise LoadBalancingError(
                            service.service_id, "initialization"
                        ) from e

                # Инициализация Circuit Breaker
                if self.mesh_config["enable_circuit_breaker"]:
                    try:
                        self._initialize_circuit_breaker(service.service_id)
                    except Exception as e:
                        raise ServiceMeshError(
                            f"Ошибка инициализации Circuit Breaker: {e}"
                        ) from e

                self.log_activity(
                    f"Сервис {service.service_id} зарегистрирован"
                )

                # Структурированное логирование регистрации сервиса
                if self.logging_enabled:
                    self.structured_logger.log_service_registration(
                        service_id=service.service_id,
                        service_name=service.name,
                        endpoints_count=len(service.endpoints)
                    )

                # Prometheus метрики для регистрации сервиса
                if self.prometheus_enabled:
                    self.prometheus_metrics.increment_counter(
                        "service_registrations_total",
                        label_values={
                            "service_id": service.service_id,
                            "service_type": service.service_type.value
                        }
                    )
                    self.prometheus_metrics.set_gauge(
                        "services_active",
                        len(self.services)
                    )

                # Публикация события регистрации сервиса
                self._publish_event(EventType.SERVICE_REGISTERED, service.service_id, {
                    "service_name": service.name,
                    "endpoints_count": len(service.endpoints),
                    "health_check_interval": service.health_check_interval,
                    "service_type": service.service_type.value
                })

                return True

        except (
            ServiceAlreadyRegisteredError,
            InvalidServiceConfigurationError,
            LoadBalancingError,
            ServiceMeshError,
        ) as e:
            self.log_activity(f"Ошибка регистрации сервиса: {e}", "error")
            raise
        except Exception as e:
            self.log_activity(
                f"Неожиданная ошибка регистрации сервиса "
                f"{service.service_id}: {e}",
                "error",
            )
            raise ServiceMeshError(f"Неожиданная ошибка: {e}") from e

    def unregister_service(self, service_id: str) -> bool:
        """Отмена регистрации сервиса"""
        try:
            # Валидация входных данных
            service_id = InputValidator.validate_service_id(service_id)

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

                    # Публикация события отмены регистрации сервиса
                    self._publish_event(EventType.SERVICE_UNREGISTERED, service_id, {
                        "service_id": service_id,
                        "cleanup_completed": True
                    })

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

    def _initialize_load_balancer(self, service_id: str) -> None:
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

    def _initialize_circuit_breaker(
        self, service_id: str, config: Optional[CircuitBreakerConfig] = None
    ) -> None:
        """Инициализация улучшенного Circuit Breaker для сервиса"""
        try:
            if config is None:
                config = CircuitBreakerConfig.get_default_config()

            self.circuit_breaker_configs[service_id] = config
            self.circuit_breakers[service_id] = EnhancedCircuitBreaker(
                service_id, config
            )

        except Exception as e:
            self.log_activity(
                f"Ошибка инициализации Circuit Breaker для {service_id}: {e}",
                "error",
            )

    def _start_monitoring(self) -> None:
        """Запуск мониторинга сервисов"""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop, daemon=True
        )
        self.monitoring_thread.start()
        self.log_activity("Мониторинг сервисов запущен")

    def _perform_health_checks(self) -> None:
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

    def _check_service_health(self, service_id: str) -> None:
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
            old_status = self.service_health.get(service_id)

            if healthy_endpoints == 0:
                self.service_health[service_id] = ServiceStatus.UNHEALTHY
            elif healthy_endpoints < len(endpoints):
                self.service_health[service_id] = ServiceStatus.DEGRADED
            else:
                self.service_health[service_id] = ServiceStatus.HEALTHY

            # Публикация события изменения здоровья сервиса
            new_status = self.service_health[service_id]
            if old_status != new_status:
                self._publish_event(EventType.SERVICE_HEALTH_CHANGED, service_id, {
                    "old_status": old_status.value if old_status else "unknown",
                    "new_status": new_status.value,
                    "healthy_endpoints": healthy_endpoints,
                    "total_endpoints": len(endpoints),
                    "health_check_timestamp": datetime.now().isoformat()
                })

            # Обновление времени последней проверки
            if service_id in self.services:
                self.services[service_id].last_updated = datetime.now()

        except Exception as e:
            # Публикация события неудачной проверки здоровья
            self._publish_event(EventType.HEALTH_CHECK_FAILED, service_id, {
                "error_message": str(e),
                "error_type": type(e).__name__,
                "health_check_timestamp": datetime.now().isoformat()
            })
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

    def _update_metrics(self) -> None:
        """Обновление метрик сервисов"""
        try:
            updated_services = []
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

                    updated_services.append(service_id)

            # Публикация события обновления метрик
            if updated_services:
                self._publish_event(EventType.METRICS_UPDATED, None, {
                    "updated_services": updated_services,
                    "total_services": len(self.services),
                    "update_timestamp": datetime.now().isoformat()
                })

        except Exception as e:
            self.log_activity(f"Ошибка обновления метрик: {e}", "error")

    def get_service_endpoint(
        self, service_id: str
    ) -> Optional[ServiceEndpoint]:
        """Получение конечной точки сервиса с балансировкой нагрузки"""
        try:
            # Валидация входных данных
            service_id = InputValidator.validate_service_id(service_id)

            # Попытка получить из кэша
            cache_key = f"endpoint_{service_id}"
            try:
                if self.cache_enabled:
                    cached_endpoint = self.cache_get(cache_key)
                    if cached_endpoint and cached_endpoint.is_healthy:
                        return cached_endpoint
            except (CacheKeyNotFoundError, CacheExpiredError):
                pass  # Продолжаем с обычной логикой

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

            selected_endpoint = None
            if strategy == LoadBalancingStrategy.ROUND_ROBIN:
                selected_endpoint = self._round_robin_selection(
                    service_id, healthy_endpoints
                )
            elif strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
                selected_endpoint = self._least_connections_selection(
                    service_id, healthy_endpoints
                )
            elif strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
                selected_endpoint = self._weighted_round_robin_selection(
                    service_id, healthy_endpoints
                )
            elif strategy == LoadBalancingStrategy.LEAST_RESPONSE_TIME:
                selected_endpoint = self._least_response_time_selection(
                    service_id, healthy_endpoints
                )
            elif strategy == LoadBalancingStrategy.RANDOM:
                selected_endpoint = self._random_selection(healthy_endpoints)
            else:
                selected_endpoint = healthy_endpoints[0]

            # Кэширование выбранной конечной точки
            if selected_endpoint and self.cache_enabled:
                self.cache_set(cache_key, selected_endpoint, ttl_seconds=60)  # 1 минута

            return selected_endpoint

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
        """Проверка состояния улучшенного Circuit Breaker"""
        try:
            if service_id not in self.circuit_breakers:
                return True

            cb = self.circuit_breakers[service_id]
            return cb.can_execute()

        except Exception as e:
            self.log_activity(
                f"Ошибка проверки Circuit Breaker для {service_id}: {e}",
                "error",
            )
            return True

    def _update_circuit_breaker(
        self,
        service_id: str,
        success: bool,
        response_time: float = 0.0,
        error: Optional[Exception] = None,
    ) -> None:
        """Обновление состояния улучшенного Circuit Breaker"""
        try:
            if service_id not in self.circuit_breakers:
                return

            cb = self.circuit_breakers[service_id]

            if success:
                cb.record_success(response_time)
            else:
                cb.record_failure(
                    error or Exception("Unknown error"), response_time
                )

            # Публикация событий Circuit Breaker
            current_state = cb.get_state()
            if current_state == CircuitBreakerState.OPEN:
                self._publish_event(EventType.CIRCUIT_BREAKER_OPENED, service_id, {
                    "state": current_state.value,
                    "failure_count": cb.metrics.failure_count,
                    "failure_rate": cb.metrics.failure_rate
                })
            elif current_state == CircuitBreakerState.CLOSED:
                self._publish_event(EventType.CIRCUIT_BREAKER_CLOSED, service_id, {
                    "state": current_state.value,
                    "success_count": cb.metrics.success_count
                })
            elif current_state == CircuitBreakerState.HALF_OPEN:
                self._publish_event(EventType.CIRCUIT_BREAKER_HALF_OPENED, service_id, {
                    "state": current_state.value,
                    "half_open_calls": cb.half_open_calls
                })

        except Exception as e:
            self.log_activity(
                f"Ошибка обновления Circuit Breaker для {service_id}: {e}",
                "error",
            )

    def get_circuit_breaker_metrics(
        self, service_id: str
    ) -> Optional[CircuitBreakerMetrics]:
        """Получение метрик Circuit Breaker для сервиса"""
        try:
            if service_id not in self.circuit_breakers:
                return None

            return self.circuit_breakers[service_id].get_metrics()

        except Exception as e:
            self.log_activity(
                f"Ошибка получения метрик Circuit Breaker для {service_id}: {e}",
                "error",
            )
            return None

    def get_all_circuit_breaker_metrics(
        self,
    ) -> Dict[str, CircuitBreakerMetrics]:
        """Получение метрик всех Circuit Breaker"""
        try:
            metrics = {}
            for service_id, cb in self.circuit_breakers.items():
                metrics[service_id] = cb.get_metrics()
            return metrics

        except Exception as e:
            self.log_activity(
                f"Ошибка получения метрик всех Circuit Breaker: {e}",
                "error",
            )
            return {}

    def reset_circuit_breaker(self, service_id: str) -> bool:
        """Сброс Circuit Breaker для сервиса"""
        try:
            if service_id not in self.circuit_breakers:
                return False

            self.circuit_breakers[service_id].reset()
            self.log_activity(
                f"Circuit Breaker сброшен для {service_id}", "info"
            )
            return True

        except Exception as e:
            self.log_activity(
                f"Ошибка сброса Circuit Breaker для {service_id}: {e}",
                "error",
            )
            return False

    def configure_circuit_breaker(
        self, service_id: str, config: CircuitBreakerConfig
    ) -> bool:
        """Конфигурация Circuit Breaker для сервиса"""
        try:
            if service_id not in self.circuit_breakers:
                return False

            self.circuit_breaker_configs[service_id] = config
            self.circuit_breakers[service_id] = EnhancedCircuitBreaker(
                service_id, config
            )
            self.log_activity(
                f"Circuit Breaker настроен для {service_id}", "info"
            )
            return True

        except Exception as e:
            self.log_activity(
                f"Ошибка конфигурации Circuit Breaker для {service_id}: {e}",
                "error",
            )
            return False

    def get_circuit_breaker_state(
        self, service_id: str
    ) -> Optional[CircuitBreakerState]:
        """Получение состояния Circuit Breaker для сервиса"""
        try:
            if service_id not in self.circuit_breakers:
                return None

            return self.circuit_breakers[service_id].get_state()

        except Exception as e:
            self.log_activity(
                f"Ошибка получения состояния Circuit Breaker для {service_id}: {e}",
                "error",
            )
            return None

    def perform_detailed_health_check(
        self, service_id: str
    ) -> Optional[HealthCheckResult]:
        """Выполнение детальной проверки здоровья сервиса"""
        try:
            if service_id not in self.service_endpoints:
                return None

            endpoints = self.service_endpoints[service_id]
            if not endpoints:
                return None

            # Берем первую конечную точку для проверки
            endpoint = endpoints[0]

            start_time = time.time()

            # Имитация HTTP запроса для проверки здоровья
            health_result = self._perform_http_health_check(endpoint)

            response_time = (
                time.time() - start_time
            ) * 1000  # в миллисекундах

            # Создание результата проверки
            result = HealthCheckResult(
                service_id=service_id,
                endpoint_url=f"{endpoint.protocol}://{endpoint.host}:{endpoint.port}{endpoint.health_check_url or '/health'}",
                status=health_result["status"],
                response_time=response_time,
                timestamp=datetime.now(),
                status_code=health_result.get("status_code"),
                error_message=health_result.get("error_message"),
                headers=health_result.get("headers"),
                memory_usage=health_result.get("memory_usage"),
                cpu_usage=health_result.get("cpu_usage"),
                disk_usage=health_result.get("disk_usage"),
                active_connections=health_result.get("active_connections"),
                database_healthy=health_result.get("database_healthy"),
                cache_healthy=health_result.get("cache_healthy"),
                external_services_healthy=health_result.get(
                    "external_services_healthy"
                ),
                custom_metrics=health_result.get("custom_metrics"),
            )

            # Сохранение результата
            self._save_health_check_result(result)

            return result

        except Exception as e:
            error_result = HealthCheckResult(
                service_id=service_id,
                endpoint_url="unknown",
                status=HealthStatus.UNHEALTHY,
                response_time=0.0,
                timestamp=datetime.now(),
                error_message=str(e),
            )

            self._save_health_check_result(error_result)
            self.log_activity(
                f"Ошибка детальной проверки здоровья для {service_id}: {e}",
                "error",
            )
            return error_result

    def _perform_http_health_check(
        self, endpoint: ServiceEndpoint
    ) -> Dict[str, Any]:
        """Выполнение HTTP проверки здоровья (имитация)"""
        try:
            # В реальной реализации здесь был бы HTTP запрос
            import random

            # Имитация различных сценариев
            scenarios = [
                {
                    "status": HealthStatus.HEALTHY,
                    "status_code": 200,
                    "memory_usage": random.uniform(30, 60),
                    "cpu_usage": random.uniform(10, 40),
                    "disk_usage": random.uniform(20, 70),
                    "active_connections": random.randint(5, 50),
                    "database_healthy": True,
                    "cache_healthy": True,
                    "external_services_healthy": True,
                    "headers": {"Content-Type": "application/json"},
                    "custom_metrics": {
                        "queue_size": random.randint(0, 100),
                        "processing_time": random.uniform(10, 100),
                    },
                },
                {
                    "status": HealthStatus.DEGRADED,
                    "status_code": 200,
                    "memory_usage": random.uniform(70, 85),
                    "cpu_usage": random.uniform(60, 80),
                    "disk_usage": random.uniform(80, 90),
                    "active_connections": random.randint(80, 150),
                    "database_healthy": True,
                    "cache_healthy": False,
                    "external_services_healthy": True,
                    "headers": {"Content-Type": "application/json"},
                    "custom_metrics": {
                        "queue_size": random.randint(200, 500),
                        "processing_time": random.uniform(200, 500),
                    },
                },
                {
                    "status": HealthStatus.UNHEALTHY,
                    "status_code": 503,
                    "error_message": "Service temporarily unavailable",
                    "memory_usage": random.uniform(90, 100),
                    "cpu_usage": random.uniform(90, 100),
                    "database_healthy": False,
                    "cache_healthy": False,
                    "external_services_healthy": False,
                },
            ]

            # Выбор сценария (90% здоровый, 8% деградированный, 2% нездоровый)
            rand = random.random()
            if rand < 0.90:
                return scenarios[0]  # Healthy
            elif rand < 0.98:
                return scenarios[1]  # Degraded
            else:
                return scenarios[2]  # Unhealthy

        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "status_code": 500,
                "error_message": str(e),
            }

    def _save_health_check_result(self, result: HealthCheckResult) -> None:
        """Сохранение результата проверки здоровья"""
        try:
            service_id = result.service_id

            # Сохранение в историю
            if service_id not in self.health_check_results:
                self.health_check_results[service_id] = []

            self.health_check_results[service_id].append(result)

            # Ограничение размера истории
            if (
                len(self.health_check_results[service_id])
                > self.max_health_history
            ):
                self.health_check_results[service_id] = (
                    self.health_check_results[service_id][
                        -self.max_health_history :
                    ]
                )

            # Обновление сводки
            if service_id not in self.health_summaries:
                self.health_summaries[service_id] = ServiceHealthSummary(
                    service_id=service_id,
                    overall_status=result.status,
                    last_check=result.timestamp,
                )

            self.health_summaries[service_id].add_check_result(result)

        except Exception as e:
            self.log_activity(
                f"Ошибка сохранения результата проверки здоровья для {result.service_id}: {e}",
                "error",
            )

    def get_health_check_results(
        self, service_id: str, limit: int = 10
    ) -> List[HealthCheckResult]:
        """Получение результатов проверки здоровья для сервиса"""
        try:
            if service_id not in self.health_check_results:
                return []

            results = self.health_check_results[service_id]
            return results[-limit:] if limit > 0 else results

        except Exception as e:
            self.log_activity(
                f"Ошибка получения результатов проверки здоровья для {service_id}: {e}",
                "error",
            )
            return []

    def get_service_health_summary(
        self, service_id: str
    ) -> Optional[ServiceHealthSummary]:
        """Получение сводки здоровья сервиса"""
        try:
            return self.health_summaries.get(service_id)

        except Exception as e:
            self.log_activity(
                f"Ошибка получения сводки здоровья для {service_id}: {e}",
                "error",
            )
            return None

    def get_all_health_summaries(self) -> Dict[str, ServiceHealthSummary]:
        """Получение сводок здоровья всех сервисов"""
        try:
            return self.health_summaries.copy()

        except Exception as e:
            self.log_activity(
                f"Ошибка получения всех сводок здоровья: {e}",
                "error",
            )
            return {}

    def get_unhealthy_services(self) -> List[str]:
        """Получение списка нездоровых сервисов"""
        try:
            unhealthy = []
            for service_id, summary in self.health_summaries.items():
                if summary.overall_status == HealthStatus.UNHEALTHY:
                    unhealthy.append(service_id)
            return unhealthy

        except Exception as e:
            self.log_activity(
                f"Ошибка получения списка нездоровых сервисов: {e}",
                "error",
            )
            return []

    def get_health_dashboard(self) -> Dict[str, Any]:
        """Получение дашборда здоровья всех сервисов"""
        try:
            total_services = len(self.health_summaries)
            healthy_count = 0
            degraded_count = 0
            unhealthy_count = 0

            for summary in self.health_summaries.values():
                if summary.overall_status == HealthStatus.HEALTHY:
                    healthy_count += 1
                elif summary.overall_status == HealthStatus.DEGRADED:
                    degraded_count += 1
                else:
                    unhealthy_count += 1

            return {
                "timestamp": datetime.now().isoformat(),
                "total_services": total_services,
                "healthy_services": healthy_count,
                "degraded_services": degraded_count,
                "unhealthy_services": unhealthy_count,
                "healthy_percentage": (
                    (healthy_count / total_services * 100)
                    if total_services > 0
                    else 0
                ),
                "service_summaries": {
                    service_id: summary.to_dict()
                    for service_id, summary in self.health_summaries.items()
                },
            }

        except Exception as e:
            self.log_activity(
                f"Ошибка создания дашборда здоровья: {e}",
                "error",
            )
            return {"error": str(e)}

    def send_request(
        self,
        service_id: str,
        method: str,
        path: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Any] = None,
    ) -> Optional["ServiceResponse"]:
        """Отправка запроса к сервису

        Args:
            service_id: Идентификатор сервиса
            method: HTTP метод (GET, POST, PUT, DELETE)
            path: Путь к ресурсу
            headers: Дополнительные заголовки
            body: Тело запроса

        Returns:
            Optional[ServiceResponse]: Ответ от сервиса или None при ошибке

        Raises:
            ServiceNotFoundError: Если сервис не найден
            CircuitBreakerOpenError: Если Circuit Breaker открыт
            ServiceUnavailableError: Если сервис недоступен
            InvalidServiceConfigurationError: Если параметры запроса неверны
            MetricsCollectionError: При ошибке сбора метрик
            ServiceMeshError: При других ошибках

        Example:
            >>> manager = ServiceMeshManager()
            >>> manager.initialize()
            >>> response = manager.send_request(
            ...     'api_service', 'GET', '/health'
            ... )
            >>> if response:
            ...     print(f'Status: {response.status_code}')
            ...     print(f'Response time: {response.response_time}ms')
        """
        try:
            # Валидация входных данных с использованием валидатора
            service_id = InputValidator.validate_service_id(service_id)
            method = InputValidator.validate_http_method(method)
            path = InputValidator.validate_path(path)
            headers = InputValidator.validate_headers(headers)

            # Проверка существования сервиса
            if service_id not in self.services:
                raise ServiceNotFoundError(service_id)

            # Проверка Circuit Breaker
            if self.mesh_config[
                "enable_circuit_breaker"
            ] and not self._is_circuit_breaker_closed(service_id):
                raise CircuitBreakerOpenError(service_id)

            # Получение конечной точки
            endpoint = self.get_service_endpoint(service_id)
            if not endpoint:
                raise ServiceUnavailableError(service_id, "endpoint не найден")

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
            try:
                response = self._execute_request(request, endpoint)
            except Exception as e:
                raise ServiceUnavailableError(
                    service_id, f"Ошибка выполнения запроса: {e}"
                ) from e

            response_time = time.time() - start_time

            if response:
                response.response_time = response_time

                # Обновление метрик
                try:
                    self._update_request_metrics(service_id, response)
                except Exception as e:
                    raise MetricsCollectionError(service_id, str(e)) from e

                # Обновление Circuit Breaker
                if self.mesh_config["enable_circuit_breaker"]:
                    try:
                        self._update_circuit_breaker(
                            service_id, response.status_code < 400
                        )
                    except Exception as e:
                        raise ServiceMeshError(
                            f"Ошибка обновления Circuit Breaker: {e}"
                        ) from e

                # Структурированное логирование запроса
                if self.logging_enabled:
                    self.structured_logger.log_request(
                        service_id=service_id,
                        method=method,
                        path=path,
                        status_code=response.status_code,
                        response_time=response_time,
                        request_id=request_id
                    )

                # Prometheus метрики для запроса
                if self.prometheus_enabled:
                    self.prometheus_metrics.increment_counter(
                        "requests_total",
                        label_values={
                            "service_id": service_id,
                            "method": method,
                            "status_code": str(response.status_code)
                        }
                    )
                    self.prometheus_metrics.observe_histogram(
                        "request_duration_seconds",
                        response_time / 1000.0,  # Конвертация в секунды
                        label_values={
                            "service_id": service_id,
                            "method": method
                        }
                    )
                    self.prometheus_metrics.observe_histogram(
                        "response_size_bytes",
                        len(response.data) if response.data else 0,
                        label_values={"service_id": service_id}
                    )

                # Публикация события успешного запроса
                self._publish_event(EventType.REQUEST_SENT, service_id, {
                    "method": method,
                    "path": path,
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "request_id": request_id
                })

            return response

        except (
            ServiceNotFoundError,
            CircuitBreakerOpenError,
            ServiceUnavailableError,
            InvalidServiceConfigurationError,
            MetricsCollectionError,
            ServiceMeshError,
        ) as e:
            # Структурированное логирование ошибки
            if self.logging_enabled:
                self.structured_logger.log_error(
                    error_type=type(e).__name__,
                    error_message=str(e),
                    service_id=service_id,
                    method=method,
                    path=path,
                    request_id=request_id if 'request_id' in locals() else None
                )

            # Prometheus метрики для ошибки
            if self.prometheus_enabled:
                self.prometheus_metrics.increment_counter(
                    "errors_total",
                    label_values={
                        "service_id": service_id,
                        "error_type": type(e).__name__
                    }
                )

            # Публикация события неудачного запроса
            self._publish_event(EventType.REQUEST_FAILED, service_id, {
                "method": method,
                "path": path,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "request_id": request_id if 'request_id' in locals() else None
            })
            self.log_activity(f"Ошибка отправки запроса: {e}", "error")
            raise
        except Exception as e:
            # Структурированное логирование неожиданной ошибки
            if self.logging_enabled:
                self.structured_logger.log_error(
                    error_type="UnexpectedError",
                    error_message=str(e),
                    service_id=service_id,
                    method=method,
                    path=path,
                    request_id=request_id if 'request_id' in locals() else None
                )

            # Prometheus метрики для неожиданной ошибки
            if self.prometheus_enabled:
                self.prometheus_metrics.increment_counter(
                    "errors_total",
                    label_values={
                        "service_id": service_id,
                        "error_type": "UnexpectedError"
                    }
                )

            # Публикация события неудачного запроса
            self._publish_event(EventType.REQUEST_FAILED, service_id, {
                "method": method,
                "path": path,
                "error_type": "UnexpectedError",
                "error_message": str(e),
                "request_id": request_id if 'request_id' in locals() else None
            })
            self.log_activity(
                f"Неожиданная ошибка отправки запроса к сервису "
                f"{service_id}: {e}",
                "error",
            )
            raise ServiceMeshError(f"Неожиданная ошибка: {e}") from e

    def _execute_request(
        self, request: ServiceRequest, endpoint: ServiceEndpoint
    ) -> Optional["ServiceResponse"]:
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
    ) -> None:
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

            # Остановка асинхронного цикла событий
            if self.async_enabled and self._async_loop is not None:
                self.stop_async_loop()

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

    def __str__(self) -> str:
        """Строковое представление объекта"""
        return (
            f"ServiceMeshManager(name='{self.name}', "
            f"status={self.status.value}, "
            f"services={len(self.services)})"
        )

    def __repr__(self) -> str:
        """Представление объекта для отладки"""
        return (
            f"ServiceMeshManager(name='{self.name}', "
            f"status={self.status.value}, "
            f"services={len(self.services)}, "
            f"monitoring={self.monitoring_active})"
        )

    def __eq__(self, other) -> bool:
        """Проверка равенства объектов"""
        if not isinstance(other, ServiceMeshManager):
            return False
        return (
            self.name == other.name
            and self.status == other.status
            and len(self.services) == len(other.services)
        )

    def __lt__(self, other) -> bool:
        """Сравнение 'меньше' по количеству сервисов"""
        if not isinstance(other, ServiceMeshManager):
            return NotImplemented
        return len(self.services) < len(other.services)

    def __le__(self, other) -> bool:
        """Сравнение 'меньше или равно' по количеству сервисов"""
        if not isinstance(other, ServiceMeshManager):
            return NotImplemented
        return len(self.services) <= len(other.services)

    def __gt__(self, other) -> bool:
        """Сравнение 'больше' по количеству сервисов"""
        if not isinstance(other, ServiceMeshManager):
            return NotImplemented
        return len(self.services) > len(other.services)

    def __ge__(self, other) -> bool:
        """Сравнение 'больше или равно' по количеству сервисов"""
        if not isinstance(other, ServiceMeshManager):
            return NotImplemented
        return len(self.services) >= len(other.services)

    def __ne__(self, other) -> bool:
        """Проверка неравенства объектов"""
        return not self.__eq__(other)

    def __iter__(self):
        """Итерация по зарегистрированным сервисам"""
        return iter(self.services.values())

    def __next__(self):
        """Следующий элемент итерации (используется __iter__)"""
        # Этот метод не будет вызван, так как __iter__ возвращает итератор
        raise StopIteration

    def __enter__(self):
        """Вход в контекстный менеджер"""
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Выход из контекстного менеджера"""
        self.stop()
        return False  # Не подавляем исключения

    # ============================================================================
    # МЕТОДЫ ДЛЯ РАБОТЫ С МЕТРИКАМИ ПРОИЗВОДИТЕЛЬНОСТИ
    # ============================================================================

    def collect_performance_metrics(
        self, service_id: str
    ) -> PerformanceMetrics:
        """Сбор метрик производительности для сервиса"""
        try:
            current_time = datetime.now()

            # Получение базовых метрик
            basic_metrics = self.service_metrics.get(service_id, {})

            # Создание объекта PerformanceMetrics
            metrics = PerformanceMetrics(
                service_id=service_id,
                timestamp=current_time,
                total_requests=basic_metrics.get("requests_count", 0),
                successful_requests=basic_metrics.get("success_count", 0),
                failed_requests=basic_metrics.get("error_count", 0),
                avg_response_time=basic_metrics.get(
                    "average_response_time", 0.0
                ),
            )

            # Расчет дополнительных метрик
            self._calculate_advanced_metrics(metrics, service_id)

            # Вычисление производных метрик
            metrics.calculate_derived_metrics()

            # Сохранение метрик
            self.performance_metrics[service_id] = metrics

            # Добавление в историю
            self.metrics_history.append(metrics)

            # Ограничение размера истории
            if len(self.metrics_history) > self.max_metrics_history:
                self.metrics_history = self.metrics_history[
                    -self.max_metrics_history :
                ]

            return metrics

        except Exception as e:
            self.log_activity(
                f"Ошибка сбора метрик для {service_id}: {e}", "error"
            )
            raise MetricsCollectionError(service_id, str(e)) from e

    def _calculate_advanced_metrics(
        self, metrics: PerformanceMetrics, service_id: str
    ) -> None:
        """Вычисление расширенных метрик"""
        try:
            # Метрики времени (percentiles)
            response_times = self._get_response_times_history(service_id)
            if response_times:
                metrics.min_response_time = min(response_times)
                metrics.max_response_time = max(response_times)
                metrics.p50_response_time = self._calculate_percentile(
                    response_times, 50
                )
                metrics.p95_response_time = self._calculate_percentile(
                    response_times, 95
                )
                metrics.p99_response_time = self._calculate_percentile(
                    response_times, 99
                )

            # Метрики пропускной способности
            time_window = 60  # секунд
            recent_requests = self._get_recent_requests_count(
                service_id, time_window
            )
            metrics.requests_per_second = recent_requests / time_window
            metrics.requests_per_minute = recent_requests
            metrics.requests_per_hour = recent_requests * 60

            # Метрики Circuit Breaker
            if service_id in self.circuit_breakers:
                cb = self.circuit_breakers[service_id]
                metrics.circuit_breaker_opens = cb.get("opens_count", 0)
                metrics.circuit_breaker_closes = cb.get("closes_count", 0)
                metrics.circuit_breaker_half_opens = cb.get(
                    "half_opens_count", 0
                )

            # Метрики балансировки нагрузки
            if service_id in self.load_balancers:
                lb = self.load_balancers[service_id]
                metrics.load_balancer_switches = lb.get("switches_count", 0)
                metrics.endpoint_failures = lb.get("failures_count", 0)

            # Метрики ресурсов (симуляция)
            metrics.memory_usage_mb = self._simulate_memory_usage(service_id)
            metrics.cpu_usage_percent = self._simulate_cpu_usage(service_id)
            metrics.active_connections = self._get_active_connections(
                service_id
            )

        except Exception as e:
            self.log_activity(
                f"Ошибка вычисления расширенных метрик: {e}", "error"
            )

    def _get_response_times_history(self, service_id: str) -> List[float]:
        """Получение истории времен отклика"""
        # В реальной реализации здесь была бы база данных или кэш
        # Пока возвращаем симулированные данные
        import random

        return [random.uniform(10, 500) for _ in range(100)]

    def _calculate_percentile(
        self, data: List[float], percentile: int
    ) -> float:
        """Вычисление перцентиля"""
        if not data:
            return 0.0

        sorted_data = sorted(data)
        index = int((percentile / 100.0) * len(sorted_data))
        index = min(index, len(sorted_data) - 1)
        return sorted_data[index]

    def _get_recent_requests_count(
        self, service_id: str, time_window: int
    ) -> int:
        """Получение количества запросов за последний период"""
        # В реальной реализации здесь был бы анализ логов
        basic_metrics = self.service_metrics.get(service_id, {})
        return basic_metrics.get("requests_count", 0)

    def _simulate_memory_usage(self, service_id: str) -> float:
        """Симуляция использования памяти"""
        import random

        return random.uniform(50, 200)  # MB

    def _simulate_cpu_usage(self, service_id: str) -> float:
        """Симуляция использования CPU"""
        import random

        return random.uniform(10, 80)  # %

    def _get_active_connections(self, service_id: str) -> int:
        """Получение количества активных соединений"""
        # В реальной реализации здесь был бы мониторинг соединений
        return len(self.service_endpoints.get(service_id, []))

    def collect_system_metrics(self) -> SystemMetrics:
        """Сбор системных метрик"""
        try:
            current_time = datetime.now()

            # Создание системных метрик
            system_metrics = SystemMetrics(timestamp=current_time)

            # Сбор метрик всех сервисов
            service_metrics_list = []
            for service_id in self.services:
                try:
                    perf_metrics = self.collect_performance_metrics(service_id)
                    service_metrics_list.append(perf_metrics)
                except Exception as e:
                    self.log_activity(
                        f"Ошибка сбора метрик для {service_id}: {e}", "error"
                    )

            # Вычисление системных метрик
            system_metrics.calculate_system_metrics(service_metrics_list)

            # Симуляция системных метрик
            system_metrics.system_cpu_usage = self._simulate_system_cpu()
            system_metrics.system_memory_usage = self._simulate_system_memory()
            system_metrics.system_load_average = self._simulate_load_average()
            system_metrics.network_throughput_mbps = (
                self._simulate_network_throughput()
            )
            system_metrics.network_latency_ms = (
                self._simulate_network_latency()
            )

            self.system_metrics = system_metrics
            return system_metrics

        except Exception as e:
            self.log_activity(f"Ошибка сбора системных метрик: {e}", "error")
            raise MetricsCollectionError("system", str(e)) from e

    def _simulate_system_cpu(self) -> float:
        """Симуляция системного CPU"""
        import random

        return random.uniform(20, 70)

    def _simulate_system_memory(self) -> float:
        """Симуляция системной памяти"""
        import random

        return random.uniform(40, 85)

    def _simulate_load_average(self) -> float:
        """Симуляция средней нагрузки"""
        import random

        return random.uniform(0.5, 3.0)

    def _simulate_network_throughput(self) -> float:
        """Симуляция пропускной способности сети"""
        import random

        return random.uniform(100, 1000)

    def _simulate_network_latency(self) -> float:
        """Симуляция задержки сети"""
        import random

        return random.uniform(1, 50)

    def get_performance_metrics(
        self, service_id: str
    ) -> Optional[PerformanceMetrics]:
        """Получение метрик производительности для сервиса"""
        return self.performance_metrics.get(service_id)

    def get_all_performance_metrics(self) -> Dict[str, PerformanceMetrics]:
        """Получение всех метрик производительности"""
        return self.performance_metrics.copy()

    def get_system_metrics(self) -> Optional[SystemMetrics]:
        """Получение системных метрик"""
        return self.system_metrics

    def export_metrics_to_json(self, filepath: str) -> bool:
        """Экспорт метрик в JSON файл"""
        try:
            import json

            export_data = {
                "timestamp": datetime.now().isoformat(),
                "system_metrics": (
                    self.system_metrics.to_dict()
                    if self.system_metrics
                    else None
                ),
                "service_metrics": {
                    service_id: metrics.to_dict()
                    for service_id, metrics in self.performance_metrics.items()
                },
                "metrics_history": [
                    m.to_dict() for m in self.metrics_history[-100:]
                ],
            }

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            self.log_activity(f"Метрики экспортированы в {filepath}")
            return True

        except Exception as e:
            self.log_activity(f"Ошибка экспорта метрик: {e}", "error")
            return False

    # ============================================================================
    # МЕТОДЫ СИСТЕМЫ СОБЫТИЙ
    # ============================================================================

    def _setup_default_observers(self) -> None:
        """Настройка наблюдателей по умолчанию"""
        try:
            # Логирующий наблюдатель
            logging_observer = LoggingEventObserver("service_mesh")
            self.event_manager.subscribe(logging_observer)

            # Метрический наблюдатель
            metrics_observer = MetricsEventObserver()
            self.event_manager.subscribe(metrics_observer)

            # Алертинговый наблюдатель с порогами
            alert_thresholds = {
                EventType.HEALTH_CHECK_FAILED: 5,
                EventType.CIRCUIT_BREAKER_OPENED: 3,
                EventType.REQUEST_FAILED: 10,
                EventType.SERVICE_UNREGISTERED: 2
            }
            alerting_observer = AlertingEventObserver(alert_thresholds)
            self.event_manager.subscribe(alerting_observer)

        except Exception as e:
            self.log_activity(f"Ошибка настройки наблюдателей: {e}", "error")

    def _publish_event(self, event_type: EventType, service_id: Optional[str],
                      data: Dict[str, Any]) -> None:
        """Публикация события"""
        try:
            event = ServiceMeshEvent(
                event_type=event_type,
                service_id=service_id,
                timestamp=datetime.now(),
                data=data
            )
            self.event_manager.publish_event(event)

        except Exception as e:
            self.log_activity(f"Ошибка публикации события: {e}", "error")

    def subscribe_observer(self, observer: EventObserver) -> bool:
        """Подписка наблюдателя на события"""
        return self.event_manager.subscribe(observer)

    def unsubscribe_observer(self, observer_id: str) -> bool:
        """Отписка наблюдателя от событий"""
        return self.event_manager.unsubscribe(observer_id)

    def get_event_history(self, event_type: Optional[EventType] = None,
                         limit: int = 100) -> List[ServiceMeshEvent]:
        """Получение истории событий"""
        return self.event_manager.get_event_history(event_type, limit)

    def get_event_metrics(self) -> Dict[str, Any]:
        """Получение метрик событий"""
        try:
            # Получение метрик от метрического наблюдателя
            metrics_observer = None
            for observer in self.event_manager.observers.values():
                if isinstance(observer, MetricsEventObserver):
                    metrics_observer = observer
                    break

            if metrics_observer:
                return metrics_observer.get_event_metrics()

            return {"error": "Метрический наблюдатель не найден"}

        except Exception as e:
            return {"error": f"Ошибка получения метрик событий: {e}"}

    def get_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Получение алертов"""
        try:
            # Получение алертов от алертингового наблюдателя
            alerting_observer = None
            for observer in self.event_manager.observers.values():
                if isinstance(observer, AlertingEventObserver):
                    alerting_observer = observer
                    break

            if alerting_observer:
                return alerting_observer.get_alerts(limit)

            return []

        except Exception as e:
            self.log_activity(f"Ошибка получения алертов: {e}", "error")
            return []

    def enable_events(self) -> None:
        """Включение системы событий"""
        self.event_manager.enable()
        self.log_activity("Система событий включена")

    def disable_events(self) -> None:
        """Отключение системы событий"""
        self.event_manager.disable()
        self.log_activity("Система событий отключена")

    def clear_event_history(self) -> None:
        """Очистка истории событий"""
        self.event_manager.clear_history()
        self.log_activity("История событий очищена")

    # ============================================================================
    # МЕТОДЫ КЭШИРОВАНИЯ С TTL
    # ============================================================================

    def cache_get(self, key: str) -> Any:
        """Получение значения из кэша"""
        try:
            if not self.cache_enabled:
                raise CacheError("Кэширование отключено")

            return self.cache.get(key)

        except (CacheKeyNotFoundError, CacheExpiredError) as e:
            self.log_activity(f"Кэш промах для ключа '{key}': {e}", "debug")
            raise
        except Exception as e:
            self.log_activity(f"Ошибка получения из кэша: {e}", "error")
            raise CacheError(f"Ошибка получения из кэша: {e}") from e

    def cache_set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """Установка значения в кэш"""
        try:
            if not self.cache_enabled:
                self.log_activity("Кэширование отключено, пропуск записи", "debug")
                return

            self.cache.set(key, value, ttl_seconds)
            self.log_activity(f"Значение записано в кэш: {key}", "debug")

        except Exception as e:
            self.log_activity(f"Ошибка записи в кэш: {e}", "error")
            raise CacheError(f"Ошибка записи в кэш: {e}") from e

    def cache_delete(self, key: str) -> bool:
        """Удаление ключа из кэша"""
        try:
            if not self.cache_enabled:
                return False

            result = self.cache.delete(key)
            if result:
                self.log_activity(f"Ключ удален из кэша: {key}", "debug")
            return result

        except Exception as e:
            self.log_activity(f"Ошибка удаления из кэша: {e}", "error")
            raise CacheError(f"Ошибка удаления из кэша: {e}") from e

    def cache_clear(self) -> None:
        """Очистка всего кэша"""
        try:
            if not self.cache_enabled:
                return

            self.cache.clear()
            self.log_activity("Кэш полностью очищен", "info")

        except Exception as e:
            self.log_activity(f"Ошибка очистки кэша: {e}", "error")
            raise CacheError(f"Ошибка очистки кэша: {e}") from e

    def cache_cleanup(self) -> int:
        """Очистка истекших записей из кэша"""
        try:
            if not self.cache_enabled:
                return 0

            cleaned = self.cache.cleanup_expired()
            if cleaned > 0:
                self.log_activity(f"Очищено {cleaned} истекших записей из кэша", "info")
            return cleaned

        except Exception as e:
            self.log_activity(f"Ошибка очистки кэша: {e}", "error")
            raise CacheError(f"Ошибка очистки кэша: {e}") from e

    def cache_get_statistics(self) -> Dict[str, Any]:
        """Получение статистики кэша"""
        try:
            if not self.cache_enabled:
                return {"enabled": False, "message": "Кэширование отключено"}

            stats = self.cache.get_statistics()
            stats["enabled"] = True
            return stats

        except Exception as e:
            self.log_activity(f"Ошибка получения статистики кэша: {e}", "error")
            return {"enabled": self.cache_enabled, "error": str(e)}

    def cache_get_entry_info(self, key: str) -> Optional[Dict[str, Any]]:
        """Получение информации о записи кэша"""
        try:
            if not self.cache_enabled:
                return None

            return self.cache.get_entry_info(key)

        except Exception as e:
            self.log_activity(f"Ошибка получения информации о записи кэша: {e}", "error")
            return None

    def cache_enable(self) -> None:
        """Включение кэширования"""
        self.cache_enabled = True
        self.log_activity("Кэширование включено", "info")

    def cache_disable(self) -> None:
        """Отключение кэширования"""
        self.cache_enabled = False
        self.log_activity("Кэширование отключено", "info")

    def cache_configure(self, config: CacheConfig) -> None:
        """Настройка конфигурации кэша"""
        try:
            self.cache = TTLCache(config)
            self.log_activity("Конфигурация кэша обновлена", "info")

        except Exception as e:
            self.log_activity(f"Ошибка настройки кэша: {e}", "error")
            raise CacheConfigurationError(f"Ошибка настройки кэша: {e}") from e

    def cache_get_or_set(self, key: str, factory_func: callable,
                        ttl_seconds: Optional[int] = None) -> Any:
        """Получение из кэша или создание и сохранение значения"""
        try:
            # Попытка получить из кэша
            cached_value = self.cache_get(key)
            if cached_value is not None:
                return cached_value

            # Создание нового значения если нет в кэше
            value = factory_func()
            self.cache_set(key, value, ttl_seconds)
            return value

        except Exception as e:
            self.log_activity(f"Ошибка cache_get_or_set: {e}", "error")
            raise CacheError(f"Ошибка cache_get_or_set: {e}") from e

    # ============================================================================
    # АСИНХРОННЫЕ МЕТОДЫ
    # ============================================================================

    def start_async_loop(self) -> None:
        """Запуск асинхронного цикла событий"""
        try:
            if self._async_loop is not None and not self._async_loop.is_closed():
                self.log_activity("Асинхронный цикл уже запущен", "warning")
                return

            def run_async_loop():
                self._async_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._async_loop)
                self._async_loop.run_forever()

            self._async_thread = threading.Thread(target=run_async_loop, daemon=True)
            self._async_thread.start()

            # Ожидание запуска цикла
            time.sleep(0.1)
            self.log_activity("Асинхронный цикл событий запущен", "info")

        except Exception as e:
            self.log_activity(f"Ошибка запуска асинхронного цикла: {e}", "error")
            raise AsyncOperationError(f"Ошибка запуска асинхронного цикла: {e}") from e

    def stop_async_loop(self) -> None:
        """Остановка асинхронного цикла событий"""
        try:
            if self._async_loop is None or self._async_loop.is_closed():
                self.log_activity("Асинхронный цикл не запущен", "warning")
                return

            # Отмена всех активных запросов
            if self.async_enabled:
                asyncio.run_coroutine_threadsafe(
                    self.async_manager.cancel_all_requests(), self._async_loop
                )

            # Остановка цикла
            self._async_loop.call_soon_threadsafe(self._async_loop.stop)

            # Ожидание завершения потока
            if self._async_thread and self._async_thread.is_alive():
                self._async_thread.join(timeout=5.0)

            self._async_loop = None
            self._async_thread = None
            self.log_activity("Асинхронный цикл событий остановлен", "info")

        except Exception as e:
            self.log_activity(f"Ошибка остановки асинхронного цикла: {e}", "error")
            raise AsyncOperationError(f"Ошибка остановки асинхронного цикла: {e}") from e

    def send_async_request(self, service_id: str, method: str, path: str,
                          headers: Optional[Dict[str, str]] = None,
                          body: Optional[Any] = None) -> Optional["ServiceResponse"]:
        """Отправка асинхронного запроса (синхронный интерфейс)"""
        try:
            if not self.async_enabled:
                raise AsyncOperationError("Асинхронная поддержка отключена")

            if self._async_loop is None or self._async_loop.is_closed():
                raise AsyncOperationError("Асинхронный цикл не запущен")

            # Валидация входных данных
            service_id = InputValidator.validate_service_id(service_id)
            method = InputValidator.validate_http_method(method)
            path = InputValidator.validate_path(path)
            headers = InputValidator.validate_headers(headers)

            # Проверка существования сервиса
            if service_id not in self.services:
                raise ServiceNotFoundError(service_id)

            # Проверка Circuit Breaker
            if self.mesh_config["enable_circuit_breaker"]:
                if not self._is_circuit_breaker_closed(service_id):
                    raise CircuitBreakerOpenError(service_id)

            # Выполнение асинхронного запроса
            future = asyncio.run_coroutine_threadsafe(
                self.async_manager.send_async_request(service_id, method, path, headers, body),
                self._async_loop
            )

            response = future.result(timeout=self.async_manager.config.request_timeout + 5)

            if response:
                # Обновление метрик
                self._update_request_metrics(service_id, response)

                # Обновление Circuit Breaker
                if self.mesh_config["enable_circuit_breaker"]:
                    self._update_circuit_breaker(service_id, response.status_code < 400)

                # Публикация события
                self._publish_event(EventType.REQUEST_SENT, service_id, {
                    "method": method,
                    "path": path,
                    "status_code": response.status_code,
                    "response_time": response.response_time,
                    "request_id": response.request_id,
                    "async": True
                })

            return response

        except (ServiceNotFoundError, CircuitBreakerOpenError, AsyncTimeoutError) as e:
            # Публикация события неудачного запроса
            self._publish_event(EventType.REQUEST_FAILED, service_id, {
                "method": method,
                "path": path,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "async": True
            })
            self.log_activity(f"Ошибка асинхронного запроса: {e}", "error")
            raise
        except Exception as e:
            # Публикация события неудачного запроса
            self._publish_event(EventType.REQUEST_FAILED, service_id, {
                "method": method,
                "path": path,
                "error_type": "UnexpectedError",
                "error_message": str(e),
                "async": True
            })
            self.log_activity(f"Неожиданная ошибка асинхронного запроса: {e}", "error")
            raise AsyncOperationError(f"Неожиданная ошибка: {e}") from e

    async def send_async_request_async(self, service_id: str, method: str, path: str,
                                     headers: Optional[Dict[str, str]] = None,
                                     body: Optional[Any] = None) -> Optional["ServiceResponse"]:
        """Отправка асинхронного запроса (асинхронный интерфейс)"""
        try:
            if not self.async_enabled:
                raise AsyncOperationError("Асинхронная поддержка отключена")

            # Валидация входных данных
            service_id = InputValidator.validate_service_id(service_id)
            method = InputValidator.validate_http_method(method)
            path = InputValidator.validate_path(path)
            headers = InputValidator.validate_headers(headers)

            # Проверка существования сервиса
            if service_id not in self.services:
                raise ServiceNotFoundError(service_id)

            # Проверка Circuit Breaker
            if self.mesh_config["enable_circuit_breaker"]:
                if not self._is_circuit_breaker_closed(service_id):
                    raise CircuitBreakerOpenError(service_id)

            # Выполнение асинхронного запроса
            response = await self.async_manager.send_async_request(
                service_id, method, path, headers, body
            )

            if response:
                # Обновление метрик
                self._update_request_metrics(service_id, response)

                # Обновление Circuit Breaker
                if self.mesh_config["enable_circuit_breaker"]:
                    self._update_circuit_breaker(service_id, response.status_code < 400)

                # Публикация события
                self._publish_event(EventType.REQUEST_SENT, service_id, {
                    "method": method,
                    "path": path,
                    "status_code": response.status_code,
                    "response_time": response.response_time,
                    "request_id": response.request_id,
                    "async": True
                })

            return response

        except (ServiceNotFoundError, CircuitBreakerOpenError, AsyncTimeoutError) as e:
            # Публикация события неудачного запроса
            self._publish_event(EventType.REQUEST_FAILED, service_id, {
                "method": method,
                "path": path,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "async": True
            })
            self.log_activity(f"Ошибка асинхронного запроса: {e}", "error")
            raise
        except Exception as e:
            # Публикация события неудачного запроса
            self._publish_event(EventType.REQUEST_FAILED, service_id, {
                "method": method,
                "path": path,
                "error_type": "UnexpectedError",
                "error_message": str(e),
                "async": True
            })
            self.log_activity(f"Неожиданная ошибка асинхронного запроса: {e}", "error")
            raise AsyncOperationError(f"Неожиданная ошибка: {e}") from e

    def get_async_statistics(self) -> Dict[str, Any]:
        """Получение статистики асинхронных операций"""
        try:
            if not self.async_enabled:
                return {"enabled": False, "message": "Асинхронная поддержка отключена"}

            stats = self.async_manager.get_statistics()
            stats["enabled"] = True
            stats["loop_running"] = self._async_loop is not None and not self._async_loop.is_closed()
            return stats

        except Exception as e:
            self.log_activity(f"Ошибка получения статистики асинхронных операций: {e}", "error")
            return {"enabled": self.async_enabled, "error": str(e)}

    def enable_async(self) -> None:
        """Включение асинхронной поддержки"""
        self.async_enabled = True
        self.log_activity("Асинхронная поддержка включена", "info")

    def disable_async(self) -> None:
        """Отключение асинхронной поддержки"""
        self.async_enabled = False
        self.log_activity("Асинхронная поддержка отключена", "info")

    def configure_async(self, config: AsyncConfig) -> None:
        """Настройка конфигурации асинхронных операций"""
        try:
            self.async_manager = AsyncRequestManager(config)
            self.log_activity("Конфигурация асинхронных операций обновлена", "info")

        except Exception as e:
            self.log_activity(f"Ошибка настройки асинхронных операций: {e}", "error")
            raise AsyncOperationError(f"Ошибка настройки асинхронных операций: {e}") from e

    # ============================================================================
    # МЕТОДЫ УПРАВЛЕНИЯ ЛОГИРОВАНИЕМ
    # ============================================================================

    def get_logging_statistics(self) -> Dict[str, Any]:
        """Получение статистики логирования"""
        try:
            if not self.logging_enabled:
                return {"enabled": False, "message": "Структурированное логирование отключено"}

            # Базовая статистика логирования
            stats = {
                "enabled": True,
                "total_logs": 0,  # Можно добавить счетчик логов
                "log_level": self.structured_logger.config.level if hasattr(self.structured_logger, 'config') else "INFO",
                "format": self.structured_logger.config.format if hasattr(self.structured_logger, 'config') else "json"
            }
            return stats

        except Exception as e:
            self.log_activity(f"Ошибка получения статистики логирования: {e}", "error")
            return {"enabled": self.logging_enabled, "error": str(e)}

    def enable_logging(self) -> None:
        """Включение структурированного логирования"""
        self.logging_enabled = True
        self.log_activity("Структурированное логирование включено", "info")

    def disable_logging(self) -> None:
        """Отключение структурированного логирования"""
        self.logging_enabled = False
        self.log_activity("Структурированное логирование отключено", "info")

    def configure_logging(self, config: LogConfig) -> None:
        """Настройка конфигурации логирования"""
        try:
            self.structured_logger = ServiceMeshLogger(config)
            self.log_activity("Конфигурация логирования обновлена", "info")

        except Exception as e:
            self.log_activity(f"Ошибка настройки логирования: {e}", "error")
            raise ServiceMeshError(f"Ошибка настройки логирования: {e}") from e

    def set_log_context(self, **kwargs) -> None:
        """Установка контекстных данных для логирования"""
        try:
            if self.logging_enabled:
                self.structured_logger.logger.set_context(**kwargs)
                self.log_activity(f"Контекст логирования обновлен: {kwargs}", "debug")

        except Exception as e:
            self.log_activity(f"Ошибка установки контекста логирования: {e}", "error")

    def clear_log_context(self) -> None:
        """Очистка контекстных данных логирования"""
        try:
            if self.logging_enabled:
                self.structured_logger.logger.clear_context()
                self.log_activity("Контекст логирования очищен", "debug")

        except Exception as e:
            self.log_activity(f"Ошибка очистки контекста логирования: {e}", "error")

    def log_system_event(self, event: str, **kwargs) -> None:
        """Логирование системного события"""
        try:
            if self.logging_enabled:
                self.structured_logger.log_system_event(event, **kwargs)

        except Exception as e:
            self.log_activity(f"Ошибка логирования системного события: {e}", "error")

    def log_health_check_event(self, service_id: str, status: str,
                              healthy_endpoints: int, total_endpoints: int) -> None:
        """Логирование события проверки здоровья"""
        try:
            if self.logging_enabled:
                self.structured_logger.log_health_check(
                    service_id=service_id,
                    status=status,
                    healthy_endpoints=healthy_endpoints,
                    total_endpoints=total_endpoints
                )

        except Exception as e:
            self.log_activity(f"Ошибка логирования проверки здоровья: {e}", "error")

    def log_circuit_breaker_event(self, service_id: str, state: str,
                                 failure_count: int, failure_rate: float) -> None:
        """Логирование события Circuit Breaker"""
        try:
            if self.logging_enabled:
                self.structured_logger.log_circuit_breaker_event(
                    service_id=service_id,
                    state=state,
                    failure_count=failure_count,
                    failure_rate=failure_rate
                )

        except Exception as e:
            self.log_activity(f"Ошибка логирования Circuit Breaker: {e}", "error")

    def log_metrics_event(self, service_id: str, metrics: Dict[str, Any]) -> None:
        """Логирование события метрик"""
        try:
            if self.logging_enabled:
                self.structured_logger.log_metrics_update(
                    service_id=service_id,
                    metrics=metrics
                )

        except Exception as e:
            self.log_activity(f"Ошибка логирования метрик: {e}", "error")

    # ============================================================================
    # МЕТОДЫ УПРАВЛЕНИЯ PROMETHEUS МЕТРИКАМИ
    # ============================================================================

    def get_prometheus_metrics_text(self) -> str:
        """Получение Prometheus метрик в текстовом формате"""
        try:
            if not self.prometheus_enabled:
                return "# Prometheus metrics disabled\n"

            return self.prometheus_metrics.get_metrics_text()

        except Exception as e:
            self.log_activity(f"Ошибка получения Prometheus метрик: {e}", "error")
            return f"# Error getting Prometheus metrics: {e}\n"

    def get_prometheus_metrics_dict(self) -> Dict[str, Any]:
        """Получение Prometheus метрик в виде словаря"""
        try:
            if not self.prometheus_enabled:
                return {"enabled": False, "message": "Prometheus метрики отключены"}

            return self.prometheus_metrics.get_metrics_dict()

        except Exception as e:
            self.log_activity(f"Ошибка получения Prometheus метрик: {e}", "error")
            return {"enabled": self.prometheus_enabled, "error": str(e)}

    def enable_prometheus_metrics(self) -> None:
        """Включение Prometheus метрик"""
        self.prometheus_enabled = True
        self.log_activity("Prometheus метрики включены", "info")

    def disable_prometheus_metrics(self) -> None:
        """Отключение Prometheus метрик"""
        self.prometheus_enabled = False
        self.log_activity("Prometheus метрики отключены", "info")

    def configure_prometheus_metrics(self, config: PrometheusConfig) -> None:
        """Настройка конфигурации Prometheus метрик"""
        try:
            self.prometheus_metrics = PrometheusMetrics(config)
            self.log_activity("Конфигурация Prometheus метрик обновлена", "info")

        except Exception as e:
            self.log_activity(f"Ошибка настройки Prometheus метрик: {e}", "error")
            raise ServiceMeshError(f"Ошибка настройки Prometheus метрик: {e}") from e

    def reset_prometheus_metrics(self) -> None:
        """Сброс всех Prometheus метрик"""
        try:
            if self.prometheus_enabled:
                self.prometheus_metrics.reset_metrics()
                self.log_activity("Prometheus метрики сброшены", "info")

        except Exception as e:
            self.log_activity(f"Ошибка сброса Prometheus метрик: {e}", "error")

    def update_circuit_breaker_metrics(self, service_id: str, state: str,
                                     failure_count: int, failure_rate: float) -> None:
        """Обновление метрик Circuit Breaker"""
        try:
            if self.prometheus_enabled:
                # Обновление состояния Circuit Breaker
                state_value = {"closed": 0, "open": 1, "half_open": 2}.get(state, 0)
                self.prometheus_metrics.set_gauge(
                    "circuit_breaker_state",
                    state_value,
                    label_values={"service_id": service_id}
                )

                # Обновление rate failure
                self.prometheus_metrics.observe_summary(
                    "circuit_breaker_failure_rate",
                    failure_rate,
                    label_values={"service_id": service_id}
                )

                # Увеличение счетчика открытий Circuit Breaker
                if state == "open":
                    self.prometheus_metrics.increment_counter(
                        "circuit_breaker_opens_total",
                        label_values={"service_id": service_id}
                    )

        except Exception as e:
            self.log_activity(f"Ошибка обновления метрик Circuit Breaker: {e}", "error")

    def update_health_check_metrics(self, service_id: str, status: str,
                                   healthy_endpoints: int, total_endpoints: int) -> None:
        """Обновление метрик проверки здоровья"""
        try:
            if self.prometheus_enabled:
                # Обновление статуса здоровья сервиса
                health_value = {"healthy": 1, "degraded": 2, "unhealthy": 0}.get(status, 0)
                self.prometheus_metrics.set_gauge(
                    "service_health_status",
                    health_value,
                    label_values={"service_id": service_id}
                )

                # Увеличение счетчика неудачных проверок здоровья
                if status == "unhealthy":
                    self.prometheus_metrics.increment_counter(
                        "health_check_failures_total",
                        label_values={"service_id": service_id}
                    )

        except Exception as e:
            self.log_activity(f"Ошибка обновления метрик проверки здоровья: {e}", "error")

    def update_cache_metrics(self, cache_size: int, hit_rate: float) -> None:
        """Обновление метрик кэша"""
        try:
            if self.prometheus_enabled:
                # Обновление размера кэша
                self.prometheus_metrics.set_gauge("cache_size", cache_size)

                # Обновление hit rate кэша
                self.prometheus_metrics.observe_summary("cache_hit_rate", hit_rate)

        except Exception as e:
            self.log_activity(f"Ошибка обновления метрик кэша: {e}", "error")

    def update_async_metrics(self, active_requests: int) -> None:
        """Обновление метрик асинхронных операций"""
        try:
            if self.prometheus_enabled:
                self.prometheus_metrics.set_gauge("async_requests_active", active_requests)

        except Exception as e:
            self.log_activity(f"Ошибка обновления метрик асинхронных операций: {e}", "error")

    def export_metrics_to_file(self, file_path: str) -> bool:
        """Экспорт метрик в файл"""
        try:
            if not self.prometheus_enabled:
                return False

            metrics_text = self.get_prometheus_metrics_text()

            import os
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(metrics_text)

            self.log_activity(f"Prometheus метрики экспортированы в {file_path}", "info")
            return True

        except Exception as e:
            self.log_activity(f"Ошибка экспорта метрик в файл: {e}", "error")
            return False

    # ============================================================================
    # МЕТОДЫ ОПТИМИЗАЦИИ ПРОИЗВОДИТЕЛЬНОСТИ
    # ============================================================================

    def enable_performance_optimization(self) -> None:
        """Включение оптимизации производительности"""
        try:
            self.log_activity("Включение оптимизации производительности", "info")

            # Запуск мониторинга производительности только если есть event loop
            if self.performance_config.enable_performance_monitoring and self.async_enabled:
                try:
                    self._start_performance_monitoring()
                except RuntimeError as e:
                    if "no running event loop" in str(e):
                        self.log_activity("Event loop не запущен, пропускаем асинхронный мониторинг", "warning")
                    else:
                        raise

            # Запуск очистки памяти (синхронная)
            self._start_memory_cleanup()

            self.log_activity("Оптимизация производительности включена", "info")

        except Exception as e:
            self.log_activity(f"Ошибка включения оптимизации производительности: {e}", "error")

    def disable_performance_optimization(self) -> None:
        """Отключение оптимизации производительности"""
        try:
            self.log_activity("Отключение оптимизации производительности", "info")

            # Остановка задач производительности
            if self._performance_monitoring_task:
                self._performance_monitoring_task.cancel()
            if self._memory_cleanup_task:
                self._memory_cleanup_task.cancel()

            # Остановка батчера
            asyncio.run(self.request_batcher.shutdown())

            self.log_activity("Оптимизация производительности отключена", "info")

        except Exception as e:
            self.log_activity(f"Ошибка отключения оптимизации производительности: {e}", "error")

    def _start_performance_monitoring(self) -> None:
        """Запуск мониторинга производительности"""
        if self._performance_monitoring_task and not self._performance_monitoring_task.done():
            return

        self._performance_monitoring_task = asyncio.create_task(self._performance_monitoring_loop())

    def _start_memory_cleanup(self) -> None:
        """Запуск очистки памяти"""
        try:
            # Синхронная очистка памяти
            result = self.memory_optimizer.optimize_memory()
            self.log_activity(f"Очистка памяти выполнена: {result}", "info")
        except Exception as e:
            self.log_activity(f"Ошибка очистки памяти: {e}", "error")

    async def _performance_monitoring_loop(self) -> None:
        """Цикл мониторинга производительности"""
        while not self._shutdown_event.is_set():
            try:
                # Собираем метрики
                # Получаем статистику для мониторинга
                self.memory_optimizer.get_memory_stats()
                self.performance_monitor.get_performance_stats()

                # Проверяем алерты
                alerts = self.performance_monitor.get_alerts()
                if alerts:
                    for alert in alerts[-5:]:  # Последние 5 алертов
                        self.log_activity(f"Performance Alert: {alert['message']}", "warning")

                await asyncio.sleep(self.performance_config.metrics_collection_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.log_activity(f"Ошибка мониторинга производительности: {e}", "error")
                await asyncio.sleep(5)

    async def _memory_cleanup_loop(self) -> None:
        """Цикл очистки памяти"""
        while not self._shutdown_event.is_set():
            try:
                # Оптимизируем память
                self.memory_optimizer.optimize_memory()

                await asyncio.sleep(60)  # Каждую минуту

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.log_activity(f"Ошибка очистки памяти: {e}", "error")
                await asyncio.sleep(30)

    def get_performance_stats(self) -> Dict[str, Any]:
        """Получение статистики производительности"""
        return {
            'memory_stats': self.memory_optimizer.get_memory_stats(),
            'performance_stats': self.performance_monitor.get_performance_stats(),
            'config': {
                'use_uvloop': self.performance_config.use_uvloop,
                'max_concurrent_requests': self.performance_config.max_concurrent_requests,
                'enable_memory_optimization': self.performance_config.enable_memory_optimization,
                'enable_performance_monitoring': self.performance_config.enable_performance_monitoring
            }
        }

    def get_performance_alerts(self) -> List[Dict[str, Any]]:
        """Получение алертов производительности"""
        return self.performance_monitor.get_alerts()

    def clear_performance_alerts(self) -> None:
        """Очистка алертов производительности"""
        self.performance_monitor.clear_alerts()

    def optimize_memory_usage(self) -> Dict[str, Any]:
        """Оптимизация использования памяти"""
        return self.memory_optimizer.optimize_memory()

    def get_memory_stats(self) -> Dict[str, Any]:
        """Получение статистики памяти"""
        return self.memory_optimizer.get_memory_stats()

    def register_weak_reference(self, obj: Any) -> None:
        """Регистрация слабой ссылки для автоматической очистки"""
        self.memory_optimizer.register_weak_ref(obj)

    async def send_optimized_request(
        self,
        service_id: str,
        method: str,
        path: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Any] = None,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """Отправка оптимизированного запроса"""
        start_time = time.time()

        async with self._request_semaphore:
            try:
                # Получаем сессию из пула (если используется)
                # Здесь должна быть логика получения сессии из пула соединений

                # Выполняем запрос
                response = await self.send_async_request(service_id, method, path, headers, body, timeout)

                # Записываем метрики
                response_time = time.time() - start_time
                memory_usage = self.memory_optimizer._get_memory_usage()
                cpu_usage = psutil.cpu_percent()

                self.performance_monitor.record_request(
                    response_time, memory_usage, cpu_usage
                )

                return {
                    'response': response,
                    'response_time': response_time,
                    'service_id': service_id,
                    'optimized': True
                }

            except Exception as e:
                self.performance_monitor.record_error()
                self.log_activity(f"Ошибка оптимизированного запроса к {service_id}: {e}", "error")
                raise

    def configure_performance(self, config: PerformanceConfig) -> None:
        """Конфигурация производительности"""
        self.performance_config = config

        # Пересоздаем компоненты с новой конфигурацией
        self.memory_optimizer = MemoryOptimizer(config)
        self.performance_monitor = PerformanceMonitor(config)
        self.request_batcher = RequestBatcher(
            batch_size=config.batch_size,
            batch_timeout=config.batch_timeout
        )

        # Обновляем семафор
        self._request_semaphore = asyncio.Semaphore(config.max_concurrent_requests)

        self.log_activity("Конфигурация производительности обновлена", "info")

    def get_connection_pool_stats(self) -> Dict[str, Any]:
        """Получение статистики пула соединений"""
        # Заглушка - в реальной реализации здесь будет статистика пула соединений
        return {
            'active_connections': 0,
            'total_connections': 0,
            'connection_errors': 0,
            'average_connection_time': 0.0
        }

    def cleanup_resources(self) -> None:
        """Очистка ресурсов"""
        try:
            # Очистка памяти
            self.memory_optimizer.optimize_memory()

            # Очистка кэша
            if hasattr(self, 'cache') and self.cache:
                self.cache.clear()

            # Очистка метрик
            if hasattr(self, 'performance_monitor'):
                self.performance_monitor.clear_alerts()

            self.log_activity("Ресурсы очищены", "info")

        except Exception as e:
            self.log_activity(f"Ошибка очистки ресурсов: {e}", "error")

    # ============================================================================
    # МЕТОДЫ RATE LIMITING
    # ============================================================================

    def enable_rate_limiting(self) -> None:
        """Включение rate limiting"""
        self.rate_limiting_enabled = True
        self.rate_limit_config.enable_rate_limiting = True
        self.log_activity("Rate limiting включен", "info")

    def disable_rate_limiting(self) -> None:
        """Отключение rate limiting"""
        self.rate_limiting_enabled = False
        self.rate_limit_config.enable_rate_limiting = False
        self.log_activity("Rate limiting отключен", "info")

    def configure_rate_limiting(self, config: RateLimitConfig) -> None:
        """Конфигурация rate limiting"""
        self.rate_limit_config = config
        self.rate_limiter = RateLimiter(config)
        self.log_activity("Конфигурация rate limiting обновлена", "info")

    def check_rate_limit(self, limit_type: str, identifier: str, tokens: int = 1) -> bool:
        """Проверка rate limit"""
        if not self.rate_limiting_enabled:
            return True

        try:
            return self.rate_limiter.is_allowed(limit_type, identifier, tokens)
        except Exception as e:
            self.log_activity(f"Ошибка проверки rate limit: {e}", "error")
            return True  # В случае ошибки разрешаем запрос

    def get_remaining_requests(self, limit_type: str, identifier: str) -> int:
        """Получение оставшихся запросов"""
        if not self.rate_limiting_enabled:
            return 999999  # Большое число, если rate limiting отключен

        try:
            return self.rate_limiter.get_remaining_requests(limit_type, identifier)
        except Exception as e:
            self.log_activity(f"Ошибка получения оставшихся запросов: {e}", "error")
            return 0

    def get_rate_limit_stats(self, limit_type: str = None, identifier: str = None) -> Dict[str, Any]:
        """Получение статистики rate limiting"""
        try:
            return self.rate_limiter.get_stats(limit_type, identifier)
        except Exception as e:
            self.log_activity(f"Ошибка получения статистики rate limiting: {e}", "error")
            return {}

    def reset_rate_limits(self, limit_type: str = None, identifier: str = None) -> None:
        """Сброс rate limits"""
        try:
            self.rate_limiter.reset_limits(limit_type, identifier)
            self.log_activity(f"Rate limits сброшены для {limit_type}:{identifier}", "info")
        except Exception as e:
            self.log_activity(f"Ошибка сброса rate limits: {e}", "error")

    def unblock_identifier(self, limit_type: str, identifier: str) -> None:
        """Разблокировка идентификатора"""
        try:
            self.rate_limiter.unblock_key(limit_type, identifier)
            self.log_activity(f"Идентификатор {limit_type}:{identifier} разблокирован", "info")
        except Exception as e:
            self.log_activity(f"Ошибка разблокировки идентификатора: {e}", "error")

    def set_service_rate_limit(self, service_id: str, limits: Dict[str, int]) -> None:
        """Установка rate limit для сервиса"""
        try:
            self.rate_limit_config.service_specific_limits[service_id] = limits
            self.log_activity(f"Rate limit для сервиса {service_id} установлен: {limits}", "info")
        except Exception as e:
            self.log_activity(f"Ошибка установки rate limit для сервиса: {e}", "error")

    def set_user_rate_limit(self, user_id: str, limits: Dict[str, int]) -> None:
        """Установка rate limit для пользователя"""
        try:
            self.rate_limit_config.user_specific_limits[user_id] = limits
            self.log_activity(f"Rate limit для пользователя {user_id} установлен: {limits}", "info")
        except Exception as e:
            self.log_activity(f"Ошибка установки rate limit для пользователя: {e}", "error")

    def set_ip_rate_limit(self, ip_address: str, limits: Dict[str, int]) -> None:
        """Установка rate limit для IP адреса"""
        try:
            self.rate_limit_config.ip_specific_limits[ip_address] = limits
            self.log_activity(f"Rate limit для IP {ip_address} установлен: {limits}", "info")
        except Exception as e:
            self.log_activity(f"Ошибка установки rate limit для IP: {e}", "error")

    def get_rate_limit_info(self, limit_type: str, identifier: str) -> Dict[str, Any]:
        """Получение информации о rate limit"""
        try:
            stats = self.rate_limiter.get_stats(limit_type, identifier)
            remaining = self.rate_limiter.get_remaining_requests(limit_type, identifier)

            return {
                "identifier": identifier,
                "limit_type": limit_type,
                "remaining_requests": remaining,
                "stats": stats,
                "is_enabled": self.rate_limiting_enabled
            }
        except Exception as e:
            self.log_activity(f"Ошибка получения информации о rate limit: {e}", "error")
            return {}

    def send_request_with_rate_limit(
        self,
        service_id: str,
        method: str,
        path: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Any] = None,
        timeout: Optional[float] = None,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Union[ServiceResponse, Dict[str, Any]]:
        """Отправка запроса с проверкой rate limit"""
        try:
            # Проверяем rate limit для сервиса
            if not self.check_rate_limit("service", service_id):
                return {
                    "error": "Service rate limit exceeded",
                    "service_id": service_id,
                    "remaining_requests": self.get_remaining_requests("service", service_id),
                    "status_code": 429
                }

            # Проверяем rate limit для пользователя (если указан)
            if user_id and not self.check_rate_limit("user", user_id):
                return {
                    "error": "User rate limit exceeded",
                    "user_id": user_id,
                    "remaining_requests": self.get_remaining_requests("user", user_id),
                    "status_code": 429
                }

            # Проверяем rate limit для IP (если указан)
            if ip_address and not self.check_rate_limit("ip", ip_address):
                return {
                    "error": "IP rate limit exceeded",
                    "ip_address": ip_address,
                    "remaining_requests": self.get_remaining_requests("ip", ip_address),
                    "status_code": 429
                }

            # Отправляем запрос
            response = self.send_request(service_id, method, path, headers, body, timeout)

            # Логируем успешный запрос
            self.log_activity(f"Запрос к {service_id} выполнен успешно с rate limiting", "info")

            return response

        except Exception as e:
            self.log_activity(f"Ошибка отправки запроса с rate limiting: {e}", "error")
            raise

    def get_rate_limiting_summary(self) -> Dict[str, Any]:
        """Получение сводки по rate limiting"""
        try:
            stats = self.rate_limiter.get_stats()

            return {
                "enabled": self.rate_limiting_enabled,
                "config": {
                    "algorithm": self.rate_limit_config.algorithm,
                    "default_requests_per_minute": self.rate_limit_config.default_requests_per_minute,
                    "block_duration_seconds": self.rate_limit_config.block_duration_seconds
                },
                "stats": stats,
                "service_limits": len(self.rate_limit_config.service_specific_limits),
                "user_limits": len(self.rate_limit_config.user_specific_limits),
                "ip_limits": len(self.rate_limit_config.ip_specific_limits)
            }
        except Exception as e:
            self.log_activity(f"Ошибка получения сводки rate limiting: {e}", "error")
            return {"error": str(e)}

    # ============================================================================
    # МЕТОДЫ РАСШИРЕННОГО МОНИТОРИНГА И АЛЕРТИНГА
    # ============================================================================

    def enable_monitoring(self) -> None:
        """Включение мониторинга"""
        self.monitoring_enabled = True
        self.monitoring_config.enable_monitoring = True
        self._start_monitoring_loop()
        self.log_activity("Мониторинг включен", "info")

    def disable_monitoring(self) -> None:
        """Отключение мониторинга"""
        self.monitoring_enabled = False
        self.monitoring_config.enable_monitoring = False
        self._stop_monitoring_loop()
        self.log_activity("Мониторинг отключен", "info")

    def configure_monitoring(self, config: MonitoringConfig) -> None:
        """Конфигурация мониторинга"""
        self.monitoring_config = config
        self.metrics_collector = MetricsCollector(config)
        self.alert_manager = AlertManager(config)
        self.notification_service = NotificationService(config)
        self.log_activity("Конфигурация мониторинга обновлена", "info")

    def _start_monitoring_loop(self) -> None:
        """Запуск цикла мониторинга"""
        if self._monitoring_task and self._monitoring_task.is_alive():
            return

        self._monitoring_task = threading.Thread(
            target=self._monitoring_loop,
            daemon=True,
            name="MonitoringLoop"
        )
        self._monitoring_task.start()
        self.log_activity("Цикл мониторинга запущен", "info")

    def _stop_monitoring_loop(self) -> None:
        """Остановка цикла мониторинга"""
        if self._monitoring_task and self._monitoring_task.is_alive():
            self._monitoring_task.join(timeout=5)
            self.log_activity("Цикл мониторинга остановлен", "info")

    def _monitoring_loop(self) -> None:
        """Основной цикл мониторинга"""
        while self.monitoring_enabled:
            try:
                # Сбор системных метрик
                system_health = self.metrics_collector.collect_system_metrics()

                # Обновляем метрики сервисов
                system_health.services_count = len(self.services)
                system_health.healthy_services = sum(
                    1 for status in self.service_health.values()
                    if status == ServiceStatus.HEALTHY
                )
                system_health.total_requests = self.total_requests
                system_health.error_rate = (
                    (self.failed_requests / max(self.total_requests, 1)) * 100
                )
                system_health.average_response_time = self.average_response_time

                # Оценка алертов
                metrics_dict = {
                    "cpu_usage": system_health.cpu_usage,
                    "memory_usage": system_health.memory_usage,
                    "disk_usage": system_health.disk_usage,
                    "error_rate": system_health.error_rate,
                    "average_response_time": system_health.average_response_time,
                    "services_count": system_health.services_count,
                    "healthy_services": system_health.healthy_services
                }

                alerts = self.alert_manager.evaluate_alerts(metrics_dict)

                # Отправка уведомлений
                for alert in alerts:
                    self.notification_service.send_alert_notification(alert)
                    self.log_activity(f"Алерт: {alert.severity} - {alert.message}", "warning")

                # Сбор метрик сервисов
                for service_id, metrics in self.service_metrics.items():
                    service_metrics_dict = {
                        "service_id": service_id,
                        "total_requests": metrics.get("total_requests", 0),
                        "successful_requests": metrics.get("successful_requests", 0),
                        "failed_requests": metrics.get("failed_requests", 0),
                        "average_response_time": metrics.get("average_response_time", 0.0),
                        "error_rate": metrics.get("error_rate", 0.0),
                        "health_status": self.service_health.get(service_id, ServiceStatus.UNKNOWN).value,
                        "circuit_breaker_state": "open" if service_id in self.circuit_breakers and
                                                 self.circuit_breakers[service_id].is_open() else "closed"
                    }

                    self.metrics_collector.collect_service_metrics(service_id, service_metrics_dict)

                # Ожидание следующего цикла
                time.sleep(self.monitoring_config.monitoring_interval)

            except Exception as e:
                self.log_activity(f"Ошибка в цикле мониторинга: {e}", "error")
                time.sleep(10)  # Пауза при ошибке

    def get_system_health(self) -> SystemHealth:
        """Получение состояния системы"""
        try:
            return self.metrics_collector.collect_system_metrics()
        except Exception as e:
            self.log_activity(f"Ошибка получения состояния системы: {e}", "error")
            return SystemHealth(
                timestamp=datetime.now(),
                cpu_usage=0.0,
                memory_usage=0.0,
                disk_usage=0.0,
                network_io={"bytes_sent": 0, "bytes_recv": 0},
                active_connections=0,
                services_count=0,
                healthy_services=0,
                total_requests=0,
                error_rate=0.0,
                average_response_time=0.0
            )

    def get_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Получение сводки метрик"""
        try:
            return self.metrics_collector.get_metrics_summary(hours)
        except Exception as e:
            self.log_activity(f"Ошибка получения сводки метрик: {e}", "error")
            return {"error": str(e)}

    def get_active_alerts(self) -> List[Alert]:
        """Получение активных алертов"""
        try:
            return self.alert_manager.get_active_alerts()
        except Exception as e:
            self.log_activity(f"Ошибка получения активных алертов: {e}", "error")
            return []

    def get_alert_history(self, hours: int = 24) -> List[Alert]:
        """Получение истории алертов"""
        try:
            return self.alert_manager.get_alert_history(hours)
        except Exception as e:
            self.log_activity(f"Ошибка получения истории алертов: {e}", "error")
            return []

    def resolve_alert(self, alert_id: str) -> bool:
        """Разрешение алерта"""
        try:
            success = self.alert_manager.resolve_alert(alert_id)
            if success:
                self.log_activity(f"Алерт {alert_id} разрешен", "info")
            return success
        except Exception as e:
            self.log_activity(f"Ошибка разрешения алерта: {e}", "error")
            return False

    def add_alert_rule(self, rule: AlertRule) -> None:
        """Добавление правила алертинга"""
        try:
            self.alert_manager.add_alert_rule(rule)
            self.log_activity(f"Правило алертинга '{rule.name}' добавлено", "info")
        except Exception as e:
            self.log_activity(f"Ошибка добавления правила алертинга: {e}", "error")

    def remove_alert_rule(self, rule_name: str) -> None:
        """Удаление правила алертинга"""
        try:
            self.alert_manager.remove_alert_rule(rule_name)
            self.log_activity(f"Правило алертинга '{rule_name}' удалено", "info")
        except Exception as e:
            self.log_activity(f"Ошибка удаления правила алертинга: {e}", "error")

    def get_monitoring_summary(self) -> Dict[str, Any]:
        """Получение сводки мониторинга"""
        try:
            system_health = self.get_system_health()
            active_alerts = self.get_active_alerts()
            metrics_summary = self.get_metrics_summary(1)  # За последний час

            return {
                "enabled": self.monitoring_enabled,
                "config": {
                    "monitoring_interval": self.monitoring_config.monitoring_interval,
                    "enable_alerting": self.monitoring_config.enable_alerting,
                    "notification_channels": self.monitoring_config.notification_channels
                },
                "system_health": {
                    "cpu_usage": system_health.cpu_usage,
                    "memory_usage": system_health.memory_usage,
                    "disk_usage": system_health.disk_usage,
                    "services_count": system_health.services_count,
                    "healthy_services": system_health.healthy_services,
                    "error_rate": system_health.error_rate,
                    "average_response_time": system_health.average_response_time
                },
                "alerts": {
                    "active_count": len(active_alerts),
                    "active_alerts": [
                        {
                            "id": alert.id,
                            "severity": alert.severity,
                            "message": alert.message,
                            "timestamp": alert.timestamp.isoformat()
                        }
                        for alert in active_alerts
                    ]
                },
                "metrics": metrics_summary
            }
        except Exception as e:
            self.log_activity(f"Ошибка получения сводки мониторинга: {e}", "error")
            return {"error": str(e)}

    def send_test_alert(self, severity: str = "info", message: str = "Test alert") -> bool:
        """Отправка тестового алерта"""
        try:
            test_alert = Alert(
                id=f"test_{int(time.time())}",
                rule_name="test_rule",
                severity=severity,
                message=message,
                timestamp=datetime.now(),
                metadata={"test": True}
            )

            success = self.notification_service.send_alert_notification(test_alert)
            self.log_activity(f"Тестовый алерт отправлен: {message}", "info")
            return success
        except Exception as e:
            self.log_activity(f"Ошибка отправки тестового алерта: {e}", "error")
            return False
