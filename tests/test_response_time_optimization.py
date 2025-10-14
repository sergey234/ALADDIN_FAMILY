#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Response Time Optimization Tests для ALADDIN Dashboard
Тесты оптимизации времени отклика и производительности

Автор: ALADDIN Security Team
Версия: 1.0.0
Дата: 2025-01-27
Качество: A+
"""

import asyncio
import time
import statistics
import psutil
import pytest
import httpx
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
import threading

# Добавляем путь к проекту
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from core.base import ComponentStatus, SecurityLevel
    from core.logging_module import LoggingManager
    ALADDIN_AVAILABLE = True
except ImportError:
    ALADDIN_AVAILABLE = False


@dataclass
class ResponseTimeMetric:
    """Метрика времени отклика"""
    endpoint: str
    method: str
    response_time: float
    status_code: int
    timestamp: datetime
    success: bool
    error_message: Optional[str] = None
    response_size: int = 0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0


@dataclass
class PerformanceBenchmark:
    """Бенчмарк производительности"""
    test_name: str
    endpoint: str
    iterations: int
    min_response_time: float
    max_response_time: float
    avg_response_time: float
    median_response_time: float
    p95_response_time: float
    p99_response_time: float
    success_rate: float
    throughput_rps: float  # Requests per second
    cpu_usage_avg: float
    memory_usage_avg: float
    optimization_score: float


@dataclass
class CachePerformanceTest:
    """Тест производительности кэша"""
    cache_type: str
    hit_rate: float
    miss_rate: float
    response_time_with_cache: float
    response_time_without_cache: float
    cache_efficiency: float
    memory_overhead: float


class ResponseTimeOptimizer:
    """Оптимизатор времени отклика"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        """
        Инициализация оптимизатора
        
        Args:
            base_url: Базовый URL дашборда
        """
        self.base_url = base_url
        self.logger = LoggingManager(name="ResponseTimeOptimizer") if ALADDIN_AVAILABLE else None
        self.response_metrics: List[ResponseTimeMetric] = []
        self.benchmarks: List[PerformanceBenchmark] = []
        
    async def measure_response_time(
        self, 
        endpoint: str, 
        method: str = "GET",
        json_data: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> ResponseTimeMetric:
        """
        Измерение времени отклика endpoint
        
        Args:
            endpoint: Endpoint для измерения
            method: HTTP метод
            json_data: JSON данные для POST запросов
            headers: Дополнительные заголовки
            
        Returns:
            Метрика времени отклика
        """
        start_time = time.time()
        cpu_before = psutil.cpu_percent()
        memory_before = psutil.virtual_memory().percent
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                default_headers = {"Authorization": "Bearer demo_token"}
                if headers:
                    default_headers.update(headers)
                
                if method.upper() == "GET":
                    response = await client.get(f"{self.base_url}{endpoint}", headers=default_headers)
                elif method.upper() == "POST":
                    response = await client.post(
                        f"{self.base_url}{endpoint}", 
                        json=json_data, 
                        headers=default_headers
                    )
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                response_time = time.time() - start_time
                cpu_after = psutil.cpu_percent()
                memory_after = psutil.virtual_memory().percent
                
                metric = ResponseTimeMetric(
                    endpoint=endpoint,
                    method=method,
                    response_time=response_time,
                    status_code=response.status_code,
                    timestamp=datetime.now(),
                    success=200 <= response.status_code < 300,
                    response_size=len(response.content),
                    cpu_usage=(cpu_after + cpu_before) / 2,
                    memory_usage=(memory_after + memory_before) / 2
                )
                
                self.response_metrics.append(metric)
                return metric
                
        except Exception as e:
            response_time = time.time() - start_time
            
            metric = ResponseTimeMetric(
                endpoint=endpoint,
                method=method,
                response_time=response_time,
                status_code=0,
                timestamp=datetime.now(),
                success=False,
                error_message=str(e)
            )
            
            self.response_metrics.append(metric)
            return metric
    
    async def run_performance_benchmark(
        self, 
        test_name: str,
        endpoint: str, 
        method: str = "GET",
        iterations: int = 100,
        json_data: Optional[Dict] = None
    ) -> PerformanceBenchmark:
        """
        Запуск бенчмарка производительности
        
        Args:
            test_name: Название теста
            endpoint: Endpoint для тестирования
            method: HTTP метод
            iterations: Количество итераций
            json_data: JSON данные
            
        Returns:
            Бенчмарк производительности
        """
        print(f"📊 Запуск бенчмарка: {test_name}")
        print(f"   Endpoint: {method} {endpoint}")
        print(f"   Итераций: {iterations}")
        
        start_time = time.time()
        metrics = []
        
        # Выполняем итерации
        for i in range(iterations):
            if i % 20 == 0:
                print(f"   Прогресс: {i}/{iterations}")
            
            metric = await self.measure_response_time(endpoint, method, json_data)
            metrics.append(metric)
            
            # Небольшая пауза между запросами
            await asyncio.sleep(0.01)
        
        total_time = time.time() - start_time
        
        # Анализируем результаты
        successful_metrics = [m for m in metrics if m.success]
        response_times = [m.response_time for m in successful_metrics]
        
        if response_times:
            min_time = min(response_times)
            max_time = max(response_times)
            avg_time = statistics.mean(response_times)
            median_time = statistics.median(response_times)
            p95_time = self._calculate_percentile(response_times, 95)
            p99_time = self._calculate_percentile(response_times, 99)
            success_rate = len(successful_metrics) / len(metrics) * 100
            throughput = len(metrics) / total_time
            
            cpu_usage = statistics.mean([m.cpu_usage for m in successful_metrics])
            memory_usage = statistics.mean([m.memory_usage for m in successful_metrics])
            
            # Вычисляем оценку оптимизации (0-1, где 1 = отлично)
            optimization_score = self._calculate_optimization_score(
                avg_time, success_rate, throughput
            )
            
            benchmark = PerformanceBenchmark(
                test_name=test_name,
                endpoint=endpoint,
                iterations=iterations,
                min_response_time=min_time,
                max_response_time=max_time,
                avg_response_time=avg_time,
                median_response_time=median_time,
                p95_response_time=p95_time,
                p99_response_time=p99_time,
                success_rate=success_rate,
                throughput_rps=throughput,
                cpu_usage_avg=cpu_usage,
                memory_usage_avg=memory_usage,
                optimization_score=optimization_score
            )
            
            self.benchmarks.append(benchmark)
            
            print(f"   Результаты:")
            print(f"     Среднее время: {avg_time:.3f}s")
            print(f"     Медианное время: {median_time:.3f}s")
            print(f"     P95: {p95_time:.3f}s")
            print(f"     Успешность: {success_rate:.1f}%")
            print(f"     Пропускная способность: {throughput:.2f} RPS")
            print(f"     Оценка оптимизации: {optimization_score:.2f}")
            
            return benchmark
        else:
            raise Exception("Все запросы завершились неудачно")
    
    def _calculate_percentile(self, values: List[float], percentile: int) -> float:
        """Вычисление перцентиля"""
        sorted_values = sorted(values)
        index = int((percentile / 100) * len(sorted_values))
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    def _calculate_optimization_score(
        self, 
        avg_response_time: float, 
        success_rate: float, 
        throughput: float
    ) -> float:
        """Вычисление оценки оптимизации"""
        # Нормализуем метрики (0-1)
        time_score = max(0, 1 - (avg_response_time / 5.0))  # Хорошо если < 5s
        success_score = success_rate / 100.0
        throughput_score = min(1.0, throughput / 100.0)  # Хорошо если > 100 RPS
        
        # Взвешенная оценка
        optimization_score = (
            time_score * 0.4 +      # 40% - время отклика
            success_score * 0.4 +   # 40% - успешность
            throughput_score * 0.2  # 20% - пропускная способность
        )
        
        return min(1.0, max(0.0, optimization_score))
    
    async def test_connection_pooling_optimization(self) -> Dict[str, Any]:
        """Тест оптимизации пула соединений"""
        print("📊 Тестирование оптимизации пула соединений...")
        
        results = {}
        
        # 1. Тест без пула соединений
        print("  1. Без пула соединений...")
        start_time = time.time()
        
        for _ in range(50):
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": "Bearer demo_token"}
                try:
                    await client.get(f"{self.base_url}/api/services", headers=headers)
                except Exception:
                    pass
        
        no_pool_time = time.time() - start_time
        results["no_pool"] = {"time": no_pool_time, "avg_per_request": no_pool_time / 50}
        
        # 2. Тест с пулом соединений
        print("  2. С пулом соединений...")
        start_time = time.time()
        
        async with httpx.AsyncClient(
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20)
        ) as client:
            headers = {"Authorization": "Bearer demo_token"}
            for _ in range(50):
                try:
                    await client.get(f"{self.base_url}/api/services", headers=headers)
                except Exception:
                    pass
        
        with_pool_time = time.time() - start_time
        results["with_pool"] = {"time": with_pool_time, "avg_per_request": with_pool_time / 50}
        
        # 3. Вычисляем улучшение
        improvement = ((no_pool_time - with_pool_time) / no_pool_time) * 100
        results["improvement_percent"] = improvement
        
        print(f"   Улучшение: {improvement:.1f}%")
        
        return results
    
    async def test_compression_optimization(self) -> Dict[str, Any]:
        """Тест оптимизации сжатия"""
        print("📊 Тестирование оптимизации сжатия...")
        
        results = {}
        
        # 1. Без сжатия
        print("  1. Без сжатия...")
        headers_no_compression = {
            "Authorization": "Bearer demo_token",
            "Accept-Encoding": "identity"
        }
        
        start_time = time.time()
        for _ in range(20):
            metric = await self.measure_response_time("/api/endpoints", "GET", headers=headers_no_compression)
        
        no_compression_time = time.time() - start_time
        no_compression_size = sum(m.response_size for m in self.response_metrics[-20:])
        
        results["no_compression"] = {
            "time": no_compression_time,
            "total_size": no_compression_size,
            "avg_size": no_compression_size / 20
        }
        
        # 2. Со сжатием
        print("  2. Со сжатием...")
        headers_with_compression = {
            "Authorization": "Bearer demo_token",
            "Accept-Encoding": "gzip, deflate"
        }
        
        start_time = time.time()
        for _ in range(20):
            metric = await self.measure_response_time("/api/endpoints", "GET", headers=headers_with_compression)
        
        with_compression_time = time.time() - start_time
        with_compression_size = sum(m.response_size for m in self.response_metrics[-20:])
        
        results["with_compression"] = {
            "time": with_compression_time,
            "total_size": with_compression_size,
            "avg_size": with_compression_size / 20
        }
        
        # 3. Вычисляем улучшения
        time_improvement = ((no_compression_time - with_compression_time) / no_compression_time) * 100
        size_improvement = ((no_compression_size - with_compression_size) / no_compression_size) * 100
        
        results["time_improvement_percent"] = time_improvement
        results["size_improvement_percent"] = size_improvement
        
        print(f"   Улучшение времени: {time_improvement:.1f}%")
        print(f"   Улучшение размера: {size_improvement:.1f}%")
        
        return results
    
    async def test_concurrent_optimization(self) -> Dict[str, Any]:
        """Тест оптимизации конкурентности"""
        print("📊 Тестирование оптимизации конкурентности...")
        
        results = {}
        
        # 1. Последовательные запросы
        print("  1. Последовательные запросы...")
        start_time = time.time()
        
        for _ in range(30):
            await self.measure_response_time("/api/services", "GET")
        
        sequential_time = time.time() - start_time
        results["sequential"] = {"time": sequential_time, "rps": 30 / sequential_time}
        
        # 2. Конкурентные запросы
        print("  2. Конкурентные запросы...")
        start_time = time.time()
        
        tasks = [self.measure_response_time("/api/services", "GET") for _ in range(30)]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        concurrent_time = time.time() - start_time
        results["concurrent"] = {"time": concurrent_time, "rps": 30 / concurrent_time}
        
        # 3. Вычисляем улучшение
        improvement = ((sequential_time - concurrent_time) / sequential_time) * 100
        results["improvement_percent"] = improvement
        
        print(f"   Улучшение: {improvement:.1f}%")
        print(f"   RPS последовательно: {results['sequential']['rps']:.2f}")
        print(f"   RPS конкурентно: {results['concurrent']['rps']:.2f}")
        
        return results
    
    def generate_optimization_report(self) -> Dict[str, Any]:
        """Генерация отчета об оптимизации"""
        print("📊 Генерация отчета об оптимизации времени отклика...")
        
        if not self.benchmarks:
            return {"error": "Нет данных бенчмарков"}
        
        # Анализируем все бенчмарки
        total_benchmarks = len(self.benchmarks)
        avg_optimization_score = statistics.mean([b.optimization_score for b in self.benchmarks])
        avg_response_time = statistics.mean([b.avg_response_time for b in self.benchmarks])
        avg_success_rate = statistics.mean([b.success_rate for b in self.benchmarks])
        avg_throughput = statistics.mean([b.throughput_rps for b in self.benchmarks])
        
        # Определяем общую оценку
        if avg_optimization_score >= 0.9:
            overall_grade = "A+"
        elif avg_optimization_score >= 0.8:
            overall_grade = "A"
        elif avg_optimization_score >= 0.7:
            overall_grade = "B+"
        elif avg_optimization_score >= 0.6:
            overall_grade = "B"
        else:
            overall_grade = "C"
        
        report = {
            "report_date": datetime.now().isoformat(),
            "total_benchmarks": total_benchmarks,
            "avg_optimization_score": avg_optimization_score,
            "avg_response_time": avg_response_time,
            "avg_success_rate": avg_success_rate,
            "avg_throughput": avg_throughput,
            "overall_grade": overall_grade,
            "benchmarks": [
                {
                    "test_name": b.test_name,
                    "endpoint": b.endpoint,
                    "avg_response_time": b.avg_response_time,
                    "p95_response_time": b.p95_response_time,
                    "success_rate": b.success_rate,
                    "throughput_rps": b.throughput_rps,
                    "optimization_score": b.optimization_score
                }
                for b in self.benchmarks
            ],
            "recommendations": self._generate_optimization_recommendations()
        }
        
        return report
    
    def _generate_optimization_recommendations(self) -> List[str]:
        """Генерация рекомендаций по оптимизации"""
        recommendations = []
        
        for benchmark in self.benchmarks:
            if benchmark.avg_response_time > 3.0:
                recommendations.append(
                    f"Оптимизировать время отклика для {benchmark.test_name}: {benchmark.avg_response_time:.3f}s"
                )
            
            if benchmark.success_rate < 95:
                recommendations.append(
                    f"Улучшить надежность для {benchmark.test_name}: {benchmark.success_rate:.1f}%"
                )
            
            if benchmark.throughput_rps < 50:
                recommendations.append(
                    f"Увеличить пропускную способность для {benchmark.test_name}: {benchmark.throughput_rps:.2f} RPS"
                )
            
            if benchmark.optimization_score < 0.7:
                recommendations.append(
                    f"Общая оптимизация для {benchmark.test_name}: {benchmark.optimization_score:.2f}"
                )
        
        if not recommendations:
            recommendations.append("Время отклика оптимизировано хорошо")
        
        return recommendations


class TestResponseTimeOptimization:
    """Тесты оптимизации времени отклика"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Настройка тестов"""
        self.optimizer = ResponseTimeOptimizer()
    
    @pytest.mark.asyncio
    async def test_main_page_benchmark(self):
        """Бенчмарк главной страницы"""
        print("\n🧪 Бенчмарк главной страницы...")
        
        benchmark = await self.optimizer.run_performance_benchmark(
            "main_page",
            "/",
            "GET",
            50
        )
        
        # Проверки
        assert benchmark.avg_response_time < 2.0, f"Слишком медленная главная страница: {benchmark.avg_response_time:.3f}s"
        assert benchmark.success_rate >= 95, f"Слишком низкая успешность: {benchmark.success_rate:.1f}%"
        assert benchmark.optimization_score >= 0.7, f"Низкая оценка оптимизации: {benchmark.optimization_score:.2f}"
        
        print(f"✅ Главная страница оптимизирована: {benchmark.avg_response_time:.3f}s")
    
    @pytest.mark.asyncio
    async def test_api_endpoints_benchmark(self):
        """Бенчмарк API endpoints"""
        print("\n🧪 Бенчмарк API endpoints...")
        
        endpoints = [
            ("api_services", "/api/services", "GET"),
            ("api_endpoints", "/api/endpoints", "GET"),
            ("api_test_history", "/api/test-history", "GET")
        ]
        
        for test_name, endpoint, method in endpoints:
            benchmark = await self.optimizer.run_performance_benchmark(
                test_name,
                endpoint,
                method,
                30
            )
            
            # Проверки
            assert benchmark.avg_response_time < 3.0, f"Слишком медленный {endpoint}: {benchmark.avg_response_time:.3f}s"
            assert benchmark.success_rate >= 90, f"Слишком низкая успешность для {endpoint}: {benchmark.success_rate:.1f}%"
            
            print(f"✅ {endpoint} оптимизирован: {benchmark.avg_response_time:.3f}s")
    
    @pytest.mark.asyncio
    async def test_connection_pooling_optimization(self):
        """Тест оптимизации пула соединений"""
        print("\n🧪 Тестирование оптимизации пула соединений...")
        
        results = await self.optimizer.test_connection_pooling_optimization()
        
        # Проверки
        assert results["improvement_percent"] >= 0, "Пул соединений должен улучшать производительность"
        
        print(f"✅ Пул соединений улучшает производительность на {results['improvement_percent']:.1f}%")
    
    @pytest.mark.asyncio
    async def test_compression_optimization(self):
        """Тест оптимизации сжатия"""
        print("\n🧪 Тестирование оптимизации сжатия...")
        
        results = await self.optimizer.test_compression_optimization()
        
        # Проверки
        assert results["size_improvement_percent"] >= 0, "Сжатие должно уменьшать размер ответов"
        
        print(f"✅ Сжатие уменьшает размер на {results['size_improvement_percent']:.1f}%")
    
    @pytest.mark.asyncio
    async def test_concurrent_optimization(self):
        """Тест оптимизации конкурентности"""
        print("\n🧪 Тестирование оптимизации конкурентности...")
        
        results = await self.optimizer.test_concurrent_optimization()
        
        # Проверки
        assert results["improvement_percent"] >= 0, "Конкурентность должна улучшать производительность"
        assert results["concurrent"]["rps"] >= results["sequential"]["rps"], "Конкурентные запросы должны быть быстрее"
        
        print(f"✅ Конкурентность улучшает производительность на {results['improvement_percent']:.1f}%")
    
    @pytest.mark.asyncio
    async def test_stress_performance(self):
        """Тест производительности под стрессом"""
        print("\n🧪 Тестирование производительности под стрессом...")
        
        benchmark = await self.optimizer.run_performance_benchmark(
            "stress_test",
            "/api/services",
            "GET",
            200  # Больше итераций для стресс-теста
        )
        
        # Проверки под стрессом более мягкие
        assert benchmark.avg_response_time < 5.0, f"Слишком медленно под стрессом: {benchmark.avg_response_time:.3f}s"
        assert benchmark.success_rate >= 80, f"Слишком низкая успешность под стрессом: {benchmark.success_rate:.1f}%"
        assert benchmark.throughput_rps >= 20, f"Слишком низкая пропускная способность: {benchmark.throughput_rps:.2f} RPS"
        
        print(f"✅ Система выдержала стресс: {benchmark.avg_response_time:.3f}s, {benchmark.throughput_rps:.2f} RPS")
    
    def test_generate_optimization_report(self):
        """Генерация отчета об оптимизации"""
        print("\n📊 Генерация отчета об оптимизации времени отклика...")
        
        report = self.optimizer.generate_optimization_report()
        
        if "error" in report:
            print(f"❌ Ошибка генерации отчета: {report['error']}")
            return
        
        # Сохранение отчета
        report_file = f"response_time_optimization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ Отчет об оптимизации сохранен: {report_file}")
        
        # Вывод краткой статистики
        print(f"\n📈 КРАТКАЯ СТАТИСТИКА:")
        print(f"  Всего бенчмарков: {report['total_benchmarks']}")
        print(f"  Средняя оценка оптимизации: {report['avg_optimization_score']:.2f}")
        print(f"  Среднее время отклика: {report['avg_response_time']:.3f}s")
        print(f"  Средняя успешность: {report['avg_success_rate']:.1f}%")
        print(f"  Средняя пропускная способность: {report['avg_throughput']:.2f} RPS")
        print(f"  Общая оценка: {report['overall_grade']}")
        
        # Проверки отчета
        assert report['total_benchmarks'] > 0, "Нет данных бенчмарков"
        assert report['avg_optimization_score'] >= 0.5, f"Слишком низкая общая оценка: {report['avg_optimization_score']:.2f}"


if __name__ == "__main__":
    print("🚀 Запуск тестов оптимизации времени отклика ALADDIN Dashboard...")
    print("⚡ Бенчмарки производительности...")
    print("🔧 Тестирование оптимизаций...")
    print("📊 Анализ времени отклика...")
    
    # Запуск тестов через pytest
    pytest.main([__file__, "-v", "--tb=short"])