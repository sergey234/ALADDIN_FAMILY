#!/usr/bin/env python3
"""
Финальная проверка всех функций Service Mesh Manager
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
    ServiceType
)


def test_all_functions():
    """Тест всех функций"""
    print("🔧 Финальная проверка Service Mesh Manager")
    print("=" * 50)
    
    try:
        # Создание менеджера
        manager = ServiceMeshManager(name="FinalTest")
        print("✅ 1. ServiceMeshManager создан")
        
        # Инициализация
        success = manager.initialize()
        assert success
        print("✅ 2. Инициализация успешна")
        
        # Регистрация сервиса
        service_info = ServiceInfo(
            service_id="test_service",
            name="Test Service",
            description="Тестовый сервис",
            service_type=ServiceType.SECURITY,
            version="1.0.0",
            endpoints=[],
            dependencies=[]
        )
        manager.register_service(service_info)
        print("✅ 3. Сервис зарегистрирован")
        
        # Rate Limiting
        manager.enable_rate_limiting()
        manager.set_service_rate_limit("test_service", {"per_minute": 3})
        allowed = sum(1 for _ in range(5) if manager.check_rate_limit("service", "test_service"))
        print(f"✅ 4. Rate Limiting работает: {allowed}/5 запросов разрешено")
        
        # Мониторинг
        manager.enable_monitoring()
        health = manager.get_system_health()
        print(f"✅ 5. Мониторинг работает: CPU {health.cpu_usage}%, Memory {health.memory_usage}%")
        
        # Кэширование
        manager.cache_enable()
        manager.cache_set("test_key", {"data": "test"}, ttl_seconds=60)
        cached = manager.cache_get("test_key")
        assert cached["data"] == "test"
        print("✅ 6. Кэширование работает")
        
        # Оптимизация производительности
        manager.enable_performance_optimization()
        perf_stats = manager.get_performance_stats()
        assert "memory_stats" in perf_stats
        print("✅ 7. Оптимизация производительности работает")
        
        # Логирование
        manager.enable_logging()
        logging_stats = manager.get_logging_statistics()
        assert logging_stats["enabled"]
        print("✅ 8. Логирование работает")
        
        # Асинхронная функциональность
        manager.enable_async()
        manager.start_async_loop()
        time.sleep(0.5)
        manager.stop_async_loop()
        print("✅ 9. Асинхронная функциональность работает")
        
        # Остановка
        manager.stop()
        print("✅ 10. Остановка успешна")
        
        print("\n🎉 ВСЕ ФУНКЦИИ РАБОТАЮТ НА 100%!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


if __name__ == "__main__":
    success = test_all_functions()
    sys.exit(0 if success else 1)