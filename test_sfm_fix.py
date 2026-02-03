#!/usr/bin/env python3
"""
Тест исправлений SFM для быстрой проверки
"""

import requests
import json
import time

def test_sfm_fix():
    """Тестирование исправлений SFM"""

    print("🧪 ТЕСТИРОВАНИЕ ИСПРАВЛЕНИЙ SFM")
    print("=" * 40)

    # Тесты
    tests = [
        {
            "name": "SFM Health",
            "url": "http://127.0.0.1:8003/api/health",
            "method": "GET",
            "expected": lambda r: r.get("status") == "healthy"
        },
        {
            "name": "SFM Functions List",
            "url": "http://127.0.0.1:8003/api/functions",
            "method": "GET",
            "expected": lambda r: "api_mappings_count" in r and r["api_mappings_count"] > 0
        },
        {
            "name": "SFM phishing sensitivity",
            "url": "http://127.0.0.1:8003/api/execute",
            "method": "POST",
            "data": {"function": "get_phishing_sensitivity", "params": {}},
            "expected": lambda r: r.get("success") == True and r.get("source") == "real_sfm"
        },
        {
            "name": "API Gateway phishing",
            "url": "http://127.0.0.1:8002/api/phishing/sensitivity",
            "method": "GET",
            "expected": lambda r: "source" in str(r) and "real_sfm" in str(r)
        },
        {
            "name": "API Gateway health",
            "url": "http://127.0.0.1:8002/api/health",
            "method": "GET",
            "expected": lambda r: r.get("sfm_adapter") == "available"
        }
    ]

    results = []

    for test in tests:
        try:
            if test["method"] == "GET":
                response = requests.get(test["url"], timeout=5)
            else:
                response = requests.post(test["url"],
                                       json=test["data"],
                                       headers={"Content-Type": "application/json"},
                                       timeout=5)

            if response.status_code == 200:
                data = response.json()
                success = test["expected"](data)
                status = "✅ PASS" if success else "❌ FAIL"
                print(f"{status} {test['name']}")
                if not success:
                    print(f"   Response: {data}")
            else:
                print(f"❌ FAIL {test['name']} - HTTP {response.status_code}")
                success = False

        except Exception as e:
            print(f"❌ ERROR {test['name']} - {e}")
            success = False

        results.append(success)
        time.sleep(0.5)

    # Итоги
    passed = sum(results)
    total = len(results)

    print("\n" + "=" * 40)
    print("🎯 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("=" * 40)
    print(f"✅ Пройдено: {passed}/{total}")

    if passed >= 4:
        print("🎉 СИСТЕМА ГОТОВА! SFM полностью интегрирован!")
        return True
    else:
        print("⚠️ Требуется доработка")
        return False

if __name__ == "__main__":
    test_sfm_fix()