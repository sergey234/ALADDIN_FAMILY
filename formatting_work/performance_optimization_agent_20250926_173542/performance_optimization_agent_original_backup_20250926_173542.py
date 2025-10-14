# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Performance Optimization Agent
AI агент оптимизации производительности системы

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
"""

import json
import random
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import psutil

from core.base import ComponentStatus, SecurityBase


class OptimizationError(Exception):
    """Базовое исключение для ошибок оптимизации производительности."""
    pass


class ModelLoadError(OptimizationError):
    """Ошибка загрузки модели производительности."""
    pass


class ConfigurationError(OptimizationError):
    """Ошибка конфигурации агента."""
    pass


class MetricCollectionError(OptimizationError):
    """Ошибка сбора метрик производительности."""
    pass


class OptimizationImplementationError(OptimizationError):
    """Ошибка реализации оптимизации."""
    pass


class OptimizationType(Enum):
    """Типы оптимизации"""

    CPU = "cpu"
    MEMORY = "memory"
    NETWORK = "network"
    DISK = "disk"
    CACHE = "cache"
    DATABASE = "database"
    API = "api"
    AI_MODEL = "ai_model"
    THREADING = "threading"
    CONCURRENCY = "concurrency"


class OptimizationLevel(Enum):
    """Уровни оптимизации"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class OptimizationStatus(Enum):
    """Статусы оптимизации"""

    PENDING = "pending"
    ANALYZING = "analyzing"
    OPTIMIZING = "optimizing"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class PerformanceMetric:
    """Метрика производительности"""

    metric_id: str
    metric_type: OptimizationType
    value: float
    unit: str
    timestamp: Optional[datetime] = None
    threshold: float = 0.0
    is_critical: bool = False
    trend: str = "stable"  # increasing, decreasing, stable
    source: str = ""

    def __post_init__(self):
        """Инициализация метрики производительности после создания объекта.
        
        Устанавливает timestamp по умолчанию, если он не указан.
        Автоматически вызывается после создания экземпляра dataclass.
        """
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование метрики производительности в словарь.
        
        Returns:
            Dict[str, Any]: Словарь с данными метрики, включая:
                - metric_id: Идентификатор метрики
                - metric_type: Тип оптимизации (строка)
                - value: Значение метрики
                - unit: Единица измерения
                - timestamp: Временная метка в ISO формате
                - threshold: Пороговое значение
                - is_critical: Критичность метрики
                - trend: Тренд изменения
                - source: Источник данных
                
        Example:
            >>> metric = PerformanceMetric("cpu_usage", OptimizationType.CPU, 75.5, "%")
            >>> data = metric.to_dict()
            >>> print(data['metric_type'])
            'cpu'
        """
        data = asdict(self)
        data["metric_type"] = self.metric_type.value
        data["timestamp"] = (
            self.timestamp.isoformat() if self.timestamp else None
        )
        return data


@dataclass
class OptimizationRecommendation:
    """Рекомендация по оптимизации"""

    recommendation_id: str
    optimization_type: OptimizationType
    optimization_level: OptimizationLevel
    description: str
    expected_improvement: float  # процент улучшения
    confidence: float
    implementation_cost: str  # low, medium, high
    risk_level: str  # low, medium, high
    prerequisites: Optional[List[str]] = None
    estimated_time: int = 0  # минуты
    auto_implementable: bool = False

    def __post_init__(self):
        """Инициализация рекомендации по оптимизации после создания объекта.
        
        Устанавливает пустой список prerequisites по умолчанию, если он не указан.
        Автоматически вызывается после создания экземпляра dataclass.
        """
        if self.prerequisites is None:
            self.prerequisites = []

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование рекомендации по оптимизации в словарь.
        
        Returns:
            Dict[str, Any]: Словарь с данными рекомендации, включая:
                - recommendation_id: Идентификатор рекомендации
                - optimization_type: Тип оптимизации (строка)
                - optimization_level: Уровень оптимизации (строка)
                - description: Описание рекомендации
                - expected_improvement: Ожидаемое улучшение в процентах
                - confidence: Уровень уверенности
                - implementation_cost: Стоимость реализации
                - risk_level: Уровень риска
                - prerequisites: Список предварительных условий
                - estimated_time: Оценка времени в минутах
                - auto_implementable: Возможность автоматической реализации
                
        Example:
            >>> rec = OptimizationRecommendation("rec1", OptimizationType.CPU, 
            ...                                  OptimizationLevel.HIGH, "Оптимизация CPU")
            >>> data = rec.to_dict()
            >>> print(data['optimization_type'])
            'cpu'
        """
        data = asdict(self)
        data["optimization_type"] = self.optimization_type.value
        data["optimization_level"] = self.optimization_level.value
        return data


