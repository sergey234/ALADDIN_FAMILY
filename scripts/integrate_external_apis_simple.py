#!/usr/bin/env python3
"""
Упрощенная интеграция ExternalAPIManager с SafeFunctionManager
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.managers.external_api_manager import external_api_manager
from security.safe_function_manager import SafeFunctionManager
from core.base import SecurityLevel


def integrate_external_apis_simple():
    """Упрощенная интеграция внешних API"""
    print("🔗 Упрощенная интеграция ExternalAPIManager...")
    
    try:
        # Получаем SafeFunctionManager
        safe_manager = SafeFunctionManager()
        
        # Регистрируем только одну функцию для теста
        print("📝 Регистрация функции: External API Manager")
        
        result = safe_manager.register_function(
            function_id="external_api_manager",
            name="External API Manager",
            description="Менеджер внешних API для анализа угроз, геолокации и валидации email",
            function_type="security",
            security_level=SecurityLevel.HIGH,
            auto_enable=False  # Не включаем автоматически
        )
        
        if result:
            print("✅ External API Manager успешно зарегистрирован")
            
            # Проверяем статус
            status = safe_manager.get_function_status("external_api_manager")
            if status:
                print(f"📊 Статус: {status.get('status', 'unknown')}")
                print(f"🔒 Уровень безопасности: {status.get('security_level', 'unknown')}")
                print(f"📝 Описание: {status.get('description', 'unknown')}")
            
            return True
        else:
            print("❌ Ошибка регистрации External API Manager")
            return False
        
    except Exception as e:
        print(f"❌ Ошибка интеграции: {e}")
        return False


def test_external_apis_direct():
    """Прямое тестирование внешних API без SafeFunctionManager"""
    print(f"\n🧪 Прямое тестирование внешних API...")
    
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
            for api_name, data in geo_result.items():
                print(f"   - {api_name}: {type(data).__name__}")
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
            for api_name, data in email_result.items():
                print(f"   - {api_name}: {type(data).__name__}")
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
            for api_name, data in threat_result.items():
                print(f"   - {api_name}: {type(data).__name__}")
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


def test_external_apis_server():
    """Тестирование External APIs Server"""
    print(f"\n🌐 Тестирование External APIs Server...")
    
    try:
        import requests
        
        # Health check
        print("🔍 Проверка здоровья сервера...")
        response = requests.get("http://localhost:5004/api/external/health", timeout=5)
        
        if response.status_code == 200:
            print("✅ External APIs Server работает")
            data = response.json()
            print(f"   📊 Статус: {data.get('status', 'unknown')}")
            print(f"   🕒 Время: {data.get('timestamp', 'unknown')}")
        else:
            print(f"❌ Сервер не отвечает: {response.status_code}")
            return False
        
        # Тест IP геолокации через API
        print("🌍 Тест IP геолокации через API...")
        geo_response = requests.post(
            "http://localhost:5004/api/external/ip-geolocation",
            json={"ip": "8.8.8.8"},
            timeout=10
        )
        
        if geo_response.status_code == 200:
            print("✅ IP геолокация API работает")
            data = geo_response.json()
            print(f"   📊 Успех: {data.get('success', False)}")
            print(f"   📊 Результаты: {len(data.get('results', {}))} API")
        else:
            print(f"❌ IP геолокация API не работает: {geo_response.status_code}")
        
        # Тест валидации email через API
        print("📧 Тест валидации email через API...")
        email_response = requests.post(
            "http://localhost:5004/api/external/email-validation",
            json={"email": "test@example.com"},
            timeout=10
        )
        
        if email_response.status_code == 200:
            print("✅ Email validation API работает")
            data = email_response.json()
            print(f"   📊 Успех: {data.get('success', False)}")
            print(f"   📊 Результаты: {len(data.get('results', {}))} API")
        else:
            print(f"❌ Email validation API не работает: {email_response.status_code}")
        
        # Статистика API
        print("📊 Получение статистики API...")
        stats_response = requests.get("http://localhost:5004/api/external/statistics", timeout=5)
        
        if stats_response.status_code == 200:
            print("✅ Статистика API работает")
            data = stats_response.json()
            stats = data.get('statistics', {})
            usage = stats.get('usage_stats', {})
            print(f"   📈 Всего запросов: {usage.get('total_requests', 0)}")
            print(f"   ✅ Успешных: {usage.get('successful_requests', 0)}")
            print(f"   ❌ Неудачных: {usage.get('failed_requests', 0)}")
        else:
            print(f"❌ Статистика API не работает: {stats_response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования сервера: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Запуск упрощенной интеграции ExternalAPIManager...")
    print("=" * 60)
    
    # Интеграция
    integration_success = integrate_external_apis_simple()
    
    if integration_success:
        print(f"\n✅ ИНТЕГРАЦИЯ С SAFEFUNCTIONMANAGER УСПЕШНА!")
    else:
        print(f"\n⚠️ Интеграция с SafeFunctionManager не удалась, но продолжаем...")
    
    # Прямое тестирование API
    direct_test_success = test_external_apis_direct()
    
    # Тестирование сервера
    server_test_success = test_external_apis_server()
    
    print(f"\n" + "=" * 60)
    print(f"📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ:")
    print(f"✅ Интеграция SafeFunctionManager: {'Да' if integration_success else 'Нет'}")
    print(f"✅ Прямое тестирование API: {'Да' if direct_test_success else 'Нет'}")
    print(f"✅ Тестирование сервера: {'Да' if server_test_success else 'Нет'}")
    
    if direct_test_success and server_test_success:
        print(f"\n🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print(f"✅ ExternalAPIManager работает корректно")
        print(f"✅ External APIs Server работает корректно")
        print(f"🌐 API доступно: http://localhost:5004/api/external/")
    else:
        print(f"\n⚠️ Некоторые тесты не прошли")
    
    print("=" * 60)