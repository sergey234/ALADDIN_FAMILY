# -*- coding: utf-8 -*-
"""
Продолжение улучшенного AutoScalingEngine - основная часть класса
"""

import asyncio
import threading
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from core.base import ComponentStatus, LogLevel, SecurityBase


# Временные классы для совместимости
class ScalingRule:
    def __init__(self, name: str, service_id: str, metric_name: str, 
                 threshold: float, action: str, cooldown: int = 300):
        self.name = name
        self.service_id = service_id
        self.metric_name = metric_name
        self.threshold = threshold
        self.action = action
        self.cooldown = cooldown
        self.last_triggered = None

class MetricData:
    def __init__(self, name: str, value: float, unit: str, timestamp: datetime):
        self.name = name
        self.value = value
        self.unit = unit
        self.timestamp = timestamp

class ScalingDecision:
    def __init__(self, service_id: str, action: str, reason: str, timestamp: datetime):
        self.service_id = service_id
        self.action = action
        self.reason = reason
        self.timestamp = timestamp

class ScalingMetrics:
    def __init__(self):
        self.total_decisions = 0
        self.successful_scales = 0
        self.failed_scales = 0

class PerformanceMetrics:
    def __init__(self):
        self.cpu_usage = 0.0
        self.memory_usage = 0.0
        self.response_time = 0.0

class ScalingError(Exception):
    pass


