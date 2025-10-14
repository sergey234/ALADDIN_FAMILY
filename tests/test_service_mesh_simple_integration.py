#!/usr/bin/env python3
"""
Простой интеграционный тест для Service Mesh Manager
Проверяет основные функции без сложных интеграций
"""

import sys
import os
import time
from datetime import datetime

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.microservices.service_mesh_manager import (
    ServiceMeshManager,
    ServiceInfo,
    ServiceType,
    ServiceStatus
)


def test_basic_functionality():
    """Тест базовой функциональности"""
    print("🧪 Тестирование базовой функциональности...")
    
    try:
        # Создание менеджера
        manager = ServiceMeshManager(name="TestManager")
        print("✅ ServiceMeshManager создан")
        
        # Инициализация
        success = manager.initialize()
        assert success, "Инициализация не удалась"
        print("✅ Инициализация успешна")
        
        # Создание тестового сервиса
        service_info = ServiceInfo(
            service_id="test_service",
            name="Test Service",
            description="Тестовый сервис",
            service_type=ServiceType.SECURITY,
            version="1.0.0",
            endpoints=[],
            dependencies=[]
        )
        
        # Регистрация сервиса
        manager.register_service(service_info)
        assert "test_service" in manager.services
        print("✅ Сервис зарегистрирован")
        
        # Проверка статуса
        assert manager.status.value == "running"
        print("✅ Статус: running")
        
        # Остановка
        manager.stop()
        print("✅ Менеджер остановлен")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


def test_rate_limiting():
    """Тест rate limiting"""
    print("\n🧪 Тестирование rate limiting...")
    
    try:
        manager = ServiceMeshManager(name="TestRateLimit")
        manager.initialize()
        
        # Включение rate limiting
        manager.enable_rate_limiting()
        print("✅ Rate limiting включен")
        
        # Установка лимитов
        manager.set_service_rate_limit("test_service", {
            "per_minute": 3,
            "per_hour": 30,
            "per_day": 300
        })
        print("✅ Лимиты установлены")
        
        # Тестирование лимитов
        allowed = 0
        blocked = 0
        
        for i in range(5):
            if manager.check_rate_limit("service", "test_service"):
                allowed += 1
            else:
                blocked += 1
        
        print(f"✅ Разрешено: {allowed}, Заблокировано: {blocked}")
        
        # Получение статистики
        stats = manager.get_rate_limit_stats("service", "test_service")
        print(f"✅ Статистика: {stats}")
        
        manager.stop()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


def test_monitoring():
    """Тест мониторинга"""
    print("\n🧪 Тестирование мониторинга...")
    
    try:
        manager = ServiceMeshManager(name="TestMonitoring")
        manager.initialize()
        
        # Включение мониторинга
        manager.enable_monitoring()
        print("✅ Мониторинг включен")
        
        # Получение состояния системы
        health = manager.get_system_health()
        print(f"✅ Состояние системы: CPU {health.cpu_usage}%, Memory {health.memory_usage}%")
        
        # Отправка тестового алерта
        success = manager.send_test_alert("info", "Test alert")
        print(f"✅ Тестовый алерт отправлен: {success}")
        
        # Получение сводки мониторинга
        summary = manager.get_monitoring_summary()
        print(f"✅ Сводка мониторинга получена")
        
        manager.stop()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


def test_caching():
    """Тест кэширования"""
    print("\n🧪 Тестирование кэширования...")
    
    try:
        manager = ServiceMeshManager(name="TestCache")
        manager.initialize()
        
        # Включение кэширования
        manager.cache_enable()
        print("✅ Кэширование включено")
        
        # Тестирование кэша
        test_key = "test_key"
        test_value = {"data": "test_value", "timestamp": datetime.now().isoformat()}
        
        # Установка значения
        manager.cache_set(test_key, test_value, ttl_seconds=60)
        print("✅ Значение установлено в кэш")
        
        # Получение значения
        cached_value = manager.cache_get(test_key)
        assert cached_value is not None
        assert cached_value["data"] == test_value["data"]
        print("✅ Значение получено из кэша")
        
        # Статистика кэша
        stats = manager.cache_get_statistics()
        print(f"✅ Статистика кэша: {stats}")
        
        manager.stop()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


def main():
    """Главная функция"""
    print("🔧 Простое тестирование Service Mesh Manager")
    print("=" * 50)
    
    tests = [
        ("Базовая функциональность", test_basic_functionality),
        ("Rate Limiting", test_rate_limiting),
        ("Мониторинг", test_monitoring),
        ("Кэширование", test_caching)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name}: Неожиданная ошибка: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("=" * 50)
    print(f"✅ Пройдено: {passed}")
    print(f"❌ Провалено: {failed}")
    print(f"📈 Успешность: {(passed / (passed + failed)) * 100:.1f}%")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)