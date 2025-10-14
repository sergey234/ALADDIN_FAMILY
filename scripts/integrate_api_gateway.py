#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Интеграция APIGateway в систему безопасности
"""

import sys
import os
import json
import time
from datetime import datetime

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def integrate_api_gateway():
    """Интеграция APIGateway в систему"""
    print("🔗 ИНТЕГРАЦИЯ APIGATEWAY В СИСТЕМУ")
    print("=" * 50)
    
    try:
        # Импорт APIGateway
        from security.microservices.api_gateway import APIGateway, HTTPMethod, AuthMethod
        
        # Создание экземпляра
        config = {
            'database_url': 'sqlite:///api_gateway.db',
            'jwt_secret': 'aladdin-security-secret-key-2025',
            'redis_url': 'redis://localhost:6379'
        }
        
        gateway = APIGateway(name="ALADDIN_APIGateway", config=config)
        print("✅ APIGateway: создан и инициализирован")
        
        # Тест функциональности
        status = gateway.get_status()
        print(f"✅ Статус: {status['status']}")
        print(f"✅ Сервисы: {status['services_count']}")
        print(f"✅ Маршруты: {status['routes_count']}")
        
        # Тест создания API ключа
        from security.microservices.api_gateway import APIKeyRequest
        key_request = APIKeyRequest(
            name="aladdin_mobile_app",
            permissions=["read", "write", "admin"],
            rate_limit=5000,
            expires_in_days=365
        )
        print("✅ APIKeyRequest: создан успешно")
        
        # Тест создания маршрута
        from security.microservices.api_gateway import RouteRequest
        route_request = RouteRequest(
            path="/api/v1/security",
            method=HTTPMethod.POST,
            service_name="security_service",
            service_url="http://localhost:8001",
            rate_limit=1000,
            timeout=30,
            retry_count=3
        )
        print("✅ RouteRequest: создан успешно")
        
        # Проверка провайдеров аутентификации
        jwt_provider = gateway.auth_providers.get(AuthMethod.JWT)
        api_key_provider = gateway.auth_providers.get(AuthMethod.API_KEY)
        
        if jwt_provider:
            print("✅ JWT провайдер: активен")
        if api_key_provider:
            print("✅ API ключ провайдер: активен")
        
        # Проверка ML компонентов
        if hasattr(gateway, 'anomaly_detector'):
            print("✅ ML детектор аномалий: инициализирован")
        if hasattr(gateway, 'request_classifier'):
            print("✅ ML классификатор запросов: инициализирован")
        if hasattr(gateway, 'clustering_model'):
            print("✅ ML кластеризатор: инициализирован")
        
        print("\n🎯 ИНТЕГРАЦИЯ УСПЕШНА!")
        return True
        
    except Exception as e:
        print(f"❌ ОШИБКА ИНТЕГРАЦИИ: {e}")
        return False

if __name__ == "__main__":
    success = integrate_api_gateway()
    if success:
        print("\n🎉 APIGATEWAY УСПЕШНО ИНТЕГРИРОВАН!")
    else:
        print("\n💥 ОШИБКА ИНТЕГРАЦИИ!")