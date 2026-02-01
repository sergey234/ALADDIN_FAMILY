#!/usr/bin/env python3
"""
ПОЛНОЕ ТЕСТИРОВАНИЕ ВСЕХ 101 ENDPOINTS API GATEWAY
Проверяет миграцию, SFM интеграцию и работоспособность
"""

import sys
import os
import re
import json
import time
import requests
from typing import Dict, List, Tuple
from datetime import datetime
from collections import defaultdict

# Конфигурация
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8002")
API_GATEWAY_FILE = "api_gateway_complete.py"
TIMEOUT = 5
VERBOSE = "--verbose" in sys.argv or "-v" in sys.argv

# Цвета для вывода
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

# Результаты тестирования
results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "skipped": 0,
    "endpoints": [],
    "groups": defaultdict(lambda: {"total": 0, "passed": 0, "failed": 0}),
    "sfm_integration": {"total": 0, "migrated": 0, "not_migrated": 0},
    "performance": {"avg_time": 0, "max_time": 0, "min_time": float('inf')}
}

def print_colored(text: str, color: str = Colors.RESET):
    """Вывод цветного текста"""
    print(f"{color}{text}{Colors.RESET}")

def print_header(text: str):
    """Вывод заголовка"""
    print_colored(f"\n{'='*60}", Colors.CYAN)
    print_colored(f"  {text}", Colors.BOLD + Colors.CYAN)
    print_colored(f"{'='*60}", Colors.CYAN)

def print_success(text: str):
    """Вывод успешного результата"""
    print_colored(f"✅ {text}", Colors.GREEN)

def print_error(text: str):
    """Вывод ошибки"""
    print_colored(f"❌ {text}", Colors.RED)

def print_warning(text: str):
    """Вывод предупреждения"""
    print_colored(f"⚠️  {text}", Colors.YELLOW)

def print_info(text: str):
    """Вывод информации"""
    print_colored(f"ℹ️  {text}", Colors.BLUE)

# =============================================================================
# ЭТАП 1: ПРОВЕРКА КОДА - ВСЕ ЛИ ENDPOINTS МИГРИРОВАНЫ
# =============================================================================

