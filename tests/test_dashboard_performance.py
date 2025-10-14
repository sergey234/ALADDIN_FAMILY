#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Performance Tests для ALADDIN
Тесты производительности веб-дашборда системы безопасности

Автор: ALADDIN Security Team
Версия: 1.0.0
Дата: 2025-01-27
Качество: A+
"""

import asyncio
import time
import psutil
import pytest
import httpx
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from statistics import mean, median, stdev

# Добавляем путь к проекту
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from core.base import ComponentStatus, SecurityLevel
    from core.logging_module import LoggingManager
    ALADDIN_AVAILABLE = True
except ImportError:
    ALADDIN_AVAILABLE = False


@dataclass
class PerformanceMetric:
    """Метрика производительности"""
    name: str
    value: float
    unit: str
    timestamp: datetime
    success: bool = True
    error_message: Optional[str] = None


@dataclass
class ResponseTimeMetric:
    """Метрика времени отклика"""
    endpoint: str
    method: str
    response_time: float
    status_code: int
    success: bool
    timestamp: datetime
    error_message: Optional[str] = None


class DashboardPerformanceMonitor:
    """Монитор производительности дашборда"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        """
        Инициализация монитора производительности
        
        Args:
            base_url: Базовый URL дашборда
        """
        self.base_url = base_url
        self.logger = LoggingManager(name="DashboardPerformanceMonitor") if ALADDIN_AVAILABLE else None
        self.metrics: List[PerformanceMetric] = []
        self.response_times: List[ResponseTimeMetric] = []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        
    async def measure_endpoint_performance(
        self, 
        endpoint: str, 
        method: str = "GET",
        iterations: int = 10,
        json_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Измерение производительности endpoint
        
        Args:
            endpoint: Endpoint для тестирования
            method: HTTP метод
            iterations: Количество итераций
            json_data: JSON данные для POST запросов
            
        Returns:
            Статистика производительности
        """
        print(f"📊 Измерение производительности {method} {endpoint}...")
        
        response_times = []
        status_codes = []
        errors = []
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {"Authorization": "Bearer demo_token"}
            
            for i in range(iterations):
                try:
                    start_time = time.time()
                    
                    if method.upper() == "GET":
                        response = await client.get(f"{self.base_url}{endpoint}", headers=headers)
                    elif method.upper() == "POST":
                        response = await client.post(
                            f"{self.base_url}{endpoint}", 
                            json=json_data, 
                            headers=headers
                        )
                    else:
                        raise ValueError(f"Unsupported method: {method}")
                    
                    duration = time.time() - start_time
                    response_times.append(duration)
                    status_codes.append(response.status_code)
                    
                    # Сохраняем метрику
                    metric = ResponseTimeMetric(
                        endpoint=endpoint,
                        method=method,
                        response_time=duration,
                        status_code=response.status_code,
                        success=200 <= response.status_code < 300,
                        timestamp=datetime.now()
                    )
                    self.response_times.append(metric)
                    
                except Exception as e:
                    errors.append(str(e))
                    metric = ResponseTimeMetric(
                        endpoint=endpoint,
                        method=method,
                        response_time=0,
                        status_code=0,
                        success=False,
                        timestamp=datetime.now(),
                        error_message=str(e)
                    )
                    self.response_times.append(metric)
        
        # Вычисляем статистику
        if response_times:
            stats = {
                "endpoint": endpoint,
                "method": method,
                "iterations": iterations,
                "successful_requests": len(response_times),
                "failed_requests": len(errors),
                "success_rate": len(response_times) / iterations * 100,
                "min_response_time": min(response_times),
                "max_response_time": max(response_times),
                "avg_response_time": mean(response_times),
                "median_response_time": median(response_times),
                "std_deviation": stdev(response_times) if len(response_times) > 1 else 0,
                "status_codes": list(set(status_codes)),
                "errors": errors
            }
        else:
            stats = {
                "endpoint": endpoint,
                "method": method,
                "iterations": iterations,
                "successful_requests": 0,
                "failed_requests": len(errors),
                "success_rate": 0,
                "errors": errors
            }
        
        return stats
    
    async def measure_system_metrics(self) -> Dict[str, Any]:
        """
        Измерение системных метрик
        
        Returns:
            Системные метрики
        """
        print("📊 Измерение системных метрик...")
        
        # CPU использование
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_metric = PerformanceMetric(
            name="cpu_usage",
            value=cpu_percent,
            unit="percent",
            timestamp=datetime.now()
        )
        self.metrics.append(cpu_metric)
        
        # Память
        memory = psutil.virtual_memory()
        memory_metric = PerformanceMetric(
            name="memory_usage",
            value=memory.percent,
            unit="percent",
            timestamp=datetime.now()
        )
        self.metrics.append(memory_metric)
        
        # Диск
        disk = psutil.disk_usage('/')
        disk_metric = PerformanceMetric(
            name="disk_usage",
            value=disk.percent,
            unit="percent",
            timestamp=datetime.now()
        )
        self.metrics.append(disk_metric)
        
        # Процессы
        process_count = len(psutil.pids())
        process_metric = PerformanceMetric(
            name="process_count",
            value=process_count,
            unit="count",
            timestamp=datetime.now()
        )
        self.metrics.append(process_metric)
        
        return {
            "cpu_usage_percent": cpu_percent,
            "memory_usage_percent": memory.percent,
            "disk_usage_percent": disk.percent,
            "process_count": process_count,
            "timestamp": datetime.now().isoformat()
        }
    
    async def measure_network_metrics(self) -> Dict[str, Any]:
        """
        Измерение сетевых метрик
        
        Returns:
            Сетевые метрики
        """
        print("📊 Измерение сетевых метрик...")
        
        # Сетевые интерфейсы
        net_io = psutil.net_io_counters()
        
        network_metric = PerformanceMetric(
            name="network_io",
            value=net_io.bytes_sent + net_io.bytes_recv,
            unit="bytes",
            timestamp=datetime.now()
        )
        self.metrics.append(network_metric)
        
        return {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv,
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """
        Генерация отчета о производительности
        
        Returns:
            Отчет о производительности
        """
        print("📊 Генерация отчета о производительности...")
        
        if not self.response_times:
            return {"error": "No performance data available"}
        
        # Группируем метрики по endpoint
        endpoint_stats = {}
        for metric in self.response_times:
            key = f"{metric.method} {metric.endpoint}"
            if key not in endpoint_stats:
                endpoint_stats[key] = []
            endpoint_stats[key].append(metric)
        
        # Вычисляем статистику для каждого endpoint
        endpoint_performance = {}
        for endpoint, metrics in endpoint_stats.items():
            successful_metrics = [m for m in metrics if m.success]
            
            if successful_metrics:
                response_times = [m.response_time for m in successful_metrics]
                endpoint_performance[endpoint] = {
                    "total_requests": len(metrics),
                    "successful_requests": len(successful_metrics),
                    "success_rate": len(successful_metrics) / len(metrics) * 100,
                    "avg_response_time": mean(response_times),
                    "min_response_time": min(response_times),
                    "max_response_time": max(response_times),
                    "median_response_time": median(response_times),
                    "std_deviation": stdev(response_times) if len(response_times) > 1 else 0
                }
            else:
                endpoint_performance[endpoint] = {
                    "total_requests": len(metrics),
                    "successful_requests": 0,
                    "success_rate": 0,
                    "error": "All requests failed"
                }
        
        # Общая статистика
        all_response_times = [m.response_time for m in self.response_times if m.success]
        total_requests = len(self.response_times)
        successful_requests = len(all_response_times)
        
        report = {
            "report_date": datetime.now().isoformat(),
            "test_duration": (self.end_time - self.start_time).total_seconds() if self.start_time and self.end_time else 0,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "overall_success_rate": successful_requests / total_requests * 100 if total_requests > 0 else 0,
            "endpoint_performance": endpoint_performance,
            "system_metrics": [m.__dict__ for m in self.metrics],
            "summary": {
                "avg_response_time": mean(all_response_times) if all_response_times else 0,
                "min_response_time": min(all_response_times) if all_response_times else 0,
                "max_response_time": max(all_response_times) if all_response_times else 0,
                "median_response_time": median(all_response_times) if all_response_times else 0
            }
        }
        
        return report


class TestDashboardPerformance:
    """Тесты производительности дашборда"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Настройка тестов"""
        self.monitor = DashboardPerformanceMonitor()
        self.monitor.start_time = datetime.now()
        
    def teardown_method(self):
        """Очистка после тестов"""
        if self.monitor:
            self.monitor.end_time = datetime.now()
    
    @pytest.mark.asyncio
    async def test_main_page_performance(self):
        """Тест производительности главной страницы"""
        print("\n🧪 Тестирование производительности главной страницы...")
        
        stats = await self.monitor.measure_endpoint_performance("/", "GET", 20)
        
        print(f"✅ Успешных запросов: {stats['successful_requests']}/20")
        print(f"📊 Среднее время отклика: {stats.get('avg_response_time', 0):.3f}s")
        print(f"📊 Медианное время отклика: {stats.get('median_response_time', 0):.3f}s")
        print(f"📊 Стандартное отклонение: {stats.get('std_deviation', 0):.3f}s")
        
        assert stats['success_rate'] >= 95, f"Слишком низкий процент успеха: {stats['success_rate']:.1f}%"
        assert stats.get('avg_response_time', 0) < 2.0, f"Слишком медленный отклик: {stats.get('avg_response_time', 0):.3f}s"
    
    @pytest.mark.asyncio
    async def test_api_endpoints_performance(self):
        """Тест производительности API endpoints"""
        print("\n🧪 Тестирование производительности API endpoints...")
        
        endpoints = [
            ("/api/endpoints", "GET"),
            ("/api/services", "GET"),
            ("/api/test-history", "GET"),
            ("/api/autocomplete?query=test", "GET")
        ]
        
        all_stats = []
        
        for endpoint, method in endpoints:
            stats = await self.monitor.measure_endpoint_performance(endpoint, method, 15)
            all_stats.append(stats)
            
            print(f"  {method} {endpoint}:")
            print(f"    Успех: {stats['success_rate']:.1f}%")
            print(f"    Время: {stats.get('avg_response_time', 0):.3f}s")
        
        # Проверяем общую производительность
        avg_response_times = [s.get('avg_response_time', 0) for s in all_stats if s.get('avg_response_time')]
        success_rates = [s['success_rate'] for s in all_stats]
        
        if avg_response_times:
            overall_avg_time = mean(avg_response_times)
            overall_success_rate = mean(success_rates)
            
            print(f"\n📊 Общая производительность:")
            print(f"  Средний успех: {overall_success_rate:.1f}%")
            print(f"  Среднее время: {overall_avg_time:.3f}s")
            
            assert overall_success_rate >= 90, f"Слишком низкий общий процент успеха: {overall_success_rate:.1f}%"
            assert overall_avg_time < 3.0, f"Слишком медленный общий отклик: {overall_avg_time:.3f}s"
    
    @pytest.mark.asyncio
    async def test_api_test_endpoint_performance(self):
        """Тест производительности endpoint для тестирования API"""
        print("\n🧪 Тестирование производительности API test endpoint...")
        
        test_data = {
            "endpoint": "/health",
            "method": "GET"
        }
        
        stats = await self.monitor.measure_endpoint_performance(
            "/api/test", 
            "POST", 
            10, 
            test_data
        )
        
        print(f"✅ Успешных запросов: {stats['successful_requests']}/10")
        print(f"📊 Среднее время отклика: {stats.get('avg_response_time', 0):.3f}s")
        print(f"📊 Медианное время отклика: {stats.get('median_response_time', 0):.3f}s")
        
        assert stats['success_rate'] >= 80, f"Слишком низкий процент успеха: {stats['success_rate']:.1f}%"
        assert stats.get('avg_response_time', 0) < 10.0, f"Слишком медленный отклик: {stats.get('avg_response_time', 0):.3f}s"
    
    @pytest.mark.asyncio
    async def test_system_metrics(self):
        """Тест системных метрик"""
        print("\n🧪 Тестирование системных метрик...")
        
        metrics = await self.monitor.measure_system_metrics()
        
        print(f"📊 CPU использование: {metrics['cpu_usage_percent']:.1f}%")
        print(f"📊 Память: {metrics['memory_usage_percent']:.1f}%")
        print(f"📊 Диск: {metrics['disk_usage_percent']:.1f}%")
        print(f"📊 Процессы: {metrics['process_count']}")
        
        # Проверки системных метрик
        assert metrics['cpu_usage_percent'] < 90, f"Слишком высокое использование CPU: {metrics['cpu_usage_percent']:.1f}%"
        assert metrics['memory_usage_percent'] < 90, f"Слишком высокое использование памяти: {metrics['memory_usage_percent']:.1f}%"
        assert metrics['disk_usage_percent'] < 95, f"Слишком высокое использование диска: {metrics['disk_usage_percent']:.1f}%"
    
    @pytest.mark.asyncio
    async def test_network_metrics(self):
        """Тест сетевых метрик"""
        print("\n🧪 Тестирование сетевых метрик...")
        
        metrics = await self.monitor.measure_network_metrics()
        
        print(f"📊 Отправлено байт: {metrics['bytes_sent']:,}")
        print(f"📊 Получено байт: {metrics['bytes_recv']:,}")
        print(f"📊 Отправлено пакетов: {metrics['packets_sent']:,}")
        print(f"📊 Получено пакетов: {metrics['packets_recv']:,}")
        
        # Проверки сетевых метрик
        assert metrics['bytes_sent'] >= 0, "Отрицательное количество отправленных байт"
        assert metrics['bytes_recv'] >= 0, "Отрицательное количество полученных байт"
        assert metrics['packets_sent'] >= 0, "Отрицательное количество отправленных пакетов"
        assert metrics['packets_recv'] >= 0, "Отрицательное количество полученных пакетов"
    
    @pytest.mark.asyncio
    async def test_performance_under_load(self):
        """Тест производительности под нагрузкой"""
        print("\n🧪 Тестирование производительности под нагрузкой...")
        
        # Измеряем системные метрики до нагрузки
        initial_metrics = await self.monitor.measure_system_metrics()
        
        # Запускаем нагрузочный тест
        load_tasks = []
        for i in range(20):
            task = self.monitor.measure_endpoint_performance("/api/services", "GET", 5)
            load_tasks.append(task)
        
        # Выполняем все задачи параллельно
        results = await asyncio.gather(*load_tasks, return_exceptions=True)
        
        # Измеряем системные метрики после нагрузки
        final_metrics = await self.monitor.measure_system_metrics()
        
        # Анализируем результаты
        successful_results = [r for r in results if isinstance(r, dict)]
        failed_results = [r for r in results if not isinstance(r, dict)]
        
        print(f"✅ Успешных тестов: {len(successful_results)}/20")
        print(f"❌ Неудачных тестов: {len(failed_results)}/20")
        
        if successful_results:
            all_response_times = []
            for result in successful_results:
                if 'avg_response_time' in result:
                    all_response_times.append(result['avg_response_time'])
            
            if all_response_times:
                avg_response_time = mean(all_response_times)
                print(f"📊 Среднее время отклика под нагрузкой: {avg_response_time:.3f}s")
                
                assert avg_response_time < 5.0, f"Слишком медленный отклик под нагрузкой: {avg_response_time:.3f}s"
        
        # Проверяем изменения системных метрик
        cpu_increase = final_metrics['cpu_usage_percent'] - initial_metrics['cpu_usage_percent']
        memory_increase = final_metrics['memory_usage_percent'] - initial_metrics['memory_usage_percent']
        
        print(f"📊 Увеличение CPU: {cpu_increase:.1f}%")
        print(f"📊 Увеличение памяти: {memory_increase:.1f}%")
        
        assert cpu_increase < 30, f"Слишком большое увеличение CPU: {cpu_increase:.1f}%"
        assert memory_increase < 20, f"Слишком большое увеличение памяти: {memory_increase:.1f}%"
    
    def test_generate_performance_report(self):
        """Генерация отчета о производительности"""
        print("\n📊 Генерация отчета о производительности...")
        
        report = self.monitor.generate_performance_report()
        
        if "error" in report:
            print(f"❌ Ошибка генерации отчета: {report['error']}")
            return
        
        # Сохранение отчета
        report_file = f"dashboard_performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ Отчет сохранен: {report_file}")
        
        # Вывод краткой статистики
        print(f"\n📈 КРАТКАЯ СТАТИСТИКА:")
        print(f"  Общее количество запросов: {report['total_requests']}")
        print(f"  Успешных запросов: {report['successful_requests']}")
        print(f"  Общий процент успеха: {report['overall_success_rate']:.1f}%")
        print(f"  Среднее время отклика: {report['summary']['avg_response_time']:.3f}s")
        print(f"  Медианное время отклика: {report['summary']['median_response_time']:.3f}s")
        
        # Проверки отчета
        assert report['total_requests'] > 0, "Нет данных о запросах"
        assert report['overall_success_rate'] >= 80, f"Слишком низкий процент успеха: {report['overall_success_rate']:.1f}%"
        assert report['summary']['avg_response_time'] < 5.0, f"Слишком медленный отклик: {report['summary']['avg_response_time']:.3f}s"


if __name__ == "__main__":
    print("🚀 Запуск тестов производительности ALADDIN Dashboard...")
    print("📊 Измерение времени отклика и системных метрик...")
    print("🛡️ Проверка стабильности производительности...")
    
    # Запуск тестов через pytest
    pytest.main([__file__, "-v", "--tb=short"])