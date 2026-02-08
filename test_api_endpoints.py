#!/usr/bin/env python3
"""
🧪 API Endpoints Testing Script
Тестирование различных вариантов API endpoints для синхронизации с документацией
"""

import requests
import json
import time
from typing import Dict, List

# Конфигурация
BASE_URL = "https://aladdin-ai.ru"
TIMEOUT = 10

# Варианты endpoints для тестирования
ENDPOINT_VARIANTS = {
    "status": [
        "/api/components/status/crash_detection_agent",  # Код приложения
        "/api/components/status/sfm_core",               # Документация
        "/components/status/crash_detection_agent",      # Без /api
        "/components/status/sfm_core",                   # Без /api + sfm_core
    ],
    "config": [
        "/api/components/configuration/crash_detection_agent",  # Код приложения
        "/api/components/config/sfm_core",                       # Документация
        "/components/configuration/crash_detection_agent",       # Без /api
        "/components/config/sfm_core",                           # Без /api + sfm_core
        "/api/components/config/crash_detection_agent",          # Гибрид
        "/components/config/crash_detection_agent",              # Гибрид без /api
    ]
}

def test_endpoint(url: str, method: str = "GET") -> Dict:
    """Тестирование одного endpoint"""
    try:
        start_time = time.time()
        if method == "GET":
            response = requests.get(url, timeout=TIMEOUT)
        else:
            response = requests.post(url, timeout=TIMEOUT)

        response_time = time.time() - start_time

        result = {
            "url": url,
            "method": method,
            "status_code": response.status_code,
            "response_time": round(response_time, 3),
            "success": response.status_code == 200,
            "error": None
        }

        # Для успешных ответов сохраняем часть данных
        if response.status_code == 200:
            try:
                data = response.json()
                result["response_preview"] = json.dumps(data, indent=2)[:200] + "..."
            except:
                result["response_preview"] = response.text[:200] + "..."

    except requests.exceptions.RequestException as e:
        result = {
            "url": url,
            "method": method,
            "status_code": None,
            "response_time": None,
            "success": False,
            "error": str(e),
            "response_preview": None
        }

    return result

def main():
    """Основная функция тестирования"""
    print("🚀 Тестирование API Endpoints для ALADDIN")
    print("=" * 60)

    all_results = {}

    # Тестируем status endpoints
    print("\n📊 ТЕСТИРОВАНИЕ STATUS ENDPOINTS:")
    print("-" * 40)
    status_results = []
    for endpoint in ENDPOINT_VARIANTS["status"]:
        url = BASE_URL + endpoint
        print(f"\n🔍 Тестируем: {endpoint}")
        result = test_endpoint(url)
        status_results.append(result)

        status_emoji = "✅" if result["success"] else "❌"
        print(f"{status_emoji} {result['status_code']} - {result['response_time']}s")
        if result["error"]:
            print(f"   Ошибка: {result['error']}")

    all_results["status"] = status_results

    # Тестируем config endpoints
    print("\n\n📊 ТЕСТИРОВАНИЕ CONFIGURATION ENDPOINTS:")
    print("-" * 40)
    config_results = []
    for endpoint in ENDPOINT_VARIANTS["config"]:
        url = BASE_URL + endpoint
        print(f"\n🔍 Тестируем: {endpoint}")
        result = test_endpoint(url)
        config_results.append(result)

        status_emoji = "✅" if result["success"] else "❌"
        print(f"{status_emoji} {result['status_code']} - {result['response_time']}s")
        if result["error"]:
            print(f"   Ошибка: {result['error']}")

    all_results["config"] = config_results

    # Анализ результатов
    print("\n\n📈 АНАЛИЗ РЕЗУЛЬТАТОВ:")
    print("=" * 60)

    # Status endpoints
    print("\n🎯 STATUS ENDPOINTS:")
    working_status = [r for r in status_results if r["success"]]
    broken_status = [r for r in status_results if not r["success"]]

    print(f"✅ Рабочих: {len(working_status)}")
    for result in working_status:
        print(f"   {result['url'].replace(BASE_URL, '')}")

    print(f"❌ Сломанных: {len(broken_status)}")
    for result in broken_status:
        print(f"   {result['url'].replace(BASE_URL, '')} - {result['error'] or result['status_code']}")

    # Config endpoints
    print("\n🎯 CONFIGURATION ENDPOINTS:")
    working_config = [r for r in config_results if r["success"]]
    broken_config = [r for r in config_results if not r["success"]]

    print(f"✅ Рабочих: {len(working_config)}")
    for result in working_config:
        print(f"   {result['url'].replace(BASE_URL, '')}")

    print(f"❌ Сломанных: {len(broken_config)}")
    for result in broken_config:
        print(f"   {result['url'].replace(BASE_URL, '')} - {result['error'] or result['status_code']}")

    # Рекомендации
    print("\n\n💡 РЕКОМЕНДАЦИИ:")
    print("=" * 60)

    if working_status and working_config:
        print("✅ Есть рабочие endpoints для обоих типов!")
        print("🔄 Можно синхронизировать код с документацией")
    elif working_status and not working_config:
        print("⚠️ Status endpoints работают, но config - нет")
        print("🔧 Нужно исправить config endpoints на сервере")
    elif not working_status and not working_config:
        print("❌ Все endpoints не работают")
        print("🔧 Нужно проверить сервер")
    else:
        print("🤔 Смешанная ситуация - нужен анализ")

    # Сохранение результатов
    with open("api_test_results.json", "w") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Результаты сохранены в api_test_results.json")

if __name__ == "__main__":
    main()