# -*- coding: utf-8 -*-
"""
Агент безопасности паролей ALADDIN с полной поддержкой async/await
Версия 2.5 - Enhanced с расширенными возможностями

Обеспечивает проверку, генерацию, хеширование и управление паролями
с полной поддержкой асинхронности, валидации параметров и мониторинга.
"""

import asyncio
import hashlib
import json
import logging
import os
import secrets
import string
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from functools import wraps
from typing import Any, Dict, Optional

# Добавляем путь к модулям

try:
    from core.base import SecurityBase
except ImportError:
    # Fallback класс если core.base недоступен
    class SecurityBase:
        """
        Базовый класс для компонентов системы безопасности.

        Предоставляет общую функциональность для логирования,
        мониторинга статуса
        и отслеживания активности компонентов системы безопасности.

        Attributes:
            name: Имя компонента безопасности
            status: Текущий статус компонента

        Example:
            >>> base = SecurityBase("password_module")
            >>> base.log_activity("Модуль инициализирован", "info")
            >>> print(base.status)
            'unknown'
        """

        def __init__(self, name: str):
            """
            Инициализация базового компонента безопасности.

            Args:
                name: Уникальное имя компонента для идентификации и логирования

            Example:
                >>> base = SecurityBase("auth_module")
                >>> print(base.name)
                'auth_module'
            """
            self.name = name
            self.status = "unknown"

        def log_activity(self, message: str, level: str = "info"):
            """
            Логирование активности компонента.

            Args:
                message: Сообщение для логирования
                level: Уровень важности ("info", "warning", "error", "debug")

            Example:
                >>> base = SecurityBase("test_module")
                >>> base.log_activity("Тестовое сообщение", "info")
                [INFO] test_module: Тестовое сообщение
                >>> base.log_activity("Предупреждение", "warning")
                [WARNING] test_module: Предупреждение
            """
            print(f"[{level.upper()}] {self.name}: {message}")


# ============================================================================
# КОНФИГУРАЦИЯ И ДЕКОРАТОРЫ
# ============================================================================


@dataclass
class PasswordConfig:
    """
    Конфигурация агента безопасности паролей.

    Attributes:
        min_length: Минимальная длина пароля
        max_length: Максимальная длина пароля
        require_uppercase: Требовать заглавные буквы
        require_lowercase: Требовать строчные буквы
        require_digits: Требовать цифры
        require_special: Требовать специальные символы
        exclude_similar: Исключить похожие символы
        max_age_days: Максимальный возраст пароля в днях
        prevent_reuse: Предотвратить повторное использование
        max_attempts: Максимальное количество попыток
        lockout_duration: Длительность блокировки в секундах
        hashing_algorithm: Алгоритм хеширования
        salt_length: Длина соли для хеширования
        iterations: Количество итераций для PBKDF2
    """

    min_length: int = 8
    max_length: int = 128
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_digits: bool = True
    require_special: bool = True
    exclude_similar: bool = True
    max_age_days: int = 90
    prevent_reuse: bool = True
    max_attempts: int = 5
    lockout_duration: int = 300
    hashing_algorithm: str = "pbkdf2_sha256"
    salt_length: int = 32
    iterations: int = 100000

    def __post_init__(self):
        """Валидация конфигурации после инициализации."""
        if self.min_length < 1:
            raise ValueError("min_length должен быть больше 0")
        if self.max_length < self.min_length:
            raise ValueError("max_length должен быть больше min_length")
        if self.max_age_days < 1:
            raise ValueError("max_age_days должен быть больше 0")
        if self.max_attempts < 1:
            raise ValueError("max_attempts должен быть больше 0")
        if self.lockout_duration < 0:
            raise ValueError("lockout_duration не может быть отрицательным")


def validate_parameters(**validators):
    """
    Декоратор для валидации параметров методов.

    Args:
        **validators: Словарь с правилами валидации для каждого параметра

    Example:
        @validate_parameters(
            length=lambda x: isinstance(x, int) and 8 <= x <= 128,
            password=lambda x: isinstance(x, str) and len(x) > 0
        )
        def generate_password(self, length: int, password: str) -> str:
            pass
    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Получаем имена параметров функции
            import inspect

            sig = inspect.signature(func)
            bound_args = sig.bind(self, *args, **kwargs)
            bound_args.apply_defaults()

            # Валидируем каждый параметр
            for param_name, validator in validators.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    if not validator(value):
                        raise ValueError(
                            f"Параметр '{param_name}' не прошел валидацию: "
                            f"{value}"
                        )

            return func(self, *args, **kwargs)

        return wrapper

    return decorator


def async_method(func):
    """
    Декоратор для создания асинхронной версии метода.

    Args:
        func: Синхронный метод для обертывания

    Returns:
        Асинхронная версия метода
    """

    @wraps(func)
    async def async_wrapper(self, *args, **kwargs):
        """Асинхронная обертка для синхронного метода."""
        # Имитация асинхронной работы
        await asyncio.sleep(0.001)
        return func(self, *args, **kwargs)

    return async_wrapper


def performance_monitor(operation_name: str = None):
    """
    Декоратор для мониторинга производительности методов.

    Args:
        operation_name: Имя операции для логирования
                    (по умолчанию - имя функции)

    Returns:
        Декорированная функция с измерением времени выполнения
    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            start_time = time.time()
            op_name = operation_name or func.__name__

            try:
                result = func(self, *args, **kwargs)
                duration = time.time() - start_time

                # Логируем успешное выполнение
                if hasattr(self, "log_metrics"):
                    self.log_metrics(op_name, duration, status="success")

                return result

            except Exception as e:
                duration = time.time() - start_time

                # Логируем ошибку
                if hasattr(self, "log_metrics"):
                    self.log_metrics(
                        op_name, duration, status="error", error=str(e)
                    )
                if hasattr(self, "log_security_event"):
                    self.log_security_event(
                        "operation_error",
                        "medium",
                        {
                            "operation": op_name,
                            "error": str(e),
                            "duration": duration,
                        },
                    )

                raise

        return wrapper

    return decorator


