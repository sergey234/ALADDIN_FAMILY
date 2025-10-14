# -*- coding: utf-8 -*-
"""
Тесты для PerformanceOptimizer
"""

import unittest
import time
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from security.reactive.performance_optimizer import (
    PerformanceOptimizer,
    OptimizationType,
    OptimizationLevel,
    PerformanceMetrics,
    OptimizationResult
)


class TestPerformanceOptimizer(unittest.TestCase):
    """Тесты для PerformanceOptimizer"""
    
    def setUp(self):
        """Настройка тестов"""
        self.optimizer = PerformanceOptimizer("TestOptimizer")
    
    def tearDown(self):
        """Очистка после тестов"""
        if self.optimizer.status.value == "active":
            self.optimizer.stop()
    
    def test_initialization(self):
        """Тест инициализации"""
        self.assertEqual(self.optimizer.name, "TestOptimizer")
        self.assertIsNotNone(self.optimizer.optimization_config)
        self.assertFalse(self.optimizer.is_optimizing)
        self.assertEqual(len(self.optimizer.optimization_history), 0)
    
    def test_initialize(self):
        """Тест инициализации оптимизатора"""
        result = self.optimizer.initialize()
        self.assertTrue(result)
        self.assertEqual(self.optimizer.status.value, "running")
        self.assertIsNotNone(self.optimizer.baseline_metrics)
    
    def test_collect_performance_metrics(self):
        """Тест сбора метрик производительности"""
        metrics = self.optimizer._collect_performance_metrics()
        
        self.assertIsInstance(metrics, PerformanceMetrics)
        self.assertIsInstance(metrics.cpu_usage, float)
        self.assertIsInstance(metrics.memory_usage, float)
        self.assertIsInstance(metrics.disk_usage, float)
        self.assertIsInstance(metrics.network_io, float)
        self.assertIsInstance(metrics.response_time, float)
        self.assertIsInstance(metrics.throughput, float)
        self.assertIsInstance(metrics.error_rate, float)
        self.assertIsInstance(metrics.timestamp, datetime)
    
    def test_measure_response_time(self):
        """Тест измерения времени отклика"""
        response_time = self.optimizer._measure_response_time()
        self.assertIsInstance(response_time, float)
        self.assertGreaterEqual(response_time, 0)
    
    def test_measure_throughput(self):
        """Тест измерения пропускной способности"""
        throughput = self.optimizer._measure_throughput()
        self.assertIsInstance(throughput, float)
        self.assertGreaterEqual(throughput, 0)
    
    def test_measure_error_rate(self):
        """Тест измерения частоты ошибок"""
        error_rate = self.optimizer._measure_error_rate()
        self.assertIsInstance(error_rate, float)
        self.assertGreaterEqual(error_rate, 0)
    
    def test_needs_optimization_false(self):
        """Тест проверки необходимости оптимизации - не нужна"""
        # Создаем метрики с низкими значениями
        self.optimizer.current_metrics = PerformanceMetrics(
            cpu_usage=50.0,
            memory_usage=60.0,
            disk_usage=70.0,
            network_io=100000,
            response_time=500.0,
            throughput=1000.0,
            error_rate=1.0,
            timestamp=datetime.now()
        )
        
        result = self.optimizer._needs_optimization()
        self.assertFalse(result)
    
    def test_needs_optimization_true_cpu(self):
        """Тест проверки необходимости оптимизации - нужна по CPU"""
        # Создаем метрики с высоким CPU
        self.optimizer.current_metrics = PerformanceMetrics(
            cpu_usage=90.0,  # Выше порога 80%
            memory_usage=60.0,
            disk_usage=70.0,
            network_io=100000,
            response_time=500.0,
            throughput=1000.0,
            error_rate=1.0,
            timestamp=datetime.now()
        )
        
        result = self.optimizer._needs_optimization()
        self.assertTrue(result)
    
    def test_needs_optimization_true_memory(self):
        """Тест проверки необходимости оптимизации - нужна по памяти"""
        # Создаем метрики с высоким использованием памяти
        self.optimizer.current_metrics = PerformanceMetrics(
            cpu_usage=50.0,
            memory_usage=90.0,  # Выше порога 85%
            disk_usage=70.0,
            network_io=100000,
            response_time=500.0,
            throughput=1000.0,
            error_rate=1.0,
            timestamp=datetime.now()
        )
        
        result = self.optimizer._needs_optimization()
        self.assertTrue(result)
    
    def test_needs_optimization_true_response_time(self):
        """Тест проверки необходимости оптимизации - нужна по времени отклика"""
        # Создаем метрики с высоким временем отклика
        self.optimizer.current_metrics = PerformanceMetrics(
            cpu_usage=50.0,
            memory_usage=60.0,
            disk_usage=70.0,
            network_io=100000,
            response_time=1500.0,  # Выше порога 1000мс
            throughput=1000.0,
            error_rate=1.0,
            timestamp=datetime.now()
        )
        
        result = self.optimizer._needs_optimization()
        self.assertTrue(result)
    
    def test_determine_optimization_types_cpu(self):
        """Тест определения типов оптимизации - CPU"""
        self.optimizer.current_metrics = PerformanceMetrics(
            cpu_usage=90.0,  # Выше порога
            memory_usage=60.0,
            disk_usage=70.0,
            network_io=100000,
            response_time=500.0,
            throughput=1000.0,
            error_rate=1.0,
            timestamp=datetime.now()
        )
        
        types = self.optimizer._determine_optimization_types()
        self.assertIn(OptimizationType.CPU, types)
    
    def test_determine_optimization_types_memory(self):
        """Тест определения типов оптимизации - память"""
        self.optimizer.current_metrics = PerformanceMetrics(
            cpu_usage=50.0,
            memory_usage=90.0,  # Выше порога
            disk_usage=70.0,
            network_io=100000,
            response_time=500.0,
            throughput=1000.0,
            error_rate=1.0,
            timestamp=datetime.now()
        )
        
        types = self.optimizer._determine_optimization_types()
        self.assertIn(OptimizationType.MEMORY, types)
    
    def test_determine_optimization_types_network(self):
        """Тест определения типов оптимизации - сеть"""
        self.optimizer.current_metrics = PerformanceMetrics(
            cpu_usage=50.0,
            memory_usage=60.0,
            disk_usage=70.0,
            network_io=2000000,  # Выше порога 1MB
            response_time=500.0,
            throughput=1000.0,
            error_rate=1.0,
            timestamp=datetime.now()
        )
        
        types = self.optimizer._determine_optimization_types()
        self.assertIn(OptimizationType.NETWORK, types)
    
    def test_determine_optimization_types_database(self):
        """Тест определения типов оптимизации - база данных"""
        self.optimizer.current_metrics = PerformanceMetrics(
            cpu_usage=50.0,
            memory_usage=60.0,
            disk_usage=70.0,
            network_io=100000,
            response_time=1500.0,  # Выше порога
            throughput=1000.0,
            error_rate=1.0,
            timestamp=datetime.now()
        )
        
        types = self.optimizer._determine_optimization_types()
        self.assertIn(OptimizationType.DATABASE, types)
        self.assertIn(OptimizationType.QUERY, types)
    
    def test_optimize_cpu(self):
        """Тест оптимизации CPU"""
        result = self.optimizer.optimize(OptimizationType.CPU, OptimizationLevel.LOW)
        
        self.assertIsInstance(result, OptimizationResult)
        self.assertEqual(result.optimization_type, OptimizationType.CPU)
        self.assertEqual(result.level, OptimizationLevel.LOW)
        self.assertIsInstance(result.improvement_percentage, float)
        self.assertIsInstance(result.before_metrics, PerformanceMetrics)
        self.assertIsInstance(result.after_metrics, PerformanceMetrics)
        self.assertIsInstance(result.optimization_time, float)
        self.assertIsInstance(result.success, bool)
    
    def test_optimize_memory(self):
        """Тест оптимизации памяти"""
        result = self.optimizer.optimize(OptimizationType.MEMORY, OptimizationLevel.MEDIUM)
        
        self.assertIsInstance(result, OptimizationResult)
        self.assertEqual(result.optimization_type, OptimizationType.MEMORY)
        self.assertEqual(result.level, OptimizationLevel.MEDIUM)
        self.assertIsInstance(result.success, bool)
    
    def test_optimize_disk(self):
        """Тест оптимизации диска"""
        result = self.optimizer.optimize(OptimizationType.DISK, OptimizationLevel.HIGH)
        
        self.assertIsInstance(result, OptimizationResult)
        self.assertEqual(result.optimization_type, OptimizationType.DISK)
        self.assertEqual(result.level, OptimizationLevel.HIGH)
        self.assertIsInstance(result.success, bool)
    
    def test_optimize_network(self):
        """Тест оптимизации сети"""
        result = self.optimizer.optimize(OptimizationType.NETWORK, OptimizationLevel.AGGRESSIVE)
        
        self.assertIsInstance(result, OptimizationResult)
        self.assertEqual(result.optimization_type, OptimizationType.NETWORK)
        self.assertEqual(result.level, OptimizationLevel.AGGRESSIVE)
        self.assertIsInstance(result.success, bool)
    
    def test_optimize_database(self):
        """Тест оптимизации базы данных"""
        result = self.optimizer.optimize(OptimizationType.DATABASE, OptimizationLevel.LOW)
        
        self.assertIsInstance(result, OptimizationResult)
        self.assertEqual(result.optimization_type, OptimizationType.DATABASE)
        self.assertEqual(result.level, OptimizationLevel.LOW)
        self.assertIsInstance(result.success, bool)
    
    def test_optimize_cache(self):
        """Тест оптимизации кэша"""
        result = self.optimizer.optimize(OptimizationType.CACHE, OptimizationLevel.MEDIUM)
        
        self.assertIsInstance(result, OptimizationResult)
        self.assertEqual(result.optimization_type, OptimizationType.CACHE)
        self.assertEqual(result.level, OptimizationLevel.MEDIUM)
        self.assertIsInstance(result.success, bool)
    
    def test_optimize_queries(self):
        """Тест оптимизации запросов"""
        result = self.optimizer.optimize(OptimizationType.QUERY, OptimizationLevel.HIGH)
        
        self.assertIsInstance(result, OptimizationResult)
        self.assertEqual(result.optimization_type, OptimizationType.QUERY)
        self.assertEqual(result.level, OptimizationLevel.HIGH)
        self.assertIsInstance(result.success, bool)
    
    def test_optimize_connections(self):
        """Тест оптимизации соединений"""
        result = self.optimizer.optimize(OptimizationType.CONNECTION, OptimizationLevel.AGGRESSIVE)
        
        self.assertIsInstance(result, OptimizationResult)
        self.assertEqual(result.optimization_type, OptimizationType.CONNECTION)
        self.assertEqual(result.level, OptimizationLevel.AGGRESSIVE)
        self.assertIsInstance(result.success, bool)
    
    def test_calculate_improvement_cpu(self):
        """Тест расчета улучшения - CPU"""
        before = PerformanceMetrics(
            cpu_usage=90.0,
            memory_usage=60.0,
            disk_usage=70.0,
            network_io=100000,
            response_time=500.0,
            throughput=1000.0,
            error_rate=1.0,
            timestamp=datetime.now()
        )
        
        after = PerformanceMetrics(
            cpu_usage=70.0,  # Улучшение на 20%
            memory_usage=60.0,
            disk_usage=70.0,
            network_io=100000,
            response_time=500.0,
            throughput=1000.0,
            error_rate=1.0,
            timestamp=datetime.now()
        )
        
        improvement = self.optimizer._calculate_improvement(before, after, OptimizationType.CPU)
        self.assertAlmostEqual(improvement, 22.22, places=1)  # 20/90 * 100
    
    def test_calculate_improvement_memory(self):
        """Тест расчета улучшения - память"""
        before = PerformanceMetrics(
            cpu_usage=50.0,
            memory_usage=90.0,
            disk_usage=70.0,
            network_io=100000,
            response_time=500.0,
            throughput=1000.0,
            error_rate=1.0,
            timestamp=datetime.now()
        )
        
        after = PerformanceMetrics(
            cpu_usage=50.0,
            memory_usage=70.0,  # Улучшение на 20%
            disk_usage=70.0,
            network_io=100000,
            response_time=500.0,
            throughput=1000.0,
            error_rate=1.0,
            timestamp=datetime.now()
        )
        
        improvement = self.optimizer._calculate_improvement(before, after, OptimizationType.MEMORY)
        self.assertAlmostEqual(improvement, 22.22, places=1)  # 20/90 * 100
    
    def test_calculate_improvement_response_time(self):
        """Тест расчета улучшения - время отклика"""
        before = PerformanceMetrics(
            cpu_usage=50.0,
            memory_usage=60.0,
            disk_usage=70.0,
            network_io=100000,
            response_time=1000.0,
            throughput=1000.0,
            error_rate=1.0,
            timestamp=datetime.now()
        )
        
        after = PerformanceMetrics(
            cpu_usage=50.0,
            memory_usage=60.0,
            disk_usage=70.0,
            network_io=100000,
            response_time=800.0,  # Улучшение на 200мс
            throughput=1000.0,
            error_rate=1.0,
            timestamp=datetime.now()
        )
        
        improvement = self.optimizer._calculate_improvement(before, after, OptimizationType.DATABASE)
        self.assertAlmostEqual(improvement, 20.0, places=1)  # 200/1000 * 100
    
    def test_optimization_history(self):
        """Тест истории оптимизаций"""
        # Выполняем несколько оптимизаций
        self.optimizer.optimize(OptimizationType.CPU, OptimizationLevel.LOW)
        self.optimizer.optimize(OptimizationType.MEMORY, OptimizationLevel.MEDIUM)
        self.optimizer.optimize(OptimizationType.DISK, OptimizationLevel.HIGH)
        
        # Проверяем историю
        self.assertEqual(len(self.optimizer.optimization_history), 3)
        
        # Проверяем типы оптимизаций
        types = [r.optimization_type for r in self.optimizer.optimization_history]
        self.assertIn(OptimizationType.CPU, types)
        self.assertIn(OptimizationType.MEMORY, types)
        self.assertIn(OptimizationType.DISK, types)
    
    def test_get_performance_report(self):
        """Тест получения отчета о производительности"""
        # Инициализируем оптимизатор
        self.optimizer.initialize()
        
        # Выполняем оптимизацию
        self.optimizer.optimize(OptimizationType.CPU, OptimizationLevel.LOW)
        
        # Получаем отчет
        report = self.optimizer.get_performance_report()
        
        self.assertIsInstance(report, dict)
        self.assertIn("current_metrics", report)
        self.assertIn("baseline_metrics", report)
        self.assertIn("optimization_stats", report)
        self.assertIn("recent_optimizations", report)
        self.assertIn("monitoring_active", report)
        self.assertIn("is_optimizing", report)
        self.assertIn("configuration", report)
        
        # Проверяем статистику
        stats = report["optimization_stats"]
        self.assertIn("total_optimizations", stats)
        self.assertIn("successful_optimizations", stats)
        self.assertIn("success_rate", stats)
        self.assertIn("average_improvement", stats)
    
    def test_get_status(self):
        """Тест получения статуса"""
        status = self.optimizer.get_status()
        
        self.assertIsInstance(status, dict)
        self.assertIn("name", status)
        self.assertIn("status", status)
        self.assertIn("security_level", status)
        self.assertIn("monitoring_active", status)
        self.assertIn("is_optimizing", status)
        self.assertIn("optimization_count", status)
        self.assertIn("current_metrics", status)
        self.assertIn("configuration", status)
        
        self.assertEqual(status["name"], "TestOptimizer")
        self.assertEqual(status["optimization_count"], 0)
    
    def test_stop(self):
        """Тест остановки оптимизатора"""
        # Инициализируем
        self.optimizer.initialize()
        
        # Останавливаем
        result = self.optimizer.stop()
        
        self.assertTrue(result)
        self.assertEqual(self.optimizer.status.value, "stopped")
    
    def test_optimization_result_to_dict(self):
        """Тест преобразования результата оптимизации в словарь"""
        result = self.optimizer.optimize(OptimizationType.CPU, OptimizationLevel.LOW)
        result_dict = result.to_dict()
        
        self.assertIsInstance(result_dict, dict)
        self.assertIn("optimization_type", result_dict)
        self.assertIn("level", result_dict)
        self.assertIn("improvement_percentage", result_dict)
        self.assertIn("before_metrics", result_dict)
        self.assertIn("after_metrics", result_dict)
        self.assertIn("optimization_time", result_dict)
        self.assertIn("success", result_dict)
        self.assertIn("error_message", result_dict)
    
    def test_performance_metrics_to_dict(self):
        """Тест преобразования метрик в словарь"""
        metrics = self.optimizer._collect_performance_metrics()
        metrics_dict = metrics.to_dict()
        
        self.assertIsInstance(metrics_dict, dict)
        self.assertIn("cpu_usage", metrics_dict)
        self.assertIn("memory_usage", metrics_dict)
        self.assertIn("disk_usage", metrics_dict)
        self.assertIn("network_io", metrics_dict)
        self.assertIn("response_time", metrics_dict)
        self.assertIn("throughput", metrics_dict)
        self.assertIn("error_rate", metrics_dict)
        self.assertIn("timestamp", metrics_dict)
    
    def test_force_garbage_collection(self):
        """Тест принудительной сборки мусора"""
        # Этот тест проверяет, что метод не вызывает исключений
        try:
            self.optimizer._force_garbage_collection()
            success = True
        except Exception:
            success = False
        
        self.assertTrue(success)
    
    def test_optimization_with_error(self):
        """Тест оптимизации с ошибкой"""
        # Мокаем метод оптимизации, чтобы он вызывал исключение
        with patch.object(self.optimizer, '_optimize_cpu', side_effect=Exception("Test error")):
            result = self.optimizer.optimize(OptimizationType.CPU, OptimizationLevel.LOW)
            
            self.assertIsInstance(result, OptimizationResult)
            self.assertFalse(result.success)
            self.assertIsNotNone(result.error_message)
            self.assertEqual(result.error_message, "Test error")


if __name__ == "__main__":
    unittest.main()