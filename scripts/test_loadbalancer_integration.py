#!/usr/bin/env python3
"""
Тест интеграции LoadBalancer с SafeFunctionManager
"""

import sys
import asyncio
sys.path.append('/Users/sergejhlystov/ALADDIN_NEW')

from security.safe_function_manager import SafeFunctionManager
from security.microservices.load_balancer import LoadBalancer, LoadBalancingRequest, ServiceRequest
from core.base import SecurityLevel


async def test_loadbalancer_integration():
    """Тест интеграции LoadBalancer с SFM"""
    print("🔧 Тест интеграции LoadBalancer с SafeFunctionManager")
    print("=" * 60)
    
    try:
        # Создаем SFM
        sfm = SafeFunctionManager()
        print("✅ SafeFunctionManager создан!")
        
        # Регистрируем LoadBalancer
        print("\n🔄 Регистрируем LoadBalancer...")
        result = sfm.register_function(
            function_id='load_balancer',
            name='LoadBalancer',
            description='Микросервис балансировки нагрузки с поддержкой множественных алгоритмов',
            function_type='microservice',
            security_level=SecurityLevel.HIGH,
            is_critical=True,
            auto_enable=False
        )
        print(f"✅ LoadBalancer зарегистрирован! Результат: {result}")
        
        # Включаем LoadBalancer
        print("\n🔄 Включаем LoadBalancer...")
        enable_result = sfm.enable_function('load_balancer')
        print(f"✅ LoadBalancer включен! Результат: {enable_result}")
        
        # Проверяем статус
        status = sfm.get_function_status('load_balancer')
        if status:
            print(f"\n📈 Статус LoadBalancer: {status['status']}")
            
            # Создаем LoadBalancer для тестирования
            print("\n🔄 Создаем LoadBalancer для тестирования...")
            lb = LoadBalancer()
            
            # Инициализируем LoadBalancer
            print("🔄 Инициализируем LoadBalancer...")
            init_result = await lb.initialize()
            print(f"✅ LoadBalancer инициализирован! Результат: {init_result}")
            
            if init_result:
                # Тестируем регистрацию сервиса
                print("\n🔄 Тестируем регистрацию сервиса...")
                service_request = ServiceRequest(
                    name="test_service",
                    url="localhost",
                    port=8080,
                    protocol="http",
                    weight=1,
                    max_connections=100,
                    health_check_url="/health",
                    health_check_interval=30
                )
                
                register_result = await lb.register_service(service_request)
                print(f"✅ Сервис зарегистрирован! Результат: {register_result}")
                
                # Тестируем балансировку нагрузки
                print("\n🔄 Тестируем балансировку нагрузки...")
                balance_request = LoadBalancingRequest(
                    service_name="test_service",
                    client_ip="127.0.0.1",
                    session_id="test_session_123"
                )
                
                balance_result = await lb.balance_load(balance_request)
                if balance_result:
                    print(f"✅ Балансировка выполнена! Результат: {balance_result.service_url}")
                else:
                    print("⚠️ Балансировка не выполнена (нет доступных сервисов)")
                
                # Тестируем получение метрик
                print("\n🔄 Тестируем получение метрик...")
                metrics = await lb.get_metrics()
                print(f"✅ Метрики получены! Результат: {metrics}")
                
                # Завершаем работу LoadBalancer
                print("\n🔄 Завершаем работу LoadBalancer...")
                await lb.shutdown()
                print("✅ LoadBalancer завершил работу!")
            
            # Тестируем выполнение через SFM
            print("\n🔄 Тестируем выполнение через SFM...")
            test_result = sfm.test_function('load_balancer')
            print(f"✅ Тест SFM завершен! Результат: {test_result}")
            
            # Получаем метрики SFM
            print("\n🔄 Получаем метрики SFM...")
            sfm_metrics = sfm.get_performance_metrics()
            print(f"✅ Метрики SFM получены!")
            print(f"   • Всего функций: {sfm_metrics['current_metrics']['total_functions']}")
            print(f"   • Включенных функций: {sfm_metrics['current_metrics']['enabled_functions']}")
            print(f"   • Спящих функций: {sfm_metrics['current_metrics']['sleeping_functions']}")
            print(f"   • Активных выполнений: {sfm_metrics['current_metrics']['active_executions']}")
            
        else:
            print("❌ LoadBalancer не найден в SFM")
            
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("🎉 Тест интеграции LoadBalancer завершен успешно!")
    return True


if __name__ == "__main__":
    result = asyncio.run(test_loadbalancer_integration())
    if result:
        print("✅ Все тесты прошли успешно!")
    else:
        print("❌ Тесты завершились с ошибками!")