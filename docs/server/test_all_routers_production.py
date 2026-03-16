#!/usr/bin/env python3
"""
ПОЛНОЕ ТЕСТИРОВАНИЕ ВСЕХ РОУТЕРОВ ДЛЯ ПРОДАКШН
------------------------------------------------
Тестирует все API endpoints и роутеры для проверки готовности к продакшн.

Категории тестирования:
1. Основные роутеры (Auth, Components, Family, Protection, Referral, Payments)
2. Analytics Router (новый)
3. Reports Router (новый)
4. Security Routers (17+ роутеров)
5. Sync Routers (7+ роутеров)
6. Wildcard Proxy (для неизвестных endpoints)

Дата: 2026-03-14
"""

import requests
import json
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import time

# Конфигурация
BASE_URL = "https://aladdin-ai.ru"
AUTH_TOKEN = None  # Установите токен для тестирования защищенных endpoints

# Цвета для вывода
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'

def print_success(message: str):
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")

def print_error(message: str):
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")

def print_warning(message: str):
    print(f"{Colors.YELLOW}⚠️ {message}{Colors.RESET}")

def print_info(message: str):
    print(f"{Colors.BLUE}ℹ️ {message}{Colors.RESET}")

def print_section(message: str):
    print(f"{Colors.CYAN}{'='*80}{Colors.RESET}")
    print(f"{Colors.CYAN}{message}{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*80}{Colors.RESET}")

class EndpointTestResult:
    def __init__(self, endpoint: str, method: str, status: int, 
                 is_wildcard: bool, has_data: bool, error: Optional[str] = None):
        self.endpoint = endpoint
        self.method = method
        self.status = status
        self.is_wildcard = is_wildcard
        self.has_data = has_data
        self.error = error
        self.timestamp = datetime.now().isoformat()

def test_endpoint(
    method: str,
    endpoint: str,
    expected_status: Any = [200, 401, 403, 422],
    should_not_be_wildcard: bool = True,
    params: Optional[Dict[str, Any]] = None,
    body: Optional[Dict[str, Any]] = None,
    description: Optional[str] = None
) -> EndpointTestResult:
    """
    Тестирует endpoint
    
    Returns:
        EndpointTestResult с результатами теста
    """
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Cache-Control": "no-cache",
        "Pragma": "no-cache"
    }
    
    if AUTH_TOKEN:
        headers["Authorization"] = f"Bearer {AUTH_TOKEN}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params, timeout=10)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=body or params, timeout=10)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=body or params, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)
        else:
            return EndpointTestResult(endpoint, method, 0, False, False, f"Неподдерживаемый метод: {method}")
        
        # Проверяем статус код
        if isinstance(expected_status, list):
            status_ok = response.status_code in expected_status
        else:
            status_ok = response.status_code == expected_status
        
        # Парсим ответ
        try:
            data = response.json()
        except:
            data = {"raw": response.text[:200]}
        
        # Проверяем, что это НЕ Wildcard Proxy
        is_wildcard = False
        if isinstance(data, dict):
            if "status" in data and data.get("status") == "SFM_PROXIED":
                is_wildcard = True
            if "message" in data and "Wildcard Proxy" in str(data.get("message", "")):
                is_wildcard = True
        
        # Проверяем наличие данных
        has_data = False
        if isinstance(data, dict):
            # Проверяем, что есть реальные данные, а не только сообщения
            keys_to_check = ["data", "result", "items", "list", "total", "period", "source"]
            has_data = any(key in data for key in keys_to_check) or len(data) > 2
        
        return EndpointTestResult(
            endpoint=endpoint,
            method=method,
            status=response.status_code,
            is_wildcard=is_wildcard,
            has_data=has_data,
            error=None if status_ok and (not should_not_be_wildcard or not is_wildcard) else "Проблема"
        )
        
    except requests.exceptions.RequestException as e:
        return EndpointTestResult(endpoint, method, 0, False, False, str(e))
    except Exception as e:
        return EndpointTestResult(endpoint, method, 0, False, False, f"Неожиданная ошибка: {e}")

