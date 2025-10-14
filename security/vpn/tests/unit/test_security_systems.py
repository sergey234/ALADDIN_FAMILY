#!/usr/bin/env python3
"""
ALADDIN VPN - Unit Tests for Security Systems
Unit тесты для систем безопасности VPN

Автор: ALADDIN Security Team
Версия: 1.0.0
Дата: 01.10.2025
"""

import unittest
import asyncio
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Импорт модулей для тестирования
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from protection.ddos_protection import DDoSProtectionSystem
from protection.rate_limiter import AdvancedRateLimiter
from protection.intrusion_detection import IntrusionDetectionSystem
from auth.two_factor_auth import TwoFactorAuth
from audit_logging.audit_logger import SecurityAuditLogger
from exceptions.vpn_exceptions import DDoSAttackDetectedError, RateLimitExceededError, IntrusionDetectedError

# ============================================================================
# БАЗОВЫЙ КЛАСС ДЛЯ ТЕСТОВ
# ============================================================================

class BaseSecurityTest(unittest.TestCase):
    """Базовый класс для тестов безопасности"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.temp_dir, "config")
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Создаем временные конфигурационные файлы
        self._create_test_configs()
    
    def tearDown(self):
        """Очистка после каждого теста"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_test_configs(self):
        """Создание тестовых конфигураций"""
        # DDoS конфигурация
        ddos_config = {
            "enabled": True,
            "max_requests_per_second": 10,
            "max_concurrent_connections": 100,
            "block_duration_minutes": 60,
            "whitelist_ips": ["127.0.0.1"],
            "blacklist_ips": []
        }
        
        with open(os.path.join(self.config_dir, "ddos_config.json"), "w") as f:
            json.dump(ddos_config, f)
        
        # Rate Limiting конфигурация
        rate_config = {
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
        }
        
        with open(os.path.join(self.config_dir, "rate_limiting.json"), "w") as f:
            json.dump(rate_config, f)
        
        # IDS конфигурация
        ids_config = {
            "enabled": True,
            "detection_rules": [
                {
                    "name": "sql_injection",
                    "pattern": r"(union|select|insert|delete|update|drop)",
                    "severity": "high"
                }
            ],
            "honeypot_endpoints": ["/admin/secret", "/api/internal"]
        }
        
        with open(os.path.join(self.config_dir, "ids_config.json"), "w") as f:
            json.dump(ids_config, f)
        
        # 2FA конфигурация
        twofa_config = {
            "enabled": True,
            "scope": "admin",
            "methods": ["totp", "sms", "email"],
            "backup_codes_count": 10
        }
        
        with open(os.path.join(self.config_dir, "2fa_config.json"), "w") as f:
            json.dump(twofa_config, f)
        
        # Audit конфигурация
        audit_config = {
            "enabled": True,
            "log_level": "INFO",
            "log_format": "json",
            "log_file": os.path.join(self.temp_dir, "audit.log"),
            "max_file_size": "10MB",
            "backup_count": 5
        }
        
        with open(os.path.join(self.config_dir, "audit_config.json"), "w") as f:
            json.dump(audit_config, f)

# ============================================================================
# ТЕСТЫ DDoS ЗАЩИТЫ
# ============================================================================

