# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Core Functions Tests
Тесты для основных функций core модуля

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-01
"""

import os
import sys
import unittest

from core.base import (
    ComponentStatus,
    CoreBase,
    SecurityBase,
    SecurityLevel,
    ServiceBase,
)

# Добавляем путь к модулям
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestCoreBase(unittest.TestCase):
    """Тесты для базового класса CoreBase"""

    def setUp(self):
        """Настройка тестов"""
        self.test_config = {"test_param": "test_value"}

    def test_core_base_initialization(self):
        """Тест инициализации CoreBase"""

        # Создаем тестовый класс, наследующий от CoreBase
        class TestComponent(CoreBase):
            def initialize(self):
                return True

            def start(self):
                return True

            def stop(self):
                return True

        component = TestComponent("TestComponent", self.test_config)

        # Проверяем инициализацию
        self.assertEqual(component.name, "TestComponent")
        self.assertEqual(component.config, self.test_config)
        self.assertEqual(component.status, ComponentStatus.INITIALIZING)
        self.assertIsNotNone(component.logger)
        self.assertIsNotNone(component.metrics)

    def test_core_base_metrics(self):
        """Тест обновления метрик"""

        class TestComponent(CoreBase):
            def initialize(self):
                return True

            def start(self):
                return True

            def stop(self):
                return True

        component = TestComponent("TestComponent")

        # Обновляем метрики
        component.update_metrics(True, 1.5)
        component.update_metrics(False, 2.0)

        # Проверяем метрики
        self.assertEqual(component.metrics["total_operations"], 2)
        self.assertEqual(component.metrics["successful_operations"], 1)
        self.assertEqual(component.metrics["failed_operations"], 1)
        self.assertGreater(component.metrics["average_response_time"], 0)

    def test_core_base_status(self):
        """Тест получения статуса"""

        class TestComponent(CoreBase):
            def initialize(self):
                return True

            def start(self):
                return True

            def stop(self):
                return True

        component = TestComponent("TestComponent")
        status = component.get_status()

        # Проверяем структуру статуса
        self.assertIn("name", status)
        self.assertIn("status", status)
        self.assertIn("metrics", status)
        self.assertEqual(status["name"], "TestComponent")


class TestServiceBase(unittest.TestCase):
    """Тесты для базового класса ServiceBase"""

    def setUp(self):
        """Настройка тестов"""
        self.test_config = {"service_param": "service_value"}

    def test_service_base_initialization(self):
        """Тест инициализации ServiceBase"""
        service = ServiceBase("TestService", self.test_config)

        # Проверяем инициализацию
        self.assertEqual(service.name, "TestService")
        self.assertEqual(service.config, self.test_config)
        self.assertIsInstance(service.services, dict)
        self.assertIsInstance(service.dependencies, list)

    def test_service_base_operations(self):
        """Тест операций с сервисами"""
        service = ServiceBase("TestService")

        # Добавляем сервис
        test_service = {"name": "test"}
        service.add_service("test_service", test_service)

        # Проверяем добавление
        self.assertIn("test_service", service.services)
        self.assertEqual(service.services["test_service"], test_service)

        # Получаем сервис
        retrieved_service = service.get_service("test_service")
        self.assertEqual(retrieved_service, test_service)

        # Удаляем сервис
        result = service.remove_service("test_service")
        self.assertTrue(result)
        self.assertNotIn("test_service", service.services)

    def test_service_base_health_check(self):
        """Тест проверки здоровья сервиса"""
        service = ServiceBase("TestService")
        health_status = service.health_check()

        # Проверяем структуру статуса здоровья
        self.assertIn("service_name", health_status)
        self.assertIn("status", health_status)
        self.assertIn("timestamp", health_status)
        self.assertIn("dependencies", health_status)
        self.assertIn("active_services", health_status)
        self.assertIn("metrics", health_status)
        self.assertEqual(health_status["service_name"], "TestService")


class TestSecurityBase(unittest.TestCase):
    """Тесты для базового класса SecurityBase"""

    def setUp(self):
        """Настройка тестов"""
        self.test_config = {"security_param": "security_value"}

    def test_security_base_initialization(self):
        """Тест инициализации SecurityBase"""
        security = SecurityBase("TestSecurity", self.test_config)

        # Проверяем инициализацию
        self.assertEqual(security.name, "TestSecurity")
        self.assertEqual(security.config, self.test_config)
        self.assertEqual(security.security_level, SecurityLevel.MEDIUM)
        self.assertEqual(security.threats_detected, 0)
        self.assertEqual(security.incidents_handled, 0)
        self.assertIsInstance(security.security_rules, list)
        self.assertTrue(security.encryption_enabled)

    def test_security_base_level_setting(self):
        """Тест установки уровня безопасности"""
        security = SecurityBase("TestSecurity")

        # Устанавливаем уровень безопасности
        security.set_security_level(SecurityLevel.HIGH)
        self.assertEqual(security.security_level, SecurityLevel.HIGH)

        security.set_security_level(SecurityLevel.CRITICAL)
        self.assertEqual(security.security_level, SecurityLevel.CRITICAL)

    def test_security_base_rules(self):
        """Тест добавления правил безопасности"""
        security = SecurityBase("TestSecurity")

        # Добавляем правило
        test_rule = {"name": "test_rule", "type": "authentication", "enabled": True}
        security.add_security_rule(test_rule)

        # Проверяем добавление
        self.assertIn(test_rule, security.security_rules)
        self.assertEqual(len(security.security_rules), 1)

    def test_security_base_threat_detection(self):
        """Тест обнаружения угроз"""
        security = SecurityBase("TestSecurity")

        # Обнаруживаем угрозу
        threat_info = {"type": "malware", "description": "Test malware threat", "source": "test_source"}

        result = security.detect_threat(threat_info)

        # Проверяем результат
        self.assertTrue(result)
        self.assertEqual(security.threats_detected, 1)
        self.assertEqual(security.incidents_handled, 1)

    def test_security_base_report(self):
        """Тест получения отчета по безопасности"""
        security = SecurityBase("TestSecurity")
        report = security.get_security_report()

        # Проверяем структуру отчета
        self.assertIn("component_name", report)
        self.assertIn("security_level", report)
        self.assertIn("threats_detected", report)
        self.assertIn("incidents_handled", report)
        self.assertIn("security_rules_count", report)
        self.assertIn("encryption_enabled", report)
        self.assertIn("status", report)
        self.assertEqual(report["component_name"], "TestSecurity")


class TestComponentStatus(unittest.TestCase):
    """Тесты для перечисления статусов компонентов"""

    def test_component_status_values(self):
        """Тест значений статусов компонентов"""
        self.assertEqual(ComponentStatus.INITIALIZING.value, "initializing")
        self.assertEqual(ComponentStatus.RUNNING.value, "running")
        self.assertEqual(ComponentStatus.STOPPED.value, "stopped")
        self.assertEqual(ComponentStatus.ERROR.value, "error")
        self.assertEqual(ComponentStatus.MAINTENANCE.value, "maintenance")


class TestSecurityLevel(unittest.TestCase):
    """Тесты для перечисления уровней безопасности"""

    def test_security_level_values(self):
        """Тест значений уровней безопасности"""
        self.assertEqual(SecurityLevel.LOW.value, "low")
        self.assertEqual(SecurityLevel.MEDIUM.value, "medium")
        self.assertEqual(SecurityLevel.HIGH.value, "high")
        self.assertEqual(SecurityLevel.CRITICAL.value, "critical")


if __name__ == "__main__":
    # Создаем тестовый набор
    test_suite = unittest.TestSuite()

    # Добавляем тесты
    test_suite.addTest(unittest.makeSuite(TestCoreBase))
    test_suite.addTest(unittest.makeSuite(TestServiceBase))
    test_suite.addTest(unittest.makeSuite(TestSecurityBase))
    test_suite.addTest(unittest.makeSuite(TestComponentStatus))
    test_suite.addTest(unittest.makeSuite(TestSecurityLevel))

    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Выводим результат
    print("\n" + "=" * 50)
    print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ CORE МОДУЛЯ")
    print("=" * 50)
    print(f"Всего тестов: {result.testsRun}")
    print(f"Успешно: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Ошибок: {len(result.errors)}")
    print(f"Провалов: {len(result.failures)}")

    if result.failures:
        print("\nПРОВАЛЕННЫЕ ТЕСТЫ:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")

    if result.errors:
        print("\nОШИБКИ В ТЕСТАХ:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")

    if result.wasSuccessful():
        print("\n✅ ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
    else:
        print("\n❌ ЕСТЬ ПРОБЛЕМЫ В ТЕСТАХ!")