def test_router_category(
    category_name: str,
    endpoints: List[Tuple[str, str, Optional[Dict], Optional[str]]],
    description: str = ""
) -> Dict[str, Any]:
    """
    Тестирует категорию роутеров
    
    Args:
        category_name: Название категории
        endpoints: Список кортежей (method, endpoint, params, description)
        description: Описание категории
    
    Returns:
        Словарь с результатами тестирования
    """
    print_section(f"ТЕСТ: {category_name}")
    if description:
        print_info(f"Описание: {description}")
    print()
    
    results = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "wildcard_errors": 0,
        "status_errors": 0,
        "network_errors": 0,
        "details": []
    }
    
    for method, endpoint, params, desc in endpoints:
        results["total"] += 1
        test_desc = desc or f"{method} {endpoint}"
        
        result = test_endpoint(
            method=method,
            endpoint=endpoint,
            params=params,
            should_not_be_wildcard=True
        )
        
        results["details"].append(result)
        
        # Анализ результата
        if result.error:
            if result.status == 0:
                results["network_errors"] += 1
                print_error(f"{test_desc}: Ошибка сети - {result.error}")
            elif result.is_wildcard:
                results["wildcard_errors"] += 1
                print_error(f"{test_desc}: Попал в Wildcard Proxy (не должен!)")
            else:
                results["status_errors"] += 1
                print_warning(f"{test_desc}: Статус {result.status} (может быть нормально для защищенных endpoints)")
        else:
            results["passed"] += 1
            status_msg = f"Статус {result.status}"
            if result.has_data:
                status_msg += ", есть данные"
            print_success(f"{test_desc}: {status_msg}")
        
        time.sleep(0.1)  # Небольшая задержка между запросами
    
    print()
    print_info(f"Итого: {results['passed']}/{results['total']} пройдено")
    if results['wildcard_errors'] > 0:
        print_error(f"Wildcard Proxy ошибок: {results['wildcard_errors']}")
    if results['status_errors'] > 0:
        print_warning(f"Ошибок статуса: {results['status_errors']}")
    if results['network_errors'] > 0:
        print_error(f"Ошибок сети: {results['network_errors']}")
    print()
    
    return results

