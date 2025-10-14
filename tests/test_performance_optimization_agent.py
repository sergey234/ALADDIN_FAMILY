# -*- coding: utf-8 -*-
"""
Тесты для Performance Optimization Agent

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import json
import tempfile
import threading

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from security.ai_agents.performance_optimization_agent import (
    PerformanceOptimizationAgent,
    OptimizationType,
    OptimizationLevel,
    OptimizationStatus,
    PerformanceMetric,
    OptimizationRecommendation,
    OptimizationResult,
    OptimizationMetrics,
    OptimizationError,
    ModelLoadError,
    ConfigurationError,
    MetricCollectionError,
    OptimizationImplementationError
)


class TestOptimizationEnums(unittest.TestCase):
    """Тесты для перечислений оптимизации"""
    
    def test_optimization_type_values(self):
        """Тест значений OptimizationType"""
        self.assertEqual(OptimizationType.CPU.value, "cpu")
        self.assertEqual(OptimizationType.MEMORY.value, "memory")
        self.assertEqual(OptimizationType.NETWORK.value, "network")
        self.assertEqual(OptimizationType.DISK.value, "disk")
        self.assertEqual(OptimizationType.CACHE.value, "cache")
        self.assertEqual(OptimizationType.DATABASE.value, "database")
        self.assertEqual(OptimizationType.API.value, "api")
        self.assertEqual(OptimizationType.AI_MODEL.value, "ai_model")
    
    def test_optimization_level_values(self):
        """Тест значений OptimizationLevel"""
        self.assertEqual(OptimizationLevel.LOW.value, "low")
        self.assertEqual(OptimizationLevel.MEDIUM.value, "medium")
        self.assertEqual(OptimizationLevel.HIGH.value, "high")
        self.assertEqual(OptimizationLevel.CRITICAL.value, "critical")
    
    def test_optimization_status_values(self):
        """Тест значений OptimizationStatus"""
        self.assertEqual(OptimizationStatus.PENDING.value, "pending")
        self.assertEqual(OptimizationStatus.ANALYZING.value, "analyzing")
        self.assertEqual(OptimizationStatus.OPTIMIZING.value, "optimizing")
        self.assertEqual(OptimizationStatus.COMPLETED.value, "completed")
        self.assertEqual(OptimizationStatus.FAILED.value, "failed")
        self.assertEqual(OptimizationStatus.ROLLED_BACK.value, "rolled_back")


class TestPerformanceMetric(unittest.TestCase):
    """Тесты для класса PerformanceMetric"""
    
    def setUp(self):
        """Настройка тестов"""
        self.metric = PerformanceMetric(
            metric_id="test_metric",
            metric_type=OptimizationType.CPU,
            value=75.5,
            unit="%",
            is_critical=True
        )
    
    def test_metric_initialization(self):
        """Тест инициализации метрики"""
        self.assertEqual(self.metric.metric_id, "test_metric")
        self.assertEqual(self.metric.metric_type, OptimizationType.CPU)
        self.assertEqual(self.metric.value, 75.5)
        self.assertEqual(self.metric.unit, "%")
        self.assertTrue(self.metric.is_critical)
        self.assertIsNotNone(self.metric.timestamp)
    
    def test_metric_to_dict(self):
        """Тест преобразования в словарь"""
        data = self.metric.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["metric_id"], "test_metric")
        self.assertEqual(data["metric_type"], "cpu")
        self.assertEqual(data["value"], 75.5)
        self.assertEqual(data["unit"], "%")
        self.assertTrue(data["is_critical"])
        self.assertIsNotNone(data["timestamp"])
    
    def test_metric_timestamp_auto_set(self):
        """Тест автоматической установки timestamp"""
        metric = PerformanceMetric(
            metric_id="test",
            metric_type=OptimizationType.CPU,
            value=50.0,
            unit="%"
        )
        self.assertIsNotNone(metric.timestamp)
        self.assertIsInstance(metric.timestamp, datetime)


class TestOptimizationRecommendation(unittest.TestCase):
    """Тесты для класса OptimizationRecommendation"""
    
    def setUp(self):
        """Настройка тестов"""
        self.recommendation = OptimizationRecommendation(
            recommendation_id="rec_001",
            optimization_type=OptimizationType.CPU,
            optimization_level=OptimizationLevel.HIGH,
            description="Оптимизация CPU",
            expected_improvement=25.0,
            confidence=0.85,
            implementation_cost="medium",
            risk_level="low",
            estimated_time=30
        )
    
    def test_recommendation_initialization(self):
        """Тест инициализации рекомендации"""
        self.assertEqual(self.recommendation.recommendation_id, "rec_001")
        self.assertEqual(self.recommendation.optimization_type, OptimizationType.CPU)
        self.assertEqual(self.recommendation.optimization_level, OptimizationLevel.HIGH)
        self.assertEqual(self.recommendation.description, "Оптимизация CPU")
        self.assertEqual(self.recommendation.expected_improvement, 25.0)
        self.assertEqual(self.recommendation.confidence, 0.85)
        self.assertEqual(self.recommendation.implementation_cost, "medium")
        self.assertEqual(self.recommendation.risk_level, "low")
        self.assertEqual(self.recommendation.estimated_time, 30)
        self.assertIsNotNone(self.recommendation.prerequisites)
    
    def test_recommendation_to_dict(self):
        """Тест преобразования в словарь"""
        data = self.recommendation.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["recommendation_id"], "rec_001")
        self.assertEqual(data["optimization_type"], "cpu")
        self.assertEqual(data["optimization_level"], "high")
        self.assertEqual(data["description"], "Оптимизация CPU")
        self.assertEqual(data["expected_improvement"], 25.0)
        self.assertEqual(data["confidence"], 0.85)
        self.assertEqual(data["implementation_cost"], "medium")
        self.assertEqual(data["risk_level"], "low")
        self.assertEqual(data["estimated_time"], 30)
        self.assertIsInstance(data["prerequisites"], list)


class TestOptimizationResult(unittest.TestCase):
    """Тесты для класса OptimizationResult"""
    
    def setUp(self):
        """Настройка тестов"""
        self.result = OptimizationResult(
            recommendation_id="rec_001",
            optimization_type=OptimizationType.CPU,
            status=OptimizationStatus.COMPLETED,
            before_value=80.0,
            after_value=60.0,
            improvement_percentage=25.0,
            implementation_time=45
        )
    
    def test_result_initialization(self):
        """Тест инициализации результата"""
        self.assertEqual(self.result.recommendation_id, "rec_001")
        self.assertEqual(self.result.optimization_type, OptimizationType.CPU)
        self.assertEqual(self.result.status, OptimizationStatus.COMPLETED)
        self.assertEqual(self.result.before_value, 80.0)
        self.assertEqual(self.result.after_value, 60.0)
        self.assertEqual(self.result.improvement_percentage, 25.0)
        self.assertEqual(self.result.implementation_time, 45)
        self.assertIsNotNone(self.result.timestamp)
        self.assertFalse(self.result.rollback_available)
    
    def test_result_to_dict(self):
        """Тест преобразования в словарь"""
        data = self.result.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["recommendation_id"], "rec_001")
        self.assertEqual(data["optimization_type"], "cpu")
        self.assertEqual(data["status"], "completed")
        self.assertEqual(data["before_value"], 80.0)
        self.assertEqual(data["after_value"], 60.0)
        self.assertEqual(data["improvement_percentage"], 25.0)
        self.assertEqual(data["implementation_time"], 45)
        self.assertIsNotNone(data["timestamp"])


class TestOptimizationMetrics(unittest.TestCase):
    """Тесты для класса OptimizationMetrics"""
    
    def setUp(self):
        """Настройка тестов"""
        self.metrics = OptimizationMetrics()
    
    def test_metrics_initialization(self):
        """Тест инициализации метрик"""
        self.assertEqual(self.metrics.total_optimizations, 0)
        self.assertEqual(self.metrics.successful_optimizations, 0)
        self.assertEqual(self.metrics.failed_optimizations, 0)
        self.assertEqual(self.metrics.average_improvement, 0.0)
        self.assertIsNotNone(self.metrics.optimizations_by_type)
        self.assertIsNotNone(self.metrics.optimizations_by_level)
        self.assertIsNotNone(self.metrics.last_optimization)
    
    def test_metrics_to_dict(self):
        """Тест преобразования в словарь"""
        data = self.metrics.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["total_optimizations"], 0)
        self.assertEqual(data["successful_optimizations"], 0)
        self.assertEqual(data["failed_optimizations"], 0)
        self.assertEqual(data["average_improvement"], 0.0)
        self.assertIsNotNone(data["last_optimization"])
    
    def test_update_metrics(self):
        """Тест обновления метрик"""
        result = OptimizationResult(
            recommendation_id="test",
            optimization_type=OptimizationType.CPU,
            status=OptimizationStatus.COMPLETED,
            before_value=80.0,
            after_value=60.0,
            improvement_percentage=25.0,
            implementation_time=30
        )
        
        self.metrics.update_metrics(result)
        
        self.assertEqual(self.metrics.total_optimizations, 1)
        self.assertEqual(self.metrics.successful_optimizations, 1)
        self.assertEqual(self.metrics.failed_optimizations, 0)
        self.assertEqual(self.metrics.average_improvement, 25.0)
        self.assertEqual(self.metrics.optimizations_by_type["cpu"], 1)


class TestPerformanceOptimizationAgent(unittest.TestCase):
    """Тесты для класса PerformanceOptimizationAgent"""
    
    def setUp(self):
        """Настройка тестов"""
        with patch('core.base.SecurityBase.__init__'):
            self.agent = PerformanceOptimizationAgent("TestAgent")
    
    def test_agent_initialization(self):
        """Тест инициализации агента"""
        self.assertEqual(self.agent.optimization_threshold, 0.7)
        self.assertEqual(self.agent.analysis_interval, 60)
        self.assertEqual(self.agent.max_concurrent_optimizations, 3)
        self.assertTrue(self.agent.auto_optimization_enabled)
        self.assertIsInstance(self.agent.optimization_lock, type(threading.Lock()))
    
    @patch('security.ai_agents.performance_optimization_agent.PerformanceOptimizationAgent._initialize_optimization_algorithms')
    @patch('security.ai_agents.performance_optimization_agent.PerformanceOptimizationAgent._load_performance_models')
    @patch('security.ai_agents.performance_optimization_agent.PerformanceOptimizationAgent._initialize_prediction_models')
    @patch('security.ai_agents.performance_optimization_agent.PerformanceOptimizationAgent._start_background_tasks')
    def test_initialize_success(self, mock_start_tasks, mock_init_pred, mock_load_models, mock_init_algo):
        """Тест успешной инициализации"""
        result = self.agent.initialize()
        self.assertTrue(result)
        self.assertEqual(self.agent.status.value, "running")
        mock_init_algo.assert_called_once()
        mock_load_models.assert_called_once()
        mock_init_pred.assert_called_once()
        mock_start_tasks.assert_called_once()
    
    @patch('security.ai_agents.performance_optimization_agent.PerformanceOptimizationAgent._initialize_optimization_algorithms')
    def test_initialize_failure(self, mock_init_algo):
        """Тест неудачной инициализации"""
        mock_init_algo.side_effect = ModelLoadError("Test error")
        result = self.agent.initialize()
        self.assertFalse(result)
        self.assertEqual(self.agent.status.value, "error")
    
    @patch('security.ai_agents.performance_optimization_agent.PerformanceOptimizationAgent._stop_background_tasks')
    @patch('security.ai_agents.performance_optimization_agent.PerformanceOptimizationAgent._save_optimization_data')
    def test_stop_success(self, mock_save_data, mock_stop_tasks):
        """Тест успешной остановки"""
        result = self.agent.stop()
        self.assertTrue(result)
        self.assertEqual(self.agent.status.value, "stopped")
        mock_stop_tasks.assert_called_once()
        mock_save_data.assert_called_once()
    
    @patch('security.ai_agents.performance_optimization_agent.PerformanceOptimizationAgent._stop_background_tasks')
    def test_stop_failure(self, mock_stop_tasks):
        """Тест неудачной остановки"""
        mock_stop_tasks.side_effect = Exception("Test error")
        result = self.agent.stop()
        self.assertFalse(result)
    
    @patch('security.ai_agents.performance_optimization_agent.PerformanceOptimizationAgent._collect_performance_metrics')
    @patch('security.ai_agents.performance_optimization_agent.PerformanceOptimizationAgent._analyze_with_ai')
    @patch('security.ai_agents.performance_optimization_agent.PerformanceOptimizationAgent._analyze_trends')
    @patch('security.ai_agents.performance_optimization_agent.PerformanceOptimizationAgent._combine_recommendations')
    def test_analyze_performance(self, mock_combine, mock_trends, mock_ai, mock_collect):
        """Тест анализа производительности"""
        # Настройка моков
        mock_collect.return_value = [Mock()]
        mock_ai.return_value = [Mock()]
        mock_trends.return_value = [Mock()]
        mock_combine.return_value = [Mock()]
        
        recommendations = self.agent.analyze_performance()
        
        self.assertIsInstance(recommendations, list)
        self.assertEqual(self.agent.statistics["total_analyses"], 1)
        mock_collect.assert_called_once()
        mock_ai.assert_called_once()
        mock_trends.assert_called_once()
        mock_combine.assert_called_once()


class TestCustomExceptions(unittest.TestCase):
    """Тесты для кастомных исключений"""
    
    def test_optimization_error_inheritance(self):
        """Тест наследования OptimizationError"""
        self.assertTrue(issubclass(OptimizationError, Exception))
        self.assertTrue(issubclass(ModelLoadError, OptimizationError))
        self.assertTrue(issubclass(ConfigurationError, OptimizationError))
        self.assertTrue(issubclass(MetricCollectionError, OptimizationError))
        self.assertTrue(issubclass(OptimizationImplementationError, OptimizationError))
    
    def test_exception_creation(self):
        """Тест создания исключений"""
        opt_error = OptimizationError("Test error")
        model_error = ModelLoadError("Model load failed")
        config_error = ConfigurationError("Config invalid")
        
        self.assertEqual(str(opt_error), "Test error")
        self.assertEqual(str(model_error), "Model load failed")
        self.assertEqual(str(config_error), "Config invalid")


class TestEdgeCases(unittest.TestCase):
    """Тесты для граничных случаев"""
    
    def test_empty_recommendations_list(self):
        """Тест пустого списка рекомендаций"""
        with patch('core.base.SecurityBase.__init__'):
            agent = PerformanceOptimizationAgent()
        
        with patch.object(agent, '_collect_performance_metrics', return_value=[]):
            with patch.object(agent, '_analyze_with_ai', return_value=[]):
                with patch.object(agent, '_analyze_trends', return_value=[]):
                    with patch.object(agent, '_combine_recommendations', return_value=[]):
                        recommendations = agent.analyze_performance()
                        self.assertEqual(len(recommendations), 0)
    
    def test_invalid_metric_values(self):
        """Тест невалидных значений метрик"""
        with self.assertRaises((ValueError, TypeError)):
            PerformanceMetric(
                metric_id="test",
                metric_type=OptimizationType.CPU,
                value="invalid",  # Должно быть число
                unit="%"
            )
    
    def test_concurrent_optimizations(self):
        """Тест одновременных оптимизаций"""
        with patch('core.base.SecurityBase.__init__'):
            agent = PerformanceOptimizationAgent()
        
        # Симуляция одновременных вызовов
        import threading
        results = []
        
        def analyze():
            with patch.object(agent, '_collect_performance_metrics', return_value=[]):
                with patch.object(agent, '_analyze_with_ai', return_value=[]):
                    with patch.object(agent, '_analyze_trends', return_value=[]):
                        with patch.object(agent, '_combine_recommendations', return_value=[]):
                            results.append(agent.analyze_performance())
        
        threads = [threading.Thread(target=analyze) for _ in range(5)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        self.assertEqual(len(results), 5)
        self.assertEqual(agent.statistics["total_analyses"], 5)


if __name__ == '__main__':
    # Создаем тестовый набор
    test_suite = unittest.TestSuite()
    
    # Добавляем тесты
    test_classes = [
        TestOptimizationEnums,
        TestPerformanceMetric,
        TestOptimizationRecommendation,
        TestOptimizationResult,
        TestOptimizationMetrics,
        TestPerformanceOptimizationAgent,
        TestCustomExceptions,
        TestEdgeCases
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Выводим результаты
    print(f"\n{'='*60}")
    print(f"РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print(f"Всего тестов: {result.testsRun}")
    print(f"Успешных: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Неудачных: {len(result.failures)}")
    print(f"Ошибок: {len(result.errors)}")
    print(f"Покрытие: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100:.1f}%")
    print(f"{'='*60}")