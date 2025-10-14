# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Умный Circuit Breaker
Защита от каскадных сбоев с автоматической настройкой

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-11
"""

import statistics
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, Optional


class CircuitState(Enum):
    """Состояния Circuit Breaker"""

    CLOSED = "closed"  # Нормальная работа
    OPEN = "open"  # Блокировка вызовов
    HALF_OPEN = "half_open"  # Тестирование восстановления


@dataclass
class CircuitBreakerConfig:
    """Конфигурация Circuit Breaker с умными настройками"""

    # Базовые пороги (автоматически настраиваются)
    failure_threshold: int = 5  # Количество ошибок для открытия
    success_threshold: int = 3  # Успешных вызовов для закрытия
    timeout: float = 60.0  # Время блокировки в секундах

    # Адаптивные настройки
    adaptive_threshold: bool = True  # Автоматическая настройка порогов
    min_failure_threshold: int = 3  # Минимальный порог ошибок
    max_failure_threshold: int = 20  # Максимальный порог ошибок

    # Защита от ложных срабатываний
    min_calls_for_analysis: int = 10  # Минимум вызовов для анализа
    error_rate_threshold: float = 0.5  # Порог ошибок (50%)
    consecutive_errors: int = 3  # Подряд идущие ошибки

    # Время восстановления
    recovery_timeout: float = 30.0  # Время до попытки восстановления
    max_recovery_timeout: float = 300.0  # Максимальное время восстановления


class SmartCircuitBreaker:
    """Умный Circuit Breaker с защитой от ложных срабатываний"""

    def __init__(
        self, name: str, config: Optional[CircuitBreakerConfig] = None
    ):
        self.name = name
        self.config = config or CircuitBreakerConfig()

        # Состояние
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.last_success_time = None

        # Статистика для адаптивной настройки
        self.call_history = []  # История вызовов (успех/ошибка)
        self.error_rates = []  # История процента ошибок
        self.response_times = []  # Время ответа

        # Защита от спама
        self.last_alert_time = None
        self.alert_cooldown = 300  # 5 минут между алертами

        # Блокировка для потокобезопасности
        self.lock = threading.Lock()

        # Callback для уведомлений
        self.on_state_change: Optional[Callable] = None
        self.on_alert: Optional[Callable] = None

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Выполнение функции через Circuit Breaker"""
        with self.lock:
            # Проверяем состояние
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                else:
                    raise CircuitBreakerOpenException(
                        f"Circuit breaker {self.name} is OPEN"
                    )

            # Выполняем функцию
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                self._on_success(time.time() - start_time)
                return result

            except Exception as e:
                self._on_failure(time.time() - start_time, e)
                raise

    def _should_attempt_reset(self) -> bool:
        """Проверка, можно ли попытаться восстановить соединение"""
        if self.last_failure_time is None:
            return True

        time_since_failure = time.time() - self.last_failure_time
        return time_since_failure >= self.config.recovery_timeout

    def _on_success(self, response_time: float):
        """Обработка успешного вызова"""
        self.success_count += 1
        self.last_success_time = time.time()

        # Записываем в историю
        self.call_history.append(True)
        self.response_times.append(response_time)

        # Адаптивная настройка
        if self.config.adaptive_threshold:
            self._adapt_thresholds()

        # Проверяем, можно ли закрыть Circuit Breaker
        if (
            self.state == CircuitState.HALF_OPEN
            and self.success_count >= self.config.success_threshold
        ):
            self._change_state(CircuitState.CLOSED)
            self.failure_count = 0

    def _on_failure(self, response_time: float, error: Exception):
        """Обработка неудачного вызова"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        # Записываем в историю
        self.call_history.append(False)
        self.response_times.append(response_time)

        # Адаптивная настройка
        if self.config.adaptive_threshold:
            self._adapt_thresholds()

        # Проверяем, нужно ли открыть Circuit Breaker
        if self._should_open_circuit():
            self._change_state(CircuitState.OPEN)

    def _should_open_circuit(self) -> bool:
        """Проверка, нужно ли открыть Circuit Breaker"""
        # Не открываем, если недостаточно данных
        if len(self.call_history) < self.config.min_calls_for_analysis:
            return False

        # Проверяем процент ошибок
        recent_calls = self.call_history[-self.config.min_calls_for_analysis :]
        error_rate = sum(1 for success in recent_calls if not success) / len(
            recent_calls
        )

        # Проверяем подряд идущие ошибки
        consecutive_errors = 0
        for success in reversed(self.call_history):
            if not success:
                consecutive_errors += 1
            else:
                break

        # Открываем если:
        # 1. Процент ошибок превышает порог ИЛИ
        # 2. Подряд идущие ошибки превышают порог
        return (
            error_rate >= self.config.error_rate_threshold
            or consecutive_errors >= self.config.consecutive_errors
        )

    def _adapt_thresholds(self):
        """Адаптивная настройка порогов на основе истории"""
        if len(self.call_history) < 20:  # Недостаточно данных
            return

        # Анализируем последние 50 вызовов
        recent_calls = self.call_history[-50:]
        error_rate = sum(1 for success in recent_calls if not success) / len(
            recent_calls
        )

        # Анализируем время ответа
        if self.response_times:
            avg_response_time = statistics.mean(self.response_times[-20:])
            response_time_std = (
                statistics.stdev(self.response_times[-20:])
                if len(self.response_times) > 1
                else 0
            )
        else:
            avg_response_time = 1.0
            response_time_std = 0

        # Адаптируем порог ошибок
        if error_rate < 0.1:  # Низкий процент ошибок
            self.config.failure_threshold = max(
                self.config.min_failure_threshold,
                self.config.failure_threshold - 1,
            )
        elif error_rate > 0.3:  # Высокий процент ошибок
            self.config.failure_threshold = min(
                self.config.max_failure_threshold,
                self.config.failure_threshold + 1,
            )

        # Адаптируем время восстановления
        if avg_response_time > 5.0:  # Медленные ответы
            self.config.recovery_timeout = min(
                self.config.max_recovery_timeout,
                self.config.recovery_timeout * 1.2,
            )
        elif avg_response_time < 1.0:  # Быстрые ответы
            self.config.recovery_timeout = max(
                10.0, self.config.recovery_timeout * 0.9  # Минимум 10 секунд
            )

    def _change_state(self, new_state: CircuitState):
        """Изменение состояния с уведомлениями"""
        old_state = self.state
        self.state = new_state

        # Уведомляем о изменении состояния
        if self.on_state_change:
            try:
                self.on_state_change(self.name, old_state, new_state)
            except Exception:
                pass  # Игнорируем ошибки в callback

        # Отправляем алерт (с защитой от спама)
        if self._should_send_alert():
            self._send_alert(new_state)

    def _should_send_alert(self) -> bool:
        """Проверка, нужно ли отправить алерт (защита от спама)"""
        if self.last_alert_time is None:
            return True

        time_since_alert = time.time() - self.last_alert_time
        return time_since_alert >= self.alert_cooldown

    def _send_alert(self, state: CircuitState):
        """Отправка алерта"""
        self.last_alert_time = time.time()

        if self.on_alert:
            try:
                alert_data = {
                    "circuit_breaker": self.name,
                    "state": state.value,
                    "failure_count": self.failure_count,
                    "success_count": self.success_count,
                    "error_rate": self.get_error_rate(),
                    "timestamp": datetime.now().isoformat(),
                }
                self.on_alert(alert_data)
            except Exception:
                pass  # Игнорируем ошибки в callback

    def get_error_rate(self) -> float:
        """Получение текущего процента ошибок"""
        if not self.call_history:
            return 0.0

        recent_calls = self.call_history[-20:]  # Последние 20 вызовов
        return sum(1 for success in recent_calls if not success) / len(
            recent_calls
        )

    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики Circuit Breaker"""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "error_rate": self.get_error_rate(),
            "total_calls": len(self.call_history),
            "avg_response_time": (
                statistics.mean(self.response_times)
                if self.response_times
                else 0
            ),
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
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "success_threshold": self.config.success_threshold,
                "timeout": self.config.timeout,
                "adaptive_threshold": self.config.adaptive_threshold,
            },
        }

    def reset(self):
        """Сброс Circuit Breaker"""
        with self.lock:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.last_failure_time = None
            self.last_success_time = None

    def get_status(self) -> str:
        """Получение статуса Circuit Breaker"""
        try:
            return self.state.value
        except Exception:
            return "unknown"

    def start_breaker(self) -> bool:
        """Запуск Circuit Breaker"""
        try:
            with self.lock:
                if self.state == CircuitState.CLOSED:
                    return True
                else:
                    self.state = CircuitState.CLOSED
                    return True
        except Exception:
            return False

    def stop_breaker(self) -> bool:
        """Остановка Circuit Breaker"""
        try:
            with self.lock:
                self.state = CircuitState.OPEN
                return True
        except Exception:
            return False

    def get_breaker_info(self) -> Dict[str, Any]:
        """Получение информации о Circuit Breaker"""
        try:
            with self.lock:
                return {
                    "name": self.name,
                    "state": self.state.value,
                    "failure_count": self.failure_count,
                    "success_count": self.success_count,
                    "error_rate": self.get_error_rate(),
                    "is_healthy": self.state == CircuitState.CLOSED,
                    "last_failure": self.last_failure_time,
                    "last_success": self.last_success_time,
                }
        except Exception as e:
            return {
                "name": self.name,
                "state": "error",
                "failure_count": 0,
                "success_count": 0,
                "error_rate": 0.0,
                "is_healthy": False,
                "last_failure": None,
                "last_success": None,
                "error": str(e),
            }


class CircuitBreakerOpenException(Exception):
    """Исключение при открытом Circuit Breaker"""

    pass


# Глобальный реестр Circuit Breaker'ов
_circuit_breakers: Dict[str, SmartCircuitBreaker] = {}


def get_circuit_breaker(
    name: str, config: Optional[CircuitBreakerConfig] = None
) -> SmartCircuitBreaker:
    """Получение или создание Circuit Breaker"""
    if name not in _circuit_breakers:
        _circuit_breakers[name] = SmartCircuitBreaker(name, config)
    return _circuit_breakers[name]


def get_all_circuit_breakers() -> Dict[str, Dict[str, Any]]:
    """Получение статистики всех Circuit Breaker'ов"""
    return {name: cb.get_stats() for name, cb in _circuit_breakers.items()}
