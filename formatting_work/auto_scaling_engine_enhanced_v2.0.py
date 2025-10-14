# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Enhanced Auto Scaling Engine
Улучшенный движок автоматического масштабирования для системы безопасности

Версия: 2.0 Enhanced
Дата: 2025-01-27
Автор: ALADDIN Security Team

Улучшения:
- Async/await поддержка
- Валидация параметров
- Расширенные docstrings
- Улучшенные специальные методы
- Контекстный менеджер
- Кэширование
- Метрики производительности
"""

import asyncio
import json
import logging
import random
import statistics
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from functools import lru_cache
from typing import Any, Dict, List, Optional, Union, Callable, AsyncGenerator

from core.base import ComponentStatus, SecurityBase


class LogLevel(Enum):
    """Уровни логирования"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ScalingError(Exception):
    """Исключение для ошибок масштабирования"""
    pass


class ScalingTrigger(Enum):
    """Триггеры масштабирования"""

    CPU_HIGH = "cpu_high"
    CPU_LOW = "cpu_low"
    MEMORY_HIGH = "memory_high"
    MEMORY_LOW = "memory_low"
    REQUEST_RATE_HIGH = "request_rate_high"
    REQUEST_RATE_LOW = "request_rate_low"
    RESPONSE_TIME_HIGH = "response_time_high"
    RESPONSE_TIME_LOW = "response_time_low"
    QUEUE_SIZE_HIGH = "queue_size_high"
    QUEUE_SIZE_LOW = "queue_size_low"
    CUSTOM = "custom"


class ScalingAction(Enum):
    """Действия масштабирования"""

    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    NO_ACTION = "no_action"
    EMERGENCY_SCALE_UP = "emergency_scale_up"
    EMERGENCY_SCALE_DOWN = "emergency_scale_down"


class ScalingStrategy(Enum):
    """Стратегии масштабирования"""

    CONSERVATIVE = "conservative"
    AGGRESSIVE = "aggressive"
    BALANCED = "balanced"
    PREDICTIVE = "predictive"
    REACTIVE = "reactive"


@dataclass
class MetricData:
    """Данные метрики"""

    metric_name: str
    value: float
    timestamp: datetime
    service_id: str
    node_id: Optional[str] = None
    tags: Optional[Dict[str, str]] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = {}

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


@dataclass
class ScalingRule:
    """Правило масштабирования"""

    rule_id: str
    name: str
    service_id: str
    metric_name: str
    trigger: ScalingTrigger
    threshold: float
    action: ScalingAction
    min_replicas: int
    max_replicas: int
    cooldown_period: int  # секунды
    enabled: bool = True
    created_at: Optional[datetime] = None
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        data = asdict(self)
        data["trigger"] = self.trigger.value
        data["action"] = self.action.value
        data["created_at"] = (
            self.created_at.isoformat() if self.created_at else None
        )
        data["last_triggered"] = (
            self.last_triggered.isoformat() if self.last_triggered else None
        )
        return data


@dataclass
class ScalingDecision:
    """Решение о масштабировании"""

    decision_id: str
    service_id: str
    action: ScalingAction
    current_replicas: int
    target_replicas: int
    reason: str
    confidence: float
    triggered_rules: List[str]
    timestamp: datetime
    metrics_used: List[MetricData]

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        data = asdict(self)
        data["action"] = self.action.value
        data["timestamp"] = self.timestamp.isoformat()
        data["metrics_used"] = [m.to_dict() for m in self.metrics_used]
        return data


@dataclass
class ScalingMetrics:
    """Метрики масштабирования"""

    total_scaling_operations: int = 0
    successful_scaling_operations: int = 0
    failed_scaling_operations: int = 0
    scale_up_operations: int = 0
    scale_down_operations: int = 0
    emergency_operations: int = 0
    average_scaling_time: float = 0.0
    last_scaling_time: Optional[datetime] = None
    active_rules: int = 0
    triggered_rules: int = 0
    false_positives: int = 0
    false_negatives: int = 0

    def __post_init__(self):
        if self.last_scaling_time is None:
            self.last_scaling_time = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        data = asdict(self)
        data["last_scaling_time"] = (
            self.last_scaling_time.isoformat()
            if self.last_scaling_time
            else None
        )
        return data


@dataclass
class PerformanceMetrics:
    """
    Метрики производительности движка.
    
    Attributes:
        average_decision_time (float): Среднее время принятия решения в секундах
        cache_hit_rate (float): Коэффициент попаданий в кэш (0.0-1.0)
        error_rate (float): Коэффициент ошибок (0.0-1.0)
        throughput_per_second (float): Пропускная способность (операций/сек)
        memory_usage_mb (float): Использование памяти в МБ
        cpu_usage_percent (float): Использование CPU в процентах
        active_connections (int): Количество активных соединений
    """
    average_decision_time: float = 0.0
    cache_hit_rate: float = 0.0
    error_rate: float = 0.0
    throughput_per_second: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    active_connections: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return asdict(self)


