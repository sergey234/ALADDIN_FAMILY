#!/usr/bin/env python3
"""
ALADDIN VPN - Retry Handler with Exponential Backoff
Система повторных попыток с экспоненциальной задержкой

Автор: ALADDIN Security Team
Версия: 1.0.0
Дата: 01.10.2025
"""

import asyncio
import time
import random
import logging
from typing import Callable, Any, List, Type, Tuple
from functools import wraps
from dataclasses import dataclass
from enum import Enum
from contextlib import asynccontextmanager
from security.types.security_types import VPNSecurityError

from exceptions.vpn_exceptions import VPNException, ConnectionTimeoutError, NetworkError

# Настройка логирования
logger = logging.getLogger(__name__)

# ============================================================================
# ТИПЫ СТРАТЕГИЙ ПОВТОРОВ
# ============================================================================


class RetryStrategy(Enum):
    """Стратегии повторных попыток"""
    FIXED = "fixed"                    # Фиксированная задержка
    EXPONENTIAL = "exponential"        # Экспоненциальная задержка
    LINEAR = "linear"                  # Линейная задержка
    CUSTOM = "custom"                  # Пользовательская стратегия


class RetryCondition(Enum):
    """Условия для повторных попыток"""
    ON_EXCEPTION = "on_exception"      # При любом исключении
    ON_SPECIFIC_EXCEPTION = "on_specific"  # При конкретном исключении
    ON_RETURN_VALUE = "on_return_value"    # При определенном возвращаемом значении
    ON_CUSTOM_CONDITION = "on_custom"      # При пользовательском условии

# ============================================================================
# КОНФИГУРАЦИЯ ПОВТОРОВ
# ============================================================================

@dataclass
class RetryConfig:
    """Конфигурация повторных попыток"""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    jitter: bool = True
    jitter_range: float = 0.1
    condition: RetryCondition = RetryCondition.ON_EXCEPTION
    specific_exceptions: Tuple[Type[Exception], ...] = (Exception,)
    return_value_condition: Callable[[Any], bool] = None
    custom_condition: Callable[[Exception, int], bool] = None
    backoff_multiplier: float = 2.0
    linear_increment: float = 1.0
    custom_delays: List[float] = None
    stop_on_exception: Tuple[Type[Exception], ...] = ()
    log_attempts: bool = True
    log_success: bool = False

# ============================================================================
# ОСНОВНОЙ КЛАСС RETRY HANDLER
# ============================================================================