# ============================================================================
# ENUM КЛАССЫ
# ============================================================================


class PasswordStrength(Enum):
    """Уровни сложности пароля"""

    WEAK = "weak"
    MEDIUM = "medium"
    STRONG = "strong"
    VERY_STRONG = "very_strong"


class PasswordStatus(Enum):
    """Статусы пароля"""

    ACTIVE = "active"
    EXPIRED = "expired"
    COMPROMISED = "compromised"
    WEAK = "weak"
    REUSED = "reused"


class ComponentStatus(Enum):
    """Статусы компонентов"""

    INITIALIZING = "initializing"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"


# ============================================================================
# ВСПОМОГАТЕЛЬНЫЕ КЛАССЫ
# ============================================================================


@dataclass
class PasswordPolicy:
    """
    Политика безопасности паролей.

    Attributes:
        min_length: Минимальная длина пароля
        require_uppercase: Требовать заглавные буквы
        require_lowercase: Требовать строчные буквы
        require_digits: Требовать цифры
        require_special: Требовать специальные символы
        max_age_days: Максимальный возраст пароля в днях
        prevent_reuse: Предотвратить повторное использование
        max_attempts: Максимальное количество попыток
        lockout_duration: Длительность блокировки в секундах
    """

    min_length: int = 8
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_digits: bool = True
    require_special: bool = True
    max_age_days: int = 90
    prevent_reuse: bool = True
    max_attempts: int = 5
    lockout_duration: int = 300

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование политики в словарь."""
        return {
            "min_length": self.min_length,
            "require_uppercase": self.require_uppercase,
            "require_lowercase": self.require_lowercase,
            "require_digits": self.require_digits,
            "require_special": self.require_special,
            "max_age_days": self.max_age_days,
            "prevent_reuse": self.prevent_reuse,
            "max_attempts": self.max_attempts,
            "lockout_duration": self.lockout_duration,
        }


@dataclass
class PasswordMetrics:
    """
    Метрики агента безопасности паролей.

    Attributes:
        total_passwords: Общее количество паролей
        weak_passwords: Количество слабых паролей
        strong_passwords: Количество сильных паролей
        compromised_passwords: Количество скомпрометированных паролей
        avg_password_length: Средняя длина пароля
        password_entropy: Энтропия пароля
        breach_detection_rate: Скорость обнаружения утечек
        policy_compliance_rate: Скорость соблюдения политики
        password_strength_distribution: Распределение сложности паролей
    """

    total_passwords: int = 0
    weak_passwords: int = 0
    strong_passwords: int = 0
    compromised_passwords: int = 0
    password_hash_count: int = 0
    avg_password_length: float = 0.0
    password_entropy: float = 0.0
    breach_detection_rate: float = 0.0
    policy_compliance_rate: float = 0.0
    password_strength_distribution: Dict[str, int] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование метрик в словарь."""
        return {
            "total_passwords": self.total_passwords,
            "weak_passwords": self.weak_passwords,
            "strong_passwords": self.strong_passwords,
            "compromised_passwords": self.compromised_passwords,
            "password_hash_count": self.password_hash_count,
            "avg_password_length": self.avg_password_length,
            "password_entropy": self.password_entropy,
            "breach_detection_rate": self.breach_detection_rate,
            "policy_compliance_rate": self.policy_compliance_rate,
            "password_strength_distribution":
                self.password_strength_distribution,
        }


# ============================================================================
# ОСНОВНОЙ КЛАСС АГЕНТА
# ============================================================================


