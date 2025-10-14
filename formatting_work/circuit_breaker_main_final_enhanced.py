#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Circuit Breaker Main - Основной Circuit Breaker
"""

import logging
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict


class CircuitState(Enum):
    """Состояния Circuit Breaker"""

    CLOSED = "closed"  # Закрыт - нормальная работа
    OPEN = "open"  # Открыт - блокировка вызовов
    HALF_OPEN = "half_open"  # Полуоткрыт - тестирование

    def __str__(self) -> str:
        """Строковое представление состояния"""
        return f"CircuitState.{self.name}"

    def __repr__(self) -> str:
        """Представление для разработчика"""
        return f"CircuitState.{self.name}"

    def __bool__(self) -> bool:
        """Булево представление - True если Circuit Breaker активен"""
        return self != CircuitState.OPEN

    def is_closed(self) -> bool:
        """Проверка, что Circuit Breaker закрыт"""
        return self == CircuitState.CLOSED

    def is_open(self) -> bool:
        """Проверка, что Circuit Breaker открыт"""
        return self == CircuitState.OPEN

    def is_half_open(self) -> bool:
        """Проверка, что Circuit Breaker полуоткрыт"""
        return self == CircuitState.HALF_OPEN

    def can_accept_calls(self) -> bool:
        """Проверка, может ли Circuit Breaker принимать вызовы"""
        return self in (CircuitState.CLOSED, CircuitState.HALF_OPEN)

    def get_description(self) -> str:
        """Получение описания состояния"""
        descriptions = {
            CircuitState.CLOSED: "Закрыт - нормальная работа",
            CircuitState.OPEN: "Открыт - блокировка вызовов",
            CircuitState.HALF_OPEN: "Полуоткрыт - тестирование"
        }
        return descriptions.get(self, "Неизвестное состояние")


@dataclass
class CircuitBreakerConfig:
    """Конфигурация Circuit Breaker"""

    service_name: str
    service_type: str
    strategy: str
    failure_threshold: int
    timeout: int
    half_open_max_calls: int = 5
    success_threshold: int = 3
    adaptive: bool = True
    ml_enabled: bool = True

    def __str__(self) -> str:
        """Строковое представление конфигурации"""
        return (
            f"CircuitBreakerConfig(service='{self.service_name}', "
            f"type='{self.service_type}', "
            f"strategy='{self.strategy}', "
            f"threshold={self.failure_threshold})"
        )

    def __repr__(self) -> str:
        """Представление для разработчика"""
        return (
            f"CircuitBreakerConfig("
            f"service_name='{self.service_name}', "
            f"service_type='{self.service_type}', "
            f"strategy='{self.strategy}', "
            f"failure_threshold={self.failure_threshold}, "
            f"timeout={self.timeout}, "
            f"half_open_max_calls={self.half_open_max_calls}, "
            f"success_threshold={self.success_threshold}, "
            f"adaptive={self.adaptive}, "
            f"ml_enabled={self.ml_enabled})"
        )

    def __hash__(self) -> int:
        """Хеш для использования в качестве ключа"""
        return hash((
            self.service_name,
            self.service_type,
            self.strategy,
            self.failure_threshold,
            self.timeout
        ))

    def __bool__(self) -> bool:
        """Булево представление - True если конфигурация валидна"""
        return (
            bool(self.service_name) and
            bool(self.service_type) and
            bool(self.strategy) and
            self.failure_threshold > 0 and
            self.timeout > 0
        )

    def validate(self) -> bool:
        """Валидация конфигурации"""
        try:
            if (not self.service_name or
                    not self.service_type or
                    not self.strategy):
                return False
            if self.failure_threshold <= 0 or self.timeout <= 0:
                return False
            if self.half_open_max_calls <= 0 or self.success_threshold <= 0:
                return False
            return True
        except Exception:
            return False

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "service_name": self.service_name,
            "service_type": self.service_type,
            "strategy": self.strategy,
            "failure_threshold": self.failure_threshold,
            "timeout": self.timeout,
            "half_open_max_calls": self.half_open_max_calls,
            "success_threshold": self.success_threshold,
            "adaptive": self.adaptive,
            "ml_enabled": self.ml_enabled
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CircuitBreakerConfig":
        """Создание из словаря"""
        return cls(**data)


class CircuitBreakerMain:
    """Основной Circuit Breaker"""

    def __init__(self, config: CircuitBreakerConfig):
        self.logger = logging.getLogger(
            f"ALADDIN.CircuitBreakerMain.{config.service_name}"
        )
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.last_success_time = None
        self.half_open_calls = 0
        self.lock = threading.Lock()
        self.stats = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "circuit_opens": 0,
            "circuit_closes": 0,
        }
        self._init_ml_analyzer()

    def _init_ml_analyzer(self) -> None:
        """Инициализация ML анализатора"""
        try:
            if self.config.ml_enabled:
                # Здесь должна быть инициализация ML модели
                self.ml_analyzer = None
                self.logger.info("ML анализатор инициализирован")
            else:
                self.ml_analyzer = None
        except Exception as e:
            self.logger.error(f"Ошибка инициализации ML анализатора: {e}")
            self.ml_analyzer = None

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Выполнение функции через Circuit Breaker"""
        try:
            with self.lock:
                self.stats["total_calls"] += 1

                # Проверка состояния
                if self.state == CircuitState.OPEN:
                    if self._should_attempt_reset():
                        self.state = CircuitState.HALF_OPEN
                        self.half_open_calls = 0
                        self.logger.info(
                            f"Circuit Breaker {self.config.service_name} "
                            f"переходит в HALF_OPEN"
                        )
                    else:
                        raise Exception(
                            f"Circuit Breaker {self.config.service_name} "
                            f"is OPEN"
                        )

                elif self.state == CircuitState.HALF_OPEN:
                    if self.half_open_calls >= self.config.half_open_max_calls:
                        raise Exception(
                            f"Circuit Breaker {self.config.service_name} "
                            f"HALF_OPEN call limit exceeded"
                        )
                    self.half_open_calls += 1

                # Выполнение функции
                start_time = time.time()
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time

                # Обработка успешного выполнения
                self._on_success(execution_time)

                return result

        except Exception as e:
            # Обработка ошибки
            self._on_failure(str(e))
            raise e

    def _should_attempt_reset(self) -> bool:
        """Проверка возможности сброса Circuit Breaker"""
        try:
            if self.last_failure_time is None:
                return True

            time_since_failure = (
                datetime.now() - self.last_failure_time
            ).total_seconds()
            return time_since_failure >= self.config.timeout

        except Exception as e:
            self.logger.error(f"Ошибка проверки сброса: {e}")
            return True

    def _on_success(self, execution_time: float) -> None:
        """Обработка успешного выполнения"""
        try:
            self.success_count += 1
            self.last_success_time = datetime.now()

            # ML анализ (если включен)
            if self.ml_analyzer:
                self._ml_analyze_success(execution_time)

            # Обновление статистики
            self.stats["successful_calls"] += 1

            # Проверка перехода в CLOSED
            if self.state == CircuitState.HALF_OPEN:
                if self.success_count >= self.config.success_threshold:
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                    self.success_count = 0
                    self.stats["circuit_closes"] += 1
                    self.logger.info(
                        f"Circuit Breaker {self.config.service_name} "
                        f"переходит в CLOSED"
                    )

            elif self.state == CircuitState.CLOSED:
                # Сброс счетчика сбоев при успешном вызове
                self.failure_count = 0

        except Exception as e:
            self.logger.error(f"Ошибка обработки успеха: {e}")

    def _on_failure(self, error_message: str) -> None:
        """Обработка ошибки выполнения"""
        try:
            self.failure_count += 1
            self.last_failure_time = datetime.now()

            # ML анализ (если включен)
            if self.ml_analyzer:
                self._ml_analyze_failure(error_message)

            # Обновление статистики
            self.stats["failed_calls"] += 1

            # Проверка перехода в OPEN
            if self.failure_count >= self.config.failure_threshold:
                self.state = CircuitState.OPEN
                self.stats["circuit_opens"] += 1
                self.logger.warning(
                    f"Circuit Breaker {self.config.service_name} "
                    f"переходит в OPEN"
                )

        except Exception as e:
            self.logger.error(f"Ошибка обработки сбоя: {e}")

    def _ml_analyze_success(self, execution_time: float) -> None:
        """ML анализ успешного выполнения"""
        try:
            # Здесь должна быть логика ML анализа
            # Пока просто логируем
            self.logger.debug(
                f"ML анализ успеха: время выполнения {execution_time:.3f}s"
            )

        except Exception as e:
            self.logger.error(f"Ошибка ML анализа успеха: {e}")

    def _ml_analyze_failure(self, error_message: str) -> None:
        """ML анализ сбоя"""
        try:
            # Здесь должна быть логика ML анализа
            # Пока просто логируем
            self.logger.debug(f"ML анализ сбоя: {error_message}")

        except Exception as e:
            self.logger.error(f"Ошибка ML анализа сбоя: {e}")

    def get_state(self) -> Dict[str, Any]:
        """Получение текущего состояния"""
        try:
            return {
                "service_name": self.config.service_name,
                "state": self.state.value,
                "failure_count": self.failure_count,
                "success_count": self.success_count,
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
                "half_open_calls": self.half_open_calls,
                "stats": self.stats,
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения состояния: {e}")
            return {"error": str(e)}

    def reset(self) -> None:
        """Сброс Circuit Breaker"""
        try:
            with self.lock:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                self.half_open_calls = 0
                self.last_failure_time = None
                self.last_success_time = None

            self.logger.info(
                f"Circuit Breaker {self.config.service_name} сброшен"
            )

        except Exception as e:
            self.logger.error(f"Ошибка сброса Circuit Breaker: {e}")

    def update_config(self, new_config: CircuitBreakerConfig) -> None:
        """Обновление конфигурации"""
        try:
            with self.lock:
                self.config = new_config

            self.logger.info(
                f"Конфигурация Circuit Breaker "
                f"{self.config.service_name} обновлена"
            )

        except Exception as e:
            self.logger.error(f"Ошибка обновления конфигурации: {e}")

    async def get_status(self) -> Dict[str, Any]:
        """Получение статуса Circuit Breaker"""
        try:
            return {
                "service_name": self.config.service_name,
                "state": self.state.value,
                "stats": self.stats,
                "config": {
                    "failure_threshold": self.config.failure_threshold,
                    "timeout": self.config.timeout,
                    "adaptive": self.config.adaptive,
                    "ml_enabled": self.config.ml_enabled,
                },
                "status": "active",
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения статуса: {e}")
            return {"status": "error", "error": str(e)}

    def cleanup(self) -> None:
        """Очистка ресурсов"""
        try:
            with self.lock:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                self.half_open_calls = 0
                self.last_failure_time = None
                self.last_success_time = None
                self.stats = {
                    "total_calls": 0,
                    "successful_calls": 0,
                    "failed_calls": 0,
                    "circuit_opens": 0,
                    "circuit_closes": 0,
                }
        except Exception as e:
            self.logger.error(f"Ошибка очистки: {e}")

    def __str__(self) -> str:
        """Строковое представление Circuit Breaker"""
        return (
            f"CircuitBreakerMain(service='{self.config.service_name}', "
            f"state={self.state.value}, "
            f"failures={self.failure_count}, "
            f"successes={self.success_count})"
        )

    def __repr__(self) -> str:
        """Представление для разработчика"""
        return (
            f"CircuitBreakerMain(config={self.config!r}, "
            f"state={self.state!r}, "
            f"failure_count={self.failure_count}, "
            f"success_count={self.success_count})"
        )

    def __eq__(self, other) -> bool:
        """Сравнение Circuit Breaker объектов"""
        if not isinstance(other, CircuitBreakerMain):
            return False
        return (
            self.config == other.config and
            self.state == other.state and
            self.failure_count == other.failure_count and
            self.success_count == other.success_count
        )

    def __hash__(self) -> int:
        """Хеш для использования в качестве ключа"""
        return hash((
            self.config.service_name,
            self.config.service_type,
            self.state.value,
            self.failure_count,
            self.success_count
        ))

    def __bool__(self) -> bool:
        """Булево представление - True если Circuit Breaker активен"""
        return self.state != CircuitState.OPEN

    def __len__(self) -> int:
        """Длина - количество вызовов"""
        return self.stats["total_calls"]

    def __iter__(self):
        """Итератор по статистике"""
        return iter(self.stats.items())

    def __contains__(self, key: str) -> bool:
        """Проверка наличия ключа в статистике"""
        return key in self.stats

    def __getitem__(self, key: str):
        """Доступ к статистике как к словарю"""
        return self.stats[key]

    def __setitem__(self, key: str, value):
        """Установка значения в статистике"""
        self.stats[key] = value

    def __delitem__(self, key: str):
        """Удаление ключа из статистики"""
        del self.stats[key]

    def __enter__(self):
        """Контекстный менеджер - вход"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Контекстный менеджер - выход"""
        if exc_type is not None:
            self._on_failure(str(exc_val))
        return False


# Глобальный экземпляр
circuit_breaker_main = CircuitBreakerMain(
    CircuitBreakerConfig(
        service_name="default",
        service_type="api",
        strategy="standard",
        failure_threshold=5,
        timeout=60,
    )
)
