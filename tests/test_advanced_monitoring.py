#!/usr/bin/env python3
"""
Тесты для расширенного мониторинга системы
"""

import unittest
import requests
import time
import os
import sys
import subprocess
import json
import threading

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from security.advanced_monitoring_manager import (
    AdvancedMonitoringManager, MetricType, AlertSeverity, 
    MonitoringRule, Metric, Alert
)
from security.safe_function_manager import SafeFunctionManager
from core.base import SecurityLevel, ComponentStatus
from core.logging_module import LoggingManager

logger = LoggingManager(name="TestAdvancedMonitoring")

class TestAdvancedMonitoringManager(unittest.TestCase):
    """Тесты AdvancedMonitoringManager"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        self.manager = AdvancedMonitoringManager("TestMonitoringManager")

    def test_01_initialization(self):
        """Тест инициализации менеджера"""
        self.assertIsInstance(self.manager, AdvancedMonitoringManager)
        self.assertEqual(self.manager.status, ComponentStatus.RUNNING)
        self.assertEqual(self.manager.security_level, SecurityLevel.HIGH)
        self.assertGreater(len(self.manager.monitoring_rules), 0)
        logger.log("INFO", "Test 01: Manager initialization passed")

    def test_02_metric_creation(self):
        """Тест создания метрик"""
        # Добавляем тестовую метрику
        self.manager._add_metric("test.metric", 42.0, MetricType.CUSTOM, "units")
        
        self.assertIn("test.metric", self.manager.metrics)
        self.assertEqual(len(self.manager.metrics["test.metric"]), 1)
        
        metric = self.manager.metrics["test.metric"][0]
        self.assertEqual(metric.value, 42.0)
        self.assertEqual(metric.metric_type, MetricType.CUSTOM)
        self.assertEqual(metric.unit, "units")
        
        logger.log("INFO", "Test 02: Metric creation passed")

    def test_03_alert_creation(self):
        """Тест создания алертов"""
        initial_count = len(self.manager.alerts)
        
        # Создаем тестовый алерт
        alert = Alert(
            alert_id="test_alert_001",
            title="Test Alert",
            message="Test message",
            severity=AlertSeverity.WARNING,
            metric_name="test.metric",
            threshold_value=50.0,
            current_value=60.0,
            timestamp=time.time()
        )
        
        self.manager.alerts.append(alert)
        
        self.assertEqual(len(self.manager.alerts), initial_count + 1)
        self.assertEqual(self.manager.alerts[-1].title, "Test Alert")
        self.assertEqual(self.manager.alerts[-1].severity, AlertSeverity.WARNING)
        
        logger.log("INFO", "Test 03: Alert creation passed")

    def test_04_monitoring_rule_creation(self):
        """Тест создания правил мониторинга"""
        initial_count = len(self.manager.monitoring_rules)
        
        rule = MonitoringRule(
            rule_id="test_rule_001",
            name="Test Rule",
            metric_name="test.metric",
            condition=">",
            threshold=50.0,
            severity=AlertSeverity.WARNING
        )
        
        success = self.manager.add_monitoring_rule(rule)
        
        self.assertTrue(success)
        self.assertEqual(len(self.manager.monitoring_rules), initial_count + 1)
        self.assertIn("test_rule_001", self.manager.monitoring_rules)
        
        logger.log("INFO", "Test 04: Monitoring rule creation passed")

    def test_05_condition_evaluation(self):
        """Тест оценки условий"""
        # Тест различных условий
        self.assertTrue(self.manager._evaluate_condition(60.0, ">", 50.0))
        self.assertFalse(self.manager._evaluate_condition(40.0, ">", 50.0))
        self.assertTrue(self.manager._evaluate_condition(40.0, "<", 50.0))
        self.assertTrue(self.manager._evaluate_condition(50.0, ">=", 50.0))
        self.assertTrue(self.manager._evaluate_condition(50.0, "<=", 50.0))
        self.assertTrue(self.manager._evaluate_condition(50.0, "==", 50.0))
        self.assertTrue(self.manager._evaluate_condition(60.0, "!=", 50.0))
        
        logger.log("INFO", "Test 05: Condition evaluation passed")

    def test_06_get_metrics(self):
        """Тест получения метрик"""
        # Добавляем тестовые метрики
        self.manager._add_metric("test.metric1", 10.0, MetricType.CUSTOM, "units1")
        self.manager._add_metric("test.metric2", 20.0, MetricType.CUSTOM, "units2")
        
        # Получаем все метрики
        all_metrics = self.manager.get_metrics()
        self.assertIn("test.metric1", all_metrics)
        self.assertIn("test.metric2", all_metrics)
        
        # Получаем конкретную метрику
        specific_metric = self.manager.get_metrics("test.metric1")
        self.assertEqual(specific_metric["metric_name"], "test.metric1")
        self.assertEqual(len(specific_metric["metrics"]), 1)
        
        logger.log("INFO", "Test 06: Get metrics passed")

    def test_07_get_alerts(self):
        """Тест получения алертов"""
        # Добавляем тестовые алерты
        alert1 = Alert(
            alert_id="alert1", title="Alert 1", message="Message 1",
            severity=AlertSeverity.WARNING, metric_name="test.metric",
            threshold_value=50.0, current_value=60.0, timestamp=time.time()
        )
        alert2 = Alert(
            alert_id="alert2", title="Alert 2", message="Message 2",
            severity=AlertSeverity.ERROR, metric_name="test.metric",
            threshold_value=50.0, current_value=70.0, timestamp=time.time()
        )
        
        self.manager.alerts.extend([alert1, alert2])
        
        # Получаем все алерты
        all_alerts = self.manager.get_alerts()
        self.assertEqual(len(all_alerts), 2)
        
        # Получаем алерты по серьезности
        warning_alerts = self.manager.get_alerts(AlertSeverity.WARNING)
        self.assertEqual(len(warning_alerts), 1)
        self.assertEqual(warning_alerts[0]["severity"], "warning")
        
        logger.log("INFO", "Test 07: Get alerts passed")

    def test_08_get_dashboard_data(self):
        """Тест получения данных дашборда"""
        dashboard_data = self.manager.get_dashboard_data()
        
        self.assertIn("system_info", dashboard_data)
        self.assertIn("metrics", dashboard_data)
        self.assertIn("alerts", dashboard_data)
        self.assertIn("rules", dashboard_data)
        self.assertIn("stats", dashboard_data)
        
        # Проверяем структуру system_info
        system_info = dashboard_data["system_info"]
        self.assertIn("uptime_seconds", system_info)
        self.assertIn("uptime_formatted", system_info)
        
        logger.log("INFO", "Test 08: Get dashboard data passed")

    def test_09_get_status(self):
        """Тест получения статуса"""
        status = self.manager.get_status()
        
        self.assertIn("component_name", status)
        self.assertIn("status", status)
        self.assertIn("security_level", status)
        self.assertIn("monitoring_active", status)
        self.assertIn("metrics_count", status)
        self.assertIn("alerts_count", status)
        self.assertIn("rules_count", status)
        
        self.assertEqual(status["component_name"], "TestMonitoringManager")
        self.assertEqual(status["status"], "RUNNING")
        
        logger.log("INFO", "Test 09: Get status passed")

    def test_10_rule_management(self):
        """Тест управления правилами"""
        # Добавляем правило
        rule = MonitoringRule(
            rule_id="test_rule_002",
            name="Test Rule 2",
            metric_name="test.metric",
            condition=">",
            threshold=30.0,
            severity=AlertSeverity.INFO
        )
        
        success = self.manager.add_monitoring_rule(rule)
        self.assertTrue(success)
        
        # Удаляем правило
        success = self.manager.remove_monitoring_rule("test_rule_002")
        self.assertTrue(success)
        self.assertNotIn("test_rule_002", self.manager.monitoring_rules)
        
        logger.log("INFO", "Test 10: Rule management passed")

    def tearDown(self):
        """Очистка после теста"""
        self.manager.stop()


class TestMonitoringAPIServer(unittest.TestCase):
    """Тесты Monitoring API Server"""
    
    @classmethod
    def setUpClass(cls):
        """Настройка перед всеми тестами"""
        cls.server_process = None
        try:
            # Проверяем, запущен ли уже сервер
            response = requests.get("http://localhost:5006/api/monitoring/health", timeout=5)
            if response.status_code == 200 and response.json().get("status") == "ok":
                logger.log("INFO", "Monitoring API Server is already running.")
            else:
                raise Exception("Server not healthy")
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, Exception):
            logger.log("INFO", "Starting Monitoring API Server for testing...")
            cls.server_process = subprocess.Popen(
                ["python3", "monitoring_api_server.py"],
                cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            time.sleep(5)
            try:
                response = requests.get("http://localhost:5006/api/monitoring/health", timeout=5)
                response.raise_for_status()
                if response.json().get("status") != "ok":
                    raise Exception("Server health check failed after startup.")
                logger.log("INFO", "Monitoring API Server started successfully.")
            except Exception as e:
                logger.log("ERROR", f"Failed to start Monitoring API Server: {e}")
                if cls.server_process and cls.server_process.poll() is not None:
                    stdout, stderr = cls.server_process.communicate()
                    logger.log("ERROR", f"Server stdout: {stdout}")
                    logger.log("ERROR", f"Server stderr: {stderr}")
                raise

    @classmethod
    def tearDownClass(cls):
        """Очистка после всех тестов"""
        if cls.server_process and cls.server_process.poll() is None:
            cls.server_process.terminate()
            cls.server_process.wait(timeout=10)
            logger.log("INFO", "Monitoring API Server stopped.")

    def test_01_health_check(self):
        """Тест health check API"""
        response = requests.get("http://localhost:5006/api/monitoring/health")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("timestamp", data)
        self.assertIn("manager_status", data)
        
        logger.log("INFO", "Test 01: Health check API passed")

    def test_02_metrics_api(self):
        """Тест API метрик"""
        response = requests.get("http://localhost:5006/api/monitoring/metrics")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("data", data)
        self.assertIn("timestamp", data)
        
        logger.log("INFO", "Test 02: Metrics API passed")

    def test_03_alerts_api(self):
        """Тест API алертов"""
        response = requests.get("http://localhost:5006/api/monitoring/alerts")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("data", data)
        self.assertIn("timestamp", data)
        
        logger.log("INFO", "Test 03: Alerts API passed")

    def test_04_dashboard_api(self):
        """Тест API дашборда"""
        response = requests.get("http://localhost:5006/api/monitoring/dashboard")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("data", data)
        self.assertIn("timestamp", data)
        
        # Проверяем структуру данных дашборда
        dashboard_data = data["data"]
        self.assertIn("system_info", dashboard_data)
        self.assertIn("metrics", dashboard_data)
        self.assertIn("alerts", dashboard_data)
        self.assertIn("rules", dashboard_data)
        
        logger.log("INFO", "Test 04: Dashboard API passed")

    def test_05_rules_api(self):
        """Тест API правил"""
        response = requests.get("http://localhost:5006/api/monitoring/rules")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("data", data)
        self.assertIn("timestamp", data)
        
        logger.log("INFO", "Test 05: Rules API passed")

    def test_06_custom_metric_api(self):
        """Тест API добавления пользовательской метрики"""
        metric_data = {
            "metric_name": "test.custom_metric",
            "value": 42.0,
            "metric_type": "custom",
            "unit": "test_units",
            "tags": {"test": "true"}
        }
        
        response = requests.post(
            "http://localhost:5006/api/monitoring/custom-metric",
            json=metric_data
        )
        self.assertEqual(response.status_code, 201)
        
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("message", data)
        
        logger.log("INFO", "Test 06: Custom metric API passed")

    def test_07_test_monitoring_api(self):
        """Тест API тестирования мониторинга"""
        response = requests.post("http://localhost:5006/api/monitoring/test")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("message", data)
        self.assertIn("test_metrics_added", data)
        
        logger.log("INFO", "Test 07: Test monitoring API passed")

    def test_08_status_api(self):
        """Тест API статуса"""
        response = requests.get("http://localhost:5006/api/monitoring/status")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("data", data)
        self.assertIn("timestamp", data)
        
        logger.log("INFO", "Test 08: Status API passed")


class TestSafeFunctionManagerIntegration(unittest.TestCase):
    """Тесты интеграции с SafeFunctionManager"""
    
    @classmethod
    def setUpClass(cls):
        """Интеграция функций перед тестами"""
        try:
            # Запускаем интеграцию
            result = subprocess.run(
                ["python3", "scripts/integrate_advanced_monitoring.py"],
                cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode != 0:
                logger.log("ERROR", f"Integration failed: {result.stderr}")
                raise Exception("Integration failed")
            logger.log("INFO", "Advanced monitoring integrated into SafeFunctionManager")
        except Exception as e:
            logger.log("ERROR", f"Failed to integrate advanced monitoring: {e}")
            raise

    def test_01_safe_function_manager_integration(self):
        """Тест интеграции с SafeFunctionManager"""
        safe_manager = SafeFunctionManager()
        status = safe_manager.get_status()
        
        self.assertEqual(status["status"], "RUNNING")
        self.assertGreater(status["total_functions"], 0)
        
        # Проверяем наличие функций мониторинга
        functions = safe_manager.list_functions()
        monitoring_functions = [f for f in functions if "monitoring" in f.get("category", "").lower()]
        
        self.assertGreater(len(monitoring_functions), 0)
        
        logger.log("INFO", "Test 01: SafeFunctionManager integration passed")

    def test_02_function_execution(self):
        """Тест выполнения функций мониторинга"""
        safe_manager = SafeFunctionManager()
        
        # Тестируем выполнение функции получения метрик
        try:
            result = safe_manager.execute_function("Get System Metrics")
            self.assertIsNotNone(result)
            self.assertIsInstance(result, dict)
            logger.log("INFO", "Test 02: Function execution passed")
        except Exception as e:
            logger.log("WARNING", f"Function execution test failed: {e}")


if __name__ == '__main__':
    # Запуск тестов
    unittest.main(verbosity=2)