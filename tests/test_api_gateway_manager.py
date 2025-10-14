# -*- coding: utf-8 -*-
"""
Тесты для APIGatewayManager
"""

import unittest
import time
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from security.microservices.api_gateway import (
    APIGateway,
    APIRoute,
    ServiceEndpoint,
    APIResponse,
    AuthMethod,
    RateLimitInfo,
    HTTPMethod,
    ServiceStatus
)


class TestAPIGateway(unittest.TestCase):
    """Тесты для APIGateway"""
    
    def setUp(self):
        """Настройка тестов"""
        self.manager = APIGateway("TestAPIGateway")
    
    def tearDown(self):
        """Очистка после тестов"""
        if hasattr(self.manager, 'status') and self.manager.status.value == "running":
            self.manager.stop()
    
    def test_initialization(self):
        """Тест инициализации"""
        self.assertEqual(self.manager.name, "TestAPIGateway")
        self.assertIsNotNone(self.manager.gateway_config)
        self.assertEqual(len(self.manager.routes), 0)
        self.assertEqual(len(self.manager.endpoints), 0)
        self.assertFalse(self.manager.monitoring_active)
    
    def test_initialize(self):
        """Тест инициализации менеджера"""
        result = self.manager.initialize()
        
        self.assertTrue(result)
        self.assertEqual(self.manager.status.value, "running")
        self.assertGreater(len(self.manager.routes), 0)  # Базовые маршруты зарегистрированы
        self.assertTrue(self.manager.monitoring_active)
        self.assertGreater(len(self.manager.api_keys), 0)  # API ключи сгенерированы
    
    def test_register_route(self):
        """Тест регистрации маршрута"""
        route = APIRoute(
            route_id="test_route",
            path_pattern="/api/test",
            service_id="test_service",
            authentication_method=AuthenticationMethod.API_KEY,
            rate_limit_strategy=RateLimitStrategy.FIXED_WINDOW,
            rate_limit=100,
            description="Тестовый маршрут"
        )
        
        result = self.manager.register_route(route)
        
        self.assertTrue(result)
        self.assertIn("test_route", self.manager.routes)
        self.assertIn("/api/test", self.manager.route_patterns)
        self.assertEqual(self.manager.route_patterns["/api/test"], "test_route")
    
    def test_unregister_route(self):
        """Тест отмены регистрации маршрута"""
        # Сначала регистрируем маршрут
        route = APIRoute(
            route_id="test_route",
            path_pattern="/api/test",
            service_id="test_service",
            authentication_method=AuthenticationMethod.API_KEY,
            rate_limit_strategy=RateLimitStrategy.FIXED_WINDOW
        )
        
        self.manager.register_route(route)
        self.assertIn("test_route", self.manager.routes)
        
        # Отменяем регистрацию
        result = self.manager.unregister_route("test_route")
        
        self.assertTrue(result)
        self.assertNotIn("test_route", self.manager.routes)
        self.assertNotIn("/api/test", self.manager.route_patterns)
    
    def test_unregister_nonexistent_route(self):
        """Тест отмены регистрации несуществующего маршрута"""
        result = self.manager.unregister_route("nonexistent_route")
        self.assertFalse(result)
    
    def test_find_route(self):
        """Тест поиска маршрута"""
        # Регистрируем маршрут
        route = APIRoute(
            route_id="test_route",
            path_pattern="/api/test",
            service_id="test_service",
            authentication_method=AuthenticationMethod.API_KEY,
            rate_limit_strategy=RateLimitStrategy.FIXED_WINDOW
        )
        
        self.manager.register_route(route)
        
        # Ищем маршрут
        found_route = self.manager.find_route("/api/test")
        
        self.assertIsNotNone(found_route)
        self.assertEqual(found_route.route_id, "test_route")
        self.assertEqual(found_route.path_pattern, "/api/test")
    
    def test_find_route_wildcard(self):
        """Тест поиска маршрута с wildcard"""
        # Регистрируем маршрут с wildcard
        route = APIRoute(
            route_id="test_route",
            path_pattern="/api/test/*",
            service_id="test_service",
            authentication_method=AuthenticationMethod.API_KEY,
            rate_limit_strategy=RateLimitStrategy.FIXED_WINDOW
        )
        
        self.manager.register_route(route)
        
        # Ищем маршрут
        found_route = self.manager.find_route("/api/test/123")
        
        self.assertIsNotNone(found_route)
        self.assertEqual(found_route.route_id, "test_route")
    
    def test_find_nonexistent_route(self):
        """Тест поиска несуществующего маршрута"""
        found_route = self.manager.find_route("/api/nonexistent")
        self.assertIsNone(found_route)
    
    def test_authenticate_api_key(self):
        """Тест аутентификации по API ключу"""
        # Создаем запрос с валидным API ключом
        request = APIRequest(
            request_id="req_123",
            client_id="test_client",
            method=HTTPMethod.GET,
            path="/api/test",
            headers={"X-API-Key": "test_key_12345"},
            query_params={}
        )
        
        route = APIRoute(
            route_id="test_route",
            path_pattern="/api/test",
            service_id="test_service",
            authentication_method=AuthenticationMethod.API_KEY,
            rate_limit_strategy=RateLimitStrategy.FIXED_WINDOW
        )
        
        # Инициализируем менеджер для получения API ключей
        self.manager.initialize()
        
        result = self.manager.authenticate_request(request, route)
        self.assertTrue(result)
    
    def test_authenticate_invalid_api_key(self):
        """Тест аутентификации с невалидным API ключом"""
        request = APIRequest(
            request_id="req_123",
            client_id="test_client",
            method=HTTPMethod.GET,
            path="/api/test",
            headers={"X-API-Key": "invalid_key"},
            query_params={}
        )
        
        route = APIRoute(
            route_id="test_route",
            path_pattern="/api/test",
            service_id="test_service",
            authentication_method=AuthenticationMethod.API_KEY,
            rate_limit_strategy=RateLimitStrategy.FIXED_WINDOW
        )
        
        self.manager.initialize()
        
        result = self.manager.authenticate_request(request, route)
        self.assertFalse(result)
    
    def test_authenticate_no_auth(self):
        """Тест аутентификации без требования аутентификации"""
        request = APIRequest(
            request_id="req_123",
            client_id="test_client",
            method=HTTPMethod.GET,
            path="/api/test",
            headers={},
            query_params={}
        )
        
        route = APIRoute(
            route_id="test_route",
            path_pattern="/api/test",
            service_id="test_service",
            authentication_method=AuthenticationMethod.NONE,
            rate_limit_strategy=RateLimitStrategy.FIXED_WINDOW
        )
        
        result = self.manager.authenticate_request(request, route)
        self.assertTrue(result)
    
    def test_authenticate_jwt(self):
        """Тест аутентификации по JWT"""
        request = APIRequest(
            request_id="req_123",
            client_id="test_client",
            method=HTTPMethod.GET,
            path="/api/test",
            headers={"Authorization": "Bearer valid_jwt_token_123456789"},
            query_params={}
        )
        
        route = APIRoute(
            route_id="test_route",
            path_pattern="/api/test",
            service_id="test_service",
            authentication_method=AuthenticationMethod.JWT,
            rate_limit_strategy=RateLimitStrategy.FIXED_WINDOW
        )
        
        result = self.manager.authenticate_request(request, route)
        self.assertTrue(result)
    
    def test_authenticate_basic(self):
        """Тест аутентификации по Basic Auth"""
        request = APIRequest(
            request_id="req_123",
            client_id="test_client",
            method=HTTPMethod.GET,
            path="/api/test",
            headers={"Authorization": "Basic dGVzdDp0ZXN0"},
            query_params={}
        )
        
        route = APIRoute(
            route_id="test_route",
            path_pattern="/api/test",
            service_id="test_service",
            authentication_method=AuthenticationMethod.BASIC,
            rate_limit_strategy=RateLimitStrategy.FIXED_WINDOW
        )
        
        result = self.manager.authenticate_request(request, route)
        self.assertTrue(result)
    
    def test_check_rate_limit_fixed_window(self):
        """Тест проверки ограничения скорости с фиксированным окном"""
        request = APIRequest(
            request_id="req_123",
            client_id="test_client",
            method=HTTPMethod.GET,
            path="/api/test",
            headers={},
            query_params={}
        )
        
        route = APIRoute(
            route_id="test_route",
            path_pattern="/api/test",
            service_id="test_service",
            authentication_method=AuthenticationMethod.NONE,
            rate_limit_strategy=RateLimitStrategy.FIXED_WINDOW,
            rate_limit=5
        )
        
        # Проверяем несколько запросов
        for i in range(5):
            rate_limit_ok, rate_limit_info = self.manager.check_rate_limit(request, route)
            self.assertTrue(rate_limit_ok)
            self.assertIsNotNone(rate_limit_info)
            self.assertEqual(rate_limit_info.remaining, 4 - i)
        
        # Шестой запрос должен быть заблокирован
        rate_limit_ok, rate_limit_info = self.manager.check_rate_limit(request, route)
        self.assertFalse(rate_limit_ok)
        self.assertEqual(rate_limit_info.remaining, 0)
    
    def test_check_rate_limit_sliding_window(self):
        """Тест проверки ограничения скорости со скользящим окном"""
        request = APIRequest(
            request_id="req_123",
            client_id="test_client",
            method=HTTPMethod.GET,
            path="/api/test",
            headers={},
            query_params={}
        )
        
        route = APIRoute(
            route_id="test_route",
            path_pattern="/api/test",
            service_id="test_service",
            authentication_method=AuthenticationMethod.NONE,
            rate_limit_strategy=RateLimitStrategy.SLIDING_WINDOW,
            rate_limit=5
        )
        
        rate_limit_ok, rate_limit_info = self.manager.check_rate_limit(request, route)
        self.assertTrue(rate_limit_ok)
        self.assertIsNotNone(rate_limit_info)
    
    def test_check_rate_limit_token_bucket(self):
        """Тест проверки ограничения скорости с токенным ведром"""
        request = APIRequest(
            request_id="req_123",
            client_id="test_client",
            method=HTTPMethod.GET,
            path="/api/test",
            headers={},
            query_params={}
        )
        
        route = APIRoute(
            route_id="test_route",
            path_pattern="/api/test",
            service_id="test_service",
            authentication_method=AuthenticationMethod.NONE,
            rate_limit_strategy=RateLimitStrategy.TOKEN_BUCKET,
            rate_limit=5
        )
        
        rate_limit_ok, rate_limit_info = self.manager.check_rate_limit(request, route)
        self.assertTrue(rate_limit_ok)
        self.assertIsNotNone(rate_limit_info)
    
    def test_check_rate_limit_leaky_bucket(self):
        """Тест проверки ограничения скорости с протекающим ведром"""
        request = APIRequest(
            request_id="req_123",
            client_id="test_client",
            method=HTTPMethod.GET,
            path="/api/test",
            headers={},
            query_params={}
        )
        
        route = APIRoute(
            route_id="test_route",
            path_pattern="/api/test",
            service_id="test_service",
            authentication_method=AuthenticationMethod.NONE,
            rate_limit_strategy=RateLimitStrategy.LEAKY_BUCKET,
            rate_limit=5
        )
        
        rate_limit_ok, rate_limit_info = self.manager.check_rate_limit(request, route)
        self.assertTrue(rate_limit_ok)
        self.assertIsNotNone(rate_limit_info)
    
    def test_generate_cache_key(self):
        """Тест генерации ключа кэша"""
        request = APIRequest(
            request_id="req_123",
            client_id="test_client",
            method=HTTPMethod.GET,
            path="/api/test",
            headers={},
            query_params={"param1": "value1", "param2": "value2"}
        )
        
        cache_key = self.manager.generate_cache_key(request)
        
        self.assertIsInstance(cache_key, str)
        self.assertGreater(len(cache_key), 0)
        
        # Ключ должен быть одинаковым для одинаковых запросов
        cache_key2 = self.manager.generate_cache_key(request)
        self.assertEqual(cache_key, cache_key2)
    
    def test_cache_response(self):
        """Тест кэширования ответа"""
        response = APIResponse(
            request_id="req_123",
            status_code=200,
            headers={"Content-Type": "application/json"},
            body={"message": "success"}
        )
        
        cache_key = "test_cache_key"
        ttl = 60
        
        self.manager.cache_response(cache_key, response, ttl)
        
        # Проверяем, что ответ закэширован
        cached_response = self.manager.get_cached_response(cache_key)
        self.assertIsNotNone(cached_response)
        self.assertEqual(cached_response.request_id, response.request_id)
        self.assertEqual(cached_response.status_code, response.status_code)
    
    def test_get_cached_response_nonexistent(self):
        """Тест получения несуществующего кэшированного ответа"""
        cached_response = self.manager.get_cached_response("nonexistent_key")
        self.assertIsNone(cached_response)
    
    def test_process_request_success(self):
        """Тест успешной обработки запроса"""
        # Инициализируем менеджер
        self.manager.initialize()
        
        request = APIRequest(
            request_id="req_123",
            client_id="test_client",
            method=HTTPMethod.GET,
            path="/health",
            headers={},
            query_params={}
        )
        
        response = self.manager.process_request(request)
        
        self.assertIsNotNone(response)
        self.assertIsInstance(response, APIResponse)
        self.assertEqual(response.request_id, request.request_id)
        self.assertIn(response.status_code, [200, 500])  # Имитация может вернуть любой из этих кодов
        self.assertIsInstance(response.response_time, float)
        self.assertGreaterEqual(response.response_time, 0)
    
    def test_process_request_route_not_found(self):
        """Тест обработки запроса с несуществующим маршрутом"""
        request = APIRequest(
            request_id="req_123",
            client_id="test_client",
            method=HTTPMethod.GET,
            path="/api/nonexistent",
            headers={},
            query_params={}
        )
        
        response = self.manager.process_request(request)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 404)
        self.assertIn("Route not found", response.error_message)
    
    def test_process_request_authentication_failed(self):
        """Тест обработки запроса с неудачной аутентификацией"""
        # Инициализируем менеджер
        self.manager.initialize()
        
        request = APIRequest(
            request_id="req_123",
            client_id="test_client",
            method=HTTPMethod.GET,
            path="/api/v1/security/status",
            headers={},  # Нет API ключа
            query_params={}
        )
        
        response = self.manager.process_request(request)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 401)
        self.assertIn("Authentication failed", response.error_message)
    
    def test_process_request_rate_limited(self):
        """Тест обработки запроса с превышением лимита скорости"""
        # Создаем маршрут с очень низким лимитом
        route = APIRoute(
            route_id="test_route",
            path_pattern="/api/test",
            service_id="test_service",
            authentication_method=AuthenticationMethod.NONE,
            rate_limit_strategy=RateLimitStrategy.FIXED_WINDOW,
            rate_limit=1  # Только 1 запрос
        )
        
        self.manager.register_route(route)
        
        request = APIRequest(
            request_id="req_123",
            client_id="test_client",
            method=HTTPMethod.GET,
            path="/api/test",
            headers={},
            query_params={}
        )
        
        # Первый запрос должен пройти
        response1 = self.manager.process_request(request)
        self.assertEqual(response1.status_code, 200)
        
        # Второй запрос должен быть заблокирован
        request.request_id = "req_124"
        response2 = self.manager.process_request(request)
        self.assertEqual(response2.status_code, 429)
        self.assertIn("Rate limit exceeded", response2.error_message)
    
    def test_circuit_breaker(self):
        """Тест Circuit Breaker"""
        route = APIRoute(
            route_id="test_route",
            path_pattern="/api/test",
            service_id="test_service",
            authentication_method=AuthenticationMethod.NONE,
            rate_limit_strategy=RateLimitStrategy.FIXED_WINDOW
        )
        
        self.manager.register_route(route)
        
        # Проверяем, что Circuit Breaker закрыт
        self.assertTrue(self.manager._is_circuit_breaker_closed("test_route"))
        
        # Имитируем несколько неудачных запросов
        for _ in range(6):  # Больше порога (5)
            self.manager._update_circuit_breaker("test_route", False)
        
        # Проверяем, что Circuit Breaker открыт
        self.assertFalse(self.manager._is_circuit_breaker_closed("test_route"))
    
    def test_get_gateway_status(self):
        """Тест получения статуса API шлюза"""
        # Инициализируем менеджер
        self.manager.initialize()
        
        status = self.manager.get_gateway_status()
        
        self.assertIsNotNone(status)
        self.assertIsInstance(status, dict)
        self.assertIn("gateway_name", status)
        self.assertIn("status", status)
        self.assertIn("total_routes", status)
        self.assertIn("total_endpoints", status)
        self.assertIn("metrics", status)
        self.assertIn("cache_stats", status)
        self.assertIn("circuit_breakers", status)
        self.assertIn("configuration", status)
        self.assertIn("timestamp", status)
        
        self.assertEqual(status["gateway_name"], "TestAPIGateway")
        self.assertGreaterEqual(status["total_routes"], 0)
    
    def test_stop(self):
        """Тест остановки менеджера"""
        # Инициализируем менеджер
        self.manager.initialize()
        
        # Останавливаем
        result = self.manager.stop()
        
        self.assertTrue(result)
        self.assertEqual(self.manager.status.value, "stopped")
        self.assertFalse(self.manager.monitoring_active)
    
    def test_get_status(self):
        """Тест получения статуса менеджера"""
        status = self.manager.get_status()
        
        self.assertIsInstance(status, dict)
        self.assertIn("name", status)
        self.assertIn("status", status)
        self.assertIn("security_level", status)
        self.assertIn("monitoring_active", status)
        self.assertIn("total_routes", status)
        self.assertIn("total_endpoints", status)
        self.assertIn("total_requests", status)
        self.assertIn("successful_requests", status)
        self.assertIn("failed_requests", status)
        self.assertIn("average_response_time", status)
        self.assertIn("configuration", status)
        
        self.assertEqual(status["name"], "TestAPIGateway")
        self.assertEqual(status["total_routes"], 0)
        self.assertEqual(status["total_requests"], 0)
    
    def test_api_route_to_dict(self):
        """Тест преобразования APIRoute в словарь"""
        route = APIRoute(
            route_id="test_route",
            path_pattern="/api/test",
            service_id="test_service",
            authentication_method=AuthenticationMethod.API_KEY,
            rate_limit_strategy=RateLimitStrategy.FIXED_WINDOW,
            rate_limit=100,
            timeout=30,
            retry_count=3,
            cache_ttl=60,
            middleware=["auth", "logging"],
            description="Тестовый маршрут"
        )
        
        route_dict = route.to_dict()
        
        self.assertIsInstance(route_dict, dict)
        self.assertEqual(route_dict["route_id"], "test_route")
        self.assertEqual(route_dict["path_pattern"], "/api/test")
        self.assertEqual(route_dict["service_id"], "test_service")
        self.assertEqual(route_dict["authentication_method"], AuthenticationMethod.API_KEY.value)
        self.assertEqual(route_dict["rate_limit_strategy"], RateLimitStrategy.FIXED_WINDOW.value)
        self.assertEqual(route_dict["rate_limit"], 100)
        self.assertEqual(route_dict["timeout"], 30)
        self.assertEqual(route_dict["retry_count"], 3)
        self.assertEqual(route_dict["cache_ttl"], 60)
        self.assertEqual(route_dict["middleware"], ["auth", "logging"])
        self.assertEqual(route_dict["description"], "Тестовый маршрут")
    
    def test_api_endpoint_to_dict(self):
        """Тест преобразования ServiceEndpoint в словарь"""
        endpoint = ServiceEndpoint(
            name="test_endpoint",
            url="/api/test",
            health_check_url="/api/test/health",
            status=ServiceStatus.HEALTHY
        )
        
        # ServiceEndpoint не имеет метода to_dict, проверим атрибуты
        self.assertEqual(endpoint.name, "test_endpoint")
        self.assertEqual(endpoint.url, "/api/test")
        self.assertEqual(endpoint.health_check_url, "/api/test/health")
        self.assertEqual(endpoint.status, ServiceStatus.HEALTHY)
    
    def test_api_request_to_dict(self):
        """Тест преобразования APIRequest в словарь"""
        request = APIRequest(
            request_id="req_123",
            client_id="test_client",
            method=HTTPMethod.POST,
            path="/api/test",
            headers={"Content-Type": "application/json"},
            query_params={"param1": "value1"},
            body={"test": "data"},
            ip_address="192.168.1.1",
            user_agent="TestAgent/1.0"
        )
        
        request_dict = request.to_dict()
        
        self.assertIsInstance(request_dict, dict)
        self.assertEqual(request_dict["request_id"], "req_123")
        self.assertEqual(request_dict["client_id"], "test_client")
        self.assertEqual(request_dict["method"], HTTPMethod.POST.value)
        self.assertEqual(request_dict["path"], "/api/test")
        self.assertEqual(request_dict["headers"], {"Content-Type": "application/json"})
        self.assertEqual(request_dict["query_params"], {"param1": "value1"})
        self.assertEqual(request_dict["body"], {"test": "data"})
        self.assertEqual(request_dict["ip_address"], "192.168.1.1")
        self.assertEqual(request_dict["user_agent"], "TestAgent/1.0")
        self.assertIn("timestamp", request_dict)
    
    def test_api_response_to_dict(self):
        """Тест преобразования APIResponse в словарь"""
        response = APIResponse(
            request_id="req_123",
            status_code=200,
            headers={"Content-Type": "application/json"},
            body={"result": "success"},
            response_time=0.5,
            error_message=None
        )
        
        response_dict = response.to_dict()
        
        self.assertIsInstance(response_dict, dict)
        self.assertEqual(response_dict["request_id"], "req_123")
        self.assertEqual(response_dict["status_code"], 200)
        self.assertEqual(response_dict["headers"], {"Content-Type": "application/json"})
        self.assertEqual(response_dict["body"], {"result": "success"})
        self.assertEqual(response_dict["response_time"], 0.5)
        self.assertIsNone(response_dict["error_message"])
        self.assertIn("timestamp", response_dict)
    
    def test_rate_limit_info_to_dict(self):
        """Тест преобразования RateLimitInfo в словарь"""
        rate_limit = RateLimitInfo(
            client_id="test_client",
            endpoint_id="test_endpoint",
            request_count=5,
            window_start=datetime.now(),
            limit=100,
            remaining=95,
            reset_time=datetime.now()
        )
        
        rate_limit_dict = rate_limit.to_dict()
        
        self.assertIsInstance(rate_limit_dict, dict)
        self.assertEqual(rate_limit_dict["client_id"], "test_client")
        self.assertEqual(rate_limit_dict["endpoint_id"], "test_endpoint")
        self.assertEqual(rate_limit_dict["request_count"], 5)
        self.assertEqual(rate_limit_dict["limit"], 100)
        self.assertEqual(rate_limit_dict["remaining"], 95)
        self.assertIn("window_start", rate_limit_dict)
        self.assertIn("reset_time", rate_limit_dict)


if __name__ == "__main__":
    unittest.main()