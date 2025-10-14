#!/usr/bin/env python3
"""
ALADDIN VPN - Unit Tests for Architecture Components
Unit тесты для архитектурных компонентов VPN

Автор: ALADDIN Security Team
Версия: 1.0.0
Дата: 01.10.2025
"""

import unittest
import asyncio
import tempfile
import os
import json
from unittest.mock import Mock, patch, MagicMock

# Импорт модулей для тестирования
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config.vpn_constants import (
    VPNProtocol, EncryptionType, ConnectionStatus, ServerStatus,
    SecurityLevel, ErrorCode, DEFAULT_PORTS, SERVER_CONFIG,
    SECURITY_CONFIG, MONITORING_CONFIG, RATE_LIMITS, DDOS_LIMITS,
    validate_ip_address, validate_domain_name, get_supported_protocols,
    get_supported_countries, get_performance_tier
)

from interfaces.vpn_protocols import (
    VPNComponent, Configurable, Monitorable, VPNServer, VPNClient,
    SecurityManager, DDoSProtection, RateLimiter, IntrusionDetection,
    AuthenticationManager, TwoFactorAuth, Logger, AuditLogger,
    MonitoringManager, MetricsCollector, ConfigurationManager,
    NetworkManager, EncryptionManager, DatabaseManager, APIManager,
    IntegrationManager, VPNRequest, VPNResponse, SecurityEvent
)

from factories.vpn_factory import (
    VPNServerFactory, VPNClientFactory, SecuritySystemFactory,
    AuthSystemFactory, LoggerFactory, MonitoringSystemFactory,
    UniversalVPNFactory, VPNServerType, VPNClientType,
    SecuritySystemType, AuthSystemType, LoggerType, MonitoringSystemType
)

from di.dependency_injection import (
    DIContainer, ServiceRegistration, Scope, LifecycleType,
    GlobalDIContainer, get_container, register_vpn_services,
    create_vpn_system
)

from exceptions.vpn_exceptions import (
    VPNException, VPNConfigurationError, VPNConnectionError,
    VPNSecurityError, ConnectionTimeoutError, InvalidCredentialsError,
    DDoSAttackDetectedError, RateLimitExceededError, IntrusionDetectedError
)

from retry.retry_handler import (
    RetryHandler, CircuitBreaker, RetryConfig, RetryStrategy,
    RetryCondition, CircuitState, retry, circuit_breaker
)

from graceful.graceful_degradation import (
    GracefulDegradationManager, ServiceConfig, DegradationRule,
    DegradationLevel, ServiceStatus, graceful_degradation
)

# ============================================================================
# ТЕСТЫ КОНСТАНТ
# ============================================================================

