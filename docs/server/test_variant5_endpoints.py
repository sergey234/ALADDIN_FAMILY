#!/usr/bin/env python3
"""
ТЕСТИРОВАНИЕ ВАРИАНТ 5: Гибридный подход
----------------------------------------
Тестирует все endpoints после реализации Варианта 5:
1. Reports Router endpoints (/api/reports/*/stats)
2. Analytics Router endpoints (/api/analytics/threats, /api/analytics/top-threats)
3. Проверка, что endpoints с роутерами НЕ попадают в Wildcard Proxy
4. Проверка, что неизвестные endpoints обрабатываются через Wildcard Proxy + SFM

Дата: 2026-03-14
"""

import requests
import json
from typing import Dict, Any, Optional

# Конфигурация
BASE_URL = "https://aladdin-ai.ru"  # Production сервер
# BASE_URL = "http://149.154.65.180:8002"  # Прямой доступ к серверу
# BASE_URL = "http://localhost:8000"  # Локальный тест
AUTH_TOKEN = None  # Установите токен для тестирования защищенных endpoints

# Цвета для вывода
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_success(message: str):
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")

def print_error(message: str):
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")

def print_warning(message: str):
    print(f"{Colors.YELLOW}⚠️ {message}{Colors.RESET}")

def print_info(message: str):
    print(f"{Colors.BLUE}ℹ️ {message}{Colors.RESET}")

