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


class ScalingError(Exception):
    """Исключение для ошибок масштабирования"""
    pass


@dataclass
class MetricData:
    """
    Данные метрики для системы масштабирования.
    
    Attributes:
        metric_name (str): Название метрики (например, 'cpu_usage', 'memory_usage')
        value (float): Значение метрики (от 0.0 до 1.0)
        timestamp (datetime): Время сбора метрики
        service_id (str): Идентификатор сервиса
        node_id (Optional[str]): Идентификатор узла (опционально)
        tags (Optional[Dict[str, str]]): Дополнительные теги метрики
    
    Example:
        >>> metric = MetricData(
        ...     metric_name="cpu_usage",
        ...     value=0.75,
        ...     timestamp=datetime.now(),
        ...     service_id="my-service"
        ... )
    """
    metric_name: str
    value: float
    timestamp: datetime
    service_id: str
    node_id: Optional[str] = None
    tags: Optional[Dict[str, str]] = None

    def __post_init__(self):
        """Пост-инициализация с валидацией"""
        if self.tags is None:
            self.tags = {}
        self._validate()

    def _validate(self) -> None:
        """Валидация данных метрики"""
        if not isinstance(self.metric_name, str) or not self.metric_name.strip():
            raise ValueError("metric_name должен быть непустой строкой")
        
        if not isinstance(self.value, (int, float)) or not (0.0 <= self.value <= 1.0):
            raise ValueError("value должен быть числом от 0.0 до 1.0")
        
        if not isinstance(self.service_id, str) or not self.service_id.strip():
            raise ValueError("service_id должен быть непустой строкой")
        
        if self.node_id is not None and not isinstance(self.node_id, str):
            raise ValueError("node_id должен быть строкой или None")
        
        if not isinstance(self.tags, dict):
            raise ValueError("tags должен быть словарем")

    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразование в словарь для сериализации.
        
        Returns:
            Dict[str, Any]: Словарь с данными метрики
        """
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data

    def __str__(self) -> str:
        """Строковое представление метрики"""
        return f"MetricData({self.metric_name}={self.value:.2f}, service={self.service_id})"

    def __repr__(self) -> str:
        """Детальное представление метрики"""
        return (f"MetricData(metric_name='{self.metric_name}', value={self.value}, "
                f"timestamp={self.timestamp}, service_id='{self.service_id}', "
                f"node_id={self.node_id}, tags={self.tags})")


@dataclass
class ScalingRule:
    """
    Правило масштабирования для автоматического управления ресурсами.
    
    Attributes:
        rule_id (str): Уникальный идентификатор правила
        name (str): Человекочитаемое название правила
        service_id (str): Идентификатор сервиса
        metric_name (str): Название метрики для мониторинга
        trigger (ScalingTrigger): Условие срабатывания
        threshold (float): Пороговое значение (от 0.0 до 1.0)
        action (ScalingAction): Действие при срабатывании
        min_replicas (int): Минимальное количество реплик
        max_replicas (int): Максимальное количество реплик
        cooldown_period (int): Период охлаждения в секундах
        enabled (bool): Включено ли правило
        created_at (Optional[datetime]): Время создания
        last_triggered (Optional[datetime]): Время последнего срабатывания
        trigger_count (int): Количество срабатываний
    
    Example:
        >>> rule = ScalingRule(
        ...     rule_id="cpu_scale_up",
        ...     name="CPU Scale Up",
        ...     service_id="my-service",
        ...     metric_name="cpu_usage",
        ...     trigger=ScalingTrigger.CPU_HIGH,
        ...     threshold=0.8,
        ...     action=ScalingAction.SCALE_UP,
        ...     min_replicas=1,
        ...     max_replicas=10,
        ...     cooldown_period=300
        ... )
    """
    rule_id: str
    name: str
    service_id: str
    metric_name: str
    trigger: ScalingTrigger
    threshold: float
    action: ScalingAction
    min_replicas: int
    max_replicas: int
    cooldown_period: int
    enabled: bool = True
    created_at: Optional[datetime] = None
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0

    def __post_init__(self):
        """Пост-инициализация с валидацией"""
        if self.created_at is None:
            self.created_at = datetime.now()
        self._validate()

    def _validate(self) -> None:
        """Валидация данных правила"""
        if not isinstance(self.rule_id, str) or not self.rule_id.strip():
            raise ValueError("rule_id должен быть непустой строкой")
        
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("name должен быть непустой строкой")
        
        if not isinstance(self.service_id, str) or not self.service_id.strip():
            raise ValueError("service_id должен быть непустой строкой")
        
        if not isinstance(self.metric_name, str) or not self.metric_name.strip():
            raise ValueError("metric_name должен быть непустой строкой")
        
        if not isinstance(self.threshold, (int, float)) or not (0.0 <= self.threshold <= 1.0):
            raise ValueError("threshold должен быть числом от 0.0 до 1.0")
        
        if not isinstance(self.min_replicas, int) or self.min_replicas < 1:
            raise ValueError("min_replicas должен быть положительным целым числом")
        
        if not isinstance(self.max_replicas, int) or self.max_replicas < self.min_replicas:
            raise ValueError("max_replicas должен быть >= min_replicas")
        
        if not isinstance(self.cooldown_period, int) or self.cooldown_period < 0:
            raise ValueError("cooldown_period должен быть неотрицательным целым числом")

    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразование в словарь для сериализации.
        
        Returns:
            Dict[str, Any]: Словарь с данными правила
        """
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

    def __str__(self) -> str:
        """Строковое представление правила"""
        return f"ScalingRule({self.name}, {self.trigger.value} > {self.threshold})"

    def __repr__(self) -> str:
        """Детальное представление правила"""
        return (f"ScalingRule(rule_id='{self.rule_id}', name='{self.name}', "
                f"service_id='{self.service_id}', metric_name='{self.metric_name}', "
                f"trigger={self.trigger.value}, threshold={self.threshold}, "
                f"action={self.action.value}, min_replicas={self.min_replicas}, "
                f"max_replicas={self.max_replicas}, cooldown_period={self.cooldown_period}, "
                f"enabled={self.enabled})")


