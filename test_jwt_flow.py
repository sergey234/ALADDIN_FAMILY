import requests
import sys

BASE_URL = "http://149.154.65.180:8002"
DEVICE_ID = "test_device_jwt_001"
DEVICE_TYPE = "mobile"

def print_step(step, msg):
    print(f"\n🔹 ШАГ {step}: {msg}")

def run_test():
    print("🚀 ЗАПУСК JWT TEST FLOW")
    
    # 1. Регистрация
    print_step(1, f"Регистрация устройства {DEVICE_ID}...")
    try:
        resp = requests.post(f"{BASE_URL}/api/auth/register", json={
            "device_id": DEVICE_ID,
            "device_type": DEVICE_TYPE
        })
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            print("✅ Регистрация успешна!")
            token = resp.json().get("access_token")
            print(f"Token: {token[:20]}...")
        else:
            print(f"❌ Ошибка регистрации: {resp.text}")
            return
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return

    # 2. Аутентификация (Login)
    print_step(2, "Вход (Login)...")
    resp = requests.post(f"{BASE_URL}/api/auth/login", json={
        "device_id": DEVICE_ID
    })
    if resp.status_code == 200:
        print("✅ Вход успешен!")
        token = resp.json().get("access_token")
    else:
        print(f"❌ Ошибка входа: {resp.text}")
        return

    # 3. Доступ к защищенному ресурсу
    print_step(3, "Доступ к защищенному эндпоинту (Protection Status)...")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/api/protection/status", headers=headers)
    
    if resp.status_code == 200:
        print("✅ Доступ разрешен!")
        print(f"Ответ: {resp.json()}")
    elif resp.status_code == 401:
        print("❌ Ошибка 401: Токен не принят")
    elif resp.status_code == 403:
        print("❌ Ошибка 403: Доступ запрещен")
    else:
        print(f"❌ Ошибка: {resp.status_code} {resp.text}")

    # 4. Проверка отказа в доступе без токена
    print_step(4, "Проверка доступа БЕЗ токена...")
    resp = requests.get(f"{BASE_URL}/api/protection/status")
    if resp.status_code == 401:
        print("✅ Доступ корректно запрещен (401 Unauthorized)")
    else:
        print(f"❌ Ошибка: Ожидался 401, получен {resp.status_code}")

    print("\n🎉 JWT ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")

if __name__ == "__main__":
    run_test()
