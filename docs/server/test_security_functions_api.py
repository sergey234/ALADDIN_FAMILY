#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Проверка работы всех функций безопасности через API endpoints
ЭТАП 6.1-6.4
"""

import requests
import json
import sys
from typing import Dict, List, Optional

# Базовый URL API
BASE_URL = "http://149.154.65.180:8002"  # Production server

# Токен авторизации (получить из переменных окружения или конфига)
AUTH_TOKEN = None  # Установить перед запуском


def get_auth_headers() -> Dict[str, str]:
    """Получить заголовки авторизации"""
    if not AUTH_TOKEN:
        raise ValueError("AUTH_TOKEN не установлен")
    return {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }


# Список всех функций безопасности по категориям
SECURITY_FUNCTIONS = {
    "threat_protection": {
        "name": "Защита от угроз",
        "total": 100,
        "endpoints": [
            # Components (5)
            "/api/components/status/{component_id}",
            "/api/components/enable/{component_id}",
            "/api/components/disable/{component_id}",
            "/api/components/config/{component_id}",
            "/api/components/health",
            
            # Protection (7)
            "/api/protection/enable",
            "/api/protection/disable",
            "/api/protection/status",
            "/api/protection/stats",
            "/api/protection/settings",
            "/api/protection/threat-scenarios",
            "/api/protection/sync",
            
            # Phishing Protection
            "/api/phishing/sensitivity",
            "/api/phishing/block_suspicious",
            "/api/phishing/exclusions",
            
            # Malware Protection
            "/api/malware/scan_scheduled",
            "/api/malware/quarantine",
            "/api/malware/scan_now",
            
            # Mobile Security
            "/api/mobile/app_lock",
            "/api/mobile/biometric",
            
            # Network Security
            "/api/network/firewall_rules",
            "/api/network/vpn_config",
            
            # AI Categories (4)
            "/api/ai/categories/stats",
            "/api/ai/categories/reports",
            "/api/ai/categories/allow",
            "/api/ai/categories/block",
            
            # Data Cleanup (3)
            "/api/data/cleanup/stats",
            "/api/data/cleanup/records",
            "/api/data/cleanup/start",
            
            # Location (4)
            "/api/location/stats",
            "/api/location/requests",
            "/api/location/allow",
            "/api/location/block",
            "/api/location/accuracy",
            
            # Dark Web (5)
            "/api/darkweb/leaks",
            "/api/darkweb/stats",
            "/api/darkweb/scans",
            "/api/darkweb/resolve",
            "/api/darkweb/scan_start",
            
            # Identity Theft (4)
            "/api/identity/attempts",
            "/api/identity/stats",
            "/api/identity/allow",
            "/api/identity/block",
            "/api/identity/whitelist",
            
            # Identity Theft Protection (5)
            "/api/identity/theft/attempts",
            "/api/identity/theft/stats",
            "/api/identity/theft/allow/{attempt_id}",
            "/api/identity/theft/block/{attempt_id}",
            "/api/identity/theft/whitelist",
            "/api/identity/theft/history",
            "/api/identity/theft/report/{attempt_id}",
            "/api/identity/theft/settings",
            
            # Anti-Tracker (6)
            "/api/antitracker/trackers",
            "/api/antitracker/block/{tracker_id}",
            "/api/antitracker/allow/{tracker_id}",
            "/api/antitracker/stats",
            "/api/antitracker/whitelist",
            "/api/antitracker/categories",
            "/api/antitracker/category/{category_id}",
            "/api/antitracker/scan",
            "/api/antitracker/reports",
            
            # Crash Detection (6)
            "/api/crash-detection/setup",
            "/api/crash-detection/alert",
            "/api/crash-detection/start",
            "/api/crash-detection/stop",
            "/api/crash-detection/data",
            "/api/crash-detection/status",
            
            # Roadside Assistance (5)
            "/api/roadside-assistance/call",
            "/api/roadside-assistance/status/{request_id}",
            "/api/roadside-assistance/cancel/{request_id}",
            "/api/roadside-assistance/history",
            "/api/roadside-assistance/health",
            
            # IoT Security (6)
            "/api/iot/status/{homeId}",
            "/api/iot/devices/{homeId}",
            "/api/iot/threats/{homeId}",
            "/api/iot/device/{deviceId}/block",
            "/api/iot/scan/{homeId}",
            "/api/iot/fix/{threatId}",
            
            # Driving Reports (5)
            "/api/reports/driving",
            "/api/reports/driving/stats",
            "/api/reports/driving/export",
            "/api/reports/driving/start",
            "/api/reports/driving/end",
            
            # Dark Web Reports (7)
            "/api/reports/dark-web/leaks",
            "/api/reports/dark-web/stats",
            "/api/reports/dark-web/scans",
            "/api/reports/dark-web/resolve",
            "/api/reports/dark-web/scan/start",
            "/api/reports/dark-web/scan/secure",
            "/api/reports/dark-web/scan/fast",
            
            # Identity Theft Reports (5)
            "/api/reports/identity-theft/attempts",
            "/api/reports/identity-theft/stats",
            "/api/reports/identity-theft/allow",
            "/api/reports/identity-theft/block",
            "/api/reports/identity-theft/whitelist",
            
            # Privacy Reports (2)
            "/api/reports/privacy/location/bubble",
            "/api/reports/privacy/location/send",
        ]
    },
    "parental_control": {
        "name": "Родительский контроль",
        "total": 32,
        "endpoints": [
            # Parental Control (2)
            "/api/v1/parental-control/stats",
            "/api/v1/parental-control/status",
            
            # Parental Control Bypass (1)
            "/api/parental/bypass/stats",
            
            # Parental Control API (5)
            "/api/v1/parental-control/blocking",
            "/api/v1/parental-control/rules",
            "/api/v1/parental-control/access-requests",
            "/api/v1/parental-control/access-requests/{requestId}",
            "/api/v1/parental-control/stats",
            
            # Parental Control Settings (4)
            "/api/parental/settings",
            "/api/parental/restrict/{child_id}",
            "/api/parental/activity/{child_id}",
            "/api/parental/alert",
            
            # Additional Parental Control endpoints (20)
            # Эти endpoints могут быть реализованы через общий роутер компонентов
            # или через специфичные endpoints родительского контроля
        ]
    },
    "additional": {
        "name": "Дополнительные функции",
        "total": 6,
        "endpoints": [
            # Analytics (3)
            "/api/analytics",
            "/api/analytics/threats",
            "/api/analytics/top-threats",
            
            # Metrics (1)
            "/api/metrics/upload",
            
            # Notifications (2)
            "/api/notifications/list",
            "/api/notifications/unread_count",
        ]
    }
}

# Тарифы и их функции
TARIFFS = {
    "FREE": {
        "name": "Бесплатный",
        "functions_count": 26,
        "components": []  # Заполнить список компонентов
    },
    "PERSONAL": {
        "name": "Персональный",
        "functions_count": 69,
        "components": []
    },
    "FAMILY": {
        "name": "Семейный",
        "functions_count": 124,
        "components": []
    },
    "PREMIUM": {
        "name": "Премиум",
        "functions_count": 138,
        "components": []
    }
}


def test_endpoint(endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict:
    """Протестировать один endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        headers = get_auth_headers()
        
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=10)
        else:
            return {"success": False, "error": f"Unsupported method: {method}"}
        
        return {
            "success": response.status_code in [200, 201],
            "status_code": response.status_code,
            "response": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
        }
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}


