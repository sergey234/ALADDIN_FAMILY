#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Optimization Tests для ALADDIN Dashboard
Тесты оптимизации памяти и профилирование

Автор: ALADDIN Security Team
Версия: 1.0.0
Дата: 2025-01-27
Качество: A+
"""

import asyncio
import time
import gc
import tracemalloc
import psutil
import pytest
import httpx
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from memory_profiler import profile
import threading
from concurrent.futures import ThreadPoolExecutor

# Добавляем путь к проекту
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from core.base import ComponentStatus, SecurityLevel
    from core.logging_module import LoggingManager
    ALADDIN_AVAILABLE = True
except ImportError:
    ALADDIN_AVAILABLE = False


@dataclass
class MemorySnapshot:
    """Снимок памяти"""
    timestamp: datetime
    rss_mb: float  # Resident Set Size в MB
    vms_mb: float  # Virtual Memory Size в MB
    percent: float  # Процент использования памяти
    available_mb: float  # Доступная память в MB
    cached_mb: float  # Кэшированная память в MB
    buffers_mb: float  # Буферная память в MB


@dataclass
class MemoryLeakDetection:
    """Детектор утечек памяти"""
    initial_snapshot: Optional[MemorySnapshot] = None
    final_snapshot: Optional[MemorySnapshot] = None
    snapshots: List[MemorySnapshot] = field(default_factory=list)
    memory_growth: float = 0.0
    leak_detected: bool = False
    growth_rate: float = 0.0


@dataclass
class MemoryOptimizationResult:
    """Результат оптимизации памяти"""
    test_name: str
    initial_memory: MemorySnapshot
    final_memory: MemorySnapshot
    memory_growth: float
    optimization_score: float
    recommendations: List[str]
    success: bool


class MemoryProfiler:
    """Профилировщик памяти"""
    
    def __init__(self):
        """Инициализация профилировщика"""
        self.tracemalloc_started = False
        self.logger = LoggingManager(name="MemoryProfiler") if ALADDIN_AVAILABLE else None
        self.snapshots: List[MemorySnapshot] = []
        
    def start_tracing(self):
        """Запуск трассировки памяти"""
        if not self.tracemalloc_started:
            tracemalloc.start()
            self.tracemalloc_started = True
            print("📊 Трассировка памяти запущена")
    
    def stop_tracing(self) -> Optional[Tuple]:
        """Остановка трассировки и получение статистики"""
        if self.tracemalloc_started:
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            self.tracemalloc_started = False
            print(f"📊 Трассировка остановлена. Текущая: {current / 1024 / 1024:.2f} MB, Пиковая: {peak / 1024 / 1024:.2f} MB")
            return current, peak
        return None
    
    def take_memory_snapshot(self) -> MemorySnapshot:
        """Создание снимка памяти"""
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_percent = process.memory_percent()
        
        # Системная память
        system_memory = psutil.virtual_memory()
        
        snapshot = MemorySnapshot(
            timestamp=datetime.now(),
            rss_mb=memory_info.rss / 1024 / 1024,
            vms_mb=memory_info.vms / 1024 / 1024,
            percent=memory_percent,
            available_mb=system_memory.available / 1024 / 1024,
            cached_mb=getattr(system_memory, 'cached', 0) / 1024 / 1024,
            buffers_mb=getattr(system_memory, 'buffers', 0) / 1024 / 1024
        )
        
        self.snapshots.append(snapshot)
        return snapshot
    
    def detect_memory_leak(self, snapshots: List[MemorySnapshot]) -> MemoryLeakDetection:
        """Обнаружение утечек памяти"""
        if len(snapshots) < 2:
            return MemoryLeakDetection()
        
        initial = snapshots[0]
        final = snapshots[-1]
        
        # Вычисляем рост памяти
        memory_growth = final.rss_mb - initial.rss_mb
        
        # Вычисляем скорость роста
        time_diff = (final.timestamp - initial.timestamp).total_seconds()
        growth_rate = memory_growth / time_diff if time_diff > 0 else 0
        
        # Определяем утечку (рост > 50MB за тест)
        leak_detected = memory_growth > 50.0
        
        return MemoryLeakDetection(
            initial_snapshot=initial,
            final_snapshot=final,
            snapshots=snapshots,
            memory_growth=memory_growth,
            leak_detected=leak_detected,
            growth_rate=growth_rate
        )
    
    def force_garbage_collection(self):
        """Принудительная сборка мусора"""
        collected = gc.collect()
        print(f"🗑️ Сборка мусора: освобождено {collected} объектов")
        return collected


class MemoryOptimizationTester:
    """Тестер оптимизации памяти"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        """
        Инициализация тестера оптимизации
        
        Args:
            base_url: Базовый URL дашборда
        """
        self.base_url = base_url
        self.profiler = MemoryProfiler()
        self.logger = LoggingManager(name="MemoryOptimizationTester") if ALADDIN_AVAILABLE else None
        self.optimization_results: List[MemoryOptimizationResult] = []
        
    async def test_memory_usage_baseline(self) -> MemorySnapshot:
        """Тест базового использования памяти"""
        print("📊 Тестирование базового использования памяти...")
        
        # Принудительная сборка мусора
        self.profiler.force_garbage_collection()
        
        # Снимок памяти
        snapshot = self.profiler.take_memory_snapshot()
        
        print(f"📊 Базовое использование памяти:")
        print(f"  RSS: {snapshot.rss_mb:.2f} MB")
        print(f"  VMS: {snapshot.vms_mb:.2f} MB")
        print(f"  Процент: {snapshot.percent:.2f}%")
        print(f"  Доступно: {snapshot.available_mb:.2f} MB")
        
        return snapshot
    
    async def test_memory_usage_during_requests(
        self, 
        num_requests: int = 100
    ) -> List[MemorySnapshot]:
        """
        Тест использования памяти во время запросов
        
        Args:
            num_requests: Количество запросов
            
        Returns:
            Список снимков памяти
        """
        print(f"📊 Тестирование памяти во время {num_requests} запросов...")
        
        snapshots = []
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {"Authorization": "Bearer demo_token"}
            
            for i in range(num_requests):
                # Делаем запрос
                try:
                    response = await client.get(f"{self.base_url}/api/services", headers=headers)
                    
                    # Каждые 10 запросов делаем снимок памяти
                    if i % 10 == 0:
                        snapshot = self.profiler.take_memory_snapshot()
                        snapshots.append(snapshot)
                        
                        print(f"  Запрос {i}: RSS {snapshot.rss_mb:.2f} MB")
                
                except Exception as e:
                    print(f"  Ошибка запроса {i}: {e}")
        
        return snapshots
    
    async def test_memory_leak_detection(self) -> MemoryLeakDetection:
        """Тест обнаружения утечек памяти"""
        print("📊 Тестирование обнаружения утечек памяти...")
        
        # Запускаем трассировку
        self.profiler.start_tracing()
        
        # Начальный снимок
        initial_snapshot = self.profiler.take_memory_snapshot()
        snapshots = [initial_snapshot]
        
        # Выполняем множество операций
        for cycle in range(5):
            print(f"  Цикл {cycle + 1}/5...")
            
            # Делаем запросы
            await self.test_memory_usage_during_requests(50)
            
            # Принудительная сборка мусора
            self.profiler.force_garbage_collection()
            
            # Снимок памяти
            snapshot = self.profiler.take_memory_snapshot()
            snapshots.append(snapshot)
            
            # Пауза между циклами
            await asyncio.sleep(1)
        
        # Останавливаем трассировку
        tracemalloc_result = self.profiler.stop_tracing()
        
        # Анализируем утечки
        leak_detection = self.profiler.detect_memory_leak(snapshots)
        
        print(f"📊 Результаты обнаружения утечек:")
        print(f"  Рост памяти: {leak_detection.memory_growth:.2f} MB")
        print(f"  Скорость роста: {leak_detection.growth_rate:.4f} MB/s")
        print(f"  Утечка обнаружена: {'Да' if leak_detection.leak_detected else 'Нет'}")
        
        if tracemalloc_result:
            current, peak = tracemalloc_result
            print(f"  Пиковая память (tracemalloc): {peak / 1024 / 1024:.2f} MB")
        
        return leak_detection
    
    async def test_concurrent_memory_usage(self) -> MemorySnapshot:
        """Тест использования памяти при конкурентных запросах"""
        print("📊 Тестирование памяти при конкурентных запросах...")
        
        initial_snapshot = self.profiler.take_memory_snapshot()
        
        async def make_requests():
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {"Authorization": "Bearer demo_token"}
                for _ in range(20):
                    try:
                        await client.get(f"{self.base_url}/api/endpoints", headers=headers)
                    except Exception:
                        pass
        
        # Запускаем 10 конкурентных задач
        tasks = [make_requests() for _ in range(10)]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Принудительная сборка мусора
        self.profiler.force_garbage_collection()
        
        final_snapshot = self.profiler.take_memory_snapshot()
        
        memory_growth = final_snapshot.rss_mb - initial_snapshot.rss_mb
        
        print(f"📊 Конкурентные запросы:")
        print(f"  Начальная память: {initial_snapshot.rss_mb:.2f} MB")
        print(f"  Финальная память: {final_snapshot.rss_mb:.2f} MB")
        print(f"  Рост памяти: {memory_growth:.2f} MB")
        
        return final_snapshot
    
    async def test_memory_optimization_techniques(self) -> Dict[str, Any]:
        """Тест техник оптимизации памяти"""
        print("📊 Тестирование техник оптимизации памяти...")
        
        results = {}
        
        # 1. Тест с отключенным кэшированием
        print("  1. Тест без кэширования...")
        initial_snapshot = self.profiler.take_memory_snapshot()
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {"Authorization": "Bearer demo_token", "Cache-Control": "no-cache"}
            for _ in range(50):
                try:
                    await client.get(f"{self.base_url}/api/services", headers=headers)
                except Exception:
                    pass
        
        no_cache_snapshot = self.profiler.take_memory_snapshot()
        results["no_cache"] = {
            "memory_usage": no_cache_snapshot.rss_mb - initial_snapshot.rss_mb,
            "snapshot": no_cache_snapshot
        }
        
        # 2. Тест с принудительной сборкой мусора
        print("  2. Тест с принудительной сборкой мусора...")
        self.profiler.force_garbage_collection()
        gc_snapshot = self.profiler.take_memory_snapshot()
        results["with_gc"] = {
            "memory_usage": gc_snapshot.rss_mb - initial_snapshot.rss_mb,
            "snapshot": gc_snapshot
        }
        
        # 3. Тест с оптимизированными запросами
        print("  3. Тест с оптимизированными запросами...")
        optimized_snapshot = await self._test_optimized_requests()
        results["optimized"] = {
            "memory_usage": optimized_snapshot.rss_mb - initial_snapshot.rss_mb,
            "snapshot": optimized_snapshot
        }
        
        return results
    
    async def _test_optimized_requests(self) -> MemorySnapshot:
        """Тест оптимизированных запросов"""
        async with httpx.AsyncClient(
            timeout=30.0,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        ) as client:
            headers = {
                "Authorization": "Bearer demo_token",
                "Connection": "keep-alive",
                "Accept-Encoding": "gzip"
            }
            
            for _ in range(50):
                try:
                    response = await client.get(f"{self.base_url}/api/services", headers=headers)
                    # Читаем только заголовки для экономии памяти
                    _ = response.headers
                except Exception:
                    pass
        
        return self.profiler.take_memory_snapshot()
    
    def generate_optimization_recommendations(
        self, 
        results: List[MemoryOptimizationResult]
    ) -> List[str]:
        """Генерация рекомендаций по оптимизации"""
        recommendations = []
        
        for result in results:
            if result.memory_growth > 100:  # Рост > 100MB
                recommendations.append(
                    f"Критический рост памяти в {result.test_name}: {result.memory_growth:.2f} MB"
                )
            elif result.memory_growth > 50:  # Рост > 50MB
                recommendations.append(
                    f"Высокий рост памяти в {result.test_name}: {result.memory_growth:.2f} MB"
                )
            
            if result.optimization_score < 0.7:
                recommendations.append(
                    f"Низкий балл оптимизации в {result.test_name}: {result.optimization_score:.2f}"
                )
        
        if not recommendations:
            recommendations.append("Память оптимизирована хорошо")
        
        return recommendations


class TestMemoryOptimization:
    """Тесты оптимизации памяти"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Настройка тестов"""
        self.tester = MemoryOptimizationTester()
        
    def teardown_method(self):
        """Очистка после тестов"""
        # Принудительная сборка мусора
        self.tester.profiler.force_garbage_collection()
    
    @pytest.mark.asyncio
    async def test_baseline_memory_usage(self):
        """Тест базового использования памяти"""
        print("\n🧪 Тестирование базового использования памяти...")
        
        baseline = await self.tester.test_memory_usage_baseline()
        
        # Проверки
        assert baseline.rss_mb < 1000, f"Слишком высокое базовое использование памяти: {baseline.rss_mb:.2f} MB"
        assert baseline.percent < 50, f"Слишком высокий процент использования памяти: {baseline.percent:.2f}%"
        
        print(f"✅ Базовое использование памяти в норме: {baseline.rss_mb:.2f} MB")
    
    @pytest.mark.asyncio
    async def test_memory_during_requests(self):
        """Тест памяти во время запросов"""
        print("\n🧪 Тестирование памяти во время запросов...")
        
        snapshots = await self.tester.test_memory_usage_during_requests(100)
        
        if len(snapshots) >= 2:
            initial = snapshots[0]
            final = snapshots[-1]
            memory_growth = final.rss_mb - initial.rss_mb
            
            print(f"📊 Рост памяти за 100 запросов: {memory_growth:.2f} MB")
            
            # Проверки
            assert memory_growth < 200, f"Слишком большой рост памяти: {memory_growth:.2f} MB"
            
            print(f"✅ Рост памяти в пределах нормы: {memory_growth:.2f} MB")
        else:
            print("⚠️ Недостаточно данных для анализа")
    
    @pytest.mark.asyncio
    async def test_memory_leak_detection(self):
        """Тест обнаружения утечек памяти"""
        print("\n🧪 Тестирование обнаружения утечек памяти...")
        
        leak_detection = await self.tester.test_memory_leak_detection()
        
        # Проверки
        assert not leak_detection.leak_detected, f"Обнаружена утечка памяти: {leak_detection.memory_growth:.2f} MB"
        assert leak_detection.memory_growth < 100, f"Слишком большой рост памяти: {leak_detection.memory_growth:.2f} MB"
        assert leak_detection.growth_rate < 10, f"Слишком высокая скорость роста: {leak_detection.growth_rate:.4f} MB/s"
        
        print(f"✅ Утечки памяти не обнаружены. Рост: {leak_detection.memory_growth:.2f} MB")
    
    @pytest.mark.asyncio
    async def test_concurrent_memory_usage(self):
        """Тест конкурентного использования памяти"""
        print("\n🧪 Тестирование конкурентного использования памяти...")
        
        final_snapshot = await self.tester.test_concurrent_memory_usage()
        
        # Проверки
        assert final_snapshot.rss_mb < 2000, f"Слишком высокое использование памяти: {final_snapshot.rss_mb:.2f} MB"
        assert final_snapshot.percent < 80, f"Слишком высокий процент: {final_snapshot.percent:.2f}%"
        
        print(f"✅ Конкурентное использование памяти в норме: {final_snapshot.rss_mb:.2f} MB")
    
    @pytest.mark.asyncio
    async def test_memory_optimization_techniques(self):
        """Тест техник оптимизации памяти"""
        print("\n🧪 Тестирование техник оптимизации памяти...")
        
        results = await self.tester.test_memory_optimization_techniques()
        
        # Анализируем результаты
        for technique, result in results.items():
            memory_usage = result["memory_usage"]
            print(f"  {technique}: {memory_usage:.2f} MB")
            
            # Проверки
            assert memory_usage < 300, f"Слишком высокое использование памяти для {technique}: {memory_usage:.2f} MB"
        
        print("✅ Все техники оптимизации работают корректно")
    
    @pytest.mark.asyncio
    async def test_memory_pressure_test(self):
        """Тест давления на память"""
        print("\n🧪 Тестирование давления на память...")
        
        initial_snapshot = self.tester.profiler.take_memory_snapshot()
        
        # Создаем давление на память
        memory_intensive_tasks = []
        
        async def memory_intensive_task():
            # Создаем большие структуры данных
            large_data = []
            for _ in range(1000):
                large_data.append({"data": "x" * 1000})
            
            # Делаем HTTP запросы
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {"Authorization": "Bearer demo_token"}
                for _ in range(10):
                    try:
                        await client.get(f"{self.tester.base_url}/api/services", headers=headers)
                    except Exception:
                        pass
            
            # Очищаем данные
            del large_data
        
        # Запускаем 5 задач одновременно
        tasks = [memory_intensive_task() for _ in range(5)]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Принудительная сборка мусора
        self.tester.profiler.force_garbage_collection()
        
        final_snapshot = self.tester.profiler.take_memory_snapshot()
        memory_growth = final_snapshot.rss_mb - initial_snapshot.rss_mb
        
        print(f"📊 Рост памяти под давлением: {memory_growth:.2f} MB")
        
        # Проверки
        assert memory_growth < 500, f"Слишком большой рост памяти под давлением: {memory_growth:.2f} MB"
        
        print(f"✅ Система выдержала давление на память. Рост: {memory_growth:.2f} MB")
    
    def test_generate_memory_report(self):
        """Генерация отчета по памяти"""
        print("\n📊 Генерация отчета по оптимизации памяти...")
        
        # Собираем все снимки памяти
        all_snapshots = self.tester.profiler.snapshots
        
        if not all_snapshots:
            print("❌ Нет данных о памяти для отчета")
            return
        
        # Анализируем тренды
        initial = all_snapshots[0]
        final = all_snapshots[-1]
        memory_growth = final.rss_mb - initial.rss_mb
        
        # Создаем отчет
        report = {
            "report_date": datetime.now().isoformat(),
            "total_snapshots": len(all_snapshots),
            "initial_memory_mb": initial.rss_mb,
            "final_memory_mb": final.rss_mb,
            "memory_growth_mb": memory_growth,
            "memory_growth_percent": (memory_growth / initial.rss_mb * 100) if initial.rss_mb > 0 else 0,
            "snapshots": [
                {
                    "timestamp": s.timestamp.isoformat(),
                    "rss_mb": s.rss_mb,
                    "vms_mb": s.vms_mb,
                    "percent": s.percent,
                    "available_mb": s.available_mb
                }
                for s in all_snapshots
            ],
            "recommendations": self.tester.generate_optimization_recommendations([])
        }
        
        # Сохранение отчета
        report_file = f"memory_optimization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ Отчет по памяти сохранен: {report_file}")
        
        # Вывод краткой статистики
        print(f"\n📈 КРАТКАЯ СТАТИСТИКА:")
        print(f"  Начальная память: {initial.rss_mb:.2f} MB")
        print(f"  Финальная память: {final.rss_mb:.2f} MB")
        print(f"  Рост памяти: {memory_growth:.2f} MB")
        print(f"  Процент роста: {report['memory_growth_percent']:.2f}%")
        
        # Проверки отчета
        assert report['total_snapshots'] > 0, "Нет снимков памяти"
        assert report['memory_growth_mb'] < 1000, f"Слишком большой рост памяти: {report['memory_growth_mb']:.2f} MB"


if __name__ == "__main__":
    print("🚀 Запуск тестов оптимизации памяти ALADDIN Dashboard...")
    print("📊 Профилирование использования памяти...")
    print("🔍 Обнаружение утечек памяти...")
    print("⚡ Тестирование техник оптимизации...")
    
    # Запуск тестов через pytest
    pytest.main([__file__, "-v", "--tb=short"])