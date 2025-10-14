#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Optimized Performance for ALADDIN System
Тестирование оптимизированной производительности системы ALADDIN
"""

import time
import requests
import json
from datetime import datetime
from typing import Dict, List, Any

class PerformanceTester:
    """Тестер производительности системы"""
    
    def __init__(self):
        self.results = {}
        self.start_time = time.time()
    
    def test_api_response_times(self, iterations: int = 10) -> Dict[str, Any]:
        """Тестирование времени отклика API"""
        print(f"🌐 Тестирование API ({iterations} запросов)...")
        
        apis = [
            {"name": "Dashboard", "url": "http://localhost:5000/api/health"},
            {"name": "Search", "url": "http://localhost:5001/api/health"},
            {"name": "Alerts", "url": "http://localhost:5003/api/alerts/health"}
        ]
        
        results = {}
        
        for api in apis:
            times = []
            success_count = 0
            
            for i in range(iterations):
                try:
                    start_time = time.time()
                    response = requests.get(api["url"], timeout=5)
                    end_time = time.time()
                    
                    response_time = (end_time - start_time) * 1000  # ms
                    times.append(response_time)
                    
                    if response.status_code == 200:
                        success_count += 1
                        
                except Exception as e:
                    times.append(None)
            
            # Статистика
            valid_times = [t for t in times if t is not None]
            if valid_times:
                avg_time = sum(valid_times) / len(valid_times)
                min_time = min(valid_times)
                max_time = max(valid_times)
            else:
                avg_time = min_time = max_time = 0
            
            results[api["name"]] = {
                "avg_response_time_ms": round(avg_time, 2),
                "min_response_time_ms": round(min_time, 2),
                "max_response_time_ms": round(max_time, 2),
                "success_rate": round((success_count / iterations) * 100, 2),
                "total_requests": iterations,
                "successful_requests": success_count
            }
        
        return results
    
    def test_database_performance(self, iterations: int = 5) -> Dict[str, Any]:
        """Тестирование производительности базы данных"""
        print(f"🗄️ Тестирование базы данных ({iterations} запросов)...")
        
        search_queries = [
            "test",
            "error",
            "security",
            "warning",
            "info"
        ]
        
        results = []
        
        for query in search_queries:
            times = []
            
            for i in range(iterations):
                try:
                    start_time = time.time()
                    response = requests.get(
                        f"http://localhost:5001/api/elasticsearch/search?query={query}",
                        timeout=10
                    )
                    end_time = time.time()
                    
                    response_time = (end_time - start_time) * 1000  # ms
                    times.append(response_time)
                    
                    if response.status_code == 200:
                        data = response.json()
                        results_count = len(data.get("results", []))
                    else:
                        results_count = 0
                        
                except Exception as e:
                    times.append(None)
                    results_count = 0
            
            # Статистика
            valid_times = [t for t in times if t is not None]
            if valid_times:
                avg_time = sum(valid_times) / len(valid_times)
            else:
                avg_time = 0
            
            results.append({
                "query": query,
                "avg_response_time_ms": round(avg_time, 2),
                "results_count": results_count,
                "success_rate": round((len(valid_times) / iterations) * 100, 2)
            })
        
        return results
    
    def test_concurrent_requests(self, concurrent_users: int = 10) -> Dict[str, Any]:
        """Тестирование конкурентных запросов"""
        print(f"👥 Тестирование конкурентных запросов ({concurrent_users} пользователей)...")
        
        import threading
        
        results = []
        threads = []
        
        def make_request(thread_id):
            start_time = time.time()
            try:
                response = requests.get("http://localhost:5000/api/health", timeout=5)
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000  # ms
                results.append({
                    "thread_id": thread_id,
                    "response_time_ms": round(response_time, 2),
                    "status_code": response.status_code,
                    "success": response.status_code == 200
                })
            except Exception as e:
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # ms
                results.append({
                    "thread_id": thread_id,
                    "response_time_ms": round(response_time, 2),
                    "status_code": None,
                    "success": False,
                    "error": str(e)
                })
        
        # Запуск конкурентных запросов
        start_time = time.time()
        
        for i in range(concurrent_users):
            thread = threading.Thread(target=make_request, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Ожидание завершения всех потоков
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_time = (end_time - start_time) * 1000  # ms
        
        # Статистика
        successful_requests = [r for r in results if r["success"]]
        success_rate = (len(successful_requests) / len(results)) * 100
        
        if successful_requests:
            avg_response_time = sum(r["response_time_ms"] for r in successful_requests) / len(successful_requests)
            max_response_time = max(r["response_time_ms"] for r in successful_requests)
            min_response_time = min(r["response_time_ms"] for r in successful_requests)
        else:
            avg_response_time = max_response_time = min_response_time = 0
        
        return {
            "concurrent_users": concurrent_users,
            "total_time_ms": round(total_time, 2),
            "success_rate": round(success_rate, 2),
            "avg_response_time_ms": round(avg_response_time, 2),
            "min_response_time_ms": round(min_response_time, 2),
            "max_response_time_ms": round(max_response_time, 2),
            "requests_per_second": round(concurrent_users / (total_time / 1000), 2)
        }
    
    def run_full_test(self) -> Dict[str, Any]:
        """Запуск полного тестирования"""
        print("🚀 Запуск полного тестирования производительности...")
        print("=" * 50)
        
        # Тестирование API
        api_results = self.test_api_response_times(10)
        
        # Тестирование базы данных
        db_results = self.test_database_performance(5)
        
        # Тестирование конкурентных запросов
        concurrent_results = self.test_concurrent_requests(10)
        
        # Общее время тестирования
        total_time = time.time() - self.start_time
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "test_time_seconds": round(total_time, 2),
            "api_performance": api_results,
            "database_performance": db_results,
            "concurrent_performance": concurrent_results
        }
        
        return results
    
    def print_results(self, results: Dict[str, Any]):
        """Вывод результатов тестирования"""
        print("\n" + "=" * 60)
        print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ ПРОИЗВОДИТЕЛЬНОСТИ")
        print("=" * 60)
        
        # API производительность
        print("\n🌐 API ПРОИЗВОДИТЕЛЬНОСТЬ:")
        for name, perf in results["api_performance"].items():
            print(f"   {name}:")
            print(f"     Среднее время: {perf['avg_response_time_ms']}ms")
            print(f"     Мин/Макс: {perf['min_response_time_ms']}ms / {perf['max_response_time_ms']}ms")
            print(f"     Успешность: {perf['success_rate']}%")
        
        # База данных
        print("\n🗄️ БАЗА ДАННЫХ:")
        for db_result in results["database_performance"]:
            print(f"   Запрос '{db_result['query']}': {db_result['avg_response_time_ms']}ms ({db_result['results_count']} результатов)")
        
        # Конкурентные запросы
        print("\n👥 КОНКУРЕНТНЫЕ ЗАПРОСЫ:")
        conc = results["concurrent_performance"]
        print(f"   Пользователей: {conc['concurrent_users']}")
        print(f"   Общее время: {conc['total_time_ms']}ms")
        print(f"   Успешность: {conc['success_rate']}%")
        print(f"   Запросов/сек: {conc['requests_per_second']}")
        print(f"   Среднее время: {conc['avg_response_time_ms']}ms")
        
        print(f"\n⏱️ Время тестирования: {results['test_time_seconds']} секунд")
        print("=" * 60)

def main():
    """Главная функция"""
    tester = PerformanceTester()
    results = tester.run_full_test()
    tester.print_results(results)
    
    # Сохранение результатов
    with open("performance_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Результаты сохранены в performance_test_results.json")

if __name__ == "__main__":
    main()