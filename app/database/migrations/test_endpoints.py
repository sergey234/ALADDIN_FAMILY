#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для тестирования endpoints компонентов защиты
Проверяет работу всех endpoints с БД и graceful degradation
"""

import os
import sys
import requests
import json
from pathlib import Path
from typing import Dict, List, Optional

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Конфигурация
BASE_URL = os.getenv("API_BASE_URL", "https://aladdin-ai.ru")
TEST_TOKEN = os.getenv("TEST_TOKEN", "")  # Токен для тестирования

class Colors:
    """Цвета для вывода в консоль"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_success(message: str):
    """Вывести успешное сообщение"""
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")

def print_error(message: str):
    """Вывести сообщение об ошибке"""
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")

def print_warning(message: str):
    """Вывести предупреждение"""
    print(f"{Colors.YELLOW}⚠️ {message}{Colors.RESET}")

def print_info(message: str):
    """Вывести информационное сообщение"""
    print(f"{Colors.BLUE}ℹ️ {message}{Colors.RESET}")

def test_endpoint(
    method: str,
    url: str,
    expected_status: int = 200,
    data: Optional[Dict] = None,
    headers: Optional[Dict] = None
) -> tuple[bool, Optional[Dict], Optional[str]]:
    """Тестировать endpoint"""
    try:
        if headers is None:
            headers = {}
        
        if TEST_TOKEN:
            headers["Authorization"] = f"Bearer {TEST_TOKEN}"
        
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        else:
            return False, None, f"Неподдерживаемый метод: {method}"
        
        success = response.status_code == expected_status
        
        try:
            response_data = response.json()
        except:
            response_data = {"raw": response.text}
        
        return success, response_data, None
        
    except requests.exceptions.RequestException as e:
        return False, None, str(e)

def test_dark_web_endpoints() -> Dict[str, bool]:
    """Тестировать Dark Web endpoints"""
    print("\n" + "=" * 60)
    print("🌑 ТЕСТИРОВАНИЕ: Dark Web Monitoring")
    print("=" * 60)
    
    results = {}
    
    # Тест 1: Статистика
    print_info("Тест 1: GET /api/reports/dark-web/stats")
    success, data, error = test_endpoint("GET", f"{BASE_URL}/api/reports/dark-web/stats")
    if success:
        print_success(f"Статус: {data.get('totalLeaks', 'N/A')} утечек")
        results["stats"] = True
    else:
        print_error(f"Ошибка: {error or 'Неизвестная ошибка'}")
        results["stats"] = False
    
    # Тест 2: Список утечек
    print_info("Тест 2: GET /api/reports/dark-web/leaks")
    success, data, error = test_endpoint("GET", f"{BASE_URL}/api/reports/dark-web/leaks?limit=10")
    if success:
        leaks_count = len(data) if isinstance(data, list) else 0
        print_success(f"Получено утечек: {leaks_count}")
        results["leaks"] = True
    else:
        print_error(f"Ошибка: {error or 'Неизвестная ошибка'}")
        results["leaks"] = False
    
    # Тест 3: История сканирований
    print_info("Тест 3: GET /api/reports/dark-web/scans")
    success, data, error = test_endpoint("GET", f"{BASE_URL}/api/reports/dark-web/scans?limit=10")
    if success:
        scans_count = len(data) if isinstance(data, list) else 0
        print_success(f"Получено сканирований: {scans_count}")
        results["scans"] = True
    else:
        print_error(f"Ошибка: {error or 'Неизвестная ошибка'}")
        results["scans"] = False
    
    return results

def test_identity_theft_endpoints() -> Dict[str, bool]:
    """Тестировать Identity Theft endpoints"""
    print("\n" + "=" * 60)
    print("🛡️ ТЕСТИРОВАНИЕ: Identity Theft Protection")
    print("=" * 60)
    
    results = {}
    
    # Тест 1: Статистика
    print_info("Тест 1: GET /api/reports/identity-theft/stats")
    success, data, error = test_endpoint("GET", f"{BASE_URL}/api/reports/identity-theft/stats")
    if success:
        print_success(f"Статус: {data.get('totalAttempts', 'N/A')} попыток")
        results["stats"] = True
    else:
        print_error(f"Ошибка: {error or 'Неизвестная ошибка'}")
        results["stats"] = False
    
    # Тест 2: Список попыток
    print_info("Тест 2: GET /api/reports/identity-theft/attempts")
    success, data, error = test_endpoint("GET", f"{BASE_URL}/api/reports/identity-theft/attempts?limit=10")
    if success:
        attempts_count = len(data) if isinstance(data, list) else 0
        print_success(f"Получено попыток: {attempts_count}")
        results["attempts"] = True
    else:
        print_error(f"Ошибка: {error or 'Неизвестная ошибка'}")
        results["attempts"] = False
    
    return results

