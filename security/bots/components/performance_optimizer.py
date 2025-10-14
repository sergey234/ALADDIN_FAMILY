"""
Оптимизатор производительности для ParentalControlBot.

Обеспечивает мониторинг производительности, оптимизацию запросов,
пулинг соединений и другие улучшения производительности.
"""

import asyncio
import gc
import logging
import threading
import time
# import weakref  # TODO: Добавить при реализации weak references
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional

import psutil


class PerformanceMetric(Enum):
    """Типы метрик производительности."""

    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    CACHE_HIT_RATE = "cache_hit_rate"
    DATABASE_QUERY_TIME = "database_query_time"
    REDIS_QUERY_TIME = "redis_query_time"


@dataclass
class PerformanceStats:
    """Статистика производительности."""

    metric_type: PerformanceMetric
    value: float
    timestamp: float
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceThreshold:
    """Пороговые значения производительности."""

    metric_type: PerformanceMetric
    warning_threshold: float
    critical_threshold: float
    action: Optional[str] = None


class ConnectionPool:
    """Пул соединений для оптимизации производительности."""

    def __init__(self, max_connections: int = 10, min_connections: int = 2):
        self.max_connections = max_connections
        self.min_connections = min_connections
        self.connections: List[Any] = []
        self.available_connections: List[Any] = []
        self.lock = threading.RLock()
        self.logger = logging.getLogger(__name__)

    def get_connection(self) -> Optional[Any]:
        """Получить соединение из пула."""
        with self.lock:
            if self.available_connections:
                return self.available_connections.pop()
            elif len(self.connections) < self.max_connections:
                # Создать новое соединение
                connection = self._create_connection()
                if connection:
                    self.connections.append(connection)
                    return connection
            return None

    def return_connection(self, connection: Any) -> None:
        """Вернуть соединение в пул."""
        with self.lock:
            if connection and connection in self.connections:
                self.available_connections.append(connection)

    def _create_connection(self) -> Optional[Any]:
        """Создать новое соединение."""
        # Заглушка для создания соединения
        # В реальной реализации здесь будет создание соединения с БД/Redis
        return {"id": len(self.connections), "created_at": time.time()}

    def close_all(self) -> None:
        """Закрыть все соединения."""
        with self.lock:
            self.connections.clear()
            self.available_connections.clear()


class QueryOptimizer:
    """Оптимизатор запросов к базе данных."""

    def __init__(self):
        self.query_cache: Dict[str, Any] = {}
        self.query_stats: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(__name__)

    def optimize_query(self, query: str, params: Dict[str, Any] = None) -> str:
        """
        Оптимизировать SQL запрос.

        Args:
            query: SQL запрос
            params: Параметры запроса

        Returns:
            Оптимизированный запрос
        """
        # Базовая оптимизация запросов
        optimized = query.strip()

        # Удаление лишних пробелов
        optimized = " ".join(optimized.split())

        # Добавление индексов для часто используемых полей
        if "WHERE" in optimized.upper():
            # Добавление подсказок для оптимизатора
            if "child_id" in optimized:
                optimized = optimized.replace(
                    "WHERE", "WHERE /*+ USE_INDEX(children, idx_child_id) */"
                )

        return optimized

    def cache_query_result(
        self, query: str, result: Any, ttl: int = 300,
        params: Dict[str, Any] = None
    ) -> None:
        """
        Кэшировать результат запроса.

        Args:
            query: SQL запрос
            result: Результат запроса
            ttl: Время жизни кэша в секундах
            params: Параметры запроса
        """
        cache_key = (
            f"{hash(query)}_{hash(str(sorted((params or {}).items())))}"
        )
        self.query_cache[cache_key] = {
            "result": result,
            "timestamp": time.time(),
            "ttl": ttl,
        }

    def get_cached_result(
        self, query: str, params: Dict[str, Any] = None
    ) -> Optional[Any]:
        """
        Получить кэшированный результат запроса.

        Args:
            query: SQL запрос
            params: Параметры запроса

        Returns:
            Кэшированный результат или None
        """
        cache_key = (
            f"{hash(query)}_{hash(str(sorted((params or {}).items())))}"
        )

        if cache_key in self.query_cache:
            cached = self.query_cache[cache_key]
            if time.time() - cached["timestamp"] < cached["ttl"]:
                return cached["result"]
            else:
                del self.query_cache[cache_key]

        return None

    def record_query_stats(
        self, query: str, execution_time: float, success: bool
    ) -> None:
        """
        Записать статистику выполнения запроса.

        Args:
            query: SQL запрос
            execution_time: Время выполнения в секундах
            success: Успешность выполнения
        """
        query_hash = hash(query)
        if query_hash not in self.query_stats:
            self.query_stats[query_hash] = {
                "query": query,
                "count": 0,
                "total_time": 0.0,
                "success_count": 0,
                "error_count": 0,
                "avg_time": 0.0,
                "max_time": 0.0,
                "min_time": float("inf"),
            }

        stats = self.query_stats[query_hash]
        stats["count"] += 1
        stats["total_time"] += execution_time
        stats["avg_time"] = stats["total_time"] / stats["count"]
        stats["max_time"] = max(stats["max_time"], execution_time)
        stats["min_time"] = min(stats["min_time"], execution_time)

        if success:
            stats["success_count"] += 1
        else:
            stats["error_count"] += 1

    def get_slow_queries(self, threshold: float = 1.0) -> List[Dict[str, Any]]:
        """
        Получить список медленных запросов.

        Args:
            threshold: Пороговое время выполнения в секундах

        Returns:
            Список медленных запросов
        """
        slow_queries = []
        for stats in self.query_stats.values():
            if stats["avg_time"] > threshold:
                slow_queries.append(stats)

        return sorted(slow_queries, key=lambda x: x["avg_time"], reverse=True)