class AutoScalingEngine(SecurityBase):
    """Движок автоматического масштабирования для ALADDIN Security System"""

    def __init__(self, name: str = "AutoScalingEngine"):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("name должен быть непустой строкой")
        super().__init__(name)

        # Конфигурация движка
        self.monitoring_interval = 30  # секунды
        self.decision_interval = 60  # секунды
        self.metric_retention_hours = 24
        self.default_cooldown = 300  # 5 минут
        self.emergency_threshold = 0.95
        self.prediction_window_minutes = 15

        # Хранилище данных
        self.scaling_rules: Dict[str, ScalingRule] = {}
        self.metric_history: Dict[str, List[MetricData]] = {}
        self.scaling_decisions: List[ScalingDecision] = []
        self.scaling_metrics: ScalingMetrics = ScalingMetrics()
        self.performance_metrics: PerformanceMetrics = PerformanceMetrics()
        self.scaling_lock = threading.RLock()

        # AI компоненты для принятия решений
        self.ai_enabled = True
        self.ml_models = {
            "cpu_predictor": None,
            "memory_predictor": None,
            "load_predictor": None,
            "anomaly_detector": None,
        }

        # Статистика
        self.statistics: Dict[str, Any] = {
            "total_metrics_collected": 0,
            "total_decisions_made": 0,
            "total_rules_triggered": 0,
            "start_time": None,
            "last_metric_collection": None,
            "last_decision": None,
            "average_decision_time": 0.0,
        }

        # Кэш для производительности
        self._cache: Dict[str, Any] = {}
        self._cache_ttl: Dict[str, datetime] = {}

    def __str__(self) -> str:
        """Строковое представление движка"""
        return (f"AutoScalingEngine(name='{self.name}', "
                f"status={self.status.value}, "
                f"rules={len(self.scaling_rules)}, "
                f"ai_enabled={self.ai_enabled})")

    def __repr__(self) -> str:
        """Детальное представление движка"""
        return (f"AutoScalingEngine(name='{self.name}', "
                f"monitoring_interval={self.monitoring_interval}s, "
                f"active_rules={len(self.scaling_rules)}, "
                f"status={self.status.value}, "
                f"ai_enabled={self.ai_enabled})")

    def __len__(self) -> int:
        """Количество активных правил масштабирования"""
        return len(self.scaling_rules)

    def __contains__(self, rule_id: str) -> bool:
        """Проверка наличия правила по ID"""
        if not isinstance(rule_id, str):
            raise TypeError("rule_id должен быть строкой")
        return rule_id in self.scaling_rules

    def __getitem__(self, rule_id: str) -> ScalingRule:
        """Получение правила по ID"""
        if not isinstance(rule_id, str):
            raise TypeError("rule_id должен быть строкой")
        if rule_id not in self.scaling_rules:
            raise KeyError(f"Правило {rule_id} не найдено")
        return self.scaling_rules[rule_id]

    def __iter__(self):
        """Итерация по правилам масштабирования"""
        return iter(self.scaling_rules.values())

    async def __aenter__(self):
        """Асинхронный вход в контекст"""
        await self.initialize_async()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Асинхронный выход из контекста"""
        try:
            await self.stop_async()
            if exc_type:
                # Безопасно обрабатываем exc_val
                if hasattr(exc_val, '__await__'):
                    # Если это корутина, не пытаемся её await
                    error_msg = f"Корутина: {type(exc_val).__name__}"
                else:
                    error_msg = str(exc_val) if exc_val else "Неизвестная ошибка"
                self.log_activity(f"Ошибка в контексте: {error_msg}", "error")
        except Exception as e:
            # Логируем ошибку, но не поднимаем исключение
            self.log_activity(f"Ошибка при выходе из контекста: {e}", "error")

    def initialize(self) -> bool:
        """Инициализация движка автоматического масштабирования"""
        try:
            self.log_activity("Инициализация Auto Scaling Engine", "info")
            self.status = ComponentStatus.RUNNING
            self.statistics["start_time"] = datetime.now()

            # Инициализация AI моделей
            self._initialize_ai_models()

            # Загрузка существующих правил
            self._load_scaling_rules()

            # Запуск фоновых задач
            self._start_background_tasks()

            self.log_activity(
                "Auto Scaling Engine успешно инициализирован", "info"
            )
            return True

        except Exception as e:
            self.log_activity(
                f"Ошибка инициализации Auto Scaling Engine: {e}", "error"
            )
            self.status = ComponentStatus.ERROR
            return False

    def stop(self) -> bool:
        """Остановка движка автоматического масштабирования"""
        try:
            self.log_activity("Остановка Auto Scaling Engine", "info")
            self.status = ComponentStatus.STOPPED

            # Остановка фоновых задач
            self._stop_background_tasks()

            # Сохранение состояния
            self._save_scaling_state()

            # Очистка данных
            with self.scaling_lock:
                self.scaling_rules.clear()
                self.metric_history.clear()
                self.scaling_decisions.clear()

            self.log_activity("Auto Scaling Engine остановлен", "info")
            return True

        except Exception as e:
            self.log_activity(
                f"Ошибка остановки Auto Scaling Engine: {e}", "error"
            )
            return False

    def add_scaling_rule(self, rule: ScalingRule) -> bool:
        """Добавление правила масштабирования"""
        if not isinstance(rule, ScalingRule):
            raise TypeError("rule должен быть экземпляром ScalingRule")
        try:
            with self.scaling_lock:
                if rule.rule_id in self.scaling_rules:
                    raise ValueError(f"Правило с ID {rule.rule_id} уже существует")
                self.scaling_rules[rule.rule_id] = rule
                self.scaling_metrics.active_rules = len(self.scaling_rules)

                self.log_activity(
                    f"Правило масштабирования {rule.name} добавлено", "info"
                )
                return True

        except Exception as e:
            self.log_activity(
                f"Ошибка добавления правила масштабирования: {e}", "error"
            )
            return False

    def remove_scaling_rule(self, rule_id: str) -> bool:
        """Удаление правила масштабирования"""
        if not isinstance(rule_id, str) or not rule_id.strip():
            raise TypeError("rule_id должен быть непустой строкой")
        try:
            with self.scaling_lock:
                if rule_id in self.scaling_rules:
                    rule = self.scaling_rules[rule_id]
                    del self.scaling_rules[rule_id]
                    self.scaling_metrics.active_rules = len(self.scaling_rules)

                    self.log_activity(
                        f"Правило масштабирования {rule.name} удалено", "info"
                    )
                    return True
                else:
                    raise ValueError(f"Правило {rule_id} не найдено")

        except Exception as e:
            self.log_activity(
                f"Ошибка удаления правила масштабирования: {e}", "error"
            )
            return False

    def collect_metric(self, metric: MetricData) -> bool:
        """Сбор метрики"""
        if not isinstance(metric, MetricData):
            raise TypeError("metric должен быть экземпляром MetricData")
        try:
            if not self._validate_metric(metric):
                return False
            with self.scaling_lock:
                service_key = f"{metric.service_id}_{metric.metric_name}"

                if service_key not in self.metric_history:
                    self.metric_history[service_key] = []

                self.metric_history[service_key].append(metric)

                # Ограничиваем историю
                cutoff_time = datetime.now() - timedelta(
                    hours=self.metric_retention_hours
                )
                self.metric_history[service_key] = [
                    m
                    for m in self.metric_history[service_key]
                    if m.timestamp > cutoff_time
                ]

                self.statistics["total_metrics_collected"] += 1
                self.statistics["last_metric_collection"] = datetime.now()

                return True

        except Exception as e:
            self.log_activity(f"Ошибка сбора метрики: {e}", "error")
            return False

    def make_scaling_decision(
        self, service_id: str
    ) -> Optional[ScalingDecision]:
        """Принятие решения о масштабировании"""
        if not isinstance(service_id, str) or not service_id.strip():
            raise ValueError("service_id должен быть непустой строкой")
        try:
            with self.scaling_lock:
                start_time = time.time()

                # Получаем правила для сервиса
                service_rules = [
                    r
                    for r in self.scaling_rules.values()
                    if r.service_id == service_id and r.enabled
                ]
                if not service_rules:
                    return None

                # Собираем метрики для сервиса
                service_metrics = self._get_service_metrics(service_id)
                if not service_metrics:
                    return None

                # Анализируем правила
                triggered_rules = []
                scaling_actions = []
                confidence_scores = []

                for rule in service_rules:
                    if self._evaluate_rule(rule, service_metrics):
                        triggered_rules.append(rule.rule_id)
                        scaling_actions.append(rule.action)
                        confidence_scores.append(
                            self._calculate_confidence(rule, service_metrics)
                        )

                        # Обновляем статистику правила
                        rule.last_triggered = datetime.now()
                        rule.trigger_count += 1
                        self.scaling_metrics.triggered_rules += 1

                if not triggered_rules:
                    return None

                # Принимаем финальное решение
                decision = self._make_final_decision(
                    service_id,
                    scaling_actions,
                    confidence_scores,
                    triggered_rules,
                    service_metrics,
                )

                if decision:
                    self.scaling_decisions.append(decision)
                    self.statistics["total_decisions_made"] += 1
                    self.statistics["last_decision"] = datetime.now()

                    # Обновляем время принятия решения
                    decision_time = time.time() - start_time
                    self.statistics["average_decision_time"] = (
                        self.statistics["average_decision_time"]
                        * (self.statistics["total_decisions_made"] - 1)
                        + decision_time
                    ) / self.statistics["total_decisions_made"]

                return decision

        except Exception as e:
            self.log_activity(
                f"Ошибка принятия решения о масштабировании: {e}", "error"
            )
            return None

    def get_scaling_rules(
        self, service_id: Optional[str] = None
    ) -> List[ScalingRule]:
        """Получение правил масштабирования"""
        try:
            with self.scaling_lock:
                if service_id:
                    return [
                        r
                        for r in self.scaling_rules.values()
                        if r.service_id == service_id
                    ]
                return list(self.scaling_rules.values())
        except Exception as e:
            self.log_activity(
                f"Ошибка получения правил масштабирования: {e}", "error"
            )
            return []

    def get_scaling_decisions(
        self, service_id: Optional[str] = None, limit: int = 100
    ) -> List[ScalingDecision]:
        """Получение решений о масштабировании"""
        try:
            with self.scaling_lock:
                decisions = self.scaling_decisions
                if service_id:
                    decisions = [
                        d for d in decisions if d.service_id == service_id
                    ]

                # Сортируем по времени (новые сначала)
                decisions.sort(key=lambda x: x.timestamp, reverse=True)
                return decisions[:limit]
        except Exception as e:
            self.log_activity(
                f"Ошибка получения решений о масштабировании: {e}", "error"
            )
            return []

    def get_scaling_metrics(self) -> ScalingMetrics:
        """Получение метрик масштабирования"""
        try:
            with self.scaling_lock:
                return self.scaling_metrics
        except Exception as e:
            self.log_activity(
                f"Ошибка получения метрик масштабирования: {e}", "error"
            )
            return ScalingMetrics()

    def get_engine_status(self) -> Dict[str, Any]:
        """Получение статуса движка"""
        try:
            with self.scaling_lock:
                return {
                    "status": self.status.value,
                    "active_rules": len(self.scaling_rules),
                    "total_metrics": sum(
                        len(metrics)
                        for metrics in self.metric_history.values()
                    ),
                    "total_decisions": len(self.scaling_decisions),
                    "metrics": self.scaling_metrics.to_dict(),
                    "statistics": self.statistics,
                    "ai_enabled": self.ai_enabled,
                    "monitoring_interval": self.monitoring_interval,
                    "decision_interval": self.decision_interval,
                }
        except Exception as e:
            self.log_activity(f"Ошибка получения статуса движка: {e}", "error")
            return {}

    def _initialize_ai_models(self):
        """Инициализация AI моделей"""
        try:
            # Симуляция инициализации AI моделей
            self.log_activity("AI модели инициализированы", "info")
        except Exception as e:
            self.log_activity(f"Ошибка инициализации AI моделей: {e}", "error")

    def _load_scaling_rules(self):
        """Загрузка правил масштабирования"""
        try:
            # Создание тестовых правил
            default_rules = [
                ScalingRule(
                    rule_id="cpu_scale_up",
                    name="CPU Scale Up",
                    service_id="threat-detection",
                    metric_name="cpu_usage",
                    trigger=ScalingTrigger.CPU_HIGH,
                    threshold=0.8,
                    action=ScalingAction.SCALE_UP,
                    min_replicas=1,
                    max_replicas=10,
                    cooldown_period=300,
                ),
                ScalingRule(
                    rule_id="cpu_scale_down",
                    name="CPU Scale Down",
                    service_id="threat-detection",
                    metric_name="cpu_usage",
                    trigger=ScalingTrigger.CPU_LOW,
                    threshold=0.3,
                    action=ScalingAction.SCALE_DOWN,
                    min_replicas=1,
                    max_replicas=10,
                    cooldown_period=600,
                ),
                ScalingRule(
                    rule_id="memory_scale_up",
                    name="Memory Scale Up",
                    service_id="threat-detection",
                    metric_name="memory_usage",
                    trigger=ScalingTrigger.MEMORY_HIGH,
                    threshold=0.85,
                    action=ScalingAction.SCALE_UP,
                    min_replicas=1,
                    max_replicas=10,
                    cooldown_period=300,
                ),
            ]

            for rule in default_rules:
                self.scaling_rules[rule.rule_id] = rule

            self.scaling_metrics.active_rules = len(self.scaling_rules)
            self.log_activity(
                f"Загружено {len(default_rules)} правил масштабирования",
                "info",
            )
        except Exception as e:
            self.log_activity(
                f"Ошибка загрузки правил масштабирования: {e}", "error"
            )

    def _start_background_tasks(self):
        """Запуск фоновых задач"""
        try:
            # Запуск задачи мониторинга метрик
            monitoring_thread = threading.Thread(
                target=self._monitoring_task, daemon=True
            )
            monitoring_thread.start()

            # Запуск задачи принятия решений
            decision_thread = threading.Thread(
                target=self._decision_task, daemon=True
            )
            decision_thread.start()

            self.log_activity("Фоновые задачи запущены", "info")
        except Exception as e:
            self.log_activity(f"Ошибка запуска фоновых задач: {e}", "error")

    def _stop_background_tasks(self):
        """Остановка фоновых задач"""
        try:
            # Фоновые задачи остановятся автоматически при остановке движка
            self.log_activity("Фоновые задачи остановлены", "info")
        except Exception as e:
            self.log_activity(f"Ошибка остановки фоновых задач: {e}", "error")

    def _get_service_metrics(self, service_id: str) -> List[MetricData]:
        """Получение метрик сервиса"""
        try:
            metrics = []
            for key, metric_list in self.metric_history.items():
                if key.startswith(f"{service_id}_"):
                    # Берем последние метрики
                    recent_metrics = (
                        metric_list[-10:]
                        if len(metric_list) > 10
                        else metric_list
                    )
                    metrics.extend(recent_metrics)
            return metrics
        except Exception as e:
            self.log_activity(f"Ошибка получения метрик сервиса: {e}", "error")
            return []

    def _evaluate_rule(
        self, rule: ScalingRule, metrics: List[MetricData]
    ) -> bool:
        """Оценка правила"""
        try:
            # Проверяем период охлаждения
            if rule.last_triggered:
                time_since_trigger = datetime.now() - rule.last_triggered
                if time_since_trigger.total_seconds() < rule.cooldown_period:
                    return False

            # Фильтруем метрики по имени
            rule_metrics = [
                m for m in metrics if m.metric_name == rule.metric_name
            ]
            if not rule_metrics:
                return False

            # Получаем последнее значение
            latest_metric = max(rule_metrics, key=lambda x: x.timestamp)
            current_value = latest_metric.value

            # Проверяем условие
            if (
                rule.trigger == ScalingTrigger.CPU_HIGH
                and current_value > rule.threshold
            ):
                return True
            elif (
                rule.trigger == ScalingTrigger.CPU_LOW
                and current_value < rule.threshold
            ):
                return True
            elif (
                rule.trigger == ScalingTrigger.MEMORY_HIGH
                and current_value > rule.threshold
            ):
                return True
            elif (
                rule.trigger == ScalingTrigger.MEMORY_LOW
                and current_value < rule.threshold
            ):
                return True

            return False

        except Exception as e:
            self.log_activity(f"Ошибка оценки правила: {e}", "error")
            return False

    def _calculate_confidence(
        self, rule: ScalingRule, metrics: List[MetricData]
    ) -> float:
        """Расчет уверенности в решении"""
        try:
            # Базовая уверенность
            base_confidence = 0.7

            # Увеличиваем уверенность если правило срабатывало много раз
            if rule.trigger_count > 10:
                base_confidence += 0.1

            # Увеличиваем уверенность если метрика стабильна
            rule_metrics = [
                m for m in metrics if m.metric_name == rule.metric_name
            ]
            if len(rule_metrics) > 5:
                values = [m.value for m in rule_metrics[-5:]]
                if statistics.stdev(values) < 0.1:  # Низкая вариативность
                    base_confidence += 0.1

            return min(base_confidence, 1.0)

        except Exception as e:
            self.log_activity(f"Ошибка расчета уверенности: {e}", "error")
            return 0.5

    def _make_final_decision(
        self,
        service_id: str,
        actions: List[ScalingAction],
        confidence_scores: List[float],
        triggered_rules: List[str],
        metrics: List[MetricData],
    ) -> Optional[ScalingDecision]:
        """Принятие финального решения"""
        try:
            if not actions:
                return None

            # Определяем доминирующее действие
            action_counts: Dict[ScalingAction, int] = {}
            for action in actions:
                action_counts[action] = action_counts.get(action, 0) + 1

            # Выбираем действие с наибольшим количеством голосов
            final_action = max(action_counts, key=lambda x: action_counts[x])

            # Рассчитываем среднюю уверенность
            avg_confidence = (
                statistics.mean(confidence_scores)
                if confidence_scores
                else 0.5
            )

            # Определяем целевое количество реплик
            current_replicas = 3  # Симуляция текущего количества
            target_replicas = self._calculate_target_replicas(
                service_id, final_action, current_replicas, avg_confidence
            )

            # Создаем решение
            decision = ScalingDecision(
                decision_id=f"decision-{int(time.time() * 1000)}",
                service_id=service_id,
                action=final_action,
                current_replicas=current_replicas,
                target_replicas=target_replicas,
                reason=(
                    f"Triggered by {len(triggered_rules)} rules with "
                    f"{avg_confidence:.2f} confidence"
                ),
                confidence=avg_confidence,
                triggered_rules=triggered_rules,
                timestamp=datetime.now(),
                metrics_used=metrics[-5:],  # Последние 5 метрик
            )

            return decision

        except Exception as e:
            self.log_activity(
                f"Ошибка принятия финального решения: {e}", "error"
            )
            return None

    def _calculate_target_replicas(
        self,
        service_id: str,
        action: ScalingAction,
        current_replicas: int,
        confidence: float,
    ) -> int:
        """Расчет целевого количества реплик"""
        try:
            if action == ScalingAction.SCALE_UP:
                # Консервативное увеличение
                increase = max(1, int(current_replicas * 0.5 * confidence))
                return min(current_replicas + increase, 10)
            elif action == ScalingAction.SCALE_DOWN:
                # Осторожное уменьшение
                decrease = max(1, int(current_replicas * 0.3 * confidence))
                return max(current_replicas - decrease, 1)
            elif action == ScalingAction.EMERGENCY_SCALE_UP:
                # Экстренное увеличение
                return min(current_replicas * 2, 10)
            elif action == ScalingAction.EMERGENCY_SCALE_DOWN:
                # Экстренное уменьшение
                return max(current_replicas // 2, 1)
            else:
                return current_replicas

        except Exception as e:
            self.log_activity(f"Ошибка расчета целевых реплик: {e}", "error")
            return current_replicas

    def _monitoring_task(self):
        """Задача мониторинга метрик"""
        try:
            while self.status == ComponentStatus.RUNNING:
                time.sleep(self.monitoring_interval)

                # Симуляция сбора метрик
                self._simulate_metric_collection()

        except Exception as e:
            self.log_activity(f"Ошибка задачи мониторинга: {e}", "error")

    def _decision_task(self):
        """Задача принятия решений"""
        try:
            while self.status == ComponentStatus.RUNNING:
                time.sleep(self.decision_interval)

                # Принимаем решения для всех сервисов
                service_ids = set(
                    rule.service_id for rule in self.scaling_rules.values()
                )
                for service_id in service_ids:
                    decision = self.make_scaling_decision(service_id)
                    if decision:
                        self.log_activity(
                            f"Принято решение о масштабировании {service_id}: "
                            f"{decision.action.value} до "
                            f"{decision.target_replicas} реплик",
                            "info",
                        )

        except Exception as e:
            self.log_activity(f"Ошибка задачи принятия решений: {e}", "error")

    def _simulate_metric_collection(self):
        """Симуляция сбора метрик"""
        try:
            # Симуляция метрик для тестовых сервисов
            services = [
                "threat-detection",
                "performance-optimization",
                "api-gateway",
            ]

            for service_id in services:
                # CPU метрика
                cpu_metric = MetricData(
                    metric_name="cpu_usage",
                    value=random.uniform(0.1, 0.9),
                    timestamp=datetime.now(),
                    service_id=service_id,
                    tags={"node": f"node-{random.randint(1, 3)}"},
                )
                self.collect_metric(cpu_metric)

                # Memory метрика
                memory_metric = MetricData(
                    metric_name="memory_usage",
                    value=random.uniform(0.2, 0.8),
                    timestamp=datetime.now(),
                    service_id=service_id,
                    tags={"node": f"node-{random.randint(1, 3)}"},
                )
                self.collect_metric(memory_metric)

        except Exception as e:
            self.log_activity(f"Ошибка симуляции сбора метрик: {e}", "error")

    def _save_scaling_state(self):
        """Сохранение состояния масштабирования"""
        try:
            import os

            os.makedirs("/tmp/aladdin_scaling", exist_ok=True)

            data_to_save = {
                "rules": {
                    k: v.to_dict() for k, v in self.scaling_rules.items()
                },
                "decisions": [
                    d.to_dict() for d in self.scaling_decisions[-100:]
                ],  # Последние 100
                "metrics": self.scaling_metrics.to_dict(),
                "statistics": self.statistics,
                "saved_at": datetime.now().isoformat(),
            }

            with open(
                "/tmp/aladdin_scaling/last_state.json", "w", encoding="utf-8"
            ) as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)

            self.log_activity("Состояние масштабирования сохранено", "info")
        except Exception as e:
            self.log_activity(
                f"Ошибка сохранения состояния масштабирования: {e}", "error"
            )

    # Асинхронные методы
    async def initialize_async(self) -> bool:
        """Асинхронная инициализация движка"""
        try:
            await self._log_async("Инициализация Auto Scaling Engine", LogLevel.INFO)
            self.status = ComponentStatus.RUNNING
            self.statistics["start_time"] = datetime.now()
            await self._initialize_ai_models_async()
            await self._load_scaling_rules_async()
            await self._start_background_tasks_async()
            await self._log_async("Auto Scaling Engine успешно инициализирован", LogLevel.INFO)
            return True
        except Exception as e:
            await self._log_async(f"Ошибка инициализации: {e}", LogLevel.ERROR)
            self.status = ComponentStatus.ERROR
            raise ScalingError(f"Ошибка инициализации: {e}") from e

    async def stop_async(self) -> bool:
        """Асинхронная остановка движка"""
        try:
            await self._log_async("Остановка Auto Scaling Engine", LogLevel.INFO)
            self.status = ComponentStatus.STOPPED
            await self._stop_background_tasks_async()
            await self._save_scaling_state_async()
            with self.scaling_lock:
                self.scaling_rules.clear()
                self.metric_history.clear()
                self.scaling_decisions.clear()
            await self._log_async("Auto Scaling Engine остановлен", LogLevel.INFO)
            return True
        except Exception as e:
            await self._log_async(f"Ошибка остановки: {e}", LogLevel.ERROR)
            return False

    async def add_scaling_rule_async(self, rule: ScalingRule) -> bool:
        """Асинхронное добавление правила масштабирования"""
        if not isinstance(rule, ScalingRule):
            raise TypeError("rule должен быть экземпляром ScalingRule")
        try:
            with self.scaling_lock:
                if rule.rule_id in self.scaling_rules:
                    raise ValueError(f"Правило с ID {rule.rule_id} уже существует")
                self.scaling_rules[rule.rule_id] = rule
                self.scaling_metrics.active_rules = len(self.scaling_rules)
                await self._log_async(f"Правило {rule.name} добавлено", LogLevel.INFO)
                return True
        except Exception as e:
            await self._log_async(f"Ошибка добавления правила: {e}", LogLevel.ERROR)
            return False

    async def remove_scaling_rule_async(self, rule_id: str) -> bool:
        """Асинхронное удаление правила масштабирования"""
        if not isinstance(rule_id, str) or not rule_id.strip():
            raise TypeError("rule_id должен быть непустой строкой")
        try:
            with self.scaling_lock:
                if rule_id not in self.scaling_rules:
                    raise ValueError(f"Правило {rule_id} не найдено")
                rule = self.scaling_rules[rule_id]
                del self.scaling_rules[rule_id]
                self.scaling_metrics.active_rules = len(self.scaling_rules)
                await self._log_async(f"Правило {rule.name} удалено", LogLevel.INFO)
                return True
        except Exception as e:
            await self._log_async(f"Ошибка удаления правила: {e}", LogLevel.ERROR)
            return False

    async def collect_metric_async(self, metric: MetricData) -> bool:
        """Асинхронный сбор метрики с валидацией"""
        if not isinstance(metric, MetricData):
            raise TypeError("metric должен быть экземпляром MetricData")
        try:
            if not self._validate_metric(metric):
                return False
            with self.scaling_lock:
                service_key = f"{metric.service_id}_{metric.metric_name}"
                if service_key not in self.metric_history:
                    self.metric_history[service_key] = []
                self.metric_history[service_key].append(metric)
                cutoff_time = datetime.now() - timedelta(hours=self.metric_retention_hours)
                self.metric_history[service_key] = [
                    m for m in self.metric_history[service_key]
                    if m.timestamp > cutoff_time
                ]
                self.statistics["total_metrics_collected"] += 1
                self.statistics["last_metric_collection"] = datetime.now()
                self._invalidate_cache(f"metrics_{service_key}")
                return True
        except Exception as e:
            await self._log_async(f"Ошибка сбора метрики: {e}", LogLevel.ERROR)
            return False

    async def make_scaling_decision_async(self, service_id: str, force_decision: bool = False, confidence_threshold: float = 0.7) -> Optional[ScalingDecision]:
        """Асинхронное принятие решения о масштабировании"""
        if not isinstance(service_id, str) or not service_id.strip():
            raise ValueError("service_id должен быть непустой строкой")
        if not isinstance(force_decision, bool):
            raise TypeError("force_decision должен быть булевым значением")
        if not isinstance(confidence_threshold, (int, float)) or not (0.0 <= confidence_threshold <= 1.0):
            raise ValueError("confidence_threshold должен быть числом от 0.0 до 1.0")
        try:
            with self.scaling_lock:
                start_time = time.time()
                service_rules = [r for r in self.scaling_rules.values() if r.service_id == service_id and r.enabled]
                if not service_rules:
                    await self._log_async(f"Нет правил для сервиса {service_id}", LogLevel.WARNING)
                    return None
                service_metrics = await self._get_service_metrics_async(service_id)
                if not service_metrics:
                    await self._log_async(f"Нет метрик для сервиса {service_id}", LogLevel.WARNING)
                    return None
                triggered_rules = []
                scaling_actions = []
                confidence_scores = []
                for rule in service_rules:
                    if await self._evaluate_rule_async(rule, service_metrics):
                        triggered_rules.append(rule.rule_id)
                        scaling_actions.append(rule.action)
                        confidence_scores.append(await self._calculate_confidence_async(rule, service_metrics))
                        rule.last_triggered = datetime.now()
                        rule.trigger_count += 1
                        self.scaling_metrics.triggered_rules += 1
                if not triggered_rules:
                    await self._log_async(f"Нет сработавших правил для сервиса {service_id}", LogLevel.DEBUG)
                    return None
                decision = await self._make_final_decision_async(service_id, scaling_actions, confidence_scores, triggered_rules, service_metrics, force_decision, confidence_threshold)
                if decision:
                    self.scaling_decisions.append(decision)
                    self.statistics["total_decisions_made"] += 1
                    self.statistics["last_decision"] = datetime.now()
                    decision_time = time.time() - start_time
                    self.statistics["average_decision_time"] = (self.statistics["average_decision_time"] * (self.statistics["total_decisions_made"] - 1) + decision_time) / self.statistics["total_decisions_made"]
                    self.performance_metrics.average_decision_time = self.statistics["average_decision_time"]
                return decision
        except Exception as e:
            await self._log_async(f"Ошибка принятия решения: {e}", LogLevel.ERROR)
            raise ScalingError(f"Ошибка принятия решения: {e}") from e

    # Вспомогательные асинхронные методы
    async def _log_async(self, message: str, level: LogLevel = LogLevel.INFO) -> None:
        """Асинхронное логирование"""
        try:
            log_message = f"[{self.name}] {message}"
            if level == LogLevel.DEBUG:
                logging.debug(log_message)
            elif level == LogLevel.INFO:
                logging.info(log_message)
            elif level == LogLevel.WARNING:
                logging.warning(log_message)
            elif level == LogLevel.ERROR:
                logging.error(log_message)
            elif level == LogLevel.CRITICAL:
                logging.critical(log_message)
            self.log_activity(message, level.value)
        except Exception as e:
            self.log_activity(f"Ошибка логирования: {e}", "error")

    async def _initialize_ai_models_async(self) -> None:
        """Асинхронная инициализация AI моделей"""
        try:
            await self._log_async("Инициализация AI моделей", LogLevel.INFO)
            await asyncio.sleep(0.1)
            self.ml_models = {
                "cpu_predictor": "initialized",
                "memory_predictor": "initialized",
                "load_predictor": "initialized",
                "anomaly_detector": "initialized",
            }
            await self._log_async("AI модели инициализированы", LogLevel.INFO)
        except Exception as e:
            await self._log_async(f"Ошибка инициализации AI моделей: {e}", LogLevel.ERROR)

    async def _load_scaling_rules_async(self) -> None:
        """Асинхронная загрузка правил масштабирования"""
        try:
            await self._log_async("Загрузка правил масштабирования", LogLevel.INFO)
            default_rules = [
                ScalingRule(
                    rule_id="cpu_scale_up",
                    name="CPU Scale Up",
                    service_id="threat-detection",
                    metric_name="cpu_usage",
                    trigger=ScalingTrigger.CPU_HIGH,
                    threshold=0.8,
                    action=ScalingAction.SCALE_UP,
                    min_replicas=1,
                    max_replicas=10,
                    cooldown_period=300,
                ),
                ScalingRule(
                    rule_id="cpu_scale_down",
                    name="CPU Scale Down",
                    service_id="threat-detection",
                    metric_name="cpu_usage",
                    trigger=ScalingTrigger.CPU_LOW,
                    threshold=0.3,
                    action=ScalingAction.SCALE_DOWN,
                    min_replicas=1,
                    max_replicas=10,
                    cooldown_period=600,
                ),
            ]
            for rule in default_rules:
                if self._validate_rule(rule):
                    self.scaling_rules[rule.rule_id] = rule
            self.scaling_metrics.active_rules = len(self.scaling_rules)
            await self._log_async(f"Загружено {len(default_rules)} правил масштабирования", LogLevel.INFO)
        except Exception as e:
            await self._log_async(f"Ошибка загрузки правил: {e}", LogLevel.ERROR)

    async def _start_background_tasks_async(self) -> None:
        """Асинхронный запуск фоновых задач"""
        try:
            await self._log_async("Запуск фоновых задач", LogLevel.INFO)
            asyncio.create_task(self._monitoring_task_async())
            asyncio.create_task(self._decision_task_async())
            await self._log_async("Фоновые задачи запущены", LogLevel.INFO)
        except Exception as e:
            await self._log_async(f"Ошибка запуска фоновых задач: {e}", LogLevel.ERROR)

    async def _stop_background_tasks_async(self) -> None:
        """Асинхронная остановка фоновых задач"""
        try:
            await self._log_async("Остановка фоновых задач", LogLevel.INFO)
            await self._log_async("Фоновые задачи остановлены", LogLevel.INFO)
        except Exception as e:
            await self._log_async(f"Ошибка остановки фоновых задач: {e}", LogLevel.ERROR)

    async def _get_service_metrics_async(self, service_id: str) -> List[MetricData]:
        """Асинхронное получение метрик сервиса"""
        try:
            cache_key = self._get_cache_key("service_metrics", service_id)
            if self._is_cache_valid(cache_key, ttl_seconds=60):
                return self._cache.get(cache_key, [])
            metrics = []
            for key, metric_list in self.metric_history.items():
                if key.startswith(f"{service_id}_"):
                    recent_metrics = metric_list[-10:] if len(metric_list) > 10 else metric_list
                    metrics.extend(recent_metrics)
            self._cache[cache_key] = metrics
            self._cache_ttl[cache_key] = datetime.now()
            return metrics
        except Exception as e:
            await self._log_async(f"Ошибка получения метрик сервиса: {e}", LogLevel.ERROR)
            return []

    async def _evaluate_rule_async(self, rule: ScalingRule, metrics: List[MetricData]) -> bool:
        """Асинхронная оценка правила масштабирования"""
        try:
            if rule.last_triggered:
                time_since_trigger = datetime.now() - rule.last_triggered
                if time_since_trigger.total_seconds() < rule.cooldown_period:
                    return False
            rule_metrics = [m for m in metrics if m.metric_name == rule.metric_name]
            if not rule_metrics:
                return False
            latest_metric = max(rule_metrics, key=lambda x: x.timestamp)
            current_value = latest_metric.value
            if rule.trigger == ScalingTrigger.CPU_HIGH and current_value > rule.threshold:
                return True
            elif rule.trigger == ScalingTrigger.CPU_LOW and current_value < rule.threshold:
                return True
            elif rule.trigger == ScalingTrigger.MEMORY_HIGH and current_value > rule.threshold:
                return True
            elif rule.trigger == ScalingTrigger.MEMORY_LOW and current_value < rule.threshold:
                return True
            return False
        except Exception as e:
            await self._log_async(f"Ошибка оценки правила: {e}", LogLevel.ERROR)
            return False

    async def _calculate_confidence_async(self, rule: ScalingRule, metrics: List[MetricData]) -> float:
        """Асинхронный расчет уверенности в решении"""
        try:
            base_confidence = 0.7
            if rule.trigger_count > 10:
                base_confidence += 0.1
            rule_metrics = [m for m in metrics if m.metric_name == rule.metric_name]
            if len(rule_metrics) > 5:
                values = [m.value for m in rule_metrics[-5:]]
                if statistics.stdev(values) < 0.1:
                    base_confidence += 0.1
            return min(base_confidence, 1.0)
        except Exception as e:
            await self._log_async(f"Ошибка расчета уверенности: {e}", LogLevel.ERROR)
            return 0.5

    async def _make_final_decision_async(self, service_id: str, actions: List[ScalingAction], confidence_scores: List[float], triggered_rules: List[str], metrics: List[MetricData], force_decision: bool = False, confidence_threshold: float = 0.7) -> Optional[ScalingDecision]:
        """Асинхронное принятие финального решения о масштабировании"""
        try:
            if not actions:
                return None
            avg_confidence = statistics.mean(confidence_scores) if confidence_scores else 0.5
            if not force_decision and avg_confidence < confidence_threshold:
                await self._log_async(f"Низкая уверенность {avg_confidence:.2f} < {confidence_threshold}", LogLevel.DEBUG)
                return None
            action_counts: Dict[ScalingAction, int] = {}
            for action in actions:
                action_counts[action] = action_counts.get(action, 0) + 1
            final_action = max(action_counts, key=lambda x: action_counts[x])
            current_replicas = 3
            target_replicas = await self._calculate_target_replicas_async(service_id, final_action, current_replicas, avg_confidence)
            decision = ScalingDecision(
                decision_id=f"decision-{int(time.time() * 1000)}",
                service_id=service_id,
                action=final_action,
                current_replicas=current_replicas,
                target_replicas=target_replicas,
                reason=f"Triggered by {len(triggered_rules)} rules with {avg_confidence:.2f} confidence",
                confidence=avg_confidence,
                triggered_rules=triggered_rules,
                timestamp=datetime.now(),
                metrics_used=metrics[-5:],
            )
            return decision
        except Exception as e:
            await self._log_async(f"Ошибка принятия финального решения: {e}", LogLevel.ERROR)
            return None

    async def _calculate_target_replicas_async(self, service_id: str, action: ScalingAction, current_replicas: int, confidence: float) -> int:
        """Асинхронный расчет целевого количества реплик"""
        try:
            if action == ScalingAction.SCALE_UP:
                increase = max(1, int(current_replicas * 0.5 * confidence))
                return min(current_replicas + increase, 10)
            elif action == ScalingAction.SCALE_DOWN:
                decrease = max(1, int(current_replicas * 0.3 * confidence))
                return max(current_replicas - decrease, 1)
            elif action == ScalingAction.EMERGENCY_SCALE_UP:
                return min(current_replicas * 2, 10)
            elif action == ScalingAction.EMERGENCY_SCALE_DOWN:
                return max(current_replicas // 2, 1)
            else:
                return current_replicas
        except Exception as e:
            await self._log_async(f"Ошибка расчета целевых реплик: {e}", LogLevel.ERROR)
            return current_replicas

    async def _monitoring_task_async(self) -> None:
        """Асинхронная задача мониторинга метрик"""
        try:
            while self.status == ComponentStatus.RUNNING:
                await asyncio.sleep(self.monitoring_interval)
                await self._simulate_metric_collection_async()
        except Exception as e:
            await self._log_async(f"Ошибка задачи мониторинга: {e}", LogLevel.ERROR)

    async def _decision_task_async(self) -> None:
        """Асинхронная задача принятия решений"""
        try:
            while self.status == ComponentStatus.RUNNING:
                await asyncio.sleep(self.decision_interval)
                service_ids = set(rule.service_id for rule in self.scaling_rules.values())
                for service_id in service_ids:
                    decision = await self.make_scaling_decision_async(service_id)
                    if decision:
                        await self._log_async(f"Принято решение о масштабировании {service_id}: {decision.action.value} до {decision.target_replicas} реплик", LogLevel.INFO)
        except Exception as e:
            await self._log_async(f"Ошибка задачи принятия решений: {e}", LogLevel.ERROR)

    async def _simulate_metric_collection_async(self) -> None:
        """Асинхронная симуляция сбора метрик"""
        try:
            services = ["threat-detection", "performance-optimization", "api-gateway"]
            for service_id in services:
                cpu_metric = MetricData(
                    metric_name="cpu_usage",
                    value=random.uniform(0.1, 0.9),
                    timestamp=datetime.now(),
                    service_id=service_id,
                    tags={"node": f"node-{random.randint(1, 3)}"},
                )
                await self.collect_metric_async(cpu_metric)
                memory_metric = MetricData(
                    metric_name="memory_usage",
                    value=random.uniform(0.2, 0.8),
                    timestamp=datetime.now(),
                    service_id=service_id,
                    tags={"node": f"node-{random.randint(1, 3)}"},
                )
                await self.collect_metric_async(memory_metric)
        except Exception as e:
            await self._log_async(f"Ошибка симуляции сбора метрик: {e}", LogLevel.ERROR)

    async def _save_scaling_state_async(self) -> None:
        """Асинхронное сохранение состояния масштабирования"""
        try:
            import os
            os.makedirs("/tmp/aladdin_scaling", exist_ok=True)
            
            # Подготовка данных с правильной сериализацией datetime
            statistics_serialized = {}
            for key, value in self.statistics.items():
                if isinstance(value, datetime):
                    statistics_serialized[key] = value.isoformat()
                else:
                    statistics_serialized[key] = value
            
            data_to_save = {
                "rules": {k: v.to_dict() for k, v in self.scaling_rules.items()},
                "decisions": [d.to_dict() for d in self.scaling_decisions[-100:]],
                "metrics": self.scaling_metrics.to_dict(),
                "performance_metrics": self.performance_metrics.to_dict(),
                "statistics": statistics_serialized,
                "saved_at": datetime.now().isoformat(),
            }
            
            with open("/tmp/aladdin_scaling/last_state.json", "w", encoding="utf-8") as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)
            await self._log_async("Состояние масштабирования сохранено", LogLevel.INFO)
        except Exception as e:
            await self._log_async(f"Ошибка сохранения состояния: {e}", LogLevel.ERROR)

    # Валидация
    def _validate_metric(self, metric: MetricData) -> bool:
        """Валидация метрики перед обработкой"""
        try:
            if not isinstance(metric, MetricData):
                return False
            if not (0.0 <= metric.value <= 1.0):
                return False
            if not metric.service_id or not metric.service_id.strip():
                return False
            if not metric.metric_name or not metric.metric_name.strip():
                return False
            return True
        except Exception:
            return False

    def _validate_rule(self, rule: ScalingRule) -> bool:
        """Валидация правила масштабирования"""
        try:
            if not isinstance(rule, ScalingRule):
                return False
            if not rule.rule_id or not rule.rule_id.strip():
                return False
            if not (0.0 <= rule.threshold <= 1.0):
                return False
            if rule.min_replicas < 1 or rule.max_replicas < rule.min_replicas:
                return False
            return True
        except Exception:
            return False

    # Кэширование
    def _get_cache_key(self, prefix: str, *args) -> str:
        """Генерация ключа кэша"""
        return f"{prefix}_{hash(str(args))}"

    def _is_cache_valid(self, key: str, ttl_seconds: int = 300) -> bool:
        """Проверка валидности кэша"""
        if key not in self._cache_ttl:
            return False
        return (datetime.now() - self._cache_ttl[key]).total_seconds() < ttl_seconds

    def _invalidate_cache(self, pattern: str) -> None:
        """Инвалидация кэша по паттерну"""
        keys_to_remove = [k for k in self._cache.keys() if pattern in k]
        for key in keys_to_remove:
            self._cache.pop(key, None)
            self._cache_ttl.pop(key, None)