@dataclass
class OptimizationResult:
    """Результат оптимизации"""

    result_id: str
    optimization_type: OptimizationType
    status: OptimizationStatus
    before_value: float
    after_value: float
    improvement_percentage: float
    implementation_time: int  # секунды
    timestamp: Optional[datetime] = None
    error_message: str = ""
    rollback_available: bool = False

    def __post_init__(self):
        """Инициализация результата оптимизации после создания объекта.
        
        Устанавливает timestamp по умолчанию, если он не указан.
        Автоматически вызывается после создания экземпляра dataclass.
        """
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование результата оптимизации в словарь.
        
        Returns:
            Dict[str, Any]: Словарь с данными результата, включая:
                - recommendation_id: Идентификатор рекомендации
                - optimization_type: Тип оптимизации (строка)
                - status: Статус оптимизации (строка)
                - improvement_percentage: Процент улучшения
                - implementation_time: Время реализации в секундах
                - resources_saved: Сэкономленные ресурсы
                - timestamp: Временная метка в ISO формате
                - rollback_available: Доступность отката
                
        Example:
            >>> result = OptimizationResult("rec1", OptimizationType.CPU, 
            ...                           OptimizationStatus.COMPLETED, 15.5)
            >>> data = result.to_dict()
            >>> print(data['optimization_type'])
            'cpu'
        """
        data = asdict(self)
        data["optimization_type"] = self.optimization_type.value
        data["status"] = self.status.value
        data["timestamp"] = (
            self.timestamp.isoformat() if self.timestamp else None
        )
        return data


@dataclass
class OptimizationMetrics:
    """Метрики оптимизации"""

    total_optimizations: int = 0
    successful_optimizations: int = 0
    failed_optimizations: int = 0
    average_improvement: float = 0.0
    total_time_saved: int = 0  # секунды
    optimizations_by_type: Optional[Dict[str, int]] = None
    optimizations_by_level: Optional[Dict[str, int]] = None
    last_optimization: Optional[datetime] = None

    def __post_init__(self):
        """Инициализация метрик оптимизации после создания объекта.
        
        Устанавливает значения по умолчанию для словарей и времени последней оптимизации.
        Автоматически вызывается после создания экземпляра dataclass.
        """
        if self.optimizations_by_type is None:
            self.optimizations_by_type = {}
        if self.optimizations_by_level is None:
            self.optimizations_by_level = {}
        if self.last_optimization is None:
            self.last_optimization = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование метрик оптимизации в словарь.
        
        Returns:
            Dict[str, Any]: Словарь с данными метрик, включая:
                - total_optimizations: Общее количество оптимизаций
                - successful_optimizations: Количество успешных оптимизаций
                - failed_optimizations: Количество неудачных оптимизаций
                - average_improvement: Средний процент улучшения
                - last_optimization: Время последней оптимизации в ISO формате
                
        Example:
            >>> metrics = OptimizationMetrics()
            >>> data = metrics.to_dict()
            >>> print(data['total_optimizations'])
            0
        """
        data = asdict(self)
        data["last_optimization"] = (
            self.last_optimization.isoformat()
            if self.last_optimization
            else None
        )
        return data

    def update_metrics(self, result: OptimizationResult):
        """Обновление метрик на основе результата"""
        self.total_optimizations += 1

        if result.status == OptimizationStatus.COMPLETED:
            self.successful_optimizations += 1
        elif result.status == OptimizationStatus.FAILED:
            self.failed_optimizations += 1

        # Обновление статистики по типам
        opt_type = result.optimization_type.value
        if self.optimizations_by_type is not None:
            self.optimizations_by_type[opt_type] = (
                self.optimizations_by_type.get(opt_type, 0) + 1
            )

        # Обновление среднего улучшения
        if self.total_optimizations > 0:
            self.average_improvement = (
                self.average_improvement * (self.total_optimizations - 1)
                + result.improvement_percentage
            ) / self.total_optimizations

        # Обновление общего времени
        self.total_time_saved += result.implementation_time

        self.last_optimization = datetime.now()


