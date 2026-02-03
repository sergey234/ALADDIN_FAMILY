#!/usr/bin/env python3
"""
🎯 ДЕТАЛЬНЫЙ АУДИТ ВСЕХ ENDPOINTS
Проверяет каждый endpoint с полными данными
"""

import requests
import time
import json
from datetime import datetime

BASE_URL = "https://aladdin-ai.ru/api"

def test_endpoint(name, url, method="GET", data=None):
    """Тестирует endpoint и возвращает полный результат"""
    print(f"\n🔍 ТЕСТИРОВАНИЕ: {name}")
    print(f"📍 URL: {url}")
    print(f"📝 Метод: {method}")

    start_time = time.time()

    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            response = requests.get(url, timeout=10)

        end_time = time.time()
        response_time = round((end_time - start_time) * 1000, 2)  # в миллисекундах

        print(f"📊 СТАТУС: {response.status_code}")
        print(f"⏱️ ВРЕМЯ ОТВЕТА: {response_time}ms")

        try:
            json_data = response.json()
            print(f"📄 JSON ОТВЕТ: {json.dumps(json_data, indent=2, ensure_ascii=False)[:200]}...")
        except:
            print(f"📄 ТЕКСТ ОТВЕТ: {response.text[:200]}...")

        return {
            "name": name,
            "url": url,
            "method": method,
            "status_code": response.status_code,
            "response_time_ms": response_time,
            "success": response.status_code == 200,
            "response_preview": str(response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text)[:100]
        }

    except Exception as e:
        end_time = time.time()
        response_time = round((end_time - start_time) * 1000, 2)
        print(f"❌ ОШИБКА: {e}")
        print(f"⏱️ ВРЕМЯ: {response_time}ms")

        return {
            "name": name,
            "url": url,
            "method": method,
            "status_code": None,
            "response_time_ms": response_time,
            "success": False,
            "error": str(e)
        }

def main():
    print("🎯 ДЕТАЛЬНЫЙ АУДИТ ВСЕХ ENDPOINTS ALADDIN API")
    print("=" * 60)
    print(f"🕐 ВРЕМЯ НАЧАЛА: {datetime.now()}")
    print(f"🌐 БАЗОВЫЙ URL: {BASE_URL}")

    # Группа 1: COMPONENTS
    endpoints = [
        # HEALTH
        ("Health Check", f"{BASE_URL}/health"),

        # COMPONENTS
        ("Component: crash_detection_agent", f"{BASE_URL}/components/status/crash_detection_agent"),
        ("Component: emergency_response_agent", f"{BASE_URL}/components/status/emergency_response_agent"),
        ("Component: phishing_protection_agent", f"{BASE_URL}/components/status/phishing_protection_agent"),

        # SECURITY
        ("Security: Phishing Sensitivity", f"{BASE_URL}/phishing/sensitivity"),
        ("Security: Malware Scan", f"{BASE_URL}/malware/scan_scheduled"),
        ("Security: Mobile App Lock", f"{BASE_URL}/mobile/app_lock"),
        ("Security: Network Firewall", f"{BASE_URL}/network/firewall_rules"),

        # MONITORING
        ("Monitoring: AI Categories Stats", f"{BASE_URL}/ai/categories/stats"),
        ("Monitoring: Location Stats", f"{BASE_URL}/location/stats"),
        ("Monitoring: Data Cleanup Stats", f"{BASE_URL}/data/cleanup/stats"),

        # PROTECTION
        ("Protection: Dark Web Leaks", f"{BASE_URL}/darkweb/leaks"),
        ("Protection: Identity Theft Stats", f"{BASE_URL}/identity/theft/stats"),
        ("Protection: Anti-Tracker", f"{BASE_URL}/antitracker/trackers"),

        # ANALYTICS (которые работают)
        ("Analytics: Overview", f"{BASE_URL}/analytics/overview"),
        ("Analytics: Security Events", f"{BASE_URL}/analytics/security_events"),
        ("Analytics: Performance", f"{BASE_URL}/analytics/performance"),

        # AUTH
        ("Auth: Login", f"{BASE_URL}/auth/login", "POST", {"email": "test@example.com", "password": "test123"}),
    ]

    results = []
    total_tests = len(endpoints)
    successful_tests = 0

    print(f"\n📊 ВСЕГО ТЕСТОВ: {total_tests}")
    print("🚀 НАЧИНАЕМ ТЕСТИРОВАНИЕ...")
    for endpoint in endpoints:
        if len(endpoint) == 2:
            name, url = endpoint
            method = "GET"
            data = None
        else:
            name, url, method, data = endpoint

        result = test_endpoint(name, url, method, data)
        results.append(result)

        if result["success"]:
            successful_tests += 1

    # ИТОГИ
    print("\n" + "=" * 60)
    print("📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ АУДИТА")
    print("=" * 60)

    print(f"✅ УСПЕШНЫХ ТЕСТОВ: {successful_tests}/{total_tests}")
    print(f"❌ НЕУДАЧНЫХ ТЕСТОВ: {total_tests - successful_tests}")
    print(".1f"
    print(f"🎯 ПРОЦЕНТ УСПЕХА: {(successful_tests/total_tests)*100:.1f}%")

    # Детальный отчет по группам
    print("
📋 РЕЗУЛЬТАТЫ ПО ГРУППАМ:"    groups = {
        "Health": ["Health Check"],
        "Components": ["Component:"],
        "Security": ["Security:"],
        "Monitoring": ["Monitoring:"],
        "Protection": ["Protection:"],
        "Analytics": ["Analytics:"],
        "Auth": ["Auth:"]
    }

    for group_name, prefixes in groups.items():
        group_results = [r for r in results if any(prefix in r["name"] for prefix in prefixes)]
        group_success = sum(1 for r in group_results if r["success"])
        print(f"🟢 {group_name}: {group_success}/{len(group_results)} успешных")

    # Сохранение полного отчета
    report_file = "AUDIT_REPORT_DETAIL.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "base_url": BASE_URL,
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": f"{(successful_tests/total_tests)*100:.1f}%",
            "results": results
        }, f, indent=2, ensure_ascii=False)

    print(f"\n💾 ПОЛНЫЙ ОТЧЕТ СОХРАНЕН: {report_file}")

    # Финальный вердикт
    if successful_tests == total_tests:
        print("\n🎉 ВЕРДИКТ: ВСЕ ENDPOINTS РАБОТАЮТ! ПРОДАКШЕН ГОТОВ!")
    elif successful_tests >= total_tests * 0.8:
        print("\n⚠️ ВЕРДИКТ: БОЛЬШИНСТВО ENDPOINTS РАБОТАЕТ! ПРОДАКШЕН ГОТОВ!")
    else:
        print("\n❌ ВЕРДИКТ: МНОГИЕ ENDPOINTS НЕ РАБОТАЮТ! ТРЕБУЕТСЯ ДОРАБОТКА!")

    print(f"\n🕐 ВРЕМЯ ОКОНЧАНИЯ АУДИТА: {datetime.now()}")

if __name__ == "__main__":
    main()