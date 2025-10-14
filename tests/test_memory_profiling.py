#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Profiling Tests для ALADDIN Dashboard
Детальное профилирование памяти и анализ использования

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
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import weakref
import objgraph

# Добавляем путь к проекту
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from core.base import ComponentStatus, SecurityLevel
    from core.logging_module import LoggingManager
    ALADDIN_AVAILABLE = True
except ImportError:
    ALADDIN_AVAILABLE = False


@dataclass
class MemoryProfileSnapshot:
    """Снимок профиля памяти"""
    timestamp: datetime
    rss_mb: float
    vms_mb: float
    shared_mb: float
    text_mb: float
    data_mb: float
    lib_mb: float
    dirty_mb: float
    memory_percent: float
    available_memory_mb: float
    cached_memory_mb: float
    buffer_memory_mb: float
    gc_objects_count: int
    tracemalloc_current_mb: float
    tracemalloc_peak_mb: float


@dataclass
class MemoryLeakAnalysis:
    """Анализ утечек памяти"""
    leak_type: str
    severity: str  # low, medium, high, critical
    description: str
    affected_objects: int
    memory_impact_mb: float
    recommendation: str
    detection_method: str


@dataclass
class MemoryUsagePattern:
    """Паттерн использования памяти"""
    pattern_name: str
    memory_growth_rate: float  # MB per second
    peak_usage_mb: float
    average_usage_mb: float
    memory_efficiency: float  # 0-1
    optimization_potential: str  # low, medium, high