class TestDDoSProtection(BaseSecurityTest):
    """Тесты DDoS защиты"""
    
    def setUp(self):
        super().setUp()
        self.ddos_system = DDoSProtectionSystem()
        self.ddos_system.load_config(os.path.join(self.config_dir, "ddos_config.json"))
    
    def test_ddos_protection_initialization(self):
        """Тест инициализации DDoS защиты"""
        self.assertTrue(self.ddos_system.enabled)
        self.assertEqual(self.ddos_system.max_requests_per_second, 10)
        self.assertEqual(self.ddos_system.max_concurrent_connections, 100)
    
    def test_legitimate_request(self):
        """Тест легитимного запроса"""
        request_data = {
            "ip_address": "192.168.1.100",
            "endpoint": "/api/v1/status",
            "method": "GET",
            "timestamp": datetime.utcnow()
        }
        
        is_attack, reason = self.ddos_system.analyze_traffic(request_data)
        self.assertFalse(is_attack)
        self.assertIsNone(reason)
    
    def test_ddos_attack_detection(self):
        """Тест обнаружения DDoS атаки"""
        # Симулируем множественные запросы с одного IP
        for i in range(15):  # Превышаем лимит 10 запросов в секунду
            request_data = {
                "ip_address": "192.168.1.200",
                "endpoint": "/api/v1/status",
                "method": "GET",
                "timestamp": datetime.utcnow()
            }
            
            is_attack, reason = self.ddos_system.analyze_traffic(request_data)
            
            if i >= 10:  # После 10 запросов должна быть атака
                self.assertTrue(is_attack)
                self.assertIn("rate", reason.lower())
    
    def test_whitelist_ip(self):
        """Тест IP в whitelist"""
        request_data = {
            "ip_address": "127.0.0.1",  # IP в whitelist
            "endpoint": "/api/v1/status",
            "method": "GET",
            "timestamp": datetime.utcnow()
        }
        
        # Даже при превышении лимита, IP в whitelist не должен блокироваться
        for i in range(15):
            is_attack, reason = self.ddos_system.analyze_traffic(request_data)
            self.assertFalse(is_attack)
    
    def test_blacklist_ip(self):
        """Тест IP в blacklist"""
        # Добавляем IP в blacklist
        self.ddos_system.blacklist_ips.append("192.168.1.300")
        
        request_data = {
            "ip_address": "192.168.1.300",
            "endpoint": "/api/v1/status",
            "method": "GET",
            "timestamp": datetime.utcnow()
        }
        
        is_attack, reason = self.ddos_system.analyze_traffic(request_data)
        self.assertTrue(is_attack)
        self.assertIn("blacklist", reason.lower())

# ============================================================================
# ТЕСТЫ RATE LIMITING
# ============================================================================

class TestRateLimiting(BaseSecurityTest):
    """Тесты Rate Limiting"""
    
    def setUp(self):
        super().setUp()
        self.rate_limiter = AdvancedRateLimiter()
        self.rate_limiter.load_config(os.path.join(self.config_dir, "rate_limiting.json"))
    
    def test_rate_limiter_initialization(self):
        """Тест инициализации Rate Limiter"""
        self.assertTrue(self.rate_limiter.enabled)
        self.assertEqual(len(self.rate_limiter.rules), 1)
    
    def test_rate_limit_check(self):
        """Тест проверки лимита скорости"""
        identifier = "test_user"
        endpoint = "/api/v1/status"
        
        # Первые 100 запросов должны проходить
        for i in range(100):
            allowed, message, action = self.rate_limiter.check_rate_limit(identifier, endpoint)
            self.assertTrue(allowed)
        
        # 101-й запрос должен быть заблокирован
        allowed, message, action = self.rate_limiter.check_rate_limit(identifier, endpoint)
        self.assertFalse(allowed)
        self.assertEqual(action, "block")
    
    def test_different_endpoints(self):
        """Тест разных эндпоинтов"""
        identifier = "test_user"
        
        # Запросы к разным эндпоинтам не должны влиять друг на друга
        allowed1, _, _ = self.rate_limiter.check_rate_limit(identifier, "/api/v1/status")
        allowed2, _, _ = self.rate_limiter.check_rate_limit(identifier, "/api/v1/users")
        
        self.assertTrue(allowed1)
        self.assertTrue(allowed2)
    
    def test_rate_limit_reset(self):
        """Тест сброса лимита скорости"""
        identifier = "test_user"
        endpoint = "/api/v1/status"
        
        # Исчерпываем лимит
        for i in range(101):
            self.rate_limiter.check_rate_limit(identifier, endpoint)
        
        # Проверяем, что лимит исчерпан
        allowed, _, _ = self.rate_limiter.check_rate_limit(identifier, endpoint)
        self.assertFalse(allowed)
        
        # Сбрасываем лимит (симуляция)
        self.rate_limiter._reset_limits()
        
        # Проверяем, что лимит сброшен
        allowed, _, _ = self.rate_limiter.check_rate_limit(identifier, endpoint)
        self.assertTrue(allowed)

# ============================================================================
# ТЕСТЫ INTRUSION DETECTION
# ============================================================================

