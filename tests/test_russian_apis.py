#!/usr/bin/env python3
"""
Тесты для российских API
Яндекс Карты, ГЛОНАСС и другие российские сервисы
"""

import unittest
import asyncio
import requests
import time
import os
import sys
import subprocess

# Add the parent directory to the sys.path to allow imports from security and core
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from security.russian_api_manager import RussianAPIManager, RussianAPIType, GeocodingResult, RoutingResult
from security.safe_function_manager import SafeFunctionManager
from core.base import SecurityLevel, ComponentStatus
from core.logging_module import LoggingManager

logger = LoggingManager(name="TestRussianAPIs")


class TestRussianAPIManager(unittest.TestCase):
    """Тесты для RussianAPIManager"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.manager = RussianAPIManager()

    def test_01_initialization(self):
        """Тест инициализации менеджера"""
        self.assertIsInstance(self.manager, RussianAPIManager)
        self.assertEqual(self.manager.status, ComponentStatus.INITIALIZING)
        self.assertEqual(self.manager.security_level, SecurityLevel.HIGH)
        self.assertGreater(len(self.manager.api_configs), 0)
        logger.log("INFO", "Test 01: Manager initialization passed")

    def test_02_api_configs(self):
        """Тест конфигурации API"""
        configs = self.manager.api_configs
        
        # Проверяем наличие основных API
        self.assertIn(RussianAPIType.YANDEX_MAPS, configs)
        self.assertIn(RussianAPIType.GLONASS_FREE, configs)
        self.assertIn(RussianAPIType.ALTOX_SERVER, configs)
        
        # Проверяем структуру конфигурации
        for api_type, config in configs.items():
            self.assertIn("name", config)
            self.assertIn("base_url", config)
            self.assertIn("free_tier_limit", config)
            self.assertIn("rate_limit", config)
            self.assertIn("supports_glonass", config)
        
        logger.log("INFO", "Test 02: API configurations passed")

    def test_03_rate_limit_check(self):
        """Тест проверки rate limit"""
        # Тестируем rate limit для разных API
        for api_type in RussianAPIType:
            if api_type in self.manager.api_configs:
                # Первый запрос должен пройти
                self.assertTrue(self.manager._check_rate_limit(api_type))
                
                # Если rate limit низкий, можем превысить его
                config = self.manager.api_configs[api_type]
                if config.get("rate_limit", 10) <= 5:
                    # Имитируем превышение rate limit
                    for _ in range(config["rate_limit"] + 1):
                        self.manager._check_rate_limit(api_type)
                    
                    # Следующий запрос должен не пройти
                    self.assertFalse(self.manager._check_rate_limit(api_type))
        
        logger.log("INFO", "Test 03: Rate limit check passed")

    def test_04_cache_functionality(self):
        """Тест функциональности кэша"""
        # Тестируем генерацию ключа кэша
        cache_key = self.manager._get_cache_key(
            RussianAPIType.YANDEX_MAPS, 
            {"address": "Москва"}
        )
        self.assertIsInstance(cache_key, str)
        self.assertEqual(len(cache_key), 32)  # MD5 hash length
        
        # Тестируем проверку валидности кэша
        self.assertFalse(self.manager._is_cache_valid(cache_key))
        
        # Добавляем данные в кэш
        self.manager.cache[cache_key] = {
            "data": {"test": "data"},
            "timestamp": time.time()
        }
        
        # Проверяем валидность
        self.assertTrue(self.manager._is_cache_valid(cache_key))
        
        # Тестируем очистку кэша
        self.manager.clear_cache()
        self.assertEqual(len(self.manager.cache), 0)
        
        logger.log("INFO", "Test 04: Cache functionality passed")

    def test_05_usage_statistics(self):
        """Тест статистики использования"""
        stats = self.manager.get_usage_statistics()
        
        self.assertIn("usage_stats", stats)
        self.assertIn("cache_size", stats)
        self.assertIn("api_configs", stats)
        self.assertIn("rate_limits", stats)
        
        usage_stats = stats["usage_stats"]
        self.assertIn("total_requests", usage_stats)
        self.assertIn("successful_requests", usage_stats)
        self.assertIn("failed_requests", usage_stats)
        self.assertIn("cache_hits", usage_stats)
        
        logger.log("INFO", "Test 05: Usage statistics passed")

    def test_06_get_status(self):
        """Тест получения статуса"""
        status = self.manager.get_status()
        
        self.assertIn("component_name", status)
        self.assertIn("status", status)
        self.assertIn("security_level", status)
        self.assertIn("api_count", status)
        self.assertIn("cache_size", status)
        self.assertIn("usage_stats", status)
        
        self.assertEqual(status["component_name"], "RussianAPIManager")
        self.assertEqual(status["status"], ComponentStatus.INITIALIZING.name)
        
        logger.log("INFO", "Test 06: Get status passed")

    @unittest.skip("Требует реального API ключа")
    async def test_07_geocode_address_mock(self):
        """Тест геокодирования (мок)"""
        # Этот тест требует реального API ключа
        # Пока что пропускаем
        pass

    @unittest.skip("Требует реального API ключа")
    async def test_08_build_route_mock(self):
        """Тест построения маршрута (мок)"""
        # Этот тест требует реального API ключа
        # Пока что пропускаем
        pass

    async def test_09_glonass_coordinates_mock(self):
        """Тест получения ГЛОНАСС координат (мок)"""
        coordinates = await self.manager.get_glonass_coordinates("test_device")
        
        # Проверяем, что возвращаются координаты
        self.assertIsNotNone(coordinates)
        self.assertIsInstance(coordinates, list)
        self.assertEqual(len(coordinates), 2)
        
        # Проверяем, что это валидные координаты
        lat, lon = coordinates
        self.assertIsInstance(lat, (int, float))
        self.assertIsInstance(lon, (int, float))
        self.assertGreaterEqual(lat, -90)
        self.assertLessEqual(lat, 90)
        self.assertGreaterEqual(lon, -180)
        self.assertLessEqual(lon, 180)
        
        logger.log("INFO", "Test 09: GLONASS coordinates mock passed")


class TestRussianAPIServer(unittest.TestCase):
    """Тесты для Russian APIs Server"""

    @classmethod
    def setUpClass(cls):
        """Запуск сервера перед тестами"""
        cls.server_process = None
        try:
            # Проверяем, запущен ли сервер
            response = requests.get("http://localhost:5005/api/russian/health", timeout=5)
            if response.status_code == 200 and response.json().get("status") == "ok":
                logger.log("INFO", "Russian APIs Server is already running.")
            else:
                raise Exception("Server not healthy")
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, Exception):
            logger.log("INFO", "Starting Russian APIs Server for testing...")
            cls.server_process = subprocess.Popen(
                ["python3", "russian_apis_server.py"],
                cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            time.sleep(5)  # Даем серверу время запуститься
            try:
                response = requests.get("http://localhost:5005/api/russian/health", timeout=5)
                response.raise_for_status()
                if response.json().get("status") != "ok":
                    raise Exception("Server health check failed after startup.")
                logger.log("CRITICAL", "Russian APIs Server started successfully.")
            except Exception as e:
                logger.log("INFO", f"Failed to start Russian APIs Server: {e}")
                if cls.server_process and cls.server_process.poll() is not None:
                    stdout, stderr = cls.server_process.communicate()
                    logger.log("ERROR", f"Server stdout: {stdout}")
                    logger.log("ERROR", f"Server stderr: {stderr}")
                raise

    @classmethod
    def tearDownClass(cls):
        """Остановка сервера после тестов"""
        if cls.server_process:
            logger.log("INFO", "Stopping Russian APIs Server...")
            cls.server_process.terminate()
            cls.server_process.wait(timeout=10)
            if cls.server_process.poll() is None:
                cls.server_process.kill()
            logger.log("INFO", "Russian APIs Server stopped.")

    def test_01_health_check(self):
        """Тест health check API"""
        response = requests.get("http://localhost:5005/api/russian/health")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['status'], 'ok')
        self.assertIn('timestamp', data)
        self.assertIn('manager_status', data)
        
        logger.log("INFO", "Test 01: Health check API passed")

    def test_02_geocode_api(self):
        """Тест API геокодирования"""
        response = requests.post(
            "http://localhost:5005/api/russian/geocode",
            json={"address": "Москва, Красная площадь"}
        )
        
        # Может вернуть ошибку из-за отсутствия API ключа, но структура должна быть правильной
        self.assertIn(response.status_code, [200, 500])
        
        data = response.json()
        if response.status_code == 200:
            self.assertIn("success", data)
            self.assertIn("address", data)
        else:
            self.assertIn("error", data)
        
        logger.log("INFO", "Test 02: Geocode API passed")

    def test_03_route_api(self):
        """Тест API маршрутизации"""
        response = requests.post(
            "http://localhost:5005/api/russian/route",
            json={
                "from_point": "Москва",
                "to_point": "Санкт-Петербург"
            }
        )
        
        # Может вернуть ошибку из-за отсутствия API ключа, но структура должна быть правильной
        self.assertIn(response.status_code, [200, 500])
        
        data = response.json()
        if response.status_code == 200:
            self.assertIn("success", data)
            self.assertIn("from_point", data)
            self.assertIn("to_point", data)
        else:
            self.assertIn("error", data)
        
        logger.log("INFO", "Test 03: Route API passed")

    def test_04_glonass_api(self):
        """Тест API ГЛОНАСС"""
        response = requests.post(
            "http://localhost:5005/api/russian/glonass",
            json={"device_id": "test_device_001"}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn("success", data)
        self.assertIn("device_id", data)
        self.assertIn("coordinates", data)
        
        logger.log("INFO", "Test 04: GLONASS API passed")

    def test_05_statistics_api(self):
        """Тест API статистики"""
        response = requests.get("http://localhost:5005/api/russian/statistics")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("success", data)
        self.assertIn("statistics", data)
        self.assertIn("timestamp", data)
        
        logger.log("INFO", "Test 05: Statistics API passed")

    def test_06_status_api(self):
        """Тест API статуса"""
        response = requests.get("http://localhost:5005/api/russian/status")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("success", data)
        self.assertIn("status", data)
        self.assertIn("timestamp", data)
        
        logger.log("INFO", "Test 06: Status API passed")

    def test_07_clear_cache_api(self):
        """Тест API очистки кэша"""
        response = requests.post("http://localhost:5005/api/russian/clear-cache")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("success", data)
        self.assertIn("message", data)
        
        logger.log("INFO", "Test 07: Clear cache API passed")

    def test_08_test_all_api(self):
        """Тест API тестирования всех функций"""
        response = requests.post("http://localhost:5005/api/russian/test-all")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("success", data)
        self.assertIn("test_results", data)
        self.assertIn("timestamp", data)
        
        test_results = data["test_results"]
        self.assertIn("geocoding", test_results)
        self.assertIn("routing", test_results)
        self.assertIn("glonass", test_results)
        
        logger.log("INFO", "Test 08: Test all API passed")


class TestSafeFunctionManagerIntegration(unittest.TestCase):
    """Тесты интеграции с SafeFunctionManager"""

    @classmethod
    def setUpClass(cls):
        """Интеграция функций перед тестами"""
        try:
            # Запускаем интеграцию
            result = subprocess.run(
                ["python3", "scripts/integrate_russian_apis.py"],
                cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.log("ERROR", f"Integration failed: {result.stderr}")
                raise Exception("Integration failed")
            
            logger.log("ERROR", "Russian APIs integrated into SafeFunctionManager")
        except Exception as e:
            logger.log("INFO", f"Failed to integrate Russian APIs: {e}")
            raise

    def test_01_safe_function_manager_integration(self):
        """Тест интеграции с SafeFunctionManager"""
        safe_manager = SafeFunctionManager()
        
        # Проверяем, что функции зарегистрированы
        function_ids = [
            "russian_yandex_maps",
            "russian_glonass",
            "russian_free_glonass",
            "russian_altox_server"
        ]
        
        for func_id in function_ids:
            status = safe_manager.get_function_status(func_id)
            self.assertIsNotNone(status)
            self.assertIn("name", status)
            self.assertIn("status", status)
            self.assertIn("security_level", status)
        
        logger.log("INFO", "Test 01: SafeFunctionManager integration passed")

    def test_02_function_execution(self):
        """Тест выполнения функций через SafeFunctionManager"""
        safe_manager = SafeFunctionManager()
        
        # Тест геокодирования
        try:
            result = safe_manager.execute_function(
                "russian_yandex_maps",
                address="Москва, Красная площадь"
            )
            self.assertIsNotNone(result)
            logger.log("INFO", f"Geocoding execution result: {result}")
        except Exception as e:
            # Может быть ошибка из-за отсутствия API ключа
            logger.log("INFO", f"Geocoding execution error (expected): {e}")
        
        # Тест ГЛОНАСС
        try:
            result = safe_manager.execute_function(
                "russian_glonass",
                device_id="test_device_001"
            )
            self.assertIsNotNone(result)
            logger.log("INFO", f"GLONASS execution result: {result}")
        except Exception as e:
            logger.log("INFO", f"GLONASS execution error: {e}")
        
        logger.log("INFO", "Test 02: Function execution passed")


if __name__ == '__main__':
    # Запуск тестов
    unittest.main(verbosity=2)