class TestVPNConstants(unittest.TestCase):
    """Тесты констант VPN"""
    
    def test_vpn_protocols(self):
        """Тест VPN протоколов"""
        self.assertEqual(VPNProtocol.WIREGUARD.value, "wireguard")
        self.assertEqual(VPNProtocol.OPENVPN.value, "openvpn")
        self.assertEqual(VPNProtocol.IPSEC.value, "ipsec")
    
    def test_encryption_types(self):
        """Тест типов шифрования"""
        self.assertEqual(EncryptionType.AES_256_GCM.value, "aes-256-gcm")
        self.assertEqual(EncryptionType.CHACHA20_POLY1305.value, "chacha20-poly1305")
    
    def test_connection_status(self):
        """Тест статусов подключения"""
        self.assertEqual(ConnectionStatus.CONNECTED.value, "connected")
        self.assertEqual(ConnectionStatus.DISCONNECTED.value, "disconnected")
    
    def test_default_ports(self):
        """Тест портов по умолчанию"""
        self.assertEqual(DEFAULT_PORTS[VPNProtocol.WIREGUARD], 51820)
        self.assertEqual(DEFAULT_PORTS[VPNProtocol.OPENVPN], 1194)
    
    def test_server_config(self):
        """Тест конфигурации сервера"""
        self.assertEqual(SERVER_CONFIG["max_connections"], 1000)
        self.assertEqual(SERVER_CONFIG["max_bandwidth_mbps"], 1000)
    
    def test_security_config(self):
        """Тест конфигурации безопасности"""
        self.assertEqual(SECURITY_CONFIG["key_size"], 256)
        self.assertEqual(SECURITY_CONFIG["handshake_timeout"], 120)
    
    def test_monitoring_config(self):
        """Тест конфигурации мониторинга"""
        self.assertEqual(MONITORING_CONFIG["check_interval_seconds"], 60)
        self.assertEqual(MONITORING_CONFIG["memory_threshold_percent"], 80)
    
    def test_rate_limits(self):
        """Тест лимитов скорости"""
        self.assertEqual(RATE_LIMITS["max_requests_per_minute"], 100)
        self.assertEqual(RATE_LIMITS["max_requests_per_hour"], 1000)
    
    def test_ddos_limits(self):
        """Тест лимитов DDoS"""
        self.assertEqual(DDOS_LIMITS["max_requests_per_second"], 10)
        self.assertEqual(DDOS_LIMITS["max_concurrent_connections"], 100)
    
    def test_validation_functions(self):
        """Тест функций валидации"""
        # Валидные IP адреса
        self.assertTrue(validate_ip_address("192.168.1.1"))
        self.assertTrue(validate_ip_address("127.0.0.1"))
        self.assertTrue(validate_ip_address("8.8.8.8"))
        
        # Невалидные IP адреса
        self.assertFalse(validate_ip_address("256.256.256.256"))
        self.assertFalse(validate_ip_address("192.168.1"))
        self.assertFalse(validate_ip_address("not-an-ip"))
        
        # Валидные доменные имена
        self.assertTrue(validate_domain_name("example.com"))
        self.assertTrue(validate_domain_name("subdomain.example.com"))
        self.assertTrue(validate_domain_name("test-site.org"))
        
        # Невалидные доменные имена
        self.assertFalse(validate_domain_name(""))
        self.assertFalse(validate_domain_name("invalid..domain"))
        self.assertFalse(validate_domain_name("domain."))
    
    def test_supported_protocols(self):
        """Тест поддерживаемых протоколов"""
        protocols = get_supported_protocols()
        self.assertIn("wireguard", protocols)
        self.assertIn("openvpn", protocols)
        self.assertIn("ipsec", protocols)
    
    def test_supported_countries(self):
        """Тест поддерживаемых стран"""
        countries = get_supported_countries()
        self.assertIn("US", countries)
        self.assertIn("GB", countries)
        self.assertIn("DE", countries)
        self.assertIn("SG", countries)
    
    def test_performance_tiers(self):
        """Тест уровней производительности"""
        basic_tier = get_performance_tier("basic")
        self.assertEqual(basic_tier["max_connections"], 100)
        self.assertEqual(basic_tier["bandwidth_mbps"], 100)
        
        enterprise_tier = get_performance_tier("enterprise")
        self.assertEqual(enterprise_tier["max_connections"], 5000)
        self.assertEqual(enterprise_tier["bandwidth_mbps"], 5000)

# ============================================================================
# ТЕСТЫ ИНТЕРФЕЙСОВ
# ============================================================================