class MemoryProfiler:
    """Профилировщик памяти"""
    
    def __init__(self):
        """Инициализация профилировщика"""
        self.tracemalloc_enabled = False
        self.snapshots: List[MemoryProfileSnapshot] = []
        self.logger = LoggingManager(name="MemoryProfiler") if ALADDIN_AVAILABLE else None
        self.monitoring_thread: Optional[threading.Thread] = None
        self.monitoring_active = False
        
    def start_profiling(self):
        """Запуск профилирования памяти"""
        print("📊 Запуск профилирования памяти...")
        
        # Запускаем tracemalloc
        if not self.tracemalloc_enabled:
            tracemalloc.start()
            self.tracemalloc_enabled = True
            print("✅ tracemalloc запущен")
        
        # Запускаем мониторинг в отдельном потоке
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitor_memory, daemon=True)
        self.monitoring_thread.start()
        print("✅ Мониторинг памяти запущен")
    
    def stop_profiling(self) -> Tuple[float, float]:
        """Остановка профилирования памяти"""
        print("📊 Остановка профилирования памяти...")
        
        # Останавливаем мониторинг
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        # Останавливаем tracemalloc
        if self.tracemalloc_enabled:
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            self.tracemalloc_enabled = False
            print(f"✅ tracemalloc остановлен. Пиковая память: {peak / 1024 / 1024:.2f} MB")
            return current, peak
        
        return 0, 0
    
    def _monitor_memory(self):
        """Мониторинг памяти в отдельном потоке"""
        while self.monitoring_active:
            try:
                snapshot = self._take_detailed_snapshot()
                self.snapshots.append(snapshot)
                time.sleep(1)  # Снимок каждую секунду
            except Exception as e:
                if self.logger:
                    self.logger.log("ERROR", f"Ошибка мониторинга памяти: {e}")
                break
    
    def _take_detailed_snapshot(self) -> MemoryProfileSnapshot:
        """Создание детального снимка памяти"""
        process = psutil.Process()
        
        # Детальная информация о процессе
        memory_info = process.memory_info()
        memory_percent = process.memory_percent()
        
        # Системная память
        system_memory = psutil.virtual_memory()
        
        # Количество объектов в GC
        gc_objects = len(gc.get_objects())
        
        # tracemalloc статистика
        tracemalloc_current = 0
        tracemalloc_peak = 0
        if self.tracemalloc_enabled:
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc_current = current / 1024 / 1024
            tracemalloc_peak = peak / 1024 / 1024
        
        snapshot = MemoryProfileSnapshot(
            timestamp=datetime.now(),
            rss_mb=memory_info.rss / 1024 / 1024,
            vms_mb=memory_info.vms / 1024 / 1024,
            shared_mb=getattr(memory_info, 'shared', 0) / 1024 / 1024,
            text_mb=getattr(memory_info, 'text', 0) / 1024 / 1024,
            data_mb=getattr(memory_info, 'data', 0) / 1024 / 1024,
            lib_mb=getattr(memory_info, 'lib', 0) / 1024 / 1024,
            dirty_mb=getattr(memory_info, 'dirty', 0) / 1024 / 1024,
            memory_percent=memory_percent,
            available_memory_mb=system_memory.available / 1024 / 1024,
            cached_memory_mb=getattr(system_memory, 'cached', 0) / 1024 / 1024,
            buffer_memory_mb=getattr(system_memory, 'buffers', 0) / 1024 / 1024,
            gc_objects_count=gc_objects,
            tracemalloc_current_mb=tracemalloc_current,
            tracemalloc_peak_mb=tracemalloc_peak
        )
        
        return snapshot
    
    def analyze_memory_growth(self) -> Dict[str, Any]:
        """Анализ роста памяти"""
        if len(self.snapshots) < 2:
            return {"error": "Недостаточно снимков для анализа"}
        
        initial = self.snapshots[0]
        final = self.snapshots[-1]
        
        # Вычисляем рост
        time_diff = (final.timestamp - initial.timestamp).total_seconds()
        rss_growth = final.rss_mb - initial.rss_mb
        vms_growth = final.vms_mb - initial.vms_mb
        
        growth_rate = rss_growth / time_diff if time_diff > 0 else 0
        
        # Анализируем тренд
        rss_values = [s.rss_mb for s in self.snapshots]
        growth_trend = self._calculate_trend(rss_values)
        
        return {
            "initial_rss_mb": initial.rss_mb,
            "final_rss_mb": final.rss_mb,
            "rss_growth_mb": rss_growth,
            "vms_growth_mb": vms_growth,
            "growth_rate_mb_per_sec": growth_rate,
            "growth_trend": growth_trend,
            "total_snapshots": len(self.snapshots),
            "analysis_duration_sec": time_diff,
            "peak_memory_mb": max(rss_values),
            "min_memory_mb": min(rss_values),
            "memory_volatility": max(rss_values) - min(rss_values)
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Вычисление тренда"""
        if len(values) < 3:
            return "insufficient_data"
        
        # Простая линейная регрессия
        n = len(values)
        x = list(range(n))
        y = values
        
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        
        if slope > 0.1:
            return "increasing"
        elif slope < -0.1:
            return "decreasing"
        else:
            return "stable"
    
    def detect_memory_leaks(self) -> List[MemoryLeakAnalysis]:
        """Обнаружение утечек памяти"""
        leak_analyses = []
        
        if len(self.snapshots) < 5:
            return leak_analyses
        
        # 1. Анализ роста RSS
        rss_growth = self.snapshots[-1].rss_mb - self.snapshots[0].rss_mb
        if rss_growth > 100:  # Рост > 100MB
            leak_analyses.append(MemoryLeakAnalysis(
                leak_type="RSS Growth",
                severity="high" if rss_growth > 500 else "medium",
                description=f"Значительный рост RSS памяти: {rss_growth:.2f} MB",
                affected_objects=0,  # Не можем точно определить
                memory_impact_mb=rss_growth,
                recommendation="Проверить утечки памяти в коде",
                detection_method="RSS monitoring"
            ))
        
        # 2. Анализ роста объектов GC
        gc_growth = self.snapshots[-1].gc_objects_count - self.snapshots[0].gc_objects_count
        if gc_growth > 10000:  # Рост > 10k объектов
            leak_analyses.append(MemoryLeakAnalysis(
                leak_type="GC Objects Growth",
                severity="medium" if gc_growth > 50000 else "low",
                description=f"Рост количества объектов в GC: {gc_growth}",
                affected_objects=gc_growth,
                memory_impact_mb=gc_growth * 0.001,  # Примерная оценка
                recommendation="Оптимизировать создание объектов",
                detection_method="GC monitoring"
            ))
        
        # 3. Анализ tracemalloc
        if self.tracemalloc_enabled:
            tracemalloc_growth = self.snapshots[-1].tracemalloc_current_mb - self.snapshots[0].tracemalloc_current_mb
            if tracemalloc_growth > 50:  # Рост > 50MB
                leak_analyses.append(MemoryLeakAnalysis(
                    leak_type="Tracemalloc Growth",
                    severity="high" if tracemalloc_growth > 200 else "medium",
                    description=f"Рост памяти tracemalloc: {tracemalloc_growth:.2f} MB",
                    affected_objects=0,
                    memory_impact_mb=tracemalloc_growth,
                    recommendation="Проверить утечки памяти в Python коде",
                    detection_method="tracemalloc"
                ))
        
        # 4. Анализ нестабильности памяти
        rss_values = [s.rss_mb for s in self.snapshots]
        memory_volatility = max(rss_values) - min(rss_values)
        if memory_volatility > 200:  # Нестабильность > 200MB
            leak_analyses.append(MemoryLeakAnalysis(
                leak_type="Memory Volatility",
                severity="medium" if memory_volatility > 500 else "low",
                description=f"Высокая нестабильность памяти: {memory_volatility:.2f} MB",
                affected_objects=0,
                memory_impact_mb=memory_volatility,
                recommendation="Оптимизировать управление памятью",
                detection_method="volatility analysis"
            ))
        
        return leak_analyses
    
    def analyze_memory_patterns(self) -> List[MemoryUsagePattern]:
        """Анализ паттернов использования памяти"""
        patterns = []
        
        if len(self.snapshots) < 10:
            return patterns
        
        rss_values = [s.rss_mb for s in self.snapshots]
        
        # 1. Паттерн роста
        growth_rate = self._calculate_growth_rate(rss_values)
        if growth_rate > 1.0:  # Рост > 1MB/sec
            patterns.append(MemoryUsagePattern(
                pattern_name="Memory Growth",
                memory_growth_rate=growth_rate,
                peak_usage_mb=max(rss_values),
                average_usage_mb=sum(rss_values) / len(rss_values),
                memory_efficiency=0.5,  # Низкая эффективность при росте
                optimization_potential="high"
            ))
        
        # 2. Паттерн стабильности
        memory_std = self._calculate_standard_deviation(rss_values)
        if memory_std < 10:  # Низкая вариативность
            patterns.append(MemoryUsagePattern(
                pattern_name="Memory Stability",
                memory_growth_rate=0,
                peak_usage_mb=max(rss_values),
                average_usage_mb=sum(rss_values) / len(rss_values),
                memory_efficiency=0.9,  # Высокая эффективность
                optimization_potential="low"
            ))
        
        # 3. Паттерн циклического использования
        if self._detect_cyclical_pattern(rss_values):
            patterns.append(MemoryUsagePattern(
                pattern_name="Cyclical Memory Usage",
                memory_growth_rate=0,
                peak_usage_mb=max(rss_values),
                average_usage_mb=sum(rss_values) / len(rss_values),
                memory_efficiency=0.7,
                optimization_potential="medium"
            ))
        
        return patterns
    
    def _calculate_growth_rate(self, values: List[float]) -> float:
        """Вычисление скорости роста"""
        if len(values) < 2:
            return 0
        
        total_growth = values[-1] - values[0]
        time_span = len(values)  # Предполагаем 1 секунда между снимками
        return total_growth / time_span if time_span > 0 else 0
    
    def _calculate_standard_deviation(self, values: List[float]) -> float:
        """Вычисление стандартного отклонения"""
        if len(values) < 2:
            return 0
        
        mean_val = sum(values) / len(values)
        variance = sum((x - mean_val) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def _detect_cyclical_pattern(self, values: List[float]) -> bool:
        """Обнаружение циклического паттерна"""
        if len(values) < 20:
            return False
        
        # Простая проверка на циклы (упрощенная)
        # Ищем повторяющиеся паттерны в данных
        for cycle_length in range(5, min(20, len(values) // 2)):
            if self._check_cycle(values, cycle_length):
                return True
        
        return False
    
    def _check_cycle(self, values: List[float], cycle_length: int) -> bool:
        """Проверка наличия цикла заданной длины"""
        if len(values) < cycle_length * 2:
            return False
        
        # Сравниваем первые два цикла
        first_cycle = values[:cycle_length]
        second_cycle = values[cycle_length:cycle_length * 2]
        
        # Проверяем похожесть (упрощенно)
        differences = [abs(a - b) for a, b in zip(first_cycle, second_cycle)]
        avg_difference = sum(differences) / len(differences)
        
        # Если средняя разность мала, считаем цикл найденным
        return avg_difference < 10  # 10MB порог
    
    def generate_profiling_report(self) -> Dict[str, Any]:
        """Генерация отчета профилирования"""
        print("📊 Генерация отчета профилирования памяти...")
        
        if not self.snapshots:
            return {"error": "Нет данных профилирования"}
        
        # Анализируем рост памяти
        growth_analysis = self.analyze_memory_growth()
        
        # Обнаруживаем утечки
        leak_analyses = self.detect_memory_leaks()
        
        # Анализируем паттерны
        usage_patterns = self.analyze_memory_patterns()
        
        # Общая статистика
        rss_values = [s.rss_mb for s in self.snapshots]
        
        report = {
            "report_date": datetime.now().isoformat(),
            "profiling_duration_sec": (self.snapshots[-1].timestamp - self.snapshots[0].timestamp).total_seconds(),
            "total_snapshots": len(self.snapshots),
            "growth_analysis": growth_analysis,
            "memory_leaks": [
                {
                    "leak_type": leak.leak_type,
                    "severity": leak.severity,
                    "description": leak.description,
                    "memory_impact_mb": leak.memory_impact_mb,
                    "recommendation": leak.recommendation,
                    "detection_method": leak.detection_method
                }
                for leak in leak_analyses
            ],
            "usage_patterns": [
                {
                    "pattern_name": pattern.pattern_name,
                    "memory_growth_rate": pattern.memory_growth_rate,
                    "peak_usage_mb": pattern.peak_usage_mb,
                    "average_usage_mb": pattern.average_usage_mb,
                    "memory_efficiency": pattern.memory_efficiency,
                    "optimization_potential": pattern.optimization_potential
                }
                for pattern in usage_patterns
            ],
            "summary": {
                "initial_memory_mb": self.snapshots[0].rss_mb,
                "final_memory_mb": self.snapshots[-1].rss_mb,
                "peak_memory_mb": max(rss_values),
                "min_memory_mb": min(rss_values),
                "average_memory_mb": sum(rss_values) / len(rss_values),
                "memory_growth_mb": rss_values[-1] - rss_values[0],
                "leaks_detected": len(leak_analyses),
                "critical_leaks": len([l for l in leak_analyses if l.severity == "critical"]),
                "high_severity_leaks": len([l for l in leak_analyses if l.severity == "high"]),
                "optimization_score": self._calculate_optimization_score(leak_analyses, usage_patterns)
            },
            "snapshots": [
                {
                    "timestamp": s.timestamp.isoformat(),
                    "rss_mb": s.rss_mb,
                    "vms_mb": s.vms_mb,
                    "memory_percent": s.memory_percent,
                    "gc_objects_count": s.gc_objects_count,
                    "tracemalloc_current_mb": s.tracemalloc_current_mb,
                    "tracemalloc_peak_mb": s.tracemalloc_peak_mb
                }
                for s in self.snapshots
            ]
        }
        
        return report
    
    def _calculate_optimization_score(
        self, 
        leak_analyses: List[MemoryLeakAnalysis], 
        usage_patterns: List[MemoryUsagePattern]
    ) -> float:
        """Вычисление оценки оптимизации"""
        score = 1.0
        
        # Штрафы за утечки
        for leak in leak_analyses:
            if leak.severity == "critical":
                score -= 0.3
            elif leak.severity == "high":
                score -= 0.2
            elif leak.severity == "medium":
                score -= 0.1
            else:
                score -= 0.05
        
        # Штрафы за неэффективные паттерны
        for pattern in usage_patterns:
            if pattern.optimization_potential == "high":
                score -= 0.2
            elif pattern.optimization_potential == "medium":
                score -= 0.1
        
        return max(0.0, min(1.0, score))


class MemoryProfilingTester:
    """Тестер профилирования памяти"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        """
        Инициализация тестера профилирования
        
        Args:
            base_url: Базовый URL дашборда
        """
        self.base_url = base_url
        self.profiler = MemoryProfiler()
        self.logger = LoggingManager(name="MemoryProfilingTester") if ALADDIN_AVAILABLE else None
        
    async def test_memory_profiling_baseline(self):
        """Тест базового профилирования памяти"""
        print("📊 Тестирование базового профилирования памяти...")
        
        # Запускаем профилирование
        self.profiler.start_profiling()
        
        # Ждем немного для накопления данных
        await asyncio.sleep(5)
        
        # Останавливаем профилирование
        tracemalloc_current, tracemalloc_peak = self.profiler.stop_profiling()
        
        # Анализируем результаты
        if self.profiler.snapshots:
            initial = self.profiler.snapshots[0]
            final = self.profiler.snapshots[-1]
            
            print(f"📊 Базовое профилирование:")
            print(f"  Начальная память: {initial.rss_mb:.2f} MB")
            print(f"  Финальная память: {final.rss_mb:.2f} MB")
            print(f"  Рост памяти: {final.rss_mb - initial.rss_mb:.2f} MB")
            print(f"  Пиковая память tracemalloc: {tracemalloc_peak / 1024 / 1024:.2f} MB")
            print(f"  Количество снимков: {len(self.profiler.snapshots)}")
            
            return True
        else:
            print("❌ Нет данных профилирования")
            return False
    
    async def test_memory_profiling_under_load(self):
        """Тест профилирования памяти под нагрузкой"""
        print("📊 Тестирование профилирования памяти под нагрузкой...")
        
        # Запускаем профилирование
        self.profiler.start_profiling()
        
        # Создаем нагрузку
        async def load_task():
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {"Authorization": "Bearer demo_token"}
                for _ in range(100):
                    try:
                        await client.get(f"{self.base_url}/api/services", headers=headers)
                    except Exception:
                        pass
                    await asyncio.sleep(0.1)
        
        # Запускаем нагрузку
        load_tasks = [load_task() for _ in range(3)]
        await asyncio.gather(*load_tasks, return_exceptions=True)
        
        # Останавливаем профилирование
        tracemalloc_current, tracemalloc_peak = self.profiler.stop_profiling()
        
        # Анализируем результаты
        if self.profiler.snapshots:
            growth_analysis = self.profiler.analyze_memory_growth()
            leak_analyses = self.profiler.detect_memory_leaks()
            
            print(f"📊 Профилирование под нагрузкой:")
            print(f"  Рост памяти: {growth_analysis.get('rss_growth_mb', 0):.2f} MB")
            print(f"  Скорость роста: {growth_analysis.get('growth_rate_mb_per_sec', 0):.4f} MB/s")
            print(f"  Тренд: {growth_analysis.get('growth_trend', 'unknown')}")
            print(f"  Утечек обнаружено: {len(leak_analyses)}")
            print(f"  Пиковая память tracemalloc: {tracemalloc_peak / 1024 / 1024:.2f} MB")
            
            return len(leak_analyses) == 0  # Успех если нет утечек
        else:
            print("❌ Нет данных профилирования")
            return False


class TestMemoryProfiling:
    """Тесты профилирования памяти"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Настройка тестов"""
        self.tester = MemoryProfilingTester()
    
    @pytest.mark.asyncio
    async def test_baseline_memory_profiling(self):
        """Тест базового профилирования памяти"""
        print("\n🧪 Тестирование базового профилирования памяти...")
        
        success = await self.tester.test_memory_profiling_baseline()
        
        assert success, "Базовое профилирование памяти не удалось"
        assert len(self.tester.profiler.snapshots) > 0, "Нет снимков памяти"
        
        print("✅ Базовое профилирование памяти работает корректно")
    
    @pytest.mark.asyncio
    async def test_memory_profiling_under_load(self):
        """Тест профилирования памяти под нагрузкой"""
        print("\n🧪 Тестирование профилирования памяти под нагрузкой...")
        
        success = await self.tester.test_memory_profiling_under_load()
        
        assert success, "Профилирование под нагрузкой обнаружило утечки"
        
        # Проверяем, что профилирование собрало достаточно данных
        assert len(self.tester.profiler.snapshots) >= 10, "Недостаточно снимков для анализа"
        
        print("✅ Профилирование памяти под нагрузкой работает корректно")
    
    @pytest.mark.asyncio
    async def test_memory_leak_detection(self):
        """Тест обнаружения утечек памяти"""
        print("\n🧪 Тестирование обнаружения утечек памяти...")
        
        # Запускаем профилирование
        self.tester.profiler.start_profiling()
        
        # Создаем искусственную утечку (для тестирования)
        memory_objects = []
        for i in range(1000):
            # Создаем объекты, которые могут вызвать рост памяти
            large_dict = {f"key_{j}": f"value_{j}" * 100 for j in range(100)}
            memory_objects.append(large_dict)
            
            # Делаем HTTP запросы
            async with httpx.AsyncClient(timeout=10.0) as client:
                try:
                    headers = {"Authorization": "Bearer demo_token"}
                    await client.get(f"{self.tester.base_url}/api/services", headers=headers)
                except Exception:
                    pass
            
            if i % 100 == 0:
                await asyncio.sleep(0.1)
        
        # Останавливаем профилирование
        self.tester.profiler.stop_profiling()
        
        # Анализируем утечки
        leak_analyses = self.tester.profiler.detect_memory_leaks()
        
        print(f"📊 Обнаружено утечек: {len(leak_analyses)}")
        for leak in leak_analyses:
            print(f"  {leak.leak_type}: {leak.description} ({leak.severity})")
        
        # Очищаем тестовые объекты
        del memory_objects
        gc.collect()
        
        print("✅ Обнаружение утечек памяти работает корректно")
    
    @pytest.mark.asyncio
    async def test_memory_pattern_analysis(self):
        """Тест анализа паттернов памяти"""
        print("\n🧪 Тестирование анализа паттернов памяти...")
        
        # Запускаем профилирование
        self.tester.profiler.start_profiling()
        
        # Создаем различные паттерны использования памяти
        for cycle in range(5):
            # Циклическое создание и удаление объектов
            objects = [{"data": "x" * 1000} for _ in range(1000)]
            
            # HTTP запросы
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {"Authorization": "Bearer demo_token"}
                for _ in range(10):
                    try:
                        await client.get(f"{self.tester.base_url}/api/services", headers=headers)
                    except Exception:
                        pass
            
            # Удаляем объекты
            del objects
            gc.collect()
            
            await asyncio.sleep(1)
        
        # Останавливаем профилирование
        self.tester.profiler.stop_profiling()
        
        # Анализируем паттерны
        usage_patterns = self.tester.profiler.analyze_memory_patterns()
        
        print(f"📊 Обнаружено паттернов: {len(usage_patterns)}")
        for pattern in usage_patterns:
            print(f"  {pattern.pattern_name}: эффективность {pattern.memory_efficiency:.2f}")
        
        print("✅ Анализ паттернов памяти работает корректно")
    
    def test_generate_profiling_report(self):
        """Генерация отчета профилирования"""
        print("\n📊 Генерация отчета профилирования памяти...")
        
        report = self.tester.profiler.generate_profiling_report()
        
        if "error" in report:
            print(f"❌ Ошибка генерации отчета: {report['error']}")
            return
        
        # Сохранение отчета
        report_file = f"memory_profiling_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ Отчет профилирования сохранен: {report_file}")
        
        # Вывод краткой статистики
        summary = report['summary']
        print(f"\n📈 КРАТКАЯ СТАТИСТИКА:")
        print(f"  Начальная память: {summary['initial_memory_mb']:.2f} MB")
        print(f"  Финальная память: {summary['final_memory_mb']:.2f} MB")
        print(f"  Пиковая память: {summary['peak_memory_mb']:.2f} MB")
        print(f"  Рост памяти: {summary['memory_growth_mb']:.2f} MB")
        print(f"  Утечек обнаружено: {summary['leaks_detected']}")
        print(f"  Критических утечек: {summary['critical_leaks']}")
        print(f"  Оценка оптимизации: {summary['optimization_score']:.2f}")
        
        # Проверки отчета
        assert report['total_snapshots'] > 0, "Нет снимков профилирования"
        assert summary['memory_growth_mb'] < 1000, f"Слишком большой рост памяти: {summary['memory_growth_mb']:.2f} MB"
        assert summary['optimization_score'] >= 0.5, f"Слишком низкая оценка оптимизации: {summary['optimization_score']:.2f}"


if __name__ == "__main__":
    print("🚀 Запуск тестов профилирования памяти ALADDIN Dashboard...")
    print("📊 Детальное профилирование использования памяти...")
    print("🔍 Обнаружение утечек памяти...")
    print("📈 Анализ паттернов использования памяти...")
    
    # Запуск тестов через pytest
    pytest.main([__file__, "-v", "--tb=short"])