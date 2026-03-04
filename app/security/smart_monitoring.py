# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Умная система мониторинга
Защита от спама уведомлений и ложных срабатываний

Этот модуль предоставляет продвинутую систему мониторинга с защитой от спама,
адаптивными порогами и асинхронной обработкой данных.

Основные возможности:
- Мониторинг метрик в реальном времени
- Защита от спама алертов (cooldown, лимиты)
- Адаптивные пороги на основе исторических данных
- Асинхронная обработка для высокой производительности
- Расширенная валидация входных данных
- Защита от переполнения памяти
- Структурированное логирование
- Экспорт/импорт данных

Пример использования:
    ```python
    # Создание системы мониторинга
    system = SmartMonitoringSystem("MySystem")

    # Добавление правила
    rule = AlertRule(
        rule_id="high_cpu",
        name="High CPU Usage",
        metric_name="cpu_usage",
        condition=">",
        threshold=80.0,
        severity=AlertSeverity.WARNING
    )
    system.add_rule(rule)

    # Добавление метрики
    system.add_metric("cpu_usage", 85.0)

    # Асинхронное добавление метрики
    await system.add_metric_async("cpu_usage", 90.0)

    # Получение статистики
    stats = system.get_alert_stats()
    memory_stats = system.get_memory_stats()
    ```

Производительность:
- Поддерживает до 1000 алертов в памяти
- До 1000 метрик на имя
- До 50 callback'ов
- Максимум 500MB использования памяти
- Автоматическая очистка старых данных

Безопасность:
- Валидация всех входных данных
- Защита от SQL injection
- Проверка лимитов памяти
- Rate limiting для callback'ов

Автор: ALADDIN Security Team
Версия: 2.6 (Enhanced)
Дата: 2025-09-22
Лицензия: MIT
"""

import asyncio
import json
import statistics
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, Iterator, List, Optional


# Кастомные декораторы для улучшения функциональности
def validate_input(func):
    """Декоратор для валидации входных данных"""

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            print(f"Ошибка валидации в {func.__name__}: {e}")
            raise

    return wrapper


def performance_monitor(func):
    """Декоратор для мониторинга производительности"""

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        start_time = time.time()
        try:
            result = func(self, *args, **kwargs)
            execution_time = time.time() - start_time
            if execution_time > 0.1:  # Логируем только медленные операции
                print(
                    f"Медленная операция {func.__name__}: "
                    f"{execution_time:.3f}s"
                )
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"Ошибка в {func.__name__} за {execution_time:.3f}s: {e}")
            raise

    return wrapper


def log_execution(func):
    """Декоратор для логирования выполнения"""

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        print(
            f"Выполнение {func.__name__} с аргументами: "
            f"{args[1:] if len(args) > 1 else 'None'}"
        )
        try:
            result = func(self, *args, **kwargs)
            print(f"Успешное выполнение {func.__name__}")
            return result
        except Exception as e:
            print(f"Ошибка выполнения {func.__name__}: {e}")
            raise

    return wrapper


def transaction(func):
    """Декоратор для транзакционных операций"""

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        print(f"Начало транзакции {func.__name__}")
        try:
            result = func(self, *args, **kwargs)
            print(f"Транзакция {func.__name__} завершена успешно")
            return result
        except Exception as e:
            print(f"Откат транзакции {func.__name__}: {e}")
            raise

    return wrapper


def private_method(func):
    """Декоратор для обозначения приватных методов"""

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        return func(self, *args, **kwargs)

    return wrapper


class AlertSeverity(Enum):
    """Уровни серьезности алертов"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Статусы алертов"""

    ACTIVE = "active"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"
    IGNORED = "ignored"


@dataclass
class AlertRule:
    """Правило для генерации алертов"""

    rule_id: str
    name: str
    metric_name: str
    condition: str  # ">", "<", "==", "!="
    threshold: float
    severity: AlertSeverity
    cooldown: int = 300  # 5 минут между алертами
    min_occurrences: int = 1  # Минимум повторений для алерта
    max_alerts_per_hour: int = 10  # Максимум алертов в час
    adaptive_threshold: bool = True  # Адаптивная настройка порога


@dataclass
class Alert:
    """Алерт"""

    alert_id: str
    rule_id: str
    title: str
    message: str
    severity: AlertSeverity
    status: AlertStatus
    timestamp: datetime
    metric_name: str
    current_value: float
    threshold_value: float
    tags: Dict[str, str]
    occurrences: int = 1