class TestVPNInterfaces(unittest.TestCase):
    """Тесты интерфейсов VPN"""
    
    def test_vpn_component_interface(self):
        """Тест интерфейса VPNComponent"""
        # Создаем мок-класс, реализующий интерфейс
        class MockVPNComponent(VPNComponent):
            def initialize(self):
                return True
            
            def shutdown(self):
                return True
            
            def get_status(self):
                return {"status": "active"}
            
            def get_metrics(self):
                return {"connections": 10}
        
        component = MockVPNComponent()
        self.assertTrue(component.initialize())
        self.assertTrue(component.shutdown())
        self.assertEqual(component.get_status()["status"], "active")
        self.assertEqual(component.get_metrics()["connections"], 10)
    
    def test_configurable_interface(self):
        """Тест интерфейса Configurable"""
        class MockConfigurable(Configurable):
            def load_config(self, config_path):
                return True
            
            def save_config(self, config_path):
                return True
            
            def validate_config(self):
                return True, []
        
        configurable = MockConfigurable()
        self.assertTrue(configurable.load_config("test.json"))
        self.assertTrue(configurable.save_config("test.json"))
        valid, errors = configurable.validate_config()
        self.assertTrue(valid)
        self.assertEqual(len(errors), 0)
    
    def test_monitorable_interface(self):
        """Тест интерфейса Monitorable"""
        class MockMonitorable(Monitorable):
            def start_monitoring(self):
                return True
            
            def stop_monitoring(self):
                return True
            
            def get_health_status(self):
                return "healthy"
        
        monitorable = MockMonitorable()
        self.assertTrue(monitorable.start_monitoring())
        self.assertTrue(monitorable.stop_monitoring())
        self.assertEqual(monitorable.get_health_status(), "healthy")
    
    def test_vpn_request_class(self):
        """Тест класса VPNRequest"""
        from datetime import datetime
        
        request = VPNRequest(
            request_id="req_123",
            timestamp=datetime.utcnow(),
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            endpoint="/api/v1/status",
            method="GET"
        )
        
        self.assertEqual(request.request_id, "req_123")
        self.assertEqual(request.ip_address, "192.168.1.1")
        self.assertEqual(request.endpoint, "/api/v1/status")
        self.assertEqual(request.method, "GET")
    
    def test_vpn_response_class(self):
        """Тест класса VPNResponse"""
        from datetime import datetime
        
        response = VPNResponse(
            request_id="req_123",
            status_code=200,
            message="Success",
            data={"result": "ok"}
        )
        
        self.assertEqual(response.request_id, "req_123")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.message, "Success")
        self.assertEqual(response.data["result"], "ok")
    
    def test_security_event_class(self):
        """Тест класса SecurityEvent"""
        from datetime import datetime
        
        event = SecurityEvent(
            event_id="evt_123",
            timestamp=datetime.utcnow(),
            event_type="login_attempt",
            severity="medium",
            source_ip="192.168.1.1",
            description="Failed login attempt"
        )
        
        self.assertEqual(event.event_id, "evt_123")
        self.assertEqual(event.event_type, "login_attempt")
        self.assertEqual(event.severity, "medium")
        self.assertEqual(event.source_ip, "192.168.1.1")

# ============================================================================
# ТЕСТЫ ФАБРИК
# ============================================================================

class TestVPNFactories(unittest.TestCase):
    """Тесты фабрик VPN"""
    
    def test_vpn_server_factory(self):
        """Тест фабрики VPN серверов"""
        factory = VPNServerFactory()
        
        # Проверяем поддерживаемые типы
        types = factory.get_supported_types()
        self.assertIn("wireguard", types)
        self.assertIn("openvpn", types)
        self.assertIn("ipsec", types)
    
    def test_vpn_client_factory(self):
        """Тест фабрики VPN клиентов"""
        factory = VPNClientFactory()
        
        # Проверяем поддерживаемые типы
        types = factory.get_supported_types()
        self.assertIn("wireguard", types)
        self.assertIn("openvpn", types)
        self.assertIn("ipsec", types)
    
    def test_security_system_factory(self):
        """Тест фабрики систем безопасности"""
        factory = SecuritySystemFactory()
        
        # Проверяем поддерживаемые типы
        types = factory.get_supported_types()
        self.assertIn("ddos_protection", types)
        self.assertIn("rate_limiter", types)
        self.assertIn("intrusion_detection", types)
    
    def test_auth_system_factory(self):
        """Тест фабрики систем аутентификации"""
        factory = AuthSystemFactory()
        
        # Проверяем поддерживаемые типы
        types = factory.get_supported_types()
        self.assertIn("two_factor_auth", types)
        self.assertIn("ldap_auth", types)
        self.assertIn("oauth_auth", types)
    
    def test_logger_factory(self):
        """Тест фабрики логгеров"""
        factory = LoggerFactory()
        
        # Проверяем поддерживаемые типы
        types = factory.get_supported_types()
        self.assertIn("audit_logger", types)
        self.assertIn("security_logger", types)
        self.assertIn("access_logger", types)
    
    def test_monitoring_system_factory(self):
        """Тест фабрики систем мониторинга"""
        factory = MonitoringSystemFactory()
        
        # Проверяем поддерживаемые типы
        types = factory.get_supported_types()
        self.assertIn("prometheus", types)
        self.assertIn("grafana", types)
        self.assertIn("elk_stack", types)
    
    def test_universal_factory(self):
        """Тест универсальной фабрики"""
        factory = UniversalVPNFactory()
        
        # Проверяем поддерживаемые компоненты
        components = factory.get_supported_components()
        self.assertIn("server", components)
        self.assertIn("client", components)
        self.assertIn("security", components)
        self.assertIn("auth", components)
        self.assertIn("logger", components)
        self.assertIn("monitoring", components)

