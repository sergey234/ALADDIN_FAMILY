#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit тесты для messenger_bots_integration_test.py
Тестирование всех компонентов интеграционного тестирования
"""

import unittest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
import sys
import os

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from security.bots.messenger_bots_integration_test import MessengerBotsIntegrationTest


class TestMessengerBotsIntegrationTest(unittest.TestCase):
    """Тесты для класса MessengerBotsIntegrationTest"""

    def setUp(self) -> None:
        """Настройка тестового окружения"""
        self.test_instance = MessengerBotsIntegrationTest()

    def test_init(self) -> None:
        """Тест инициализации класса"""
        self.assertIsInstance(self.test_instance.bots, dict)
        self.assertIsInstance(self.test_instance.test_results, dict)
        self.assertIsInstance(self.test_instance.performance_metrics, dict)
        self.assertIsNone(self.test_instance.start_time)
        self.assertIsNone(self.test_instance.end_time)

    @patch('security.bots.messenger_bots_integration_test.WhatsAppSecurityBot')
    @patch('security.bots.messenger_bots_integration_test.TelegramSecurityBot')
    @patch('security.bots.messenger_bots_integration_test.InstagramSecurityBot')
    @patch('security.bots.messenger_bots_integration_test.MaxMessengerSecurityBot')
    @patch('security.bots.messenger_bots_integration_test.AnalyticsBot')
    @patch('security.bots.messenger_bots_integration_test.WebsiteNavigationBot')
    async def test_setup_bots(self, mock_website, mock_analytics, 
                             mock_max, mock_instagram, mock_telegram, mock_whatsapp) -> None:
        """Тест инициализации ботов"""
        # Настраиваем моки
        mock_whatsapp.return_value = Mock()
        mock_telegram.return_value = Mock()
        mock_instagram.return_value = Mock()
        mock_max.return_value = Mock()
        mock_analytics.return_value = Mock()
        mock_website.return_value = Mock()

        await self.test_instance.setup_bots()

        # Проверяем что все боты созданы
        self.assertEqual(len(self.test_instance.bots), 6)
        self.assertIn('whatsapp', self.test_instance.bots)
        self.assertIn('telegram', self.test_instance.bots)
        self.assertIn('instagram', self.test_instance.bots)
        self.assertIn('max_messenger', self.test_instance.bots)
        self.assertIn('analytics', self.test_instance.bots)
        self.assertIn('website_navigation', self.test_instance.bots)

    async def test_start_all_bots_success(self) -> None:
        """Тест успешного запуска всех ботов"""
        # Создаем моки ботов
        mock_bot = AsyncMock()
        mock_bot.start.return_value = True
        self.test_instance.bots = {
            'test_bot1': mock_bot,
            'test_bot2': mock_bot
        }

        result = await self.test_instance.start_all_bots()
        self.assertTrue(result)
        self.assertEqual(mock_bot.start.call_count, 2)

    async def test_start_all_bots_failure(self) -> None:
        """Тест неудачного запуска ботов"""
        # Создаем моки ботов с ошибкой
        mock_bot = AsyncMock()
        mock_bot.start.return_value = False
        self.test_instance.bots = {
            'test_bot1': mock_bot,
            'test_bot2': mock_bot
        }

        result = await self.test_instance.start_all_bots()
        self.assertFalse(result)

    async def test_start_all_bots_exception(self) -> None:
        """Тест обработки исключений при запуске ботов"""
        # Создаем мок с исключением
        mock_bot = AsyncMock()
        mock_bot.start.side_effect = Exception("Test error")
        self.test_instance.bots = {'test_bot': mock_bot}

        result = await self.test_instance.start_all_bots()
        self.assertFalse(result)

    def test_generate_test_report(self) -> None:
        """Тест генерации отчета"""
        # Настраиваем тестовые данные
        self.test_instance.test_results = {
            'test1': {'status': 'success', 'error': None},
            'test2': {'status': 'success', 'error': None},
            'test3': {'status': 'error', 'error': 'Test error'}
        }

        with patch('builtins.open', unittest.mock.mock_open()) as mock_file:
            report = self.test_instance.generate_test_report()

        # Проверяем структуру отчета
        self.assertIn('test_summary', report)
        self.assertIn('test_results', report)
        self.assertIn('recommendations', report)
        
        # Проверяем статистику
        self.assertEqual(report['test_summary']['total_tests'], 3)
        self.assertEqual(report['test_summary']['successful_tests'], 2)
        self.assertEqual(report['test_summary']['failed_tests'], 1)

    def test_generate_recommendations(self) -> None:
        """Тест генерации рекомендаций"""
        # Тест с ошибками
        self.test_instance.test_results = {
            'bot1': {'status': 'error', 'error': 'Test error'},
            'bot2': {'status': 'success', 'error': None}
        }

        recommendations = self.test_instance._generate_recommendations()
        self.assertIsInstance(recommendations, list)
        self.assertTrue(len(recommendations) > 0)

        # Тест без ошибок
        self.test_instance.test_results = {
            'bot1': {'status': 'success', 'error': None},
            'bot2': {'status': 'success', 'error': None}
        }

        recommendations = self.test_instance._generate_recommendations()
        self.assertIn("Все тесты прошли успешно", recommendations[0])

    async def test_whatsapp_bot_validation(self) -> None:
        """Тест валидации WhatsApp бота"""
        # Тест с None ботом
        with self.assertRaises(ValueError):
            await self.test_instance._test_whatsapp_bot(None)

        # Тест с ботом без метода analyze_message
        mock_bot = Mock()
        with self.assertRaises(AttributeError):
            await self.test_instance._test_whatsapp_bot(mock_bot)

    async def test_whatsapp_bot_success(self) -> None:
        """Тест успешного тестирования WhatsApp бота"""
        # Создаем мок бота с нужными методами
        mock_bot = AsyncMock()
        mock_result = Mock()
        mock_result.threat_level.value = "LOW"
        mock_bot.analyze_message.return_value = mock_result
        mock_bot.get_security_report.return_value = {'total_messages': 10}

        # Должно пройти без исключений
        await self.test_instance._test_whatsapp_bot(mock_bot)
        
        # Проверяем что методы были вызваны
        mock_bot.analyze_message.assert_called_once()
        mock_bot.get_security_report.assert_called_once()

    def test_type_hints(self) -> None:
        """Тест корректности type hints"""
        import inspect
        
        # Проверяем что у методов есть аннотации типов
        methods_to_check = [
            'setup_bots', 'start_all_bots', 'test_individual_functionality',
            'generate_test_report', '_generate_recommendations'
        ]
        
        for method_name in methods_to_check:
            method = getattr(self.test_instance, method_name)
            sig = inspect.signature(method)
            
            # Проверяем что есть аннотация возвращаемого типа
            if sig.return_annotation == inspect.Signature.empty:
                self.fail(f"Method {method_name} missing return type annotation")


class TestMessengerIntegrationAsync(unittest.IsolatedAsyncioTestCase):
    """Асинхронные тесты для интеграционного тестирования"""

    async def asyncSetUp(self) -> None:
        """Асинхронная настройка тестового окружения"""
        self.test_instance = MessengerBotsIntegrationTest()

    async def test_full_integration_flow(self) -> None:
        """Тест полного потока интеграционного тестирования"""
        # Мокаем все зависимости
        with patch.object(self.test_instance, 'setup_bots') as mock_setup, \
             patch.object(self.test_instance, 'start_all_bots', return_value=True) as mock_start, \
             patch.object(self.test_instance, 'test_individual_functionality') as mock_test, \
             patch.object(self.test_instance, 'test_inter_bot_communication') as mock_inter, \
             patch.object(self.test_instance, 'test_performance') as mock_perf, \
             patch.object(self.test_instance, 'stop_all_bots', return_value=True) as mock_stop, \
             patch.object(self.test_instance, 'generate_test_report') as mock_report:
            
            # Настраиваем мок отчета
            mock_report.return_value = {
                'test_summary': {'success_rate': 85.0, 'duration': 10.5}
            }
            
            result = await self.test_instance.run_full_test()
            
            # Проверяем что все методы были вызваны
            mock_setup.assert_called_once()
            mock_start.assert_called_once()
            mock_test.assert_called_once()
            mock_inter.assert_called_once()
            mock_perf.assert_called_once()
            mock_stop.assert_called_once()
            mock_report.assert_called_once()
            
            # Проверяем результат
            self.assertTrue(result)

    async def test_integration_flow_with_failure(self) -> None:
        """Тест потока интеграционного тестирования с ошибкой"""
        with patch.object(self.test_instance, 'setup_bots') as mock_setup, \
             patch.object(self.test_instance, 'start_all_bots', return_value=False) as mock_start:
            
            result = await self.test_instance.run_full_test()
            
            # Проверяем что тестирование остановилось после ошибки запуска
            mock_setup.assert_called_once()
            mock_start.assert_called_once()
            self.assertFalse(result)


def run_tests() -> None:
    """Запуск всех тестов"""
    print("🧪 Запуск unit тестов для messenger_bots_integration_test...")
    
    # Создаем test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Добавляем синхронные тесты
    suite.addTests(loader.loadTestsFromTestCase(TestMessengerBotsIntegrationTest))
    
    # Добавляем асинхронные тесты
    suite.addTests(loader.loadTestsFromTestCase(TestMessengerIntegrationAsync))
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Выводим результаты
    print(f"\n📊 Результаты тестирования:")
    print(f"✅ Успешных тестов: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Неудачных тестов: {len(result.failures)}")
    print(f"🚨 Ошибок: {len(result.errors)}")
    print(f"📈 Успешность: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)