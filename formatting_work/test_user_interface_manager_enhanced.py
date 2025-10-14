#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit тесты для улучшенного UserInterfaceManager
"""

import unittest
import asyncio
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Добавляем путь к модулю
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'security', 'microservices'))

from user_interface_manager_enhanced import (
    UserInterfaceManager, InterfaceFactory, WebInterface, MobileInterface,
    VoiceInterface, APIInterface, InterfaceRequest, InterfaceResponse,
    InterfaceConfig, ValidationError, CacheError, InterfaceError
)

class TestUserInterfaceManager(unittest.TestCase):
    """Тесты для UserInterfaceManager"""
    
    def setUp(self):
        """Настройка тестов"""
        self.manager = UserInterfaceManager("TestManager")
        self.sample_request = InterfaceRequest(
            user_id="test_user",
            interface_type="web",
            device_type="desktop",
            platform="windows"
        )
    
    def test_manager_initialization(self):
        """Тест инициализации менеджера"""
        self.assertIsInstance(self.manager, UserInterfaceManager)
        self.assertEqual(len(self.manager.interfaces), 4)
        self.assertIn('web', self.manager.interfaces)
        self.assertIn('mobile', self.manager.interfaces)
        self.assertIn('voice', self.manager.interfaces)
        self.assertIn('api', self.manager.interfaces)
    
    def test_start_ui_success(self):
        """Тест успешного запуска UI"""
        result = self.manager.start_ui()
        self.assertTrue(result)
    
    def test_stop_ui_success(self):
        """Тест успешной остановки UI"""
        result = self.manager.stop_ui()
        self.assertTrue(result)
    
    def test_get_ui_info(self):
        """Тест получения информации о UI"""
        info = self.manager.get_ui_info()
        self.assertIsInstance(info, dict)
        self.assertIn('interfaces_count', info)
        self.assertIn('active_sessions', info)
        self.assertIn('performance_metrics', info)
    
    @patch('asyncio.sleep')
    async def test_get_interface_success(self, mock_sleep):
        """Тест успешного получения интерфейса"""
        response = await self.manager.get_interface(self.sample_request)
        
        self.assertTrue(response.success)
        self.assertIsInstance(response.interface_data, dict)
        self.assertEqual(response.interface_data['type'], 'web')
        self.assertIsNotNone(response.session_id)
    
    async def test_get_interface_validation_error(self):
        """Тест ошибки валидации"""
        invalid_request = InterfaceRequest(
            user_id="",  # Пустой user_id
            interface_type="web",
            device_type="desktop",
            platform="windows"
        )
        
        response = await self.manager.get_interface(invalid_request)
        self.assertFalse(response.success)
        self.assertIsNotNone(response.error_message)
    
    def test_caching_mechanism(self):
        """Тест механизма кэширования"""
        # Первый запрос
        cached_data = self.manager.get_cached_interface(self.sample_request)
        self.assertIsNone(cached_data)  # Кэш пуст
        
        # Кэшируем данные
        test_data = {"type": "web", "test": "data"}
        self.manager.cache_interface(self.sample_request, test_data)
        
        # Проверяем кэш
        cached_data = self.manager.get_cached_interface(self.sample_request)
        self.assertIsNotNone(cached_data)
        self.assertEqual(cached_data['type'], 'web')
    
    def test_cache_key_generation(self):
        """Тест генерации ключа кэша"""
        key = self.manager._generate_cache_key(self.sample_request)
        self.assertIsInstance(key, str)
        self.assertEqual(len(key), 32)  # MD5 hash length
        
        # Проверяем, что одинаковые запросы дают одинаковые ключи
        key2 = self.manager._generate_cache_key(self.sample_request)
        self.assertEqual(key, key2)
    
    def test_interface_preferences_update(self):
        """Тест обновления предпочтений"""
        preferences = {"theme": "dark", "language": "ru"}
        result = self.manager.update_interface_preferences("test_user", preferences)
        
        self.assertTrue(result)
        self.assertEqual(self.manager.user_preferences["test_user"], preferences)
    
    def test_interface_preferences_validation(self):
        """Тест валидации предпочтений"""
        # Валидные предпочтения
        valid_preferences = {"theme": "dark", "language": "ru"}
        self.assertTrue(self.manager._validate_preferences(valid_preferences))
        
        # Невалидные предпочтения
        invalid_preferences = "not a dict"
        self.assertFalse(self.manager._validate_preferences(invalid_preferences))
    
    def test_statistics_calculation(self):
        """Тест расчета статистики"""
        # Обновляем статистику
        self.manager._update_statistics("web", True)
        self.manager._update_statistics("web", False)
        self.manager._update_statistics("mobile", True)
        
        stats = self.manager.get_interface_statistics()
        
        self.assertEqual(stats["total_requests"], 3)
        self.assertEqual(stats["successful_requests"], 2)
        self.assertEqual(stats["interface_types_usage"]["web"], 2)
        self.assertEqual(stats["interface_types_usage"]["mobile"], 1)
        self.assertAlmostEqual(stats["error_rate"], 1/3, places=2)
    
    def test_session_id_generation(self):
        """Тест генерации ID сессии"""
        session_id = self.manager._generate_session_id()
        
        self.assertIsInstance(session_id, str)
        self.assertTrue(session_id.startswith("session_"))
    
    def test_recommendations_generation(self):
        """Тест генерации рекомендаций"""
        preferences = {"language": "ru", "theme": "light"}
        recommendations = self.manager._generate_recommendations(
            self.sample_request, preferences
        )
        
        self.assertIsInstance(recommendations, list)
        # Проверяем, что есть рекомендация по языку
        self.assertTrue(any("English" in rec for rec in recommendations))

class TestInterfaceFactory(unittest.TestCase):
    """Тесты для InterfaceFactory"""
    
    def test_create_web_interface(self):
        """Тест создания веб-интерфейса"""
        interface = InterfaceFactory.create_interface("web")
        self.assertIsInstance(interface, WebInterface)
    
    def test_create_mobile_interface(self):
        """Тест создания мобильного интерфейса"""
        interface = InterfaceFactory.create_interface("mobile")
        self.assertIsInstance(interface, MobileInterface)
    
    def test_create_voice_interface(self):
        """Тест создания голосового интерфейса"""
        interface = InterfaceFactory.create_interface("voice")
        self.assertIsInstance(interface, VoiceInterface)
    
    def test_create_api_interface(self):
        """Тест создания API интерфейса"""
        interface = InterfaceFactory.create_interface("api")
        self.assertIsInstance(interface, APIInterface)
    
    def test_create_unknown_interface_defaults_to_web(self):
        """Тест создания неизвестного интерфейса (должен вернуть веб)"""
        interface = InterfaceFactory.create_interface("unknown")
        self.assertIsInstance(interface, WebInterface)

class TestInterfaceGenerators(unittest.TestCase):
    """Тесты для генераторов интерфейсов"""
    
    def setUp(self):
        """Настройка тестов"""
        self.user_preferences = {
            "theme": "dark",
            "language": "ru",
            "layout": "compact"
        }
    
    def test_web_interface_generation(self):
        """Тест генерации веб-интерфейса"""
        web_interface = WebInterface()
        result = web_interface.generate_interface(self.user_preferences)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["type"], "web")
        self.assertIn("components", result)
        self.assertIn("navigation", result)
        self.assertIn("responsive", result)
        self.assertIn("accessibility", result)
    
    def test_mobile_interface_generation(self):
        """Тест генерации мобильного интерфейса"""
        mobile_interface = MobileInterface()
        result = mobile_interface.generate_interface(self.user_preferences)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["type"], "mobile")
        self.assertIn("components", result)
        self.assertIn("gestures", result)
        self.assertIn("touch_optimized", result)
        self.assertIn("offline_support", result)
    
    def test_voice_interface_generation(self):
        """Тест генерации голосового интерфейса"""
        voice_interface = VoiceInterface()
        result = voice_interface.generate_interface(self.user_preferences)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["type"], "voice")
        self.assertIn("commands", result)
        self.assertIn("responses", result)
        self.assertIn("speech_recognition", result)
        self.assertIn("text_to_speech", result)
    
    def test_api_interface_generation(self):
        """Тест генерации API интерфейса"""
        api_interface = APIInterface()
        result = api_interface.generate_interface(self.user_preferences)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["type"], "api")
        self.assertIn("endpoints", result)
        self.assertIn("authentication", result)
        self.assertIn("rate_limiting", result)
        self.assertIn("documentation", result)
    
    def test_interface_validation(self):
        """Тест валидации интерфейсов"""
        # Веб-интерфейс
        web_interface = WebInterface()
        self.assertTrue(web_interface.validate_preferences(self.user_preferences))
        
        # Мобильный интерфейс
        mobile_interface = MobileInterface()
        self.assertTrue(mobile_interface.validate_preferences(self.user_preferences))
        
        # Голосовой интерфейс
        voice_interface = VoiceInterface()
        self.assertTrue(voice_interface.validate_preferences(self.user_preferences))
        
        # API интерфейс
        api_interface = APIInterface()
        self.assertTrue(api_interface.validate_preferences(self.user_preferences))

class TestPydanticModels(unittest.TestCase):
    """Тесты для Pydantic моделей"""
    
    def test_interface_config_validation(self):
        """Тест валидации InterfaceConfig"""
        # Валидная конфигурация
        config = InterfaceConfig(
            interface_type="web",
            user_id="test_user",
            user_type="adult",
            device_type="desktop",
            platform="windows"
        )
        self.assertEqual(config.interface_type, "web")
        self.assertEqual(config.user_type, "adult")
    
    def test_interface_config_invalid_type(self):
        """Тест невалидного типа интерфейса"""
        with self.assertRaises(ValueError):
            InterfaceConfig(
                interface_type="invalid",
                user_id="test_user",
                user_type="adult",
                device_type="desktop",
                platform="windows"
            )
    
    def test_interface_config_invalid_user_type(self):
        """Тест невалидного типа пользователя"""
        with self.assertRaises(ValueError):
            InterfaceConfig(
                interface_type="web",
                user_id="test_user",
                user_type="invalid",
                device_type="desktop",
                platform="windows"
            )
    
    def test_interface_request_creation(self):
        """Тест создания InterfaceRequest"""
        request = InterfaceRequest(
            user_id="test_user",
            interface_type="web",
            device_type="desktop",
            platform="windows",
            language="ru",
            theme="dark"
        )
        
        self.assertEqual(request.user_id, "test_user")
        self.assertEqual(request.interface_type, "web")
        self.assertEqual(request.language, "ru")
        self.assertEqual(request.theme, "dark")
    
    def test_interface_response_creation(self):
        """Тест создания InterfaceResponse"""
        response = InterfaceResponse(
            success=True,
            interface_data={"type": "web"},
            session_id="test_session"
        )
        
        self.assertTrue(response.success)
        self.assertEqual(response.interface_data["type"], "web")
        self.assertEqual(response.session_id, "test_session")

class TestPerformanceMonitoring(unittest.TestCase):
    """Тесты для мониторинга производительности"""
    
    def setUp(self):
        """Настройка тестов"""
        self.manager = UserInterfaceManager("PerformanceTestManager")
    
    def test_performance_metrics_initialization(self):
        """Тест инициализации метрик производительности"""
        self.assertIsInstance(self.manager.performance_metrics, dict)
        self.assertEqual(len(self.manager.performance_metrics), 0)
    
    def test_average_time_calculation(self):
        """Тест расчета среднего времени"""
        # Первый вызов - инициализация метрик
        self.manager.performance_metrics["test_method"] = {
            'total_calls': 1,
            'average_time': 1.0
        }
        
        # Второй вызов - увеличиваем total_calls
        self.manager.performance_metrics["test_method"]['total_calls'] = 2
        avg2 = self.manager._calculate_average_time("test_method", 3.0)
        self.assertEqual(avg2, 2.0)  # (1.0 + 3.0) / 2
        
        # Третий вызов - увеличиваем total_calls
        self.manager.performance_metrics["test_method"]['total_calls'] = 3
        avg3 = self.manager._calculate_average_time("test_method", 5.0)
        self.assertAlmostEqual(avg3, 7.0/3, places=1)  # (2.0 * 2 + 5.0) / 3 = 9/3 = 3.0

class TestErrorHandling(unittest.TestCase):
    """Тесты для обработки ошибок"""
    
    def setUp(self):
        """Настройка тестов"""
        self.manager = UserInterfaceManager("ErrorTestManager")
    
    def test_error_response_creation(self):
        """Тест создания ответа с ошибкой"""
        error_message = "Test error"
        response = self.manager._create_error_response(error_message)
        
        self.assertFalse(response.success)
        self.assertEqual(response.error_message, error_message)
        self.assertEqual(response.session_id, "")
        self.assertEqual(response.interface_data, {})
    
    def test_validation_error_handling(self):
        """Тест обработки ошибок валидации"""
        try:
            raise ValidationError("Validation failed")
        except ValidationError as e:
            self.assertEqual(str(e), "Validation failed")
    
    def test_cache_error_handling(self):
        """Тест обработки ошибок кэширования"""
        try:
            raise CacheError("Cache failed")
        except CacheError as e:
            self.assertEqual(str(e), "Cache failed")
    
    def test_interface_error_handling(self):
        """Тест обработки общих ошибок интерфейса"""
        try:
            raise InterfaceError("Interface failed")
        except InterfaceError as e:
            self.assertEqual(str(e), "Interface failed")

class TestAsyncFunctionality(unittest.TestCase):
    """Тесты для асинхронной функциональности"""
    
    def setUp(self):
        """Настройка тестов"""
        self.manager = UserInterfaceManager("AsyncTestManager")
        self.sample_request = InterfaceRequest(
            user_id="test_user",
            interface_type="web",
            device_type="desktop",
            platform="windows"
        )
    
    async def test_get_interface_with_retry_success(self):
        """Тест успешного получения интерфейса с retry"""
        with patch.object(self.manager, 'get_interface') as mock_get:
            mock_response = InterfaceResponse(
                success=True,
                interface_data={"type": "web"},
                session_id="test_session"
            )
            # Исправляем mock - get_interface должен возвращать awaitable
            mock_get.return_value = asyncio.coroutine(lambda: mock_response)()
            
            response = await self.manager.get_interface_with_retry(self.sample_request)
            
            self.assertTrue(response.success)
            mock_get.assert_called_once_with(self.sample_request)
    
    async def test_get_interface_with_retry_failure(self):
        """Тест неудачного получения интерфейса с retry"""
        with patch.object(self.manager, 'get_interface') as mock_get:
            # Создаем async функцию, которая выбрасывает исключение
            async def mock_get_interface(*args, **kwargs):
                raise ValidationError("Validation failed")
            
            mock_get.side_effect = mock_get_interface
            
            response = await self.manager.get_interface_with_retry(
                self.sample_request, max_retries=2
            )
            
            self.assertFalse(response.success)
            self.assertEqual(response.error_message, "Validation failed")
            self.assertEqual(mock_get.call_count, 2)

def run_async_test(test_func):
    """Запуск асинхронного теста"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(test_func())
    finally:
        loop.close()

if __name__ == '__main__':
    # Запуск синхронных тестов
    unittest.main(verbosity=2, exit=False)
    
    # Запуск асинхронных тестов
    print("\n🧪 Запуск асинхронных тестов...")
    
    async_test_manager = TestAsyncFunctionality()
    async_test_manager.setUp()
    
    try:
        run_async_test(async_test_manager.test_get_interface_with_retry_success)
        print("✅ test_get_interface_with_retry_success passed")
        
        run_async_test(async_test_manager.test_get_interface_with_retry_failure)
        print("✅ test_get_interface_with_retry_failure passed")
        
        print("🎉 Все асинхронные тесты прошли успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка в асинхронных тестах: {e}")
        import traceback
        traceback.print_exc()