# ============================================================================
# ТЕСТЫ DEPENDENCY INJECTION
# ============================================================================

class TestDependencyInjection(unittest.TestCase):
    """Тесты внедрения зависимостей"""
    
    def setUp(self):
        self.container = DIContainer()
    
    def test_service_registration(self):
        """Тест регистрации сервисов"""
        # Регистрируем singleton сервис
        self.container.register_singleton(Mock, Mock)
        
        # Проверяем, что сервис зарегистрирован
        self.assertTrue(self.container.is_registered(Mock))
    
    def test_service_retrieval(self):
        """Тест получения сервисов"""
        # Создаем мок-класс
        class MockService:
            def __init__(self):
                self.initialized = True
        
        # Регистрируем сервис
        self.container.register_singleton(MockService, MockService)
        
        # Получаем сервис
        service = self.container.get(MockService)
        self.assertIsInstance(service, MockService)
        self.assertTrue(service.initialized)
    
    def test_lifecycle_types(self):
        """Тест типов жизненного цикла"""
        # Тестируем singleton
        self.container.register_singleton(Mock, Mock)
        service1 = self.container.get(Mock)
        service2 = self.container.get(Mock)
        self.assertIs(service1, service2)  # Должен быть тот же объект
        
        # Очищаем контейнер
        self.container.clear()
        
        # Тестируем transient
        self.container.register_transient(Mock, Mock)
        service1 = self.container.get(Mock)
        service2 = self.container.get(Mock)
        self.assertIsNot(service1, service2)  # Должны быть разные объекты
    
    def test_scope_management(self):
        """Тест управления областями видимости"""
        scope = Scope("test_scope")
        
        # Добавляем объект в область видимости
        test_obj = {"data": "test"}
        scope.set_instance("test_key", test_obj)
        
        # Получаем объект из области видимости
        retrieved_obj = scope.get_instance("test_key")
        self.assertEqual(retrieved_obj, test_obj)
        
        # Очищаем область видимости
        scope.clear()
        self.assertIsNone(scope.get_instance("test_key"))
    
    def test_global_container(self):
        """Тест глобального контейнера"""
        # Получаем глобальный контейнер
        container1 = GlobalDIContainer.get_instance()
        container2 = GlobalDIContainer.get_instance()
        
        # Должен быть тот же объект
        self.assertIs(container1, container2)
        
        # Сбрасываем глобальный контейнер
        GlobalDIContainer.reset()
        container3 = GlobalDIContainer.get_instance()
        self.assertIsNot(container1, container3)

# ============================================================================
# ТЕСТЫ ИСКЛЮЧЕНИЙ
# ============================================================================