class RetryHandler:
    """Обработчик повторных попыток с различными стратегиями"""

    def __init__(self, config: RetryConfig = None):
        self.config = config or RetryConfig()
        self._attempt_count = 0
        self._start_time = None
        self._last_exception = None

    def calculate_delay(self, attempt: int) -> float:
        """Расчет задержки для попытки"""
        if self.config.custom_delays and attempt < len(self.config.custom_delays):
            delay = self.config.custom_delays[attempt]
        elif self.config.strategy == RetryStrategy.FIXED:
            delay = self.config.base_delay
        elif self.config.strategy == RetryStrategy.EXPONENTIAL:
            delay = min(
                self.config.base_delay * (self.config.backoff_multiplier ** (attempt - 1)),
                self.config.max_delay
            )
        elif self.config.strategy == RetryStrategy.LINEAR:
            delay = min(
                self.config.base_delay + (self.config.linear_increment * (attempt - 1)),
                self.config.max_delay
            )
        else:
            delay = self.config.base_delay

        # Добавляем jitter для предотвращения thundering herd
        if self.config.jitter:
            jitter_amount = delay * self.config.jitter_range
            delay += random.uniform(-jitter_amount, jitter_amount)

        return max(0, delay)

    def should_retry(self, exception: Exception = None, return_value: Any = None, attempt: int = 0) -> bool:
        """Определение необходимости повторной попытки"""
        # Проверяем максимальное количество попыток
        if attempt >= self.config.max_attempts:
            return False

        # Проверяем исключения, при которых нужно остановиться
        if exception and self.config.stop_on_exception:
            if isinstance(exception, self.config.stop_on_exception):
                return False

        # Проверяем условие повторной попытки
        if self.config.condition == RetryCondition.ON_EXCEPTION:
            return exception is not None
        elif self.config.condition == RetryCondition.ON_SPECIFIC_EXCEPTION:
            return exception is not None and isinstance(exception, self.config.specific_exceptions)
        elif self.config.condition == RetryCondition.ON_RETURN_VALUE:
            return return_value is not None and self.config.return_value_condition(return_value)
        elif self.config.condition == RetryCondition.ON_CUSTOM_CONDITION:
            return self.config.custom_condition(exception, attempt)

        return False

    def log_attempt(self, attempt: int, exception: Exception = None, delay: float = 0):
        """Логирование попытки"""
        if not self.config.log_attempts:
            return

        if exception:
            logger.warning(
                f"Retry attempt {attempt}/{self.config.max_attempts} failed: {type(exception).__name__}: {exception}. "
                f"Retrying in {delay:.2f}s"
            )
        else:
            logger.info(f"Retry attempt {attempt}/{self.config.max_attempts} starting")

    def log_success(self, attempt: int, total_time: float):
        """Логирование успешной попытки"""
        if self.config.log_success:
            logger.info(f"Operation succeeded on attempt {attempt} after {total_time:.2f}s")

    async def execute_async(self, func: Callable, *args, **kwargs) -> Any:
        """Асинхронное выполнение с повторными попытками"""
        self._attempt_count = 0
        self._start_time = time.time()
        self._last_exception = None

        while self._attempt_count < self.config.max_attempts:
            self._attempt_count += 1

            try:
                # Выполняем функцию
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)

                # Проверяем условие повторной попытки по возвращаемому значению
                if self.should_retry(return_value=result, attempt=self._attempt_count):
                    delay = self.calculate_delay(self._attempt_count)
                    self.log_attempt(self._attempt_count, delay=delay)
                    await asyncio.sleep(delay)
                    continue

                # Успешное выполнение
                total_time = time.time() - self._start_time
                self.log_success(self._attempt_count, total_time)
                return result

            except Exception as e:
                self._last_exception = e

                # Проверяем необходимость повторной попытки
                if not self.should_retry(exception=e, attempt=self._attempt_count):
                    raise e

                # Рассчитываем задержку и ждем
                delay = self.calculate_delay(self._attempt_count)
                self.log_attempt(self._attempt_count, e, delay)
                await asyncio.sleep(delay)

        # Все попытки исчерпаны
        if self._last_exception:
            raise self._last_exception
        else:
            raise VPNException("All retry attempts exhausted")

    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Синхронное выполнение с повторными попытками"""
        self._attempt_count = 0
        self._start_time = time.time()
        self._last_exception = None

        while self._attempt_count < self.config.max_attempts:
            self._attempt_count += 1

            try:
                # Выполняем функцию
                result = func(*args, **kwargs)

                # Проверяем условие повторной попытки по возвращаемому значению
                if self.should_retry(return_value=result, attempt=self._attempt_count):
                    delay = self.calculate_delay(self._attempt_count)
                    self.log_attempt(self._attempt_count, delay=delay)
                    time.sleep(delay)
                    continue

                # Успешное выполнение
                total_time = time.time() - self._start_time
                self.log_success(self._attempt_count, total_time)
                return result

            except Exception as e:
                self._last_exception = e

                # Проверяем необходимость повторной попытки
                if not self.should_retry(exception=e, attempt=self._attempt_count):
                    raise e

                # Рассчитываем задержку и ждем
                delay = self.calculate_delay(self._attempt_count)
                self.log_attempt(self._attempt_count, e, delay)
                time.sleep(delay)

        # Все попытки исчерпаны
        if self._last_exception:
            raise self._last_exception
        else:
            raise VPNException("All retry attempts exhausted")

# ============================================================================
# CIRCUIT BREAKER PATTERN
# ============================================================================


class CircuitState(Enum):
    """Состояния Circuit Breaker"""
    CLOSED = "closed"      # Нормальная работа
    OPEN = "open"          # Разомкнут (блокирует запросы)
    HALF_OPEN = "half_open"  # Полуоткрыт (тестирует восстановление)


class CircuitBreaker:
    """Circuit Breaker для предотвращения каскадных сбоев"""

    def __init__(self,
                 failure_threshold: int = 5,
                 recovery_timeout: float = 60.0,
                 expected_exception: Type[Exception] = Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    def can_execute(self) -> bool:
        """Проверка возможности выполнения"""
        if self.state == CircuitState.CLOSED:
            return True
        elif self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                return True
            return False
        elif self.state == CircuitState.HALF_OPEN:
            return True

        return False

    def on_success(self):
        """Обработка успешного выполнения"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def on_failure(self, exception: Exception):
        """Обработка неудачного выполнения"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")

    async def execute_async(self, func: Callable, *args, **kwargs) -> Any:
        """Асинхронное выполнение через Circuit Breaker"""
        if not self.can_execute():
            raise VPNException("Circuit breaker is open")

        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            self.on_success()
            return result

        except self.expected_exception as e:
            self.on_failure(e)
            raise e

    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Синхронное выполнение через Circuit Breaker"""
        if not self.can_execute():
            raise VPNException("Circuit breaker is open")

        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result

        except self.expected_exception as e:
            self.on_failure(e)
            raise e

