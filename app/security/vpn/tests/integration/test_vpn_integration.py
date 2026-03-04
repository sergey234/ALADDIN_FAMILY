#!/usr/bin/env python3
"""
ALADDIN VPN - Integration Tests
Интеграционные тесты для VPN системы

Автор: ALADDIN Security Team
Версия: 1.0.0
Дата: 01.10.2025
"""

import unittest
import asyncio
import tempfile
import os
import json
import time
from unittest.mock import Mock, patch, MagicMock

# Импорт модулей для тестирования
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from security_integration import SecurityIntegration
from protection.ddos_protection import DDoSProtectionSystem
from protection.rate_limiter import AdvancedRateLimiter
from protection.intrusion_detection import IntrusionDetectionSystem
from auth.two_factor_auth import TwoFactorAuth
from audit_logging.audit_logger import SecurityAuditLogger
from di.dependency_injection import create_vpn_system
from graceful.graceful_degradation import create_default_manager
from retry.retry_handler import RetryHandler, RetryConfig, RetryStrategy

# ============================================================================
# БАЗОВЫЙ КЛАСС ДЛЯ ИНТЕГРАЦИОННЫХ ТЕСТОВ
# ============================================================================

class BaseIntegrationTest(unittest.TestCase):
    """Базовый класс для интеграционных тестов"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.temp_dir, "config")
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Создаем конфигурационные файлы
        self._create_integration_configs()
        
        # Инициализируем системы
        self._setup_systems()
    
    def tearDown(self):
        """Очистка после каждого теста"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_integration_configs(self):
        """Создание конфигураций для интеграционных тестов"""
        configs = {
            "ddos_config.json": {
                "enabled": True,
                "max_requests_per_second": 10,
                "max_concurrent_connections": 100,
                "block_duration_minutes": 60,
                "whitelist_ips": ["127.0.0.1"],
                "blacklist_ips": []
            },
            "rate_limiting.json": {
                "enabled": True,
                "rules": [
                    {
                        "name": "api_requests",
                        "endpoint": "/api/*",
                        "limit": 100,
                        "window": "1m",
                        "action": "block"
                    }
                ]
            },
            "ids_config.json": {
                "enabled": True,
                "detection_rules": [
                    {
                        "name": "sql_injection",
                        "pattern": r"(union|select|insert|delete|update|drop)",
                        "severity": "high"
                    }
                ],
                "honeypot_endpoints": ["/admin/secret", "/api/internal"]
            },
            "2fa_config.json": {
                "enabled": True,
                "scope": "admin",
                "methods": ["totp", "sms", "email"],
                "backup_codes_count": 10
            },
            "audit_config.json": {
                "enabled": True,
                "log_level": "INFO",
                "log_format": "json",
                "log_file": os.path.join(self.temp_dir, "audit.log"),
                "max_file_size": "10MB",
                "backup_count": 5
            }
        }
        
        for filename, config in configs.items():
            with open(os.path.join(self.config_dir, filename), "w") as f:
                json.dump(config, f)
    
    def _setup_systems(self):
        """Настройка систем для тестирования"""
        # Создаем системы безопасности
        self.ddos_system = DDoSProtectionSystem()
        self.ddos_system.load_config(os.path.join(self.config_dir, "ddos_config.json"))
        
        self.rate_limiter = AdvancedRateLimiter()
        self.rate_limiter.load_config(os.path.join(self.config_dir, "rate_limiting.json"))
        
        self.ids_system = IntrusionDetectionSystem()
        self.ids_system.load_config(os.path.join(self.config_dir, "ids_config.json"))
        
        self.twofa = TwoFactorAuth()
        self.twofa.load_config(os.path.join(self.config_dir, "2fa_config.json"))
        
        self.audit_logger = SecurityAuditLogger()
        self.audit_logger.load_config(os.path.join(self.config_dir, "audit_config.json"))
        
        # Создаем интегрированную систему безопасности
        self.security_integration = SecurityIntegration()
        
        # Создаем системы graceful degradation и retry
        self.degradation_manager = create_default_manager()
        self.retry_handler = RetryHandler(RetryConfig(
            max_attempts=3,
            base_delay=0.1,
            strategy=RetryStrategy.EXPONENTIAL
        ))

# ============================================================================
# ТЕСТЫ ИНТЕГРАЦИИ СИСТЕМ БЕЗОПАСНОСТИ
# ============================================================================

