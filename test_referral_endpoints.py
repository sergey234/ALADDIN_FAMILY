#!/usr/bin/env python3
"""Тестирование referral endpoint'ов с реальным токеном"""
import requests
import json

BASE_URL = "http://149.154.65.180:8002"

# Создаем семью
print("1. Создание семьи...")
response = requests.post(
    f"{BASE_URL}/api/family/create",
    json={
        "role": "parent",
        "age_group": "24-55",
        "personal_letter": "T",
        "device_type": "iOS"
    }
)

if response.status_code == 200:
    family_data = response.json()
    family_id = family_data.get("family_id")
    print(f"   ✅ Family ID: {family_id}")
    
    # Получаем токен
    print("2. Получение токена...")
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login-by-recovery-code",
        json={
            "family_id": family_id,
            "recovery_code": family_id
        }
    )
    
    if login_response.status_code == 200:
        token_data = login_response.json()
        token = token_data.get("access_token")
        print(f"   ✅ Token получен")
        
        # Тестируем referral endpoints
        print("\n3. Тестирование referral endpoints:")
        endpoints = [
            "/api/referral/code",
            "/api/referral/stats",
            "/api/referral/history",
            "/api/referral/rewards"
        ]
        
        for endpoint in endpoints:
            resp = requests.get(
                f"{BASE_URL}{endpoint}",
                headers={"Authorization": f"Bearer {token}"}
            )
            status = "✅" if resp.status_code == 200 else "❌"
            print(f"   {status} {endpoint}: {resp.status_code}")
            if resp.status_code != 200:
                print(f"      Ошибка: {resp.text[:200]}")
    else:
        print(f"   ❌ Ошибка авторизации: {login_response.status_code}")
        print(f"      {login_response.text}")
else:
    print(f"❌ Ошибка создания семьи: {response.status_code}")
    print(f"   {response.text}")
