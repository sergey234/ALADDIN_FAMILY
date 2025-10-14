#!/usr/bin/env python3
"""
Тест интеграции APIGateway с SafeFunctionManager
"""

import asyncio
import uuid
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import sys
import os
sys.path.insert(0, '/Users/sergejhlystov/ALADDIN_NEW')

from security.safe_function_manager import SafeFunctionManager, SecurityLevel
from security.microservices.api_gateway import APIGateway, RouteConfig, AuthMethod


async def run_integration_test():
    """Запуск теста интеграции APIGateway с SFM"""
    print("🔧 Тест интеграции APIGateway с SafeFunctionManager")
    print("============================================================")
    
    # Создаем SFM
    sfm = SafeFunctionManager(name="ALADDIN")
    print("✅ SafeFunctionManager создан!")
    
    # Регистрируем APIGateway в SFM
    registration_success = sfm.register_function(
        function_id="api_gateway",
        name="APIGateway",
        description="API шлюз системы безопасности с маршрутизацией и аутентификацией",
        function_type="microservice",
        security_level=SecurityLevel.HIGH,
        is_critical=True,
        auto_enable=False
    )
    print(f"✅ APIGateway зарегистрирован! Результат: {registration_success}")
    
    # Включаем APIGateway
    enable_success = sfm.enable_function("api_gateway")
    print(f"✅ APIGateway включен! Результат: {enable_success}")
    
    # Получаем статус
    gateway_status = sfm.get_function_status("api_gateway")
    print(f"\n📈 Статус APIGateway: {gateway_status['status']}")
    
    # Создаем экземпляр APIGateway
    gateway = APIGateway(
        database_url="sqlite:///test_api_gateway.db",
        redis_url="redis://localhost:6379/0"
    )
    print("✅ APIGateway создан!")
    
    # Инициализируем
    init_success = await gateway.initialize()
    print(f"✅ APIGateway инициализирован! Результат: {init_success}")
    
    # Регистрируем тестовый маршрут
    test_route = RouteConfig(
        path="/test",
        method="GET",
        target_service="test_service",
        target_url="http://localhost:8000",
        auth_required=False,
        auth_method=AuthMethod.NONE,
        rate_limit=100,
        timeout=30,
        cache_ttl=300,
        is_active=True
    )
    
    route_success = await gateway.register_route(test_route)
    print(f"✅ Тестовый маршрут зарегистрирован! Результат: {route_success}")
    
    # Получаем метрики
    metrics = await gateway.get_metrics()
    print(f"✅ Метрики получены! Результат: {metrics}")
    print(f"   • Активных соединений: {metrics.get('active_connections', 0)}")
    print(f"   • Всего маршрутов: {metrics.get('total_routes', 0)}")
    print(f"   • Активных маршрутов: {metrics.get('active_routes', 0)}")
    
    # Завершаем работу
    await gateway.shutdown()
    print("✅ APIGateway завершил работу!")
    
    # Тестируем через SFM
    sfm_test_result = sfm.test_function("api_gateway")
    print(f"✅ Тест SFM завершен! Результат: {sfm_test_result}")
    
    # Получаем метрики SFM
    sfm_metrics = sfm.get_performance_metrics()
    print("✅ Метрики SFM получены!")
    print(f"   • Всего функций: {sfm_metrics['current_metrics']['total_functions']}")
    print(f"   • Включенных функций: {sfm_metrics['current_metrics']['enabled_functions']}")
    print(f"   • Спящих функций: {sfm_metrics['current_metrics']['sleeping_functions']}")
    print(f"   • Активных выполнений: {sfm_metrics['current_metrics']['active_executions']}")
    
    print("\n============================================================")
    print("🎉 Тест интеграции APIGateway завершен успешно!")
    
    if registration_success and enable_success and init_success:
        print("✅ Все тесты прошли успешно!")
        return True
    else:
        print("❌ Некоторые тесты провалились.")
        return False


if __name__ == "__main__":
    asyncio.run(run_integration_test())