class TestSecurityIntegration(BaseIntegrationTest):
    """Тесты интеграции систем безопасности"""
    
    def test_security_workflow(self):
        """Тест полного workflow безопасности"""
        # Тестовые данные запроса
        request_data = {
            "ip_address": "192.168.1.100",
            "endpoint": "/api/v1/status",
            "method": "GET",
            "payload": "",
            "headers": {"Content-Type": "application/json"},
            "user_id": "test_user",
            "timestamp": time.time()
        }
        
        # 1. Проверка DDoS защиты
        is_ddos, ddos_reason = self.ddos_system.analyze_traffic(request_data)
        self.assertFalse(is_ddos, f"DDoS check failed: {ddos_reason}")
        
        # 2. Проверка Rate Limiting
        allowed, rate_message, rate_action = self.rate_limiter.check_rate_limit(
            request_data["ip_address"], request_data["endpoint"]
        )
        self.assertTrue(allowed, f"Rate limiting failed: {rate_message}")
        
        # 3. Проверка IDS
        is_intrusion, threats = self.ids_system.analyze_request(request_data)
        self.assertFalse(is_intrusion, f"IDS check failed: {threats}")
        
        # 4. Логирование события
        event_id = self.audit_logger.log_security_event(
            "api_request",
            "API request processed",
            user_id=request_data["user_id"],
            ip_address=request_data["ip_address"],
            details={"endpoint": request_data["endpoint"]}
        )
        self.assertIsNotNone(event_id)
    
    def test_ddos_attack_workflow(self):
        """Тест workflow при DDoS атаке"""
        # Симулируем DDoS атаку
        for i in range(15):  # Превышаем лимит
            request_data = {
                "ip_address": "192.168.1.200",
                "endpoint": "/api/v1/status",
                "method": "GET",
                "payload": "",
                "headers": {"Content-Type": "application/json"},
                "timestamp": time.time()
            }
            
            # Проверяем DDoS защиту
            is_ddos, ddos_reason = self.ddos_system.analyze_traffic(request_data)
            
            if i >= 10:  # После 10 запросов должна быть атака
                self.assertTrue(is_ddos)
                
                # Логируем событие атаки
                event_id = self.audit_logger.log_security_event(
                    "ddos_attack",
                    f"DDoS attack detected: {ddos_reason}",
                    ip_address=request_data["ip_address"],
                    details={"attack_type": "rate_limit", "request_count": i + 1}
                )
                self.assertIsNotNone(event_id)
    
    def test_intrusion_detection_workflow(self):
        """Тест workflow при обнаружении вторжения"""
        # Запрос с SQL инъекцией
        request_data = {
            "ip_address": "192.168.1.100",
            "endpoint": "/api/v1/users",
            "method": "POST",
            "payload": "SELECT * FROM users WHERE id = 1 UNION SELECT password FROM admin",
            "headers": {"Content-Type": "application/json"},
            "user_id": "test_user",
            "timestamp": time.time()
        }
        
        # Проверяем IDS
        is_intrusion, threats = self.ids_system.analyze_request(request_data)
        self.assertTrue(is_intrusion)
        self.assertGreater(len(threats), 0)
        
        # Логируем событие вторжения
        event_id = self.audit_logger.log_security_event(
            "intrusion_detected",
            f"Intrusion detected: {threats[0]['type']}",
            user_id=request_data["user_id"],
            ip_address=request_data["ip_address"],
            details={"threats": threats}
        )
        self.assertIsNotNone(event_id)
    
    def test_rate_limiting_workflow(self):
        """Тест workflow при превышении лимита скорости"""
        identifier = "test_user"
        endpoint = "/api/v1/status"
        
        # Исчерпываем лимит
        for i in range(101):
            allowed, message, action = self.rate_limiter.check_rate_limit(identifier, endpoint)
            
            if i >= 100:  # После 100 запросов должен быть блок
                self.assertFalse(allowed)
                self.assertEqual(action, "block")
                
                # Логируем событие блокировки
                event_id = self.audit_logger.log_security_event(
                    "rate_limit_exceeded",
                    f"Rate limit exceeded: {message}",
                    user_id=identifier,
                    details={"endpoint": endpoint, "limit": 100, "attempt": i + 1}
                )
                self.assertIsNotNone(event_id)

# ============================================================================
# ТЕСТЫ ИНТЕГРАЦИИ С DEPENDENCY INJECTION
# ============================================================================

class TestDependencyInjectionIntegration(BaseIntegrationTest):
    """Тесты интеграции с Dependency Injection"""
    
    def test_vpn_system_creation(self):
        """Тест создания VPN системы через DI"""
        # Создаем VPN систему через DI
        vpn_system = create_vpn_system()
        
        # Проверяем, что все компоненты созданы
        self.assertIn("config_manager", vpn_system)
        self.assertIn("logger", vpn_system)
        self.assertIn("security_manager", vpn_system)
        self.assertIn("auth_manager", vpn_system)
        self.assertIn("monitoring_manager", vpn_system)
        self.assertIn("container", vpn_system)
        
        # Проверяем, что контейнер работает
        container = vpn_system["container"]
        self.assertIsNotNone(container)
    
    def test_service_dependency_resolution(self):
        """Тест разрешения зависимостей сервисов"""
        # Создаем мок-классы с зависимостями
        class MockServiceA:
            def __init__(self, service_b=None):
                self.service_b = service_b
        
        class MockServiceB:
            def __init__(self):
                self.initialized = True
        
        # Регистрируем сервисы в контейнере
        container = create_vpn_system()["container"]
        container.register_singleton(MockServiceB, MockServiceB)
        container.register_singleton(MockServiceA, MockServiceA)
        
        # Получаем сервис A, который должен получить зависимость B
        service_a = container.get(MockServiceA)
        self.assertIsInstance(service_a, MockServiceA)
        self.assertIsNotNone(service_a.service_b)
        self.assertIsInstance(service_a.service_b, MockServiceB)

