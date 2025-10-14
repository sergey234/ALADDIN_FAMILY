#!/usr/bin/env python3
"""
Тесты для ExternalAPIManager и внешних API интеграций
"""

import unittest
import asyncio
import json
import time
from unittest.mock import patch, MagicMock
import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.managers.external_api_manager import (
    ExternalAPIManager, 
    APIType, 
    APIStatus, 
    APIEndpoint,
    APIResponse
)


class TestExternalAPIManager(unittest.TestCase):
    """Тесты для ExternalAPIManager"""
    
    def setUp(self):
        """Настройка тестов"""
        self.manager = ExternalAPIManager()
    
    def test_initialization(self):
        """Тест инициализации менеджера"""
        self.assertIsNotNone(self.manager)
        self.assertEqual(self.manager.name, "ExternalAPIManager")
        self.assertIsNotNone(self.manager.api_endpoints)
        self.assertIsNotNone(self.manager.cache)
        self.assertIsNotNone(self.manager.usage_stats)
    
    def test_api_endpoints_configuration(self):
        """Тест конфигурации API endpoints"""
        # Проверяем наличие всех необходимых API
        expected_apis = ["scumware", "otx", "apip", "reallyfreegeoip", "rapid_email", "noparam"]
        
        for api_name in expected_apis:
            self.assertIn(api_name, self.manager.api_endpoints)
            
            endpoint = self.manager.api_endpoints[api_name]
            self.assertIsInstance(endpoint, APIEndpoint)
            self.assertIsNotNone(endpoint.name)
            self.assertIsNotNone(endpoint.url)
            self.assertIsNotNone(endpoint.api_type)
            self.assertGreater(endpoint.rate_limit, 0)
    
    def test_rate_limit_initialization(self):
        """Тест инициализации rate limits"""
        for api_name in self.manager.api_endpoints:
            self.assertIn(api_name, self.manager.rate_limits)
            
            rate_data = self.manager.rate_limits[api_name]
            self.assertIn("requests_count", rate_data)
            self.assertIn("window_start", rate_data)
            self.assertIn("status", rate_data)
            self.assertEqual(rate_data["requests_count"], 0)
            self.assertEqual(rate_data["status"], APIStatus.ACTIVE)
    
    async def test_check_rate_limit(self):
        """Тест проверки rate limit"""
        # Тест с пустым rate limit
        result = await self.manager._check_rate_limit("nonexistent_api")
        self.assertTrue(result)
        
        # Тест с существующим API
        result = await self.manager._check_rate_limit("apip")
        self.assertTrue(result)
    
    async def test_make_api_request_invalid_api(self):
        """Тест запроса к несуществующему API"""
        response = await self.manager._make_api_request("nonexistent_api", {})
        
        self.assertIsInstance(response, APIResponse)
        self.assertFalse(response.success)
        self.assertIn("не найден", response.error_message)
    
    def test_get_usage_statistics(self):
        """Тест получения статистики использования"""
        stats = self.manager.get_usage_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertIn("usage_stats", stats)
        self.assertIn("rate_limits", stats)
        self.assertIn("cache_size", stats)
        self.assertIn("active_apis", stats)
        self.assertIn("timestamp", stats)
        
        usage_stats = stats["usage_stats"]
        self.assertIn("total_requests", usage_stats)
        self.assertIn("successful_requests", usage_stats)
        self.assertIn("failed_requests", usage_stats)
        self.assertIn("cache_hits", usage_stats)
    
    def test_get_api_status(self):
        """Тест получения статуса API"""
        status = self.manager.get_api_status()
        
        self.assertIsInstance(status, dict)
        
        for api_name, api_status in status.items():
            self.assertIn("name", api_status)
            self.assertIn("type", api_status)
            self.assertIn("rate_limit", api_status)
            self.assertIn("status", api_status)
            self.assertIn("requests_count", api_status)
            self.assertIn("last_request", api_status)
    
    def test_clear_cache(self):
        """Тест очистки кэша"""
        # Добавляем данные в кэш
        self.manager.cache["test_key"] = {"data": "test", "timestamp": time.time()}
        self.assertEqual(len(self.manager.cache), 1)
        
        # Очищаем кэш
        self.manager.clear_cache()
        self.assertEqual(len(self.manager.cache), 0)
    
    @patch('aiohttp.ClientSession')
    async def test_get_ip_geolocation_mock(self, mock_session):
        """Тест получения геолокации IP с моком"""
        # Настройка мока
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "country": "United States",
            "city": "Mountain View",
            "latitude": 37.386,
            "longitude": -122.0838
        }
        
        mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
        
        # Выполнение теста
        result = await self.manager.get_ip_geolocation("8.8.8.8")
        
        # Проверки
        self.assertIsInstance(result, dict)
        # Проверяем, что результат был сохранен в кэш
        cache_key = "geo_8.8.8.8"
        self.assertIn(cache_key, self.manager.cache)
    
    @patch('aiohttp.ClientSession')
    async def test_validate_email_mock(self, mock_session):
        """Тест валидации email с моком"""
        # Настройка мока
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "valid": True,
            "disposable": False,
            "role": False
        }
        
        mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
        
        # Выполнение теста
        result = await self.manager.validate_email("test@example.com")
        
        # Проверки
        self.assertIsInstance(result, dict)
        # Проверяем, что результат был сохранен в кэш
        cache_key = "email_test@example.com"
        self.assertIn(cache_key, self.manager.cache)
    
    @patch('aiohttp.ClientSession')
    async def test_check_threat_intelligence_mock(self, mock_session):
        """Тест анализа угроз с моком"""
        # Настройка мока
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "threats": [],
            "reputation": "clean"
        }
        
        mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
        
        # Выполнение теста
        result = await self.manager.check_threat_intelligence("8.8.8.8")
        
        # Проверки
        self.assertIsInstance(result, dict)
        # Проверяем, что результат был сохранен в кэш
        cache_key = "threat_ip_8.8.8.8"
        self.assertIn(cache_key, self.manager.cache)


