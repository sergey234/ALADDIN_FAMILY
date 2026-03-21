#!/usr/bin/env python3
"""
Проверка соответствия секретов для создания и декодирования токена
"""

import requests
import jwt
import os

BASE_URL = "https://aladdin-ai.ru"
DEVICE_ID = "verify_secret_device"

# Получаем токен
print("🔑 Получение токена с сервера...")
response = requests.post(
    f"{BASE_URL}/api/auth/register-device",
    json={"device_id": DEVICE_ID, "device_type": "ios"},
    timeout=30
)

if response.status_code not in [200, 201]:
    print(f"❌ Ошибка: {response.status_code}")
    sys.exit(1)

token = response.json().get("token") or response.json().get("access_token")
print(f"✅ Токен получен: {token[:30]}...{token[-30:]}")
print()

# Пробуем декодировать с разными секретами
secrets = [
    ("your-secret-key-change-in-production", "Старый секрет из app/auth/auth.py"),
    ("aladdin-super-secret-key-change-in-production", "Новый унифицированный секрет"),
]

print("🔍 Попытка декодирования токена с разными секретами:")
print()

for secret, description in secrets:
    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            options={"verify_signature": True}
        )
        print(f"✅ {description}")
        print(f"   Секрет: {secret[:20]}...")
        print(f"   Декодирован успешно!")
        print(f"   Payload: {payload.get('sub', 'N/A')}")
        print()
    except jwt.ExpiredSignatureError:
        print(f"⚠️ {description}: Токен истек")
        print()
    except jwt.InvalidTokenError as e:
        print(f"❌ {description}: Невалидный токен - {str(e)[:50]}")
        print()
    except Exception as e:
        print(f"❌ {description}: Ошибка - {str(e)[:50]}")
        print()

print("💡 Если ни один секрет не работает, возможно:")
print("   1. Токен создан с другим секретом")
print("   2. На сервере используется переменная окружения JWT_SECRET")
print("   3. Токен поврежден или имеет неправильный формат")
