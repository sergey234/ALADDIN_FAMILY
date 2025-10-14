"""
Тесты для системы оптимизации производительности ParentalControlBot.
"""

import pytest
import asyncio
import time
import threading
from unittest.mock import Mock, patch

from security.bots.components.performance_optimizer import (
    PerformanceOptimizer, PerformanceMonitor, QueryOptimizer, ConnectionPool,
    PerformanceMetric, PerformanceStats, PerformanceThreshold,
    performance_monitor
)


class TestPerformanceOptimizer:
    """Тесты для PerformanceOptimizer."""
    
    def test_initialization(self):
        """Тест инициализации оптимизатора."""
        optimizer = PerformanceOptimizer(max_connections=5)
        
        assert optimizer.connection_pool.max_connections == 5
        assert optimizer.connection_pool.min_connections == 2
        assert isinstance(optimizer.query_optimizer, QueryOptimizer)
        assert isinstance(optimizer.performance_monitor, PerformanceMonitor)
        assert len(optimizer.data_cache) == 0
        assert len(optimizer.cache_ttl) == 0
    
    def test_start_stop(self):
        """Тест запуска и остановки оптимизатора."""
        optimizer = PerformanceOptimizer()
        
        # Запуск
        optimizer.start()
        assert optimizer.performance_monitor.running is True
        
        # Остановка
        optimizer.stop()
        assert optimizer.performance_monitor.running is False
    
    def test_cache_operations(self):
        """Тест операций с кэшем."""
        optimizer = PerformanceOptimizer()
        
        # Кэширование данных
        test_data = {"key": "value", "number": 42}
        optimizer.cache_data("test_key", test_data, ttl=1)
        
        # Получение кэшированных данных
        cached_data = optimizer.get_cached_data("test_key")
        assert cached_data == test_data
        
        # Получение несуществующих данных
        non_existent = optimizer.get_cached_data("non_existent")
        assert non_existent is None
    
    def test_cache_expiration(self):
        """Тест истечения срока действия кэша."""
        optimizer = PerformanceOptimizer()
        
        # Кэширование с коротким TTL
        optimizer.cache_data("expired_key", "test_value", ttl=0.1)
        
        # Данные должны быть доступны сразу
        assert optimizer.get_cached_data("expired_key") == "test_value"
        
        # Ждем истечения TTL
        time.sleep(0.2)
        
        # Данные должны быть удалены
        assert optimizer.get_cached_data("expired_key") is None
    
    def test_cleanup_cache(self):
        """Тест очистки кэша."""
        optimizer = PerformanceOptimizer()
        
        # Добавляем данные с разными TTL
        optimizer.cache_data("valid_key", "valid_value", ttl=300)
        optimizer.cache_data("expired_key", "expired_value", ttl=0.1)
        
        # Ждем истечения одного ключа
        time.sleep(0.2)
        
        # Очистка кэша
        cleaned_count = optimizer.cleanup_cache()
        
        # Должен быть очищен один ключ
        assert cleaned_count == 1
        assert optimizer.get_cached_data("valid_key") == "valid_value"
        assert optimizer.get_cached_data("expired_key") is None
    
    def test_optimize_memory(self):
        """Тест оптимизации памяти."""
        optimizer = PerformanceOptimizer()
        
        # Добавляем данные в кэш
        for i in range(10):
            optimizer.cache_data(f"key_{i}", f"value_{i}", ttl=300)
        
        # Оптимизация памяти
        result = optimizer.optimize_memory()
        
        assert "cache_cleaned" in result
        assert "memory_usage_before" in result
        assert "memory_available" in result
        assert "memory_total" in result
        assert result["cache_cleaned"] == 0  # Нет истекших ключей
    
    def test_get_performance_stats(self):
        """Тест получения статистики производительности."""
        optimizer = PerformanceOptimizer()
        optimizer.start()
        
        # Ждем сбора метрик
        time.sleep(1.5)
        
        stats = optimizer.get_performance_stats()
        
        # Должны быть метрики CPU и памяти
        assert "cpu_usage" in stats
        assert "memory_usage" in stats
        
        optimizer.stop()
    
    def test_get_slow_queries(self):
        """Тест получения медленных запросов."""
        optimizer = PerformanceOptimizer()
        
        # Добавляем статистику запросов
        optimizer.query_optimizer.record_query_stats("SELECT * FROM users", 2.5, True)
        optimizer.query_optimizer.record_query_stats("SELECT * FROM posts", 0.5, True)
        
        # Получаем медленные запросы
        slow_queries = optimizer.get_slow_queries(threshold=1.0)
        
        assert len(slow_queries) == 1
        assert slow_queries[0]["query"] == "SELECT * FROM users"
        assert slow_queries[0]["avg_time"] == 2.5


