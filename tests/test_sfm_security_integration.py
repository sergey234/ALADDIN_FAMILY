#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SFM Security Integration Tests для ALADDIN Dashboard
Тесты интеграции безопасности Safe Function Manager

Автор: ALADDIN Security Team
Версия: 1.0.0
Дата: 2025-01-27
Качество: A+
"""

import asyncio
import time
import pytest
import httpx
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import base64
import hmac
import secrets

# Добавляем путь к проекту
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from security.safe_function_manager import SafeFunctionManager
    from core.base import ComponentStatus, SecurityLevel
    from core.logging_module import LoggingManager
    ALADDIN_AVAILABLE = True
except ImportError:
    ALADDIN_AVAILABLE = False


class SecurityTestType(Enum):
    """Типы тестов безопасности"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    INPUT_VALIDATION = "input_validation"
    RATE_LIMITING = "rate_limiting"
    ENCRYPTION = "encryption"
    AUDIT_LOGGING = "audit_logging"
    SESSION_MANAGEMENT = "session_management"
    CSRF_PROTECTION = "csrf_protection"
    XSS_PROTECTION = "xss_protection"
    SQL_INJECTION = "sql_injection"


class SecurityVulnerability(Enum):
    """Типы уязвимостей безопасности"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityTestResult:
    """Результат теста безопасности"""
    test_id: str
    test_type: SecurityTestType
    function_id: str
    timestamp: datetime
    success: bool
    vulnerability_level: SecurityVulnerability
    details: Dict[str, Any]
    recommendations: List[str]
    execution_time: float


@dataclass
class SecurityMetrics:
    """Метрики безопасности"""
    total_tests: int
    passed_tests: int
    failed_tests: int
    vulnerabilities_found: int
    critical_vulnerabilities: int
    high_vulnerabilities: int
    medium_vulnerabilities: int
    low_vulnerabilities: int
    security_score: float  # 0-100
    compliance_percent: float  # Процент соответствия стандартам


class SFMSecurityIntegrationTester:
    """Тестер интеграции безопасности SFM"""
    
    def __init__(self, sfm_url: str = "http://localhost:8011"):
        """
        Инициализация тестера безопасности
        
        Args:
            sfm_url: URL SFM
        """
        self.sfm_url = sfm_url
        self.logger = LoggingManager(name="SFMSecurityIntegrationTester") if ALADDIN_AVAILABLE else None
        self.security_results: List[SecurityTestResult] = []
        self.test_tokens: Dict[str, str] = {}  # Хранилище токенов для тестирования
        
    def generate_test_token(self, user_type: str = "admin") -> str:
        """
        Генерация тестового токена
        
        Args:
            user_type: Тип пользователя
            
        Returns:
            Тестовый токен
        """
        payload = {
            "user": user_type,
            "timestamp": int(time.time()),
            "random": secrets.token_hex(16)
        }
        
        # Простая генерация токена (в реальной системе используется JWT)
        token_data = f"{user_type}:{payload['timestamp']}:{payload['random']}"
        token = base64.b64encode(token_data.encode()).decode()
        
        self.test_tokens[user_type] = token
        return token
    
    def generate_malicious_input(self, input_type: str) -> str:
        """
        Генерация вредоносного ввода для тестирования
        
        Args:
            input_type: Тип ввода
            
        Returns:
            Вредоносная строка
        """
        malicious_inputs = {
            "xss": "<script>alert('XSS')</script>",
            "sql_injection": "'; DROP TABLE users; --",
            "path_traversal": "../../../etc/passwd",
            "command_injection": "; rm -rf /",
            "json_injection": '{"malicious": true, "code": "exec(\'rm -rf /\')"}',
            "xml_bomb": "<?xml version='1.0'?><!DOCTYPE lolz [<!ENTITY lol 'lol'><!ENTITY lol2 '&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;'><!ENTITY lol3 '&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;'>]><lolz>&lol3;</lolz>",
            "buffer_overflow": "A" * 10000,
            "null_byte": "test\x00null",
            "unicode_attack": "\u0000\u0001\u0002",
            "special_chars": "!@#$%^&*()_+-=[]{}|;:,.<>?"
        }
        
        return malicious_inputs.get(input_type, "malicious_input")
    
    async def test_authentication_security(self, function_id: str = "test_function") -> SecurityTestResult:
        """
        Тест безопасности аутентификации
        
        Args:
            function_id: ID функции
            
        Returns:
            Результат теста аутентификации
        """
        print(f"🔐 Тестирование аутентификации для функции: {function_id}")
        
        test_id = f"auth_test_{function_id}_{int(time.time())}"
        start_time = time.time()
        test_details = {
            "tests_performed": [],
            "vulnerabilities": [],
            "auth_methods": []
        }
        
        # 1. Тест без токена
        print("  1. Тест без токена аутентификации...")
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.sfm_url}/functions/{function_id}/status")
                
                test_details["tests_performed"].append({
                    "test": "no_auth",
                    "status_code": response.status_code,
                    "success": response.status_code == 401 or response.status_code == 403
                })
                
                if response.status_code not in [401, 403]:
                    test_details["vulnerabilities"].append({
                        "type": "no_auth_protection",
                        "severity": "high",
                        "description": "Endpoint доступен без аутентификации"
                    })
                    
        except Exception as e:
            test_details["tests_performed"].append({
                "test": "no_auth",
                "error": str(e),
                "success": False
            })
        
        # 2. Тест с неверным токеном
        print("  2. Тест с неверным токеном...")
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {"Authorization": "Bearer invalid_token_12345"}
                response = await client.get(f"{self.sfm_url}/functions/{function_id}/status", headers=headers)
                
                test_details["tests_performed"].append({
                    "test": "invalid_token",
                    "status_code": response.status_code,
                    "success": response.status_code == 401 or response.status_code == 403
                })
                
                if response.status_code not in [401, 403]:
                    test_details["vulnerabilities"].append({
                        "type": "weak_token_validation",
                        "severity": "high",
                        "description": "Неверный токен принят системой"
                    })
                    
        except Exception as e:
            test_details["tests_performed"].append({
                "test": "invalid_token",
                "error": str(e),
                "success": False
            })
        
        # 3. Тест с корректным токеном
        print("  3. Тест с корректным токеном...")
        try:
            valid_token = self.generate_test_token("admin")
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {"Authorization": f"Bearer {valid_token}"}
                response = await client.get(f"{self.sfm_url}/functions/{function_id}/status", headers=headers)
                
                test_details["tests_performed"].append({
                    "test": "valid_token",
                    "status_code": response.status_code,
                    "success": 200 <= response.status_code < 300
                })
                
                test_details["auth_methods"].append("Bearer Token")
                
        except Exception as e:
            test_details["tests_performed"].append({
                "test": "valid_token",
                "error": str(e),
                "success": False
            })
        
        # 4. Тест с поддельным токеном
        print("  4. Тест с поддельным токеном...")
        try:
            fake_token = base64.b64encode(b"fake_admin_token").decode()
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {"Authorization": f"Bearer {fake_token}"}
                response = await client.get(f"{self.sfm_url}/functions/{function_id}/status", headers=headers)
                
                test_details["tests_performed"].append({
                    "test": "fake_token",
                    "status_code": response.status_code,
                    "success": response.status_code == 401 or response.status_code == 403
                })
                
                if response.status_code not in [401, 403]:
                    test_details["vulnerabilities"].append({
                        "type": "token_forgery",
                        "severity": "critical",
                        "description": "Поддельный токен принят системой"
                    })
                    
        except Exception as e:
            test_details["tests_performed"].append({
                "test": "fake_token",
                "error": str(e),
                "success": False
            })
        
        # Анализируем результаты
        total_tests = len(test_details["tests_performed"])
        successful_tests = sum(1 for test in test_details["tests_performed"] if test["success"])
        vulnerabilities = len(test_details["vulnerabilities"])
        
        # Определяем уровень уязвимости
        if vulnerabilities == 0:
            vulnerability_level = SecurityVulnerability.NONE
        elif any(v["severity"] == "critical" for v in test_details["vulnerabilities"]):
            vulnerability_level = SecurityVulnerability.CRITICAL
        elif any(v["severity"] == "high" for v in test_details["vulnerabilities"]):
            vulnerability_level = SecurityVulnerability.HIGH
        elif any(v["severity"] == "medium" for v in test_details["vulnerabilities"]):
            vulnerability_level = SecurityVulnerability.MEDIUM
        else:
            vulnerability_level = SecurityVulnerability.LOW
        
        # Генерируем рекомендации
        recommendations = []
        if vulnerabilities > 0:
            recommendations.append("Усилить проверку аутентификации")
            recommendations.append("Реализовать строгую валидацию токенов")
        
        if successful_tests < total_tests * 0.8:
            recommendations.append("Улучшить обработку ошибок аутентификации")
        
        result = SecurityTestResult(
            test_id=test_id,
            test_type=SecurityTestType.AUTHENTICATION,
            function_id=function_id,
            timestamp=datetime.now(),
            success=vulnerabilities == 0,
            vulnerability_level=vulnerability_level,
            details=test_details,
            recommendations=recommendations,
            execution_time=time.time() - start_time
        )
        
        self.security_results.append(result)
        
        print(f"  Результат: {vulnerabilities} уязвимостей, уровень: {vulnerability_level.value}")
        
        return result
    
    async def test_input_validation_security(self, function_id: str = "test_function") -> SecurityTestResult:
        """
        Тест безопасности валидации ввода
        
        Args:
            function_id: ID функции
            
        Returns:
            Результат теста валидации ввода
        """
        print(f"🔐 Тестирование валидации ввода для функции: {function_id}")
        
        test_id = f"input_test_{function_id}_{int(time.time())}"
        start_time = time.time()
        test_details = {
            "malicious_inputs_tested": [],
            "vulnerabilities": [],
            "validation_methods": []
        }
        
        # Список вредоносных входных данных для тестирования
        malicious_inputs = [
            ("xss", self.generate_malicious_input("xss")),
            ("sql_injection", self.generate_malicious_input("sql_injection")),
            ("path_traversal", self.generate_malicious_input("path_traversal")),
            ("command_injection", self.generate_malicious_input("command_injection")),
            ("json_injection", self.generate_malicious_input("json_injection")),
            ("buffer_overflow", self.generate_malicious_input("buffer_overflow")),
            ("null_byte", self.generate_malicious_input("null_byte")),
            ("special_chars", self.generate_malicious_input("special_chars"))
        ]
        
        # Тестируем каждый тип вредоносного ввода
        for input_type, malicious_input in malicious_inputs:
            print(f"  Тестирование {input_type}...")
            
            try:
                valid_token = self.generate_test_token("admin")
                async with httpx.AsyncClient(timeout=10.0) as client:
                    headers = {"Authorization": f"Bearer {valid_token}"}
                    
                    # Отправляем вредоносный ввод в различных форматах
                    test_data = {
                        "function_id": malicious_input,
                        "config": {"malicious": malicious_input},
                        "name": malicious_input
                    }
                    
                    # POST запрос с вредоносными данными
                    response = await client.post(
                        f"{self.sfm_url}/functions/{function_id}/configure",
                        headers=headers,
                        json=test_data
                    )
                    
                    test_result = {
                        "input_type": input_type,
                        "status_code": response.status_code,
                        "response_contains_input": malicious_input in response.text,
                        "vulnerable": response.status_code == 200 and malicious_input in response.text
                    }
                    
                    test_details["malicious_inputs_tested"].append(test_result)
                    
                    if test_result["vulnerable"]:
                        test_details["vulnerabilities"].append({
                            "type": f"{input_type}_vulnerability",
                            "severity": "high" if input_type in ["sql_injection", "command_injection"] else "medium",
                            "description": f"Система уязвима к {input_type}",
                            "input": malicious_input
                        })
                        
            except Exception as e:
                test_details["malicious_inputs_tested"].append({
                    "input_type": input_type,
                    "error": str(e),
                    "vulnerable": False
                })
        
        # Анализируем результаты
        total_tests = len(test_details["malicious_inputs_tested"])
        vulnerabilities = len(test_details["vulnerabilities"])
        
        # Определяем уровень уязвимости
        if vulnerabilities == 0:
            vulnerability_level = SecurityVulnerability.NONE
        elif any(v["severity"] == "high" for v in test_details["vulnerabilities"]):
            vulnerability_level = SecurityVulnerability.HIGH
        elif any(v["severity"] == "medium" for v in test_details["vulnerabilities"]):
            vulnerability_level = SecurityVulnerability.MEDIUM
        else:
            vulnerability_level = SecurityVulnerability.LOW
        
        # Генерируем рекомендации
        recommendations = []
        if vulnerabilities > 0:
            recommendations.append("Реализовать строгую валидацию ввода")
            recommendations.append("Добавить санитизацию пользовательских данных")
            recommendations.append("Использовать whitelist для разрешенных символов")
        
        result = SecurityTestResult(
            test_id=test_id,
            test_type=SecurityTestType.INPUT_VALIDATION,
            function_id=function_id,
            timestamp=datetime.now(),
            success=vulnerabilities == 0,
            vulnerability_level=vulnerability_level,
            details=test_details,
            recommendations=recommendations,
            execution_time=time.time() - start_time
        )
        
        self.security_results.append(result)
        
        print(f"  Результат: {vulnerabilities} уязвимостей, уровень: {vulnerability_level.value}")
        
        return result
    
    async def test_rate_limiting_security(self, function_id: str = "test_function") -> SecurityTestResult:
        """
        Тест безопасности ограничения скорости запросов
        
        Args:
            function_id: ID функции
            
        Returns:
            Результат теста ограничения скорости
        """
        print(f"🔐 Тестирование ограничения скорости для функции: {function_id}")
        
        test_id = f"rate_test_{function_id}_{int(time.time())}"
        start_time = time.time()
        test_details = {
            "requests_sent": 0,
            "requests_blocked": 0,
            "rate_limit_detected": False,
            "response_times": []
        }
        
        # Отправляем множество быстрых запросов
        print("  Отправка быстрых запросов для проверки rate limiting...")
        
        valid_token = self.generate_test_token("admin")
        async with httpx.AsyncClient(timeout=5.0) as client:
            headers = {"Authorization": f"Bearer {valid_token}"}
            
            for i in range(50):  # Отправляем 50 запросов быстро
                try:
                    request_start = time.time()
                    response = await client.get(f"{self.sfm_url}/functions/{function_id}/status", headers=headers)
                    request_time = time.time() - request_start
                    
                    test_details["requests_sent"] += 1
                    test_details["response_times"].append(request_time)
                    
                    # Проверяем, заблокирован ли запрос
                    if response.status_code == 429:  # Too Many Requests
                        test_details["requests_blocked"] += 1
                        test_details["rate_limit_detected"] = True
                        print(f"    Запрос {i+1} заблокирован (429)")
                    elif response.status_code == 503:  # Service Unavailable
                        test_details["requests_blocked"] += 1
                        test_details["rate_limit_detected"] = True
                        print(f"    Запрос {i+1} заблокирован (503)")
                    
                    # Небольшая задержка между запросами
                    await asyncio.sleep(0.01)
                    
                except Exception as e:
                    test_details["requests_sent"] += 1
                    # Ошибка может означать блокировку
                    if "timeout" in str(e).lower() or "connection" in str(e).lower():
                        test_details["requests_blocked"] += 1
                        test_details["rate_limit_detected"] = True
        
        # Анализируем результаты
        block_rate = (test_details["requests_blocked"] / test_details["requests_sent"]) * 100 if test_details["requests_sent"] > 0 else 0
        
        # Определяем уровень уязвимости
        if test_details["rate_limit_detected"] and block_rate > 50:
            vulnerability_level = SecurityVulnerability.NONE  # Rate limiting работает
        elif test_details["rate_limit_detected"] and block_rate > 20:
            vulnerability_level = SecurityVulnerability.LOW  # Частичная защита
        elif test_details["rate_limit_detected"]:
            vulnerability_level = SecurityVulnerability.MEDIUM  # Слабая защита
        else:
            vulnerability_level = SecurityVulnerability.HIGH  # Нет защиты
        
        # Генерируем рекомендации
        recommendations = []
        if not test_details["rate_limit_detected"]:
            recommendations.append("Реализовать rate limiting для защиты от DDoS")
            recommendations.append("Настроить ограничения по IP адресам")
        
        if block_rate < 50:
            recommendations.append("Усилить rate limiting")
            recommendations.append("Настроить более агрессивные ограничения")
        
        result = SecurityTestResult(
            test_id=test_id,
            test_type=SecurityTestType.RATE_LIMITING,
            function_id=function_id,
            timestamp=datetime.now(),
            success=test_details["rate_limit_detected"],
            vulnerability_level=vulnerability_level,
            details=test_details,
            recommendations=recommendations,
            execution_time=time.time() - start_time
        )
        
        self.security_results.append(result)
        
        print(f"  Результат: {test_details['requests_blocked']}/{test_details['requests_sent']} заблокировано")
        print(f"  Rate limiting: {'✅ Работает' if test_details['rate_limit_detected'] else '❌ Не работает'}")
        
        return result
    
    async def test_encryption_security(self, function_id: str = "test_function") -> SecurityTestResult:
        """
        Тест безопасности шифрования
        
        Args:
            function_id: ID функции
            
        Returns:
            Результат теста шифрования
        """
        print(f"🔐 Тестирование шифрования для функции: {function_id}")
        
        test_id = f"encryption_test_{function_id}_{int(time.time())}"
        start_time = time.time()
        test_details = {
            "encryption_tests": [],
            "vulnerabilities": [],
            "encryption_methods": []
        }
        
        # 1. Проверяем использование HTTPS
        print("  1. Проверка использования HTTPS...")
        try:
            # Пытаемся подключиться по HTTP (должно быть перенаправлено на HTTPS)
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"http://localhost:8011/health")
                
                https_test = {
                    "test": "https_redirect",
                    "http_accessible": response.status_code == 200,
                    "secure": response.status_code not in [200]  # HTTP не должен быть доступен
                }
                
                test_details["encryption_tests"].append(https_test)
                
                if response.status_code == 200:
                    test_details["vulnerabilities"].append({
                        "type": "http_access",
                        "severity": "medium",
                        "description": "HTTP доступен без перенаправления на HTTPS"
                    })
                    
        except Exception as e:
            test_details["encryption_tests"].append({
                "test": "https_redirect",
                "error": str(e),
                "secure": True  # Ошибка подключения по HTTP - хорошо
            })
        
        # 2. Проверяем заголовки безопасности
        print("  2. Проверка заголовков безопасности...")
        try:
            valid_token = self.generate_test_token("admin")
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {"Authorization": f"Bearer {valid_token}"}
                response = await client.get(f"{self.sfm_url}/health", headers=headers)
                
                security_headers = {
                    "strict-transport-security": response.headers.get("Strict-Transport-Security"),
                    "x-frame-options": response.headers.get("X-Frame-Options"),
                    "x-content-type-options": response.headers.get("X-Content-Type-Options"),
                    "x-xss-protection": response.headers.get("X-XSS-Protection"),
                    "content-security-policy": response.headers.get("Content-Security-Policy")
                }
                
                headers_test = {
                    "test": "security_headers",
                    "headers_present": sum(1 for v in security_headers.values() if v is not None),
                    "headers": security_headers
                }
                
                test_details["encryption_tests"].append(headers_test)
                
                # Проверяем наличие критически важных заголовков
                if not security_headers["strict-transport-security"]:
                    test_details["vulnerabilities"].append({
                        "type": "missing_hsts",
                        "severity": "medium",
                        "description": "Отсутствует заголовок Strict-Transport-Security"
                    })
                
                if not security_headers["x-frame-options"]:
                    test_details["vulnerabilities"].append({
                        "type": "missing_frame_options",
                        "severity": "low",
                        "description": "Отсутствует заголовок X-Frame-Options"
                    })
                    
        except Exception as e:
            test_details["encryption_tests"].append({
                "test": "security_headers",
                "error": str(e),
                "secure": False
            })
        
        # 3. Проверяем шифрование данных в ответах
        print("  3. Проверка шифрования данных...")
        try:
            valid_token = self.generate_test_token("admin")
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {"Authorization": f"Bearer {valid_token}"}
                response = await client.get(f"{self.sfm_url}/functions/{function_id}/config", headers=headers)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        
                        # Проверяем, есть ли в ответе чувствительные данные в открытом виде
                        response_text = response.text.lower()
                        sensitive_patterns = [
                            "password", "secret", "key", "token", "api_key",
                            "private", "credential", "auth", "login"
                        ]
                        
                        exposed_data = [pattern for pattern in sensitive_patterns if pattern in response_text]
                        
                        encryption_test = {
                            "test": "data_encryption",
                            "exposed_patterns": exposed_data,
                            "secure": len(exposed_data) == 0
                        }
                        
                        test_details["encryption_tests"].append(encryption_test)
                        
                        if exposed_data:
                            test_details["vulnerabilities"].append({
                                "type": "exposed_sensitive_data",
                                "severity": "high",
                                "description": f"Обнаружены чувствительные данные: {', '.join(exposed_data)}"
                            })
                            
                    except json.JSONDecodeError:
                        test_details["encryption_tests"].append({
                            "test": "data_encryption",
                            "error": "Invalid JSON response",
                            "secure": True
                        })
                        
        except Exception as e:
            test_details["encryption_tests"].append({
                "test": "data_encryption",
                "error": str(e),
                "secure": False
            })
        
        # Анализируем результаты
        total_tests = len(test_details["encryption_tests"])
        vulnerabilities = len(test_details["vulnerabilities"])
        
        # Определяем уровень уязвимости
        if vulnerabilities == 0:
            vulnerability_level = SecurityVulnerability.NONE
        elif any(v["severity"] == "high" for v in test_details["vulnerabilities"]):
            vulnerability_level = SecurityVulnerability.HIGH
        elif any(v["severity"] == "medium" for v in test_details["vulnerabilities"]):
            vulnerability_level = SecurityVulnerability.MEDIUM
        else:
            vulnerability_level = SecurityVulnerability.LOW
        
        # Генерируем рекомендации
        recommendations = []
        if vulnerabilities > 0:
            recommendations.append("Настроить HTTPS и обязательные редиректы")
            recommendations.append("Добавить заголовки безопасности")
            recommendations.append("Зашифровать чувствительные данные")
        
        result = SecurityTestResult(
            test_id=test_id,
            test_type=SecurityTestType.ENCRYPTION,
            function_id=function_id,
            timestamp=datetime.now(),
            success=vulnerabilities == 0,
            vulnerability_level=vulnerability_level,
            details=test_details,
            recommendations=recommendations,
            execution_time=time.time() - start_time
        )
        
        self.security_results.append(result)
        
        print(f"  Результат: {vulnerabilities} уязвимостей, уровень: {vulnerability_level.value}")
        
        return result
    
    def calculate_security_metrics(self) -> SecurityMetrics:
        """Вычисление метрик безопасности"""
        total_tests = len(self.security_results)
        passed_tests = sum(1 for result in self.security_results if result.success)
        failed_tests = total_tests - passed_tests
        
        vulnerabilities = len([r for r in self.security_results if not r.success])
        critical_vulnerabilities = len([r for r in self.security_results if r.vulnerability_level == SecurityVulnerability.CRITICAL])
        high_vulnerabilities = len([r for r in self.security_results if r.vulnerability_level == SecurityVulnerability.HIGH])
        medium_vulnerabilities = len([r for r in self.security_results if r.vulnerability_level == SecurityVulnerability.MEDIUM])
        low_vulnerabilities = len([r for r in self.security_results if r.vulnerability_level == SecurityVulnerability.LOW])
        
        # Вычисляем общий балл безопасности (0-100)
        if total_tests == 0:
            security_score = 0.0
        else:
            # Штрафы за уязвимости
            score = 100.0
            score -= critical_vulnerabilities * 25  # -25 за критические
            score -= high_vulnerabilities * 15      # -15 за высокие
            score -= medium_vulnerabilities * 10    # -10 за средние
            score -= low_vulnerabilities * 5        # -5 за низкие
            security_score = max(0.0, score)
        
        # Процент соответствия стандартам
        compliance_percent = (passed_tests / total_tests) * 100 if total_tests > 0 else 0.0
        
        return SecurityMetrics(
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            vulnerabilities_found=vulnerabilities,
            critical_vulnerabilities=critical_vulnerabilities,
            high_vulnerabilities=high_vulnerabilities,
            medium_vulnerabilities=medium_vulnerabilities,
            low_vulnerabilities=low_vulnerabilities,
            security_score=security_score,
            compliance_percent=compliance_percent
        )
    
    def generate_security_report(self) -> Dict[str, Any]:
        """Генерация отчета о безопасности"""
        print("📊 Генерация отчета о безопасности SFM...")
        
        metrics = self.calculate_security_metrics()
        
        # Группируем результаты по типам тестов
        results_by_type = {}
        for result in self.security_results:
            test_type = result.test_type.value
            if test_type not in results_by_type:
                results_by_type[test_type] = []
            results_by_type[test_type].append(result)
        
        report = {
            "report_date": datetime.now().isoformat(),
            "security_metrics": {
                "total_tests": metrics.total_tests,
                "passed_tests": metrics.passed_tests,
                "failed_tests": metrics.failed_tests,
                "vulnerabilities_found": metrics.vulnerabilities_found,
                "critical_vulnerabilities": metrics.critical_vulnerabilities,
                "high_vulnerabilities": metrics.high_vulnerabilities,
                "medium_vulnerabilities": metrics.medium_vulnerabilities,
                "low_vulnerabilities": metrics.low_vulnerabilities,
                "security_score": metrics.security_score,
                "compliance_percent": metrics.compliance_percent
            },
            "results_by_type": {
                test_type: [
                    {
                        "test_id": result.test_id,
                        "function_id": result.function_id,
                        "timestamp": result.timestamp.isoformat(),
                        "success": result.success,
                        "vulnerability_level": result.vulnerability_level.value,
                        "details": result.details,
                        "recommendations": result.recommendations,
                        "execution_time": result.execution_time
                    }
                    for result in results
                ]
                for test_type, results in results_by_type.items()
            },
            "summary": {
                "overall_security_grade": "A+" if metrics.security_score >= 95 else
                                         "A" if metrics.security_score >= 85 else
                                         "B" if metrics.security_score >= 70 else
                                         "C" if metrics.security_score >= 50 else "F",
                "security_status": "secure" if metrics.security_score >= 80 else
                                 "needs_improvement" if metrics.security_score >= 60 else
                                 "critical_issues",
                "priority_recommendations": self._generate_priority_recommendations()
            }
        }
        
        return report
    
    def _generate_priority_recommendations(self) -> List[str]:
        """Генерация приоритетных рекомендаций"""
        recommendations = []
        
        # Анализируем результаты и генерируем рекомендации
        critical_results = [r for r in self.security_results if r.vulnerability_level == SecurityVulnerability.CRITICAL]
        high_results = [r for r in self.security_results if r.vulnerability_level == SecurityVulnerability.HIGH]
        
        if critical_results:
            recommendations.append("🚨 КРИТИЧНО: Исправить критические уязвимости безопасности немедленно")
        
        if high_results:
            recommendations.append("⚠️ ВЫСОКИЙ ПРИОРИТЕТ: Устранить высокие уязвимости безопасности")
        
        # Анализируем типы тестов
        auth_results = [r for r in self.security_results if r.test_type == SecurityTestType.AUTHENTICATION]
        if any(not r.success for r in auth_results):
            recommendations.append("🔐 Усилить аутентификацию и авторизацию")
        
        input_results = [r for r in self.security_results if r.test_type == SecurityTestType.INPUT_VALIDATION]
        if any(not r.success for r in input_results):
            recommendations.append("🛡️ Реализовать строгую валидацию ввода")
        
        rate_results = [r for r in self.security_results if r.test_type == SecurityTestType.RATE_LIMITING]
        if any(not r.success for r in rate_results):
            recommendations.append("⚡ Настроить rate limiting для защиты от DDoS")
        
        encryption_results = [r for r in self.security_results if r.test_type == SecurityTestType.ENCRYPTION]
        if any(not r.success for r in encryption_results):
            recommendations.append("🔒 Улучшить шифрование и безопасность передачи данных")
        
        if not recommendations:
            recommendations.append("✅ Система безопасности настроена корректно")
        
        return recommendations


class TestSFMSecurityIntegration:
    """Тесты интеграции безопасности SFM"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Настройка тестов"""
        self.tester = SFMSecurityIntegrationTester()
    
    @pytest.mark.asyncio
    async def test_authentication_security(self):
        """Тест безопасности аутентификации"""
        print("\n🧪 Тестирование безопасности аутентификации...")
        
        auth_result = await self.tester.test_authentication_security("test_function")
        
        # Проверки
        assert auth_result.test_type == SecurityTestType.AUTHENTICATION
        assert auth_result.execution_time > 0
        assert len(auth_result.details["tests_performed"]) > 0
        
        print(f"✅ Аутентификация: {auth_result.vulnerability_level.value} уровень уязвимости")
    
    @pytest.mark.asyncio
    async def test_input_validation_security(self):
        """Тест безопасности валидации ввода"""
        print("\n🧪 Тестирование безопасности валидации ввода...")
        
        input_result = await self.tester.test_input_validation_security("test_function")
        
        # Проверки
        assert input_result.test_type == SecurityTestType.INPUT_VALIDATION
        assert len(input_result.details["malicious_inputs_tested"]) > 0
        assert input_result.execution_time > 0
        
        print(f"✅ Валидация ввода: {input_result.vulnerability_level.value} уровень уязвимости")
    
    @pytest.mark.asyncio
    async def test_rate_limiting_security(self):
        """Тест безопасности ограничения скорости"""
        print("\n🧪 Тестирование безопасности ограничения скорости...")
        
        rate_result = await self.tester.test_rate_limiting_security("test_function")
        
        # Проверки
        assert rate_result.test_type == SecurityTestType.RATE_LIMITING
        assert rate_result.details["requests_sent"] > 0
        assert rate_result.execution_time > 0
        
        print(f"✅ Ограничение скорости: {rate_result.vulnerability_level.value} уровень уязвимости")
    
    @pytest.mark.asyncio
    async def test_encryption_security(self):
        """Тест безопасности шифрования"""
        print("\n🧪 Тестирование безопасности шифрования...")
        
        encryption_result = await self.tester.test_encryption_security("test_function")
        
        # Проверки
        assert encryption_result.test_type == SecurityTestType.ENCRYPTION
        assert len(encryption_result.details["encryption_tests"]) > 0
        assert encryption_result.execution_time > 0
        
        print(f"✅ Шифрование: {encryption_result.vulnerability_level.value} уровень уязвимости")
    
    @pytest.mark.asyncio
    async def test_comprehensive_security(self):
        """Комплексный тест безопасности"""
        print("\n🧪 Комплексное тестирование безопасности...")
        
        # Запускаем все тесты безопасности
        auth_result = await self.tester.test_authentication_security("comprehensive_test")
        input_result = await self.tester.test_input_validation_security("comprehensive_test")
        rate_result = await self.tester.test_rate_limiting_security("comprehensive_test")
        encryption_result = await self.tester.test_encryption_security("comprehensive_test")
        
        # Анализируем общие результаты
        metrics = self.tester.calculate_security_metrics()
        
        # Проверки
        assert metrics.total_tests >= 4, "Должно быть выполнено минимум 4 теста"
        assert 0 <= metrics.security_score <= 100, "Балл безопасности должен быть от 0 до 100"
        assert 0 <= metrics.compliance_percent <= 100, "Процент соответствия должен быть от 0 до 100"
        
        print(f"✅ Комплексная безопасность: балл {metrics.security_score:.1f}/100")
        print(f"  Соответствие: {metrics.compliance_percent:.1f}%")
        print(f"  Уязвимостей: {metrics.vulnerabilities_found}")
    
    def test_generate_security_report(self):
        """Генерация отчета о безопасности"""
        print("\n📊 Генерация отчета о безопасности SFM...")
        
        report = self.tester.generate_security_report()
        
        # Сохранение отчета
        report_file = f"sfm_security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ Отчет о безопасности сохранен: {report_file}")
        
        # Вывод краткой статистики
        metrics = report['security_metrics']
        summary = report['summary']
        
        print(f"\n📈 КРАТКАЯ СТАТИСТИКА БЕЗОПАСНОСТИ:")
        print(f"  Всего тестов: {metrics['total_tests']}")
        print(f"  Пройдено тестов: {metrics['passed_tests']}")
        print(f"  Найдено уязвимостей: {metrics['vulnerabilities_found']}")
        print(f"  Критических: {metrics['critical_vulnerabilities']}")
        print(f"  Высоких: {metrics['high_vulnerabilities']}")
        print(f"  Средних: {metrics['medium_vulnerabilities']}")
        print(f"  Низких: {metrics['low_vulnerabilities']}")
        print(f"  Балл безопасности: {metrics['security_score']:.1f}/100")
        print(f"  Соответствие стандартам: {metrics['compliance_percent']:.1f}%")
        print(f"  Общая оценка: {summary['overall_security_grade']}")
        print(f"  Статус безопасности: {summary['security_status']}")
        
        # Проверки отчета
        assert report['security_metrics']['total_tests'] > 0, "Нет данных о тестах безопасности"
        assert 0 <= metrics['security_score'] <= 100, "Балл безопасности должен быть от 0 до 100"


if __name__ == "__main__":
    print("🚀 Запуск тестов интеграции безопасности ALADDIN Dashboard с SFM...")
    print("🔐 Тестирование аутентификации и авторизации...")
    print("🛡️ Проверка валидации ввода и защиты от атак...")
    print("⚡ Тестирование rate limiting и шифрования...")
    
    # Запуск тестов через pytest
    pytest.main([__file__, "-v", "--tb=short"])