# ============================================================================
# ДЕКОРАТОРЫ
# ============================================================================


def retry(config: RetryConfig = None, **kwargs):
    """Декоратор для повторных попыток"""
    if config is None:
        config = RetryConfig(**kwargs)

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            handler = RetryHandler(config)
            return await handler.execute_async(func, *args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            handler = RetryHandler(config)
            return handler.execute(func, *args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def circuit_breaker(failure_threshold: int = 5,
                    recovery_timeout: float = 60.0,
                    expected_exception: Type[Exception] = Exception):
    """Декоратор для Circuit Breaker"""
    def decorator(func):
        breaker = CircuitBreaker(failure_threshold, recovery_timeout, expected_exception)

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await breaker.execute_async(func, *args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return breaker.execute(func, *args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator

# ============================================================================
# КОНТЕКСТНЫЕ МЕНЕДЖЕРЫ
# ============================================================================

@asynccontextmanager
async def retry_context(config: RetryConfig = None, **kwargs):
    """Контекстный менеджер для повторных попыток"""
    if config is None:
        config = RetryConfig(**kwargs)

    handler = RetryHandler(config)
    yield handler

@asynccontextmanager
async def circuit_breaker_context(failure_threshold: int = 5,
                                  recovery_timeout: float = 60.0,
                                  expected_exception: Type[Exception] = Exception):
    """Контекстный менеджер для Circuit Breaker"""
    breaker = CircuitBreaker(failure_threshold, recovery_timeout, expected_exception)
    yield breaker

# ============================================================================
# ПРЕДУСТАНОВЛЕННЫЕ КОНФИГУРАЦИИ
# ============================================================================

# Конфигурации для различных типов операций
CONFIGS = {
    "database": RetryConfig(
        max_attempts=3,
        base_delay=1.0,
        max_delay=10.0,
        strategy=RetryStrategy.EXPONENTIAL,
        specific_exceptions=(ConnectionTimeoutError, NetworkError),
        stop_on_exception=(VPNException,)
    ),

    "api_call": RetryConfig(
        max_attempts=5,
        base_delay=0.5,
        max_delay=30.0,
        strategy=RetryStrategy.EXPONENTIAL,
        jitter=True,
        specific_exceptions=(ConnectionTimeoutError, NetworkError)
    ),

    "file_operation": RetryConfig(
        max_attempts=3,
        base_delay=0.1,
        max_delay=5.0,
        strategy=RetryStrategy.LINEAR,
        specific_exceptions=(OSError, IOError)
    ),

    "vpn_connection": RetryConfig(
        max_attempts=5,
        base_delay=2.0,
        max_delay=60.0,
        strategy=RetryStrategy.EXPONENTIAL,
        jitter=True,
        specific_exceptions=(ConnectionTimeoutError, ConnectionRefusedError)
    ),

    "security_check": RetryConfig(
        max_attempts=2,
        base_delay=0.5,
        max_delay=5.0,
        strategy=RetryStrategy.FIXED,
        specific_exceptions=(VPNSecurityError,)
    )
}

# ============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================================


def get_config(config_name: str) -> RetryConfig:
    """Получение предустановленной конфигурации"""
    return CONFIGS.get(config_name, RetryConfig())


def create_custom_config(**kwargs) -> RetryConfig:
    """Создание пользовательской конфигурации"""
    return RetryConfig(**kwargs)


def is_retryable_exception(exception: Exception, config: RetryConfig = None) -> bool:
    """Проверка, является ли исключение подходящим для повторной попытки"""
    if config is None:
        config = RetryConfig()

    if isinstance(exception, config.stop_on_exception):
        return False

    if config.condition == RetryCondition.ON_EXCEPTION:
        return True
    elif config.condition == RetryCondition.ON_SPECIFIC_EXCEPTION:
        return isinstance(exception, config.specific_exceptions)

    return False

# ============================================================================
# ЭКСПОРТ
# ============================================================================

__all__ = [
    # Основные классы
    "RetryHandler", "CircuitBreaker", "RetryConfig",

    # Перечисления
    "RetryStrategy", "RetryCondition", "CircuitState",

    # Декораторы
    "retry", "circuit_breaker",

    # Контекстные менеджеры
    "retry_context", "circuit_breaker_context",

    # Предустановленные конфигурации
    "CONFIGS", "get_config", "create_custom_config",

    # Вспомогательные функции
    "is_retryable_exception"
]