class TestQueryOptimizer:
    """Тесты для QueryOptimizer."""
    
    def test_optimize_query(self):
        """Тест оптимизации запросов."""
        optimizer = QueryOptimizer()
        
        # Простой запрос
        query = "SELECT * FROM users WHERE id = 1"
        optimized = optimizer.optimize_query(query)
        
        assert optimized == "SELECT * FROM users WHERE id = 1"
        
        # Запрос с лишними пробелами
        messy_query = "  SELECT   *   FROM   users   WHERE   id   =   1  "
        optimized = optimizer.optimize_query(messy_query)
        
        assert optimized == "SELECT * FROM users WHERE id = 1"
    
    def test_cache_query_result(self):
        """Тест кэширования результатов запросов."""
        optimizer = QueryOptimizer()
        
        # Кэширование результата
        result = [{"id": 1, "name": "John"}]
        optimizer.cache_query_result("SELECT * FROM users", result, ttl=300)
        
        # Получение кэшированного результата
        cached_result = optimizer.get_cached_result("SELECT * FROM users")
        assert cached_result == result
    
    def test_cache_query_with_params(self):
        """Тест кэширования запросов с параметрами."""
        optimizer = QueryOptimizer()
        
        # Кэширование с параметрами
        result = [{"id": 1, "name": "John"}]
        params = {"user_id": 1}
        optimizer.cache_query_result("SELECT * FROM users WHERE id = :user_id", result, ttl=300)
        
        # Получение с теми же параметрами
        cached_result = optimizer.get_cached_result("SELECT * FROM users WHERE id = :user_id", params)
        assert cached_result == result
        
        # Получение с другими параметрами
        other_params = {"user_id": 2}
        cached_result = optimizer.get_cached_result("SELECT * FROM users WHERE id = :user_id", other_params)
        assert cached_result is None
    
    def test_query_stats(self):
        """Тест статистики запросов."""
        optimizer = QueryOptimizer()
        
        # Запись статистики
        optimizer.record_query_stats("SELECT * FROM users", 1.5, True)
        optimizer.record_query_stats("SELECT * FROM users", 2.0, True)
        optimizer.record_query_stats("SELECT * FROM users", 0.5, False)
        
        # Получение медленных запросов
        slow_queries = optimizer.get_slow_queries(threshold=1.0)
        
        assert len(slow_queries) == 1
        assert slow_queries[0]["query"] == "SELECT * FROM users"
        assert slow_queries[0]["count"] == 3
        assert slow_queries[0]["avg_time"] == 1.33  # (1.5 + 2.0 + 0.5) / 3
        assert slow_queries[0]["max_time"] == 2.0
        assert slow_queries[0]["min_time"] == 0.5
        assert slow_queries[0]["success_count"] == 2
        assert slow_queries[0]["error_count"] == 1


