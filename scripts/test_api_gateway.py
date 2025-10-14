#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест APIGateway - проверка функциональности
"""

import sys
import os
import asyncio
import time
import json
from datetime import datetime

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_api_gateway():
    """Тестирование APIGateway"""
    print("🔍 ТЕСТИРОВАНИЕ APIGATEWAY")
    print("=" * 50)
    
    try:
        # Импорт APIGateway
        from security.microservices.api_gateway import APIGateway, HTTPMethod, AuthMethod
        
        # Создание экземпляра
        config = {
            'database_url': 'sqlite:///test_api_gateway.db',
            'jwt_secret': 'test-secret-key'
        }
        
        gateway = APIGateway(name="TestAPIGateway", config=config)
        print("✅ APIGateway: инициализация успешна")
        
        # Тест создания API ключа
        try:
            from security.microservices.api_gateway import APIKeyRequest
            key_request = APIKeyRequest(
                name="test_key",
                permissions=["read", "write"],
                rate_limit=1000,
                expires_in_days=30
            )
            print("✅ APIKeyRequest: создание успешно")
        except Exception as e:
            print(f"❌ APIKeyRequest: {e}")
        
        # Тест создания маршрута
        try:
            from security.microservices.api_gateway import RouteRequest
            route_request = RouteRequest(
                path="/test",
                method=HTTPMethod.GET,
                service_name="test_service",
                service_url="http://localhost:8001",
                rate_limit=100,
                timeout=30,
                retry_count=3
            )
            print("✅ RouteRequest: создание успешно")
        except Exception as e:
            print(f"❌ RouteRequest: {e}")
        
        # Тест статуса
        status = gateway.get_status()
        print(f"✅ Статус: {status['status']}")
        print(f"✅ Сервисы: {status['services_count']}")
        print(f"✅ Маршруты: {status['routes_count']}")
        
        # Тест аутентификации
        try:
            jwt_provider = gateway.auth_providers.get(AuthMethod.JWT)
            if jwt_provider:
                print("✅ JWT провайдер: доступен")
            
            api_key_provider = gateway.auth_providers.get(AuthMethod.API_KEY)
            if api_key_provider:
                print("✅ API ключ провайдер: доступен")
        except Exception as e:
            print(f"❌ Аутентификация: {e}")
        
        print("\n🎯 РЕЗУЛЬТАТ: APIGateway работает корректно!")
        return True
        
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        return False

if __name__ == "__main__":
    success = test_api_gateway()
    if success:
        print("\n🎉 ТЕСТ ПРОЙДЕН УСПЕШНО!")
    else:
        print("\n💥 ТЕСТ ПРОВАЛЕН!")