def test_security_functions():
    """Протестировать все функции безопасности"""
    print("=" * 80)
    print("ПРОВЕРКА РАБОТЫ ВСЕХ ФУНКЦИЙ БЕЗОПАСНОСТИ ЧЕРЕЗ API")
    print("=" * 80)
    print()
    
    if not AUTH_TOKEN:
        print("⚠️ ВНИМАНИЕ: AUTH_TOKEN не установлен")
        print("   Установите токен перед запуском тестов")
        print("   export AUTH_TOKEN='your_token_here'")
        print()
    
    results = {}
    
    # Тестировать каждую категорию
    for category, info in SECURITY_FUNCTIONS.items():
        print(f"🔍 Тестирование: {info['name']} ({info['total']} функций)...")
        
        category_results = {
            "success": [],
            "failed": []
        }
        
        for endpoint in info["endpoints"]:
            result = test_endpoint(endpoint)
            if result["success"]:
                category_results["success"].append(endpoint)
            else:
                category_results["failed"].append({
                    "endpoint": endpoint,
                    "error": result.get("error", f"Status: {result.get('status_code', 'Unknown')}")
                })
        
        results[category] = category_results
        
        print(f"  ✅ Успешно: {len(category_results['success'])}/{len(info['endpoints'])}")
        print(f"  ❌ Ошибки: {len(category_results['failed'])}/{len(info['endpoints'])}")
        print()
    
    # Вывести детальные результаты
    print("=" * 80)
    print("ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ")
    print("=" * 80)
    print()
    
    for category, category_results in results.items():
        print(f"📊 {SECURITY_FUNCTIONS[category]['name']}:")
        if category_results["failed"]:
            print("  ❌ Ошибки:")
            for failed in category_results["failed"][:5]:  # Показать первые 5
                print(f"    - {failed['endpoint']}: {failed['error']}")
            if len(category_results["failed"]) > 5:
                print(f"    ... и еще {len(category_results['failed']) - 5} ошибок")
        print()
    
    # Сохранить результаты
    results_file = '/opt/aladdin-backend/docs/server/security_functions_test_results.json'
    try:
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"📄 Результаты сохранены в: {results_file}")
    except Exception as e:
        print(f"⚠️ Не удалось сохранить результаты: {e}")
    
    return results