class TestConnectionPool:
    """Тесты для ConnectionPool."""
    
    def test_initialization(self):
        """Тест инициализации пула соединений."""
        pool = ConnectionPool(max_connections=5, min_connections=2)
        
        assert pool.max_connections == 5
        assert pool.min_connections == 2
        assert len(pool.connections) == 0
        assert len(pool.available_connections) == 0
    
    def test_get_return_connection(self):
        """Тест получения и возврата соединений."""
        pool = ConnectionPool(max_connections=3)
        
        # Получение соединений
        conn1 = pool.get_connection()
        conn2 = pool.get_connection()
        
        assert conn1 is not None
        assert conn2 is not None
        assert conn1 != conn2
        assert len(pool.connections) == 2
        assert len(pool.available_connections) == 0
        
        # Возврат соединений
        pool.return_connection(conn1)
        pool.return_connection(conn2)
        
        assert len(pool.available_connections) == 2
        
        # Получение возвращенного соединения
        conn3 = pool.get_connection()
        assert conn3 in [conn1, conn2]
        assert len(pool.available_connections) == 1
    
    def test_max_connections(self):
        """Тест ограничения максимального количества соединений."""
        pool = ConnectionPool(max_connections=2)
        
        # Получение максимального количества соединений
        conn1 = pool.get_connection()
        conn2 = pool.get_connection()
        conn3 = pool.get_connection()  # Должно вернуть None
        
        assert conn1 is not None
        assert conn2 is not None
        assert conn3 is None
        assert len(pool.connections) == 2
    
    def test_close_all(self):
        """Тест закрытия всех соединений."""
        pool = ConnectionPool(max_connections=3)
        
        # Получение соединений
        conn1 = pool.get_connection()
        conn2 = pool.get_connection()
        
        # Возврат одного соединения
        pool.return_connection(conn1)
        
        # Закрытие всех соединений
        pool.close_all()
        
        assert len(pool.connections) == 0
        assert len(pool.available_connections) == 0


class TestPerformanceMonitor:
    """Тесты для PerformanceMonitor."""
    
    def test_initialization(self):
        """Тест инициализации монитора."""
        monitor = PerformanceMonitor(collection_interval=0.1)
        
        assert monitor.collection_interval == 0.1
        assert len(monitor.stats) == 0
        assert len(monitor.thresholds) > 0
        assert monitor.running is False
    
    def test_start_stop_monitoring(self):
        """Тест запуска и остановки мониторинга."""
        monitor = PerformanceMonitor(collection_interval=0.1)
        
        # Запуск
        monitor.start_monitoring()
        assert monitor.running is True
        
        # Ждем сбора метрик
        time.sleep(0.5)
        
        # Остановка
        monitor.stop_monitoring()
        assert monitor.running is False
        
        # Должны быть собраны метрики
        assert len(monitor.stats) > 0
    
    def test_record_metric(self):
        """Тест записи метрик."""
        monitor = PerformanceMonitor()
        
        # Запись метрики
        monitor._record_metric(PerformanceMetric.CPU_USAGE, 50.0, {"test": "context"})
        
        assert len(monitor.stats) == 1
        assert monitor.stats[0].metric_type == PerformanceMetric.CPU_USAGE
        assert monitor.stats[0].value == 50.0
        assert monitor.stats[0].context == {"test": "context"}
    
    def test_get_performance_summary(self):
        """Тест получения сводки производительности."""
        monitor = PerformanceMonitor()
        
        # Добавление метрик
        monitor._record_metric(PerformanceMetric.CPU_USAGE, 30.0)
        monitor._record_metric(PerformanceMetric.CPU_USAGE, 70.0)
        monitor._record_metric(PerformanceMetric.MEMORY_USAGE, 50.0)
        
        # Получение сводки
        summary = monitor.get_performance_summary()
        
        assert "cpu_usage" in summary
        assert "memory_usage" in summary
        
        cpu_stats = summary["cpu_usage"]
        assert cpu_stats["current"] == 70.0
        assert cpu_stats["average"] == 50.0
        assert cpu_stats["min"] == 30.0
        assert cpu_stats["max"] == 70.0
        assert cpu_stats["count"] == 2
    
    def test_get_recent_metrics(self):
        """Тест получения последних метрик."""
        monitor = PerformanceMonitor()
        
        # Добавление метрик
        for i in range(5):
            monitor._record_metric(PerformanceMetric.CPU_USAGE, float(i * 10))
        
        # Получение последних 3 метрик
        recent = monitor.get_recent_metrics(PerformanceMetric.CPU_USAGE, count=3)
        
        assert len(recent) == 3
        assert recent[0].value == 20.0  # Третья с конца
        assert recent[1].value == 30.0  # Вторая с конца
        assert recent[2].value == 40.0  # Последняя


