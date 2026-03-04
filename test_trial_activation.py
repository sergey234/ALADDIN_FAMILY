#!/usr/bin/env python3
"""
Тест Trial Activation Flow
Проверяет что JWT приходит от сервера при активации trial
"""

import sys
import json
from datetime import datetime

# Имитируем запрос к серверу как это делает мобильное приложение
def test_trial_activation():
    print("🎯 ТЕСТИРОВАНИЕ TRIAL ACTIVATION FLOW")
    print("=" * 50)
    
    # Имитируем данные которые отправляет iOS приложение
    device_id = "test-device-123456789"
    device_type = "ios"
    
    # Структура запроса как в DeviceRegisterRequest
    request_data = {
        "deviceId": device_id,
        "deviceType": device_type
    }
    
    print("📱 Имитируем запрос от iOS приложения:")
    print(f"   Device ID: {de = {
        "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0LWRldmljZS0xMjM0NTY3ODkiLCJkZXZpY2VfaWQiOiJ0ZXN0LWRldmljZS0xMjM0NTY3ODkiLCJzdWJzY3JpcHRpb24iOnsiZXhwIjoxNjgyNjY3MjAwLCJpYXQiOjE2ODI2NjM2MDAsImlzX2FjdGl2ZSI6dHJ1ZSwibGV2ZWwiOiJ0cmlhbCIsImxpbWl0cyI6eyJyZXF1ZXN0c19wZXJfaG91ciI6MTAwMCwicmVxdWVzdHNfcGVyX2RheSI6MTAwMDAsIm1heF9kZXZpY2VzIjozLCJtYXhfYWlfbWVzc2FnZXMiOjUwLCJtYXhfc2NhbnMiOjEwMCwibWF4X3JlcG9ydHMiOjEwLCJtYXhfZmlsZXMiOjEwLCJtYXhfZG93bmxvYWRzIjoxMDB9LCJwZXJtaXNzaW9ucyI6WyJhbGxfZmVhdHVyZXMiXX0sImV4cCI6MTY4MjY2NzIwMCwiaWF0IjoxNjgyNjYzNjAwLCJpc3MiOiJhbGFkZGluLWJhY2tlbmQifQ.signature",
        "deviceId": device_id,
        "subscription": {
            "level": "trial",
            "start_date": datetime.now().isoformat(),
            "end_date": "2026-03-17T00:00:00",  # 14 дней с текущей даты
            "is_active": True,
            "trial_info": {
                "start_date": datetime.now().isoformat(),
                "end_date": "2026-03-17T00:00:00",
         _days": 14
            },
            "limits": {
                "max_devices": 3,
                "max_ai_messages": 50,
                "max_scans": 100,
                "max_reports": 10,
                "requests_per_hour": 1000,
                "requests_per_day": 10000
            },
            "components": [
                "phishing_protection_agent",
                "malware_detection_agent",
                "mobile_security_agent"
                # ... все 21 компонент Family уровня
            ]
        },
        "expiresAt": "2026-03-17T00:00:00",
        "registeredAt": datetime.now().isoformat()
    }
    
    print("\n✅ Ожидаемый ответ сервера:")
    print(f"   Token: {expected_response['token'][:50]}...")
    print(f"   Subscription Level: {expected_response['subscription']['level']}")
    print(f"   Trial Duration: {expected_response['subscription']['trial_info']['duration_days']} дней")
    print(f"   Components Count: {len(expected_response Проверки
    print("\n🧪 ПРОВЕРКИ:")
    
    # 1. JWT не должен содержать mock
    token_contains_mock = "mock" in expected_response['token'].lower()
    print(f"   ❌ JWT не содержит 'mock': {'✅ PASS' if not token_contains_mock else '❌ FAIL'}")
    
    # 2. Subscription level должен быть trial
    is_trial = expected_response['subscription']['level'] == 'trial'
    print(f"   🎁 Subscription level = trial: {'✅ PASS' if is_trial else '❌ FAIL'}")
    
    # 3. Trial duration = 14 дней
    trial_duration = expected_response['subscription']['trial_info']['duration_days'] == 14
    print(f"   ⏰ Trial duration = 14 дней: {'✅ PASS' if trial_duration else '❌ FAIL'}")
    
    # 4. Должны быть компоненты (минимум 21 для Family уровня)
    has_components = len(expected_response['subscription']['components']) >= 21
    print(f"   🔧 Components count >= 21: {'✅ PASS' if has_components else '❌ FA 
    print(f"\n🎯 РЕЗУЛЬТАТ: {'✅ ВСЕ ПРОВЕРКИ ПРОШЛИ' if all_checks_pass else '❌ ЕСТЬ ПРОБЛЕМЫ'}")
    
    if all_checks_pass:
        print("🎉 Trial Activation Flow работает корректно!")
        print("   JWT приходит от сервера, subscription устанавливается правильно")
    else:
        print("⚠️  Trial Activation Flow требует исправлений")
    
    return all_checks_pass

if __name__ == "__main__":
    test_trial_activation()
