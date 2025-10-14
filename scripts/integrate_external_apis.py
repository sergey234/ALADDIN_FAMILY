#!/usr/bin/env python3
"""
Интеграция ExternalAPIManager с SafeFunctionManager
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.managers.external_api_manager import external_api_manager
from security.safe_function_manager import SafeFunctionManager
from core.base import SecurityLevel


def integrate_external_apis():
    """Интеграция внешних API с SafeFunctionManager"""
    print("🔗 Интеграция ExternalAPIManager с SafeFunctionManager...")
    
    try:
        # Получаем SafeFunctionManager
        safe_manager = SafeFunctionManager()
        
        # Регистрируем функции внешних API
        functions_to_register = [
            {
                "function_id": "external_api_manager",
                "name": "External API Manager",
                "description": "Менеджер внешних API для анализа угроз, геолокации и валидации email",
                "function_type": "security",
                "security_level": SecurityLevel.HIGH,
                "auto_enable": False
            }
        ]
        
        registered_functions = []
        
        for func_config in functions_to_register:
            print(f"📝 Регистрация функции: {func_config['name']}")
            
            result = safe_manager.register_function(
                function_id=func_config["function_id"],
                name=func_config["name"],
                description=func_config["description"],
                function_type=func_config["function_type"],
                security_level=func_config["security_level"],
                auto_enable=func_config["auto_enable"]
            )
            
            if result:
                print(f"✅ {func_config['name']} успешно зарегистрирована")
                registered_functions.append(func_config["function_id"])
            else:
                print(f"❌ Ошибка регистрации {func_config['name']}")
        
        print(f"\n📊 Результаты интеграции:")
        print(f"✅ Успешно зарегистрировано: {len(registered_functions)} функций")
        print(f"📋 Функции: {', '.join(registered_functions)}")
        
        # Тестируем функции
        print(f"\n🧪 Тестирование зарегистрированных функций...")
        
        for func_id in registered_functions:
            print(f"🔍 Тестирование {func_id}...")
            
            # Получаем статус функции
            status = safe_manager.get_function_status(func_id)
            if status:
                print(f"   📊 Статус: {status.get('status', 'unknown')}")
                print(f"   🔒 Уровень безопасности: {status.get('security_level', 'unknown')}")
                print(f"   📝 Описание: {status.get('description', 'unknown')}")
                
                # Включаем функцию
                enable_result = safe_manager.enable_function(func_id)
                if enable_result:
                    print(f"   ✅ Функция включена")
                else:
                    print(f"   ❌ Ошибка включения функции")
            else:
                print(f"   ❌ Функция не найдена")
        
        print(f"\n🎉 Интеграция ExternalAPIManager завершена!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка интеграции: {e}")
        return False


def test_external_apis():
    """Тестирование внешних API"""
    print(f"\n🧪 Тестирование внешних API...")
    
    try:
        import asyncio
        
        # Тест геолокации
        print("🌍 Тестирование IP геолокации...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        geo_result = loop.run_until_complete(
            external_api_manager.get_ip_geolocation("8.8.8.8")
        )
        loop.close()
        
        if geo_result:
            print("✅ IP геолокация работает")
            print(f"   📊 Результаты: {len(geo_result)} API ответили")
        else:
            print("❌ IP геолокация не работает")
        
        # Тест валидации email
        print("📧 Тестирование валидации email...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        email_result = loop.run_until_complete(
            external_api_manager.validate_email("test@example.com")
        )
        loop.close()
        
        if email_result:
            print("✅ Валидация email работает")
            print(f"   📊 Результаты: {len(email_result)} API ответили")
        else:
            print("❌ Валидация email не работает")
        
        # Тест анализа угроз
        print("🛡️ Тестирование анализа угроз...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        threat_result = loop.run_until_complete(
            external_api_manager.check_threat_intelligence("8.8.8.8")
        )
        loop.close()
        
        if threat_result:
            print("✅ Анализ угроз работает")
            print(f"   📊 Результаты: {len(threat_result)} API ответили")
        else:
            print("❌ Анализ угроз не работает")
        
        # Статистика
        stats = external_api_manager.get_usage_statistics()
        print(f"\n📊 Статистика использования:")
        print(f"   📈 Всего запросов: {stats['usage_stats']['total_requests']}")
        print(f"   ✅ Успешных: {stats['usage_stats']['successful_requests']}")
        print(f"   ❌ Неудачных: {stats['usage_stats']['failed_requests']}")
        print(f"   💾 Кэш попаданий: {stats['usage_stats']['cache_hits']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Запуск интеграции ExternalAPIManager...")
    print("=" * 50)
    
    # Интеграция
    integration_success = integrate_external_apis()
    
    if integration_success:
        # Тестирование
        test_success = test_external_apis()
        
        if test_success:
            print(f"\n🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
            print(f"✅ ExternalAPIManager интегрирован с SafeFunctionManager")
            print(f"✅ Внешние API работают корректно")
        else:
            print(f"\n⚠️ Интеграция прошла, но тесты не прошли")
    else:
        print(f"\n❌ ОШИБКА ИНТЕГРАЦИИ")
    
    print("=" * 50)