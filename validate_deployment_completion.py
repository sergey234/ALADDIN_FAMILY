#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
СКРИПТ ВАЛИДАЦИИ ЗАВЕРШЕНИЯ ДЕПЛОЯ CRASH DETECTION
Проверяет выполнение всех пунктов плана деплоя
"""

import requests
import time
import json
from datetime import datetime

def validate_crash_detection_deployment():
    """Комплексная валидация деплоя Crash Detection"""

    server_url = "http://149.154.65.180:8002"

    print("🔍 ВАЛИДАЦИЯ ЗАВЕРШЕНИЯ ДЕПЛОЯ CRASH DETECTION")
    print("=" * 60)
    print(f"Сервер: {server_url}")
    print(f"Время проверки: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    validation_results = {
        "server_accessible": False,
        "crash_detection_endpoints": 0,
        "working_endpoints": 0,
        "sfm_integration": 0,
        "performance_tests": [],
        "mobile_integration_ready": False
    }

    # 1. Проверка доступности сервера
    print("1️⃣ ПРОВЕРКА ДОСТУПНОСТИ СЕРВЕРА")
    try:
        response = requests.get(f"{server_url}/api/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            validation_results["server_accessible"] = True
            print(f"   ✅ Сервер доступен (HTTP {response.status_code})")
            print(f"   📊 Эндпоинтов: {data.get('endpoints', 'N/A')}")
            print(f"   🔒 SFM: {data.get('sfm_adapter', 'N/A')}")
        else:
            print(f"   ❌ Сервер недоступен (HTTP {response.status_code})")
    except Exception as e:
        print(f"   ❌ Ошибка подключения: {str(e)}")

    print()

    # 2. Проверка Crash Detection эндпоинтов
    print("2️⃣ ПРОВЕРКА CRASH DETECTION ЭНДПОИНТОВ")
    crash_endpoints = [
        ("GET", "api/crash-detection/status"),
        ("POST", "api/crash-detection/setup"),
        ("POST", "api/crash-detection/start"),
        ("POST", "api/crash-detection/stop"),
        ("POST", "api/crash-detection/data"),
        ("POST", "api/crash-detection/alert")
    ]

    for method, endpoint in crash_endpoints:
        try:
            url = f"{server_url}/{endpoint}"

            if method == "POST":
                if "setup" in endpoint:
                    data = {"latitude": 55.7558, "longitude": 37.6173, "radius": 500}
                elif "data" in endpoint:
                    data = {
                        "accelerometer": {"x": 1.0, "y": 1.0, "z": 1.0},
                        "gyroscope": {"x": 0.1, "y": 0.1, "z": 0.1},
                        "speed": 50.0,
                        "latitude": 55.7558,
                        "longitude": 37.6173,
                        "timestamp": time.time()
                    }
                elif "alert" in endpoint:
                    data = {"latitude": 55.7558, "longitude": 37.6173, "severity": "high"}
                else:
                    data = {}

                response = requests.post(url, json=data, timeout=5)
            else:
                response = requests.get(url, timeout=5)

            validation_results["crash_detection_endpoints"] += 1

            if response.status_code == 200:
                validation_results["working_endpoints"] += 1

                try:
                    json_data = response.json()
                    if json_data.get("source") == "real_sfm":
                        validation_results["sfm_integration"] += 1
                        sfm_status = "🔒 SFM"
                    else:
                        sfm_status = "⚠️ No SFM"

                    print(f"   ✅ {method} {endpoint} - HTTP 200, {sfm_status}")
                except:
                    print(f"   ✅ {method} {endpoint} - HTTP 200 (no JSON)")
            else:
                print(f"   ❌ {method} {endpoint} - HTTP {response.status_code}")

        except Exception as e:
            print(f"   ❌ {method} {endpoint} - ОШИБКА: {str(e)[:50]}")

    print()

    # 3. Тестирование производительности
    print("3️⃣ ТЕСТИРОВАНИЕ ПРОИЗВОДИТЕЛЬНОСТИ")
    performance_tests = [
        ("GET", "api/health"),
        ("GET", "api/crash-detection/status"),
        ("POST", "api/crash-detection/setup", {"latitude": 55.7558, "longitude": 37.6173, "radius": 500})
    ]

    for method, endpoint, *data in performance_tests:
        try:
            url = f"{server_url}/{endpoint}"
            times = []

            # 5 измерений
            for i in range(5):
                start_time = time.time()

                if method == "POST" and data:
                    response = requests.post(url, json=data[0], timeout=5)
                else:
                    response = requests.get(url, timeout=5)

                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # в ms

                if response.status_code == 200:
                    times.append(response_time)

            if times:
                avg_time = sum(times) / len(times)
                max_time = max(times)
                validation_results["performance_tests"].append({
                    "endpoint": endpoint,
                    "avg_ms": round(avg_time, 2),
                    "max_ms": round(max_time, 2),
                    "success": len(times)
                })

                status = "✅" if avg_time < 50 else "⚠️" if avg_time < 100 else "❌"
                print(f"   {status} {endpoint}: {avg_time:.1f}ms среднее, {max_time:.1f}ms максимум")
            else:
                print(f"   ❌ {endpoint}: все запросы неудачны")

        except Exception as e:
            print(f"   ❌ {endpoint}: ошибка тестирования")

    print()

    # 4. Проверка мобильной интеграции
    print("4️⃣ ПРОВЕРКА ГОТОВНОСТИ МОБИЛЬНОЙ ИНТЕГРАЦИИ")

    # Проверяем что все необходимые эндпоинты для мобильного app работают
    mobile_endpoints = [
        "api/crash-detection/setup",  # Для настройки геозоны
        "api/crash-detection/start",  # Для запуска мониторинга
        "api/crash-detection/stop",   # Для остановки мониторинга
        "api/crash-detection/data",   # Для отправки сенсорных данных
        "api/crash-detection/alert",  # Для отправки алерта
        "api/crash-detection/status"  # Для проверки статуса
    ]

    mobile_ready_count = 0
    for endpoint in mobile_endpoints:
        try:
            response = requests.get(f"{server_url}/{endpoint}", timeout=3)
            if response.status_code == 200:
                mobile_ready_count += 1
        except:
            pass

    if mobile_ready_count == len(mobile_endpoints):
        validation_results["mobile_integration_ready"] = True
        print("   ✅ Мобильная интеграция готова (6/6 эндпоинтов)")
    else:
        print(f"   ⚠️ Мобильная интеграция частична ({mobile_ready_count}/6 эндпоинтов)")

    print()

    # 5. Финальные результаты
    print("5️⃣ ФИНАЛЬНЫЕ РЕЗУЛЬТАТЫ ВАЛИДАЦИИ")
    print("=" * 60)

    # Оценки
    scores = {
        "server_accessibility": 100 if validation_results["server_accessible"] else 0,
        "crash_detection_completeness": (validation_results["working_endpoints"] / 6) * 100 if validation_results["crash_detection_endpoints"] > 0 else 0,
        "sfm_integration": (validation_results["sfm_integration"] / validation_results["working_endpoints"]) * 100 if validation_results["working_endpoints"] > 0 else 0,
        "performance": 100 if all(test.get("avg_ms", 1000) < 50 for test in validation_results["performance_tests"]) else 50,
        "mobile_integration": 100 if validation_results["mobile_integration_ready"] else 0
    }

    overall_score = sum(scores.values()) / len(scores)

    print(f"📊 ОБЩАЯ ОЦЕНКА: {overall_score:.1f}%")
    print()

    for category, score in scores.items():
        status = "✅" if score >= 80 else "⚠️" if score >= 50 else "❌"
        category_name = {
            "server_accessibility": "Доступность сервера",
            "crash_detection_completeness": "Полнота Crash Detection",
            "sfm_integration": "SFM интеграция",
            "performance": "Производительность",
            "mobile_integration": "Мобильная интеграция"
        }.get(category, category)

        print(f"   {status} {category_name}: {score:.1f}%")

    print()

    # Рекомендации
    print("🎯 РЕКОМЕНДАЦИИ:")
    if overall_score >= 80:
        print("   ✅ ДЕПЛОЙ УСПЕШЕН! Система готова к использованию.")
        print("   📱 Мобильное приложение может использовать Crash Detection.")
    elif overall_score >= 50:
        print("   ⚠️ ДЕПЛОЙ ЧАСТИЧНО УСПЕШЕН. Требуется доработка.")
        if scores["performance"] < 50:
            print("   🔧 Оптимизировать производительность сервера.")
        if scores["crash_detection_completeness"] < 80:
            print("   🚨 Проверить работу всех Crash Detection эндпоинтов.")
    else:
        print("   ❌ ДЕПЛОЙ НЕ УДАЧЕН. Требуется полный перепроверка.")
        print("   🔄 Повторить процесс деплоя согласно плану.")

    # Сохранение результатов
    with open("deployment_validation_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "validation_results": validation_results,
            "scores": scores,
            "overall_score": overall_score,
            "recommendations": "См. вывод выше"
        }, f, ensure_ascii=False, indent=2)

    print("
💾 Результаты сохранены в deployment_validation_results.json"
    return overall_score >= 80

if __name__ == "__main__":
    success = validate_crash_detection_deployment()
    exit(0 if success else 1)