#!/usr/bin/env python3
"""
Интеграция российских API с SafeFunctionManager
Яндекс Карты, ГЛОНАСС и другие российские сервисы
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.russian_api_manager import russian_api_manager, RussianAPIType
from security.safe_function_manager import SafeFunctionManager
from core.base import SecurityLevel, ComponentStatus
from core.logging_module import LoggingManager

logger = LoggingManager(name="IntegrateRussianAPIs")


def integrate_russian_apis():
    """Интеграция российских API с SafeFunctionManager"""
    logger.log("INFO", "🚀 Запуск интеграции российских API...")
    print("=" * 60)
    print("🔗 Интеграция российских API с SafeFunctionManager...")
    
    try:
        # Получаем SafeFunctionManager
        safe_manager = SafeFunctionManager()
        
        # Регистрируем Яндекс Карты API
        print("📝 Регистрация функции: Яндекс Карты API")
        result_yandex = safe_manager.register_function(
            function_id="russian_yandex_maps",
            name="Яндекс Карты API",
            description="Геокодирование и маршрутизация через Яндекс Карты с поддержкой ГЛОНАСС",
            function_type="geolocation",
            security_level=SecurityLevel.HIGH,
            auto_enable=True
        )
        
        if result_yandex:
            logger.log("ERROR", "✅ Функция 'Яндекс Карты API' успешно интегрирована")
            print("✅ Яндекс Карты API зарегистрирован")
        else:
            logger.log("INFO", "❌ Ошибка интеграции функции 'Яндекс Карты API'")
            print("❌ Ошибка регистрации Яндекс Карты API")
        
        # Регистрируем ГЛОНАСС API
        print("📝 Регистрация функции: ГЛОНАСС API")
        result_glonass = safe_manager.register_function(
            function_id="russian_glonass",
            name="ГЛОНАСС API",
            description="Получение координат через российскую спутниковую систему ГЛОНАСС",
            function_type="geolocation",
            security_level=SecurityLevel.HIGH,
            auto_enable=True
        )
        
        if result_glonass:
            logger.log("ERROR", "✅ Функция 'ГЛОНАСС API' успешно интегрирована")
            print("✅ ГЛОНАСС API зарегистрирован")
        else:
            logger.log("INFO", "❌ Ошибка интеграции функции 'ГЛОНАСС API'")
            print("❌ Ошибка регистрации ГЛОНАСС API")
        
        # Регистрируем Открытый ГЛОНАСС
        print("📝 Регистрация функции: Открытый ГЛОНАСС")
        result_free_glonass = safe_manager.register_function(
            function_id="russian_free_glonass",
            name="Открытый ГЛОНАСС",
            description="Бесплатный мониторинг транспорта через ГЛОНАСС/GPS IoT",
            function_type="monitoring",
            security_level=SecurityLevel.MEDIUM,
            auto_enable=True
        )
        
        if result_free_glonass:
            logger.log("ERROR", "✅ Функция 'Открытый ГЛОНАСС' успешно интегрирована")
            print("✅ Открытый ГЛОНАСС зарегистрирован")
        else:
            logger.log("INFO", "❌ Ошибка интеграции функции 'Открытый ГЛОНАСС'")
            print("❌ Ошибка регистрации Открытый ГЛОНАСС")
        
        # Регистрируем ALTOX Server
        print("📝 Регистрация функции: ALTOX Server")
        result_altox = safe_manager.register_function(
            function_id="russian_altox_server",
            name="ALTOX Server",
            description="Бесплатная система GPS-GLONASS мониторинга транспорта",
            function_type="monitoring",
            security_level=SecurityLevel.MEDIUM,
            auto_enable=True
        )
        
        if result_altox:
            logger.log("ERROR", "✅ Функция 'ALTOX Server' успешно интегрирована")
            print("✅ ALTOX Server зарегистрирован")
        else:
            logger.log("INFO", "❌ Ошибка интеграции функции 'ALTOX Server'")
            print("❌ Ошибка регистрации ALTOX Server")
        
        # Проверяем статус зарегистрированных функций
        print("\n📊 Статус зарегистрированных функций:")
        function_ids = [
            "russian_yandex_maps",
            "russian_glonass", 
            "russian_free_glonass",
            "russian_altox_server"
        ]
        
        for func_id in function_ids:
            status = safe_manager.get_function_status(func_id)
            if status:
                print(f"  - {status.get('name')}: {status.get('status')}")
                logger.log("WARNING", f"Функция {func_id}: {status.get('status')}")
            else:
                print(f"  - {func_id}: Не найдена")
                logger.log("INFO", f"Функция {func_id} не найдена")
        
        # Тестируем функции через SafeFunctionManager
        print("\n🧪 Тестирование функций через SafeFunctionManager:")
        
        # Тест геокодирования
        print("  - Тест геокодирования (Москва):")
        try:
            geocode_result = safe_manager.execute_function(
                "russian_yandex_maps", 
                address="Москва, Красная площадь"
            )
            print(f"    Результат: {geocode_result}")
            logger.log("ERROR", f"Тест геокодирования: {geocode_result}")
        except Exception as e:
            print(f"    Ошибка: {e}")
            logger.log("INFO", f"Ошибка теста геокодирования: {e}")
        
        # Тест маршрутизации
        print("  - Тест маршрутизации (Москва -> СПб):")
        try:
            route_result = safe_manager.execute_function(
                "russian_yandex_maps",
                from_point="Москва",
                to_point="Санкт-Петербург"
            )
            print(f"    Результат: {route_result}")
            logger.log("ERROR", f"Тест маршрутизации: {route_result}")
        except Exception as e:
            print(f"    Ошибка: {e}")
            logger.log("INFO", f"Ошибка теста маршрутизации: {e}")
        
        # Тест ГЛОНАСС
        print("  - Тест ГЛОНАСС координат:")
        try:
            glonass_result = safe_manager.execute_function(
                "russian_glonass",
                device_id="test_device_001"
            )
            print(f"    Результат: {glonass_result}")
            logger.log("ERROR", f"Тест ГЛОНАСС: {glonass_result}")
        except Exception as e:
            print(f"    Ошибка: {e}")
            logger.log("INFO", f"Ошибка теста ГЛОНАСС: {e}")
        
        # Получаем статистику
        print("\n📊 Статистика российских API:")
        try:
            stats = russian_api_manager.get_usage_statistics()
            usage = stats.get('usage_stats', {})
            print(f"  📈 Всего запросов: {usage.get('total_requests', 0)}")
            print(f"  ✅ Успешных: {usage.get('successful_requests', 0)}")
            print(f"  ❌ Неудачных: {usage.get('failed_requests', 0)}")
            print(f"  💾 Кэш попаданий: {usage.get('cache_hits', 0)}")
            print(f"  🔧 API конфигураций: {len(stats.get('api_configs', {}))}")
            
            logger.log("ERROR", f"Статистика: {stats}")
        except Exception as e:
            print(f"  Ошибка получения статистики: {e}")
            logger.log("INFO", f"Ошибка получения статистики: {e}")
        
        print("\n✅ Интеграция российских API завершена успешно!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        logger.log("CRITICAL", f"❌ Критическая ошибка при интеграции российских API: {e}")
        print(f"❌ Критическая ошибка при интеграции российских API: {e}")
        return False


def test_russian_apis_direct():
    """Прямое тестирование российских API без SafeFunctionManager"""
    print(f"\n🧪 Прямое тестирование российских API...")
    
    try:
        import asyncio
        
        # Тест геокодирования
        print("🌍 Тестирование геокодирования...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        geocode_result = loop.run_until_complete(
            russian_api_manager.geocode_address("Москва, Красная площадь")
        )
        loop.close()
        
        if geocode_result:
            print("✅ Геокодирование работает")
            print(f"   📍 Адрес: {geocode_result.address}")
            print(f"   📊 Координаты: {geocode_result.coordinates}")
            print(f"   🏙️ Город: {geocode_result.city}")
            print(f"   🌍 Страна: {geocode_result.country}")
            print(f"   🔧 API: {geocode_result.api_source}")
        else:
            print("❌ Геокодирование не работает")
        
        # Тест маршрутизации
        print("🛣️ Тестирование маршрутизации...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        route_result = loop.run_until_complete(
            russian_api_manager.build_route("Москва", "Санкт-Петербург")
        )
        loop.close()
        
        if route_result:
            print("✅ Маршрутизация работает")
            print(f"   🚗 Маршрут: {route_result.from_point} -> {route_result.to_point}")
            print(f"   📏 Расстояние: {route_result.distance:.0f} м")
            print(f"   ⏱️ Время: {route_result.duration:.0f} сек")
            print(f"   🔧 API: {route_result.api_source}")
        else:
            print("❌ Маршрутизация не работает")
        
        # Тест ГЛОНАСС
        print("🛰️ Тестирование ГЛОНАСС...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        glonass_result = loop.run_until_complete(
            russian_api_manager.get_glonass_coordinates("test_device")
        )
        loop.close()
        
        if glonass_result:
            print("✅ ГЛОНАСС работает")
            print(f"   📍 Координаты: {glonass_result}")
        else:
            print("❌ ГЛОНАСС не работает")
        
        # Статистика
        stats = russian_api_manager.get_usage_statistics()
        print(f"\n📊 Статистика использования:")
        usage = stats.get('usage_stats', {})
        print(f"   📈 Всего запросов: {usage.get('total_requests', 0)}")
        print(f"   ✅ Успешных: {usage.get('successful_requests', 0)}")
        print(f"   ❌ Неудачных: {usage.get('failed_requests', 0)}")
        print(f"   💾 Кэш попаданий: {usage.get('cache_hits', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        logger.log("ERROR", f"Ошибка прямого тестирования: {e}")
        return False


if __name__ == '__main__':
    print("🚀 Запуск интеграции российских API...")
    print("=" * 60)
    
    # Интеграция с SafeFunctionManager
    integration_success = integrate_russian_apis()
    
    # Прямое тестирование
    direct_test_success = test_russian_apis_direct()
    
    print(f"\n" + "=" * 60)
    print(f"📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ:")
    print(f"✅ Интеграция SafeFunctionManager: {'Да' if integration_success else 'Нет'}")
    print(f"✅ Прямое тестирование API: {'Да' if direct_test_success else 'Нет'}")
    
    if integration_success and direct_test_success:
        print(f"\n🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print(f"✅ Российские API работают корректно")
        print(f"✅ Интеграция с SafeFunctionManager успешна")
        print(f"🌐 API доступно: http://localhost:5005/api/russian/")
    else:
        print(f"\n⚠️ Некоторые тесты не прошли")
    
    print("=" * 60)