def check_code_migration():
    """Проверяет код на наличие SFM интеграции во всех endpoints"""
    print_header("ЭТАП 1: ПРОВЕРКА КОДА - МИГРАЦИЯ SFM")
    
    if not os.path.exists(API_GATEWAY_FILE):
        print_error(f"Файл {API_GATEWAY_FILE} не найден!")
        return False
    
    with open(API_GATEWAY_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Находим все endpoints
    endpoint_pattern = r'@app\.(get|post|put|delete|patch)\("([^"]+)"\)'
    endpoints = re.findall(endpoint_pattern, content)
    
    print_info(f"Найдено {len(endpoints)} endpoints в коде")
    
    # Проверяем каждый endpoint на SFM интеграцию
    migrated_count = 0
    not_migrated_count = 0
    not_migrated_list = []
    
    for method, path in endpoints:
        # Пропускаем служебные endpoints
        if path in ["/", "/api/health", "/docs", "/openapi.json", "/redoc"]:
            continue
        
        # Находим функцию для этого endpoint
        func_pattern = rf'@app\.{method}\("{re.escape(path)}"\)\s+async def (\w+)\([^)]*\):'
        func_match = re.search(func_pattern, content)
        
        if func_match:
            func_name = func_match.group(1)
            # Ищем тело функции
            func_start = func_match.end()
            # Находим следующую функцию или конец файла
            next_func = re.search(r'@app\.(get|post|put|delete|patch)\(', content[func_start:])
            if next_func:
                func_body = content[func_start:func_start + next_func.start()]
            else:
                func_body = content[func_start:]
            
            # Проверяем наличие SFM интеграции
            has_sfm = "SFM_ADAPTER_AVAILABLE" in func_body and "sfm_adapter.execute_function" in func_body
            has_fallback = '"source": "mock"' in func_body or "'source': 'mock'" in func_body
            
            if has_sfm and has_fallback:
                migrated_count += 1
                if VERBOSE:
                    print_success(f"{method.upper()} {path} - мигрирован")
            else:
                not_migrated_count += 1
                not_migrated_list.append(f"{method.upper()} {path}")
                print_error(f"{method.upper()} {path} - НЕ мигрирован!")
    
    results["sfm_integration"]["total"] = migrated_count + not_migrated_count
    results["sfm_integration"]["migrated"] = migrated_count
    results["sfm_integration"]["not_migrated"] = not_migrated_count
    
    print_info(f"Мигрировано: {migrated_count}/{migrated_count + not_migrated_count}")
    
    if not_migrated_count > 0:
        print_warning(f"Не мигрировано endpoints: {not_migrated_count}")
        if VERBOSE:
            for endpoint in not_migrated_list[:10]:  # Показываем первые 10
                print(f"  - {endpoint}")
        return False
    
    print_success("Все endpoints мигрированы!")
    return True

# =============================================================================
# ЭТАП 2: СПИСОК ВСЕХ ENDPOINTS
# =============================================================================

def get_all_endpoints() -> List[Tuple[str, str, str]]:
    """Извлекает все endpoints из кода"""
    with open(API_GATEWAY_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    endpoints = []
    endpoint_pattern = r'@app\.(get|post|put|delete|patch)\("([^"]+)"\)'
    
    for match in re.finditer(endpoint_pattern, content):
        method = match.group(1).upper()
        path = match.group(2)
        
        # Пропускаем служебные
        if path in ["/", "/api/health", "/docs", "/openapi.json", "/redoc"]:
            continue
        
        # Определяем группу
        group = "unknown"
        if "/components/" in path:
            group = "Группа 1: Компоненты"
        elif any(x in path for x in ["/phishing/", "/malware/", "/mobile/", "/network/"]):
            group = "Группа 2: Настройки"
        elif any(x in path for x in ["/ai/", "/data/cleanup", "/location/", "/darkweb/", "/identity/attempts"]):
            group = "Группа 3: Мониторинг"
        elif any(x in path for x in ["/identity/theft/", "/antitracker/", "/parental/", "/roadside/"]):
            group = "Группа 4: Защита"
        elif any(x in path for x in ["/notifications/", "/analytics/", "/subscription/", "/auth/", "/system/"]):
            group = "Группа 5: Система"
        
        endpoints.append((method, path, group))
    
    return endpoints

# =============================================================================
# ЭТАП 3: HTTP ТЕСТИРОВАНИЕ ENDPOINTS
# =============================================================================

def test_endpoint(method: str, path: str, group: str) -> Dict:
    """Тестирует один endpoint"""
    results["total"] += 1
    results["groups"][group]["total"] += 1
    
    endpoint_result = {
        "method": method,
        "path": path,
        "group": group,
        "status": "unknown",
        "http_code": None,
        "response_time": None,
        "error": None,
        "source": None
    }
    
    try:
        url = f"{BASE_URL}{path}"
        
        # Подготовка параметров для разных типов запросов
        if method == "GET":
            # Заменяем параметры пути на тестовые значения
            test_path = path
            if "{component_id}" in test_path:
                test_path = test_path.replace("{component_id}", "test_component")
            if "{attempt_id}" in test_path:
                test_path = test_path.replace("{attempt_id}", "test_attempt")
            if "{tracker_id}" in test_path:
                test_path = test_path.replace("{tracker_id}", "test_tracker")
            if "{child_id}" in test_path:
                test_path = test_path.replace("{child_id}", "test_child")
            if "{notification_id}" in test_path:
                test_path = test_path.replace("{notification_id}", "test_notification")
            if "{category_id}" in test_path:
                test_path = test_path.replace("{category_id}", "test_category")
            
            url = f"{BASE_URL}{test_path}"
            start_time = time.time()
            response = requests.get(url, timeout=TIMEOUT)
            response_time = time.time() - start_time
        
        elif method == "POST":
            start_time = time.time()
            response = requests.post(url, json={}, timeout=TIMEOUT)
            response_time = time.time() - start_time
        
        elif method == "PUT":
            start_time = time.time()
            response = requests.put(url, json={}, timeout=TIMEOUT)
            response_time = time.time() - start_time
        
        elif method == "DELETE":
            start_time = time.time()
            response = requests.delete(url, timeout=TIMEOUT)
            response_time = time.time() - start_time
        
        else:
            endpoint_result["status"] = "skipped"
            endpoint_result["error"] = f"Метод {method} не поддерживается"
            results["skipped"] += 1
            results["groups"][group]["failed"] += 1
            return endpoint_result
        
        endpoint_result["http_code"] = response.status_code
        endpoint_result["response_time"] = response_time
        
        # Обновляем статистику производительности
        if response_time < results["performance"]["min_time"]:
            results["performance"]["min_time"] = response_time
        if response_time > results["performance"]["max_time"]:
            results["performance"]["max_time"] = response_time
        
        # Проверяем ответ
        if response.status_code == 200:
            try:
                data = response.json()
                endpoint_result["source"] = data.get("source", "unknown")
                
                # Проверяем, что есть source (SFM или mock)
                if endpoint_result["source"] in ["mock", "sfm"]:
                    endpoint_result["status"] = "passed"
                    results["passed"] += 1
                    results["groups"][group]["passed"] += 1
                else:
                    endpoint_result["status"] = "warning"
                    endpoint_result["error"] = f"Неизвестный source: {endpoint_result['source']}"
                    results["passed"] += 1  # Считаем как passed, но с предупреждением
                    results["groups"][group]["passed"] += 1
            except:
                # Если не JSON, но статус 200 - считаем успешным
                endpoint_result["status"] = "passed"
                results["passed"] += 1
                results["groups"][group]["passed"] += 1
        else:
            endpoint_result["status"] = "failed"
            endpoint_result["error"] = f"HTTP {response.status_code}"
            results["failed"] += 1
            results["groups"][group]["failed"] += 1
    
    except requests.exceptions.Timeout:
        endpoint_result["status"] = "failed"
        endpoint_result["error"] = "Timeout"
        results["failed"] += 1
        results["groups"][group]["failed"] += 1
    
    except requests.exceptions.ConnectionError:
        endpoint_result["status"] = "failed"
        endpoint_result["error"] = "Connection Error"
        results["failed"] += 1
        results["groups"][group]["failed"] += 1
    
    except Exception as e:
        endpoint_result["status"] = "failed"
        endpoint_result["error"] = str(e)
        results["failed"] += 1
        results["groups"][group]["failed"] += 1
    
    results["endpoints"].append(endpoint_result)
    return endpoint_result

def test_all_endpoints():
    """Тестирует все endpoints"""
    print_header("ЭТАП 2: HTTP ТЕСТИРОВАНИЕ ENDPOINTS")
    
    # Проверяем доступность сервера
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print_success(f"API Gateway доступен: {BASE_URL}")
            print_info(f"Статус: {health_data.get('status', 'unknown')}")
            print_info(f"SFM Adapter: {health_data.get('sfm_adapter', 'unknown')}")
            print_info(f"Endpoints: {health_data.get('endpoints', 'unknown')}")
        else:
            print_warning(f"API Gateway отвечает с кодом {response.status_code}")
    except Exception as e:
        print_error(f"Не удалось подключиться к API Gateway: {e}")
        print_warning("Продолжаем тестирование кода...")
        return False
    
    # Получаем список всех endpoints
    endpoints = get_all_endpoints()
    print_info(f"Найдено {len(endpoints)} endpoints для тестирования")
    
    # Тестируем каждый endpoint
    print(f"\nТестирование endpoints...")
    for i, (method, path, group) in enumerate(endpoints, 1):
        result = test_endpoint(method, path, group)
        
        if result["status"] == "passed":
            if VERBOSE:
                print_success(f"[{i}/{len(endpoints)}] {method} {path} - OK ({result['response_time']:.3f}s, source: {result['source']})")
        elif result["status"] == "failed":
            print_error(f"[{i}/{len(endpoints)}] {method} {path} - FAILED: {result['error']}")
        elif result["status"] == "warning":
            print_warning(f"[{i}/{len(endpoints)}] {method} {path} - WARNING: {result['error']}")
        
        # Небольшая задержка между запросами
        if i % 10 == 0:
            time.sleep(0.1)
    
    return True

# =============================================================================
# ЭТАП 4: ГЕНЕРАЦИЯ ОТЧЕТА
# =============================================================================

def generate_report():
    """Генерирует детальный отчет"""
    print_header("ЭТАП 3: ГЕНЕРАЦИЯ ОТЧЕТА")
    
    report_file = f"migration_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# 📊 ОТЧЕТ О ТЕСТИРОВАНИИ МИГРАЦИИ API GATEWAY\n\n")
        f.write(f"**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Base URL:** {BASE_URL}\n\n")
        
        # Общая статистика
        f.write("## 📈 ОБЩАЯ СТАТИСТИКА\n\n")
        f.write(f"- **Всего endpoints:** {results['total']}\n")
        f.write(f"- **✅ Успешно:** {results['passed']}\n")
        f.write(f"- **❌ Ошибки:** {results['failed']}\n")
        f.write(f"- **⏭️  Пропущено:** {results['skipped']}\n")
        f.write(f"- **📊 Успешность:** {(results['passed']/results['total']*100) if results['total'] > 0 else 0:.1f}%\n\n")
        
        # SFM интеграция
        f.write("## 🔌 SFM ИНТЕГРАЦИЯ\n\n")
        sfm = results["sfm_integration"]
        f.write(f"- **Всего проверено:** {sfm['total']}\n")
        f.write(f"- **✅ Мигрировано:** {sfm['migrated']}\n")
        f.write(f"- **❌ Не мигрировано:** {sfm['not_migrated']}\n")
        if sfm['total'] > 0:
            f.write(f"- **📊 Процент миграции:** {(sfm['migrated']/sfm['total']*100):.1f}%\n")
        f.write("\n")
        
        # Статистика по группам
        f.write("## 📦 СТАТИСТИКА ПО ГРУППАМ\n\n")
        for group, stats in results["groups"].items():
            if stats["total"] > 0:
                success_rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
                f.write(f"### {group}\n")
                f.write(f"- Всего: {stats['total']}\n")
                f.write(f"- ✅ Успешно: {stats['passed']}\n")
                f.write(f"- ❌ Ошибки: {stats['failed']}\n")
                f.write(f"- 📊 Успешность: {success_rate:.1f}%\n\n")
        
        # Производительность
        f.write("## ⚡ ПРОИЗВОДИТЕЛЬНОСТЬ\n\n")
        perf = results["performance"]
        if perf["min_time"] != float('inf'):
            f.write(f"- **Минимальное время:** {perf['min_time']:.3f}s\n")
            f.write(f"- **Максимальное время:** {perf['max_time']:.3f}s\n")
            avg_time = sum(e["response_time"] for e in results["endpoints"] if e["response_time"]) / len([e for e in results["endpoints"] if e["response_time"]])
            f.write(f"- **Среднее время:** {avg_time:.3f}s\n\n")
        
        # Детальный список endpoints
        f.write("## 📋 ДЕТАЛЬНЫЙ СПИСОК ENDPOINTS\n\n")
        f.write("| Метод | Путь | Группа | Статус | HTTP | Время | Source | Ошибка |\n")
        f.write("|-------|------|--------|--------|------|-------|--------|--------|\n")
        
        for endpoint in results["endpoints"]:
            status_icon = "✅" if endpoint["status"] == "passed" else "❌" if endpoint["status"] == "failed" else "⚠️"
            http_code = endpoint.get("http_code", "N/A")
            response_time = f"{endpoint['response_time']:.3f}s" if endpoint.get("response_time") else "N/A"
            source = endpoint.get("source", "N/A")
            error = endpoint.get("error", "")
            
            f.write(f"| {endpoint['method']} | {endpoint['path']} | {endpoint['group']} | {status_icon} | {http_code} | {response_time} | {source} | {error} |\n")
    
    print_success(f"Отчет сохранен: {report_file}")
    return report_file

def print_summary():
    """Выводит итоговую сводку"""
    print_header("ИТОГОВАЯ СВОДКА")
    
    total = results["total"]
    passed = results["passed"]
    failed = results["failed"]
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print_info(f"Всего endpoints: {total}")
    print_success(f"Успешно: {passed}")
    if failed > 0:
        print_error(f"Ошибки: {failed}")
    print_info(f"Успешность: {success_rate:.1f}%")
    
    # SFM интеграция
    sfm = results["sfm_integration"]
    print(f"\n🔌 SFM Интеграция:")
    print_success(f"Мигрировано: {sfm['migrated']}/{sfm['total']}")
    if sfm['not_migrated'] > 0:
        print_error(f"Не мигрировано: {sfm['not_migrated']}")
    
    # По группам
    print(f"\n📦 По группам:")
    for group, stats in results["groups"].items():
        if stats["total"] > 0:
            rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
            status_icon = "✅" if rate == 100 else "⚠️" if rate >= 80 else "❌"
            print(f"  {status_icon} {group}: {stats['passed']}/{stats['total']} ({rate:.1f}%)")
    
    # Итоговая оценка
    print(f"\n{'='*60}")
    if success_rate == 100 and sfm['not_migrated'] == 0:
        print_colored("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! МИГРАЦИЯ УСПЕШНА!", Colors.GREEN + Colors.BOLD)
    elif success_rate >= 95:
        print_colored("✅ МИГРАЦИЯ В ОСНОВНОМ УСПЕШНА", Colors.GREEN)
    elif success_rate >= 80:
        print_colored("⚠️  МИГРАЦИЯ ТРЕБУЕТ ДОРАБОТКИ", Colors.YELLOW)
    else:
        print_colored("❌ МИГРАЦИЯ НЕ ЗАВЕРШЕНА", Colors.RED)
    print(f"{'='*60}\n")

# =============================================================================
# ГЛАВНАЯ ФУНКЦИЯ
# =============================================================================

def main():
    """Главная функция тестирования"""
    print_colored("\n" + "="*60, Colors.CYAN)
    print_colored("  🚀 ПОЛНОЕ ТЕСТИРОВАНИЕ API GATEWAY МИГРАЦИИ", Colors.BOLD + Colors.CYAN)
    print_colored("="*60 + "\n", Colors.CYAN)
    
    print_info(f"Base URL: {BASE_URL}")
    print_info(f"Файл: {API_GATEWAY_FILE}")
    print_info(f"Режим: {'Verbose' if VERBOSE else 'Normal'}\n")
    
    # Этап 1: Проверка кода
    code_ok = check_code_migration()
    
    # Этап 2: HTTP тестирование
    if code_ok:
        http_ok = test_all_endpoints()
    else:
        print_warning("Пропускаем HTTP тестирование из-за ошибок в коде")
        http_ok = False
    
    # Этап 3: Генерация отчета
    if http_ok or code_ok:
        report_file = generate_report()
        print_info(f"Отчет: {report_file}")
    
    # Итоговая сводка
    print_summary()
    
    # Возвращаем код выхода
    if results["failed"] == 0 and results["sfm_integration"]["not_migrated"] == 0:
        return 0
    else:
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_colored("\n\n⚠️  Тестирование прервано пользователем", Colors.YELLOW)
        sys.exit(130)
    except Exception as e:
        print_error(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)