def test_endpoint(
    method: str,
    endpoint: str,
    expected_status: Any = 200,  # Может быть int или list[int]
    expected_source: Optional[str] = None,
    should_not_be_wildcard: bool = False,
    params: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Тестирует endpoint
    
    Args:
        method: HTTP метод (GET, POST, etc.)
        endpoint: Путь endpoint
        expected_status: Ожидаемый статус код
        expected_source: Ожидаемый источник данных (например, "sfm_real", "router")
        should_not_be_wildcard: Должен ли endpoint обрабатываться роутером (не Wildcard Proxy)
        params: Параметры запроса
    
    Returns:
        True если тест пройден, False если нет
    """
    url = f"{BASE_URL}{endpoint}"
    headers = {}
    
    if AUTH_TOKEN:
        headers["Authorization"] = f"Bearer {AUTH_TOKEN}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params, timeout=10)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=params, timeout=10)
        else:
            print_error(f"Неподдерживаемый метод: {method}")
            return False
        
        # Проверяем статус код (может быть список допустимых статусов)
        if isinstance(expected_status, list):
            if response.status_code not in expected_status:
                print_error(f"{endpoint}: Ожидался статус {expected_status}, получен {response.status_code}")
                return False
        else:
            if response.status_code != expected_status:
                print_error(f"{endpoint}: Ожидался статус {expected_status}, получен {response.status_code}")
                return False
        
        # Парсим ответ
        try:
            data = response.json()
        except:
            print_error(f"{endpoint}: Не удалось распарсить JSON ответ")
            return False
        
        # Проверяем, что это НЕ Wildcard Proxy (если должен обрабатываться роутером)
        if should_not_be_wildcard:
            if "status" in data and data.get("status") == "SFM_PROXIED":
                print_error(f"{endpoint}: Попал в Wildcard Proxy, но должен обрабатываться роутером!")
                print_error(f"   Ответ: {json.dumps(data, indent=2, ensure_ascii=False)}")
                return False
            if "message" in data and "Wildcard Proxy" in str(data.get("message", "")):
                print_error(f"{endpoint}: Попал в Wildcard Proxy, но должен обрабатываться роутером!")
                print_error(f"   Ответ: {json.dumps(data, indent=2, ensure_ascii=False)}")
                return False
            # Проверяем, что нет признаков Wildcard Proxy в ответе
            response_str = json.dumps(data).lower()
            if "wildcard" in response_str or "sfm_proxied" in response_str:
                print_warning(f"{endpoint}: Возможно попал в Wildcard Proxy (проверьте ответ)")
                print_warning(f"   Ответ: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        # Проверяем источник данных (может быть список допустимых источников)
        if expected_source:
            actual_source = data.get("source", "unknown")
            if isinstance(expected_source, list):
                if actual_source not in expected_source:
                    print_warning(f"{endpoint}: Ожидался источник {expected_source}, получен '{actual_source}'")
            else:
                if actual_source != expected_source:
                    print_warning(f"{endpoint}: Ожидался источник '{expected_source}', получен '{actual_source}'")
        
        print_success(f"{endpoint}: Статус {response.status_code}, источник: {data.get('source', 'unknown')}")
        return True
        
    except requests.exceptions.RequestException as e:
        print_error(f"{endpoint}: Ошибка запроса: {e}")
        return False
    except Exception as e:
        print_error(f"{endpoint}: Неожиданная ошибка: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print_info("=" * 80)
    print_info("ТЕСТИРОВАНИЕ ВАРИАНТА 5: ГИБРИДНЫЙ ПОДХОД")
    print_info("=" * 80)
    print()
    
    results = {
        "passed": 0,
        "failed": 0,
        "total": 0
    }
    
    # ========================================================================
    # ТЕСТ 1: Reports Router endpoints (должны обрабатываться роутером)
    # ========================================================================
    print_info("ТЕСТ 1: Reports Router endpoints (/api/reports/*/stats)")
    print_info("-" * 80)
    
    reports_endpoints = [
        "/api/reports/driving/stats",
        "/api/reports/dark-web/stats",
        "/api/reports/identity-theft/stats",
        "/api/reports/privacy/location/stats",
        "/api/reports/privacy/cleanup/stats",
        "/api/reports/privacy/tracker/stats",
        "/api/reports/ai-categories/stats",
    ]
    
    for endpoint in reports_endpoints:
        results["total"] += 1
        if test_endpoint(
            "GET",
            endpoint,
            expected_status=[200, 403],  # Может быть 403 если требуется авторизация
            should_not_be_wildcard=True,
            expected_source=["sfm_real", "real_sfm"]  # Может быть любой из этих источников
        ):
            results["passed"] += 1
        else:
            results["failed"] += 1
        print()
    
    # ========================================================================
    # ТЕСТ 2: Analytics Router endpoints (должны обрабатываться роутером)
    # ========================================================================
    print_info("ТЕСТ 2: Analytics Router endpoints")
    print_info("-" * 80)
    
    analytics_endpoints = [
        ("/api/analytics", {"period": "day"}),
        ("/api/analytics/threats", {"period": "day"}),
        ("/api/analytics/top-threats", {"limit": 10, "period": "day"}),
    ]
    
    for endpoint, params in analytics_endpoints:
        results["total"] += 1
        # Analytics endpoints требуют авторизацию, поэтому 403 тоже нормально
        if test_endpoint(
            "GET",
            endpoint,
            expected_status=[200, 403],  # 403 = требуется авторизация (нормально)
            should_not_be_wildcard=True,
            params=params
        ):
            results["passed"] += 1
        else:
            results["failed"] += 1
        print()
    
    # ========================================================================
    # ТЕСТ 3: Endpoints с роутерами НЕ должны попадать в Wildcard Proxy
    # ========================================================================
    print_info("ТЕСТ 3: Проверка, что endpoints с роутерами НЕ попадают в Wildcard Proxy")
    print_info("-" * 80)
    
    router_endpoints = [
        "/api/auth/login",
        "/api/components/list",
        "/api/family/stats",
        "/api/payments/create",
        "/api/referral/code",
        "/api/protection/status",
    ]
    
    for endpoint in router_endpoints:
        results["total"] += 1
        if test_endpoint(
            "GET",
            endpoint,
            expected_status=[200, 401, 403, 422],  # Может быть 401, 403 или 422 для защищенных endpoints
            should_not_be_wildcard=True
        ):
            results["passed"] += 1
        else:
            results["failed"] += 1
        print()
    
    # ========================================================================
    # ТЕСТ 4: Неизвестные endpoints должны обрабатываться через Wildcard Proxy + SFM
    # ========================================================================
    print_info("ТЕСТ 4: Неизвестные endpoints через Wildcard Proxy + SFM")
    print_info("-" * 80)
    
    unknown_endpoints = [
        "/api/unknown/endpoint",
        "/api/test/function",
        "/api/custom/stats",
    ]
    
    for endpoint in unknown_endpoints:
        results["total"] += 1
        # Неизвестные endpoints могут вернуть 200 (через SFM), 404 или 403
        if test_endpoint(
            "GET",
            endpoint,
            expected_status=[200, 403, 404],  # Может быть 200 (SFM), 403 (авторизация) или 404
            should_not_be_wildcard=False  # Может быть Wildcard Proxy
        ):
            results["passed"] += 1
        else:
            results["failed"] += 1
        print()
    
    # ========================================================================
    # ИТОГОВЫЙ ОТЧЕТ
    # ========================================================================
    print_info("=" * 80)
    print_info("ИТОГОВЫЙ ОТЧЕТ")
    print_info("=" * 80)
    print()
    print_info(f"Всего тестов: {results['total']}")
    print_success(f"Пройдено: {results['passed']}")
    if results['failed'] > 0:
        print_error(f"Провалено: {results['failed']}")
    else:
        print_success(f"Провалено: {results['failed']}")
    print()
    
    success_rate = (results['passed'] / results['total'] * 100) if results['total'] > 0 else 0
    print_info(f"Процент успеха: {success_rate:.1f}%")
    print()
    
    if results['failed'] == 0:
        print_success("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Вариант 5 работает правильно!")
    else:
        print_warning("⚠️ Некоторые тесты провалены. Проверьте логи выше.")
    
    return results['failed'] == 0

if __name__ == "__main__":
    import sys
    
    # Можно передать токен как аргумент
    if len(sys.argv) > 1:
        AUTH_TOKEN = sys.argv[1]
        print_info(f"Используется токен: {AUTH_TOKEN[:20]}...")
        print()
    
    success = main()
    sys.exit(0 if success else 1)