class TestVPNExceptions(unittest.TestCase):
    """Тесты исключений VPN"""
    
    def test_base_vpn_exception(self):
        """Тест базового исключения VPN"""
        exception = VPNException("Test error", "TEST_ERROR", {"key": "value"})
        
        self.assertEqual(exception.message, "Test error")
        self.assertEqual(exception.error_code, "TEST_ERROR")
        self.assertEqual(exception.details["key"], "value")
        self.assertIsNotNone(exception.timestamp)
    
    def test_exception_to_dict(self):
        """Тест преобразования исключения в словарь"""
        exception = VPNException("Test error", "TEST_ERROR", {"key": "value"})
        exception_dict = exception.to_dict()
        
        self.assertEqual(exception_dict["error_type"], "VPNException")
        self.assertEqual(exception_dict["error_code"], "TEST_ERROR")
        self.assertEqual(exception_dict["message"], "Test error")
        self.assertEqual(exception_dict["details"]["key"], "value")
        self.assertIn("timestamp", exception_dict)
    
    def test_connection_exceptions(self):
        """Тест исключений подключения"""
        # ConnectionTimeoutError
        timeout_error = ConnectionTimeoutError("server1", 30)
        self.assertEqual(timeout_error.server_id, "server1")
        self.assertEqual(timeout_error.timeout_seconds, 30)
        
        # ConnectionRefusedError
        refused_error = ConnectionRefusedError("server1", "Port closed")
        self.assertEqual(refused_error.server_id, "server1")
        self.assertEqual(refused_error.reason, "Port closed")
        
        # ServerUnavailableError
        unavailable_error = ServerUnavailableError("server1", "maintenance")
        self.assertEqual(unavailable_error.server_id, "server1")
        self.assertEqual(unavailable_error.status, "maintenance")
    
    def test_security_exceptions(self):
        """Тест исключений безопасности"""
        # DDoSAttackDetectedError
        ddos_error = DDoSAttackDetectedError(["192.168.1.1", "192.168.1.2"], "flood")
        self.assertEqual(len(ddos_error.source_ips), 2)
        self.assertEqual(ddos_error.attack_type, "flood")
        
        # RateLimitExceededError
        rate_error = RateLimitExceededError("user1", 100, "1m")
        self.assertEqual(rate_error.identifier, "user1")
        self.assertEqual(rate_error.limit, 100)
        self.assertEqual(rate_error.window, "1m")
        
        # IntrusionDetectedError
        intrusion_error = IntrusionDetectedError("sql_injection", "192.168.1.1")
        self.assertEqual(intrusion_error.attack_type, "sql_injection")
        self.assertEqual(intrusion_error.source_ip, "192.168.1.1")
    
    def test_exception_hierarchy(self):
        """Тест иерархии исключений"""
        from exceptions.vpn_exceptions import get_exception_hierarchy
        
        hierarchy = get_exception_hierarchy()
        
        # Проверяем, что иерархия содержит основные исключения
        self.assertIn("ConnectionTimeoutError", hierarchy)
        self.assertIn("DDoSAttackDetectedError", hierarchy)
        self.assertIn("RateLimitExceededError", hierarchy)
        
        # Проверяем наследование
        self.assertIn("VPNConnectionError", hierarchy["ConnectionTimeoutError"])
        self.assertIn("VPNSecurityError", hierarchy["DDoSAttackDetectedError"])

# ============================================================================
# ТЕСТЫ RETRY HANDLER
# ============================================================================