class PerformanceMonitor:
    """Монитор производительности."""

    def __init__(self, collection_interval: float = 1.0):
        self.collection_interval = collection_interval
        self.stats: List[PerformanceStats] = []
        self.thresholds: List[PerformanceThreshold] = []
        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.lock = threading.RLock()
        self.logger = logging.getLogger(__name__)

        # Инициализация пороговых значений
        self._setup_default_thresholds()

    def _setup_default_thresholds(self) -> None:
        """Настройка пороговых значений по умолчанию."""
        self.thresholds = [
            PerformanceThreshold(
                PerformanceMetric.CPU_USAGE, 70.0, 90.0, "scale_up"
            ),
            PerformanceThreshold(
                PerformanceMetric.MEMORY_USAGE, 80.0, 95.0, "cleanup_memory"
            ),
            PerformanceThreshold(
                PerformanceMetric.RESPONSE_TIME, 1.0, 5.0, "optimize_queries"
            ),
            PerformanceThreshold(
                PerformanceMetric.ERROR_RATE, 5.0, 10.0, "investigate_errors"
            ),
        ]

    def start_monitoring(self) -> None:
        """Запустить мониторинг производительности."""
        if not self.running:
            self.running = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            self.logger.info("Мониторинг производительности запущен")

    def stop_monitoring(self) -> None:
        """Остановить мониторинг производительности."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        self.logger.info("Мониторинг производительности остановлен")

    def _monitor_loop(self) -> None:
        """Основной цикл мониторинга."""
        while self.running:
            try:
                self._collect_metrics()
                time.sleep(self.collection_interval)
            except Exception as e:
                self.logger.error(f"Ошибка в цикле мониторинга: {e}")

    def _collect_metrics(self) -> None:
        """Сбор метрик производительности."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self._record_metric(PerformanceMetric.CPU_USAGE, cpu_percent)

            # Memory usage
            memory = psutil.virtual_memory()
            self._record_metric(PerformanceMetric.MEMORY_USAGE, memory.percent)

            # Проверка пороговых значений
            self._check_thresholds()

        except Exception as e:
            self.logger.error(f"Ошибка сбора метрик: {e}")

    def _record_metric(
        self,
        metric_type: PerformanceMetric,
        value: float,
        context: Dict[str, Any] = None,
    ) -> None:
        """Записать метрику производительности."""
        with self.lock:
            stat = PerformanceStats(
                metric_type=metric_type,
                value=value,
                timestamp=time.time(),
                context=context or {},
            )
            self.stats.append(stat)

            # Ограничение размера буфера
            if len(self.stats) > 10000:
                self.stats = self.stats[-5000:]

    def _check_thresholds(self) -> None:
        """Проверить пороговые значения."""
        if not self.stats:
            return

        latest_stats = {}
        for stat in self.stats[-10:]:  # Последние 10 записей
            latest_stats[stat.metric_type] = stat.value

        for threshold in self.thresholds:
            if threshold.metric_type in latest_stats:
                value = latest_stats[threshold.metric_type]
                if value >= threshold.critical_threshold:
                    self.logger.critical(
                        f"КРИТИЧЕСКИЙ уровень {threshold.metric_type.value}: "
                        f"{value}% "
                        f"(порог: {threshold.critical_threshold}%)"
                    )
                    if threshold.action:
                        self._execute_action(threshold.action)
                elif value >= threshold.warning_threshold:
                    self.logger.warning(
                        f"ПРЕДУПРЕЖДЕНИЕ {threshold.metric_type.value}: "
                        f"{value}% "
                        f"(порог: {threshold.warning_threshold}%)"
                    )

    def _execute_action(self, action: str) -> None:
        """Выполнить действие при превышении порога."""
        if action == "scale_up":
            self.logger.info("Рекомендация: увеличить ресурсы")
        elif action == "cleanup_memory":
            self.logger.info("Рекомендация: очистить память")
            gc.collect()
        elif action == "optimize_queries":
            self.logger.info("Рекомендация: оптимизировать запросы")
        elif action == "investigate_errors":
            self.logger.info("Рекомендация: исследовать ошибки")

    def get_performance_summary(self) -> Dict[str, Any]:
        """Получить сводку производительности."""
        with self.lock:
            if not self.stats:
                return {}

            summary = {}
            for metric_type in PerformanceMetric:
                metric_stats = [
                    s for s in self.stats if s.metric_type == metric_type
                ]
                if metric_stats:
                    values = [s.value for s in metric_stats]
                    summary[metric_type.value] = {
                        "current": values[-1] if values else 0,
                        "average": sum(values) / len(values),
                        "min": min(values),
                        "max": max(values),
                        "count": len(values),
                    }

            return summary

    def get_recent_metrics(
        self, metric_type: PerformanceMetric, count: int = 100
    ) -> List[PerformanceStats]:
        """Получить последние метрики определенного типа."""
        with self.lock:
            metric_stats = [
                s for s in self.stats if s.metric_type == metric_type
            ]
            return metric_stats[-count:]


