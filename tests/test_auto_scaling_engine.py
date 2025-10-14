# -*- coding: utf-8 -*-
"""
Тесты для AutoScalingEngine
"""

import unittest
import time
import threading
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from security.scaling.auto_scaling_engine import (
    AutoScalingEngine, ScalingTrigger, ScalingAction, ScalingStrategy,
    MetricData, ScalingRule, ScalingDecision, ScalingMetrics
)


class TestAutoScalingEngine(unittest.TestCase):
    """Тесты для AutoScalingEngine"""

    def setUp(self):
        """Настройка тестов"""
        self.engine = AutoScalingEngine("TestAutoScalingEngine")

    def tearDown(self):
        """Очистка после тестов"""
        if hasattr(self, 'engine'):
            self.engine.stop()

    def test_initialization(self):
        """Тест инициализации"""
        result = self.engine.initialize()
        self.assertTrue(result)
        self.assertEqual(self.engine.status.value, "running")

    def test_stop(self):
        """Тест остановки"""
        self.engine.initialize()
        result = self.engine.stop()
        self.assertTrue(result)
        self.assertEqual(self.engine.status.value, "stopped")

    def test_add_scaling_rule(self):
        """Тест добавления правила масштабирования"""
        self.engine.initialize()

        rule = ScalingRule(
            rule_id="test-rule",
            name="Test Rule",
            service_id="test-service",
            metric_name="cpu_usage",
            trigger=ScalingTrigger.CPU_HIGH,
            threshold=0.8,
            action=ScalingAction.SCALE_UP,
            min_replicas=1,
            max_replicas=5,
            cooldown_period=300
        )

        result = self.engine.add_scaling_rule(rule)
        self.assertTrue(result)

        # Проверяем что правило добавлено
        rules = self.engine.get_scaling_rules()
        self.assertGreater(len(rules), 0)

    def test_remove_scaling_rule(self):
        """Тест удаления правила масштабирования"""
        self.engine.initialize()

        rule = ScalingRule(
            rule_id="test-rule",
            name="Test Rule",
            service_id="test-service",
            metric_name="cpu_usage",
            trigger=ScalingTrigger.CPU_HIGH,
            threshold=0.8,
            action=ScalingAction.SCALE_UP,
            min_replicas=1,
            max_replicas=5,
            cooldown_period=300
        )

        # Добавляем правило
        self.engine.add_scaling_rule(rule)

        # Удаляем правило
        result = self.engine.remove_scaling_rule("test-rule")
        self.assertTrue(result)

        # Проверяем что правило удалено
        rules = self.engine.get_scaling_rules("test-service")
        self.assertEqual(len(rules), 0)

    def test_remove_nonexistent_rule(self):
        """Тест удаления несуществующего правила"""
        self.engine.initialize()

        result = self.engine.remove_scaling_rule("nonexistent-rule")
        self.assertFalse(result)

    def test_collect_metric(self):
        """Тест сбора метрики"""
        self.engine.initialize()

        metric = MetricData(
            metric_name="cpu_usage",
            value=0.75,
            timestamp=datetime.now(),
            service_id="test-service"
        )

        result = self.engine.collect_metric(metric)
        self.assertTrue(result)

    def test_make_scaling_decision(self):
        """Тест принятия решения о масштабировании"""
        self.engine.initialize()

        # Добавляем правило
        rule = ScalingRule(
            rule_id="test-rule",
            name="Test Rule",
            service_id="test-service",
            metric_name="cpu_usage",
            trigger=ScalingTrigger.CPU_HIGH,
            threshold=0.8,
            action=ScalingAction.SCALE_UP,
            min_replicas=1,
            max_replicas=5,
            cooldown_period=300
        )
        self.engine.add_scaling_rule(rule)

        # Добавляем метрику, которая должна сработать
        metric = MetricData(
            metric_name="cpu_usage",
            value=0.9,  # Выше порога 0.8
            timestamp=datetime.now(),
            service_id="test-service"
        )
        self.engine.collect_metric(metric)

        # Принимаем решение
        decision = self.engine.make_scaling_decision("test-service")
        self.assertIsNotNone(decision)
        self.assertEqual(decision.service_id, "test-service")
        self.assertEqual(decision.action, ScalingAction.SCALE_UP)

    def test_make_scaling_decision_no_trigger(self):
        """Тест принятия решения без срабатывания правил"""
        self.engine.initialize()

        # Добавляем правило
        rule = ScalingRule(
            rule_id="test-rule",
            name="Test Rule",
            service_id="test-service",
            metric_name="cpu_usage",
            trigger=ScalingTrigger.CPU_HIGH,
            threshold=0.8,
            action=ScalingAction.SCALE_UP,
            min_replicas=1,
            max_replicas=5,
            cooldown_period=300
        )
        self.engine.add_scaling_rule(rule)

        # Добавляем метрику, которая НЕ должна сработать
        metric = MetricData(
            metric_name="cpu_usage",
            value=0.5,  # Ниже порога 0.8
            timestamp=datetime.now(),
            service_id="test-service"
        )
        self.engine.collect_metric(metric)

        # Принимаем решение
        decision = self.engine.make_scaling_decision("test-service")
        self.assertIsNone(decision)

    def test_get_scaling_rules(self):
        """Тест получения правил масштабирования"""
        self.engine.initialize()

        # Добавляем несколько правил
        rule1 = ScalingRule(
            rule_id="rule-1",
            name="Rule 1",
            service_id="service-1",
            metric_name="cpu_usage",
            trigger=ScalingTrigger.CPU_HIGH,
            threshold=0.8,
            action=ScalingAction.SCALE_UP,
            min_replicas=1,
            max_replicas=5,
            cooldown_period=300
        )

        rule2 = ScalingRule(
            rule_id="rule-2",
            name="Rule 2",
            service_id="service-2",
            metric_name="memory_usage",
            trigger=ScalingTrigger.MEMORY_HIGH,
            threshold=0.85,
            action=ScalingAction.SCALE_UP,
            min_replicas=1,
            max_replicas=5,
            cooldown_period=300
        )

        self.engine.add_scaling_rule(rule1)
        self.engine.add_scaling_rule(rule2)

        # Получаем все правила (включая дефолтные)
        all_rules = self.engine.get_scaling_rules()
        self.assertGreaterEqual(len(all_rules), 2)  # Минимум 2 добавленных правила

        # Получаем правила для конкретного сервиса
        service1_rules = self.engine.get_scaling_rules("service-1")
        self.assertEqual(len(service1_rules), 1)
        self.assertEqual(service1_rules[0].service_id, "service-1")

    def test_get_scaling_decisions(self):
        """Тест получения решений о масштабировании"""
        self.engine.initialize()

        # Создаем тестовое решение
        decision = ScalingDecision(
            decision_id="test-decision",
            service_id="test-service",
            action=ScalingAction.SCALE_UP,
            current_replicas=2,
            target_replicas=3,
            reason="Test decision",
            confidence=0.8,
            triggered_rules=["rule-1"],
            timestamp=datetime.now(),
            metrics_used=[]
        )

        # Добавляем решение вручную (в реальной системе это делается автоматически)
        with self.engine.scaling_lock:
            self.engine.scaling_decisions.append(decision)

        # Получаем решения
        decisions = self.engine.get_scaling_decisions()
        self.assertEqual(len(decisions), 1)
        self.assertEqual(decisions[0].decision_id, "test-decision")

    def test_get_scaling_metrics(self):
        """Тест получения метрик масштабирования"""
        self.engine.initialize()

        metrics = self.engine.get_scaling_metrics()
        self.assertIsInstance(metrics, ScalingMetrics)
        self.assertGreaterEqual(metrics.total_scaling_operations, 0)

    def test_get_engine_status(self):
        """Тест получения статуса движка"""
        self.engine.initialize()

        status = self.engine.get_engine_status()
        self.assertIsInstance(status, dict)
        self.assertIn("status", status)
        self.assertIn("active_rules", status)
        self.assertIn("total_metrics", status)
        self.assertIn("total_decisions", status)
        self.assertIn("metrics", status)
        self.assertIn("statistics", status)
        self.assertIn("ai_enabled", status)

    def test_metric_data_creation(self):
        """Тест создания данных метрики"""
        metric = MetricData(
            metric_name="cpu_usage",
            value=0.75,
            timestamp=datetime.now(),
            service_id="test-service",
            node_id="node-1",
            tags={"environment": "test"}
        )

        self.assertEqual(metric.metric_name, "cpu_usage")
        self.assertEqual(metric.value, 0.75)
        self.assertEqual(metric.service_id, "test-service")
        self.assertEqual(metric.node_id, "node-1")
        self.assertEqual(metric.tags["environment"], "test")

    def test_metric_data_to_dict(self):
        """Тест преобразования данных метрики в словарь"""
        metric = MetricData(
            metric_name="cpu_usage",
            value=0.75,
            timestamp=datetime.now(),
            service_id="test-service"
        )

        data = metric.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["metric_name"], "cpu_usage")
        self.assertEqual(data["value"], 0.75)
        self.assertIn("timestamp", data)

    def test_scaling_rule_creation(self):
        """Тест создания правила масштабирования"""
        rule = ScalingRule(
            rule_id="test-rule",
            name="Test Rule",
            service_id="test-service",
            metric_name="cpu_usage",
            trigger=ScalingTrigger.CPU_HIGH,
            threshold=0.8,
            action=ScalingAction.SCALE_UP,
            min_replicas=1,
            max_replicas=5,
            cooldown_period=300
        )

        self.assertEqual(rule.rule_id, "test-rule")
        self.assertEqual(rule.name, "Test Rule")
        self.assertEqual(rule.service_id, "test-service")
        self.assertEqual(rule.metric_name, "cpu_usage")
        self.assertEqual(rule.trigger, ScalingTrigger.CPU_HIGH)
        self.assertEqual(rule.threshold, 0.8)
        self.assertEqual(rule.action, ScalingAction.SCALE_UP)
        self.assertEqual(rule.min_replicas, 1)
        self.assertEqual(rule.max_replicas, 5)
        self.assertEqual(rule.cooldown_period, 300)
        self.assertTrue(rule.enabled)

    def test_scaling_rule_to_dict(self):
        """Тест преобразования правила масштабирования в словарь"""
        rule = ScalingRule(
            rule_id="test-rule",
            name="Test Rule",
            service_id="test-service",
            metric_name="cpu_usage",
            trigger=ScalingTrigger.CPU_HIGH,
            threshold=0.8,
            action=ScalingAction.SCALE_UP,
            min_replicas=1,
            max_replicas=5,
            cooldown_period=300
        )

        data = rule.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["rule_id"], "test-rule")
        self.assertEqual(data["trigger"], "cpu_high")
        self.assertEqual(data["action"], "scale_up")
        self.assertIn("created_at", data)

    def test_scaling_decision_creation(self):
        """Тест создания решения о масштабировании"""
        decision = ScalingDecision(
            decision_id="test-decision",
            service_id="test-service",
            action=ScalingAction.SCALE_UP,
            current_replicas=2,
            target_replicas=3,
            reason="High CPU usage",
            confidence=0.8,
            triggered_rules=["rule-1", "rule-2"],
            timestamp=datetime.now(),
            metrics_used=[]
        )

        self.assertEqual(decision.decision_id, "test-decision")
        self.assertEqual(decision.service_id, "test-service")
        self.assertEqual(decision.action, ScalingAction.SCALE_UP)
        self.assertEqual(decision.current_replicas, 2)
        self.assertEqual(decision.target_replicas, 3)
        self.assertEqual(decision.reason, "High CPU usage")
        self.assertEqual(decision.confidence, 0.8)
        self.assertEqual(len(decision.triggered_rules), 2)

    def test_scaling_decision_to_dict(self):
        """Тест преобразования решения о масштабировании в словарь"""
        decision = ScalingDecision(
            decision_id="test-decision",
            service_id="test-service",
            action=ScalingAction.SCALE_UP,
            current_replicas=2,
            target_replicas=3,
            reason="High CPU usage",
            confidence=0.8,
            triggered_rules=["rule-1"],
            timestamp=datetime.now(),
            metrics_used=[]
        )

        data = decision.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["decision_id"], "test-decision")
        self.assertEqual(data["action"], "scale_up")
        self.assertIn("timestamp", data)
        self.assertIn("metrics_used", data)

    def test_scaling_metrics_creation(self):
        """Тест создания метрик масштабирования"""
        metrics = ScalingMetrics()
        
        self.assertEqual(metrics.total_scaling_operations, 0)
        self.assertEqual(metrics.successful_scaling_operations, 0)
        self.assertEqual(metrics.failed_scaling_operations, 0)
        self.assertEqual(metrics.scale_up_operations, 0)
        self.assertEqual(metrics.scale_down_operations, 0)
        self.assertEqual(metrics.emergency_operations, 0)

    def test_scaling_metrics_to_dict(self):
        """Тест преобразования метрик в словарь"""
        metrics = ScalingMetrics()
        data = metrics.to_dict()

        self.assertIsInstance(data, dict)
        self.assertIn("total_scaling_operations", data)
        self.assertIn("successful_scaling_operations", data)
        self.assertIn("failed_scaling_operations", data)
        self.assertIn("last_scaling_time", data)

    def test_concurrent_metric_collection(self):
        """Тест параллельного сбора метрик"""
        self.engine.initialize()

        def collect_worker(worker_id):
            metric = MetricData(
                metric_name="cpu_usage",
                value=0.5 + worker_id * 0.1,
                timestamp=datetime.now(),
                service_id=f"service-{worker_id}"
            )
            result = self.engine.collect_metric(metric)
            return result

        # Запуск нескольких потоков
        threads = []
        results = []
        
        for i in range(5):
            thread = threading.Thread(target=lambda i=i: results.append(collect_worker(i)))
            threads.append(thread)
            thread.start()

        # Ожидание завершения всех потоков
        for thread in threads:
            thread.join()

        # Проверка результатов
        self.assertEqual(len(results), 5)
        self.assertTrue(all(results))  # Все должны быть успешными

    def test_rule_cooldown(self):
        """Тест периода охлаждения правила"""
        self.engine.initialize()

        # Создаем правило с коротким периодом охлаждения
        rule = ScalingRule(
            rule_id="test-rule",
            name="Test Rule",
            service_id="test-service",
            metric_name="cpu_usage",
            trigger=ScalingTrigger.CPU_HIGH,
            threshold=0.8,
            action=ScalingAction.SCALE_UP,
            min_replicas=1,
            max_replicas=5,
            cooldown_period=1  # 1 секунда
        )
        self.engine.add_scaling_rule(rule)

        # Добавляем метрику, которая должна сработать
        metric = MetricData(
            metric_name="cpu_usage",
            value=0.9,
            timestamp=datetime.now(),
            service_id="test-service"
        )
        self.engine.collect_metric(metric)

        # Первое решение должно сработать
        decision1 = self.engine.make_scaling_decision("test-service")
        self.assertIsNotNone(decision1)

        # Второе решение сразу не должно сработать из-за периода охлаждения
        decision2 = self.engine.make_scaling_decision("test-service")
        self.assertIsNone(decision2)

        # Ждем окончания периода охлаждения
        time.sleep(1.1)

        # Третье решение должно снова сработать
        decision3 = self.engine.make_scaling_decision("test-service")
        self.assertIsNotNone(decision3)

    def test_error_handling(self):
        """Тест обработки ошибок"""
        # Тест с неинициализированным движком
        result = self.engine.add_scaling_rule(None)
        self.assertFalse(result)

        result = self.engine.collect_metric(None)
        self.assertFalse(result)

        decision = self.engine.make_scaling_decision("nonexistent-service")
        self.assertIsNone(decision)

    def test_statistics_tracking(self):
        """Тест отслеживания статистики"""
        self.engine.initialize()

        initial_metrics = self.engine.statistics["total_metrics_collected"]
        initial_decisions = self.engine.statistics["total_decisions_made"]

        # Собираем метрику
        metric = MetricData(
            metric_name="cpu_usage",
            value=0.75,
            timestamp=datetime.now(),
            service_id="test-service"
        )
        self.engine.collect_metric(metric)

        # Проверяем статистику
        self.assertGreater(self.engine.statistics["total_metrics_collected"], initial_metrics)

        # Добавляем правило и принимаем решение
        rule = ScalingRule(
            rule_id="test-rule",
            name="Test Rule",
            service_id="test-service",
            metric_name="cpu_usage",
            trigger=ScalingTrigger.CPU_HIGH,
            threshold=0.7,  # Ниже значения метрики
            action=ScalingAction.SCALE_UP,
            min_replicas=1,
            max_replicas=5,
            cooldown_period=300
        )
        self.engine.add_scaling_rule(rule)

        decision = self.engine.make_scaling_decision("test-service")
        if decision:
            self.assertGreater(self.engine.statistics["total_decisions_made"], initial_decisions)


if __name__ == '__main__':
    unittest.main()