@dataclass
class ScalingDecision:
    """
    Решение о масштабировании, принятое движком.
    
    Attributes:
        decision_id (str): Уникальный идентификатор решения
        service_id (str): Идентификатор сервиса
        action (ScalingAction): Принятое действие
        current_replicas (int): Текущее количество реплик
        target_replicas (int): Целевое количество реплик
        reason (str): Обоснование решения
        confidence (float): Уверенность в решении (от 0.0 до 1.0)
        triggered_rules (List[str]): Список сработавших правил
        timestamp (datetime): Время принятия решения
        metrics_used (List[MetricData]): Использованные метрики
    
    Example:
        >>> decision = ScalingDecision(
        ...     decision_id="dec_123",
        ...     service_id="my-service",
        ...     action=ScalingAction.SCALE_UP,
        ...     current_replicas=3,
        ...     target_replicas=5,
        ...     reason="High CPU usage detected",
        ...     confidence=0.85
        ... )
    """
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

    def __post_init__(self):
        """Пост-инициализация с валидацией"""
        self._validate()

    def _validate(self) -> None:
        """Валидация данных решения"""
        if not isinstance(self.decision_id, str) or not self.decision_id.strip():
            raise ValueError("decision_id должен быть непустой строкой")
        
        if not isinstance(self.service_id, str) or not self.service_id.strip():
            raise ValueError("service_id должен быть непустой строкой")
        
        if not isinstance(self.current_replicas, int) or self.current_replicas < 0:
            raise ValueError("current_replicas должен быть неотрицательным целым числом")
        
        if not isinstance(self.target_replicas, int) or self.target_replicas < 0:
            raise ValueError("target_replicas должен быть неотрицательным целым числом")
        
        if not isinstance(self.reason, str) or not self.reason.strip():
            raise ValueError("reason должен быть непустой строкой")
        
        if not isinstance(self.confidence, (int, float)) or not (0.0 <= self.confidence <= 1.0):
            raise ValueError("confidence должен быть числом от 0.0 до 1.0")
        
        if not isinstance(self.triggered_rules, list):
            raise ValueError("triggered_rules должен быть списком")
        
        if not isinstance(self.metrics_used, list):
            raise ValueError("metrics_used должен быть списком")

    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразование в словарь для сериализации.
        
        Returns:
            Dict[str, Any]: Словарь с данными решения
        """
        data = asdict(self)
        data["action"] = self.action.value
        data["timestamp"] = self.timestamp.isoformat()
        data["metrics_used"] = [m.to_dict() for m in self.metrics_used]
        return data

    def __str__(self) -> str:
        """Строковое представление решения"""
        return (f"ScalingDecision({self.action.value}, "
                f"{self.current_replicas} -> {self.target_replicas}, "
                f"confidence={self.confidence:.2f})")

    def __repr__(self) -> str:
        """Детальное представление решения"""
        return (f"ScalingDecision(decision_id='{self.decision_id}', "
                f"service_id='{self.service_id}', action={self.action.value}, "
                f"current_replicas={self.current_replicas}, "
                f"target_replicas={self.target_replicas}, reason='{self.reason}', "
                f"confidence={self.confidence}, triggered_rules={self.triggered_rules}, "
                f"timestamp={self.timestamp})")


@dataclass
class ScalingMetrics:
    """
    Метрики производительности системы масштабирования.
    
    Attributes:
        total_scaling_operations (int): Общее количество операций масштабирования
        successful_scaling_operations (int): Количество успешных операций
        failed_scaling_operations (int): Количество неудачных операций
        scale_up_operations (int): Количество операций увеличения
        scale_down_operations (int): Количество операций уменьшения
        emergency_operations (int): Количество экстренных операций
        average_scaling_time (float): Среднее время операции масштабирования
        last_scaling_time (Optional[datetime]): Время последней операции
        active_rules (int): Количество активных правил
        triggered_rules (int): Количество сработавших правил
        false_positives (int): Количество ложных срабатываний
        false_negatives (int): Количество пропущенных срабатываний
    """
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
        """Пост-инициализация с валидацией"""
        if self.last_scaling_time is None:
            self.last_scaling_time = datetime.now()
        self._validate()

    def _validate(self) -> None:
        """Валидация данных метрик"""
        for field_name in ['total_scaling_operations', 'successful_scaling_operations', 
                          'failed_scaling_operations', 'scale_up_operations', 
                          'scale_down_operations', 'emergency_operations', 
                          'active_rules', 'triggered_rules', 'false_positives', 
                          'false_negatives']:
            value = getattr(self, field_name)
            if not isinstance(value, int) or value < 0:
                raise ValueError(f"{field_name} должен быть неотрицательным целым числом")
        
        if not isinstance(self.average_scaling_time, (int, float)) or self.average_scaling_time < 0:
            raise ValueError("average_scaling_time должен быть неотрицательным числом")

    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразование в словарь для сериализации.
        
        Returns:
            Dict[str, Any]: Словарь с данными метрик
        """
        data = asdict(self)
        data["last_scaling_time"] = (
            self.last_scaling_time.isoformat()
            if self.last_scaling_time
            else None
        )
        return data

    def __str__(self) -> str:
        """Строковое представление метрик"""
        return (f"ScalingMetrics(operations={self.total_scaling_operations}, "
                f"success_rate={self.success_rate:.2%}, "
                f"active_rules={self.active_rules})")

    def __repr__(self) -> str:
        """Детальное представление метрик"""
        return (f"ScalingMetrics(total_scaling_operations={self.total_scaling_operations}, "
                f"successful_scaling_operations={self.successful_scaling_operations}, "
                f"failed_scaling_operations={self.failed_scaling_operations}, "
                f"scale_up_operations={self.scale_up_operations}, "
                f"scale_down_operations={self.scale_down_operations}, "
                f"emergency_operations={self.emergency_operations}, "
                f"average_scaling_time={self.average_scaling_time}, "
                f"last_scaling_time={self.last_scaling_time}, "
                f"active_rules={self.active_rules}, triggered_rules={self.triggered_rules}, "
                f"false_positives={self.false_positives}, "
                f"false_negatives={self.false_negatives})")

    @property
    def success_rate(self) -> float:
        """
        Коэффициент успешности операций.
        
        Returns:
            float: Коэффициент от 0.0 до 1.0
        """
        if self.total_scaling_operations == 0:
            return 0.0
        return self.successful_scaling_operations / self.total_scaling_operations


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