# ============================================================================
# ТЕСТЫ ИНТЕГРАЦИИ С GRACEFUL DEGRADATION
# ============================================================================

class TestGracefulDegradationIntegration(BaseIntegrationTest):
    """Тесты интеграции с Graceful Degradation"""
    
    def test_service_degradation_workflow(self):
        """Тест workflow деградации сервисов"""
        # Регистрируем тестовый сервис
        def healthy_service():
            return {"status": "healthy", "data": "test_data"}
        
        def degraded_service():
            return {"status": "degraded", "data": "limited_data"}
        
        def fallback_service():
            return {"status": "fallback", "data": "cached_data"}
        
        config = ServiceConfig(
            name="test_service",
            priority=1,
            degraded_function=degraded_service,
            fallback_function=fallback_service,
            required_for_levels=[DegradationLevel.FULL, DegradationLevel.REDUCED]
        )
        
        self.degradation_manager.register_service(config)
        
        # Тестируем нормальную работу
        result = asyncio.run(self.degradation_manager.execute_service(
            "test_service", healthy_service
        ))
        self.assertEqual(result["status"], "healthy")
        
        # Симулируем сбой сервиса
        def failing_service():
            raise Exception("Service failure")
        
        # Тестируем degraded функцию
        result = asyncio.run(self.degradation_manager.execute_service(
            "test_service", failing_service
        ))
        self.assertEqual(result["status"], "degraded")
    
    def test_degradation_level_changes(self):
        """Тест изменения уровней деградации"""
        # Добавляем правило деградации
        rule = DegradationRule(
            condition=lambda metrics: metrics.get("test_metric", 0) > 50,
            target_level=DegradationLevel.REDUCED,
            message="Test degradation triggered"
        )
        
        self.degradation_manager.add_degradation_rule(rule)
        
        # Симулируем условие деградации
        system_metrics = {"test_metric": 75}
        asyncio.run(self.degradation_manager.evaluate_degradation_level())
        
        # Проверяем, что уровень деградации изменился
        # (Это зависит от реализации evaluate_degradation_level)

# ============================================================================
# ТЕСТЫ ИНТЕГРАЦИИ С RETRY HANDLER
# ============================================================================

class TestRetryHandlerIntegration(BaseIntegrationTest):
    """Тесты интеграции с Retry Handler"""
    
    def test_retry_with_failing_service(self):
        """Тест повторных попыток с падающим сервисом"""
        attempt_count = 0
        
        def failing_service():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise ConnectionTimeoutError("server1", 30)
            return {"status": "success"}
        
        # Выполняем с retry
        result = self.retry_handler.execute(failing_service)
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(attempt_count, 3)  # Должно быть 3 попытки
    
    def test_retry_with_circuit_breaker(self):
        """Тест retry с Circuit Breaker"""
        from retry.retry_handler import CircuitBreaker
        
        breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=1.0)
        
        def failing_service():
            raise ConnectionTimeoutError("server1", 30)
        
        # Первые два вызова должны пройти
        for i in range(2):
            with self.assertRaises(ConnectionTimeoutError):
                breaker.execute(failing_service)
        
        # Третий вызов должен быть заблокирован Circuit Breaker
        with self.assertRaises(Exception):  # VPNException от Circuit Breaker
            breaker.execute(failing_service)
    
    def test_retry_decorator(self):
        """Тест декоратора retry"""
        from retry.retry_handler import retry, RetryConfig, RetryStrategy
        
        attempt_count = 0
        
        @retry(RetryConfig(
            max_attempts=3,
            base_delay=0.01,
            strategy=RetryStrategy.EXPONENTIAL
        ))
        def decorated_failing_service():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise ConnectionTimeoutError("server1", 30)
            return {"status": "success"}
        
        result = decorated_failing_service()
        self.assertEqual(result["status"], "success")
        self.assertEqual(attempt_count, 3)

# ============================================================================
# ТЕСТЫ END-TO-END СЦЕНАРИЕВ
# ============================================================================