class AutoScalingEngine(SecurityBase):
    """
    Улучшенный движок автоматического масштабирования для ALADDIN Security System.
    
    Этот класс предоставляет полную функциональность для автоматического 
    масштабирования сервисов на основе метрик производительности. Поддерживает
    асинхронные операции, валидацию параметров и расширенное логирование.
    
    Attributes:
        name (str): Название движка
        monitoring_interval (int): Интервал мониторинга в секундах
        decision_interval (int): Интервал принятия решений в секундах
        metric_retention_hours (int): Время хранения метрик в часах
        default_cooldown (int): Период охлаждения по умолчанию в секундах
        emergency_threshold (float): Порог для экстренных операций
        prediction_window_minutes (int): Окно предсказания в минутах
        ai_enabled (bool): Включены ли AI функции
        scaling_rules (Dict[str, ScalingRule]): Словарь правил масштабирования
        metric_history (Dict[str, List[MetricData]]): История метрик
        scaling_decisions (List[ScalingDecision]): История решений
        scaling_metrics (ScalingMetrics): Метрики масштабирования
        performance_metrics (PerformanceMetrics): Метрики производительности
        scaling_lock (threading.RLock): Блокировка для потокобезопасности
    
    Example:
        >>> # Синхронное использование
        >>> engine = AutoScalingEngine("MyEngine")
        >>> engine.initialize()
        >>> 
        >>> # Асинхронное использование
        >>> async with AutoScalingEngine("MyEngine") as engine:
        ...     await engine.collect_metric(metric)
        ...     decision = await engine.make_scaling_decision("my-service")
    
    Note:
        Класс поддерживает как синхронный, так и асинхронный режимы работы.
        Для максимальной производительности рекомендуется использовать 
        асинхронный режим.
    
    See Also:
        ScalingRule: Правила масштабирования
        MetricData: Данные метрик
        ScalingDecision: Решения о масштабировании
    """

    def __init__(self, name: str = "AutoScalingEngine"):
        """
        Инициализация движка автоматического масштабирования.
        
        Args:
            name (str, optional): Название движка. По умолчанию "AutoScalingEngine".
        
        Raises:
            ValueError: Если name пустой или некорректный
            TypeError: Если name не является строкой
        
        Example:
            >>> engine = AutoScalingEngine("ProductionEngine")
            >>> print(engine.name)
            ProductionEngine
        """
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
        """
        Строковое представление движка.
        
        Returns:
            str: Краткое описание движка
        """
        return (f"AutoScalingEngine(name='{self.name}', "
                f"status={self.status.value}, "
                f"rules={len(self.scaling_rules)}, "
                f"ai_enabled={self.ai_enabled})")

    def __repr__(self) -> str:
        """
        Детальное представление движка.
        
        Returns:
            str: Подробное описание движка
        """
        return (f"AutoScalingEngine(name='{self.name}', "
                f"monitoring_interval={self.monitoring_interval}s, "
                f"active_rules={len(self.scaling_rules)}, "
                f"status={self.status.value}, "
                f"ai_enabled={self.ai_enabled})")

    def __len__(self) -> int:
        """
        Количество активных правил масштабирования.
        
        Returns:
            int: Количество правил
        """
        return len(self.scaling_rules)

    def __contains__(self, rule_id: str) -> bool:
        """
        Проверка наличия правила по ID.
        
        Args:
            rule_id (str): Идентификатор правила
        
        Returns:
            bool: True если правило существует
        
        Raises:
            TypeError: Если rule_id не является строкой
        """
        if not isinstance(rule_id, str):
            raise TypeError("rule_id должен быть строкой")
        return rule_id in self.scaling_rules

    def __getitem__(self, rule_id: str) -> ScalingRule:
        """
        Получение правила по ID.
        
        Args:
            rule_id (str): Идентификатор правила
        
        Returns:
            ScalingRule: Правило масштабирования
        
        Raises:
            KeyError: Если правило не найдено
            TypeError: Если rule_id не является строкой
        """
        if not isinstance(rule_id, str):
            raise TypeError("rule_id должен быть строкой")
        if rule_id not in self.scaling_rules:
            raise KeyError(f"Правило {rule_id} не найдено")
        return self.scaling_rules[rule_id]

    def __iter__(self):
        """
        Итерация по правилам масштабирования.
        
        Yields:
            ScalingRule: Правила масштабирования
        """
        return iter(self.scaling_rules.values())

    async def __aenter__(self):
        """
        Асинхронный вход в контекст.
        
        Returns:
            AutoScalingEngine: Инициализированный движок
        """
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Асинхронный выход из контекста.
        
        Args:
            exc_type: Тип исключения
            exc_val: Значение исключения
            exc_tb: Трассировка исключения
        """
        await self.stop()
        if exc_type:
            await self._log_async(f"Ошибка в контексте: {exc_val}", LogLevel.ERROR)

    async def initialize(self) -> bool:
        """
        Асинхронная инициализация движка автоматического масштабирования.
        
        Returns:
            bool: True если инициализация успешна, False иначе
        
        Raises:
            ScalingError: Если произошла критическая ошибка инициализации
        
        Example:
            >>> engine = AutoScalingEngine()
            >>> success = await engine.initialize()
            >>> print(f"Инициализация: {'успешна' if success else 'неудачна'}")
        """
        try:
            await self._log_async("Инициализация Auto Scaling Engine", LogLevel.INFO)
            self.status = ComponentStatus.RUNNING
            self.statistics["start_time"] = datetime.now()

            # Инициализация AI моделей
            await self._initialize_ai_models_async()

            # Загрузка существующих правил
            await self._load_scaling_rules_async()

            # Запуск фоновых задач
            await self._start_background_tasks_async()

            await self._log_async("Auto Scaling Engine успешно инициализирован", LogLevel.INFO)
            return True

        except Exception as e:
            await self._log_async(f"Ошибка инициализации Auto Scaling Engine: {e}", LogLevel.ERROR)
            self.status = ComponentStatus.ERROR
            raise ScalingError(f"Ошибка инициализации: {e}") from e

    async def stop(self) -> bool:
        """
        Асинхронная остановка движка автоматического масштабирования.
        
        Returns:
            bool: True если остановка успешна, False иначе
        
        Example:
            >>> await engine.stop()
        """
        try:
            await self._log_async("Остановка Auto Scaling Engine", LogLevel.INFO)
            self.status = ComponentStatus.STOPPED

            # Остановка фоновых задач
            await self._stop_background_tasks_async()

            # Сохранение состояния
            await self._save_scaling_state_async()

            # Очистка данных
            async with self.scaling_lock:
                self.scaling_rules.clear()
                self.metric_history.clear()
                self.scaling_decisions.clear()

            await self._log_async("Auto Scaling Engine остановлен", LogLevel.INFO)
            return True

        except Exception as e:
            await self._log_async(f"Ошибка остановки Auto Scaling Engine: {e}", LogLevel.ERROR)
            return False

    async def add_scaling_rule(self, rule: ScalingRule) -> bool:
        """
        Асинхронное добавление правила масштабирования.
        
        Args:
            rule (ScalingRule): Правило для добавления
        
        Returns:
            bool: True если правило добавлено успешно, False иначе
        
        Raises:
            TypeError: Если rule не является экземпляром ScalingRule
            ValueError: Если правило с таким ID уже существует
        
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
            >>> success = await engine.add_scaling_rule(rule)
        """
        if not isinstance(rule, ScalingRule):
            raise TypeError("rule должен быть экземпляром ScalingRule")
        
        try:
            async with self.scaling_lock:
                if rule.rule_id in self.scaling_rules:
                    raise ValueError(f"Правило с ID {rule.rule_id} уже существует")
                
                self.scaling_rules[rule.rule_id] = rule
                self.scaling_metrics.active_rules = len(self.scaling_rules)

                await self._log_async(f"Правило масштабирования {rule.name} добавлено", LogLevel.INFO)
                return True

        except Exception as e:
            await self._log_async(f"Ошибка добавления правила масштабирования: {e}", LogLevel.ERROR)
            return False

    async def remove_scaling_rule(self, rule_id: str) -> bool:
        """
        Асинхронное удаление правила масштабирования.
        
        Args:
            rule_id (str): Идентификатор правила для удаления
        
        Returns:
            bool: True если правило удалено успешно, False иначе
        
        Raises:
            TypeError: Если rule_id не является строкой
            ValueError: Если правило не найдено
        
        Example:
            >>> success = await engine.remove_scaling_rule("cpu_scale_up")
        """
        if not isinstance(rule_id, str) or not rule_id.strip():
            raise TypeError("rule_id должен быть непустой строкой")
        
        try:
            async with self.scaling_lock:
                if rule_id not in self.scaling_rules:
                    raise ValueError(f"Правило {rule_id} не найдено")
                
                rule = self.scaling_rules[rule_id]
                del self.scaling_rules[rule_id]
                self.scaling_metrics.active_rules = len(self.scaling_rules)

                await self._log_async(f"Правило масштабирования {rule.name} удалено", LogLevel.INFO)
                return True

        except Exception as e:
            await self._log_async(f"Ошибка удаления правила масштабирования: {e}", LogLevel.ERROR)
            return False

    async def collect_metric(self, metric: MetricData) -> bool:
        """
        Асинхронный сбор метрики с валидацией.
        
        Args:
            metric (MetricData): Метрика для сбора
        
        Returns:
            bool: True если метрика собрана успешно, False иначе
        
        Raises:
            TypeError: Если metric не является экземпляром MetricData
            ValueError: Если метрика некорректна
        
        Example:
            >>> metric = MetricData(
            ...     metric_name="cpu_usage",
            ...     value=0.75,
            ...     timestamp=datetime.now(),
            ...     service_id="my-service"
            ... )
            >>> success = await engine.collect_metric(metric)
        """
        if not isinstance(metric, MetricData):
            raise TypeError("metric должен быть экземпляром MetricData")
        
        try:
            # Валидация метрики
            if not self._validate_metric(metric):
                return False
            
            async with self.scaling_lock:
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

                # Обновляем кэш
                self._invalidate_cache(f"metrics_{service_key}")

                return True

        except Exception as e:
            await self._log_async(f"Ошибка сбора метрики: {e}", LogLevel.ERROR)
            return False

    async def make_scaling_decision(
        self, 
        service_id: str,
        force_decision: bool = False,
        confidence_threshold: float = 0.7
    ) -> Optional[ScalingDecision]:
        """
        Асинхронное принятие решения о масштабировании для указанного сервиса.
        
        Args:
            service_id (str): Идентификатор сервиса для анализа
            force_decision (bool, optional): Принудительное принятие решения 
                даже при низкой уверенности. По умолчанию False.
            confidence_threshold (float, optional): Минимальный порог уверенности 
                для принятия решения. По умолчанию 0.7.
        
        Returns:
            Optional[ScalingDecision]: Объект решения о масштабировании или None, 
                если решение не принято.
        
        Raises:
            ValueError: Если service_id пустой или некорректный
            TypeError: Если параметры имеют неверный тип
            ScalingError: Если произошла ошибка в процессе принятия решения
        
        Example:
            >>> decision = await engine.make_scaling_decision("my-service")
            >>> if decision:
            ...     print(f"Действие: {decision.action.value}")
            ...     print(f"Целевые реплики: {decision.target_replicas}")
        """
        if not isinstance(service_id, str) or not service_id.strip():
            raise ValueError("service_id должен быть непустой строкой")
        
        if not isinstance(force_decision, bool):
            raise TypeError("force_decision должен быть булевым значением")
        
        if not isinstance(confidence_threshold, (int, float)) or not (0.0 <= confidence_threshold <= 1.0):
            raise ValueError("confidence_threshold должен быть числом от 0.0 до 1.0")
        
        try:
            async with self.scaling_lock:
                start_time = time.time()

                # Получаем правила для сервиса
                service_rules = [
                    r
                    for r in self.scaling_rules.values()
                    if r.service_id == service_id and r.enabled
                ]
                if not service_rules:
                    await self._log_async(f"Нет правил для сервиса {service_id}", LogLevel.WARNING)
                    return None

                # Собираем метрики для сервиса
                service_metrics = await self._get_service_metrics_async(service_id)
                if not service_metrics:
                    await self._log_async(f"Нет метрик для сервиса {service_id}", LogLevel.WARNING)
                    return None

                # Анализируем правила
                triggered_rules = []
                scaling_actions = []
                confidence_scores = []

                for rule in service_rules:
                    if await self._evaluate_rule_async(rule, service_metrics):
                        triggered_rules.append(rule.rule_id)
                        scaling_actions.append(rule.action)
                        confidence_scores.append(
                            await self._calculate_confidence_async(rule, service_metrics)
                        )

                        # Обновляем статистику правила
                        rule.last_triggered = datetime.now()
                        rule.trigger_count += 1
                        self.scaling_metrics.triggered_rules += 1

                if not triggered_rules:
                    await self._log_async(f"Нет сработавших правил для сервиса {service_id}", LogLevel.DEBUG)
                    return None

                # Принимаем финальное решение
                decision = await self._make_final_decision_async(
                    service_id,
                    scaling_actions,
                    confidence_scores,
                    triggered_rules,
                    service_metrics,
                    force_decision,
                    confidence_threshold
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
                    
                    # Обновляем метрики производительности
                    self.performance_metrics.average_decision_time = self.statistics["average_decision_time"]

                return decision

        except Exception as e:
            await self._log_async(f"Ошибка принятия решения о масштабировании: {e}", LogLevel.ERROR)
            raise ScalingError(f"Ошибка принятия решения: {e}") from e

    async def get_scaling_rules(
        self, service_id: Optional[str] = None
    ) -> List[ScalingRule]:
        """
        Асинхронное получение правил масштабирования.
        
        Args:
            service_id (Optional[str], optional): Фильтр по сервису. 
                Если None, возвращаются все правила.
        
        Returns:
            List[ScalingRule]: Список правил масштабирования
        
        Raises:
            TypeError: Если service_id не является строкой или None
        
        Example:
            >>> # Все правила
            >>> all_rules = await engine.get_scaling_rules()
            >>> 
            >>> # Правила для конкретного сервиса
            >>> service_rules = await engine.get_scaling_rules("my-service")
        """
        if service_id is not None and not isinstance(service_id, str):
            raise TypeError("service_id должен быть строкой или None")
        
        try:
            async with self.scaling_lock:
                if service_id:
                    return [
                        r
                        for r in self.scaling_rules.values()
                        if r.service_id == service_id
                    ]
                return list(self.scaling_rules.values())
        except Exception as e:
            await self._log_async(f"Ошибка получения правил масштабирования: {e}", LogLevel.ERROR)
            return []

    async def get_scaling_decisions(
        self, service_id: Optional[str] = None, limit: int = 100
    ) -> List[ScalingDecision]:
        """
        Асинхронное получение решений о масштабировании.
        
        Args:
            service_id (Optional[str], optional): Фильтр по сервису. 
                Если None, возвращаются все решения.
            limit (int, optional): Максимальное количество решений. 
                По умолчанию 100.
        
        Returns:
            List[ScalingDecision]: Список решений о масштабировании
        
        Raises:
            TypeError: Если параметры имеют неверный тип
            ValueError: Если limit отрицательный
        
        Example:
            >>> # Последние 50 решений
            >>> decisions = await engine.get_scaling_decisions(limit=50)
            >>> 
            >>> # Решения для конкретного сервиса
            >>> service_decisions = await engine.get_scaling_decisions("my-service")
        """
        if service_id is not None and not isinstance(service_id, str):
            raise TypeError("service_id должен быть строкой или None")
        
        if not isinstance(limit, int) or limit < 0:
            raise ValueError("limit должен быть неотрицательным целым числом")
        
        try:
            async with self.scaling_lock:
                decisions = self.scaling_decisions
                if service_id:
                    decisions = [
                        d for d in decisions if d.service_id == service_id
                    ]

                # Сортируем по времени (новые сначала)
                decisions.sort(key=lambda x: x.timestamp, reverse=True)
                return decisions[:limit]
        except Exception as e:
            await self._log_async(f"Ошибка получения решений о масштабировании: {e}", LogLevel.ERROR)
            return []

    async def get_scaling_metrics(self) -> ScalingMetrics:
        """
        Асинхронное получение метрик масштабирования.
        
        Returns:
            ScalingMetrics: Метрики масштабирования
        
        Example:
            >>> metrics = await engine.get_scaling_metrics()
            >>> print(f"Успешность: {metrics.success_rate:.2%}")
        """
        try:
            async with self.scaling_lock:
                return self.scaling_metrics
        except Exception as e:
            await self._log_async(f"Ошибка получения метрик масштабирования: {e}", LogLevel.ERROR)
            return ScalingMetrics()

    async def get_engine_status(self) -> Dict[str, Any]:
        """
        Асинхронное получение статуса движка.
        
        Returns:
            Dict[str, Any]: Словарь со статусом движка
        
        Example:
            >>> status = await engine.get_engine_status()
            >>> print(f"Статус: {status['status']}")
            >>> print(f"Активных правил: {status['active_rules']}")
        """
        try:
            async with self.scaling_lock:
                return {
                    "status": self.status.value,
                    "active_rules": len(self.scaling_rules),
                    "total_metrics": sum(
                        len(metrics)
                        for metrics in self.metric_history.values()
                    ),
                    "total_decisions": len(self.scaling_decisions),
                    "metrics": self.scaling_metrics.to_dict(),
                    "performance_metrics": self.performance_metrics.to_dict(),
                    "statistics": self.statistics,
                    "ai_enabled": self.ai_enabled,
                    "monitoring_interval": self.monitoring_interval,
                    "decision_interval": self.decision_interval,
                }
        except Exception as e:
            await self._log_async(f"Ошибка получения статуса движка: {e}", LogLevel.ERROR)
            return {}