class PerformanceOptimizationAgent(SecurityBase):
    """AI агент оптимизации производительности"""

    def __init__(self, name: str = "PerformanceOptimizationAgent"):
        """Инициализация агента оптимизации производительности.
        
        Args:
            name: Имя агента (по умолчанию "PerformanceOptimizationAgent")
            
        Initializes:
            - Конфигурация агента (пороги, интервалы)
            - Хранилище данных (метрики, рекомендации)
            - Фоновые задачи и модели
            - Статистика и мониторинг
            
        Example:
            >>> agent = PerformanceOptimizationAgent("MyAgent")
            >>> print(agent.optimization_threshold)
            0.7
        """
        super().__init__(name)

        # Конфигурация агента
        self.optimization_threshold = 0.7  # порог для оптимизации
        self.analysis_interval = 60  # интервал анализа (секунды)
        self.max_concurrent_optimizations = (
            3  # максимум одновременных оптимизаций
        )
        self.auto_optimization_enabled = True  # автоматическая оптимизация

        # Хранилище данных
        self.metrics: Dict[str, PerformanceMetric] = {}
        self.recommendations: Dict[str, OptimizationRecommendation] = {}
        self.results: Dict[str, OptimizationResult] = {}
        self.optimization_metrics: OptimizationMetrics = OptimizationMetrics()
        self.optimization_lock = threading.RLock()

        # AI модели и алгоритмы
        self.optimization_algorithms: Dict[str, Any] = {}
        self.performance_models: Dict[str, Any] = {}
        self.prediction_models: Dict[str, Any] = {}

        # Конфигурация
        self.agent_config = {
            "enable_cpu_optimization": True,
            "enable_memory_optimization": True,
            "enable_network_optimization": True,
            "enable_disk_optimization": True,
            "enable_cache_optimization": True,
            "enable_ai_optimization": True,
            "cpu_threshold": 80.0,
            "memory_threshold": 85.0,
            "network_threshold": 70.0,
            "disk_threshold": 90.0,
            "optimization_cooldown": 300,  # 5 минут
            "max_optimizations_per_hour": 10,
        }

        # Статистика
        self.statistics: Dict[str, Any] = {
            "total_analyses": 0,
            "successful_optimizations": 0,
            "failed_optimizations": 0,
            "start_time": None,
            "last_optimization": None,
            "optimization_cooldowns": {},
        }

    def initialize(self) -> bool:
        """Инициализация агента оптимизации производительности.
        
        Выполняет полную инициализацию агента, включая загрузку моделей,
        инициализацию алгоритмов и запуск фоновых задач.
        
        Returns:
            bool: True если инициализация успешна, False в случае ошибки
            
        Raises:
            ModelLoadError: При ошибке загрузки моделей
            ConfigurationError: При ошибке конфигурации
            Exception: При других неожиданных ошибках
            
        Example:
            >>> agent = PerformanceOptimizationAgent()
            >>> success = agent.initialize()
            >>> print(f"Инициализация: {'успешна' if success else 'неудачна'}")
            Инициализация: успешна
        """
        try:
            self.log_activity(
                "Инициализация Performance Optimization Agent", "info"
            )
            self.status = ComponentStatus.RUNNING
            self.statistics["start_time"] = datetime.now()

            # Инициализация AI алгоритмов
            self._initialize_optimization_algorithms()

            # Загрузка моделей производительности
            self._load_performance_models()

            # Инициализация предиктивных моделей
            self._initialize_prediction_models()

            # Запуск фоновых задач
            self._start_background_tasks()

            self.log_activity(
                "Performance Optimization Agent успешно инициализирован",
                "info",
            )
            return True

        except (ModelLoadError, ConfigurationError) as e:
            self.log_activity(
                f"Ошибка конфигурации/загрузки модели: {e}",
                "error",
            )
            self.status = ComponentStatus.ERROR
            return False
        except Exception as e:
            self.log_activity(
                f"Неожиданная ошибка инициализации: {e}",
                "error",
            )
            self.status = ComponentStatus.ERROR
            return False
        finally:
            # Очистка ресурсов при ошибке инициализации
            if self.status == ComponentStatus.ERROR:
                self._cleanup_resources()

    def stop(self) -> bool:
        """Остановка агента оптимизации производительности.
        
        Корректно останавливает все фоновые задачи, сохраняет данные
        и освобождает системные ресурсы.
        
        Returns:
            bool: True если остановка успешна, False в случае ошибки
            
        Raises:
            Exception: При ошибках во время остановки
            
        Example:
            >>> agent = PerformanceOptimizationAgent()
            >>> agent.initialize()
            >>> success = agent.stop()
            >>> print(f"Остановка: {'успешна' if success else 'неудачна'}")
            Остановка: успешна
        """
        try:
            self.log_activity(
                "Остановка Performance Optimization Agent", "info"
            )
            self.status = ComponentStatus.STOPPED

            # Остановка фоновых задач
            self._stop_background_tasks()

            # Сохранение данных
            self._save_optimization_data()

            # Очистка данных
            with self.optimization_lock:
                self.metrics.clear()
                self.recommendations.clear()
                self.results.clear()

            self.log_activity(
                "Performance Optimization Agent остановлен", "info"
            )
            return True

        except Exception as e:
            self.log_activity(
                f"Ошибка остановки Performance Optimization Agent: {e}",
                "error",
            )
            return False

    def analyze_performance(self) -> List[OptimizationRecommendation]:
        """Анализ производительности системы и генерация рекомендаций.
        
        Выполняет комплексный анализ текущего состояния системы,
        собирает метрики производительности и генерирует рекомендации
        по оптимизации на основе AI алгоритмов и трендов.
        
        Returns:
            List[OptimizationRecommendation]: Список рекомендаций по оптимизации
            
        Raises:
            MetricCollectionError: При ошибке сбора метрик
            Exception: При других неожиданных ошибках
            
        Example:
            >>> agent = PerformanceOptimizationAgent()
            >>> agent.initialize()
            >>> recommendations = agent.analyze_performance()
            >>> print(f"Найдено {len(recommendations)} рекомендаций")
            Найдено 5 рекомендаций
        """
        try:
            with self.optimization_lock:
                self.statistics["total_analyses"] += 1

                # Сбор метрик производительности
                current_metrics = self._collect_performance_metrics()

                # Анализ с помощью AI
                recommendations = self._analyze_with_ai(current_metrics)

                # Анализ трендов
                trend_analysis = self._analyze_trends(current_metrics)

                # Объединение рекомендаций
                final_recommendations = self._combine_recommendations(
                    recommendations, trend_analysis
                )

                # Сохранение рекомендаций
                for rec in final_recommendations:
                    self.recommendations[rec.recommendation_id] = rec

                self.log_activity(
                    f"Анализ производительности завершен. "
                    f"Найдено {len(final_recommendations)} рекомендаций",
                    "info",
                )

                return final_recommendations

        except Exception as e:
            self.log_activity(
                f"Ошибка анализа производительности: {e}", "error"
            )
            return []

    def optimize_system(
        self, recommendation_id: str
    ) -> Optional[OptimizationResult]:
        """Оптимизация системы по рекомендации"""
        try:
            with self.optimization_lock:
                if recommendation_id not in self.recommendations:
                    self.log_activity(
                        f"Рекомендация {recommendation_id} не найдена",
                        "warning",
                    )
                    return None

                recommendation = self.recommendations[recommendation_id]

                # Проверка возможности автоматической реализации
                if not recommendation.auto_implementable:
                    self.log_activity(
                        f"Рекомендация {recommendation_id} "
                        f"требует ручной реализации",
                        "warning",
                    )
                    return None

                # Измерение производительности до оптимизации
                before_metrics = self._collect_performance_metrics()

                # Выполнение оптимизации
                start_time = time.time()
                success = self._implement_optimization(recommendation)
                implementation_time = int(time.time() - start_time)

                # Измерение производительности после оптимизации
                after_metrics = self._collect_performance_metrics()

                # Создание результата
                result = OptimizationResult(
                    result_id=f"opt_{int(time.time())}",
                    optimization_type=recommendation.optimization_type,
                    status=(
                        OptimizationStatus.COMPLETED
                        if success
                        else OptimizationStatus.FAILED
                    ),
                    before_value=self._calculate_metric_value(
                        before_metrics, recommendation.optimization_type
                    ),
                    after_value=self._calculate_metric_value(
                        after_metrics, recommendation.optimization_type
                    ),
                    improvement_percentage=self._calculate_improvement(
                        before_metrics,
                        after_metrics,
                        recommendation.optimization_type,
                    ),
                    implementation_time=implementation_time,
                    rollback_available=success,
                )

                # Сохранение результата
                self.results[result.result_id] = result

                # Обновление метрик
                self.optimization_metrics.update_metrics(result)

                # Обновление статистики
                if success:
                    self.statistics["successful_optimizations"] += 1
                else:
                    self.statistics["failed_optimizations"] += 1
                self.statistics["last_optimization"] = datetime.now()

                self.log_activity(
                    f"Оптимизация {recommendation.optimization_type.value} "
                    f"завершена. "
                    f"Улучшение: {result.improvement_percentage:.2f}%",
                    "info",
                )

                return result

        except Exception as e:
            self.log_activity(f"Ошибка оптимизации системы: {e}", "error")
            return None

    def get_performance_metrics(self) -> List[PerformanceMetric]:
        """Получение метрик производительности"""
        try:
            with self.optimization_lock:
                return list(self.metrics.values())
        except Exception as e:
            self.log_activity(
                f"Ошибка получения метрик производительности: {e}", "error"
            )
            return []

    def get_optimization_recommendations(
        self,
    ) -> List[OptimizationRecommendation]:
        """Получение рекомендаций по оптимизации"""
        try:
            with self.optimization_lock:
                return list(self.recommendations.values())
        except Exception as e:
            self.log_activity(f"Ошибка получения рекомендаций: {e}", "error")
            return []

    def get_optimization_results(self) -> List[OptimizationResult]:
        """Получение результатов оптимизации"""
        try:
            with self.optimization_lock:
                return list(self.results.values())
        except Exception as e:
            self.log_activity(
                f"Ошибка получения результатов оптимизации: {e}", "error"
            )
            return []

    def get_agent_status(self) -> Dict[str, Any]:
        """Получение статуса агента"""
        try:
            with self.optimization_lock:
                return {
                    "status": self.status.value,
                    "total_metrics": len(self.metrics),
                    "total_recommendations": len(self.recommendations),
                    "total_results": len(self.results),
                    "optimization_metrics": (
                        self.optimization_metrics.to_dict()
                    ),
                    "statistics": self.statistics,
                    "config": self.agent_config,
                    "algorithms_count": len(self.optimization_algorithms),
                    "models_count": len(self.performance_models),
                    "prediction_models_count": len(self.prediction_models),
                }
        except Exception as e:
            self.log_activity(f"Ошибка получения статуса агента: {e}", "error")
            return {}

    def _initialize_optimization_algorithms(self):
        """Инициализация алгоритмов оптимизации"""
        try:
            self.optimization_algorithms = {
                "cpu_optimizer": {
                    "type": "genetic_algorithm",
                    "status": "initialized",
                    "efficiency": 0.85,
                },
                "memory_optimizer": {
                    "type": "greedy_algorithm",
                    "status": "initialized",
                    "efficiency": 0.90,
                },
                "network_optimizer": {
                    "type": "simulated_annealing",
                    "status": "initialized",
                    "efficiency": 0.88,
                },
                "cache_optimizer": {
                    "type": "lru_algorithm",
                    "status": "initialized",
                    "efficiency": 0.92,
                },
            }
            self.log_activity("Алгоритмы оптимизации инициализированы", "info")
        except Exception as e:
            self.log_activity(
                f"Ошибка инициализации алгоритмов оптимизации: {e}", "error"
            )

    def _load_performance_models(self):
        """Загрузка моделей производительности"""
        try:
            self.performance_models = {
                "cpu_model": {
                    "type": "regression",
                    "accuracy": 0.87,
                    "last_trained": datetime.now(),
                },
                "memory_model": {
                    "type": "neural_network",
                    "accuracy": 0.91,
                    "last_trained": datetime.now(),
                },
                "network_model": {
                    "type": "time_series",
                    "accuracy": 0.89,
                    "last_trained": datetime.now(),
                },
            }
            self.log_activity("Модели производительности загружены", "info")
        except Exception as e:
            self.log_activity(
                f"Ошибка загрузки моделей производительности: {e}", "error"
            )

    def _initialize_prediction_models(self):
        """Инициализация предиктивных моделей"""
        try:
            self.prediction_models = {
                "bottleneck_predictor": {
                    "type": "lstm",
                    "accuracy": 0.84,
                    "prediction_horizon": 3600,  # 1 час
                },
                "performance_predictor": {
                    "type": "arima",
                    "accuracy": 0.86,
                    "prediction_horizon": 1800,  # 30 минут
                },
                "optimization_predictor": {
                    "type": "random_forest",
                    "accuracy": 0.88,
                    "prediction_horizon": 7200,  # 2 часа
                },
            }
            self.log_activity("Предиктивные модели инициализированы", "info")
        except Exception as e:
            self.log_activity(
                f"Ошибка инициализации предиктивных моделей: {e}", "error"
            )

    def _start_background_tasks(self):
        """Запуск фоновых задач"""
        try:
            # Запуск задачи мониторинга производительности
            monitoring_thread = threading.Thread(
                target=self._monitoring_task, daemon=True
            )
            monitoring_thread.start()

            # Запуск задачи автоматической оптимизации
            if self.auto_optimization_enabled:
                auto_opt_thread = threading.Thread(
                    target=self._auto_optimization_task, daemon=True
                )
                auto_opt_thread.start()

            self.log_activity("Фоновые задачи запущены", "info")
        except Exception as e:
            self.log_activity(f"Ошибка запуска фоновых задач: {e}", "error")

    def _stop_background_tasks(self):
        """Остановка фоновых задач"""
        try:
            # Фоновые задачи остановятся автоматически при остановке агента
            self.log_activity("Фоновые задачи остановлены", "info")
        except Exception as e:
            self.log_activity(f"Ошибка остановки фоновых задач: {e}", "error")

    def _collect_performance_metrics(self) -> List[PerformanceMetric]:
        """Сбор метрик производительности"""
        try:
            metrics = []

            # CPU метрики
            if self.agent_config["enable_cpu_optimization"]:
                cpu_percent = psutil.cpu_percent(interval=1)
                cpu_metric = PerformanceMetric(
                    metric_id=f"cpu_{int(time.time())}",
                    metric_type=OptimizationType.CPU,
                    value=cpu_percent,
                    unit="percent",
                    threshold=self.agent_config["cpu_threshold"],
                    is_critical=cpu_percent
                    > self.agent_config["cpu_threshold"],
                    source="psutil",
                )
                metrics.append(cpu_metric)

            # Memory метрики
            if self.agent_config["enable_memory_optimization"]:
                memory = psutil.virtual_memory()
                memory_metric = PerformanceMetric(
                    metric_id=f"memory_{int(time.time())}",
                    metric_type=OptimizationType.MEMORY,
                    value=memory.percent,
                    unit="percent",
                    threshold=self.agent_config["memory_threshold"],
                    is_critical=memory.percent
                    > self.agent_config["memory_threshold"],
                    source="psutil",
                )
                metrics.append(memory_metric)

            # Network метрики
            if self.agent_config["enable_network_optimization"]:
                network = psutil.net_io_counters()
                network_metric = PerformanceMetric(
                    metric_id=f"network_{int(time.time())}",
                    metric_type=OptimizationType.NETWORK,
                    value=float(network.bytes_sent + network.bytes_recv),
                    unit="bytes",
                    threshold=self.agent_config["network_threshold"],
                    is_critical=False,
                    source="psutil",
                )
                metrics.append(network_metric)

            # Disk метрики
            if self.agent_config["enable_disk_optimization"]:
                disk = psutil.disk_usage("/")
                disk_metric = PerformanceMetric(
                    metric_id=f"disk_{int(time.time())}",
                    metric_type=OptimizationType.DISK,
                    value=disk.percent,
                    unit="percent",
                    threshold=self.agent_config["disk_threshold"],
                    is_critical=disk.percent
                    > self.agent_config["disk_threshold"],
                    source="psutil",
                )
                metrics.append(disk_metric)

            # Сохранение метрик
            for metric in metrics:
                self.metrics[metric.metric_id] = metric

            return metrics

        except Exception as e:
            self.log_activity(
                f"Ошибка сбора метрик производительности: {e}", "error"
            )
            return []

    def _analyze_with_ai(
        self, metrics: List[PerformanceMetric]
    ) -> List[OptimizationRecommendation]:
        """Анализ с помощью AI"""
        try:
            recommendations = []

            for metric in metrics:
                if metric.is_critical or metric.value > metric.threshold:
                    # Генерация рекомендации на основе AI
                    recommendation = self._generate_ai_recommendation(metric)
                    if recommendation:
                        recommendations.append(recommendation)

            return recommendations

        except Exception as e:
            self.log_activity(f"Ошибка AI анализа: {e}", "error")
            return []

    def _analyze_trends(
        self, metrics: List[PerformanceMetric]
    ) -> List[OptimizationRecommendation]:
        """Анализ трендов"""
        try:
            recommendations = []

            # Анализ трендов для каждого типа метрик
            for opt_type in OptimizationType:
                type_metrics = [
                    m for m in metrics if m.metric_type == opt_type
                ]
                if len(type_metrics) >= 2:
                    trend = self._calculate_trend(type_metrics)
                    if (
                        trend == "increasing"
                        and type_metrics[-1].value
                        > type_metrics[-1].threshold * 0.8
                    ):
                        recommendation = self._generate_trend_recommendation(
                            opt_type, trend
                        )
                        if recommendation:
                            recommendations.append(recommendation)

            return recommendations

        except Exception as e:
            self.log_activity(f"Ошибка анализа трендов: {e}", "error")
            return []

    def _combine_recommendations(
        self,
        ai_recommendations: List[OptimizationRecommendation],
        trend_recommendations: List[OptimizationRecommendation],
    ) -> List[OptimizationRecommendation]:
        """Объединение рекомендаций"""
        try:
            all_recommendations = ai_recommendations + trend_recommendations

            # Удаление дубликатов
            unique_recommendations: Dict[str, OptimizationRecommendation] = (
                {}
            )
            for rec in all_recommendations:
                key = (
                    f"{rec.optimization_type.value}_"
                    f"{rec.optimization_level.value}"
                )
                if (
                    key not in unique_recommendations
                    or rec.confidence > unique_recommendations[key].confidence
                ):
                    unique_recommendations[key] = rec

            return list(unique_recommendations.values())

        except Exception as e:
            self.log_activity(f"Ошибка объединения рекомендаций: {e}", "error")
            return []

    def _generate_ai_recommendation(
        self, metric: PerformanceMetric
    ) -> Optional[OptimizationRecommendation]:
        """Генерация AI рекомендации"""
        try:
            # Симуляция AI анализа
            confidence = random.uniform(0.7, 0.95)
            improvement = random.uniform(10.0, 50.0)

            # Определение уровня оптимизации
            if metric.value > metric.threshold * 1.5:
                level = OptimizationLevel.CRITICAL
            elif metric.value > metric.threshold * 1.2:
                level = OptimizationLevel.HIGH
            elif metric.value > metric.threshold:
                level = OptimizationLevel.MEDIUM
            else:
                level = OptimizationLevel.LOW

            recommendation = OptimizationRecommendation(
                recommendation_id=f"ai_{metric.metric_id}",
                optimization_type=metric.metric_type,
                optimization_level=level,
                description=(
                    f"AI рекомендует оптимизацию {metric.metric_type.value}"
                ),
                expected_improvement=improvement,
                confidence=confidence,
                implementation_cost="medium",
                risk_level="low",
                estimated_time=random.randint(5, 30),
                auto_implementable=confidence > 0.8,
            )

            return recommendation

        except Exception as e:
            self.log_activity(
                f"Ошибка генерации AI рекомендации: {e}", "error"
            )
            return None

    def _generate_trend_recommendation(
        self,
        opt_type: OptimizationType,
        trend: str,
    ) -> Optional[OptimizationRecommendation]:
        """Генерация рекомендации на основе тренда"""
        try:
            recommendation = OptimizationRecommendation(
                recommendation_id=(
                    f"trend_{opt_type.value}_{int(time.time())}"
                ),
                optimization_type=opt_type,
                optimization_level=OptimizationLevel.MEDIUM,
                description=(
                    f"Проактивная оптимизация {opt_type.value} "
                    f"на основе тренда {trend}"
                ),
                expected_improvement=random.uniform(15.0, 35.0),
                confidence=random.uniform(0.6, 0.85),
                implementation_cost="low",
                risk_level="low",
                estimated_time=random.randint(3, 15),
                auto_implementable=True,
            )

            return recommendation

        except Exception as e:
            self.log_activity(
                f"Ошибка генерации рекомендации по тренду: {e}", "error"
            )
            return None

    def _calculate_trend(self, metrics: List[PerformanceMetric]) -> str:
        """Расчет тренда"""
        try:
            if len(metrics) < 2:
                return "stable"

            values = [m.value for m in metrics]
            if values[-1] > values[0] * 1.1:
                return "increasing"
            elif values[-1] < values[0] * 0.9:
                return "decreasing"
            else:
                return "stable"

        except Exception as e:
            self.log_activity(f"Ошибка расчета тренда: {e}", "error")
            return "stable"

    def _implement_optimization(
        self, recommendation: OptimizationRecommendation
    ) -> bool:
        """Реализация оптимизации"""
        try:
            # Симуляция реализации оптимизации
            time.sleep(
                random.uniform(0.1, 0.5)
            )  # Симуляция времени выполнения

            # В реальной системе здесь была бы настоящая оптимизация
            success = random.random() > 0.1  # 90% успешности

            return success

        except Exception as e:
            self.log_activity(f"Ошибка реализации оптимизации: {e}", "error")
            return False

    def _calculate_metric_value(
        self, metrics: List[PerformanceMetric], opt_type: OptimizationType
    ) -> float:
        """Расчет значения метрики"""
        try:
            type_metrics = [m for m in metrics if m.metric_type == opt_type]
            if type_metrics:
                return type_metrics[-1].value
            return 0.0

        except Exception as e:
            self.log_activity(f"Ошибка расчета значения метрики: {e}", "error")
            return 0.0

    def _calculate_improvement(
        self,
        before_metrics: List[PerformanceMetric],
        after_metrics: List[PerformanceMetric],
        opt_type: OptimizationType,
    ) -> float:
        """Расчет улучшения"""
        try:
            before_value = self._calculate_metric_value(
                before_metrics, opt_type
            )
            after_value = self._calculate_metric_value(after_metrics, opt_type)

            if before_value == 0:
                return 0.0

            improvement = ((before_value - after_value) / before_value) * 100
            return max(0.0, improvement)  # Не может быть отрицательным

        except Exception as e:
            self.log_activity(f"Ошибка расчета улучшения: {e}", "error")
            return 0.0

    def _monitoring_task(self):
        """Задача мониторинга производительности"""
        try:
            while self.status == ComponentStatus.RUNNING:
                time.sleep(self.analysis_interval)

                # Сбор метрик
                metrics = self._collect_performance_metrics()

                # Проверка критических значений
                critical_metrics = [
                    m for m in metrics if m.is_critical
                ]
                if critical_metrics:
                    self.log_activity(
                        f"Обнаружены критические метрики: "
                        f"{len(critical_metrics)}",
                        "warning",
                    )

        except Exception as e:
            self.log_activity(f"Ошибка задачи мониторинга: {e}", "error")

    def _auto_optimization_task(self):
        """Задача автоматической оптимизации"""
        try:
            while self.status == ComponentStatus.RUNNING:
                time.sleep(self.analysis_interval * 2)  # Реже чем мониторинг

                # Анализ производительности
                recommendations = self.analyze_performance()

                # Автоматическая реализация высокоприоритетных рекомендаций
                for rec in recommendations:
                    if (
                        rec.auto_implementable
                        and rec.optimization_level
                        in [OptimizationLevel.HIGH, OptimizationLevel.CRITICAL]
                        and rec.confidence > 0.9
                    ):
                        self.optimize_system(rec.recommendation_id)

        except Exception as e:
            self.log_activity(
                f"Ошибка задачи автоматической оптимизации: {e}", "error"
            )

    def _save_optimization_data(self):
        """Сохранение данных оптимизации"""
        try:
            import os

            os.makedirs("/tmp/aladdin_optimizations", exist_ok=True)

            data_to_save = {
                "metrics": {k: v.to_dict() for k, v in self.metrics.items()},
                "recommendations": {
                    k: v.to_dict() for k, v in self.recommendations.items()
                },
                "results": {k: v.to_dict() for k, v in self.results.items()},
                "optimization_metrics": self.optimization_metrics.to_dict(),
                "statistics": self.statistics,
                "saved_at": datetime.now().isoformat(),
            }

            with open(
                "/tmp/aladdin_optimizations/last_optimizations.json",
                "w",
                encoding="utf-8",
            ) as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)

            self.log_activity("Данные оптимизации сохранены", "info")
        except Exception as e:
            self.log_activity(
                f"Ошибка сохранения данных оптимизации: {e}", "error"
            )

    def _cleanup_resources(self):
        """Очистка ресурсов при ошибке инициализации.
        
        Закрывает открытые соединения, останавливает фоновые задачи
        и освобождает системные ресурсы.
        """
        try:
            # Остановка фоновых задач
            if hasattr(self, 'background_tasks') and self.background_tasks:
                for task in self.background_tasks:
                    if hasattr(task, 'stop'):
                        task.stop()
            
            # Очистка моделей
            if hasattr(self, 'performance_models'):
                self.performance_models.clear()
            
            if hasattr(self, 'prediction_models'):
                self.prediction_models.clear()
            
            # Сброс статуса
            self.status = ComponentStatus.STOPPED
            
            self.log_activity("Ресурсы успешно очищены", "info")
            
        except Exception as e:
            self.log_activity(
                f"Ошибка очистки ресурсов: {e}", "error"
            )
