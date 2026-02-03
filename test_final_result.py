#!/usr/bin/env python3
"""
ПРОСТОЙ ТЕСТ ФИНАЛЬНОГО РЕЗУЛЬТАТА
"""

import requests
import json

def test_final_result():
    """Простой тест финального результата"""

    print("🎯 ТЕСТ ФИНАЛЬНОГО РЕЗУЛЬТАТА")
    print("=" * 40)

    try:
        # Health check
        response = requests.get("http://127.0.0.1:8002/api/health", timeout=5)
        health = response.json()

        print(f"Health check: {health.get('sfm_adapter', 'unknown')}")

        if health.get('sfm_adapter') == 'available':
            print("✅ SFM адаптер работает!")
        else:
            print("❌ SFM адаптер в fallback")
            return

        # Test functions
        functions = [
            ("http://127.0.0.1:8002/api/phishing/sensitivity", "Phishing"),
            ("http://127.0.0.1:8002/api/analytics/overview", "Analytics"),
            ("http://127.0.0.1:8002/api/components/health", "Components")
        ]

        real_sfm_count = 0

        for url, name in functions:
            try:
                response = requests.get(url, timeout=5)
                data = response.json()

                if isinstance(data, dict) and data.get('source') == 'real_sfm':
                    print(f"✅ {name}: real_sfm")
                    real_sfm_count += 1
                else:
                    print(f"❌ {name}: не real_sfm")
                    print(f"   Данные: {str(data)[:100]}...")
            except Exception as e:
                print(f"❌ {name}: ошибка - {e}")

        print("\n" + "=" * 40)
        if real_sfm_count >= 2:
            print("🎉 УСПЕХ! ALADDIN имеет РЕАЛЬНУЮ ЗАЩИТУ!")
            print(f"✅ {real_sfm_count}/3 функций возвращают real_sfm")
        else:
            print(f"⚠️ Частичный успех: {real_sfm_count}/3 функций")

    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        print("Убедитесь что:")
        print("1. Сервер запущен")
        print("2. API Gateway работает на порту 8002")
        print("3. SFM HTTP API работает на порту 8003")

if __name__ == "__main__":
    test_final_result()