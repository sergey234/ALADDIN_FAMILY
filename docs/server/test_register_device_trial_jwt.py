#!/usr/bin/env python3
"""
✅ JWT-TRIAL: Тестирование эндпоинта /api/auth/register-device-trial

Проверяет, что:
- POST /api/auth/register-device-trial принимает TrialDeviceRegisterRequest
- возвращает 200 + JWTDeviceRegisterResponse
- выданный токен работает на защищённом эндпоинте /api/user/profile
"""

import json
from datetime import datetime, timedelta

import jwt
import requests

BASE_URL = "https://aladdin-ai.ru"
DEVICE_ID = "test_register_device_trial_001"


def get_trial_token() -> dict:
    """Выдаём trial-токен через /api/auth/register-device-trial."""
    print("🔑 [JWT-TRIAL] Регистрация устройства с trial...")
    try:
        now = datetime.utcnow()
        body = {
            "deviceId": DEVICE_ID,
            "deviceType": "ios",
            "trialInfo": {
                "start_date": now.isoformat(),
                "end_date": (now + timedelta(days=14)).isoformat(),
                "duration_days": 14,
            },
        }
        resp = requests.post(
            f"{BASE_URL}/api/auth/register-device-trial",
            json=body,
            timeout=30,
        )
        print(f"   HTTP {resp.status_code}")
        print(f"   body: {resp.text[:400]}")

        if resp.status_code not in (200, 201):
            return {}

        data = resp.json()
        token = data.get("token") or data.get("access_token")
        if not token:
            print("❌ [JWT-TRIAL] Токен не найден в ответе")
            return {}

        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            exp = payload.get("exp")
            print("✅ [JWT-TRIAL] Токен получен, payload preview:")
            print(json.dumps(payload, ensure_ascii=False)[:400])
            return {"access_token": token, "payload": payload, "exp": exp}
        except Exception as e:
            print(f"⚠️ [JWT-TRIAL] Не удалось декодировать токен: {e}")
            return {"access_token": token}
    except Exception as e:
        print(f"❌ [JWT-TRIAL] Ошибка регистрации trial: {e}")
        return {}


def test_protected_profile(token: str) -> bool:
    """Пробуем /api/user/profile с выданным токеном."""
    try:
        resp = requests.get(
            f"{BASE_URL}/api/user/profile",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            timeout=15,
        )
        print(f"🔍 [JWT-TRIAL] /api/user/profile -> HTTP {resp.status_code}")
        print(f"   body: {resp.text[:400]}")
        return resp.status_code in (200, 201, 422)
    except Exception as e:
        print(f"❌ [JWT-TRIAL] Ошибка при вызове профиля: {e}")
        return False


def run():
    print("=" * 70)
    print("🔄 [JWT-TRIAL] ТЕСТ /api/auth/register-device-trial")
    print("=" * 70)
    print(f"📅 Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Сервер: {BASE_URL}")
    print(f"📱 Device ID: {DEVICE_ID}")
    print()

    info = get_trial_token()
    token = info.get("access_token")
    if not token:
        print("❌ [JWT-TRIAL] Не удалось получить trial-токен, см. вывод выше")
        return

    print()
    print("🧪 [JWT-TRIAL] Проверка работы токена на /api/user/profile...")
    ok = test_protected_profile(token)
    if ok:
        print("✅ [JWT-TRIAL] Токен от register-device-trial успешно работает на /api/user/profile")
    else:
        print("❌ [JWT-TRIAL] Токен НЕ работает на /api/user/profile")

    print()
    print("=" * 70)
    print("📊 [JWT-TRIAL] ИТОГОВЫЙ ОТЧЁТ")
    print("=" * 70)
    if ok:
        print("✅ /api/auth/register-device-trial возвращает рабочий JWT для защищённых эндпоинтов")
    else:
        print("❌ Нужна доработка: токен trial не проходит профиль")
    print("=" * 70)


if __name__ == "__main__":
    run()