def test_tariff_functions():
    """Проверить соответствие функций тарифам"""
    print("=" * 80)
    print("ПРОВЕРКА СООТВЕТСТВИЯ ФУНКЦИЙ ТАРИФАМ")
    print("=" * 80)
    print()
    
    # TODO: Реализовать проверку соответствия функций тарифам
    # Это требует доступа к базе данных или API для получения списка функций по тарифам
    
    print("⚠️ Эта функция требует доступа к базе данных или API")
    print("   для получения списка функций по тарифам")
    print()
    
    return True


def main():
    print("🚀 ЗАПУСК ТЕСТИРОВАНИЯ ФУНКЦИЙ БЕЗОПАСНОСТИ")
    print()
    
    # Проверить токен
    if not AUTH_TOKEN:
        print("❌ ОШИБКА: AUTH_TOKEN не установлен")
        print("   Установите токен перед запуском:")
        print("   export AUTH_TOKEN='your_token_here'")
        sys.exit(1)
    
    # Тестировать функции безопасности
    results = test_security_functions()
    
    # Проверить соответствие тарифам
    test_tariff_functions()
    
    # Итоговый результат
    total_success = sum(len(r["success"]) for r in results.values())
    total_failed = sum(len(r["failed"]) for r in results.values())
    
    print("=" * 80)
    print("ИТОГОВЫЙ РЕЗУЛЬТАТ")
    print("=" * 80)
    print(f"✅ Успешно: {total_success}")
    print(f"❌ Ошибки: {total_failed}")
    print()
    
    if total_failed == 0:
        print("✅ ВСЕ ФУНКЦИИ РАБОТАЮТ КОРРЕКТНО!")
        return True
    else:
        print(f"⚠️ НАЙДЕНО {total_failed} ОШИБОК")
        print("   Проверьте детальные результаты выше")
        return False


if __name__ == '__main__':
    # Получить токен из переменных окружения
    import os
    AUTH_TOKEN = os.environ.get('AUTH_TOKEN')
    
    success = main()
    sys.exit(0 if success else 1)