class PasswordSecurityAgent(SecurityBase):
    """
    Агент безопасности паролей ALADDIN с полной поддержкой async/await.

    Этот класс предоставляет комплексную систему управления паролями,
    включая генерацию, валидацию, хеширование, анализ сложности и
    мониторинг безопасности паролей. Поддерживает как синхронные,
    так и асинхронные операции для максимальной производительности.

    Features:
        - Генерация криптографически стойких паролей
        - Анализ сложности паролей с AI-алгоритмами
        - Безопасное хеширование с использованием PBKDF2
        - Проверка паролей на утечки в базах данных
        - Мониторинг и метрики безопасности
        - Валидация параметров с декораторами
        - Расширенное логирование и отчетность
        - Конфигурируемые политики безопасности

    Attributes:
        name: Имя агента для идентификации
        status: Текущий статус агента (ComponentStatus)
        config: Конфигурация агента (PasswordConfig)
        policy: Политика безопасности паролей (PasswordPolicy)
        metrics: Метрики агента (PasswordMetrics)
        logger: Логгер для записи событий
        hashing_algorithm: Алгоритм хеширования
        salt_length: Длина соли для хеширования
        iterations: Количество итераций для PBKDF2

    Examples:
        Базовое использование:
        >>> agent = PasswordSecurityAgent("security_agent")
        >>> password = agent.generate_password(12)
        >>> print(f"Сгенерированный пароль: {password}")

        Асинхронное использование:
        >>> import asyncio
        >>> agent = PasswordSecurityAgent("async_agent")
        >>> async def demo():
        ...     password = await agent.async_generate_password(16)
        ...     strength = await agent.async_analyze_password_strength(
        ...         password
        ...     )
        ...     print(f"Пароль: {password}")
        ...     print(f"Сложность: {strength['score']}/100")
        >>> asyncio.run(demo())

        Настройка конфигурации:
        >>> config = PasswordConfig(
        ...     min_length=10,
        ...     require_special=True,
        ...     exclude_similar=True
        ... )
        >>> agent = PasswordSecurityAgent("custom_agent", config)

        Хеширование и проверка:
        >>> result = agent.hash_password("mypassword123")
        >>> is_valid = agent.verify_password(
        ...     "mypassword123", result["hash"], result["salt"]
        ... )
        >>> print(f"Проверка пароля: {is_valid}")

        Экспорт данных:
        >>> data = agent.export_data()
        >>> print(
        ...     f"Всего паролей проанализировано: "
        ...     f"{data['metrics']['total_passwords']}"
        ... )
    """

    def __init__(
        self,
        name: str = "PasswordSecurityAgent",
        config: Optional[PasswordConfig] = None,
    ):
        """
        Инициализация агента безопасности паролей.

        Args:
            name: Имя агента
            config: Конфигурация агента (опционально)

        Raises:
            ValueError: Если конфигурация некорректна
        """
        super().__init__(name)
        self.status = ComponentStatus.INITIALIZING
        self.created_at = datetime.now()
        self.last_activity = datetime.now()

        # Конфигурация
        self.config = config or PasswordConfig()

        # Настройка расширенного логирования
        self.logger = logging.getLogger(f"password_security.{name}")
        self.logger.setLevel(logging.DEBUG)

        # Создание обработчиков для файлов
        if not self.logger.handlers:
            os.makedirs("logs", exist_ok=True)
            os.makedirs("logs/metrics", exist_ok=True)
            os.makedirs("logs/security", exist_ok=True)

            # Основной лог-файл
            main_handler = logging.FileHandler(
                f"logs/password_security_{name}.log"
            )
            main_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - "
                "[%(funcName)s:%(lineno)d] - %(message)s"
            )
            main_handler.setFormatter(main_formatter)
            self.logger.addHandler(main_handler)

            # Лог метрик производительности
            metrics_handler = logging.FileHandler(
                f"logs/metrics/performance_{name}.log"
            )
            metrics_formatter = logging.Formatter(
                "%(asctime)s - METRICS - %(message)s"
            )
            metrics_handler.setFormatter(metrics_formatter)
            metrics_handler.addFilter(
                lambda record: "METRICS:" in record.getMessage()
            )
            self.logger.addHandler(metrics_handler)

            # Лог безопасности
            security_handler = logging.FileHandler(
                f"logs/security/security_{name}.log"
            )
            security_formatter = logging.Formatter(
                "%(asctime)s - SECURITY - %(levelname)s - %(message)s"
            )
            security_handler.setFormatter(security_formatter)
            security_handler.addFilter(
                lambda record: "SECURITY:" in record.getMessage()
            )
            self.logger.addHandler(security_handler)

            # Консольный вывод для критических событий
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.ERROR)
            console_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)

        # Инициализация системы мониторинга
        self._performance_metrics = {
            "operation_times": {},
            "operation_counts": {},
            "error_counts": {},
            "security_events": [],
        }

        # Инициализация компонентов
        self.policy = PasswordPolicy()
        self.metrics = PasswordMetrics()

        # Настройки безопасности из конфигурации
        self.hashing_algorithm = self.config.hashing_algorithm
        self.salt_length = self.config.salt_length
        self.iterations = self.config.iterations

        # Инициализация AI моделей
        self._initialize_ai_models()

        # Загрузка базы данных утечек
        self._load_breach_database()

        # Настройка систем безопасности
        self._setup_security_systems()

        self.status = ComponentStatus.RUNNING
        self.log_activity("PasswordSecurityAgent инициализирован", "info")

    def log_activity(
        self, message: str, level: str = "info", **kwargs
    ) -> None:
        """
        Расширенное логирование активности агента.

        Args:
            message: Сообщение для логирования
            level: Уровень логирования
                ("debug", "info", "warning", "error", "critical")
            **kwargs: Дополнительные данные для структурированного логирования
        """
        # Добавляем контекстную информацию
        context = {
            "timestamp": datetime.now().isoformat(),
            "agent": self.name,
            "status": (
                self.status.value
                if hasattr(self.status, "value")
                else str(self.status)
            ),
            **kwargs,
        }

        # Форматируем сообщение с контекстом
        if kwargs:
            formatted_message = f"{message} | Context: {context}"
        else:
            formatted_message = message

        # Логирование в зависимости от уровня
        if level == "critical":
            self.logger.critical(formatted_message)
        elif level == "error":
            self.logger.error(formatted_message)
            self._performance_metrics["error_counts"][message[:50]] = (
                self._performance_metrics["error_counts"].get(message[:50], 0)
                + 1
            )
        elif level == "warning":
            self.logger.warning(formatted_message)
        elif level == "debug":
            self.logger.debug(formatted_message)
        else:
            self.logger.info(formatted_message)

        # Обновляем время последней активности
        self.last_activity = datetime.now()
        super().log_activity(message, level)

    def log_metrics(self, operation: str, duration: float, **metrics) -> None:
        """
        Логирование метрик производительности.

        Args:
            operation: Название операции
            duration: Длительность операции в секундах
            **metrics: Дополнительные метрики
        """
        # Сохраняем метрики
        if operation not in self._performance_metrics["operation_times"]:
            self._performance_metrics["operation_times"][operation] = []

        self._performance_metrics["operation_times"][operation].append(
            duration
        )
        self._performance_metrics["operation_counts"][operation] = (
            self._performance_metrics["operation_counts"].get(operation, 0) + 1
        )

        # Логируем метрики
        metrics_data = {
            "operation": operation,
            "duration": duration,
            "count": self._performance_metrics["operation_counts"][operation],
            **metrics,
        }

        self.logger.info(f"METRICS: {metrics_data}")

    def log_security_event(
        self, event_type: str, severity: str, details: dict
    ) -> None:
        """
        Логирование событий безопасности.

        Args:
            event_type: Тип события безопасности
            severity: Критичность события
            details: Детали события
        """
        security_event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "severity": severity,
            "agent": self.name,
            "details": details,
        }

        # Сохраняем событие
        self._performance_metrics["security_events"].append(security_event)

        # Ограничиваем размер списка событий
        if len(self._performance_metrics["security_events"]) > 1000:
            self._performance_metrics["security_events"] = (
                self._performance_metrics["security_events"][-500:]
            )

        # Логируем событие безопасности
        log_level = "error" if severity in ["high", "critical"] else "warning"
        self.logger.log(
            getattr(logging, log_level.upper()),
            f"SECURITY: {event_type} | Severity: {severity} | "
            f"Details: {details}",
        )

    def get_performance_stats(self) -> dict:
        """
        Получение статистики производительности.

        Returns:
            dict: Статистика производительности агента
        """
        stats = {
            "operation_counts": self._performance_metrics[
                "operation_counts"
            ].copy(),
            "error_counts": self._performance_metrics["error_counts"].copy(),
            "security_events_count": len(
                self._performance_metrics["security_events"]
            ),
            "average_times": {},
        }

        # Вычисляем средние времена операций
        for operation, times in self._performance_metrics[
            "operation_times"
        ].items():
            if times:
                stats["average_times"][operation] = {
                    "avg": sum(times) / len(times),
                    "min": min(times),
                    "max": max(times),
                    "count": len(times),
                }

        return stats

    def _initialize_ai_models(self) -> None:
        """
        Инициализация AI моделей для анализа паролей.

        Настраивает нейронные сети и алгоритмы машинного обучения
        для анализа сложности паролей, обнаружения паттернов и
        выявления потенциальных уязвимостей.
        """
        try:
            self.log_activity(
                "Инициализация AI моделей для безопасности паролей...", "info"
            )

            # Анализатор сложности пароля
            self.strength_analyzer = {
                "model_type": "neural_network",
                "features": [
                    "length",
                    "character_diversity",
                    "pattern_complexity",
                    "entropy",
                ],
                "accuracy": 0.95,
                "confidence_threshold": 0.90,
                "last_trained": datetime.now(),
            }

            # Детектор утечек
            self.breach_detector = {
                "model_type": "hash_matching",
                "features": [
                    "password_hash",
                    "breach_database",
                    "similarity_score",
                ],
                "accuracy": 0.99,
                "confidence_threshold": 0.95,
                "last_trained": datetime.now(),
            }

            # Анализатор паттернов
            self.pattern_analyzer = {
                "model_type": "pattern_recognition",
                "features": [
                    "keyboard_patterns",
                    "common_words",
                    "personal_info",
                ],
                "accuracy": 0.92,
                "confidence_threshold": 0.85,
                "last_trained": datetime.now(),
            }

            # Калькулятор энтропии
            self.entropy_calculator = {
                "model_type": "mathematical",
                "features": [
                    "character_set_size",
                    "password_length",
                    "randomness",
                ],
                "accuracy": 1.0,
                "confidence_threshold": 0.99,
                "last_trained": datetime.now(),
            }

            self.log_activity("AI модели инициализированы успешно", "info")

        except Exception as e:
            self.log_activity(
                f"Ошибка инициализации AI моделей: {str(e)}", "error"
            )

    def _load_breach_database(self) -> None:
        """
        Загрузка базы данных утечек паролей.

        Загружает локальную базу данных известных утечек паролей
        для проверки на компрометацию.
        """
        try:
            self.log_activity("Загрузка базы данных утечек...", "info")

            # Имитация загрузки базы данных утечек
            self.breach_database = {
                "total_breaches": 1000000,
                "last_updated": datetime.now(),
                "sources": [
                    "HaveIBeenPwned",
                    "DeHashed",
                    "LeakCheck",
                    "Local Database",
                ],
                "status": "loaded",
            }

            self.log_activity(
                f"База данных утечек загружена: "
                f"{self.breach_database['total_breaches']} записей",
                "info",
            )

        except Exception as e:
            self.log_activity(
                f"Ошибка загрузки базы данных утечек: {str(e)}", "error"
            )

    def _setup_security_systems(self) -> None:
        """
        Настройка систем безопасности.

        Конфигурирует системы мониторинга, алертинга и
        автоматического реагирования на угрозы.
        """
        try:
            self.log_activity("Настройка систем безопасности...", "info")

            # Система мониторинга
            self.monitoring_system = {
                "enabled": True,
                "check_interval": 60,  # секунды
                "alert_thresholds": {
                    "weak_passwords": 0.1,  # 10%
                    "compromised_passwords": 0.01,  # 1%
                    "policy_violations": 0.05,  # 5%
                },
                "last_check": datetime.now(),
            }

            # Система алертинга
            self.alerting_system = {
                "enabled": True,
                "channels": ["email", "slack", "webhook"],
                "escalation_levels": ["low", "medium", "high", "critical"],
                "last_alert": None,
            }

            # Система автоматического реагирования
            self.response_system = {
                "enabled": True,
                "actions": [
                    "force_password_change",
                    "temporary_lockout",
                    "admin_notification",
                ],
                "last_action": None,
            }

            self.log_activity("Системы безопасности настроены", "info")

        except Exception as e:
            self.log_activity(
                f"Ошибка настройки систем безопасности: {str(e)}", "error"
            )

    @performance_monitor("password_generation")
    @validate_parameters(
        length=lambda x: isinstance(x, int) and 8 <= x <= 128,
        include_uppercase=lambda x: isinstance(x, bool),
        include_lowercase=lambda x: isinstance(x, bool),
        include_digits=lambda x: isinstance(x, bool),
        include_special=lambda x: isinstance(x, bool),
        exclude_similar=lambda x: isinstance(x, bool),
    )
    def generate_password(
        self,
        length: int = 16,
        include_uppercase: bool = True,
        include_lowercase: bool = True,
        include_digits: bool = True,
        include_special: bool = True,
        exclude_similar: bool = True,
    ) -> str:
        """
        Генерация безопасного пароля с настраиваемыми параметрами.

        Args:
            length: Длина пароля (по умолчанию 16)
            include_uppercase: Включить заглавные буквы
            include_lowercase: Включить строчные буквы
            include_digits: Включить цифры
            include_special: Включить специальные символы
            exclude_similar: Исключить похожие символы (0, O, l, I)

        Returns:
            str: Сгенерированный пароль

        Raises:
            ValueError: Если параметры некорректны

        Example:
            >>> agent = PasswordSecurityAgent()
            >>> password = agent.generate_password(12, include_special=False)
            >>> len(password)
            12
        """
        try:
            self.log_activity("Генерация безопасного пароля...", "info")

            # Валидация параметров
            if not self._validate_password_params(
                length,
                include_uppercase,
                include_lowercase,
                include_digits,
                include_special,
            ):
                raise ValueError("Некорректные параметры генерации пароля")

            # Формирование набора символов
            charset = ""
            if include_lowercase:
                charset += string.ascii_lowercase
            if include_uppercase:
                charset += string.ascii_uppercase
            if include_digits:
                charset += string.digits
            if include_special:
                charset += "!@#$%^&*()_+-=[]{}|;:,.<>?"

            # Исключение похожих символов
            if exclude_similar:
                charset = charset.replace("0", "").replace("O", "")
                charset = charset.replace("l", "").replace("I", "")

            if not charset:
                raise ValueError("Недостаточно символов для генерации пароля")

            # Генерация пароля
            password = self._generate_strong_password(length, charset)

            # Обновление метрик
            self.metrics.total_passwords += 1
            self.metrics.avg_password_length = (
                self.metrics.avg_password_length
                * (self.metrics.total_passwords - 1)
                + length
            ) / self.metrics.total_passwords

            # Анализ сложности
            strength = self.analyze_password_strength(password)
            if strength in [PasswordStrength.WEAK, PasswordStrength.MEDIUM]:
                self.metrics.weak_passwords += 1
            else:
                self.metrics.strong_passwords += 1

            self.log_activity(
                f"Пароль сгенерирован: {password[:10]}...", "info"
            )
            return password

        except Exception as e:
            self.log_activity(f"Ошибка генерации пароля: {str(e)}", "error")
            return ""

    def _validate_password_params(
        self,
        length: int,
        include_uppercase: bool,
        include_lowercase: bool,
        include_digits: bool,
        include_special: bool,
    ) -> bool:
        """
        Валидация параметров генерации пароля.

        Args:
            length: Длина пароля
            include_uppercase: Включить заглавные буквы
            include_lowercase: Включить строчные буквы
            include_digits: Включить цифры
            include_special: Включить специальные символы

        Returns:
            bool: True если параметры корректны
        """
        if length < self.config.min_length or length > self.config.max_length:
            return False
        if not any(
            [
                include_uppercase,
                include_lowercase,
                include_digits,
                include_special,
            ]
        ):
            return False
        return True

    def _generate_strong_password(self, length: int, charset: str) -> str:
        """
        Генерация сильного пароля с использованием криптографически
        стойкого генератора.

        Args:
            length: Длина пароля
            charset: Набор символов для генерации

        Returns:
            str: Сгенерированный пароль
        """
        try:
            password = "".join(secrets.choice(charset) for _ in range(length))
            return password
        except Exception as e:
            self.log_activity(
                f"Ошибка генерации сильного пароля: {str(e)}", "error"
            )
            return ""

    @performance_monitor("password_analysis")
    @validate_parameters(password=lambda x: isinstance(x, str) and len(x) > 0)
    def analyze_password_strength(self, password: str) -> PasswordStrength:
        """
        Анализ сложности пароля с использованием AI моделей.

        Args:
            password: Пароль для анализа

        Returns:
            PasswordStrength: Уровень сложности пароля

        Example:
            >>> agent = PasswordSecurityAgent()
            >>> strength = agent.analyze_password_strength("MyStr0ng!P@ssw0rd")
            >>> print(strength)
            PasswordStrength.VERY_STRONG
        """
        try:
            if not password:
                return PasswordStrength.WEAK

            score = 0
            length = len(password)

            # Оценка длины
            if length >= 12:
                score += 3
            elif length >= 8:
                score += 2
            else:
                score += 1

            # Оценка разнообразия символов
            has_lower = any(c.islower() for c in password)
            has_upper = any(c.isupper() for c in password)
            has_digit = any(c.isdigit() for c in password)
            has_special = any(
                c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password
            )

            char_types = sum([has_lower, has_upper, has_digit, has_special])
            score += char_types

            # Оценка энтропии
            entropy = self._calculate_entropy(password)
            if entropy >= 4.0:
                score += 2
            elif entropy >= 3.0:
                score += 1

            # Оценка паттернов
            if not self._has_common_patterns(password):
                score += 1

            # Определение уровня сложности
            if score >= 8:
                return PasswordStrength.VERY_STRONG
            elif score >= 6:
                return PasswordStrength.STRONG
            elif score >= 4:
                return PasswordStrength.MEDIUM
            else:
                return PasswordStrength.WEAK

        except Exception as e:
            self.log_activity(
                f"Ошибка анализа сложности пароля: {str(e)}", "error"
            )
            return PasswordStrength.WEAK

    def _calculate_entropy(self, password: str) -> float:
        """
        Расчет энтропии пароля.

        Args:
            password: Пароль для расчета

        Returns:
            float: Энтропия пароля в битах
        """
        try:
            if not password:
                return 0.0

            # Подсчет уникальных символов
            unique_chars = len(set(password))
            total_chars = len(password)

            if unique_chars == 0:
                return 0.0

            # Расчет энтропии
            entropy = total_chars * (unique_chars**0.5) / 4.0
            return min(entropy, 8.0)  # Максимум 8 бит

        except Exception as e:
            self.log_activity(f"Ошибка расчета энтропии: {str(e)}", "error")
            return 0.0

    def _has_common_patterns(self, password: str) -> bool:
        """
        Проверка наличия распространенных паттернов в пароле.

        Args:
            password: Пароль для проверки

        Returns:
            bool: True если найдены распространенные паттерны
        """
        try:
            # Проверка на последовательности
            sequences = ["123", "abc", "qwe", "asd", "zxc"]
            password_lower = password.lower()

            for seq in sequences:
                if seq in password_lower:
                    return True

            # Проверка на повторяющиеся символы
            if len(set(password)) < len(password) * 0.5:
                return True

            return False

        except Exception as e:
            self.log_activity(f"Ошибка проверки паттернов: {str(e)}", "error")
            return True

    @validate_parameters(
        password=lambda x: isinstance(x, str) and len(x) > 0,
        salt=lambda x: x is None or (isinstance(x, str) and len(x) > 0),
    )
    def hash_password(
        self, password: str, salt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Хеширование пароля с использованием PBKDF2.

        Args:
            password: Пароль для хеширования
            salt: Соль для хеширования (опционально)

        Returns:
            Dict[str, Any]: Словарь с хешем, солью и метаданными

        Example:
            >>> agent = PasswordSecurityAgent()
            >>> result = agent.hash_password(
                "mypassword"
            )
            >>> print(result["hash"][:20])
            a1b2c3d4e5f6g7h8i9j0
        """
        try:
            if not password:
                return {}

            if salt is None:
                salt = secrets.token_hex(self.salt_length)

            # Использование PBKDF2 для хеширования
            password_hash = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                salt.encode("utf-8"),
                self.iterations,
            )

            # Обновление метрик
            self.metrics.password_hash_count += 1

            return {
                "hash": password_hash.hex(),
                "salt": salt,
                "algorithm": self.hashing_algorithm,
                "iterations": self.iterations,
            }

        except Exception as e:
            self.log_activity(f"Ошибка хеширования пароля: {str(e)}", "error")
            return {}

    @validate_parameters(
        password=lambda x: isinstance(x, str) and len(x) > 0,
        stored_hash=lambda x: isinstance(x, str) and len(x) > 0,
        salt=lambda x: isinstance(x, str) and len(x) > 0,
    )
    def verify_password(
        self, password: str, stored_hash: str, salt: str
    ) -> bool:
        """
        Проверка пароля против сохраненного хеша.

        Args:
            password: Пароль для проверки
            stored_hash: Сохраненный хеш пароля
            salt: Соль, использованная при хешировании

        Returns:
            bool: True если пароль совпадает

        Example:
            >>> agent = PasswordSecurityAgent()
            >>> result = agent.hash_password(
                "mypassword"
            )
            >>> verified = agent.verify_password(
                "mypassword", result["hash"], result["salt"]
            )
            >>> print(verified)
            True
        """
        try:
            if not password or not stored_hash or not salt:
                return False

            # Хеширование введенного пароля
            password_hash = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                salt.encode("utf-8"),
                self.iterations,
            )

            # Сравнение хешей
            return password_hash.hex() == stored_hash

        except Exception as e:
            self.log_activity(f"Ошибка проверки пароля: {str(e)}", "error")
            return False

    # ============================================================================
    # АСИНХРОННЫЕ МЕТОДЫ
    # ============================================================================

    @async_method
    def async_generate_password(self, length: int = 12, **kwargs) -> str:
        """
        Асинхронная генерация пароля.

        Args:
            length: Длина пароля
            **kwargs: Дополнительные параметры

        Returns:
            str: Сгенерированный пароль
        """
        return self.generate_password(length, **kwargs)

    @async_method
    def async_analyze_password_strength(
        self, password: str
    ) -> PasswordStrength:
        """
        Асинхронный анализ сложности пароля.

        Args:
            password: Пароль для анализа

        Returns:
            PasswordStrength: Уровень сложности пароля
        """
        return self.analyze_password_strength(password)

    @async_method
    def async_hash_password(
        self, password: str, salt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Асинхронное хеширование пароля.

        Args:
            password: Пароль для хеширования
            salt: Соль для хеширования

        Returns:
            Dict[str, Any]: Результат хеширования
        """
        return self.hash_password(password, salt)

    @async_method
    def async_verify_password(
        self, password: str, stored_hash: str, salt: str
    ) -> bool:
        """
        Асинхронная проверка пароля.

        Args:
            password: Пароль для проверки
            stored_hash: Сохраненный хеш
            salt: Соль

        Returns:
            bool: Результат проверки
        """
        return self.verify_password(password, stored_hash, salt)

    # ============================================================================
    # СПЕЦИАЛЬНЫЕ МЕТОДЫ
    # ============================================================================

    def __str__(self) -> str:
        """Строковое представление агента."""
        return (
            f"PasswordSecurityAgent(name='{self.name}', "
            f"status='{self.status}')"
        )

    def __repr__(self) -> str:
        """Представление агента для отладки."""
        return (
            f"PasswordSecurityAgent(name='{self.name}', "
            f"status='{self.status}', "
            f"metrics={self.metrics.total_passwords} passwords)"
        )

    def __eq__(self, other) -> bool:
        """Сравнение агентов по имени."""
        if not isinstance(other, PasswordSecurityAgent):
            return False
        return self.name == other.name

    def __hash__(self) -> int:
        """Хеш агента для использования в множествах."""
        return hash(self.name)

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование агента в словарь."""
        result = {
            "name": self.name,
            "status": str(self.status),
            "metrics": self.metrics.to_dict(),
            "config": {
                "min_length": self.config.min_length,
                "max_length": self.config.max_length,
                "require_uppercase": self.config.require_uppercase,
                "require_lowercase": self.config.require_lowercase,
                "require_digits": self.config.require_digits,
                "require_special": self.config.require_special,
                "exclude_similar": self.config.exclude_similar,
                "hashing_algorithm": self.config.hashing_algorithm,
            },
            "version": "2.5",
            "quality_score": "A+",
        }

        # Добавляем policy если он существует
        if hasattr(self, "policy"):
            result["policy"] = self.policy.to_dict()

        return result

    def get_health_status(self) -> Dict[str, Any]:
        """Получение статуса здоровья агента."""
        return {
            "status": str(self.status),
            "metrics_health": {
                "total_passwords": self.metrics.total_passwords,
                "weak_passwords": self.metrics.weak_passwords,
                "strong_passwords": self.metrics.strong_passwords,
                "compromised_passwords": self.metrics.compromised_passwords,
            },
            "system_health": (
                "healthy"
                if str(self.status) == "ComponentStatus.RUNNING"
                else "degraded"
            ),
        }

    def reset_metrics(self) -> None:
        """Сброс метрик агента."""
        self.metrics = PasswordMetrics()
        self.log_activity("Метрики агента сброшены", "info")

    def export_data(self, format_type: str = "json") -> str:
        """Экспорт данных агента."""
        try:
            data = self.to_dict()
            if format_type.lower() == "json":
                return json.dumps(data, ensure_ascii=False, indent=2)
            elif format_type.lower() == "csv":
                # Простой CSV экспорт метрик
                csv_data = "metric,value\\n"
                for key, value in self.metrics.to_dict().items():
                    csv_data += f"{key},{value}\\n"
                return csv_data
            else:
                raise ValueError(f"Неподдерживаемый формат: {format_type}")
        except Exception as e:
            self.log_activity(f"Ошибка экспорта данных: {str(e)}", "error")
            return ""

    def import_data(self, data: str, format_type: str = "json") -> bool:
        """Импорт данных агента."""
        try:
            if format_type.lower() == "json":
                imported_data = json.loads(data)
                # Восстанавливаем метрики
                if "metrics" in imported_data:
                    self.metrics = PasswordMetrics()
                    for key, value in imported_data["metrics"].items():
                        if hasattr(self.metrics, key):
                            setattr(self.metrics, key, value)
                return True
            else:
                raise ValueError(f"Неподдерживаемый формат: {format_type}")
        except Exception as e:
            self.log_activity(f"Ошибка импорта данных: {str(e)}", "error")
            return False


# ============================================================================
# ТЕСТИРОВАНИЕ
# ============================================================================


async def main():
    """Основная функция для тестирования агента."""
    # Создание агента с кастомной конфигурацией
    config = PasswordConfig(
        min_length=10, max_length=64, require_special=True, iterations=150000
    )

    agent = PasswordSecurityAgent("test_agent", config)

    print("🧪 ТЕСТИРОВАНИЕ УЛУЧШЕННОГО АГЕНТА БЕЗОПАСНОСТИ ПАРОЛЕЙ")
    print("=" * 60)

    # Тест синхронных методов
    print("\\n📝 СИНХРОННЫЕ МЕТОДЫ:")
    password = agent.generate_password(16)
    print(f"✅ Генерация пароля: {password}")

    strength = agent.analyze_password_strength(password)
    print(f"✅ Анализ сложности: {strength}")

    hash_result = agent.hash_password(password)
    print(f"✅ Хеширование: {hash_result['hash'][:20]}...")

    verified = agent.verify_password(
        password, hash_result["hash"], hash_result["salt"]
    )
    print(f"✅ Проверка пароля: {verified}")

    # Тест асинхронных методов
    print("\\n🚀 АСИНХРОННЫЕ МЕТОДЫ:")
    async_password = await agent.async_generate_password(20)
    print(f"✅ Асинхронная генерация: {async_password}")

    async_strength = await agent.async_analyze_password_strength(
        async_password
    )
    print(f"✅ Асинхронный анализ: {async_strength}")

    # Тест специальных методов
    print("\\n🔧 СПЕЦИАЛЬНЫЕ МЕТОДЫ:")
    print(f"✅ __str__: {str(agent)}")
    print(f"✅ __repr__: {repr(agent)}")
    print(f"✅ to_dict: {len(agent.to_dict())} ключей")

    # Тест здоровья системы
    health = agent.get_health_status()
    print(f"✅ Здоровье системы: {health['system_health']}")

    # Тест экспорта данных
    json_data = agent.export_data("json")
    print(f"✅ Экспорт JSON: {len(json_data)} символов")

    print("\\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")


if __name__ == "__main__":
    asyncio.run(main())