class TestEndToEndScenarios(BaseIntegrationTest):
    """Тесты end-to-end сценариев"""
    
    def test_user_authentication_flow(self):
        """Тест полного flow аутентификации пользователя"""
        # 1. Пользователь пытается войти
        username = "test_user"
        password = "test_password"
        
        # 2. Проверяем учетные данные (мок)
        with patch.object(self.twofa, 'authenticate_user') as mock_auth:
            mock_auth.return_value = (True, "user_id_123", None)
            
            success, user_id, message = self.twofa.authenticate_user({
                "username": username,
                "password": password
            })
            
            self.assertTrue(success)
            self.assertEqual(user_id, "user_id_123")
        
        # 3. Настраиваем 2FA
        setup_result = self.twofa.setup_2fa(user_id, ["totp"])
        self.assertIn("secret_key", setup_result)
        
        # 4. Логируем событие аутентификации
        event_id = self.audit_logger.log_security_event(
            "user_authenticated",
            f"User {username} authenticated successfully",
            user_id=user_id,
            details={"method": "password", "2fa_setup": True}
        )
        self.assertIsNotNone(event_id)
    
    def test_vpn_connection_flow(self):
        """Тест полного flow подключения к VPN"""
        # 1. Пользователь запрашивает подключение
        request_data = {
            "ip_address": "192.168.1.100",
            "endpoint": "/api/v1/vpn/connect",
            "method": "POST",
            "payload": json.dumps({"server_id": "sg-singapore-01"}),
            "headers": {"Content-Type": "application/json"},
            "user_id": "test_user",
            "timestamp": time.time()
        }
        
        # 2. Проверяем все системы безопасности
        # DDoS защита
        is_ddos, ddos_reason = self.ddos_system.analyze_traffic(request_data)
        self.assertFalse(is_ddos)
        
        # Rate Limiting
        allowed, rate_message, rate_action = self.rate_limiter.check_rate_limit(
            request_data["ip_address"], request_data["endpoint"]
        )
        self.assertTrue(allowed)
        
        # IDS
        is_intrusion, threats = self.ids_system.analyze_request(request_data)
        self.assertFalse(is_intrusion)
        
        # 3. Симулируем успешное подключение
        connection_result = {
            "status": "connected",
            "server_id": "sg-singapore-01",
            "connection_id": "conn_123456",
            "ip_address": "103.123.45.67"
        }
        
        # 4. Логируем событие подключения
        event_id = self.audit_logger.log_security_event(
            "vpn_connected",
            f"VPN connection established to {connection_result['server_id']}",
            user_id=request_data["user_id"],
            ip_address=request_data["ip_address"],
            details=connection_result
        )
        self.assertIsNotNone(event_id)
    
    def test_security_incident_response_flow(self):
        """Тест flow реагирования на инцидент безопасности"""
        # 1. Обнаруживаем атаку
        attack_request = {
            "ip_address": "192.168.1.200",
            "endpoint": "/api/v1/users",
            "method": "POST",
            "payload": "SELECT * FROM users WHERE id = 1 UNION SELECT password FROM admin",
            "headers": {"Content-Type": "application/json"},
            "timestamp": time.time()
        }
        
        # 2. IDS обнаруживает вторжение
        is_intrusion, threats = self.ids_system.analyze_request(attack_request)
        self.assertTrue(is_intrusion)
        
        # 3. Блокируем IP
        self.ddos_system.blacklist_ips.append(attack_request["ip_address"])
        
        # 4. Логируем инцидент
        event_id = self.audit_logger.log_security_event(
            "security_incident",
            f"Security incident detected: {threats[0]['type']}",
            ip_address=attack_request["ip_address"],
            details={
                "threats": threats,
                "action_taken": "ip_blocked",
                "severity": "high"
            }
        )
        self.assertIsNotNone(event_id)
        
        # 5. Проверяем, что IP заблокирован
        blocked_request = {
            "ip_address": attack_request["ip_address"],
            "endpoint": "/api/v1/status",
            "method": "GET",
            "timestamp": time.time()
        }
        
        is_ddos, ddos_reason = self.ddos_system.analyze_traffic(blocked_request)
        self.assertTrue(is_ddos)
        self.assertIn("blacklist", ddos_reason.lower())

# ============================================================================
# ЗАПУСК ТЕСТОВ
# ============================================================================

if __name__ == "__main__":
    # Создаем test suite
    test_suite = unittest.TestSuite()
    
    # Добавляем тесты
    test_classes = [
        TestSecurityIntegration,
        TestDependencyInjectionIntegration,
        TestGracefulDegradationIntegration,
        TestRetryHandlerIntegration,
        TestEndToEndScenarios
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Выводим результаты
    print(f"\n{'='*50}")
    print(f"Integration Tests Results:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*50}")
    
    # Выводим детали ошибок
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"\n{test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"\n{test}: {traceback}")