def test_location_bubble_endpoints() -> Dict[str, bool]:
    """Тестировать Location Bubble endpoints"""
    print("\n" + "=" * 60)
    print("📍 ТЕСТИРОВАНИЕ: Location Bubble")
    print("=" * 60)
    
    results = {}
    
    # Тест 1: Статистика
    print_info("Тест 1: GET /api/reports/privacy/location/stats")
    success, data, error = test_endpoint("GET", f"{BASE_URL}/api/reports/privacy/location/stats")
    if success:
        print_success(f"Статус: заблокировано {data.get('blockedRequests', 'N/A')} запросов")
        results["stats"] = True
    else:
        print_error(f"Ошибка: {error or 'Неизвестная ошибка'}")
        results["stats"] = False
    
    # Тест 2: Список запросов
    print_info("Тест 2: GET /api/reports/privacy/location/requests")
    success, data, error = test_endpoint("GET", f"{BASE_URL}/api/reports/privacy/location/requests?limit=10")
    if success:
        requests_count = len(data) if isinstance(data, list) else 0
        print_success(f"Получено запросов: {requests_count}")
        results["requests"] = True
    else:
        print_error(f"Ошибка: {error or 'Неизвестная ошибка'}")
        results["requests"] = False
    
    return results

def test_data_cleanup_endpoints() -> Dict[str, bool]:
    """Тестировать Data Cleanup endpoints"""
    print("\n" + "=" * 60)
    print("🧹 ТЕСТИРОВАНИЕ: Data Cleanup")
    print("=" * 60)
    
    results = {}
    
    # Тест 1: Статистика
    print_info("Тест 1: GET /api/reports/privacy/cleanup/stats")
    success, data, error = test_endpoint("GET", f"{BASE_URL}/api/reports/privacy/cleanup/stats")
    if success:
        freed = data.get('totalFreed', 0)
        freed_gb = freed / (1024 ** 3) if freed else 0
        print_success(f"Статус: освобождено {freed_gb:.2f} GB")
        results["stats"] = True
    else:
        print_error(f"Ошибка: {error or 'Неизвестная ошибка'}")
        results["stats"] = False
    
    # Тест 2: История очисток
    print_info("Тест 2: GET /api/reports/privacy/cleanup/records")
    success, data, error = test_endpoint("GET", f"{BASE_URL}/api/reports/privacy/cleanup/records?limit=10")
    if success:
        records_count = len(data) if isinstance(data, list) else 0
        print_success(f"Получено записей: {records_count}")
        results["records"] = True
    else:
        print_error(f"Ошибка: {error or 'Неизвестная ошибка'}")
        results["records"] = False
    
    return results

def test_anti_tracker_endpoints() -> Dict[str, bool]:
    """Тестировать Anti Tracker endpoints"""
    print("\n" + "=" * 60)
    print("🚫 ТЕСТИРОВАНИЕ: Anti Tracker")
    print("=" * 60)
    
    results = {}
    
    # Тест 1: Статистика
    print_info("Тест 1: GET /api/reports/privacy/tracker/stats")
    success, data, error = test_endpoint("GET", f"{BASE_URL}/api/reports/privacy/tracker/stats")
    if success:
        blocked = data.get('totalBlocked', 0)
        print_success(f"Статус: заблокировано {blocked} трекеров")
        results["stats"] = True
    else:
        print_error(f"Ошибка: {error or 'Неизвестная ошибка'}")
        results["stats"] = False
    
    # Тест 2: Топ трекеров
    print_info("Тест 2: GET /api/reports/privacy/tracker/top")
    success, data, error = test_endpoint("GET", f"{BASE_URL}/api/reports/privacy/tracker/top?limit=10")
    if success:
        trackers_count = len(data) if isinstance(data, list) else 0
        print_success(f"Получено трекеров: {trackers_count}")
        results["top"] = True
    else:
        print_error(f"Ошибка: {error or 'Неизвестная ошибка'}")
        results["top"] = False
    
    return results

