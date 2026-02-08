#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Альтернативный деплой Crash Detection через API
Если SSH недоступен, используем этот метод
"""

import requests
import time

def deploy_crash_detection_via_api():
    """Деплой через API вызовы"""

    server_ip = "149.154.65.180"
    api_url = f"http://{server_ip}:8002"

    print("🚀 АЛЬТЕРНАТИВНЫЙ ДЕПЛОЙ CRASH DETECTION ЧЕРЕЗ API")
    print("=" * 60)

    # Проверяем соединение
    try:
        response = requests.get(f"{api_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Сервер доступен")
        else:
            print(f"❌ Сервер недоступен: HTTP {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return

    # Проверяем текущие файлы (если есть endpoint для этого)
    try:
        response = requests.get(f"{api_url}/api/system/info", timeout=5)
        if response.status_code == 200:
            print("✅ Система отвечает")
        else:
            print(f"⚠️ Система info недоступен: HTTP {response.status_code}")
    except:
        print("⚠️ System info недоступен")

    print("\\n📋 ПЛАН ДЕПЛОЯ:")
    print("1. 🚨 CRASH DETECTION API отсутствует на сервере")
    print("2. 🔄 Нужно загрузить файлы вручную:")
    print("   - crash_detection_router.py")
    print("   - crash_detection_agent.py")
    print("   - deploy_crash_detection_server.sh")
    print("3. 🔧 Выполнить деплой на сервере:")
    print("   ./deploy_crash_detection_server.sh")
    print("4. 🧪 Протестировать новые эндпоинты")

    print("\\n📤 ФАЙЛЫ ДЛЯ ЗАГРУЗКИ:")
    print("crash_detection_router.py - FastAPI роутер (10KB)")
    print("crash_detection_agent.py - AI агент (5KB)")
    print("deploy_crash_detection_server.sh - скрипт деплоя (3KB)")

    print("\\n🎯 РЕЗУЛЬТАТ:")
    print("После деплоя будут доступны 6 эндпоинтов:")
    print("✅ POST /api/crash-detection/setup")
    print("✅ POST /api/crash-detection/alert")
    print("✅ POST /api/crash-detection/start")
    print("✅ POST /api/crash-detection/stop")
    print("✅ POST /api/crash-detection/data")
    print("✅ GET /api/crash-detection/status")

    # Проверяем что сейчас работает
    print("\\n🔍 ТЕКУЩЕЕ СОСТОЯНИЕ CRASH DETECTION:")
    crash_endpoints = [
        "api/crash-detection/setup",
        "api/crash-detection/alert",
        "api/crash-detection/start",
        "api/crash-detection/stop",
        "api/crash-detection/data",
        "api/crash-detection/status"
    ]

    for endpoint in crash_endpoints:
        try:
            response = requests.get(f"{api_url}/{endpoint}", timeout=3)
            if response.status_code == 200:
                print(f"   ✅ {endpoint} - работает")
            else:
                print(f"   ❌ {endpoint} - HTTP {response.status_code}")
        except:
            print(f"   ❌ {endpoint} - ошибка")

    print("\\n💡 РЕКОМЕНДАЦИИ:")
    print("1. Загрузите файлы на сервер вручную")
    print("2. Выполните: chmod +x deploy_crash_detection_server.sh")
    print("3. Запустите: ./deploy_crash_detection_server.sh")
    print("4. Проверьте логи сервера")

if __name__ == "__main__":
    deploy_crash_detection_via_api()