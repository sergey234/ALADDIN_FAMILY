#!/usr/bin/env python3
"""
ТЕСТИРОВАНИЕ ВСЕХ 240 ENDPOINTS
--------------------------------
Тестирует все endpoints из всех роутеров для полной проверки системы.

Дата: 2026-03-14
"""

import requests
import json
import re
import os
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

def extract_endpoints_from_file(file_path: str) -> List[Dict[str, Any]]:
    """Извлекает endpoints из файла роутера"""
    endpoints = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Паттерн для поиска декораторов роутера
        pattern = r'@router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']'
        
        matches = re.finditer(pattern, content, re.IGNORECASE)
        
        for match in matches:
            method = match.group(1).upper()
            path = match.group(2)
            
            # Получаем имя функции после декоратора
            func_pattern = rf'{re.escape(match.group(0))}.*?def\s+(\w+)\('
            func_match = re.search(func_pattern, content, re.DOTALL)
            func_name = func_match.group(1) if func_match else "unknown"
            
            endpoints.append({
                "method": method,
                "path": path,
                "function": func_name,
                "file": os.path.basename(file_path)
            })
    
    except Exception as e:
        print_warning(f"Ошибка при чтении {file_path}: {e}")
    
    return endpoints

def find_all_routers(base_path: str) -> List[str]:
    """Находит все файлы роутеров"""
    router_files = []
    
    # Ищем в app/routers/
    app_routers_path = os.path.join(base_path, "app/routers")
    if os.path.exists(app_routers_path):
        for file in os.listdir(app_routers_path):
            if file.endswith(".py") and not file.startswith("__"):
                router_files.append(os.path.join(app_routers_path, file))
    
    # Ищем в security/api/routers/
    security_routers_path = os.path.join(base_path, "security/api/routers")
    if os.path.exists(security_routers_path):
        for file in os.listdir(security_routers_path):
            if file.endswith(".py") and not file.startswith("__"):
                router_files.append(os.path.join(security_routers_path, file))
    
    return router_files

def test_endpoint(
    method: str,
    endpoint: str,
    expected_status: Any = [200, 401, 403, 422, 404],
    should_not_be_wildcard: bool = True,
    params: Optional[Dict[str, Any]] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """Тестирует endpoint"""
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Cache-Control": "no-cache",
        "Pragma": "no-cache"
    }
    
    if AUTH_TOKEN:
        headers["Authorization"] = f"Bearer {AUTH_TOKEN}"
    
    result = {
        "endpoint": endpoint,
        "method": method,
        "status": 0,
        "is_wildcard": False,
        "has_data": False,
        "error": None,
        "success": False
    }
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params, timeout=5)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=params, timeout=5)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=params, timeout=5)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=5)
        else:
            result["error"] = f"Неподдерживаемый метод: {method}"
            return result
        
        result["status"] = response.status_code
        
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
        
        result["is_wildcard"] = is_wildcard
        
        # Проверяем наличие данных
        has_data = False
        if isinstance(data, dict):
            keys_to_check = ["data", "result", "items", "list", "total", "period", "source", "success"]
            has_data = any(key in data for key in keys_to_check) or len(data) > 2
        
        result["has_data"] = has_data
        
        # Определяем успех
        if status_ok and (not should_not_be_wildcard or not is_wildcard):
            result["success"] = True
        else:
            if is_wildcard and should_not_be_wildcard:
                result["error"] = "Попал в Wildcard Proxy"
            elif not status_ok:
                result["error"] = f"Неожиданный статус {response.status_code}"
        
    except requests.exceptions.RequestException as e:
        result["error"] = f"Ошибка сети: {str(e)[:50]}"
    except Exception as e:
        result["error"] = f"Неожиданная ошибка: {str(e)[:50]}"
    
    return result