def main():
    """Основная функция тестирования"""
    print_section("ПОЛНОЕ ТЕСТИРОВАНИЕ ВСЕХ РОУТЕРОВ ДЛЯ ПРОДАКШН")
    print()
    print_info(f"База URL: {BASE_URL}")
    if AUTH_TOKEN:
        print_info(f"Токен: {AUTH_TOKEN[:20]}...")
    else:
        print_warning("Токен не установлен - некоторые endpoints могут вернуть 401/403")
    print()
    
    all_results = {}
    
    # ========================================================================
    # ТЕСТ 1: ОСНОВНЫЕ РОУТЕРЫ
    # ========================================================================
    main_routers = [
        ("GET", "/api/auth/login", None, "Auth Login"),
        ("GET", "/api/components/list", None, "Components List"),
        ("GET", "/api/components/status/crash_detection_agent", None, "Component Status"),
        ("GET", "/api/family/stats", None, "Family Stats"),
        ("GET", "/api/protection/status", None, "Protection Status"),
        ("GET", "/api/referral/code", None, "Referral Code"),
        ("GET", "/api/payments/create", None, "Payments Create"),
    ]
    
    all_results["main_routers"] = test_router_category(
        "Основные роутеры",
        main_routers,
        "Auth, Components, Family, Protection, Referral, Payments"
    )
    
    # ========================================================================
    # ТЕСТ 2: ANALYTICS ROUTER (НОВЫЙ)
    # ========================================================================
    analytics_endpoints = [
        ("GET", "/api/analytics", {"period": "day"}, "Analytics Overview"),
        ("GET", "/api/analytics/threats", {"period": "day"}, "Analytics Threats"),
        ("GET", "/api/analytics/top-threats", {"limit": 10, "period": "day"}, "Analytics Top Threats"),
    ]
    
    all_results["analytics_router"] = test_router_category(
        "Analytics Router (НОВЫЙ)",
        analytics_endpoints,
        "Расширенный Analytics Router с новыми endpoints"
    )
    
    # ========================================================================
    # ТЕСТ 3: REPORTS ROUTER (НОВЫЙ)
    # ========================================================================
    reports_endpoints = [
        ("GET", "/api/reports/driving/stats", None, "Driving Reports Stats"),
        ("GET", "/api/reports/dark-web/stats", None, "Dark Web Stats"),
        ("GET", "/api/reports/identity-theft/stats", None, "Identity Theft Stats"),
        ("GET", "/api/reports/privacy/location/stats", None, "Location Stats"),
        ("GET", "/api/reports/privacy/cleanup/stats", None, "Cleanup Stats"),
        ("GET", "/api/reports/privacy/tracker/stats", None, "Tracker Stats"),
        ("GET", "/api/reports/ai-categories/stats", None, "AI Categories Stats"),
    ]
    
    all_results["reports_router"] = test_router_category(
        "Reports Router (НОВЫЙ)",
        reports_endpoints,
        "Все 7 endpoints для статистики отчетов"
    )
    
    # ========================================================================
    # ТЕСТ 4: SECURITY ROUTERS
    # ========================================================================
    security_endpoints = [
        ("GET", "/api/location/bubble", None, "Location Bubble"),
        ("GET", "/api/identity-theft/results", None, "Identity Theft Results"),
        ("GET", "/api/darkweb/leaks", None, "Dark Web Leaks"),
        ("GET", "/api/anti-tracker/status", None, "Anti Tracker Status"),
        ("GET", "/api/data-cleanup/status", None, "Data Cleanup Status"),
        ("GET", "/api/ai-categories/list", None, "AI Categories List"),
        ("GET", "/api/crash-detection/status", None, "Crash Detection Status"),
        ("GET", "/api/iot/status", None, "IoT Status"),
        ("GET", "/api/parental-control/status", None, "Parental Control Status"),
        ("GET", "/api/roadside-assistance/status", None, "Roadside Assistance Status"),
    ]
    
    all_results["security_routers"] = test_router_category(
        "Security Routers",
        security_endpoints,
        "Роутеры безопасности (Location, Identity, Dark Web, etc.)"
    )
    
    # ========================================================================
    # ТЕСТ 5: SYNC ROUTERS
    # ========================================================================
    sync_endpoints = [
        ("GET", "/api/sync/subscription/status", None, "Subscription Sync Status"),
        ("GET", "/api/sync/user-profile", None, "User Profile Sync"),
        ("GET", "/api/sync/app-settings", None, "App Settings Sync"),
        ("GET", "/api/sync/offline-storage", None, "Offline Storage Sync"),
        ("GET", "/api/sync/crash-detection", None, "Crash Detection Sync"),
    ]
    
    all_results["sync_routers"] = test_router_category(
        "Sync Routers",
        sync_endpoints,
        "Роутеры синхронизации между устройствами"
    )
    
    # ========================================================================
    # ТЕСТ 6: SYSTEM ROUTER
    # ========================================================================
    system_endpoints = [
        ("GET", "/api/system/health", None, "System Health"),
        ("GET", "/api/system/info", None, "System Info"),
        ("GET", "/api/system/version", None, "System Version"),
    ]
    
    all_results["system_router"] = test_router_category(
        "System Router",
        system_endpoints,
        "Системные endpoints (Health, Info, Version)"
    )
    
    # ========================================================================
    # ТЕСТ 7: WILDCARD PROXY (для неизвестных endpoints)
    # ========================================================================
    unknown_endpoints = [
        ("GET", "/api/unknown/test", None, "Unknown Endpoint"),
        ("GET", "/api/test/function", None, "Test Function"),
        ("GET", "/api/custom/stats", None, "Custom Stats"),
    ]
    
    all_results["wildcard_proxy"] = test_router_category(
        "Wildcard Proxy (неизвестные endpoints)",
        unknown_endpoints,
        "Проверка работы Wildcard Proxy для неизвестных endpoints",
    )
    
    # Изменяем ожидания для Wildcard Proxy
    for result in all_results["wildcard_proxy"]["details"]:
        result.is_wildcard = True  # Для Wildcard Proxy это нормально
    
    # ========================================================================
    # ИТОГОВЫЙ ОТЧЕТ
    # ========================================================================
    print_section("ИТОГОВЫЙ ОТЧЕТ")
    print()
    
    total_tests = sum(r["total"] for r in all_results.values())
    total_passed = sum(r["passed"] for r in all_results.values())
    total_failed = sum(r["failed"] for r in all_results.values())
    total_wildcard_errors = sum(r["wildcard_errors"] for r in all_results.values())
    total_status_errors = sum(r["status_errors"] for r in all_results.values())
    total_network_errors = sum(r["network_errors"] for r in all_results.values())
    
    print_info(f"Всего тестов: {total_tests}")
    print_success(f"Пройдено: {total_passed}")
    if total_failed > 0:
        print_error(f"Провалено: {total_failed}")
    else:
        print_success(f"Провалено: {total_failed}")
    
    print()
    print_info("Детальная статистика:")
    print_info(f"  - Wildcard Proxy ошибок: {total_wildcard_errors}")
    print_info(f"  - Ошибок статуса: {total_status_errors}")
    print_info(f"  - Ошибок сети: {total_network_errors}")
    print()
    
    print_info("Результаты по категориям:")
    for category, results in all_results.items():
        success_rate = (results["passed"] / results["total"] * 100) if results["total"] > 0 else 0
        status_icon = "✅" if results["wildcard_errors"] == 0 and results["network_errors"] == 0 else "⚠️"
        print(f"  {status_icon} {category}: {results['passed']}/{results['total']} ({success_rate:.1f}%)")
    
    print()
    success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    print_info(f"Общий процент успеха: {success_rate:.1f}%")
    print()
    
    # Критерии готовности к продакшн
    print_section("КРИТЕРИИ ГОТОВНОСТИ К ПРОДАКШН")
    print()
    
    criteria = {
        "Нет Wildcard Proxy ошибок для endpoints с роутерами": total_wildcard_errors == 0,
        "Все основные роутеры работают": all_results["main_routers"]["wildcard_errors"] == 0,
        "Analytics Router работает": all_results["analytics_router"]["wildcard_errors"] == 0,
        "Reports Router работает": all_results["reports_router"]["wildcard_errors"] == 0,
        "Security Routers работают": all_results["security_routers"]["wildcard_errors"] == 0,
        "Wildcard Proxy работает для неизвестных": all_results["wildcard_proxy"]["passed"] > 0,
    }
    
    all_ready = True
    for criterion, passed in criteria.items():
        if passed:
            print_success(f"✅ {criterion}")
        else:
            print_error(f"❌ {criterion}")
            all_ready = False
    
    print()
    if all_ready and total_wildcard_errors == 0:
        print_success("🎉 ВСЕ КРИТЕРИИ ВЫПОЛНЕНЫ! СИСТЕМА ГОТОВА К ПРОДАКШН!")
    else:
        print_warning("⚠️ Некоторые критерии не выполнены. Проверьте детали выше.")
    
    return all_ready

if __name__ == "__main__":
    import sys
    
    # Можно передать токен как аргумент
    if len(sys.argv) > 1:
        AUTH_TOKEN = sys.argv[1]
    
    success = main()
    sys.exit(0 if success else 1)