class TestIntrusionDetection(BaseSecurityTest):
    """Тесты обнаружения вторжений"""
    
    def setUp(self):
        super().setUp()
        self.ids_system = IntrusionDetectionSystem()
        self.ids_system.load_config(os.path.join(self.config_dir, "ids_config.json"))
    
    def test_ids_initialization(self):
        """Тест инициализации IDS"""
        self.assertTrue(self.ids_system.enabled)
        self.assertEqual(len(self.ids_system.detection_rules), 1)
        self.assertEqual(len(self.ids_system.honeypot_endpoints), 2)
    
    def test_sql_injection_detection(self):
        """Тест обнаружения SQL инъекции"""
        request_data = {
            "ip_address": "192.168.1.100",
            "endpoint": "/api/v1/users",
            "method": "POST",
            "payload": "SELECT * FROM users WHERE id = 1 UNION SELECT password FROM admin",
            "headers": {"Content-Type": "application/json"},
            "timestamp": datetime.utcnow()
        }
        
        is_intrusion, threats = self.ids_system.analyze_request(request_data)
        self.assertTrue(is_intrusion)
        self.assertGreater(len(threats), 0)
        self.assertEqual(threats[0]["type"], "sql_injection")
    
    def test_xss_detection(self):
        """Тест обнаружения XSS"""
        request_data = {
            "ip_address": "192.168.1.100",
            "endpoint": "/api/v1/comments",
            "method": "POST",
            "payload": "<script>alert('XSS')</script>",
            "headers": {"Content-Type": "application/json"},
            "timestamp": datetime.utcnow()
        }
        
        is_intrusion, threats = self.ids_system.analyze_request(request_data)
        self.assertTrue(is_intrusion)
        self.assertGreater(len(threats), 0)
    
    def test_legitimate_request(self):
        """Тест легитимного запроса"""
        request_data = {
            "ip_address": "192.168.1.100",
            "endpoint": "/api/v1/status",
            "method": "GET",
            "payload": "",
            "headers": {"Content-Type": "application/json"},
            "timestamp": datetime.utcnow()
        }
        
        is_intrusion, threats = self.ids_system.analyze_request(request_data)
        self.assertFalse(is_intrusion)
        self.assertEqual(len(threats), 0)
    
    def test_honeypot_detection(self):
        """Тест обнаружения honeypot"""
        request_data = {
            "ip_address": "192.168.1.100",
            "endpoint": "/admin/secret",  # Honeypot endpoint
            "method": "GET",
            "payload": "",
            "headers": {"Content-Type": "application/json"},
            "timestamp": datetime.utcnow()
        }
        
        is_intrusion, threats = self.ids_system.analyze_request(request_data)
        self.assertTrue(is_intrusion)
        self.assertGreater(len(threats), 0)
        self.assertEqual(threats[0]["type"], "honeypot_access")

# ============================================================================
# ТЕСТЫ TWO-FACTOR AUTHENTICATION
# ============================================================================

class TestTwoFactorAuth(BaseSecurityTest):
    """Тесты двухфакторной аутентификации"""
    
    def setUp(self):
        super().setUp()
        self.twofa = TwoFactorAuth()
        self.twofa.load_config(os.path.join(self.config_dir, "2fa_config.json"))
    
    def test_2fa_initialization(self):
        """Тест инициализации 2FA"""
        self.assertTrue(self.twofa.enabled)
        self.assertEqual(self.twofa.scope, "admin")
        self.assertIn("totp", self.twofa.methods)
    
    def test_setup_2fa(self):
        """Тест настройки 2FA"""
        user_id = "test_user"
        methods = ["totp", "sms"]
        
        result = self.twofa.setup_2fa(user_id, methods)
        
        self.assertIn("secret_key", result)
        self.assertIn("qr_code", result)
        self.assertIn("backup_codes", result)
        self.assertEqual(len(result["backup_codes"]), 10)
    
    def test_verify_totp_code(self):
        """Тест проверки TOTP кода"""
        user_id = "test_user"
        
        # Настраиваем 2FA
        setup_result = self.twofa.setup_2fa(user_id, ["totp"])
        secret_key = setup_result["secret_key"]
        
        # Генерируем валидный код
        valid_code = self.twofa._generate_totp_code(secret_key)
        
        # Проверяем код
        is_valid, message = self.twofa.verify_2fa_code(user_id, valid_code, "totp")
        self.assertTrue(is_valid)
    
    def test_verify_invalid_code(self):
        """Тест проверки неверного кода"""
        user_id = "test_user"
        
        # Настраиваем 2FA
        self.twofa.setup_2fa(user_id, ["totp"])
        
        # Проверяем неверный код
        is_valid, message = self.twofa.verify_2fa_code(user_id, "123456", "totp")
        self.assertFalse(is_valid)
        self.assertIn("invalid", message.lower())
    
    def test_backup_codes(self):
        """Тест резервных кодов"""
        user_id = "test_user"
        
        # Настраиваем 2FA
        setup_result = self.twofa.setup_2fa(user_id, ["totp"])
        backup_codes = setup_result["backup_codes"]
        
        # Используем резервный код
        is_valid, message = self.twofa.verify_2fa_code(user_id, backup_codes[0], "backup")
        self.assertTrue(is_valid)
        
        # Проверяем, что код больше не действителен
        is_valid, message = self.twofa.verify_2fa_code(user_id, backup_codes[0], "backup")
        self.assertFalse(is_valid)