class TestRetryHandler(unittest.TestCase):
    """Тесты обработчика повторных попыток"""
    
    def test_retry_config(self):
        """Тест конфигурации повторных попыток"""
        config = RetryConfig(
            max_attempts=3,
            base_delay=1.0,
            max_delay=10.0,
            strategy=RetryStrategy.EXPONENTIAL
        )
        
        self.assertEqual(config.max_attempts, 3)
        self.assertEqual(config.base_delay, 1.0)
        self.assertEqual(config.max_delay, 10.0)
        self.assertEqual(config.strategy, RetryStrategy.EXPONENTIAL)
    
    def test_delay_calculation(self):
        """Тест расчета задержки"""
        config = RetryConfig(
            base_delay=1.0,
            max_delay=10.0,
            strategy=RetryStrategy.EXPONENTIAL,
            backoff_multiplier=2.0
        )
        
        handler = RetryHandler(config)
        
        # Тестируем экспоненциальную задержку
        delay1 = handler.calculate_delay(1)
        delay2 = handler.calculate_delay(2)
        delay3 = handler.calculate_delay(3)
        
        self.assertEqual(delay1, 1.0)  # base_delay
        self.assertEqual(delay2, 2.0)  # base_delay * 2^1
        self.assertEqual(delay3, 4.0)  # base_delay * 2^2
    
    def test_retry_condition_check(self):
        """Тест проверки условия повторной попытки"""
        config = RetryConfig(
            max_attempts=3,
            condition=RetryCondition.ON_EXCEPTION
        )
        
        handler = RetryHandler(config)
        
        # Тест с исключением
        self.assertTrue(handler.should_retry(exception=Exception("test"), attempt=1))
        
        # Тест без исключения
        self.assertFalse(handler.should_retry(exception=None, attempt=1))
        
        # Тест превышения максимального количества попыток
        self.assertFalse(handler.should_retry(exception=Exception("test"), attempt=3))
    
    def test_circuit_breaker(self):
        """Тест Circuit Breaker"""
        breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=60.0,
            expected_exception=Exception
        )
        
        # Проверяем начальное состояние
        self.assertTrue(breaker.can_execute())
        
        # Симулируем сбои
        for i in range(3):
            breaker.on_failure(Exception("test"))
        
        # Circuit breaker должен быть открыт
        self.assertFalse(breaker.can_execute())
        
        # Симулируем успех
        breaker.on_success()
        self.assertTrue(breaker.can_execute())

# ============================================================================
# ТЕСТЫ GRACEFUL DEGRADATION
# ============================================================================

class TestGracefulDegradation(unittest.TestCase):
    """Тесты graceful degradation"""
    
    def setUp(self):
        self.manager = GracefulDegradationManager()
    
    def test_service_registration(self):
        """Тест регистрации сервисов"""
        config = ServiceConfig(
            name="test_service",
            priority=1,
            fallback_function=lambda: {"status": "fallback"}
        )
        
        self.manager.register_service(config)
        
        self.assertIn("test_service", self.manager.services)
        self.assertEqual(self.manager.get_service_status("test_service"), ServiceStatus.HEALTHY)
    
    def test_degradation_levels(self):
        """Тест уровней деградации"""
        self.assertEqual(self.manager.get_current_level(), DegradationLevel.FULL)
        
        # Изменяем уровень деградации
        self.manager.current_level = DegradationLevel.REDUCED
        self.assertEqual(self.manager.get_current_level(), DegradationLevel.REDUCED)
    
    def test_service_availability(self):
        """Тест доступности сервисов"""
        config = ServiceConfig(
            name="test_service",
            priority=1,
            required_for_levels=[DegradationLevel.FULL]
        )
        
        self.manager.register_service(config)
        
        # Сервис должен быть доступен при полной функциональности
        self.assertTrue(self.manager.can_use_service("test_service"))
        
        # При сниженной функциональности сервис не должен быть доступен
        self.manager.current_level = DegradationLevel.REDUCED
        self.assertFalse(self.manager.can_use_service("test_service"))
    
    def test_degradation_rule(self):
        """Тест правил деградации"""
        rule = DegradationRule(
            condition=lambda metrics: metrics.get("test_metric", 0) > 100,
            target_level=DegradationLevel.REDUCED,
            message="Test degradation rule"
        )
        
        self.manager.add_degradation_rule(rule)
        
        # Проверяем, что правило добавлено
        self.assertEqual(len(self.manager.degradation_rules), 1)
        self.assertEqual(self.manager.degradation_rules[0].message, "Test degradation rule")

# ============================================================================
# ЗАПУСК ТЕСТОВ
# ============================================================================

if __name__ == "__main__":
    # Создаем test suite
    test_suite = unittest.TestSuite()
    
    # Добавляем тесты
    test_classes = [
        TestVPNConstants,
        TestVPNInterfaces,
        TestVPNFactories,
        TestDependencyInjection,
        TestVPNExceptions,
        TestRetryHandler,
        TestGracefulDegradation
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Выводим результаты
    print(f"\n{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*50}")