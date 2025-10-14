#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование LoadBalancer
"""

import sys
import os
import asyncio
import time
from datetime import datetime

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_load_balancer():
    """Тестирование LoadBalancer"""
    print("🧪 ТЕСТИРОВАНИЕ LOADBALANCER")
    print("=" * 50)
    
    try:
        # Импорт LoadBalancer
        from security.microservices.load_balancer import (
            LoadBalancer, 
            LoadBalancingAlgorithm, 
            ServiceRequest, 
            LoadBalancingRequest
        )
        
        # Создание экземпляра
        lb = LoadBalancer(name="TestLoadBalancer")
        print("✅ LoadBalancer: создан и инициализирован")
        
        # Тест статуса
        status = lb.get_status()
        print(f"✅ Статус: {status['status']}")
        print(f"✅ Алгоритмы: {status['algorithms_count']}")
        print(f"✅ Сервисы: {status['services_count']}")
        
        # Тест создания запроса
        request = LoadBalancingRequest(
            service_name="test_services",
            algorithm=LoadBalancingAlgorithm.ROUND_ROBIN,
            client_ip="192.168.1.100",
            session_id="test_session_123",
            priority=5,
            timeout=30,
            retry_count=3
        )
        print("✅ LoadBalancingRequest: создан успешно")
        
        # Тест создания запроса сервиса
        service_request = ServiceRequest(
            name="test_service_1",
            url="http://localhost",
            port=8001,
            protocol="http",
            weight=10,
            max_connections=1000,
            health_check_url="/health",
            health_check_interval=30
        )
        print("✅ ServiceRequest: создан успешно")
        
        # Проверка алгоритмов
        algorithms = lb.algorithms
        print(f"✅ Доступные алгоритмы: {list(algorithms.keys())}")
        
        for name, algorithm in algorithms.items():
            print(f"  - {name}: {algorithm.get_algorithm_description()}")
        
        print("\n🎯 ТЕСТИРОВАНИЕ УСПЕШНО!")
        return True
        
    except Exception as e:
        print(f"❌ ОШИБКА ТЕСТИРОВАНИЯ: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_load_balancer())
    if success:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
    else:
        print("\n💥 ТЕСТЫ НЕ ПРОШЛИ!")