class TestAPIResponse(unittest.TestCase):
    """Тесты для APIResponse"""
    
    def test_api_response_creation(self):
        """Тест создания APIResponse"""
        response = APIResponse(
            success=True,
            data={"test": "data"},
            status_code=200,
            response_time=0.5,
            api_name="test_api",
            timestamp=time.time()
        )
        
        self.assertTrue(response.success)
        self.assertEqual(response.data, {"test": "data"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.response_time, 0.5)
        self.assertEqual(response.api_name, "test_api")
        self.assertIsNone(response.error_message)


class TestAPIEndpoint(unittest.TestCase):
    """Тесты для APIEndpoint"""
    
    def test_api_endpoint_creation(self):
        """Тест создания APIEndpoint"""
        endpoint = APIEndpoint(
            name="Test API",
            url="https://test.api.com",
            api_type=APIType.IP_GEOLOCATION,
            rate_limit=100
        )
        
        self.assertEqual(endpoint.name, "Test API")
        self.assertEqual(endpoint.url, "https://test.api.com")
        self.assertEqual(endpoint.api_type, APIType.IP_GEOLOCATION)
        self.assertEqual(endpoint.rate_limit, 100)
        self.assertEqual(endpoint.timeout, 10)  # default value
        self.assertEqual(endpoint.retry_attempts, 3)  # default value
        self.assertFalse(endpoint.requires_auth)  # default value


class TestIntegration(unittest.TestCase):
    """Интеграционные тесты"""
    
    def setUp(self):
        """Настройка интеграционных тестов"""
        self.manager = ExternalAPIManager()
    
    def test_cache_functionality(self):
        """Тест функциональности кэша"""
        # Добавляем данные в кэш
        test_data = {"test": "value"}
        self.manager.cache["test_key"] = {
            "data": test_data,
            "timestamp": time.time()
        }
        
        # Проверяем, что данные в кэше
        self.assertIn("test_key", self.manager.cache)
        self.assertEqual(self.manager.cache["test_key"]["data"], test_data)
    
    def test_usage_statistics_tracking(self):
        """Тест отслеживания статистики использования"""
        initial_stats = self.manager.usage_stats.copy()
        
        # Симулируем использование
        self.manager.usage_stats["total_requests"] += 1
        self.manager.usage_stats["successful_requests"] += 1
        
        # Проверяем, что статистика обновилась
        self.assertEqual(
            self.manager.usage_stats["total_requests"], 
            initial_stats["total_requests"] + 1
        )
        self.assertEqual(
            self.manager.usage_stats["successful_requests"], 
            initial_stats["successful_requests"] + 1
        )


def run_async_test(coro):
    """Запуск асинхронного теста"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


class TestAsyncMethods(unittest.TestCase):
    """Тесты асинхронных методов"""
    
    def setUp(self):
        """Настройка тестов"""
        self.manager = ExternalAPIManager()
    
    def test_check_rate_limit_async(self):
        """Тест асинхронной проверки rate limit"""
        result = run_async_test(self.manager._check_rate_limit("apip"))
        self.assertTrue(result)
    
    def test_make_api_request_async(self):
        """Тест асинхронного запроса к API"""
        response = run_async_test(
            self.manager._make_api_request("nonexistent_api", {})
        )
        self.assertIsInstance(response, APIResponse)
        self.assertFalse(response.success)


if __name__ == '__main__':
    # Настройка тестового окружения
    unittest.main(verbosity=2)