def main():
    """Основная функция тестирования"""
    print_section("ТЕСТИРОВАНИЕ ВСЕХ 240 ENDPOINTS")
    print()
    print_info(f"База URL: {BASE_URL}")
    if AUTH_TOKEN:
        print_info(f"Токен: {AUTH_TOKEN[:20]}...")
    else:
        print_warning("Токен не установлен - некоторые endpoints могут вернуть 401/403")
    print()
    
    # Определяем базовый путь проекта
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_path = os.path.join(script_dir, "../..")
    
    print_info("🔍 Поиск всех роутеров...")
    router_files = find_all_routers(base_path)
    
    print_info(f"✅ Найдено роутеров: {len(router_files)}")
    print()
    
    all_endpoints = []
    
    for router_file in router_files:
        endpoints = extract_endpoints_from_file(router_file)
        all_endpoints.extend(endpoints)
    
    print_info(f"✅ Всего endpoints найдено: {len(all_endpoints)}")
    print()
    
    # Группируем по файлам
    by_file = {}
    for endpoint in all_endpoints:
        file = endpoint["file"]
        if file not in by_file:
            by_file[file] = []
        by_file[file].append(endpoint)
    
    print_section("НАЧАЛО ТЕСТИРОВАНИЯ")
    print()
    
    total_tests = len(all_endpoints)
    passed = 0
    failed = 0
    wildcard_errors = 0
    status_errors = 0
    network_errors = 0
    
    results_by_file = {}
    
    # Тестируем по файлам
    for file, endpoints in sorted(by_file.items()):
        print_info(f"📄 Тестирование: {file} ({len(endpoints)} endpoints)")
        
        file_passed = 0
        file_failed = 0
        file_wildcard = 0
        
        for endpoint in endpoints:
            method = endpoint["method"]
            path = endpoint["path"]
            
            # Формируем полный путь
            if not path.startswith("/api"):
                if path.startswith("/"):
                    full_path = f"/api{path}"
                else:
                    full_path = f"/api/{path}"
            else:
                full_path = path
            
            result = test_endpoint(
                method=method,
                endpoint=full_path,
                should_not_be_wildcard=True
            )
            
            if result["success"]:
                passed += 1
                file_passed += 1
            else:
                failed += 1
                file_failed += 1
                
                if result["is_wildcard"]:
                    wildcard_errors += 1
                    file_wildcard += 1
                elif result["status"] == 0:
                    network_errors += 1
                else:
                    status_errors += 1
            
            time.sleep(0.05)  # Небольшая задержка между запросами
        
        results_by_file[file] = {
            "total": len(endpoints),
            "passed": file_passed,
            "failed": file_failed,
            "wildcard": file_wildcard
        }
        
        success_rate = (file_passed / len(endpoints) * 100) if len(endpoints) > 0 else 0
        status_icon = "✅" if file_wildcard == 0 and file_failed == 0 else "⚠️" if file_wildcard == 0 else "❌"
        print(f"   {status_icon} {file_passed}/{len(endpoints)} пройдено ({success_rate:.1f}%)")
        if file_wildcard > 0:
            print_warning(f"      Wildcard Proxy ошибок: {file_wildcard}")
        print()
    
    # Итоговый отчет
    print_section("ИТОГОВЫЙ ОТЧЕТ")
    print()
    
    print_info(f"Всего тестов: {total_tests}")
    print_success(f"Пройдено: {passed}")
    if failed > 0:
        print_error(f"Провалено: {failed}")
    else:
        print_success(f"Провалено: {failed}")
    
    print()
    print_info("Детальная статистика:")
    print_info(f"  - Wildcard Proxy ошибок: {wildcard_errors}")
    print_info(f"  - Ошибок статуса: {status_errors}")
    print_info(f"  - Ошибок сети: {network_errors}")
    print()
    
    success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
    print_info(f"Общий процент успеха: {success_rate:.1f}%")
    print()
    
    # Топ проблемных файлов
    if wildcard_errors > 0:
        print_warning("Файлы с Wildcard Proxy ошибками:")
        for file, stats in sorted(results_by_file.items(), key=lambda x: x[1]["wildcard"], reverse=True):
            if stats["wildcard"] > 0:
                print_warning(f"  - {file}: {stats['wildcard']} ошибок")
        print()
    
    # Критерии готовности
    print_section("КРИТЕРИИ ГОТОВНОСТИ К ПРОДАКШН")
    print()
    
    criteria = {
        "Нет Wildcard Proxy ошибок для endpoints с роутерами": wildcard_errors == 0,
        "Процент успеха >= 95%": success_rate >= 95,
        "Нет критических ошибок сети": network_errors < total_tests * 0.05,
    }
    
    all_ready = True
    for criterion, passed_crit in criteria.items():
        if passed_crit:
            print_success(f"✅ {criterion}")
        else:
            print_error(f"❌ {criterion}")
            all_ready = False
    
    print()
    if all_ready and wildcard_errors == 0:
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
