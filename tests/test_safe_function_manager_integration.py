# -*- coding: utf-8 -*-
"""
Тесты интеграции SafeFunctionManager с PerformanceOptimizer
"""

import unittest
import time
from datetime import datetime

from security.safe_function_manager import SafeFunctionManager
from security.reactive.performance_optimizer import PerformanceOptimizer, OptimizationType, OptimizationLevel


class TestSafeFunctionManagerIntegration(unittest.TestCase):
    """Тесты интеграции SafeFunctionManager с PerformanceOptimizer"""
    
    def setUp(self):
        """Настройка тестов"""
        self.manager = SafeFunctionManager("TestManager")
    
    def tearDown(self):
        """Очистка после тестов"""
        if hasattr(self.manager, 'status') and self.manager.status.value == "running":
            self.manager.stop()
    
    def test_initialization_with_performance_optimizer(self):
        """Тест инициализации с Performance Optimizer"""
        result = self.manager.initialize()
        
        self.assertTrue(result)
        self.assertEqual(self.manager.status.value, "running")
        self.assertIsNotNone(self.manager.performance_optimizer)
        self.assertEqual(self.manager.performance_optimizer.name, "SafeFunctionManagerOptimizer")
    
    def test_performance_optimizer_status(self):
        """Тест статуса Performance Optimizer"""
        self.manager.initialize()
        
        status = self.manager.performance_optimizer.get_status()
        
        self.assertIsInstance(status, dict)
        self.assertIn("name", status)
        self.assertIn("status", status)
        self.assertIn("monitoring_active", status)
        self.assertIn("is_optimizing", status)
        self.assertIn("optimization_count", status)
        
        self.assertEqual(status["name"], "SafeFunctionManagerOptimizer")
        self.assertEqual(status["status"], "running")
        self.assertTrue(status["monitoring_active"])
        self.assertFalse(status["is_optimizing"])
    
    def test_performance_report(self):
        """Тест получения отчета о производительности"""
        self.manager.initialize()
        
        report = self.manager.get_performance_report()
        
        self.assertIsInstance(report, dict)
        self.assertIn("function_manager_stats", report)
        self.assertIn("performance_optimizer_report", report)
        self.assertIn("timestamp", report)
        
        # Проверка статистики функций
        function_stats = report["function_manager_stats"]
        self.assertIn("total_functions", function_stats)
        self.assertIn("enabled_functions", function_stats)
        self.assertIn("disabled_functions", function_stats)
        self.assertIn("total_executions", function_stats)
        self.assertIn("successful_executions", function_stats)
        self.assertIn("failed_executions", function_stats)
        self.assertIn("success_rate", function_stats)
        
        # Проверка отчета Performance Optimizer
        performance_report = report["performance_optimizer_report"]
        self.assertIn("current_metrics", performance_report)
        self.assertIn("baseline_metrics", performance_report)
        self.assertIn("optimization_stats", performance_report)
        self.assertIn("monitoring_active", performance_report)
        self.assertIn("is_optimizing", performance_report)
    
    def test_performance_optimization(self):
        """Тест оптимизации производительности"""
        self.manager.initialize()
        
        # Выполняем оптимизацию CPU
        result = self.manager.performance_optimizer.optimize(OptimizationType.CPU, OptimizationLevel.LOW)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.optimization_type, OptimizationType.CPU)
        self.assertEqual(result.level, OptimizationLevel.LOW)
        self.assertIsInstance(result.improvement_percentage, float)
        self.assertIsInstance(result.success, bool)
        self.assertIsInstance(result.optimization_time, float)
    
    def test_performance_optimization_history(self):
        """Тест истории оптимизаций"""
        self.manager.initialize()
        
        # Выполняем несколько оптимизаций
        self.manager.performance_optimizer.optimize(OptimizationType.CPU, OptimizationLevel.LOW)
        self.manager.performance_optimizer.optimize(OptimizationType.MEMORY, OptimizationLevel.MEDIUM)
        self.manager.performance_optimizer.optimize(OptimizationType.DISK, OptimizationLevel.HIGH)
        
        # Проверяем историю
        history = self.manager.performance_optimizer.optimization_history
        self.assertEqual(len(history), 3)
        
        # Проверяем типы оптимизаций
        types = [r.optimization_type for r in history]
        self.assertIn(OptimizationType.CPU, types)
        self.assertIn(OptimizationType.MEMORY, types)
        self.assertIn(OptimizationType.DISK, types)
    
    def test_stop_with_performance_optimizer(self):
        """Тест остановки с Performance Optimizer"""
        self.manager.initialize()
        
        # Останавливаем менеджер
        result = self.manager.stop()
        
        self.assertTrue(result)
        self.assertEqual(self.manager.status.value, "stopped")
        
        # Проверяем, что Performance Optimizer тоже остановлен
        self.assertEqual(self.manager.performance_optimizer.status.value, "stopped")
    
    def test_performance_optimizer_configuration(self):
        """Тест конфигурации Performance Optimizer"""
        self.manager.initialize()
        
        config = self.manager.performance_optimizer.optimization_config
        
        self.assertIsInstance(config, dict)
        self.assertIn("cpu_threshold", config)
        self.assertIn("memory_threshold", config)
        self.assertIn("disk_threshold", config)
        self.assertIn("response_time_threshold", config)
        self.assertIn("error_rate_threshold", config)
        self.assertIn("optimization_interval", config)
        self.assertIn("enable_auto_optimization", config)
        
        # Проверяем значения по умолчанию
        self.assertEqual(config["cpu_threshold"], 80.0)
        self.assertEqual(config["memory_threshold"], 85.0)
        self.assertEqual(config["disk_threshold"], 90.0)
        self.assertEqual(config["response_time_threshold"], 1000.0)
        self.assertEqual(config["error_rate_threshold"], 5.0)
        self.assertEqual(config["optimization_interval"], 30)
        self.assertTrue(config["enable_auto_optimization"])
    
    def test_performance_metrics_collection(self):
        """Тест сбора метрик производительности"""
        self.manager.initialize()
        
        # Собираем метрики
        metrics = self.manager.performance_optimizer._collect_performance_metrics()
        
        self.assertIsNotNone(metrics)
        self.assertIsInstance(metrics.cpu_usage, float)
        self.assertIsInstance(metrics.memory_usage, float)
        self.assertIsInstance(metrics.disk_usage, float)
        self.assertIsInstance(metrics.network_io, float)
        self.assertIsInstance(metrics.response_time, float)
        self.assertIsInstance(metrics.throughput, float)
        self.assertIsInstance(metrics.error_rate, float)
        self.assertIsInstance(metrics.timestamp, datetime)
        
        # Проверяем диапазоны значений
        self.assertGreaterEqual(metrics.cpu_usage, 0.0)
        self.assertLessEqual(metrics.cpu_usage, 100.0)
        self.assertGreaterEqual(metrics.memory_usage, 0.0)
        self.assertLessEqual(metrics.memory_usage, 100.0)
        self.assertGreaterEqual(metrics.disk_usage, 0.0)
        self.assertLessEqual(metrics.disk_usage, 100.0)
        self.assertGreaterEqual(metrics.network_io, 0.0)
        self.assertGreaterEqual(metrics.response_time, 0.0)
        self.assertGreaterEqual(metrics.throughput, 0.0)
        self.assertGreaterEqual(metrics.error_rate, 0.0)


if __name__ == "__main__":
    unittest.main()