class TestPerformanceDecorator:
    """Тесты для декоратора мониторинга производительности."""
    
    def test_sync_function_decorator(self):
        """Тест декоратора для синхронной функции."""
        class MockBot:
            def __init__(self):
                self.performance_optimizer = Mock()
                self.performance_optimizer.performance_monitor = Mock()
                self.performance_optimizer.performance_monitor._record_metric = Mock()
        
        @performance_monitor(PerformanceMetric.RESPONSE_TIME)
        def test_function(self, value):
            time.sleep(0.1)
            return value * 2
        
        bot = MockBot()
        result = test_function(bot, 5)
        
        assert result == 10
        assert bot.performance_optimizer.performance_monitor._record_metric.called
    
    def test_async_function_decorator(self):
        """Тест декоратора для асинхронной функции."""
        class MockBot:
            def __init__(self):
                self.performance_optimizer = Mock()
                self.performance_optimizer.performance_monitor = Mock()
                self.performance_optimizer.performance_monitor._record_metric = Mock()
        
        @performance_monitor(PerformanceMetric.RESPONSE_TIME)
        async def test_async_function(self, value):
            await asyncio.sleep(0.1)
            return value * 2
        
        async def run_test():
            bot = MockBot()
            result = await test_async_function(bot, 5)
            
            assert result == 10
            assert bot.performance_optimizer.performance_monitor._record_metric.called
        
        asyncio.run(run_test())
    
    def test_decorator_with_exception(self):
        """Тест декоратора с исключением."""
        class MockBot:
            def __init__(self):
                self.performance_optimizer = Mock()
                self.performance_optimizer.performance_monitor = Mock()
                self.performance_optimizer.performance_monitor._record_metric = Mock()
        
        @performance_monitor(PerformanceMetric.RESPONSE_TIME)
        def test_function_with_error(self):
            raise ValueError("Test error")
        
        bot = MockBot()
        
        with pytest.raises(ValueError):
            test_function_with_error(bot)
        
        # Должна быть записана метрика ошибки
        assert bot.performance_optimizer.performance_monitor._record_metric.called


class TestPerformanceIntegration:
    """Интеграционные тесты производительности."""
    
    def test_full_optimization_cycle(self):
        """Тест полного цикла оптимизации."""
        optimizer = PerformanceOptimizer(max_connections=3)
        
        try:
            # Запуск оптимизатора
            optimizer.start()
            
            # Кэширование данных
            optimizer.cache_data("test_key", {"data": "test"}, ttl=300)
            
            # Получение соединений
            conn1 = optimizer.get_connection()
            conn2 = optimizer.get_connection()
            
            assert conn1 is not None
            assert conn2 is not None
            
            # Возврат соединений
            optimizer.return_connection(conn1)
            optimizer.return_connection(conn2)
            
            # Получение статистики
            stats = optimizer.get_performance_stats()
            assert isinstance(stats, dict)
            
            # Очистка кэша
            cleaned = optimizer.cleanup_cache()
            assert cleaned == 0  # Нет истекших ключей
            
            # Оптимизация памяти
            memory_result = optimizer.optimize_memory()
            assert "cache_cleaned" in memory_result
            
        finally:
            optimizer.stop()
    
    def test_concurrent_operations(self):
        """Тест конкурентных операций."""
        optimizer = PerformanceOptimizer(max_connections=5)
        
        def worker(worker_id):
            # Кэширование данных
            optimizer.cache_data(f"key_{worker_id}", f"value_{worker_id}", ttl=300)
            
            # Получение соединения
            conn = optimizer.get_connection()
            if conn:
                time.sleep(0.1)  # Имитация работы
                optimizer.return_connection(conn)
            
            return worker_id
        
        # Запуск нескольких потоков
        threads = []
        for i in range(10):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Ожидание завершения
        for thread in threads:
            thread.join()
        
        # Проверка результатов
        assert len(optimizer.data_cache) == 10
        assert len(optimizer.connection_pool.connections) <= 5


if __name__ == "__main__":
    pytest.main([__file__])