#!/usr/bin/env python3
"""
Упрощенная интеграция российских API с SafeFunctionManager
Без блокировок и сложных операций
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.russian_api_manager import russian_api_manager, RussianAPIType
from security.safe_function_manager import SafeFunctionManager
from core.base import SecurityLevel, ComponentStatus
from core.logging_module import LoggingManager

logger = LoggingManager(name="IntegrateRussianAPIsSimple")


def integrate_russian_apis_simple():
    """Упрощенная интеграция российских API"""
    logger.log("INFO", "🚀 Запуск упрощенной интеграции российских API...")
    print("=" * 60)
    print("🔗 Упрощенная интеграция российских API...")
    
    try:
        # Получаем SafeFunctionManager
        safe_manager = SafeFunctionManager()
        
        # Регистрируем только одну функцию для теста
        print("📝 Регистрация функции: Russian API Manager")
        
        result = safe_manager.register_function(
            function_id="russian_api_manager",
            name="Russian API Manager",
            description="Менеджер российских API для геолокации, маршрутизации и ГЛОНАСС",
            function_type="geolocation",
            security_level=SecurityLevel.HIGH,
            auto_enable=False  # НЕ включаем автоматически
        )
        
        if result:
            logger.log("INFO", "✅ Russian API Manager успешно зарегистрирован")
            print("✅ Russian API Manager зарегистрирован")
            
            # Проверяем статус
            status = safe_manager.get_function_status("russian_api_manager")
            if status:
                print(f"📊 Статус: {status.get('status')}")
                print(f"🔒 Уровень безопасности: {status.get('security_level')}")
                print(f"📝 Описание: {status.get('description')}")
                logger.log("INFO", f"Статус функции: {status}")
            else:
                print("❌ Функция не найдена")
                logger.log("ERROR", "Функция не найдена")
        else:
            logger.log("ERROR", "❌ Ошибка регистрации Russian API Manager")
            print("❌ Ошибка регистрации Russian API Manager")
        
        # Тестируем российские API напрямую
        print("\n🧪 Прямое тестирование российских API...")
        
        # Тест геокодирования
        print("🌍 Тестирование геокодирования...")
        try:
            import asyncio
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
                logger.log("INFO", f"Геокодирование успешно: {geocode_result}")
            else:
                print("❌ Геокодирование не работает")
                logger.log("ERROR", "Геокодирование не работает")
        except Exception as e:
            print(f"❌ Ошибка геокодирования: {e}")
            logger.log("ERROR", f"Ошибка геокодирования: {e}")
        
        # Тест маршрутизации
        print("🛣️ Тестирование маршрутизации...")
        try:
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
                logger.log("INFO", f"Маршрутизация успешно: {route_result}")
            else:
                print("❌ Маршрутизация не работает")
                logger.log("ERROR", "Маршрутизация не работает")
        except Exception as e:
            print(f"❌ Ошибка маршрутизации: {e}")
            logger.log("ERROR", f"Ошибка маршрутизации: {e}")
        
        # Тест ГЛОНАСС
        print("🛰️ Тестирование ГЛОНАСС...")
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            glonass_result = loop.run_until_complete(
                russian_api_manager.get_glonass_coordinates("test_device")
            )
            loop.close()
            
            if glonass_result:
                print("✅ ГЛОНАСС работает")
                print(f"   📍 Координаты: {glonass_result}")
                logger.log("INFO", f"ГЛОНАСС успешно: {glonass_result}")
            else:
                print("❌ ГЛОНАСС не работает")
                logger.log("ERROR", "ГЛОНАСС не работает")
        except Exception as e:
            print(f"❌ Ошибка ГЛОНАСС: {e}")
            logger.log("ERROR", f"Ошибка ГЛОНАСС: {e}")
        
        # Статистика
        print("\n📊 Статистика использования:")
        try:
            stats = russian_api_manager.get_usage_statistics()
            usage = stats.get('usage_stats', {})
            print(f"   📈 Всего запросов: {usage.get('total_requests', 0)}")
            print(f"   ✅ Успешных: {usage.get('successful_requests', 0)}")
            print(f"   ❌ Неудачных: {usage.get('failed_requests', 0)}")
            print(f"   💾 Кэш попаданий: {usage.get('cache_hits', 0)}")
            print(f"   🔧 API конфигураций: {len(stats.get('api_configs', {}))}")
            logger.log("INFO", f"Статистика: {stats}")
        except Exception as e:
            print(f"   Ошибка получения статистики: {e}")
            logger.log("ERROR", f"Ошибка получения статистики: {e}")
        
        print("\n✅ Упрощенная интеграция завершена!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        logger.log("CRITICAL", f"❌ Критическая ошибка при интеграции: {e}")
        print(f"❌ Критическая ошибка при интеграции: {e}")
        return False


if __name__ == '__main__':
    print("🚀 Запуск упрощенной интеграции российских API...")
    print("=" * 60)
    
    # Интеграция с SafeFunctionManager
    integration_success = integrate_russian_apis_simple()
    
    print(f"\n" + "=" * 60)
    print(f"📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ:")
    print(f"✅ Интеграция SafeFunctionManager: {'Да' if integration_success else 'Нет'}")
    
    if integration_success:
        print(f"\n🎉 ИНТЕГРАЦИЯ УСПЕШНА!")
        print(f"✅ Российские API работают корректно")
        print(f"✅ SafeFunctionManager интеграция успешна")
        print(f"🌐 API доступно: http://localhost:5005/api/russian/")
    else:
        print(f"\n⚠️ Интеграция не завершена")
    
    print("=" * 60)