def test_ai_categories_endpoints() -> Dict[str, bool]:
    """Тестировать AI Categories endpoints"""
    print("\n" + "=" * 60)
    print("🤖 ТЕСТИРОВАНИЕ: AI Categories")
    print("=" * 60)
    
    results = {}
    
    # Тест 1: Статистика
    print_info("Тест 1: GET /api/reports/ai-categories/stats")
    success, data, error = test_endpoint("GET", f"{BASE_URL}/api/reports/ai-categories/stats")
    if success:
        categorized = data.get('totalCategorized', 0)
        print_success(f"Статус: категоризировано {categorized} сайтов")
        results["stats"] = True
    else:
        print_error(f"Ошибка: {error or 'Неизвестная ошибка'}")
        results["stats"] = False
    
    # Тест 2: Отчеты
    print_info("Тест 2: GET /api/reports/ai-categories/reports")
    success, data, error = test_endpoint("GET", f"{BASE_URL}/api/reports/ai-categories/reports")
    if success:
        reports_count = len(data) if isinstance(data, list) else 0
        print_success(f"Получено отчетов: {reports_count}")
        results["reports"] = True
    else:
        print_error(f"Ошибка: {error or 'Неизвестная ошибка'}")
        results["reports"] = False
    
    return results

def test_graceful_degradation():
    """Тестировать graceful degradation при отсутствии таблиц"""
    print("\n" + "=" * 60)
    print("🛡️ ТЕСТИРОВАНИЕ: Graceful Degradation")
    print("=" * 60)
    
    print_warning("Этот тест проверяет, что endpoints возвращают пустые данные")
    print_warning("вместо ошибок при отсутствии таблиц в БД")
    
    # Тестируем все endpoints - они должны вернуть пустые данные без ошибок
    endpoints = [
        ("Dark Web Stats", f"{BASE_URL}/api/reports/dark-web/stats"),
        ("Identity Theft Stats", f"{BASE_URL}/api/reports/identity-theft/stats"),
        ("Location Stats", f"{BASE_URL}/api/reports/privacy/location/stats"),
        ("Data Cleanup Stats", f"{BASE_URL}/api/reports/privacy/cleanup/stats"),
        ("Anti Tracker Stats", f"{BASE_URL}/api/reports/privacy/tracker/stats"),
        ("AI Categories Stats", f"{BASE_URL}/api/reports/ai-categories/stats"),
    ]
    
    all_passed = True
    
    for name, url in endpoints:
        print_info(f"Тест: {name}")
        success, data, error = test_endpoint("GET", url)
        
        if success:
            # Проверяем что данные пустые (статистика = 0 или список пустой)
            if isinstance(data, dict):
                # Для статистики проверяем что значения = 0
                has_data = any(v != 0 and v is not None for v in data.values() if isinstance(v, (int, float)))
            elif isinstance(data, list):
                has_data = len(data) > 0
            else:
                has_data = False
            
            if not has_data:
                print_success(f"   ✅ Graceful degradation работает (пустые данные)")
            else:
                print_warning(f"   ⚠️ Есть данные (возможно таблицы уже созданы)")
        else:
            print_error(f"   ❌ Ошибка: {error}")
            all_passed = False
    
    return all_passed

def main():
    """Главная функция"""
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ ENDPOINTS: Компоненты защиты")
    print("=" * 60)
    print()
    
    if TEST_TOKEN:
        print_info(f"Используется токен: {TEST_TOKEN[:20]}...")
    else:
        print_warning("Токен не указан (TEST_TOKEN). Некоторые endpoints могут требовать авторизацию.")
    
    print_info(f"Base URL: {BASE_URL}")
    print()
    
    # Тестируем все компоненты
    all_results = {}
    
    all_results["dark_web"] = test_dark_web_endpoints()
    all_results["identity_theft"] = test_identity_theft_endpoints()
    all_results["location_bubble"] = test_location_bubble_endpoints()
    all_results["data_cleanup"] = test_data_cleanup_endpoints()
    all_results["anti_tracker"] = test_anti_tracker_endpoints()
    all_results["ai_categories"] = test_ai_categories_endpoints()
    
    # Тестируем graceful degradation
    all_results["graceful_degradation"] = test_graceful_degradation()
    
    # Итоговая статистика
    print("\n" + "=" * 60)
    print("📊 ИТОГОВАЯ СТАТИСТИКА")
    print("=" * 60)
    
    total_tests = 0
    passed_tests = 0
    
    for component, results in all_results.items():
        if isinstance(results, dict):
            component_total = len(results)
            component_passed = sum(1 for v in results.values() if v)
            total_tests += component_total
            passed_tests += component_passed
            
            status = "✅" if component_passed == component_total else "⚠️"
            print(f"{status} {component}: {component_passed}/{component_total}")
        else:
            total_tests += 1
            if results:
                passed_tests += 1
            status = "✅" if results else "❌"
            print(f"{status} {component}")
    
    print()
    print(f"Всего тестов: {total_tests}")
    print(f"Пройдено: {passed_tests}")
    print(f"Провалено: {total_tests - passed_tests}")
    
    if passed_tests == total_tests:
        print_success("\n✅ Все тесты пройдены!")
        return 0
    else:
        print_error(f"\n❌ Провалено тестов: {total_tests - passed_tests}")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️ Тестирование прервано пользователем")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