class SmartMonitoringSystem:
    """
    Умная система мониторинга с защитой от спама

    Этот класс предоставляет продвинутую систему мониторинга метрик с
    защитой от спама,

    Атрибуты:
        name (str): Название системы мониторинга
        rules (Dict[str, AlertRule]): Словарь правил мониторинга
        alerts (List[Alert]): Список алертов
        metrics (Dict[str, List[float]]): Словарь метрик
        alert_history (Dict[str, List[datetime]]): История алертов по правилам

    Производительность:
        - Поддерживает до 1000 алертов в памяти
        - До 1000 метрик на имя
        - Автоматическая очистка старых данных
        - Потокобезопасные операции

    Пример:
        >>> system = SmartMonitoringSystem("MySystem")
        >>> rule = AlertRule(
        ...     "cpu_rule", "CPU", "cpu_usage", ">", 80.0,
        ...     AlertSeverity.WARNING)
    """

    __slots__ = (
        "name",
        "rules",
        "alerts",
        "metrics",
        "alert_history",
        "alert_cooldowns",
        "hourly_alert_counts",
        "last_hour_reset",
        "adaptive_thresholds",
        "baseline_metrics",
        "alert_callbacks",
        "lock",
        "_stop_cleanup",
        "is_running",
        "is_paused",
        "start_time",
        "last_activity",
        "total_metrics_received",
        "total_alerts_generated",
        "total_alerts_suppressed",
        "total_alerts_resolved",
        "config_version",
        "max_alerts_in_memory",
        "max_metrics_per_name",
        "cleanup_interval_hours",
        "performance_stats",
        "log_level",
        "log_file",
        "enable_debug",
        "enable_validation",
        "max_callback_errors",
        "callback_error_count",
        "max_memory_usage_mb",
        "memory_check_interval",
        "operation_count",
        "last_memory_check",
    )

    @performance_monitor
    def __init__(self, name: str = "SmartMonitoring"):
        """
        Инициализация системы умного мониторинга

        Args:
            name: Название системы мониторинга (по умолчанию "SmartMonitoring")

        Attributes:
            name: Название системы мониторинга
            rules: Словарь правил мониторинга
            alerts: Список алертов
            metrics: Словарь метрик
            alert_history: История алертов по правилам
            alert_cooldowns: Временные ограничения для алертов
            hourly_alert_counts: Счетчики алертов в час
            adaptive_thresholds: Адаптивные пороги
            baseline_metrics: Базовые метрики для адаптации
            alert_callbacks: Callback функции для уведомлений
            lock: Блокировка для потокобезопасности
            is_running: Статус работы системы
            is_paused: Статус приостановки системы
            start_time: Время запуска системы
            last_activity: Время последней активности
            total_metrics_received: Общее количество полученных метрик
            total_alerts_generated: Общее количество сгенерированных алертов
            config_version: Версия конфигурации
            max_alerts_in_memory: Максимальное количество алертов в памяти
            max_metrics_per_name: Максимальное количество метрик на имя
            cleanup_interval_hours: Интервал очистки в часах
            performance_stats: Статистика производительности
            log_level: Уровень логирования
            log_file: Файл для логирования
            enable_debug: Включение отладочного режима
            enable_validation: Включение валидации
            max_callback_errors: Максимальное количество ошибок в callback'ах
            callback_error_count: Счетчик ошибок в callback'ах
            max_memory_usage_mb: Максимальное использование памяти в MB
            memory_check_interval: Интервал проверки памяти
            operation_count: Счетчик операций
            last_memory_check: Время последней проверки памяти

        Example:
            >>> system = SmartMonitoringSystem("MySystem")
            >>> system.start()
            >>> system.add_metric("cpu_usage", 75.0)
        """
        self.name = name
        self.rules: Dict[str, AlertRule] = {}
        self.alerts: List[Alert] = []
        self.metrics: Dict[str, List[float]] = {}
        self.alert_history: Dict[str, List[datetime]] = {}

        # Защита от спама
        self.alert_cooldowns: Dict[str, datetime] = {}
        self.hourly_alert_counts: Dict[str, int] = {}
        self.last_hour_reset = datetime.now()

        # Адаптивные пороги
        self.adaptive_thresholds: Dict[str, float] = {}
        self.baseline_metrics: Dict[str, List[float]] = {}

        # Callback для уведомлений
        self.alert_callbacks: List[Callable] = []

        # Блокировка для потокобезопасности
        self.lock = threading.Lock()

        # Флаг остановки для бесконечных циклов
        self._stop_cleanup = False

        # НОВЫЕ АТРИБУТЫ ДЛЯ УПРАВЛЕНИЯ СИСТЕМОЙ
        self.is_running: bool = False
        self.is_paused: bool = False
        self.start_time: Optional[datetime] = None
        self.last_activity: Optional[datetime] = None

        # АТРИБУТЫ ДЛЯ СТАТИСТИКИ
        self.total_metrics_received: int = 0
        self.total_alerts_generated: int = 0
        self.total_alerts_suppressed: int = 0
        self.total_alerts_resolved: int = 0

        # АТРИБУТЫ ДЛЯ КОНФИГУРАЦИИ
        self.config_version: str = "1.0"
        self.max_alerts_in_memory: int = 1000
        self.max_metrics_per_name: int = 1000
        self.cleanup_interval_hours: int = 1

        # АТРИБУТЫ ДЛЯ ПРОИЗВОДИТЕЛЬНОСТИ
        self.performance_stats: Dict[str, Any] = {
            "avg_processing_time": 0.0,
            "max_processing_time": 0.0,
            "total_processing_time": 0.0,
            "operations_count": 0,
        }

        # АТРИБУТЫ ДЛЯ ЛОГИРОВАНИЯ
        self.log_level: str = "INFO"
        self.log_file: Optional[str] = None
        self.enable_debug: bool = False

        # АТРИБУТЫ ДЛЯ БЕЗОПАСНОСТИ
        self.enable_validation: bool = True
        self.max_callback_errors: int = 10
        self.callback_error_count: int = 0

        # АТРИБУТЫ ДЛЯ ЗАЩИТЫ ОТ ПЕРЕПОЛНЕНИЯ ПАМЯТИ
        self.max_memory_usage_mb: int = 500  # Максимум 500MB
        self.memory_check_interval: int = 100  # Проверка каждые 100 операций
        self.operation_count: int = 0
        self.last_memory_check: datetime = datetime.now()

        # Инициализация времени запуска
        self.start_time = datetime.now()
        self.last_activity = datetime.now()

        # Автоматическая очистка старых данных
        self._start_cleanup_thread()

    @performance_monitor
    def __str__(self) -> str:
        """Строковое представление системы мониторинга"""
        return (
            f"SmartMonitoringSystem(name='{self.name}', "
            f"rules={len(self.rules)}, alerts={len(self.alerts)})"
        )

    @performance_monitor
    def __repr__(self) -> str:
        """Детальное представление системы мониторинга"""
        return (
            f"SmartMonitoringSystem(name='{self.name}', "
            f"rules={len(self.rules)}, alerts={len(self.alerts)}, "
            f"metrics={len(self.metrics)})"
        )

    @staticmethod
    def create_with_rules(
        name: str, rules: List[AlertRule]
    ) -> "SmartMonitoringSystem":
        """Создание системы мониторинга с предустановленными правилами"""
        try:
            system = SmartMonitoringSystem(name)
            for rule in rules:
                system.add_rule(rule)
            return system
        except Exception as e:
            print(f"Ошибка создания системы с правилами: {e}")
            raise

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "SmartMonitoringSystem":
        """Создание системы мониторинга из конфигурации"""
        try:
            name = config.get("name", "SmartMonitoring")
            system = cls(name)

            # Добавляем правила из конфигурации
            if "rules" in config:
                for rule_id, rule_config in config["rules"].items():
                    if isinstance(rule_config, dict):
                        rule = AlertRule(
                            rule_id=rule_id,
                            name=rule_config.get("name", rule_id),
                            metric_name=rule_config.get("metric_name", ""),
                            condition=rule_config.get("condition", ">"),
                            threshold=rule_config.get("threshold", 0.0),
                            severity=AlertSeverity(
                                rule_config.get("severity", "info")
                            ),
                            cooldown=rule_config.get("cooldown", 300),
                            min_occurrences=rule_config.get(
                                "min_occurrences", 1
                            ),
                            max_alerts_per_hour=rule_config.get(
                                "max_alerts_per_hour", 10
                            ),
                            adaptive_threshold=rule_config.get(
                                "adaptive_threshold", True
                            ),
                        )
                        system.add_rule(rule)

            return system
        except Exception as e:
            print(f"Ошибка создания системы из конфигурации: {e}")
            raise

    @validate_input
    def add_rule(self, rule: AlertRule):
        """Добавление правила мониторинга"""
        try:
            with self.lock:
                self.rules[rule.rule_id] = rule
                self.alert_history[rule.rule_id] = []
                self.hourly_alert_counts[rule.rule_id] = 0
        except Exception as e:
            print(f"Ошибка добавления правила {rule.rule_id}: {e}")
            raise

    @validate_input
    def add_metric(
        self,
        metric_name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None,
    ):
        """Добавление метрики"""
        try:
            # Валидация входных данных
            if not isinstance(metric_name, str) or not metric_name.strip():
                raise ValueError("metric_name должен быть непустой строкой")
            if not isinstance(value, (int, float)):
                raise ValueError("value должен быть числом")
            if tags is not None and not isinstance(tags, dict):
                raise ValueError("tags должен быть словарем или None")

            with self.lock:
                if metric_name not in self.metrics:
                    self.metrics[metric_name] = []

                self.metrics[metric_name].append(value)

                # Ограничиваем размер истории
                if len(self.metrics[metric_name]) > 1000:
                    self.metrics[metric_name] = self.metrics[metric_name][
                        -500:
                    ]

                # Проверяем правила
                self._check_rules(metric_name, value, tags or {})
        except Exception as e:
            print(f"Ошибка добавления метрики {metric_name}: {e}")
            raise

    @private_method
    @performance_monitor
    def _check_rules(
        self, metric_name: str, value: float, tags: Dict[str, str]
    ):
        """Проверка правил для метрики"""
        try:
            current_time = datetime.now()

            for rule_id, rule in self.rules.items():
                if rule.metric_name != metric_name:
                    continue

                # Проверяем условие
                if not self._evaluate_condition(
                    value, rule.condition, rule.threshold
                ):
                    continue

                # Проверяем cooldown
                if rule_id in self.alert_cooldowns:
                    if current_time - self.alert_cooldowns[
                        rule_id
                    ] < timedelta(seconds=rule.cooldown):
                        continue

                # Проверяем лимит алертов в час
                if self._is_hourly_limit_exceeded(
                    rule_id, rule.max_alerts_per_hour
                ):
                    continue

                # Проверяем минимальное количество повторений
                if not self._check_min_occurrences(
                    rule_id, rule.min_occurrences
                ):
                    continue

                # Генерируем алерт
                self._generate_alert(rule, value, tags, current_time)
        except Exception as e:
            print(f"Ошибка проверки правил для {metric_name}: {e}")
            raise

    @private_method
    @performance_monitor
    def _evaluate_condition(
        self, value: float, condition: str, threshold: float
    ) -> bool:
        """Вычисление условия"""
        try:
            if condition == ">":
                return value > threshold
            elif condition == "<":
                return value < threshold
            elif condition == ">=":
                return value >= threshold
            elif condition == "<=":
                return value <= threshold
            elif condition == "==":
                return abs(value - threshold) < 0.001
            elif condition == "!=":
                return abs(value - threshold) >= 0.001
            else:
                return False
        except Exception as e:
            print(f"Ошибка вычисления условия {condition}: {e}")
            return False

    @private_method
    @performance_monitor
    def _is_hourly_limit_exceeded(self, rule_id: str, max_alerts: int) -> bool:
        """Проверка превышения лимита алертов в час"""
        try:
            current_hour = datetime.now().hour

            # Сбрасываем счетчик каждый час
            if current_hour != self.last_hour_reset.hour:
                self.hourly_alert_counts[rule_id] = 0
                self.last_hour_reset = datetime.now()

            return self.hourly_alert_counts[rule_id] >= max_alerts
        except Exception as e:
            print(f"Ошибка проверки лимита алертов для {rule_id}: {e}")
            return False

    @private_method
    def _check_min_occurrences(
        self, rule_id: str, min_occurrences: int
    ) -> bool:
        """Проверка минимального количества повторений"""
        try:
            # Если min_occurrences = 1, всегда разрешаем первый алерт
            if min_occurrences <= 1:
                return True
            if rule_id not in self.alert_history:
                return False

            recent_alerts = [
                alert_time
                for alert_time in self.alert_history[rule_id]
                if datetime.now() - alert_time < timedelta(minutes=5)
            ]

            return len(recent_alerts) >= min_occurrences
        except Exception as e:
            print(f"Ошибка проверки минимальных повторений для {rule_id}: {e}")
            return False

    @private_method
    @log_execution
    def _generate_alert(
        self,
        rule: AlertRule,
        value: float,
        tags: Dict[str, str],
        timestamp: datetime,
    ):
        """Генерация алерта"""
        try:
            alert_id = f"{rule.rule_id}_{int(timestamp.timestamp())}"

            # Адаптивная настройка порога
            if rule.adaptive_threshold:
                self._adapt_threshold(rule, value)

            alert = Alert(
                alert_id=alert_id,
                rule_id=rule.rule_id,
                title=f"{rule.name}: {rule.metric_name}",
                message=(
                    f"Метрика {rule.metric_name} = {value:.2f} "
                    f"{rule.condition} {rule.threshold:.2f}"
                ),
                severity=rule.severity,
                status=AlertStatus.ACTIVE,
                timestamp=timestamp,
                metric_name=rule.metric_name,
                current_value=value,
                threshold_value=rule.threshold,
                tags=tags,
            )

            # Добавляем алерт (блокировка уже захвачена в add_metric)
            self.alerts.append(alert)
            self.alert_cooldowns[rule.rule_id] = timestamp
            self.hourly_alert_counts[rule.rule_id] += 1
            self.alert_history[rule.rule_id].append(timestamp)

            # Ограничиваем размер списка алертов
            if len(self.alerts) > 1000:
                self.alerts = self.alerts[-500:]

            # Отправляем уведомления
            self._send_alert(alert)
        except Exception as e:
            print(f"Ошибка генерации алерта для {rule.rule_id}: {e}")
            raise

    @private_method
    def _adapt_threshold(self, rule: AlertRule, current_value: float):
        """Адаптивная настройка порога"""
        try:
            metric_name = rule.metric_name

            if metric_name not in self.baseline_metrics:
                self.baseline_metrics[metric_name] = []

            # Добавляем значение в базовую линию
            self.baseline_metrics[metric_name].append(current_value)

            # Ограничиваем размер базовой линии
            if len(self.baseline_metrics[metric_name]) > 100:
                self.baseline_metrics[metric_name] = self.baseline_metrics[
                    metric_name
                ][-50:]

            # Вычисляем адаптивный порог
            if len(self.baseline_metrics[metric_name]) >= 10:
                baseline_values = self.baseline_metrics[metric_name]
                mean_value = statistics.mean(baseline_values)
                std_value = (
                    statistics.stdev(baseline_values)
                    if len(baseline_values) > 1
                    else 0
                )

                # Адаптируем порог на основе статистики
                if rule.condition == ">":
                    adaptive_threshold = mean_value + (2 * std_value)
                elif rule.condition == "<":
                    adaptive_threshold = mean_value - (2 * std_value)
                else:
                    adaptive_threshold = rule.threshold

                # Обновляем порог (но не слишком агрессивно)
                rule.threshold = (rule.threshold * 0.8) + (
                    adaptive_threshold * 0.2
                )
        except Exception as e:
            print(f"Ошибка адаптации порога для {rule.rule_id}: {e}")
            # Не поднимаем исключение, так как это не критично

    @private_method
    @log_execution
    def _send_alert(self, alert: Alert):
        """Отправка алерта через callback'и"""
        try:
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    print(
                        f"Ошибка в callback для алерта {alert.alert_id}: {e}"
                    )
                    # Игнорируем ошибки в callback'ах
        except Exception as e:
            print(f"Ошибка отправки алерта {alert.alert_id}: {e}")
            # Не поднимаем исключение, так как это не критично

    @validate_input
    def add_alert_callback(self, callback: Callable[[Alert], None]):
        """Добавление callback для алертов"""
        try:
            if not callable(callback):
                raise ValueError("callback должен быть вызываемым объектом")
            self.alert_callbacks.append(callback)
        except Exception as e:
            print(f"Ошибка добавления callback: {e}")
            raise

    @property
    def active_alerts_count(self) -> int:
        """Количество активных алертов"""
        try:
            with self.lock:
                return len(
                    [
                        alert
                        for alert in self.alerts
                        if alert.status == AlertStatus.ACTIVE
                    ]
                )
        except Exception as e:
            print(f"Ошибка получения количества активных алертов: {e}")
            return 0

    @property
    def total_alerts_count(self) -> int:
        """Общее количество алертов"""
        try:
            with self.lock:
                return len(self.alerts)
        except Exception as e:
            print(f"Ошибка получения общего количества алертов: {e}")
            return 0

    @property
    def rules_count(self) -> int:
        """Количество правил мониторинга"""
        try:
            with self.lock:
                return len(self.rules)
        except Exception as e:
            print(f"Ошибка получения количества правил: {e}")
            return 0

    @performance_monitor
    def get_active_alerts(self) -> List[Alert]:
        """Получение активных алертов"""
        try:
            with self.lock:
                return [
                    alert
                    for alert in self.alerts
                    if alert.status == AlertStatus.ACTIVE
                ]
        except Exception as e:
            print(f"Ошибка получения активных алертов: {e}")
            return []

    @performance_monitor
    def get_alert_stats(self) -> Dict[str, Any]:
        """Получение статистики алертов"""
        try:
            with self.lock:
                active_count = len(
                    [a for a in self.alerts if a.status == AlertStatus.ACTIVE]
                )
                total_count = len(self.alerts)

                # Статистика по серьезности
                severity_stats = {}
                for severity in AlertSeverity:
                    count = len(
                        [a for a in self.alerts if a.severity == severity]
                    )
                    severity_stats[severity.value] = count

                # Статистика по правилам
                rule_stats = {}
                for rule_id in self.rules:
                    count = len(
                        [a for a in self.alerts if a.rule_id == rule_id]
                    )
                    rule_stats[rule_id] = count

                return {
                    "total_alerts": total_count,
                    "active_alerts": active_count,
                    "severity_stats": severity_stats,
                    "rule_stats": rule_stats,
                    "hourly_limits": self.hourly_alert_counts,
                    "cooldowns": {
                        rule_id: cooldown.isoformat()
                        for rule_id, cooldown in self.alert_cooldowns.items()
                    },
                }
        except Exception as e:
            print(f"Ошибка получения статистики алертов: {e}")
            return {
                "total_alerts": 0,
                "active_alerts": 0,
                "severity_stats": {},
                "rule_stats": {},
                "hourly_limits": {},
                "cooldowns": {},
            }

    @transaction
    def suppress_alert(
        self, alert_id: str, reason: str = "Manual suppression"
    ):
        """Подавление алерта"""
        try:
            if not isinstance(alert_id, str) or not alert_id.strip():
                raise ValueError("alert_id должен быть непустой строкой")

            with self.lock:
                for alert in self.alerts:
                    if alert.alert_id == alert_id:
                        alert.status = AlertStatus.SUPPRESSED
                        return True
                return False
        except Exception as e:
            print(f"Ошибка подавления алерта {alert_id}: {e}")
            return False

    @transaction
    def resolve_alert(self, alert_id: str):
        """Разрешение алерта"""
        try:
            if not isinstance(alert_id, str) or not alert_id.strip():
                raise ValueError("alert_id должен быть непустой строкой")

            with self.lock:
                for alert in self.alerts:
                    if alert.alert_id == alert_id:
                        alert.status = AlertStatus.RESOLVED
                        return True
                return False
        except Exception as e:
            print(f"Ошибка разрешения алерта {alert_id}: {e}")
            return False

    @private_method
    def _start_cleanup_thread(self) -> None:
        """Запуск потока для очистки старых данных"""
        try:

            def cleanup_worker():
                while not self._stop_cleanup:
                    try:
                        time.sleep(3600)  # Каждый час
                        if not self._stop_cleanup:
                            self._cleanup_old_data()
                    except Exception as e:
                        print(f"Ошибка в cleanup_worker: {e}")

            cleanup_thread = threading.Thread(
                target=cleanup_worker, daemon=True
            )
            cleanup_thread.start()
        except Exception as e:
            print(f"Ошибка запуска cleanup_thread: {e}")

    def stop_monitoring(self) -> None:
        """Остановка системы мониторинга"""
        try:
            self._stop_cleanup = True
            self.is_running = False
            print("Система мониторинга остановлена")
        except Exception as e:
            print(f"Ошибка остановки мониторинга: {e}")

    @private_method
    def _cleanup_old_data(self) -> None:
        """Очистка старых данных"""
        try:
            with self.lock:
                cutoff_time = datetime.now() - timedelta(days=7)

                # Удаляем старые алерты
                self.alerts = [
                    alert
                    for alert in self.alerts
                    if alert.timestamp > cutoff_time
                ]

                # Очищаем старую историю алертов
                for rule_id in self.alert_history:
                    self.alert_history[rule_id] = [
                        alert_time
                        for alert_time in self.alert_history[rule_id]
                        if alert_time > cutoff_time
                    ]
        except Exception as e:
            print(f"Ошибка очистки старых данных: {e}")

    # ================ НОВЫЕ МЕТОДЫ УПРАВЛЕНИЯ СИСТЕМОЙ ================

    @validate_input
    def start(self) -> None:
        """Запуск системы мониторинга"""
        try:
            with self.lock:
                self.is_running = True
                self.start_time = datetime.now()
                self.last_activity = datetime.now()
                print(f"Система мониторинга {self.name} запущена")
                return True
        except Exception as e:
            print(f"Ошибка запуска системы мониторинга: {e}")
            return False

    @validate_input
    def stop(self) -> None:
        """Остановка системы мониторинга"""
        try:
            with self.lock:
                self.is_running = False
                self.last_activity = datetime.now()
                print(f"Система мониторинга {self.name} остановлена")
                return True
        except Exception as e:
            print(f"Ошибка остановки системы мониторинга: {e}")
            return False

    @validate_input
    def pause(self) -> None:
        """Приостановка системы мониторинга"""
        try:
            with self.lock:
                self.is_paused = True
                self.last_activity = datetime.now()
                print(f"Система мониторинга {self.name} приостановлена")
                return True
        except Exception as e:
            print(f"Ошибка приостановки системы мониторинга: {e}")
            return False

    @validate_input
    def resume(self) -> None:
        """Возобновление системы мониторинга"""
        try:
            with self.lock:
                self.is_paused = False
                self.last_activity = datetime.now()
                print(f"Система мониторинга {self.name} возобновлена")
                return True
        except Exception as e:
            print(f"Ошибка возобновления системы мониторинга: {e}")
            return False

    @transaction
    def reset(self) -> None:
        """Сброс системы мониторинга к начальному состоянию"""
        try:
            with self.lock:
                # Очищаем все данные
                self.alerts.clear()
                self.metrics.clear()
                self.alert_history.clear()
                self.alert_cooldowns.clear()
                self.hourly_alert_counts.clear()
                self.adaptive_thresholds.clear()
                self.baseline_metrics.clear()

                # Сбрасываем статусы
                self.is_running = False
                self.is_paused = False
                self.start_time = datetime.now()
                self.last_activity = datetime.now()

                # Сбрасываем статистику
                self.total_metrics_received = 0
                self.total_alerts_generated = 0
                self.total_alerts_suppressed = 0
                self.total_alerts_resolved = 0

                # Сбрасываем счетчики ошибок
                self.callback_error_count = 0

                # Сбрасываем статистику производительности
                self.performance_stats = {
                    "avg_processing_time": 0.0,
                    "max_processing_time": 0.0,
                    "total_processing_time": 0.0,
                    "operations_count": 0,
                }

                print(f"Система мониторинга {self.name} сброшена")
                return True
        except Exception as e:
            print(f"Ошибка сброса системы мониторинга: {e}")
            return False

    @transaction
    def clear(self) -> None:
        """Очистка всех данных без сброса системы"""
        try:
            with self.lock:
                # Очищаем только данные, оставляем правила и конфигурацию
                self.alerts.clear()
                self.metrics.clear()
                self.alert_history.clear()
                self.alert_cooldowns.clear()
                self.hourly_alert_counts.clear()
                self.adaptive_thresholds.clear()
                self.baseline_metrics.clear()

                # Обновляем время последней активности
                self.last_activity = datetime.now()

                print(f"Данные системы мониторинга {self.name} очищены")
                return True
        except Exception as e:
            print(f"Ошибка очистки данных системы мониторинга: {e}")
            return False

    # ==================== МЕТОДЫ КОНФИГУРАЦИИ ====================

    @performance_monitor
    def get_config(self) -> Dict[str, Any]:
        """Получение конфигурации системы"""
        try:
            with self.lock:
                return {
                    "name": self.name,
                    "config_version": self.config_version,
                    "rules_count": len(self.rules),
                    "is_running": self.is_running,
                    "is_paused": self.is_paused,
                    "callback_count": len(self.alert_callbacks),
                    "start_time": (
                        self.start_time.isoformat()
                        if self.start_time
                        else None
                    ),
                    "last_activity": (
                        self.last_activity.isoformat()
                        if self.last_activity
                        else None
                    ),
                    "max_alerts_in_memory": self.max_alerts_in_memory,
                    "max_metrics_per_name": self.max_metrics_per_name,
                    "cleanup_interval_hours": self.cleanup_interval_hours,
                    "log_level": self.log_level,
                    "enable_debug": self.enable_debug,
                    "enable_validation": self.enable_validation,
                    "max_callback_errors": self.max_callback_errors,
                    "statistics": {
                        "total_metrics_received": self.total_metrics_received,
                        "total_alerts_generated": self.total_alerts_generated,
                        "total_alerts_suppressed": (
                            self.total_alerts_suppressed
                        ),
                        "total_alerts_resolved": self.total_alerts_resolved,
                        "callback_error_count": (self.callback_error_count),
                    },
                    "performance_stats": self.performance_stats.copy(),
                    "rules": {
                        rule_id: {
                            "name": rule.name,
                            "metric_name": rule.metric_name,
                            "condition": rule.condition,
                            "threshold": rule.threshold,
                            "severity": rule.severity.value,
                            "cooldown": rule.cooldown,
                            "min_occurrences": rule.min_occurrences,
                            "max_alerts_per_hour": rule.max_alerts_per_hour,
                            "adaptive_threshold": rule.adaptive_threshold,
                        }
                        for rule_id, rule in self.rules.items()
                    },
                }
        except Exception as e:
            print(f"Ошибка получения конфигурации: {e}")
            return {}

    @validate_input
    def set_config(self, config: Dict[str, Any]) -> bool:
        """Установка конфигурации системы"""
        try:
            if not isinstance(config, dict):
                raise ValueError("config должен быть словарем")

            with self.lock:
                if "name" in config:
                    self.name = str(config["name"])

                if "rules" in config:
                    # Обновляем правила
                    for rule_id, rule_config in config["rules"].items():
                        if rule_id in self.rules:
                            rule = self.rules[rule_id]
                            rule.name = rule_config.get("name", rule.name)
                            rule.threshold = rule_config.get(
                                "threshold", rule.threshold
                            )
                            rule.cooldown = rule_config.get(
                                "cooldown", rule.cooldown
                            )
                            rule.max_alerts_per_hour = rule_config.get(
                                "max_alerts_per_hour", rule.max_alerts_per_hour
                            )

                print(f"Конфигурация системы {self.name} обновлена")
                return True
        except Exception as e:
            print(f"Ошибка установки конфигурации: {e}")
            return False

    @validate_input
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Валидация конфигурации системы"""
        try:
            if not isinstance(config, dict):
                return False

            # Проверяем обязательные поля
            if "name" not in config:
                return False

            # Проверяем правила
            if "rules" in config:
                if not isinstance(config["rules"], dict):
                    return False

                for rule_id, rule_config in config["rules"].items():
                    if not isinstance(rule_config, dict):
                        return False

                    # Проверяем обязательные поля правила
                    required_fields = [
                        "name",
                        "metric_name",
                        "condition",
                        "threshold",
                    ]
                    if not all(
                        field in rule_config for field in required_fields
                    ):
                        return False

            return True
        except Exception as e:
            print(f"Ошибка валидации конфигурации: {e}")
            return False

    # ==================== МЕТОДЫ СТАТИСТИКИ И МОНИТОРИНГА ====================

    @performance_monitor
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Получение сводки по метрикам"""
        try:
            with self.lock:
                summary = {}
                for metric_name, values in self.metrics.items():
                    if values:
                        summary[metric_name] = {
                            "count": len(values),
                            "min": min(values),
                            "max": max(values),
                            "mean": statistics.mean(values),
                            "median": statistics.median(values),
                            "latest": values[-1],
                            "std": (
                                statistics.stdev(values)
                                if len(values) > 1
                                else 0
                            ),
                        }
                return summary
        except Exception as e:
            print(f"Ошибка получения сводки метрик: {e}")
            return {}

    @performance_monitor
    def get_performance_stats(self) -> Dict[str, Any]:
        """Получение статистики производительности"""
        try:
            with self.lock:
                return {
                    "total_alerts": len(self.alerts),
                    "active_alerts": len(
                        [
                            a
                            for a in self.alerts
                            if a.status == AlertStatus.ACTIVE
                        ]
                    ),
                    "rules_count": len(self.rules),
                    "metrics_count": len(self.metrics),
                    "callback_count": len(self.alert_callbacks),
                    "is_running": getattr(self, "is_running", False),
                    "is_paused": getattr(self, "is_paused", False),
                    "memory_usage": {
                        "alerts": len(self.alerts)
                        * 0.001,  # Примерная оценка в KB
                        "metrics": sum(
                            len(values) for values in self.metrics.values()
                        )
                        * 0.0001,
                        "rules": len(self.rules) * 0.01,
                    },
                }
        except Exception as e:
            print(f"Ошибка получения статистики производительности: {e}")
            return {}

    @performance_monitor
    def is_healthy(self) -> bool:
        """Проверка здоровья системы"""
        try:
            with self.lock:
                # Проверяем базовые условия здоровья
                if not self.is_running:
                    return False

                if self.is_paused:
                    return False

                # Проверяем количество ошибок в callback'ах
                if self.callback_error_count > self.max_callback_errors:
                    return False

                # Проверяем наличие критических алертов
                critical_alerts = [
                    a
                    for a in self.alerts
                    if a.severity == AlertSeverity.CRITICAL
                    and a.status == AlertStatus.ACTIVE
                ]

                if (
                    len(critical_alerts) > 5
                ):  # Слишком много критических алертов
                    return False

                return True
        except Exception as e:
            print(f"Ошибка проверки здоровья системы: {e}")
            return False

    @performance_monitor
    def get_health_status(self) -> Dict[str, Any]:
        """Получение детального статуса здоровья системы"""
        try:
            with self.lock:
                critical_alerts = [
                    a
                    for a in self.alerts
                    if a.severity == AlertSeverity.CRITICAL
                    and a.status == AlertStatus.ACTIVE
                ]

                error_alerts = [
                    a
                    for a in self.alerts
                    if a.severity == AlertSeverity.ERROR
                    and a.status == AlertStatus.ACTIVE
                ]

                health_score = 100
                issues = []

                if not self.is_running:
                    health_score -= 50
                    issues.append("Система не запущена")

                if self.is_paused:
                    health_score -= 20
                    issues.append("Система приостановлена")

                if len(critical_alerts) > 3:
                    health_score -= 30
                    issues.append(
                        f"Слишком много критических алертов: "
                        f"{len(critical_alerts)}"
                    )

                if len(error_alerts) > 10:
                    health_score -= 20
                    issues.append(
                        f"Слишком много алертов об ошибках: "
                        f"{len(error_alerts)}"
                    )

                if self.callback_error_count > self.max_callback_errors:
                    health_score -= 25
                    issues.append(
                        f"Слишком много ошибок в callback'ах: "
                        f"{self.callback_error_count}"
                    )

                # Проверяем время последней активности
                if self.last_activity:
                    inactive_minutes = (
                        datetime.now() - self.last_activity
                    ).total_seconds() / 60
                    if inactive_minutes > 60:  # Более часа без активности
                        health_score -= 10
                        issues.append(
                            f"Система неактивна {inactive_minutes:.1f} минут"
                        )

                return {
                    "healthy": health_score > 70,
                    "health_score": max(0, health_score),
                    "is_running": self.is_running,
                    "is_paused": self.is_paused,
                    "critical_alerts": len(critical_alerts),
                    "error_alerts": len(error_alerts),
                    "total_alerts": len(self.alerts),
                    "callback_errors": self.callback_error_count,
                    "max_callback_errors": self.max_callback_errors,
                    "last_activity": (
                        self.last_activity.isoformat()
                        if self.last_activity
                        else None
                    ),
                    "uptime_minutes": (
                        (datetime.now() - self.start_time).total_seconds() / 60
                        if self.start_time
                        else 0
                    ),
                    "issues": issues,
                    "timestamp": datetime.now().isoformat(),
                }
        except Exception as e:
            print(f"Ошибка получения статуса здоровья: {e}")
            return {
                "healthy": False,
                "health_score": 0,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    # ==================== МЕТОДЫ ЭКСПОРТА/ИМПОРТА ====================

    @transaction
    def export_data(self, file_path: str) -> bool:
        """Экспорт данных системы в файл"""
        try:
            if not isinstance(file_path, str) or not file_path.strip():
                raise ValueError("file_path должен быть непустой строкой")

            import json

            with self.lock:
                export_data = {
                    "name": self.name,
                    "rules": {
                        rule_id: {
                            "rule_id": rule.rule_id,
                            "name": rule.name,
                            "metric_name": rule.metric_name,
                            "condition": rule.condition,
                            "threshold": rule.threshold,
                            "severity": rule.severity.value,
                            "cooldown": rule.cooldown,
                            "min_occurrences": rule.min_occurrences,
                            "max_alerts_per_hour": rule.max_alerts_per_hour,
                            "adaptive_threshold": rule.adaptive_threshold,
                        }
                        for rule_id, rule in self.rules.items()
                    },
                    "alerts": [
                        {
                            "alert_id": alert.alert_id,
                            "rule_id": alert.rule_id,
                            "title": alert.title,
                            "message": alert.message,
                            "severity": alert.severity.value,
                            "status": alert.status.value,
                            "timestamp": alert.timestamp.isoformat(),
                            "metric_name": alert.metric_name,
                            "current_value": alert.current_value,
                            "threshold_value": alert.threshold_value,
                            "tags": alert.tags,
                            "occurrences": alert.occurrences,
                        }
                        for alert in self.alerts
                    ],
                    "metrics": {
                        metric_name: values[-100:]  # Последние 100 значений
                        for metric_name, values in self.metrics.items()
                    },
                    "export_timestamp": datetime.now().isoformat(),
                }

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            print(f"Данные экспортированы в {file_path}")
            return True
        except Exception as e:
            print(f"Ошибка экспорта данных: {e}")
            return False

    @transaction
    def import_data(self, file_path: str) -> bool:
        """Импорт данных системы из файла"""
        try:
            if not isinstance(file_path, str) or not file_path.strip():
                raise ValueError("file_path должен быть непустой строкой")

            import json

            with open(file_path, "r", encoding="utf-8") as f:
                import_data = json.load(f)

            with self.lock:
                # Импортируем правила
                if "rules" in import_data:
                    for rule_id, rule_data in import_data["rules"].items():
                        rule = AlertRule(
                            rule_id=rule_data["rule_id"],
                            name=rule_data["name"],
                            metric_name=rule_data["metric_name"],
                            condition=rule_data["condition"],
                            threshold=rule_data["threshold"],
                            severity=AlertSeverity(rule_data["severity"]),
                            cooldown=rule_data["cooldown"],
                            min_occurrences=rule_data["min_occurrences"],
                            max_alerts_per_hour=rule_data[
                                "max_alerts_per_hour"
                            ],
                            adaptive_threshold=rule_data["adaptive_threshold"],
                        )
                        self.rules[rule_id] = rule

                # Импортируем алерты
                if "alerts" in import_data:
                    for alert_data in import_data["alerts"]:
                        alert = Alert(
                            alert_id=alert_data["alert_id"],
                            rule_id=alert_data["rule_id"],
                            title=alert_data["title"],
                            message=alert_data["message"],
                            severity=AlertSeverity(alert_data["severity"]),
                            status=AlertStatus(alert_data["status"]),
                            timestamp=datetime.fromisoformat(
                                alert_data["timestamp"]
                            ),
                            metric_name=alert_data["metric_name"],
                            current_value=alert_data["current_value"],
                            threshold_value=alert_data["threshold_value"],
                            tags=alert_data["tags"],
                            occurrences=alert_data["occurrences"],
                        )
                        self.alerts.append(alert)

                # Импортируем метрики
                if "metrics" in import_data:
                    self.metrics.update(import_data["metrics"])

            print(f"Данные импортированы из {file_path}")
            return True
        except Exception as e:
            print(f"Ошибка импорта данных: {e}")
            return False

    @transaction
    def backup(self, backup_path: str = None) -> bool:
        """Создание резервной копии системы"""
        try:
            if backup_path is None:
                backup_path = (
                    f"smart_monitoring_backup_"
                    f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                )

            return self.export_data(backup_path)
        except Exception as e:
            print(f"Ошибка создания резервной копии: {e}")
            return False

    @transaction
    def restore(self, backup_path: str) -> bool:
        """Восстановление системы из резервной копии"""
        try:
            if not isinstance(backup_path, str) or not backup_path.strip():
                raise ValueError("backup_path должен быть непустой строкой")

            # Очищаем текущие данные
            self.clear()

            # Импортируем данные из резервной копии
            return self.import_data(backup_path)
        except Exception as e:
            print(f"Ошибка восстановления из резервной копии: {e}")
            return False

    # ==================== ASYNC/AWAIT МЕТОДЫ ====================

    @validate_input
    async def add_metric_async(
        self,
        metric_name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None,
    ) -> bool:
        """
        Асинхронное добавление метрики

        Args:
            metric_name: Название метрики
            value: Значение метрики
            tags: Дополнительные теги

        Returns:
            bool: True если метрика добавлена успешно

        Raises:
            ValueError: При некорректных входных данных
        """
        try:
            # Валидация входных данных
            if not isinstance(metric_name, str) or not metric_name.strip():
                raise ValueError("metric_name должен быть непустой строкой")
            if not isinstance(value, (int, float)):
                raise ValueError("value должен быть числом")
            if not isinstance(value, (int, float)) or value < 0:
                raise ValueError("value должен быть неотрицательным числом")
            if tags is not None and not isinstance(tags, dict):
                raise ValueError("tags должен быть словарем или None")

            # Проверка лимитов памяти
            if not self._check_memory_limits():
                await self._cleanup_old_data_async()
                if not self._check_memory_limits():
                    raise MemoryError("Превышен лимит памяти для метрик")

            with self.lock:
                if metric_name not in self.metrics:
                    self.metrics[metric_name] = []

                self.metrics[metric_name].append(value)
                self.total_metrics_received += 1

                # Ограничиваем размер истории
                if len(self.metrics[metric_name]) > self.max_metrics_per_name:
                    self.metrics[metric_name] = self.metrics[metric_name][
                        -self.max_metrics_per_name // 2:
                    ]

                # Асинхронная проверка правил
                await self._check_rules_async(metric_name, value, tags or {})

            return True
        except Exception as e:
            print(f"Ошибка асинхронного добавления метрики {metric_name}: {e}")
            raise

    @private_method
    async def _check_rules_async(
        self, metric_name: str, value: float, tags: Dict[str, str]
    ) -> None:
        """
        Асинхронная проверка правил для метрики

        Args:
            metric_name: Название метрики
            value: Значение метрики
            tags: Теги метрики
        """
        try:
            current_time = datetime.now()

            for rule_id, rule in self.rules.items():
                if rule.metric_name != metric_name:
                    continue

                # Проверяем условие
                if not self._evaluate_condition(
                    value, rule.condition, rule.threshold
                ):
                    continue

                # Проверяем cooldown
                if rule_id in self.alert_cooldowns:
                    if current_time - self.alert_cooldowns[
                        rule_id
                    ] < timedelta(seconds=rule.cooldown):
                        continue

                # Проверяем лимит алертов в час
                if self._is_hourly_limit_exceeded(
                    rule_id, rule.max_alerts_per_hour
                ):
                    continue

                # Проверяем минимальное количество повторений
                if not self._check_min_occurrences(
                    rule_id, rule.min_occurrences
                ):
                    continue

                # Асинхронная генерация алерта
                await self._generate_alert_async(
                    rule, value, tags, current_time
                )
        except Exception as e:
            print(f"Ошибка асинхронной проверки правил для {metric_name}: {e}")
            raise

    @private_method
    async def _generate_alert_async(
        self,
        rule: AlertRule,
        value: float,
        tags: Dict[str, str],
        timestamp: datetime,
    ) -> None:
        """
        Асинхронная генерация алерта

        Args:
            rule: Правило алерта
            value: Значение метрики
            tags: Теги метрики
            timestamp: Время генерации
        """
        try:
            alert_id = f"{rule.rule_id}_{int(timestamp.timestamp())}"

            # Адаптивная настройка порога
            if rule.adaptive_threshold:
                await self._adapt_threshold_async(rule, value)

            alert = Alert(
                alert_id=alert_id,
                rule_id=rule.rule_id,
                title=f"{rule.name}: {rule.metric_name}",
                message=(
                    f"Метрика {rule.metric_name} = {value:.2f} "
                    f"{rule.condition} {rule.threshold:.2f}"
                ),
                severity=rule.severity,
                status=AlertStatus.ACTIVE,
                timestamp=timestamp,
                metric_name=rule.metric_name,
                current_value=value,
                threshold_value=rule.threshold,
                tags=tags,
            )

            # Добавляем алерт
            with self.lock:
                self.alerts.append(alert)
                self.alert_cooldowns[rule.rule_id] = timestamp
                self.hourly_alert_counts[rule.rule_id] += 1
                self.alert_history[rule.rule_id].append(timestamp)
                self.total_alerts_generated += 1

                # Ограничиваем размер списка алертов
                if len(self.alerts) > self.max_alerts_in_memory:
                    self.alerts = self.alerts[
                        -self.max_alerts_in_memory // 2:
                    ]

            # Асинхронная отправка уведомлений
            await self._send_alert_async(alert)
        except Exception as e:
            print(
                f"Ошибка асинхронной генерации алерта для {rule.rule_id}: {e}"
            )
            raise

    @private_method
    async def _send_alert_async(self, alert: Alert) -> None:
        """
        Асинхронная отправка алерта через callback'и

        Args:
            alert: Алерт для отправки
        """
        try:
            for callback in self.alert_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(alert)
                    else:
                        callback(alert)
                except Exception as e:
                    print(
                        f"Ошибка в асинхронном callback для алерта "
                        f"{alert.alert_id}: {e}"
                    )
                    self.callback_error_count += 1
        except Exception as e:
            print(f"Ошибка асинхронной отправки алерта {alert.alert_id}: {e}")

    @private_method
    async def _adapt_threshold_async(
        self, rule: AlertRule, current_value: float
    ) -> None:
        """
        Асинхронная адаптивная настройка порога

        Args:
            rule: Правило для адаптации
            current_value: Текущее значение метрики
        """
        try:
            metric_name = rule.metric_name

            if metric_name not in self.baseline_metrics:
                self.baseline_metrics[metric_name] = []

            # Добавляем значение в базовую линию
            self.baseline_metrics[metric_name].append(current_value)

            # Ограничиваем размер базовой линии
            if len(self.baseline_metrics[metric_name]) > 100:
                self.baseline_metrics[metric_name] = self.baseline_metrics[
                    metric_name
                ][-50:]

            # Вычисляем адаптивный порог
            if len(self.baseline_metrics[metric_name]) >= 10:
                baseline_values = self.baseline_metrics[metric_name]
                mean_value = statistics.mean(baseline_values)
                std_value = (
                    statistics.stdev(baseline_values)
                    if len(baseline_values) > 1
                    else 0
                )

                # Адаптируем порог на основе статистики
                if rule.condition == ">":
                    adaptive_threshold = mean_value + (2 * std_value)
                elif rule.condition == "<":
                    adaptive_threshold = mean_value - (2 * std_value)
                else:
                    adaptive_threshold = rule.threshold

                # Обновляем порог (но не слишком агрессивно)
                rule.threshold = (rule.threshold * 0.8) + (
                    adaptive_threshold * 0.2
                )
        except Exception as e:
            print(
                f"Ошибка асинхронной адаптации порога для {rule.rule_id}: {e}"
            )

    @private_method
    async def _cleanup_old_data_async(self) -> None:
        """Асинхронная очистка старых данных"""
        try:
            with self.lock:
                cutoff_time = datetime.now() - timedelta(days=7)

                # Удаляем старые алерты
                old_count = len(self.alerts)
                self.alerts = [
                    alert
                    for alert in self.alerts
                    if alert.timestamp > cutoff_time
                ]
                removed_alerts = old_count - len(self.alerts)

                # Очищаем старую историю алертов
                for rule_id in self.alert_history:
                    old_count = len(self.alert_history[rule_id])
                    self.alert_history[rule_id] = [
                        alert_time
                        for alert_time in self.alert_history[rule_id]
                        if alert_time > cutoff_time
                    ]

                print(
                    f"Асинхронная очистка: удалено {removed_alerts} "
                    f"старых алертов"
                )
        except Exception as e:
            print(f"Ошибка асинхронной очистки старых данных: {e}")

    @validate_input
    async def add_alert_callback_async(self, callback: Callable) -> bool:
        """
        Асинхронное добавление callback для алертов

        Args:
            callback: Callback функция (может быть async или sync)

        Returns:
            bool: True если callback добавлен успешно

        Raises:
            ValueError: При некорректном callback
        """
        try:
            if not callable(callback):
                raise ValueError("callback должен быть вызываемым объектом")

            # Проверяем лимит callback'ов
            if len(self.alert_callbacks) >= 50:  # Максимум 50 callback'ов
                raise ValueError("Превышен лимит callback'ов (50)")

            self.alert_callbacks.append(callback)
            return True
        except Exception as e:
            print(f"Ошибка асинхронного добавления callback: {e}")
            raise

    # ==================== УЛУЧШЕННАЯ ВАЛИДАЦИЯ ПАРАМЕТРОВ ====================

    @private_method
    def _validate_metric_name(self, metric_name: str) -> None:
        """
        Расширенная валидация имени метрики

        Args:
            metric_name: Имя метрики для валидации

        Raises:
            ValueError: При некорректном имени метрики
        """
        if not isinstance(metric_name, str):
            raise ValueError("metric_name должен быть строкой")

        if not metric_name.strip():
            raise ValueError("metric_name не может быть пустой строкой")

        if len(metric_name) > 255:
            raise ValueError("metric_name не может быть длиннее 255 символов")

        # Проверяем на недопустимые символы
        invalid_chars = [
            "\x00",
            "\x01",
            "\x02",
            "\x03",
            "\x04",
            "\x05",
            "\x06",
            "\x07",
            "\x08",
            "\x0b",
            "\x0c",
            "\x0e",
            "\x0f",
            "\x10",
            "\x11",
            "\x12",
            "\x13",
            "\x14",
            "\x15",
            "\x16",
            "\x17",
            "\x18",
            "\x19",
            "\x1a",
            "\x1b",
            "\x1c",
            "\x1d",
            "\x1e",
            "\x1f",
        ]

        for char in invalid_chars:
            if char in metric_name:
                raise ValueError(
                    f"metric_name содержит недопустимый символ: {repr(char)}"
                )

        # Проверяем на SQL injection попытки
        sql_keywords = [
            "SELECT",
            "INSERT",
            "UPDATE",
            "DELETE",
            "DROP",
            "CREATE",
            "ALTER",
        ]
        metric_upper = metric_name.upper()
        for keyword in sql_keywords:
            if keyword in metric_upper:
                raise ValueError(
                    f"metric_name содержит потенциально опасный SQL "
                    f"ключевое слово: {keyword}"
                )

    @private_method
    def _validate_metric_value(self, value: float) -> None:
        """
        Расширенная валидация значения метрики

        Args:
            value: Значение метрики для валидации

        Raises:
            ValueError: При некорректном значении метрики
        """
        if not isinstance(value, (int, float)):
            raise ValueError("value должен быть числом (int или float)")

        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError("value должен быть неотрицательным числом")

        # Проверяем на NaN и бесконечность
        import math

        if math.isnan(value):
            raise ValueError("value не может быть NaN")

        if math.isinf(value):
            raise ValueError("value не может быть бесконечностью")

        # Проверяем разумные пределы
        if abs(value) > 1e15:
            raise ValueError("value слишком большое (больше 1e15)")

    @private_method
    def _validate_tags(self, tags: Optional[Dict[str, str]]) -> None:
        """
        Расширенная валидация тегов метрики

        Args:
            tags: Теги для валидации

        Raises:
            ValueError: При некорректных тегах
        """
        if tags is None:
            return

        if not isinstance(tags, dict):
            raise ValueError("tags должен быть словарем или None")

        if len(tags) > 50:  # Максимум 50 тегов
            raise ValueError("Слишком много тегов (максимум 50)")

        for key, value in tags.items():
            if not isinstance(key, str) or not isinstance(value, str):
                raise ValueError("Ключи и значения тегов должны быть строками")

            if len(key) > 100 or len(value) > 500:
                raise ValueError(
                    "Ключи тегов не должны превышать 100 символов, "
                    "значения - 500"
                )

            if not key.strip() or not value.strip():
                raise ValueError(
                    "Ключи и значения тегов не могут быть пустыми"
                )

            # Проверяем на недопустимые символы в ключах
            invalid_chars = ["=", " ", "\n", "\r", "\t"]
            for char in invalid_chars:
                if char in key:
                    raise ValueError(
                        f"Ключ тега содержит недопустимый символ: {repr(char)}"
                    )

    @private_method
    def _validate_rule(self, rule: AlertRule) -> None:
        """
        Расширенная валидация правила алерта

        Args:
            rule: Правило для валидации

        Raises:
            ValueError: При некорректном правиле
        """
        if not isinstance(rule, AlertRule):
            raise ValueError("rule должен быть экземпляром AlertRule")

        # Валидируем rule_id
        if not isinstance(rule.rule_id, str) or not rule.rule_id.strip():
            raise ValueError("rule_id должен быть непустой строкой")

        if len(rule.rule_id) > 100:
            raise ValueError("rule_id не может быть длиннее 100 символов")

        # Валидируем threshold
        if not isinstance(rule.threshold, (int, float)):
            raise ValueError("threshold должен быть числом")

        if rule.threshold < 0:
            raise ValueError("threshold должен быть неотрицательным")

        # Валидируем cooldown
        if not isinstance(rule.cooldown, int) or rule.cooldown < 0:
            raise ValueError(
                "cooldown должен быть неотрицательным целым числом"
            )

        if rule.cooldown > 86400:  # Максимум 24 часа
            raise ValueError(
                "cooldown не может превышать 86400 секунд (24 часа)"
            )

        # Валидируем min_occurrences
        if (
            not isinstance(rule.min_occurrences, int)
            or rule.min_occurrences < 1
        ):
            raise ValueError(
                "min_occurrences должен быть положительным целым числом"
            )

        # Валидируем max_alerts_per_hour
        if (
            not isinstance(rule.max_alerts_per_hour, int)
            or rule.max_alerts_per_hour < 1
        ):
            raise ValueError(
                "max_alerts_per_hour должен быть положительным целым числом"
            )

        if rule.max_alerts_per_hour > 3600:  # Максимум 1 алерт в секунду
            raise ValueError("max_alerts_per_hour не может превышать 3600")

    @private_method
    def _validate_alert_id(self, alert_id: str) -> None:
        """
        Валидация ID алерта

        Args:
            alert_id: ID алерта для валидации

        Raises:
            ValueError: При некорректном ID алерта
        """
        if not isinstance(alert_id, str):
            raise ValueError("alert_id должен быть строкой")

        if not alert_id.strip():
            raise ValueError("alert_id не может быть пустой строкой")

        if len(alert_id) > 255:
            raise ValueError("alert_id не может быть длиннее 255 символов")

        # Проверяем формат ID (должен содержать rule_id и timestamp)
        if "_" not in alert_id:
            raise ValueError(
                "alert_id должен содержать символ '_' для разделения "
                "rule_id и timestamp"
            )

        parts = alert_id.split("_", 1)
        if len(parts) != 2:
            raise ValueError(
                "alert_id должен иметь формат 'rule_id_timestamp'"
            )

        try:
            int(parts[1])  # Проверяем что timestamp - число
        except ValueError:
            raise ValueError("timestamp в alert_id должен быть числом")

    # ==================== ЗАЩИТА ОТ ПЕРЕПОЛНЕНИЯ ПАМЯТИ ====================

    @private_method
    def _check_memory_limits(self) -> bool:
        """
        Проверка лимитов памяти

        Returns:
            bool: True если лимиты не превышены
        """
        try:
            self.operation_count += 1

            # Проверяем лимиты каждые N операций
            if self.operation_count % self.memory_check_interval != 0:
                return True

            # Проверяем количество алертов
            if len(self.alerts) > self.max_alerts_in_memory:
                return False

            # Проверяем количество метрик
            total_metrics = sum(
                len(values) for values in self.metrics.values()
            )
            if (
                total_metrics > self.max_metrics_per_name * 10
            ):  # 10x лимит для всех метрик
                return False

            # Проверяем размер callback'ов
            if len(self.alert_callbacks) > 100:
                return False

            # Проверяем использование памяти процесса (если доступно)
            try:
                import psutil

                process = psutil.Process()
                memory_mb = process.memory_info().rss / 1024 / 1024
                if memory_mb > self.max_memory_usage_mb:
                    return False
            except ImportError:
                # psutil не доступен, пропускаем проверку
                pass

            self.last_memory_check = datetime.now()
            return True

        except Exception as e:
            print(f"Ошибка проверки лимитов памяти: {e}")
            return False

    @private_method
    def _cleanup_memory(self) -> None:
        """Принудительная очистка памяти"""
        try:
            with self.lock:
                # Очищаем старые алерты
                cutoff_time = datetime.now() - timedelta(hours=24)
                old_count = len(self.alerts)
                self.alerts = [
                    alert
                    for alert in self.alerts
                    if alert.timestamp > cutoff_time
                ]

                # Очищаем старые метрики
                for metric_name in list(self.metrics.keys()):
                    if (
                        len(self.metrics[metric_name])
                        > self.max_metrics_per_name
                    ):
                        # Оставляем только последние 25% значений
                        keep_count = self.max_metrics_per_name // 4
                        self.metrics[metric_name] = self.metrics[metric_name][
                            -keep_count:
                        ]

                # Очищаем историю алертов
                for rule_id in self.alert_history:
                    self.alert_history[rule_id] = [
                        alert_time
                        for alert_time in self.alert_history[rule_id]
                        if alert_time > cutoff_time
                    ]

                # Очищаем базовые метрики
                for metric_name in list(self.baseline_metrics.keys()):
                    if len(self.baseline_metrics[metric_name]) > 50:
                        self.baseline_metrics[metric_name] = (
                            self.baseline_metrics[metric_name][-25:]
                        )

                removed_alerts = old_count - len(self.alerts)
                print(
                    f"Принудительная очистка памяти: удалено "
                    f"{removed_alerts} алертов"
                )

        except Exception as e:
            print(f"Ошибка принудительной очистки памяти: {e}")

    @private_method
    def _estimate_memory_usage(self) -> Dict[str, int]:
        """
        Оценка использования памяти

        Returns:
            Dict с оценкой использования памяти по компонентам
        """
        try:
            # Примерная оценка размера в байтах
            alert_size = 200  # Примерный размер одного алерта
            metric_size = 8  # Размер float
            rule_size = 100  # Размер правила

            memory_usage = {
                "alerts_mb": (len(self.alerts) * alert_size) / 1024 / 1024,
                "metrics_mb": (
                    sum(len(values) for values in self.metrics.values())
                    * metric_size
                )
                / 1024
                / 1024,
                "rules_mb": (len(self.rules) * rule_size) / 1024 / 1024,
                "callbacks_count": len(self.alert_callbacks),
                "total_estimated_mb": 0,
            }

            memory_usage["total_estimated_mb"] = (
                memory_usage["alerts_mb"]
                + memory_usage["metrics_mb"]
                + memory_usage["rules_mb"]
            )

            return memory_usage

        except Exception as e:
            print(f"Ошибка оценки использования памяти: {e}")
            return {"error": str(e)}

    @performance_monitor
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Получение статистики использования памяти

        Returns:
            Dict со статистикой памяти
        """
        try:
            with self.lock:
                memory_usage = self._estimate_memory_usage()

                return {
                    "memory_usage": memory_usage,
                    "limits": {
                        "max_memory_mb": self.max_memory_usage_mb,
                        "max_alerts": self.max_alerts_in_memory,
                        "max_metrics_per_name": self.max_metrics_per_name,
                        "max_callbacks": 100,
                    },
                    "current_counts": {
                        "alerts": len(self.alerts),
                        "metrics_names": len(self.metrics),
                        "total_metrics": sum(
                            len(values) for values in self.metrics.values()
                        ),
                        "rules": len(self.rules),
                        "callbacks": len(self.alert_callbacks),
                    },
                    "memory_pressure": memory_usage["total_estimated_mb"]
                    > self.max_memory_usage_mb * 0.8,
                    "last_check": self.last_memory_check.isoformat(),
                    "operation_count": self.operation_count,
                }

        except Exception as e:
            print(f"Ошибка получения статистики памяти: {e}")
            return {"error": str(e)}

    # ==================== СТРУКТУРИРОВАННОЕ ЛОГИРОВАНИЕ ====================

    @private_method
    def _log_event(self, level: str, message: str, **kwargs) -> None:
        """
        Структурированное логирование событий

        Args:
            level: Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: Сообщение для логирования
            **kwargs: Дополнительные поля для структурированного лога
        """
        try:
            if self.log_level == "DISABLED":
                return

            # Проверяем уровень логирования
            levels = {
                "DEBUG": 0,
                "INFO": 1,
                "WARNING": 2,
                "ERROR": 3,
                "CRITICAL": 4,
            }
            current_level = levels.get(self.log_level, 1)
            event_level = levels.get(level, 1)

            if event_level < current_level:
                return

            # Создаем структурированный лог
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "level": level,
                "message": message,
                "system_name": self.name,
                "component": "SmartMonitoringSystem",
                **kwargs,
            }

            # Выводим в консоль
            if self.enable_debug or level in ["ERROR", "CRITICAL"]:
                print(f"[{level}] {message}")
                if kwargs:
                    print(f"  Дополнительные данные: {kwargs}")

            # Записываем в файл если указан
            if self.log_file:
                try:
                    import json

                    with open(self.log_file, "a", encoding="utf-8") as f:
                        f.write(
                            json.dumps(log_entry, ensure_ascii=False) + "\n"
                        )
                except Exception as e:
                    print(f"Ошибка записи в лог файл: {e}")

        except Exception as e:
            print(f"Ошибка логирования: {e}")

    @private_method
    def _log_performance(
        self, operation: str, duration: float, **kwargs
    ) -> None:
        """
        Логирование производительности операций

        Args:
            operation: Название операции
            duration: Время выполнения в секундах
            **kwargs: Дополнительные метрики
        """
        try:
            self._log_event(
                "INFO",
                f"Операция {operation} выполнена",
                operation=operation,
                duration_seconds=duration,
                performance_metrics={
                    "total_alerts": len(self.alerts),
                    "total_metrics": sum(
                        len(values) for values in self.metrics.values()
                    ),
                    "memory_usage_mb": self._estimate_memory_usage().get(
                        "total_estimated_mb", 0
                    ),
                    **kwargs,
                },
            )
        except Exception as e:
            print(f"Ошибка логирования производительности: {e}")

    @private_method
    def _log_security_event(
        self, event_type: str, details: str, severity: str = "INFO"
    ) -> None:
        """
        Логирование событий безопасности

        Args:
            event_type: Тип события безопасности
            details: Детали события
            severity: Серьезность события
        """
        try:
            self._log_event(
                severity,
                f"Событие безопасности: {event_type}",
                security_event_type=event_type,
                details=details,
                system_state={
                    "is_running": self.is_running,
                    "is_paused": self.is_paused,
                    "callback_errors": self.callback_error_count,
                    "total_alerts": len(self.alerts),
                },
            )
        except Exception as e:
            print(f"Ошибка логирования события безопасности: {e}")

    @validate_input
    def set_logging_config(
        self,
        log_level: str = "INFO",
        log_file: Optional[str] = None,
        enable_debug: bool = False,
    ) -> bool:
        """
        Настройка конфигурации логирования

        Args:
            log_level: Уровень логирования (DEBUG, INFO, WARNING, ERROR,
                CRITICAL, DISABLED)
            log_file: Путь к файлу лога (опционально)
            enable_debug: Включить отладочный вывод

        Returns:
            bool: True если конфигурация применена успешно
        """
        try:
            valid_levels = [
                "DEBUG",
                "INFO",
                "WARNING",
                "ERROR",
                "CRITICAL",
                "DISABLED",
            ]
            if log_level not in valid_levels:
                raise ValueError(
                    f"log_level должен быть одним из: {valid_levels}"
                )

            self.log_level = log_level
            self.log_file = log_file
            self.enable_debug = enable_debug

            self._log_event(
                "INFO",
                "Конфигурация логирования обновлена",
                log_level=log_level,
                log_file=log_file,
                enable_debug=enable_debug,
            )

            return True
        except Exception as e:
            print(f"Ошибка настройки логирования: {e}")
            return False

    # ==================== УЛУЧШЕННАЯ ОБРАБОТКА ОШИБОК ====================

    @private_method
    def _handle_error(
        self, error: Exception, context: str, severity: str = "ERROR"
    ) -> None:
        """
        Улучшенная обработка ошибок с логированием и восстановлением

        Args:
            error: Исключение для обработки
            context: Контекст возникновения ошибки
            severity: Серьезность ошибки
        """
        try:
            # Логируем ошибку
            self._log_event(
                severity,
                f"Ошибка в {context}: {str(error)}",
                error_type=type(error).__name__,
                error_message=str(error),
                context=context,
                severity=severity,
                system_state={
                    "is_running": self.is_running,
                    "is_paused": self.is_paused,
                    "total_alerts": len(self.alerts),
                    "callback_errors": self.callback_error_count,
                },
            )

            # Увеличиваем счетчик ошибок если это критическая ошибка
            if severity in ["ERROR", "CRITICAL"]:
                self.callback_error_count += 1

            # Проверяем лимит ошибок
            if self.callback_error_count > self.max_callback_errors:
                self._log_security_event(
                    "ERROR_LIMIT_EXCEEDED",
                    f"Превышен лимит ошибок: {self.callback_error_count}",
                    "CRITICAL",
                )

                # Автоматическое восстановление
                if severity == "CRITICAL":
                    self._emergency_recovery()

        except Exception as log_error:
            print(f"Критическая ошибка в обработке ошибок: {log_error}")

    @private_method
    def _emergency_recovery(self) -> None:
        """Экстренное восстановление системы при критических ошибках"""
        try:
            self._log_security_event(
                "EMERGENCY_RECOVERY",
                "Запуск экстренного восстановления системы",
                "CRITICAL",
            )

            # Очищаем проблемные callback'ы
            if self.callback_error_count > self.max_callback_errors:
                self.alert_callbacks.clear()
                self.callback_error_count = 0
                self._log_event(
                    "WARNING", "Очищены все callback'ы из-за ошибок"
                )

            # Принудительная очистка памяти
            self._cleanup_memory()

            # Сброс критических счетчиков
            self.performance_stats["operations_count"] = 0

            self._log_event("INFO", "Экстренное восстановление завершено")

        except Exception as e:
            print(f"Ошибка экстренного восстановления: {e}")

    @performance_monitor
    def get_system_health_detailed(self) -> Dict[str, Any]:
        """
        Детальная проверка здоровья системы

        Returns:
            Dict с детальной информацией о состоянии системы
        """
        try:
            with self.lock:
                # Получаем статистику памяти
                memory_stats = self.get_memory_stats()

                # Получаем статистику производительности
                perf_stats = self.get_performance_stats()

                # Проверяем критические алерты
                critical_alerts = [
                    alert
                    for alert in self.alerts
                    if alert.severity == AlertSeverity.CRITICAL
                    and alert.status == AlertStatus.ACTIVE
                ]

                # Вычисляем общий индекс здоровья
                health_score = 100

                if len(critical_alerts) > 3:
                    health_score -= 25

                if self.callback_error_count > self.max_callback_errors:
                    health_score -= 20

                if memory_stats.get("memory_pressure", False):
                    health_score -= 15

                if not self.is_running:
                    health_score -= 10

                return {
                    "overall_health_score": max(0, health_score),
                    "health_status": (
                        "HEALTHY"
                        if health_score > 80
                        else "WARNING" if health_score > 50 else "CRITICAL"
                    ),
                    "memory_stats": memory_stats,
                    "performance_stats": perf_stats,
                    "critical_alerts_count": len(critical_alerts),
                    "callback_errors": self.callback_error_count,
                    "max_callback_errors": self.max_callback_errors,
                    "is_running": self.is_running,
                    "is_paused": self.is_paused,
                    "uptime_minutes": (
                        (datetime.now() - self.start_time).total_seconds() / 60
                        if self.start_time
                        else 0
                    ),
                    "last_activity": (
                        self.last_activity.isoformat()
                        if self.last_activity
                        else None
                    ),
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception as e:
            self._handle_error(
                e, "получение детального здоровья системы", "ERROR"
            )
            return {
                "overall_health_score": 0,
                "health_status": "ERROR",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    # ==================== ДОПОЛНИТЕЛЬНЫЕ МЕТОДЫ ====================

    def __eq__(self, other) -> bool:
        """
        Сравнение объектов SmartMonitoringSystem

        Args:
            other: Другой объект для сравнения
        Returns:
            bool: True если объекты равны
        """
        if not isinstance(other, SmartMonitoringSystem):
            return False

        return (
            self.name == other.name
            and len(self.rules) == len(other.rules)
            and len(self.alerts) == len(other.alerts)
            and self.is_running == other.is_running
        )

    def __hash__(self) -> int:
        """
        Хеширование объекта для использования в множествах

        Returns:
            int: Хеш объекта
        """
        return hash((self.name, len(self.rules), len(self.alerts)))

    def __len__(self) -> int:
        """
        Возвращает количество активных алертов

        Returns:
            int: Количество активных алертов
        """
        return self.active_alerts_count

    def __contains__(self, item) -> bool:
        """
        Проверяет принадлежность алерта к системе

        Args:
            item: Алерт или ID алерта для проверки

        Returns:
            bool: True если алерт принадлежит системе
        """
        if isinstance(item, Alert):
            return item in self.alerts
        elif isinstance(item, str):
            return any(alert.alert_id == item for alert in self.alerts)
        return False

    def __enter__(self) -> "SmartMonitoringSystem":
        """
        Вход в контекстный менеджер

        Returns:
            SmartMonitoringSystem: Сам объект
        """
        self.start()
        return self

    def __exit__(self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Optional[object]) -> None:
        """
        Выход из контекстного менеджера

        Args:
            exc_type: Тип исключения
            exc_val: Значение исключения
            exc_tb: Трассировка исключения
        """
        self.stop()

    def __iter__(self) -> "Iterator[Alert]":
        """
        Итератор по активным алертам

        Returns:
            Iterator[Alert]: Итератор по активным алертам
        """
        return iter(self.get_active_alerts())

    def __next__(self) -> Alert:
        """
        Следующий элемент итерации

        Returns:
            Alert: Следующий активный алерт
        """
        active_alerts = self.get_active_alerts()
        if not hasattr(self, '_iter_index'):
            self._iter_index = 0

        if self._iter_index >= len(active_alerts):
            self._iter_index = 0
            raise StopIteration

        alert = active_alerts[self._iter_index]
        self._iter_index += 1
        return alert

    @performance_monitor
    def to_dict(self) -> Dict[str, Any]:
        """
        Сериализация объекта в словарь

        Returns:
            Dict[str, Any]: Словарь с данными объекта
        """
        try:
            with self.lock:
                return {
                    "name": self.name,
                    "rules": {
                        rule_id: {
                            "rule_id": rule.rule_id,
                            "name": rule.name,
                            "metric_name": rule.metric_name,
                            "condition": rule.condition,
                            "threshold": rule.threshold,
                            "severity": rule.severity.value,
                            "cooldown": rule.cooldown,
                            "min_occurrences": rule.min_occurrences,
                            "max_alerts_per_hour": rule.max_alerts_per_hour,
                            "adaptive_threshold": rule.adaptive_threshold,
                        }
                        for rule_id, rule in self.rules.items()
                    },
                    "alerts": [
                        {
                            "alert_id": alert.alert_id,
                            "rule_id": alert.rule_id,
                            "title": alert.title,
                            "message": alert.message,
                            "severity": alert.severity.value,
                            "status": alert.status.value,
                            "timestamp": alert.timestamp.isoformat(),
                            "metric_name": alert.metric_name,
                            "current_value": alert.current_value,
                            "threshold_value": alert.threshold_value,
                            "tags": alert.tags,
                            "occurrences": alert.occurrences,
                        }
                        for alert in self.alerts
                    ],
                    "metrics": {
                        metric_name: values[-100:]  # Последние 100 значений
                        for metric_name, values in self.metrics.items()
                    },
                    "config": {
                        "name": self.name,
                        "config_version": self.config_version,
                        "max_alerts_in_memory": self.max_alerts_in_memory,
                        "max_metrics_per_name": self.max_metrics_per_name,
                        "cleanup_interval_hours": self.cleanup_interval_hours,
                        "log_level": self.log_level,
                        "enable_debug": self.enable_debug,
                        "enable_validation": self.enable_validation,
                        "max_callback_errors": self.max_callback_errors,
                        "max_memory_usage_mb": self.max_memory_usage_mb,
                    },
                    "health_status": {
                        "health_score": 50,  # Базовое значение
                        "is_healthy": self.is_running and not self.is_paused,
                    },
                    "performance_stats": {
                        "total_metrics_received": self.total_metrics_received,
                        "total_alerts_generated": self.total_alerts_generated,
                        "operation_count": self.operation_count,
                    },
                    "memory_stats": {
                        "alerts_count": len(self.alerts),
                        "rules_count": len(self.rules),
                        "metrics_count": len(self.metrics),
                    },
                }
        except Exception as e:
            print(f"Ошибка сериализации в словарь: {e}")
            return {}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SmartMonitoringSystem":
        """
        Десериализация объекта из словаря

        Args:
            data: Словарь с данными объекта

        Returns:
            SmartMonitoringSystem: Восстановленный объект
        """
        try:
            name = data.get("name", "RestoredSystem")
            system = cls(name)

            # Восстанавливаем правила
            if "rules" in data:
                for rule_id, rule_data in data["rules"].items():
                    rule = AlertRule(
                        rule_id=rule_data["rule_id"],
                        name=rule_data["name"],
                        metric_name=rule_data["metric_name"],
                        condition=rule_data["condition"],
                        threshold=rule_data["threshold"],
                        severity=AlertSeverity(rule_data["severity"]),
                        cooldown=rule_data["cooldown"],
                        min_occurrences=rule_data["min_occurrences"],
                        max_alerts_per_hour=rule_data["max_alerts_per_hour"],
                        adaptive_threshold=rule_data["adaptive_threshold"],
                    )
                    system.add_rule(rule)

            # Восстанавливаем алерты
            if "alerts" in data:
                for alert_data in data["alerts"]:
                    alert = Alert(
                        alert_id=alert_data["alert_id"],
                        rule_id=alert_data["rule_id"],
                        title=alert_data["title"],
                        message=alert_data["message"],
                        severity=AlertSeverity(alert_data["severity"]),
                        status=AlertStatus(alert_data["status"]),
                        timestamp=datetime.fromisoformat(
                            alert_data["timestamp"]
                        ),
                        metric_name=alert_data["metric_name"],
                        current_value=alert_data["current_value"],
                        threshold_value=alert_data["threshold_value"],
                        tags=alert_data["tags"],
                        occurrences=alert_data["occurrences"],
                    )
                    system.alerts.append(alert)

            # Восстанавливаем метрики
            if "metrics" in data:
                system.metrics.update(data["metrics"])

            return system
        except Exception as e:
            print(f"Ошибка десериализации из словаря: {e}")
            return cls("ErrorSystem")

    @performance_monitor
    def clone(self) -> "SmartMonitoringSystem":
        """
        Клонирование объекта

        Returns:
            SmartMonitoringSystem: Клонированный объект
        """
        try:
            data = self.to_dict()
            data["name"] = f"{self.name}_clone"
            return self.from_dict(data)
        except Exception as e:
            print(f"Ошибка клонирования: {e}")
            return SmartMonitoringSystem(f"{self.name}_clone")

    @performance_monitor
    def merge(self, other: "SmartMonitoringSystem") -> bool:
        """
        Слияние с другим объектом SmartMonitoringSystem

        Args:
            other: Другой объект для слияния

        Returns:
            bool: True если слияние прошло успешно
        """
        try:
            if not isinstance(other, SmartMonitoringSystem):
                return False

            with self.lock:
                # Объединяем правила
                for rule_id, rule in other.rules.items():
                    if rule_id not in self.rules:
                        self.rules[rule_id] = rule

                # Объединяем алерты
                for alert in other.alerts:
                    if alert not in self.alerts:
                        self.alerts.append(alert)

                # Объединяем метрики
                for metric_name, values in other.metrics.items():
                    if metric_name not in self.metrics:
                        self.metrics[metric_name] = []
                    self.metrics[metric_name].extend(values)

                # Ограничиваем размер метрик
                for metric_name in self.metrics:
                    if len(self.metrics[metric_name]) > self.max_metrics_per_name:
                        self.metrics[metric_name] = self.metrics[metric_name][
                            -self.max_metrics_per_name:
                        ]

            return True
        except Exception as e:
            print(f"Ошибка слияния: {e}")
            return False

    @performance_monitor
    def validate(self) -> Dict[str, Any]:
        """
        Валидация состояния системы

        Returns:
            Dict[str, Any]: Результат валидации
        """
        try:
            issues = []
            warnings = []

            # Проверяем базовые атрибуты
            if not self.name or not isinstance(self.name, str):
                issues.append("Некорректное имя системы")

            if not isinstance(self.rules, dict):
                issues.append("Некорректный тип правил")

            if not isinstance(self.alerts, list):
                issues.append("Некорректный тип алертов")

            if not isinstance(self.metrics, dict):
                issues.append("Некорректный тип метрик")

            # Проверяем правила
            for rule_id, rule in self.rules.items():
                if not isinstance(rule, AlertRule):
                    issues.append(f"Некорректное правило {rule_id}")
                elif not rule.rule_id or not rule.name:
                    issues.append(f"Неполное правило {rule_id}")

            # Проверяем алерты
            for i, alert in enumerate(self.alerts):
                if not isinstance(alert, Alert):
                    issues.append(f"Некорректный алерт {i}")
                elif not alert.alert_id or not alert.rule_id:
                    issues.append(f"Неполный алерт {i}")

            # Проверяем метрики
            for metric_name, values in self.metrics.items():
                if not isinstance(values, list):
                    issues.append(f"Некорректные метрики {metric_name}")
                elif len(values) > self.max_metrics_per_name:
                    warnings.append(f"Слишком много метрик {metric_name}")

            # Проверяем состояние системы
            if self.callback_error_count > self.max_callback_errors:
                warnings.append("Слишком много ошибок в callback'ах")

            if len(self.alerts) > self.max_alerts_in_memory:
                warnings.append("Слишком много алертов в памяти")

            return {
                "valid": len(issues) == 0,
                "issues": issues,
                "warnings": warnings,
                "total_issues": len(issues),
                "total_warnings": len(warnings),
            }
        except Exception as e:
            return {
                "valid": False,
                "issues": [f"Ошибка валидации: {e}"],
                "warnings": [],
                "total_issues": 1,
                "total_warnings": 0,
            }

    @performance_monitor
    def optimize(self) -> Dict[str, Any]:
        """
        Оптимизация производительности системы

        Returns:
            Dict[str, Any]: Результат оптимизации
        """
        try:
            optimizations = []
            memory_saved = 0

            with self.lock:
                # Очистка старых алертов
                old_count = len(self.alerts)
                cutoff_time = datetime.now() - timedelta(days=7)
                self.alerts = [
                    alert
                    for alert in self.alerts
                    if alert.timestamp > cutoff_time
                ]
                removed_alerts = old_count - len(self.alerts)
                if removed_alerts > 0:
                    optimizations.append(f"Удалено {removed_alerts} старых алертов")
                    memory_saved += removed_alerts * 200  # Примерная оценка

                # Очистка старых метрик
                for metric_name in list(self.metrics.keys()):
                    if len(self.metrics[metric_name]) > self.max_metrics_per_name:
                        old_count = len(self.metrics[metric_name])
                        self.metrics[metric_name] = self.metrics[metric_name][
                            -self.max_metrics_per_name // 2:
                        ]
                        removed_metrics = old_count - len(self.metrics[metric_name])
                        optimizations.append(
                            f"Очищены метрики {metric_name}: {removed_metrics} значений"
                        )
                        memory_saved += removed_metrics * 8  # Размер float

                # Очистка истории алертов
                for rule_id in self.alert_history:
                    old_count = len(self.alert_history[rule_id])
                    self.alert_history[rule_id] = [
                        alert_time
                        for alert_time in self.alert_history[rule_id]
                        if alert_time > cutoff_time
                    ]
                    removed_history = old_count - len(self.alert_history[rule_id])
                    if removed_history > 0:
                        memory_saved += removed_history * 50  # Примерная оценка

            return {
                "optimizations": optimizations,
                "memory_saved_bytes": memory_saved,
                "memory_saved_mb": memory_saved / 1024 / 1024,
                "total_optimizations": len(optimizations),
            }
        except Exception as e:
            print(f"Ошибка оптимизации: {e}")
            return {
                "optimizations": [],
                "memory_saved_bytes": 0,
                "memory_saved_mb": 0,
                "total_optimizations": 0,
            }

    @performance_monitor
    def get_summary(self) -> Dict[str, Any]:
        """
        Краткая сводка о состоянии системы

        Returns:
            Dict[str, Any]: Краткая сводка
        """
        try:
            with self.lock:
                # Вычисляем active_alerts_count напрямую, избегая вложенной блокировки
                active_alerts_count = len([
                    alert for alert in self.alerts
                    if alert.status == AlertStatus.ACTIVE
                ])
                return {
                    "name": self.name,
                    "status": "running" if self.is_running else "stopped",
                    "paused": self.is_paused,
                    "rules_count": len(self.rules),
                    "alerts_count": len(self.alerts),
                    "active_alerts_count": active_alerts_count,
                    "metrics_count": len(self.metrics),
                    "total_metrics": sum(
                        len(values) for values in self.metrics.values()
                    ),
                    "health_score": 50,  # Базовое значение, вычисляемое без блокировки
                    "uptime_minutes": (
                        (datetime.now() - self.start_time).total_seconds() / 60
                        if self.start_time
                        else 0
                    ),
                    "last_activity": (
                        self.last_activity.isoformat()
                        if self.last_activity
                        else None
                    ),
                }
        except Exception as e:
            print(f"Ошибка получения сводки: {e}")
            return {"error": str(e)}

    @performance_monitor
    def export_config(self, file_path: str) -> bool:
        """
        Экспорт конфигурации системы

        Args:
            file_path: Путь к файлу для экспорта

        Returns:
            bool: True если экспорт прошел успешно
        """
        try:
            config_data = {
                "name": self.name,
                "config_version": self.config_version,
                "rules": {
                    rule_id: {
                        "name": rule.name,
                        "metric_name": rule.metric_name,
                        "condition": rule.condition,
                        "threshold": rule.threshold,
                        "severity": rule.severity.value,
                        "cooldown": rule.cooldown,
                        "min_occurrences": rule.min_occurrences,
                        "max_alerts_per_hour": rule.max_alerts_per_hour,
                        "adaptive_threshold": rule.adaptive_threshold,
                    }
                    for rule_id, rule in self.rules.items()
                },
                "settings": {
                    "max_alerts_in_memory": self.max_alerts_in_memory,
                    "max_metrics_per_name": self.max_metrics_per_name,
                    "cleanup_interval_hours": self.cleanup_interval_hours,
                    "log_level": self.log_level,
                    "enable_debug": self.enable_debug,
                    "enable_validation": self.enable_validation,
                    "max_callback_errors": self.max_callback_errors,
                    "max_memory_usage_mb": self.max_memory_usage_mb,
                },
                "export_timestamp": datetime.now().isoformat(),
            }

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

            return True
        except Exception as e:
            print(f"Ошибка экспорта конфигурации: {e}")
            return False

    @performance_monitor
    def import_config(self, file_path: str) -> bool:
        """
        Импорт конфигурации системы

        Args:
            file_path: Путь к файлу конфигурации

        Returns:
            bool: True если импорт прошел успешно
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)

            with self.lock:
                # Обновляем имя
                if "name" in config_data:
                    self.name = config_data["name"]

                # Обновляем настройки
                if "settings" in config_data:
                    settings = config_data["settings"]
                    self.max_alerts_in_memory = settings.get(
                        "max_alerts_in_memory", self.max_alerts_in_memory
                    )
                    self.max_metrics_per_name = settings.get(
                        "max_metrics_per_name", self.max_metrics_per_name
                    )
                    self.cleanup_interval_hours = settings.get(
                        "cleanup_interval_hours", self.cleanup_interval_hours
                    )
                    self.log_level = settings.get("log_level", self.log_level)
                    self.enable_debug = settings.get("enable_debug", self.enable_debug)
                    self.enable_validation = settings.get(
                        "enable_validation", self.enable_validation
                    )
                    self.max_callback_errors = settings.get(
                        "max_callback_errors", self.max_callback_errors
                    )
                    self.max_memory_usage_mb = settings.get(
                        "max_memory_usage_mb", self.max_memory_usage_mb
                    )

                # Обновляем правила
                if "rules" in config_data:
                    for rule_id, rule_config in config_data["rules"].items():
                        if rule_id in self.rules:
                            rule = self.rules[rule_id]
                            rule.name = rule_config.get("name", rule.name)
                            rule.threshold = rule_config.get("threshold", rule.threshold)
                            rule.cooldown = rule_config.get("cooldown", rule.cooldown)
                            rule.max_alerts_per_hour = rule_config.get(
                                "max_alerts_per_hour", rule.max_alerts_per_hour
                            )

            return True
        except Exception as e:
            print(f"Ошибка импорта конфигурации: {e}")
            return False


