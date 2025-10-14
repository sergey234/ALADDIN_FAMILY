# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Tests for Safe Security Monitoring
Тесты для безопасного модуля мониторинга безопасности

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
"""

import os
import sys
import unittest

from config.safe_config import SecurityMode
from core.base import ComponentStatus
from security.safe_security_monitoring import (
    AlertSeverity,
    MonitoringRule,
    MonitoringType,
    SafeSecurityMonitoringManager,
    SecurityAlert,
    create_safe_monitoring_manager,
)

# Добавляем путь к модулям проекта
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


class TestSafeSecurityMonitoring(unittest.TestCase):
    """Тесты для безопасного мониторинга безопасности"""

    def setUp(self):
        """Настройка тестов"""
        self.config = {
            "monitoring_interval": 5,
            "alert_retention_days": 7,
            "enable_real_time": False,  # Отключаем для тестов
            "max_concurrent_monitors": 5,
        }
        self.monitoring_manager = SafeSecurityMonitoringManager(config=self.config)

    def test_safe_monitoring_initialization(self):
        """Тест инициализации безопасного мониторинга"""
        print("Тест инициализации безопасного мониторинга...")

        # Проверяем инициализацию
        result = self.monitoring_manager.initialize()
        self.assertTrue(result, "Инициализация должна быть успешной")

        # Проверяем статус
        self.assertEqual(self.monitoring_manager.status, ComponentStatus.RUNNING)

        # Проверяем безопасную конфигурацию
        self.assertEqual(self.monitoring_manager.safe_config.security_mode, SecurityMode.SAFE)

        print("✅ Инициализация безопасного мониторинга прошла успешно")

    def test_safe_operations_only(self):
        """Тест что разрешены только безопасные операции"""
        print("Тест безопасных операций...")

        # Проверяем разрешенные операции
        self.assertTrue(self.monitoring_manager.safe_config.is_operation_allowed("read"))
        self.assertTrue(self.monitoring_manager.safe_config.is_operation_allowed("monitor"))
        self.assertTrue(self.monitoring_manager.safe_config.is_operation_allowed("analyze"))
        self.assertTrue(self.monitoring_manager.safe_config.is_operation_allowed("report"))

        # Проверяем запрещенные операции
        self.assertFalse(self.monitoring_manager.safe_config.is_operation_allowed("delete"))
        self.assertFalse(self.monitoring_manager.safe_config.is_operation_allowed("remove"))
        self.assertFalse(self.monitoring_manager.safe_config.is_operation_allowed("modify"))
        self.assertFalse(self.monitoring_manager.safe_config.is_operation_allowed("execute"))

        print("✅ Проверка безопасных операций прошла успешно")

    def test_monitoring_rules_read_only(self):
        """Тест чтения правил мониторинга"""
        print("Тест чтения правил мониторинга...")

        # Инициализируем менеджер
        self.monitoring_manager.initialize()

        # Получаем правила мониторинга
        rules = self.monitoring_manager.get_monitoring_rules()

        # Проверяем что правила есть
        self.assertIsInstance(rules, dict)
        self.assertGreater(len(rules), 0, "Должны быть базовые правила мониторинга")

        # Проверяем структуру правила
        for rule_id, rule_data in rules.items():
            self.assertIn("rule_id", rule_data)
            self.assertIn("name", rule_data)
            self.assertIn("description", rule_data)
            self.assertIn("monitoring_type", rule_data)
            self.assertIn("severity", rule_data)

        print("✅ Чтение правил мониторинга прошло успешно")

    def test_alert_management_read_only(self):
        """Тест управления оповещениями (только чтение)"""
        print("Тест управления оповещениями...")

        # Инициализируем менеджер
        self.monitoring_manager.initialize()

        # Получаем активные оповещения
        active_alerts = self.monitoring_manager.get_active_alerts()
        self.assertIsInstance(active_alerts, dict)

        # Получаем историю оповещений
        alert_history = self.monitoring_manager.get_alert_history()
        self.assertIsInstance(alert_history, list)

        print("✅ Управление оповещениями прошло успешно")

    def test_monitoring_statistics(self):
        """Тест статистики мониторинга"""
        print("Тест статистики мониторинга...")

        # Инициализируем менеджер
        self.monitoring_manager.initialize()

        # Получаем статистику
        stats = self.monitoring_manager.get_monitoring_statistics()

        # Проверяем структуру статистики
        self.assertIsInstance(stats, dict)
        self.assertIn("total_alerts", stats)
        self.assertIn("active_alerts_count", stats)
        self.assertIn("monitoring_rules_count", stats)
        self.assertIn("status", stats)
        self.assertIn("uptime", stats)

        # Проверяем типы данных
        self.assertIsInstance(stats["total_alerts"], int)
        self.assertIsInstance(stats["active_alerts_count"], int)
        self.assertIsInstance(stats["monitoring_rules_count"], int)
        self.assertIsInstance(stats["uptime"], (int, float))

        print("✅ Статистика мониторинга получена успешно")

    def test_security_report_generation(self):
        """Тест генерации отчета по безопасности"""
        print("Тест генерации отчета по безопасности...")

        # Инициализируем менеджер
        self.monitoring_manager.initialize()

        # Генерируем отчет
        report = self.monitoring_manager.generate_security_report()

        # Проверяем структуру отчета
        self.assertIsInstance(report, dict)
        self.assertIn("report_id", report)
        self.assertIn("generated_at", report)
        self.assertIn("monitoring_manager", report)
        self.assertIn("status", report)
        self.assertIn("statistics", report)
        self.assertIn("active_alerts", report)
        self.assertIn("monitoring_rules", report)
        self.assertIn("summary", report)

        # Проверяем сводку
        summary = report["summary"]
        self.assertIn("total_alerts", summary)
        self.assertIn("critical_alerts", summary)
        self.assertIn("warning_alerts", summary)
        self.assertIn("system_health", summary)

        print("✅ Отчет по безопасности сгенерирован успешно")

    def test_operation_validation(self):
        """Тест валидации операций"""
        print("Тест валидации операций...")

        # Проверяем разрешенные операции
        allowed, message = self.monitoring_manager.validate_monitoring_operation("read")
        self.assertTrue(allowed, f"Операция 'read' должна быть разрешена: {message}")

        allowed, message = self.monitoring_manager.validate_monitoring_operation("analyze")
        self.assertTrue(allowed, f"Операция 'analyze' должна быть разрешена: {message}")

        # Проверяем запрещенные операции
        allowed, message = self.monitoring_manager.validate_monitoring_operation("delete")
        self.assertFalse(allowed, f"Операция 'delete' должна быть запрещена: {message}")

        allowed, message = self.monitoring_manager.validate_monitoring_operation("remove")
        self.assertFalse(allowed, f"Операция 'remove' должна быть запрещена: {message}")

        print("✅ Валидация операций прошла успешно")

    def test_safe_monitoring_status(self):
        """Тест статуса безопасного мониторинга"""
        print("Тест статуса безопасного мониторинга...")

        # Инициализируем менеджер
        self.monitoring_manager.initialize()

        # Получаем статус
        status = self.monitoring_manager.get_status()

        # Проверяем структуру статуса
        self.assertIsInstance(status, dict)
        self.assertIn("name", status)
        self.assertIn("status", status)
        self.assertIn("security_mode", status)
        self.assertIn("monitoring_enabled", status)
        self.assertIn("active_monitors", status)
        self.assertIn("monitoring_rules", status)
        self.assertIn("active_alerts", status)
        self.assertIn("uptime", status)
        self.assertIn("safe_operations_only", status)

        # Проверяем что только безопасные операции
        self.assertTrue(status["safe_operations_only"])

        print("✅ Статус безопасного мониторинга получен успешно")

    def test_create_safe_monitoring_manager(self):
        """Тест создания безопасного менеджера мониторинга"""
        print("Тест создания безопасного менеджера мониторинга...")

        # Создаем менеджер через функцию
        manager = create_safe_monitoring_manager(self.config)

        # Проверяем что менеджер создан и инициализирован
        self.assertIsInstance(manager, SafeSecurityMonitoringManager)
        self.assertEqual(manager.status, ComponentStatus.RUNNING)

        # Проверяем безопасную конфигурацию
        self.assertEqual(manager.safe_config.security_mode, SecurityMode.SAFE)

        print("✅ Создание безопасного менеджера мониторинга прошло успешно")

    def test_monitoring_rule_creation(self):
        """Тест создания правил мониторинга"""
        print("Тест создания правил мониторинга...")

        # Создаем правило мониторинга
        rule = MonitoringRule(
            rule_id="test_rule",
            name="Тестовое правило",
            description="Тестовое правило для проверки",
            monitoring_type=MonitoringType.REAL_TIME,
            target_component="test_component",
            condition="test_condition == True",
            severity=AlertSeverity.INFO,
        )

        # Проверяем свойства правила
        self.assertEqual(rule.rule_id, "test_rule")
        self.assertEqual(rule.name, "Тестовое правило")
        self.assertEqual(rule.monitoring_type, MonitoringType.REAL_TIME)
        self.assertEqual(rule.severity, AlertSeverity.INFO)
        self.assertTrue(rule.enabled)

        # Проверяем преобразование в словарь
        rule_dict = rule.to_dict()
        self.assertIsInstance(rule_dict, dict)
        self.assertEqual(rule_dict["rule_id"], "test_rule")

        print("✅ Создание правил мониторинга прошло успешно")

    def test_security_alert_creation(self):
        """Тест создания оповещений безопасности"""
        print("Тест создания оповещений безопасности...")

        # Создаем оповещение
        alert = SecurityAlert(
            alert_id="test_alert",
            rule_id="test_rule",
            severity=AlertSeverity.WARNING,
            message="Тестовое оповещение",
            source="test_source",
        )

        # Проверяем свойства оповещения
        self.assertEqual(alert.alert_id, "test_alert")
        self.assertEqual(alert.rule_id, "test_rule")
        self.assertEqual(alert.severity, AlertSeverity.WARNING)
        self.assertEqual(alert.message, "Тестовое оповещение")
        self.assertEqual(alert.source, "test_source")
        self.assertFalse(alert.acknowledged)
        self.assertFalse(alert.resolved)

        # Проверяем преобразование в словарь
        alert_dict = alert.to_dict()
        self.assertIsInstance(alert_dict, dict)
        self.assertEqual(alert_dict["alert_id"], "test_alert")

        print("✅ Создание оповещений безопасности прошло успешно")

    def tearDown(self):
        """Очистка после тестов"""
        if hasattr(self, "monitoring_manager"):
            self.monitoring_manager.stop()


def run_safe_monitoring_tests():
    """Запуск тестов безопасного мониторинга"""
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ БЕЗОПАСНОГО МОНИТОРИНГА БЕЗОПАСНОСТИ")
    print("=" * 60)

    # Создаем тестовый набор
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestSafeSecurityMonitoring)

    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Выводим результаты
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ БЕЗОПАСНОГО МОНИТОРИНГА")
    print("=" * 60)
    print(f"Всего тестов: {result.testsRun}")
    print(f"Успешно: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Ошибок: {len(result.errors)}")
    print(f"Провалов: {len(result.failures)}")

    if result.failures:
        print("\nПРОВАЛЫ:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")

    if result.errors:
        print("\nОШИБКИ:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")

    if result.wasSuccessful():
        print("\n✅ ВСЕ ТЕСТЫ БЕЗОПАСНОГО МОНИТОРИНГА ПРОШЛИ УСПЕШНО!")
    else:
        print("\n❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ!")

    return result.wasSuccessful()


if __name__ == "__main__":
    run_safe_monitoring_tests()
