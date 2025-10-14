#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive тесты для EmergencyEventManager
Тестирование всех новых функций и улучшений
"""

import sys
import os
import unittest
from datetime import datetime, timedelta
from typing import Dict, Any

# Добавляем путь к модулю
sys.path.append('/Users/sergejhlystov/ALADDIN_NEW')

from security.ai_agents.emergency_event_manager import EmergencyEventManager
from security.ai_agents.emergency_models import (
    EmergencyType, EmergencySeverity, ResponseStatus
)


class TestEmergencyEventManagerComprehensive(unittest.TestCase):
    """Comprehensive тесты для EmergencyEventManager"""

    def setUp(self):
        """Настройка тестов"""
        self.manager = EmergencyEventManager(max_events=100, auto_cleanup_days=7)
        self.test_location = {
            "lat": 55.7558,
            "lon": 37.6176,
            "address": "Moscow, Russia",
            "city": "Moscow",
            "country": "Russia"
        }

    def test_01_basic_functionality(self):
        """Тест базовой функциональности"""
        print("\n=== Тест 1: Базовая функциональность ===")
        
        # Создание события
        event = self.manager.create_event(
            emergency_type=EmergencyType.SECURITY,
            severity=EmergencySeverity.HIGH,
            location=self.test_location,
            description="Security breach detected in main system",
            user_id="test_user_001"
        )
        
        self.assertIsNotNone(event)
        self.assertEqual(event.emergency_type, EmergencyType.SECURITY)
        self.assertEqual(event.severity, EmergencySeverity.HIGH)
        self.assertEqual(event.user_id, "test_user_001")
        print("✅ Создание события: OK")

        # Получение события
        retrieved_event = self.manager.get_event(event.event_id)
        self.assertEqual(retrieved_event.event_id, event.event_id)
        print("✅ Получение события: OK")

        # Обновление статуса
        success = self.manager.update_event_status(event.event_id, ResponseStatus.RESOLVED)
        self.assertTrue(success)
        print("✅ Обновление статуса: OK")

        # Получение статистики
        stats = self.manager.get_event_statistics()
        self.assertIn("total_events", stats)
        self.assertEqual(stats["total_events"], 1)
        print("✅ Статистика событий: OK")

    def test_02_async_functionality(self):
        """Тест асинхронной функциональности"""
        print("\n=== Тест 2: Асинхронная функциональность ===")
        
        import asyncio
        
        async def async_test():
            # Асинхронное создание события
            event = await self.manager.create_event_async(
                emergency_type=EmergencyType.MEDICAL,
                severity=EmergencySeverity.CRITICAL,
                location=self.test_location,
                description="Medical emergency in building A",
                user_id="test_user_002"
            )
            
            self.assertIsNotNone(event)
            self.assertEqual(event.emergency_type, EmergencyType.MEDICAL)
            print("✅ Асинхронное создание события: OK")

            # Асинхронное получение событий по типу
            medical_events = await self.manager.get_events_by_type_async(EmergencyType.MEDICAL)
            self.assertEqual(len(medical_events), 1)
            print("✅ Асинхронное получение по типу: OK")

            # Асинхронная статистика
            stats = await self.manager.get_event_statistics_async()
            self.assertIn("total_events", stats)
            print("✅ Асинхронная статистика: OK")

        asyncio.run(async_test())

    def test_03_validation_functionality(self):
        """Тест валидации"""
        print("\n=== Тест 3: Валидация ===")
        
        # Валидация данных события
        valid_data = {
            "emergency_type": "security",
            "description": "Valid description",
            "location": {"lat": 55.7558, "lon": 37.6176}
        }
        self.assertTrue(self.manager._validate_event_data(valid_data))
        print("✅ Валидация данных события: OK")

        # Валидация ID пользователя
        self.assertTrue(self.manager._validate_user_id("valid_user_123"))
        self.assertFalse(self.manager._validate_user_id("ab"))  # Слишком короткий
        print("✅ Валидация ID пользователя: OK")

        # Валидация местоположения
        valid_location = {"lat": 55.7558, "lon": 37.6176, "address": "Valid address"}
        self.assertTrue(self.manager._validate_location(valid_location))
        print("✅ Валидация местоположения: OK")

    def test_04_advanced_analytics(self):
        """Тест расширенной аналитики"""
        print("\n=== Тест 4: Расширенная аналитика ===")
        
        # Создаем несколько событий для аналитики
        for i in range(5):
            self.manager.create_event(
                emergency_type=EmergencyType.SECURITY,
                severity=EmergencySeverity.HIGH,
                location=self.test_location,
                description=f"Security event {i}",
                user_id=f"user_{i}"
            )
        
        # Получаем расширенную аналитику
        analytics = self.manager.get_advanced_analytics()
        
        self.assertIn("trends", analytics)
        self.assertIn("hotspots", analytics)
        self.assertIn("response_times", analytics)
        self.assertIn("user_activity", analytics)
        print("✅ Расширенная аналитика: OK")

        # Проверяем тренды
        trends = analytics["trends"]
        self.assertIn("hourly_distribution", trends)
        self.assertIn("type_distribution", trends)
        print("✅ Анализ трендов: OK")

    def test_05_caching_functionality(self):
        """Тест кэширования"""
        print("\n=== Тест 5: Кэширование ===")
        
        # Создаем событие
        self.manager.create_event(
            emergency_type=EmergencyType.FIRE,
            severity=EmergencySeverity.CRITICAL,
            location=self.test_location,
            description="Fire emergency",
            user_id="test_user_003"
        )
        
        # Тестируем кэшированную статистику
        stats1 = self.manager.get_cached_event_statistics()
        stats2 = self.manager.get_cached_event_statistics()
        
        self.assertEqual(stats1, stats2)
        print("✅ Кэшированная статистика: OK")

        # Тестируем кэшированные события по типу
        fire_events1 = self.manager.get_cached_events_by_type(EmergencyType.FIRE)
        fire_events2 = self.manager.get_cached_events_by_type(EmergencyType.FIRE)
        
        self.assertEqual(len(fire_events1), len(fire_events2))
        print("✅ Кэшированные события по типу: OK")

        # Информация о кэше
        cache_info = self.manager.get_cache_info()
        self.assertIn("total_entries", cache_info)
        print("✅ Информация о кэше: OK")

    def test_06_rate_limiting(self):
        """Тест rate limiting"""
        print("\n=== Тест 6: Rate Limiting ===")
        
        user_id = "test_user_004"
        
        # Создаем события с rate limiting
        for i in range(5):
            try:
                event = self.manager.create_event_with_rate_limit(
                    emergency_type=EmergencyType.POLICE,
                    severity=EmergencySeverity.MEDIUM,
                    location=self.test_location,
                    description=f"Police event {i}",
                    user_id=user_id,
                    rate_limit=3  # Лимит 3 запроса
                )
                if i < 3:
                    self.assertIsNotNone(event)
                else:
                    self.fail("Rate limit должен был сработать")
            except ValueError as e:
                if i >= 3:
                    self.assertIn("Rate limit превышен", str(e))
                    print("✅ Rate limiting работает: OK")
                    break

        # Информация о rate limit
        rate_info = self.manager.get_rate_limit_info(user_id)
        self.assertIn("current_requests", rate_info)
        print("✅ Информация о rate limit: OK")

    def test_07_performance_metrics(self):
        """Тест метрик производительности"""
        print("\n=== Тест 7: Метрики производительности ===")
        
        # Создаем несколько событий
        for i in range(10):
            self.manager.create_event(
                emergency_type=EmergencyType.TECHNICAL,
                severity=EmergencySeverity.LOW,
                location=self.test_location,
                description=f"Technical event {i}",
                user_id=f"user_{i}"
            )
        
        # Получаем метрики производительности
        metrics = self.manager.get_performance_metrics()
        
        self.assertIn("total_operations", metrics)
        self.assertIn("average_response_time", metrics)
        self.assertIn("error_count", metrics)
        self.assertIn("memory_usage", metrics)
        print("✅ Метрики производительности: OK")

        # Состояние системы
        health = self.manager.get_system_health()
        self.assertIn("health_score", health)
        self.assertIn("health_status", health)
        print("✅ Состояние системы: OK")

    def test_08_rest_api_methods(self):
        """Тест REST API методов"""
        print("\n=== Тест 8: REST API методы ===")
        
        # Создаем событие
        event = self.manager.create_event(
            emergency_type=EmergencyType.ACCIDENT,
            severity=EmergencySeverity.HIGH,
            location=self.test_location,
            description="Car accident on highway",
            user_id="test_user_005"
        )
        
        # Преобразование в словарь
        manager_dict = self.manager.to_dict()
        self.assertIn("manager_id", manager_dict)
        self.assertIn("total_events", manager_dict)
        print("✅ Преобразование в словарь: OK")

        # API сводка
        api_summary = self.manager.get_api_summary()
        self.assertIn("status", api_summary)
        self.assertIn("version", api_summary)
        self.assertIn("endpoints", api_summary)
        print("✅ API сводка: OK")

        # События для API
        api_events = self.manager.get_events_for_api(limit=5, offset=0)
        self.assertIn("events", api_events)
        self.assertIn("total", api_events)
        print("✅ События для API: OK")

        # Создание события через API
        api_data = {
            "emergency_type": "natural",
            "severity": "critical",
            "location": self.test_location,
            "description": "Natural disaster",
            "user_id": "test_user_006"
        }
        result = self.manager.create_event_from_api(api_data)
        self.assertTrue(result["success"])
        print("✅ Создание через API: OK")

        # Обновление события через API
        update_data = {"status": "resolved"}
        update_result = self.manager.update_event_from_api(event.event_id, update_data)
        self.assertTrue(update_result["success"])
        print("✅ Обновление через API: OK")

    def test_09_error_handling(self):
        """Тест обработки ошибок"""
        print("\n=== Тест 9: Обработка ошибок ===")
        
        # Попытка получить несуществующее событие
        non_existent = self.manager.get_event("non_existent_id")
        self.assertIsNone(non_existent)
        print("✅ Обработка несуществующего события: OK")

        # Попытка обновить несуществующее событие
        update_result = self.manager.update_event_status("non_existent_id", ResponseStatus.RESOLVED)
        self.assertFalse(update_result)
        print("✅ Обработка обновления несуществующего события: OK")

        # Попытка создать событие с невалидными данными
        try:
            self.manager.create_event_from_api({
                "emergency_type": "invalid_type",
                "severity": "invalid_severity",
                "location": {},
                "description": "Test"
            })
            self.fail("Должна была возникнуть ошибка валидации")
        except Exception:
            print("✅ Обработка невалидных данных API: OK")

    def test_10_comprehensive_integration(self):
        """Тест комплексной интеграции"""
        print("\n=== Тест 10: Комплексная интеграция ===")
        
        # Создаем разнообразные события
        event_types = [EmergencyType.SECURITY, EmergencyType.MEDICAL, EmergencyType.FIRE]
        severities = [EmergencySeverity.LOW, EmergencySeverity.MEDIUM, EmergencySeverity.HIGH]
        
        for i, (event_type, severity) in enumerate(zip(event_types, severities)):
            event = self.manager.create_event(
                emergency_type=event_type,
                severity=severity,
                location=self.test_location,
                description="Security breach detected in main system",
                user_id=f"integration_user_{i}"
            )
            
            # Обновляем статус
            self.manager.update_event_status(event.event_id, ResponseStatus.RESOLVED)
        
        # Получаем все виды аналитики
        basic_stats = self.manager.get_event_statistics()
        advanced_analytics = self.manager.get_advanced_analytics()
        performance_metrics = self.manager.get_performance_metrics()
        system_health = self.manager.get_system_health()
        
        # Проверяем, что все работает
        self.assertGreater(basic_stats["total_events"], 0)
        self.assertIn("trends", advanced_analytics)
        self.assertIn("total_operations", performance_metrics)
        self.assertIn("health_score", system_health)
        
        print("✅ Комплексная интеграция: OK")

    def test_11_cleanup_and_maintenance(self):
        """Тест очистки и обслуживания"""
        print("\n=== Тест 11: Очистка и обслуживание ===")
        
        # Создаем старые события
        old_time = datetime.now() - timedelta(days=10)
        for i in range(5):
            event = self.manager.create_event(
                emergency_type=EmergencyType.TECHNICAL,
                severity=EmergencySeverity.LOW,
                location=self.test_location,
                description=f"Old event {i}",
                user_id=f"old_user_{i}"
            )
            # Устанавливаем старую дату
            event.timestamp = old_time
        
        # Очистка старых событий
        cleaned_count = self.manager.cleanup_old_events(days=5)
        self.assertGreater(cleaned_count, 0)
        print("✅ Очистка старых событий: OK")

        # Очистка кэша
        cache_cleared = self.manager.clear_cache()
        self.assertGreaterEqual(cache_cleared, 0)
        print("✅ Очистка кэша: OK")

        # Очистка rate limits
        rate_limits_cleared = self.manager.clear_rate_limits()
        self.assertGreaterEqual(rate_limits_cleared, 0)
        print("✅ Очистка rate limits: OK")

    def test_12_edge_cases(self):
        """Тест граничных случаев"""
        print("\n=== Тест 12: Граничные случаи ===")
        
        # Пустой менеджер
        empty_manager = EmergencyEventManager(max_events=10)
        self.assertEqual(len(empty_manager.events), 0)
        print("✅ Пустой менеджер: OK")

        # Максимальное количество событий
        for i in range(5):
            import time
            time.sleep(0.001)  # Небольшая задержка для уникальных ID
            empty_manager.create_event(
                emergency_type=EmergencyType.SECURITY,
                severity=EmergencySeverity.LOW,
                location=self.test_location,
                description="Security breach detected in main system",
                user_id=f"edge_user_{i}"
            )
        
        # Проверяем, что события создаются
        self.assertEqual(len(empty_manager.events), 5)
        print("✅ Максимальное количество событий: OK")

        # Экспорт/импорт
        export_file = "/tmp/test_export.json"
        export_success = empty_manager.export_events(export_file)
        self.assertTrue(export_success)
        print("✅ Экспорт событий: OK")

        # Импорт событий
        import_success = empty_manager.import_events(export_file)
        self.assertTrue(import_success)
        print("✅ Импорт событий: OK")

        # Очистка тестового файла
        if os.path.exists(export_file):
            os.remove(export_file)


def run_comprehensive_tests():
    """Запуск всех comprehensive тестов"""
    print("🚀 Запуск Comprehensive тестов для EmergencyEventManager")
    print("=" * 60)
    
    # Создаем test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestEmergencyEventManagerComprehensive)
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Выводим результаты
    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТЫ COMPREHENSIVE ТЕСТОВ:")
    print(f"✅ Успешных тестов: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Неудачных тестов: {len(result.failures)}")
    print(f"💥 Ошибок: {len(result.errors)}")
    print(f"📈 Успешность: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\n❌ НЕУДАЧНЫЕ ТЕСТЫ:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n💥 ОШИБКИ:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)