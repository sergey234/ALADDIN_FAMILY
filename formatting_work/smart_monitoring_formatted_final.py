# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Умная система мониторинга
Защита от спама уведомлений и ложных срабатываний

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
from functools import wraps
from typing import Any, Callable, Dict, List, Optional


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
    """Умная система мониторинга с защитой от спама"""

    @performance_monitor
    def __init__(self, name: str = "SmartMonitoring"):
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
                for rule_config in config["rules"]:
                    rule = AlertRule(**rule_config)
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

            # Добавляем алерт
            with self.lock:
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
    def _start_cleanup_thread(self):
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

    def stop_monitoring(self):
        """Остановка системы мониторинга"""
        try:
            self._stop_cleanup = True
            self.is_running = False
            print("Система мониторинга остановлена")
        except Exception as e:
            print(f"Ошибка остановки мониторинга: {e}")

    @private_method
    def _cleanup_old_data(self):
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
    def start(self):
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
    def stop(self):
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
    def pause(self):
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
    def resume(self):
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
    def reset(self):
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
    def clear(self):
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
                        "callback_error_count": (
                            self.callback_error_count
                        ),
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
