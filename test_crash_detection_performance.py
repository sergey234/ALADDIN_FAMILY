#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
СКРИПТ ТЕСТИРОВАНИЯ ПРОИЗВОДИТЕЛЬНОСТИ CRASH DETECTION API
Выполняет тесты всех эндпоинтов и измеряет время ответа
"""

import requests
import time
import json
import statistics
from datetime import datetime
from typing import List, Dict, Any, Tuple

# Конфигурация
BASE_URL = "http://149.154.65.180:8002"
REQUESTS_PER_ENDPOINT = 10
TARGET_TIME_MS = 15  # Целевое время ответа

# Цвета для вывода
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Печать заголовка"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}\n")

def print_result(icon: str, text: str, color: str = Colors.RESET):
    """Печать результата"""
    print(f"{color}{icon} {text}{Colors.RESET}")

def test_endpoint(
    method: str,
    endpoint: str,
    data: Dict[Any, Any] = None,
    headers: Dict[str, str] = None
) -> Tuple[float, int, Dict[Any, Any], bool]:
    """
    Тестирует один запрос к эндпоинту
    Возвращает: (время_ответа_ms, http_статус, ответ_json, sfm_интеграция)
    """
    url = f"{BASE_URL}{endpoint}"
    
    if headers is None:
        headers = {"Content-Type": "application/json"}
    
    start_time = time.perf_counter()
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        else:
            raise ValueError(f"Неподдерживаемый метод: {method}")
        
        elapsed_time = (time.perf_counter() - start_time) * 1000  # в миллисекундах
        
        # Парсим JSON ответ
        try:
            response_json = response.json()
        except:
            response_json = {}
        
        # Проверяем SFM интеграцию
        has_sfm = "source" in response_json and response_json.get("source") == "real_sfm"
        
        return elapsed_time, response.status_code, response_json, has_sfm
        
    except requests.exceptions.Timeout:
        elapsed_time = (time.perf_counter() - start_time) * 1000
        return elapsed_time, 0, {}, False
    except Exception as e:
        elapsed_time = (time.perf_counter() - start_time) * 1000
        return elapsed_time, 0, {"error": str(e)}, False

def test_endpoint_multiple(
    name: str,
    method: str,
    endpoint: str,
    data: Dict[Any, Any] = None,
    headers: Dict[str, str] = None,
    num_requests: int = REQUESTS_PER_ENDPOINT
) -> Dict[str, Any]:
    """
    Тестирует эндпоинт несколько раз и собирает статистику
    """
    print(f"\n{Colors.BOLD}Тестирование: {name}{Colors.RESET}")
    print(f"Эндпоинт: {method} {endpoint}")
    print(f"Количество запросов: {num_requests}")
    
    times = []
    statuses = []
    sfm_count = 0
    responses = []
    
    for i in range(1, num_requests + 1):
        time_ms, status, response_json, has_sfm = test_endpoint(method, endpoint, data, headers)
        
        times.append(time_ms)
        statuses.append(status)
        if has_sfm:
            sfm_count += 1
        responses.append(response_json)
        
        # Статус иконка
        status_icon = "✅" if status == 200 else "❌"
        sfm_icon = "✅ real_sfm" if has_sfm else "❌ no_sfm"
        time_color = Colors.GREEN if time_ms < TARGET_TIME_MS else Colors.RED if time_ms > 100 else Colors.YELLOW
        
        print(f"  {status_icon} Запрос #{i:2d}: {time_color}{time_ms:7.2f}ms{Colors.RESET} | HTTP {status} | {sfm_icon}")
        
        # Небольшая задержка между запросами
        time.sleep(0.1)
    
    # Статистика
    avg_time = statistics.mean(times)
    min_time = min(times)
    max_time = max(times)
    median_time = statistics.median(times)
    
    # 95-й перцентиль
    sorted_times = sorted(times)
    percentile_95 = sorted_times[int(len(sorted_times) * 0.95)] if len(sorted_times) > 0 else 0
    
    success_count = sum(1 for s in statuses if s == 200)
    success_rate = (success_count / num_requests) * 100
    sfm_rate = (sfm_count / num_requests) * 100
    
    # Оценка производительности
    meets_target = avg_time < TARGET_TIME_MS
    
    result = {
        "name": name,
        "endpoint": endpoint,
        "method": method,
        "num_requests": num_requests,
        "times": times,
        "avg_time": avg_time,
        "min_time": min_time,
        "max_time": max_time,
        "median_time": median_time,
        "percentile_95": percentile_95,
        "success_count": success_count,
        "success_rate": success_rate,
        "sfm_count": sfm_count,
        "sfm_rate": sfm_rate,
        "meets_target": meets_target,
        "responses": responses
    }
    
    # Вывод статистики
    print(f"\n{Colors.BOLD}Статистика:{Colors.RESET}")
    avg_color = Colors.GREEN if meets_target else Colors.RED
    print(f"  Среднее время: {avg_color}{avg_time:.2f}ms{Colors.RESET} (цель: <{TARGET_TIME_MS}ms)")
    print(f"  Минимум: {Colors.GREEN}{min_time:.2f}ms{Colors.RESET}")
    print(f"  Максимум: {Colors.RED if max_time > 100 else Colors.YELLOW}{max_time:.2f}ms{Colors.RESET}")
    print(f"  Медиана: {median_time:.2f}ms")
    print(f"  95-й перцентиль: {percentile_95:.2f}ms")
    print(f"  Успешность: {Colors.GREEN if success_rate == 100 else Colors.RED}{success_count}/{num_requests} ({success_rate:.1f}%){Colors.RESET}")
    print(f"  SFM интеграция: {Colors.GREEN if sfm_rate == 100 else Colors.YELLOW}{sfm_count}/{num_requests} ({sfm_rate:.1f}%){Colors.RESET}")
    
    if meets_target:
        print(f"  {Colors.GREEN}✅ Цель достигнута!{Colors.RESET}")
    else:
        deviation = avg_time / TARGET_TIME_MS
        print(f"  {Colors.RED}❌ Цель НЕ достигнута (в {deviation:.1f}x хуже){Colors.RESET}")
    
    return result

def main():
    """Основная функция тестирования"""
    print_header("🧪 ТЕСТИРОВАНИЕ ПРОИЗВОДИТЕЛЬНОСТИ CRASH DETECTION API")
    print(f"Сервер: {BASE_URL}")
    print(f"Дата тестирования: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Количество запросов на эндпоинт: {REQUESTS_PER_ENDPOINT}")
    print(f"Целевое время ответа: <{TARGET_TIME_MS}ms")
    
    # Проверка доступности сервера
    print(f"\n{Colors.BOLD}Проверка доступности сервера...{Colors.RESET}")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print_result("✅", f"Сервер доступен (HTTP {response.status_code})", Colors.GREEN)
        else:
            print_result("⚠️", f"Сервер отвечает с кодом {response.status_code}", Colors.YELLOW)
    except Exception as e:
        print_result("❌", f"Сервер недоступен: {str(e)}", Colors.RED)
        return
    
    results = []
    
    # 1. GET /api/health
    results.append(test_endpoint_multiple(
        "1️⃣ GET /api/health",
        "GET",
        "/api/health",
        num_requests=REQUESTS_PER_ENDPOINT
    ))
    
    # 2. GET /api/crash-detection/status
    results.append(test_endpoint_multiple(
        "2️⃣ GET /api/crash-detection/status",
        "GET",
        "/api/crash-detection/status",
        num_requests=REQUESTS_PER_ENDPOINT
    ))
    
    # 3. POST /api/crash-detection/setup
    results.append(test_endpoint_multiple(
        "3️⃣ POST /api/crash-detection/setup",
        "POST",
        "/api/crash-detection/setup",
        data={
            "latitude": 55.7558,
            "longitude": 37.6173,
            "radius": 500
        },
        num_requests=REQUESTS_PER_ENDPOINT
    ))
    
    # 4. POST /api/crash-detection/start
    results.append(test_endpoint_multiple(
        "4️⃣ POST /api/crash-detection/start",
        "POST",
        "/api/crash-detection/start",
        data={},
        num_requests=REQUESTS_PER_ENDPOINT
    ))
    
    # 5. POST /api/crash-detection/data
    results.append(test_endpoint_multiple(
        "5️⃣ POST /api/crash-detection/data",
        "POST",
        "/api/crash-detection/data",
        data={
            "accelerometer": {"x": 0, "y": 0, "z": 9.8},
            "gyroscope": {"x": 0, "y": 0, "z": 0},
            "speed": 0,
            "latitude": 55.7558,
            "longitude": 37.6173,
            "timestamp": time.time()
        },
        num_requests=REQUESTS_PER_ENDPOINT
    ))
    
    # 6. POST /api/crash-detection/alert
    results.append(test_endpoint_multiple(
        "6️⃣ POST /api/crash-detection/alert",
        "POST",
        "/api/crash-detection/alert",
        data={
            "latitude": 55.7558,
            "longitude": 37.6173,
            "severity": "high"
        },
        num_requests=REQUESTS_PER_ENDPOINT
    ))
    
    # 7. POST /api/crash-detection/stop
    results.append(test_endpoint_multiple(
        "7️⃣ POST /api/crash-detection/stop",
        "POST",
        "/api/crash-detection/stop",
        data={},
        num_requests=REQUESTS_PER_ENDPOINT
    ))
    
    # Итоговая статистика
    print_header("📊 ИТОГОВАЯ СТАТИСТИКА")
    
    all_times = []
    total_requests = 0
    total_success = 0
    total_sfm = 0
    
    for result in results:
        all_times.extend(result["times"])
        total_requests += result["num_requests"]
        total_success += result["success_count"]
        total_sfm += result["sfm_count"]
    
    overall_avg = statistics.mean(all_times) if all_times else 0
    overall_min = min(all_times) if all_times else 0
    overall_max = max(all_times) if all_times else 0
    
    print(f"{Colors.BOLD}Общие показатели:{Colors.RESET}")
    avg_color = Colors.GREEN if overall_avg < TARGET_TIME_MS else Colors.RED
    print(f"  Среднее время всех эндпоинтов: {avg_color}{overall_avg:.2f}ms{Colors.RESET} (цель: <{TARGET_TIME_MS}ms)")
    print(f"  Минимальное время: {Colors.GREEN}{overall_min:.2f}ms{Colors.RESET}")
    print(f"  Максимальное время: {Colors.RED if overall_max > 100 else Colors.YELLOW}{overall_max:.2f}ms{Colors.RESET}")
    print(f"  Общая успешность: {Colors.GREEN if total_success == total_requests else Colors.RED}{total_success}/{total_requests} ({total_success/total_requests*100:.1f}%){Colors.RESET}")
    print(f"  SFM интеграция: {Colors.GREEN if total_sfm == total_requests else Colors.YELLOW}{total_sfm}/{total_requests} ({total_sfm/total_requests*100:.1f}%){Colors.RESET}")
    
    if overall_avg >= TARGET_TIME_MS:
        deviation = overall_avg / TARGET_TIME_MS
        print(f"\n{Colors.RED}{Colors.BOLD}❌ ТРЕБУЕТСЯ ОПТИМИЗАЦИЯ ПРОИЗВОДИТЕЛЬНОСТИ{Colors.RESET}")
        print(f"{Colors.RED}Отклонение от цели: в {deviation:.1f}x хуже{Colors.RESET}")
    
    # Рейтинг эндпоинтов
    print(f"\n{Colors.BOLD}Рейтинг эндпоинтов по производительности:{Colors.RESET}")
    sorted_results = sorted(results, key=lambda x: x["avg_time"])
    medals = ["🥇", "🥈", "🥉"]
    
    for i, result in enumerate(sorted_results):
        medal = medals[i] if i < 3 else "  "
        status_icon = "✅" if result["meets_target"] else "❌"
        time_color = Colors.GREEN if result["avg_time"] < TARGET_TIME_MS else Colors.RED
        print(f"  {medal} {status_icon} {result['name']}: {time_color}{result['avg_time']:.2f}ms{Colors.RESET}")
    
    # Сохранение результатов в JSON
    output_file = f"crash_detection_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    output_data = {
        "test_date": datetime.now().isoformat(),
        "server": BASE_URL,
        "target_time_ms": TARGET_TIME_MS,
        "requests_per_endpoint": REQUESTS_PER_ENDPOINT,
        "overall_stats": {
            "avg_time_ms": overall_avg,
            "min_time_ms": overall_min,
            "max_time_ms": overall_max,
            "total_requests": total_requests,
            "total_success": total_success,
            "total_sfm": total_sfm,
            "success_rate": total_success / total_requests * 100 if total_requests > 0 else 0,
            "sfm_rate": total_sfm / total_requests * 100 if total_requests > 0 else 0
        },
        "endpoints": [
            {
                "name": r["name"],
                "endpoint": r["endpoint"],
                "method": r["method"],
                "avg_time_ms": r["avg_time"],
                "min_time_ms": r["min_time"],
                "max_time_ms": r["max_time"],
                "median_time_ms": r["median_time"],
                "percentile_95_ms": r["percentile_95"],
                "success_rate": r["success_rate"],
                "sfm_rate": r["sfm_rate"],
                "meets_target": r["meets_target"]
            }
            for r in results
        ]
    }
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n{Colors.GREEN}✅ Результаты сохранены в: {output_file}{Colors.RESET}")
    
    print_header("✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")

if __name__ == "__main__":
    main()