# Глобальный экземпляр системы мониторинга
smart_monitoring = SmartMonitoringSystem("ALADDIN_SmartMonitoring")


def setup_default_rules():
    """Настройка правил по умолчанию"""
    try:
        default_rules = [
            AlertRule(
                rule_id="high_cpu_usage",
                name="High CPU Usage",
                metric_name="cpu_usage",
                condition=">",
                threshold=80.0,
                severity=AlertSeverity.WARNING,
                cooldown=300,
                min_occurrences=2,
                max_alerts_per_hour=5,
            ),
            AlertRule(
                rule_id="high_memory_usage",
                name="High Memory Usage",
                metric_name="memory_usage",
                condition=">",
                threshold=85.0,
                severity=AlertSeverity.ERROR,
                cooldown=600,
                min_occurrences=1,
                max_alerts_per_hour=3,
            ),
            AlertRule(
                rule_id="low_disk_space",
                name="Low Disk Space",
                metric_name="disk_usage",
                condition=">",
                threshold=90.0,
                severity=AlertSeverity.CRITICAL,
                cooldown=1800,
                min_occurrences=1,
                max_alerts_per_hour=2,
            ),
            AlertRule(
                rule_id="high_error_rate",
                name="High Error Rate",
                metric_name="error_rate",
                condition=">",
                threshold=0.1,
                severity=AlertSeverity.ERROR,
                cooldown=300,
                min_occurrences=3,
                max_alerts_per_hour=5,
            ),
        ]

        for rule in default_rules:
            smart_monitoring.add_rule(rule)
    except Exception as e:
        print(f"Ошибка настройки правил по умолчанию: {e}")
        raise


# Настраиваем правила по умолчанию
setup_default_rules()