class PerformanceOptimizer:
    """Основной класс оптимизатора производительности."""

    def __init__(self, max_connections: int = 10):
        self.connection_pool = ConnectionPool(max_connections)
        self.query_optimizer = QueryOptimizer()
        self.performance_monitor = PerformanceMonitor()
        self.logger = logging.getLogger(__name__)

        # Кэш для часто используемых данных
        self.data_cache: Dict[str, Any] = {}
        self.cache_ttl: Dict[str, float] = {}
        self.cache_lock = threading.RLock()

        # Пул потоков для CPU-интенсивных задач
        self.thread_pool = ThreadPoolExecutor(max_workers=4)

        # Пул процессов для изолированных задач
        self.process_pool = ProcessPoolExecutor(max_workers=2)

    def start(self) -> None:
        """Запустить оптимизатор производительности."""
        self.performance_monitor.start_monitoring()
        self.logger.info("Оптимизатор производительности запущен")

    def stop(self) -> None:
        """Остановить оптимизатор производительности."""
        self.performance_monitor.stop_monitoring()
        self.connection_pool.close_all()
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)
        self.logger.info("Оптимизатор производительности остановлен")

    def optimize_database_query(
        self, query: str, params: Dict[str, Any] = None
    ) -> str:
        """Оптимизировать запрос к базе данных."""
        return self.query_optimizer.optimize_query(query, params)

    def cache_data(self, key: str, data: Any, ttl: int = 300) -> None:
        """Кэшировать данные."""
        with self.cache_lock:
            self.data_cache[key] = data
            self.cache_ttl[key] = time.time() + ttl

    def get_cached_data(self, key: str) -> Optional[Any]:
        """Получить кэшированные данные."""
        with self.cache_lock:
            if key in self.data_cache:
                if time.time() < self.cache_ttl.get(key, 0):
                    return self.data_cache[key]
                else:
                    del self.data_cache[key]
                    del self.cache_ttl[key]
            return None

    def execute_async(self, func: Callable, *args, **kwargs) -> Any:
        """Выполнить функцию асинхронно в пуле потоков."""
        loop = asyncio.get_event_loop()
        return loop.run_in_executor(self.thread_pool, func, *args, **kwargs)

    def execute_isolated(self, func: Callable, *args, **kwargs) -> Any:
        """Выполнить функцию в изолированном процессе."""
        loop = asyncio.get_event_loop()
        return loop.run_in_executor(self.process_pool, func, *args, **kwargs)

    def get_connection(self) -> Optional[Any]:
        """Получить соединение из пула."""
        return self.connection_pool.get_connection()

    def return_connection(self, connection: Any) -> None:
        """Вернуть соединение в пул."""
        self.connection_pool.return_connection(connection)

    def get_performance_stats(self) -> Dict[str, Any]:
        """Получить статистику производительности."""
        return self.performance_monitor.get_performance_summary()

    def get_slow_queries(self, threshold: float = 1.0) -> List[Dict[str, Any]]:
        """Получить список медленных запросов."""
        return self.query_optimizer.get_slow_queries(threshold)

    def cleanup_cache(self) -> int:
        """Очистить устаревший кэш."""
        with self.cache_lock:
            current_time = time.time()
            expired_keys = [
                key
                for key, ttl in self.cache_ttl.items()
                if current_time >= ttl
            ]

            for key in expired_keys:
                if key in self.data_cache:
                    del self.data_cache[key]
                del self.cache_ttl[key]

            return len(expired_keys)

    def optimize_memory(self) -> Dict[str, Any]:
        """Оптимизировать использование памяти."""
        # Очистка кэша
        cache_cleaned = self.cleanup_cache()

        # Принудительная сборка мусора
        gc.collect()

        # Получение статистики памяти
        memory_info = psutil.virtual_memory()

        return {
            "cache_cleaned": cache_cleaned,
            "memory_usage_before": memory_info.percent,
            "memory_available": memory_info.available,
            "memory_total": memory_info.total,
        }


