# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Tests for Security Integration
Тесты для интеграции системы безопасности

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
"""

import os
import sys
import unittest

from core.base import ComponentStatus
from security.access_control import AccessControl, Permission, UserRole
from security.audit_system import AuditLevel, AuditSystem
from security.minimal_security_integration import (
    MinimalSecurityIntegration as SecurityIntegration,
)
from security.secure_wrapper import SecureModuleWrapper
from security.security_layer import SecurityLayer, SecurityRisk

# Добавляем путь к модулям проекта
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


class TestSecurityIntegration(unittest.TestCase):
    """Тесты для интеграции системы безопасности"""

    def setUp(self):
        """Настройка тестов"""
        self.config = {
            "enable_real_time_protection": False,
            "auto_block_high_risk": True,
            "require_approval_for_critical": True,
            "max_operations_per_minute": 10,
            "audit_retention_days": 7,
            "max_events_in_memory": 1000,
            "enable_real_time_audit": False,
            "max_failed_attempts": 3,
            "lockout_duration": 60,
            "session_timeout": 300,
            "enable_ip_whitelist": False,
            "enable_mfa": False,
            "auto_integrate": False,
            "enable_wrappers": True,
            "strict_mode": True,
        }

    def test_security_layer_initialization(self):
        """Тест инициализации SecurityLayer"""
        print("Тест инициализации SecurityLayer...")

        security_layer = SecurityLayer(config=self.config)
        result = security_layer.initialize()

        self.assertTrue(result, "SecurityLayer должен инициализироваться успешно")
        self.assertEqual(security_layer.status, ComponentStatus.RUNNING)

        # Проверка базовых правил безопасности
        self.assertGreater(len(security_layer.security_rules), 0)
        self.assertIn("delete_user", security_layer.security_rules)
        self.assertIn("read_data", security_layer.security_rules)

        print("✅ SecurityLayer инициализирован успешно")

    def test_audit_system_initialization(self):
        """Тест инициализации AuditSystem"""
        print("Тест инициализации AuditSystem...")

        audit_system = AuditSystem(config=self.config)
        result = audit_system.initialize()

        self.assertTrue(result, "AuditSystem должен инициализироваться успешно")
        self.assertEqual(audit_system.status, ComponentStatus.RUNNING)

        # Проверка уровней аудита
        self.assertGreater(len(audit_system.audit_levels), 0)
        self.assertIn(AuditLevel.INFO, audit_system.audit_levels)
        self.assertIn(AuditLevel.CRITICAL, audit_system.audit_levels)

        print("✅ AuditSystem инициализирован успешно")

    def test_access_control_initialization(self):
        """Тест инициализации AccessControl"""
        print("Тест инициализации AccessControl...")

        access_control = AccessControl(config=self.config)
        result = access_control.initialize()

        self.assertTrue(result, "AccessControl должен инициализироваться успешно")
        self.assertEqual(access_control.status, ComponentStatus.RUNNING)

        # Проверка ролевых разрешений
        self.assertGreater(len(access_control.role_permissions), 0)
        self.assertIn(UserRole.ADMIN, access_control.role_permissions)
        self.assertIn(UserRole.MONITOR, access_control.role_permissions)

        # Проверка системных пользователей
        self.assertGreater(len(access_control.users), 0)
        self.assertIn("admin", access_control.users)

        print("✅ AccessControl инициализирован успешно")

    def test_security_integration_initialization(self):
        """Тест инициализации SecurityIntegration"""
        print("Тест инициализации SecurityIntegration...")

        security_integration = SecurityIntegration(config=self.config)
        result = security_integration.initialize()

        self.assertTrue(result, "SecurityIntegration должен инициализироваться успешно")
        self.assertEqual(security_integration.status, ComponentStatus.RUNNING)

        # Проверка компонентов безопасности
        self.assertEqual(security_integration.security_layer.status, ComponentStatus.RUNNING)
        self.assertEqual(security_integration.audit_system.status, ComponentStatus.RUNNING)
        self.assertEqual(security_integration.access_control.status, ComponentStatus.RUNNING)

        print("✅ SecurityIntegration инициализирован успешно")

    def test_operation_validation(self):
        """Тест валидации операций"""
        print("Тест валидации операций...")

        security_layer = SecurityLayer(config=self.config)
        security_layer.initialize()

        # Тест разрешенной операции
        allowed, message, risk = security_layer.validate_operation("read_data", "admin")
        self.assertTrue(allowed, f"Операция 'read_data' должна быть разрешена: {message}")
        self.assertEqual(risk, SecurityRisk.LOW)

        # Тест запрещенной операции
        allowed, message, risk = security_layer.validate_operation("delete_user", "admin")
        self.assertFalse(allowed, f"Операция 'delete_user' должна быть запрещена: {message}")
        self.assertEqual(risk, SecurityRisk.CRITICAL)

        print("✅ Валидация операций работает корректно")

    def test_audit_event_logging(self):
        """Тест логирования событий аудита"""
        print("Тест логирования событий аудита...")

        audit_system = AuditSystem(config=self.config)
        audit_system.initialize()

        # Логирование события
        event_id = audit_system.log_audit_event(
            event_type="test_event",
            user="test_user",
            operation="test_operation",
            level=AuditLevel.INFO,
            details={"test": "data"},
        )

        self.assertIsNotNone(event_id, "ID события должен быть сгенерирован")
        self.assertIn(event_id, audit_system.audit_events)

        # Проверка статистики
        stats = audit_system.get_audit_statistics()
        self.assertGreater(stats["total_events"], 0)

        print("✅ Логирование событий аудита работает корректно")

    def test_user_authentication(self):
        """Тест аутентификации пользователей"""
        print("Тест аутентификации пользователей...")

        access_control = AccessControl(config=self.config)
        access_control.initialize()

        # Тест успешной аутентификации
        success, message, user = access_control.authenticate_user("admin", "admin123")
        self.assertTrue(success, f"Аутентификация admin должна быть успешной: {message}")
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "admin")
        self.assertEqual(user.role, UserRole.ADMIN)

        # Тест неудачной аутентификации
        success, message, user = access_control.authenticate_user("admin", "wrong_password")
        self.assertFalse(success, f"Аутентификация с неверным паролем должна быть неудачной: {message}")
        self.assertIsNone(user)

        print("✅ Аутентификация пользователей работает корректно")

    def test_session_management(self):
        """Тест управления сессиями"""
        print("Тест управления сессиями...")

        access_control = AccessControl(config=self.config)
        access_control.initialize()

        # Аутентификация пользователя
        success, message, user = access_control.authenticate_user("admin", "admin123")
        self.assertTrue(success)

        # Создание сессии
        session_id = access_control.create_session(user)
        self.assertIsNotNone(session_id)
        self.assertIn(session_id, access_control.active_sessions)

        # Валидация сессии
        valid, session = access_control.validate_session(session_id)
        self.assertTrue(valid)
        self.assertIsNotNone(session)
        self.assertEqual(session["user_id"], user.user_id)

        # Выход из системы
        logout_success = access_control.logout_user(session_id)
        self.assertTrue(logout_success)
        self.assertNotIn(session_id, access_control.active_sessions)

        print("✅ Управление сессиями работает корректно")

    def test_permission_checking(self):
        """Тест проверки разрешений"""
        print("Тест проверки разрешений...")

        access_control = AccessControl(config=self.config)
        access_control.initialize()

        # Аутентификация и создание сессии
        success, message, user = access_control.authenticate_user("admin", "admin123")
        session_id = access_control.create_session(user)

        # Проверка разрешений admin
        self.assertTrue(access_control.check_permission(session_id, Permission.READ_DATA))
        self.assertTrue(access_control.check_permission(session_id, Permission.WRITE_DATA))
        self.assertTrue(access_control.check_permission(session_id, Permission.DELETE_DATA))
        self.assertTrue(access_control.check_permission(session_id, Permission.MANAGE_USERS))

        # Аутентификация monitor пользователя
        success, message, monitor_user = access_control.authenticate_user("monitor", "monitor123")
        monitor_session = access_control.create_session(monitor_user)

        # Проверка ограниченных разрешений monitor
        self.assertTrue(access_control.check_permission(monitor_session, Permission.READ_DATA))
        self.assertFalse(access_control.check_permission(monitor_session, Permission.WRITE_DATA))
        self.assertFalse(access_control.check_permission(monitor_session, Permission.DELETE_DATA))
        self.assertFalse(access_control.check_permission(monitor_session, Permission.MANAGE_USERS))

        print("✅ Проверка разрешений работает корректно")

    def test_secure_operation_execution(self):
        """Тест безопасного выполнения операций"""
        print("Тест безопасного выполнения операций...")

        security_layer = SecurityLayer(config=self.config)
        security_layer.initialize()

        # Тест безопасной операции
        def safe_function(params):
            return {"result": "success", "data": params}

        success, result, message = security_layer.execute_with_protection(
            operation="read_data", user="admin", params={"test": "data"}, function=safe_function
        )

        self.assertTrue(success, f"Безопасная операция должна выполняться: {message}")
        self.assertIsNotNone(result)
        self.assertEqual(result["result"], "success")

        # Тест запрещенной операции
        success, result, message = security_layer.execute_with_protection(
            operation="delete_user", user="admin", params={"user_id": "test"}, function=safe_function
        )

        self.assertFalse(success, f"Запрещенная операция должна блокироваться: {message}")
        self.assertIsNone(result)

        print("✅ Безопасное выполнение операций работает корректно")

    def test_secure_wrapper_creation(self):
        """Тест создания безопасных оберток"""
        print("Тест создания безопасных оберток...")

        # Создание тестового модуля
        class TestModule:
            def test_operation(self, params):
                return {"result": "test_success"}

        test_module = TestModule()

        # Создание безопасной обертки
        wrapper = SecureModuleWrapper("TestModule")

        # Тест выполнения операции через обертку
        success, result, message = wrapper.execute_secure_operation(
            operation="test_operation",
            user="admin",
            params={"test": "data"},
            function=lambda p: test_module.test_operation(p),
        )

        self.assertTrue(success, f"Операция через обертку должна выполняться: {message}")
        self.assertIsNotNone(result)

        print("✅ Создание безопасных оберток работает корректно")

    def test_security_statistics(self):
        """Тест получения статистики безопасности"""
        print("Тест получения статистики безопасности...")

        security_integration = SecurityIntegration(config=self.config)
        security_integration.initialize()

        # Получение статистики
        stats = security_integration.get_security_statistics()

        # Проверка структуры статистики
        self.assertIn("security_layer", stats)
        self.assertIn("audit_system", stats)
        self.assertIn("access_control", stats)
        self.assertIn("integration", stats)

        # Проверка статистики SecurityLayer
        security_stats = stats["security_layer"]
        self.assertIn("total_operations", security_stats)
        self.assertIn("blocked_operations", security_stats)
        self.assertIn("approved_operations", security_stats)

        print("✅ Получение статистики безопасности работает корректно")

    def test_security_report_generation(self):
        """Тест генерации отчета по безопасности"""
        print("Тест генерации отчета по безопасности...")

        security_integration = SecurityIntegration(config=self.config)
        security_integration.initialize()

        # Генерация отчета
        report = security_integration.generate_security_report()

        # Проверка структуры отчета
        self.assertIn("report_id", report)
        self.assertIn("generated_at", report)
        self.assertIn("integration_status", report)
        self.assertIn("security_statistics", report)
        self.assertIn("component_status", report)
        self.assertIn("summary", report)

        # Проверка сводки
        summary = report["summary"]
        self.assertIn("total_modules", summary)
        self.assertIn("secured_modules", summary)
        self.assertIn("security_level", summary)
        self.assertIn("integration_complete", summary)

        print("✅ Генерация отчета по безопасности работает корректно")

    def tearDown(self):
        """Очистка после тестов"""


def run_security_integration_tests():
    """Запуск тестов интеграции безопасности"""
    print("=" * 70)
    print("ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ СИСТЕМЫ БЕЗОПАСНОСТИ")
    print("=" * 70)

    # Создаем тестовый набор
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestSecurityIntegration)

    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Выводим результаты
    print("\n" + "=" * 70)
    print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ ИНТЕГРАЦИИ БЕЗОПАСНОСТИ")
    print("=" * 70)
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
        print("\n✅ ВСЕ ТЕСТЫ ИНТЕГРАЦИИ БЕЗОПАСНОСТИ ПРОШЛИ УСПЕШНО!")
    else:
        print("\n❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ!")

    return result.wasSuccessful()


if __name__ == "__main__":
    run_security_integration_tests()
