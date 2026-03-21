#!/usr/bin/env python3
"""
Диагностика проблемы 401 на конкретном эндпоинте
"""

import requests
import sys

BASE_URL = "https://aladdin-ai.ru"
DEVICE_ID = "diagnose_401_device"

# Получаем токен
print("🔑 Получение токена...")
response = requests.post(
    f"{BASE_URL}/api/auth/register-device",
    json={"device_id": DEVICE_ID, "device_type": "ios"},
    timeout=30
)

if response.status_code not in [200, 201]:
    print(f"❌ Ошибка регистрации: {response.status_code} - {response.text}")
    sys.exit(1)

token = response.json().get("token") or response.json().get("access_token")
if not token:
    print("❌ Токен не найден в ответе")
    sys.exit(1)

print(f"✅ Токен получен: {token[:30]}...{token[-30:]}")
print(f"   Длина: {len(token)} символов")
print()

# Тестируем проблемный эндпоинт
test_endpoint = "/api/components/status/crash_detection_agent"
print(f"🧪 Тестирование: {test_endpoint}")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

response = requests.get(
    f"{BASE_URL}{test_endpoint}",
    headers=headers,
    timeout=15
)

print(f"📊 Статус: {response.status_code}")
print(f"📋 Заголовки ответа:")
for key, value in response.headers.items():
    if key.lower() in ['www-authenticate', 'content-type']:
        print(f"   {key}: {value}")

print(f"📄 Тело ответа:")
try:
    print(f"   {response.json()}")
except:
    print(f"   {response.text[:500]}")

print()
print("💡 Проверьте логи сервера для детальной информации о декодировании токена")