def performance_monitor(metric_type: PerformanceMetric):
    """Декоратор для мониторинга производительности функций."""

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time

                # Запись метрики (если есть доступ к оптимизатору)
                if hasattr(args[0], "performance_optimizer"):
                    args[
                        0
                    ].performance_optimizer.performance_monitor._record_metric(
                        metric_type,
                        execution_time,
                        {"function": func.__name__},
                    )

                return result
            except Exception as e:
                execution_time = time.time() - start_time
                # Запись ошибки
                if hasattr(args[0], "performance_optimizer"):
                    args[
                        0
                    ].performance_optimizer.performance_monitor._record_metric(
                        PerformanceMetric.ERROR_RATE,
                        1.0,
                        {"function": func.__name__, "error": str(e)},
                    )
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time

                # Запись метрики (если есть доступ к оптимизатору)
                if hasattr(args[0], "performance_optimizer"):
                    args[
                        0
                    ].performance_optimizer.performance_monitor._record_metric(
                        metric_type,
                        execution_time,
                        {"function": func.__name__},
                    )

                return result
            except Exception as e:
                execution_time = time.time() - start_time
                # Запись ошибки
                if hasattr(args[0], "performance_optimizer"):
                    args[
                        0
                    ].performance_optimizer.performance_monitor._record_metric(
                        PerformanceMetric.ERROR_RATE,
                        1.0,
                        {"function": func.__name__, "error": str(e)},
                    )
                raise

        return (
            async_wrapper
            if asyncio.iscoroutinefunction(func)
            else sync_wrapper
        )

    return decorator