# ============================================================================
# ТЕСТЫ AUDIT LOGGING
# ============================================================================

class TestAuditLogging(BaseSecurityTest):
    """Тесты аудит логирования"""
    
    def setUp(self):
        super().setUp()
        self.audit_logger = SecurityAuditLogger()
        self.audit_logger.load_config(os.path.join(self.config_dir, "audit_config.json"))
    
    def test_audit_logger_initialization(self):
        """Тест инициализации аудит логгера"""
        self.assertTrue(self.audit_logger.enabled)
        self.assertEqual(self.audit_logger.log_level, "INFO")
        self.assertEqual(self.audit_logger.log_format, "json")
    
    def test_security_event_logging(self):
        """Тест логирования событий безопасности"""
        event_id = self.audit_logger.log_security_event(
            "login_attempt",
            "User login attempt",
            user_id="test_user",
            ip_address="192.168.1.100",
            details={"success": True}
        )
        
        self.assertIsNotNone(event_id)
        self.assertIsInstance(event_id, str)
    
    def test_audit_event_retrieval(self):
        """Тест получения событий аудита"""
        # Логируем несколько событий
        self.audit_logger.log_security_event("login", "User login", user_id="user1")
        self.audit_logger.log_security_event("logout", "User logout", user_id="user1")
        self.audit_logger.log_security_event("login", "User login", user_id="user2")
        
        # Получаем события
        events = self.audit_logger.get_audit_events()
        self.assertGreaterEqual(len(events), 3)
    
    def test_audit_event_filtering(self):
        """Тест фильтрации событий аудита"""
        # Логируем события с разными типами
        self.audit_logger.log_security_event("login", "User login", user_id="user1")
        self.audit_logger.log_security_event("logout", "User logout", user_id="user1")
        self.audit_logger.log_security_event("security_violation", "Security violation", user_id="user2")
        
        # Фильтруем по типу события
        login_events = self.audit_logger.get_audit_events({"event_type": "login"})
        self.assertEqual(len(login_events), 1)
        
        # Фильтруем по пользователю
        user1_events = self.audit_logger.get_audit_events({"user_id": "user1"})
        self.assertEqual(len(user1_events), 2)

# ============================================================================
# ИНТЕГРАЦИОННЫЕ ТЕСТЫ
# ============================================================================

class TestSecurityIntegration(BaseSecurityTest):
    """Интеграционные тесты систем безопасности"""
    
    def setUp(self):
        super().setUp()
        # Здесь можно добавить инициализацию интегрированной системы безопасности
        pass
    
    def test_security_workflow(self):
        """Тест полного workflow безопасности"""
        # Этот тест будет проверять взаимодействие всех систем безопасности
        pass

# ============================================================================
# ЗАПУСК ТЕСТОВ
# ============================================================================

if __name__ == "__main__":
    # Создаем test suite
    test_suite = unittest.TestSuite()
    
    # Добавляем тесты
    test_classes = [
        TestDDoSProtection,
        TestRateLimiting,
        TestIntrusionDetection,
        TestTwoFactorAuth,
        TestAuditLogging,
        TestSecurityIntegration
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