#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performance Analyzer for ALADDIN System
Анализатор производительности системы ALADDIN
"""

import time
import psutil
import requests
import json
from datetime import datetime
from typing import Dict, List, Any

class PerformanceAnalyzer:
    """Анализатор производительности системы"""
    
    def __init__(self):
        self.results = {}
        self.start_time = time.time()
    
    def analyze_system_resources(self) -> Dict[str, Any]:
        """Анализ системных ресурсов"""
        print("🔍 Анализ системных ресурсов...")
        
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Память
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_available = memory.available / (1024**3)  # GB
        
        # Диск
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        disk_free = disk.free / (1024**3)  # GB
        
        return {
            "cpu": {
                "percent": cpu_percent,
                "count": cpu_count,
                "status": "🟢 Низкая" if cpu_percent < 30 else "🟡 Средняя" if cpu_percent < 70 else "🔴 Высокая"
            },
            "memory": {
                "percent": memory_percent,
                "available_gb": round(memory_available, 2),
                "status": "🟢 Низкая" if memory_percent < 50 else "🟡 Средняя" if memory_percent < 80 else "🔴 Высокая"
            },
            "disk": {
                "percent": disk_percent,
                "free_gb": round(disk_free, 2),
                "status": "🟢 Низкая" if disk_percent < 70 else "🟡 Средняя" if disk_percent < 90 else "🔴 Высокая"
            }
        }
    
    def analyze_api_performance(self) -> Dict[str, Any]:
        """Анализ производительности API"""
        print("🌐 Анализ производительности API...")
        
        apis = [
            {"name": "Dashboard", "url": "http://localhost:5000/api/health"},
            {"name": "Search", "url": "http://localhost:5001/api/health"},
            {"name": "Alerts", "url": "http://localhost:5003/api/alerts/health"}
        ]
        
        results = {}
        
        for api in apis:
            try:
                start_time = time.time()
                response = requests.get(api["url"], timeout=5)
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000  # ms
                status_code = response.status_code
                
                results[api["name"]] = {
                    "response_time_ms": round(response_time, 2),
                    "status_code": status_code,
                    "status": "✅ OK" if status_code == 200 else "❌ ERROR",
                    "performance": "🟢 Быстро" if response_time < 100 else "🟡 Средне" if response_time < 500 else "🔴 Медленно"
                }
                
            except Exception as e:
                results[api["name"]] = {
                    "response_time_ms": None,
                    "status_code": None,
                    "status": f"❌ ERROR: {str(e)}",
                    "performance": "🔴 Недоступно"
                }
        
        return results
    
    def analyze_database_performance(self) -> Dict[str, Any]:
        """Анализ производительности базы данных"""
        print("🗄️ Анализ производительности базы данных...")
        
        try:
            # Тест поиска
            start_time = time.time()
            response = requests.get("http://localhost:5001/api/elasticsearch/search?query=test", timeout=10)
            end_time = time.time()
            
            search_time = (end_time - start_time) * 1000  # ms
            
            if response.status_code == 200:
                data = response.json()
                results_count = len(data.get("results", []))
                
                return {
                    "search_time_ms": round(search_time, 2),
                    "results_count": results_count,
                    "performance": "🟢 Быстро" if search_time < 200 else "🟡 Средне" if search_time < 1000 else "🔴 Медленно",
                    "status": "✅ OK"
                }
            else:
                return {
                    "search_time_ms": None,
                    "results_count": 0,
                    "performance": "🔴 Ошибка",
                    "status": f"❌ HTTP {response.status_code}"
                }
                
        except Exception as e:
            return {
                "search_time_ms": None,
                "results_count": 0,
                "performance": "🔴 Недоступно",
                "status": f"❌ ERROR: {str(e)}"
            }
    
    def analyze_processes(self) -> Dict[str, Any]:
        """Анализ процессов ALADDIN"""
        print("📊 Анализ процессов ALADDIN...")
        
        processes = []
        total_cpu = 0
        total_memory = 0
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'cmdline']):
            try:
                if proc.info['name'] == 'python3' and proc.info['cmdline']:
                    cmdline = ' '.join(proc.info['cmdline'])
                    if any(service in cmdline for service in ['dashboard_server.py', 'elasticsearch_api.py', 'alerts_api.py']):
                        processes.append({
                            "pid": proc.info['pid'],
                            "name": proc.info['name'],
                            "cpu_percent": proc.info['cpu_percent'],
                            "memory_percent": proc.info['memory_percent'],
                            "cmdline": cmdline
                        })
                        total_cpu += proc.info['cpu_percent'] or 0
                        total_memory += proc.info['memory_percent'] or 0
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return {
            "processes": processes,
            "total_cpu_percent": round(total_cpu, 2),
            "total_memory_percent": round(total_memory, 2),
            "process_count": len(processes)
        }
    
    def run_full_analysis(self) -> Dict[str, Any]:
        """Полный анализ производительности"""
        print("🚀 Запуск полного анализа производительности...")
        print("=" * 50)
        
        # Анализ системных ресурсов
        system_resources = self.analyze_system_resources()
        
        # Анализ API
        api_performance = self.analyze_api_performance()
        
        # Анализ базы данных
        db_performance = self.analyze_database_performance()
        
        # Анализ процессов
        processes = self.analyze_processes()
        
        # Общее время анализа
        total_time = time.time() - self.start_time
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "analysis_time_seconds": round(total_time, 2),
            "system_resources": system_resources,
            "api_performance": api_performance,
            "database_performance": db_performance,
            "processes": processes
        }
        
        return results
    
    def print_results(self, results: Dict[str, Any]):
        """Вывод результатов анализа"""
        print("\n" + "=" * 60)
        print("📊 РЕЗУЛЬТАТЫ АНАЛИЗА ПРОИЗВОДИТЕЛЬНОСТИ")
        print("=" * 60)
        
        # Системные ресурсы
        print("\n🖥️ СИСТЕМНЫЕ РЕСУРСЫ:")
        sys = results["system_resources"]
        print(f"   CPU: {sys['cpu']['percent']}% {sys['cpu']['status']} ({sys['cpu']['count']} ядер)")
        print(f"   Память: {sys['memory']['percent']}% {sys['memory']['status']} ({sys['memory']['available_gb']} GB свободно)")
        print(f"   Диск: {sys['disk']['percent']}% {sys['disk']['status']} ({sys['disk']['free_gb']} GB свободно)")
        
        # API производительность
        print("\n🌐 API ПРОИЗВОДИТЕЛЬНОСТЬ:")
        for name, perf in results["api_performance"].items():
            if perf["response_time_ms"]:
                print(f"   {name}: {perf['response_time_ms']}ms {perf['performance']} {perf['status']}")
            else:
                print(f"   {name}: {perf['status']}")
        
        # База данных
        print("\n🗄️ БАЗА ДАННЫХ:")
        db = results["database_performance"]
        if db["search_time_ms"]:
            print(f"   Поиск: {db['search_time_ms']}ms {db['performance']} ({db['results_count']} результатов)")
        else:
            print(f"   Поиск: {db['status']}")
        
        # Процессы
        print("\n📊 ПРОЦЕССЫ ALADDIN:")
        proc = results["processes"]
        print(f"   Всего процессов: {proc['process_count']}")
        print(f"   Общий CPU: {proc['total_cpu_percent']}%")
        print(f"   Общая память: {proc['total_memory_percent']}%")
        
        for p in proc["processes"]:
            print(f"   PID {p['pid']}: {p['cpu_percent']}% CPU, {p['memory_percent']}% RAM")
        
        print(f"\n⏱️ Время анализа: {results['analysis_time_seconds']} секунд")
        print("=" * 60)

def main():
    """Главная функция"""
    analyzer = PerformanceAnalyzer()
    results = analyzer.run_full_analysis()
    analyzer.print_results(results)
    
    # Сохранение результатов
    with open("performance_analysis.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Результаты сохранены в performance_analysis.json")

if __name__ == "__main__":
    main()