#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Optimization System - Система оптимизации пулов памяти
Умное управление памятью для 14+ функций системы

Функция: Memory Optimization System
Приоритет: ВЫСОКИЙ
Версия: 1.0
Дата: 2025-01-11
"""

import asyncio
import gc
import logging
import psutil
import threading
import time
import weakref
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from weakref import WeakValueDictionary

# Импорт базовых классов
try:
    from core.base import ComponentStatus, SecurityBase
except ImportError:
    # Fallback для тестирования
    class ComponentStatus:
        RUNNING = "running"
        ERROR = "error"
    
    class SecurityBase:
        def __init__(self, name, config=None):
            self.name = name
            self.config = config or {}
            self.status = ComponentStatus.RUNNING

logger = logging.getLogger(__name__)


class MemoryPoolType(Enum):
    """Типы пулов памяти"""
    
    DATABASE = "database"
    CACHE = "cache"
    BUFFER = "buffer"
    THREAD_POOL = "thread_pool"
    OBJECT_POOL = "object_pool"
    CONNECTION_POOL = "connection_pool"


class MemoryStrategy(Enum):
    """Стратегии управления памятью"""
    
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    SIZE_BASED = "size_based"  # По размеру
    FREQUENCY_BASED = "frequency_based"  # По частоте использования


@dataclass
class MemoryMetrics:
    """Метрики использования памяти"""
    
    total_memory: int = 0
    used_memory: int = 0
    free_memory: int = 0
    cache_size: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    gc_collections: int = 0
    memory_pressure: float = 0.0
    fragmentation: float = 0.0
    
    def get_usage_percentage(self) -> float:
        """Получение процента использования памяти"""
        if self.total_memory == 0:
            return 0.0
        return (self.used_memory / self.total_memory) * 100


@dataclass
class MemoryPool:
    """Пул памяти для конкретной функции"""
    
    name: str
    pool_type: MemoryPoolType
    max_size: int
    current_size: int = 0
    strategy: MemoryStrategy = MemoryStrategy.LRU
    ttl_seconds: int = 3600  # 1 час
    access_count: int = 0
    last_access: float = field(default_factory=time.time)
    objects: Dict[str, Any] = field(default_factory=dict)
    access_times: Dict[str, float] = field(default_factory=dict)
    access_frequency: Dict[str, int] = field(default_factory=dict)
    
    def get_hit_rate(self) -> float:
        """Получение hit rate пула"""
        total_access = self.access_count
        if total_access == 0:
            return 0.0
        return (total_access - len(self.objects)) / total_access


class MemoryOptimizationSystem(SecurityBase):
    """Система оптимизации пулов памяти"""

    def __init__(
        self,
        name: str = "MemoryOptimizationSystem",
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(name, config)

        # Конфигурация системы
        self.max_total_memory = config.get("max_total_memory", 1024 * 1024 * 1024) if config else 1024 * 1024 * 1024  # 1GB
        self.memory_pressure_threshold = config.get("memory_pressure_threshold", 0.8) if config else 0.8  # 80%
        self.cleanup_interval = config.get("cleanup_interval", 300) if config else 300  # 5 минут
        
        # Пулы памяти
        self.memory_pools: Dict[str, MemoryPool] = {}
        self.function_memory_map: Dict[str, Set[str]] = defaultdict(set)
        
        # Мониторинг памяти
        self.memory_metrics = MemoryMetrics()
        self.memory_history: deque = deque(maxlen=100)
        
        # Автоматическая очистка
        self._cleanup_thread = None
        self._cleanup_running = False
        
        # Слабые ссылки для автоматической очистки
        self._weak_refs: WeakValueDictionary = WeakValueDictionary()
        
        # Статистика
        self.total_optimizations = 0
        self.memory_freed = 0
        self.optimization_errors = 0

        # Инициализация
        self._initialize_memory_system()

        logger.info(f"Memory Optimization System инициализирован: {name}")

    def _initialize_memory_system(self):
        """Инициализация системы управления памятью"""
        try:
            # Запуск мониторинга памяти
            self._start_memory_monitoring()
            
            # Запуск автоматической очистки
            self._start_cleanup_thread()
            
            logger.info("Система управления памятью инициализирована")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации системы памяти: {e}")
            self.status = ComponentStatus.ERROR

    def create_memory_pool(
        self,
        name: str,
        pool_type: MemoryPoolType,
        max_size: int,
        strategy: MemoryStrategy = MemoryStrategy.LRU,
        ttl_seconds: int = 3600,
    ) -> MemoryPool:
        """Создание пула памяти для функции"""
        try:
            pool = MemoryPool(
                name=name,
                pool_type=pool_type,
                max_size=max_size,
                strategy=strategy,
                ttl_seconds=ttl_seconds,
            )
            
            self.memory_pools[name] = pool
            logger.info(f"Пул памяти создан: {name} (тип: {pool_type.value}, размер: {max_size})")
            
            return pool
            
        except Exception as e:
            logger.error(f"Ошибка создания пула памяти {name}: {e}")
            raise

    def register_function_memory(
        self,
        function_id: str,
        pool_name: str,
        memory_usage: int,
    ) -> bool:
        """Регистрация использования памяти функцией"""
        try:
            if pool_name not in self.memory_pools:
                logger.warning(f"Пул памяти {pool_name} не найден")
                return False
            
            pool = self.memory_pools[pool_name]
            
            # Проверка лимитов
            if pool.current_size + memory_usage > pool.max_size:
                self._optimize_pool(pool_name)
            
            # Обновление метрик
            pool.current_size += memory_usage
            pool.access_count += 1
            pool.last_access = time.time()
            
            # Регистрация в карте функций
            self.function_memory_map[function_id].add(pool_name)
            
            logger.debug(f"Память зарегистрирована: {function_id} -> {pool_name} ({memory_usage} байт)")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка регистрации памяти: {e}")
            return False

    def get_memory_usage(self, function_id: str) -> Dict[str, int]:
        """Получение использования памяти функцией"""
        try:
            usage = {}
            for pool_name in self.function_memory_map.get(function_id, set()):
                if pool_name in self.memory_pools:
                    pool = self.memory_pools[pool_name]
                    usage[pool_name] = pool.current_size
            
            return usage
            
        except Exception as e:
            logger.error(f"Ошибка получения использования памяти: {e}")
            return {}

    def optimize_memory(self, function_id: Optional[str] = None) -> Dict[str, Any]:
        """Оптимизация памяти для функции или всей системы"""
        try:
            start_time = time.time()
            optimization_results = {
                'function_id': function_id,
                'pools_optimized': 0,
                'memory_freed': 0,
                'objects_removed': 0,
                'optimization_time': 0.0,
            }
            
            if function_id:
                # Оптимизация конкретной функции
                pools_to_optimize = self.function_memory_map.get(function_id, set())
                for pool_name in pools_to_optimize:
                    if pool_name in self.memory_pools:
                        result = self._optimize_pool(pool_name)
                        optimization_results['pools_optimized'] += 1
                        optimization_results['memory_freed'] += result.get('memory_freed', 0)
                        optimization_results['objects_removed'] += result.get('objects_removed', 0)
            else:
                # Оптимизация всей системы
                for pool_name in self.memory_pools:
                    result = self._optimize_pool(pool_name)
                    optimization_results['pools_optimized'] += 1
                    optimization_results['memory_freed'] += result.get('memory_freed', 0)
                    optimization_results['objects_removed'] += result.get('objects_removed', 0)
            
            # Принудительная сборка мусора
            gc.collect()
            
            optimization_results['optimization_time'] = time.time() - start_time
            self.total_optimizations += 1
            self.memory_freed += optimization_results['memory_freed']
            
            logger.info(f"Оптимизация памяти завершена: {optimization_results}")
            return optimization_results
            
        except Exception as e:
            self.optimization_errors += 1
            logger.error(f"Ошибка оптимизации памяти: {e}")
            return {'error': str(e)}

    def _optimize_pool(self, pool_name: str) -> Dict[str, Any]:
        """Оптимизация конкретного пула памяти"""
        try:
            if pool_name not in self.memory_pools:
                return {'error': f'Пул {pool_name} не найден'}
            
            pool = self.memory_pools[pool_name]
            result = {
                'memory_freed': 0,
                'objects_removed': 0,
            }
            
            # Применение стратегии очистки
            if pool.strategy == MemoryStrategy.LRU:
                result.update(self._cleanup_lru(pool))
            elif pool.strategy == MemoryStrategy.LFU:
                result.update(self._cleanup_lfu(pool))
            elif pool.strategy == MemoryStrategy.TTL:
                result.update(self._cleanup_ttl(pool))
            elif pool.strategy == MemoryStrategy.SIZE_BASED:
                result.update(self._cleanup_size_based(pool))
            elif pool.strategy == MemoryStrategy.FREQUENCY_BASED:
                result.update(self._cleanup_frequency_based(pool))
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка оптимизации пула {pool_name}: {e}")
            return {'error': str(e)}

    def _cleanup_lru(self, pool: MemoryPool) -> Dict[str, int]:
        """Очистка по стратегии LRU (Least Recently Used)"""
        memory_freed = 0
        objects_removed = 0
        
        # Сортировка по времени последнего доступа
        sorted_objects = sorted(
            pool.access_times.items(),
            key=lambda x: x[1]
        )
        
        # Удаление 20% самых старых объектов
        objects_to_remove = len(sorted_objects) // 5
        for obj_id, _ in sorted_objects[:objects_to_remove]:
            if obj_id in pool.objects:
                del pool.objects[obj_id]
                del pool.access_times[obj_id]
                objects_removed += 1
        
        pool.current_size = len(pool.objects)
        return {'memory_freed': memory_freed, 'objects_removed': objects_removed}

    def _cleanup_lfu(self, pool: MemoryPool) -> Dict[str, int]:
        """Очистка по стратегии LFU (Least Frequently Used)"""
        memory_freed = 0
        objects_removed = 0
        
        # Сортировка по частоте использования
        sorted_objects = sorted(
            pool.access_frequency.items(),
            key=lambda x: x[1]
        )
        
        # Удаление 20% наименее используемых объектов
        objects_to_remove = len(sorted_objects) // 5
        for obj_id, _ in sorted_objects[:objects_to_remove]:
            if obj_id in pool.objects:
                del pool.objects[obj_id]
                del pool.access_frequency[obj_id]
                objects_removed += 1
        
        pool.current_size = len(pool.objects)
        return {'memory_freed': memory_freed, 'objects_removed': objects_removed}

    def _cleanup_ttl(self, pool: MemoryPool) -> Dict[str, int]:
        """Очистка по TTL (Time To Live)"""
        memory_freed = 0
        objects_removed = 0
        current_time = time.time()
        
        # Удаление объектов с истекшим TTL
        expired_objects = []
        for obj_id, access_time in pool.access_times.items():
            if current_time - access_time > pool.ttl_seconds:
                expired_objects.append(obj_id)
        
        for obj_id in expired_objects:
            if obj_id in pool.objects:
                del pool.objects[obj_id]
                del pool.access_times[obj_id]
                objects_removed += 1
        
        pool.current_size = len(pool.objects)
        return {'memory_freed': memory_freed, 'objects_removed': objects_removed}

    def _cleanup_size_based(self, pool: MemoryPool) -> Dict[str, int]:
        """Очистка по размеру объектов"""
        memory_freed = 0
        objects_removed = 0
        
        # Сортировка объектов по размеру (если доступно)
        # Удаление самых больших объектов
        objects_to_remove = len(pool.objects) // 5
        for obj_id in list(pool.objects.keys())[:objects_to_remove]:
            del pool.objects[obj_id]
            objects_removed += 1
        
        pool.current_size = len(pool.objects)
        return {'memory_freed': memory_freed, 'objects_removed': objects_removed}

    def _cleanup_frequency_based(self, pool: MemoryPool) -> Dict[str, int]:
        """Очистка по частоте использования"""
        memory_freed = 0
        objects_removed = 0
        
        # Удаление объектов с низкой частотой использования
        avg_frequency = sum(pool.access_frequency.values()) / len(pool.access_frequency) if pool.access_frequency else 0
        
        for obj_id, frequency in list(pool.access_frequency.items()):
            if frequency < avg_frequency * 0.5:  # Менее 50% от средней частоты
                if obj_id in pool.objects:
                    del pool.objects[obj_id]
                    del pool.access_frequency[obj_id]
                    objects_removed += 1
        
        pool.current_size = len(pool.objects)
        return {'memory_freed': memory_freed, 'objects_removed': objects_removed}

    def _start_memory_monitoring(self):
        """Запуск мониторинга памяти"""
        def monitor_memory():
            while self.status == ComponentStatus.RUNNING:
                try:
                    # Получение метрик системы
                    memory_info = psutil.virtual_memory()
                    
                    self.memory_metrics.total_memory = memory_info.total
                    self.memory_metrics.used_memory = memory_info.used
                    self.memory_metrics.free_memory = memory_info.available
                    self.memory_metrics.memory_pressure = memory_info.percent / 100.0
                    
                    # Обновление истории
                    self.memory_history.append({
                        'timestamp': time.time(),
                        'used_memory': memory_info.used,
                        'memory_pressure': memory_info.percent / 100.0,
                    })
                    
                    # Проверка давления памяти
                    if self.memory_metrics.memory_pressure > self.memory_pressure_threshold:
                        logger.warning(f"Высокое давление памяти: {self.memory_metrics.memory_pressure:.2%}")
                        self.optimize_memory()
                    
                    time.sleep(60)  # Проверка каждую минуту
                    
                except Exception as e:
                    logger.error(f"Ошибка мониторинга памяти: {e}")
                    time.sleep(60)
        
        monitoring_thread = threading.Thread(target=monitor_memory, daemon=True)
        monitoring_thread.start()
        logger.info("Мониторинг памяти запущен")

    def _start_cleanup_thread(self):
        """Запуск автоматической очистки"""
        def cleanup_loop():
            while self.status == ComponentStatus.RUNNING:
                try:
                    time.sleep(self.cleanup_interval)
                    
                    # Автоматическая оптимизация
                    self.optimize_memory()
                    
                    logger.debug("Автоматическая очистка памяти выполнена")
                    
                except Exception as e:
                    logger.error(f"Ошибка автоматической очистки: {e}")
        
        self._cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        self._cleanup_thread.start()
        logger.info("Автоматическая очистка памяти запущена")

    def get_memory_metrics(self) -> Dict[str, Any]:
        """Получение метрик памяти"""
        return {
            'total_memory': self.memory_metrics.total_memory,
            'used_memory': self.memory_metrics.used_memory,
            'free_memory': self.memory_metrics.free_memory,
            'usage_percentage': self.memory_metrics.get_usage_percentage(),
            'memory_pressure': self.memory_metrics.memory_pressure,
            'pools_count': len(self.memory_pools),
            'total_optimizations': self.total_optimizations,
            'memory_freed': self.memory_freed,
            'optimization_errors': self.optimization_errors,
            'pools_metrics': {
                name: {
                    'current_size': pool.current_size,
                    'max_size': pool.max_size,
                    'hit_rate': pool.get_hit_rate(),
                    'access_count': pool.access_count,
                }
                for name, pool in self.memory_pools.items()
            }
        }

    def get_memory_report(self) -> Dict[str, Any]:
        """Получение отчета по памяти"""
        return {
            'system_metrics': self.get_memory_metrics(),
            'memory_history': list(self.memory_history),
            'function_memory_map': dict(self.function_memory_map),
            'recommendations': self._get_memory_recommendations(),
        }

    def _get_memory_recommendations(self) -> List[str]:
        """Получение рекомендаций по оптимизации памяти"""
        recommendations = []
        
        if self.memory_metrics.memory_pressure > 0.8:
            recommendations.append("Критическое давление памяти - требуется немедленная оптимизация")
        
        if self.memory_metrics.memory_pressure > 0.6:
            recommendations.append("Высокое давление памяти - рекомендуется очистка кэша")
        
        for pool_name, pool in self.memory_pools.items():
            if pool.current_size > pool.max_size * 0.9:
                recommendations.append(f"Пул {pool_name} почти заполнен - требуется очистка")
            
            if pool.get_hit_rate() < 0.5:
                recommendations.append(f"Низкий hit rate у пула {pool_name} - рассмотрите изменение стратегии")
        
        return recommendations

    def __del__(self):
        """Деструктор для очистки ресурсов"""
        if hasattr(self, '_cleanup_thread') and self._cleanup_thread:
            self._cleanup_running = False


# ============================================================================
# ТЕСТИРОВАНИЕ СИСТЕМЫ ОПТИМИЗАЦИИ ПАМЯТИ
# ============================================================================

if __name__ == "__main__":
    print("💾 ТЕСТИРОВАНИЕ СИСТЕМЫ ОПТИМИЗАЦИИ ПАМЯТИ")
    print("=" * 60)
    
    # Создание системы оптимизации памяти
    memory_system = MemoryOptimizationSystem("TestMemorySystem")
    
    # Создание пулов памяти для разных функций
    print("\n1. Создание пулов памяти:")
    
    # Пул для базы данных
    db_pool = memory_system.create_memory_pool(
        "database_pool",
        MemoryPoolType.DATABASE,
        max_size=100 * 1024 * 1024,  # 100MB
        strategy=MemoryStrategy.LRU
    )
    print(f"   ✅ Пул базы данных: {db_pool.name}")
    
    # Пул для кэша
    cache_pool = memory_system.create_memory_pool(
        "cache_pool",
        MemoryPoolType.CACHE,
        max_size=50 * 1024 * 1024,  # 50MB
        strategy=MemoryStrategy.TTL,
        ttl_seconds=1800  # 30 минут
    )
    print(f"   ✅ Пул кэша: {cache_pool.name}")
    
    # Пул для тестирования
    test_pool = memory_system.create_memory_pool(
        "test_pool",
        MemoryPoolType.OBJECT_POOL,
        max_size=10 * 1024 * 1024,  # 10MB
        strategy=MemoryStrategy.LFU
    )
    print(f"   ✅ Пул тестирования: {test_pool.name}")
    
    # Регистрация использования памяти
    print("\n2. Регистрация использования памяти:")
    
    # Симуляция использования памяти функциями
    test_functions = [
        ("database", "database_pool", 1024 * 1024),  # 1MB
        ("security_cacheentry", "cache_pool", 512 * 1024),  # 512KB
        ("test_cache", "test_pool", 256 * 1024),  # 256KB
    ]
    
    for func_id, pool_name, memory_usage in test_functions:
        success = memory_system.register_function_memory(func_id, pool_name, memory_usage)
        if success:
            print(f"   ✅ {func_id}: {memory_usage // 1024}KB в {pool_name}")
        else:
            print(f"   ❌ {func_id}: ошибка регистрации")
    
    # Получение метрик
    print("\n3. Метрики памяти:")
    metrics = memory_system.get_memory_metrics()
    for key, value in metrics.items():
        if isinstance(value, dict):
            print(f"   📊 {key}:")
            for sub_key, sub_value in value.items():
                print(f"      {sub_key}: {sub_value}")
        else:
            print(f"   📊 {key}: {value}")
    
    # Оптимизация памяти
    print("\n4. Оптимизация памяти:")
    optimization_result = memory_system.optimize_memory()
    print(f"   ✅ Оптимизация завершена:")
    for key, value in optimization_result.items():
        print(f"      {key}: {value}")
    
    # Отчет по памяти
    print("\n5. Отчет по памяти:")
    report = memory_system.get_memory_report()
    recommendations = report.get('recommendations', [])
    if recommendations:
        print("   📋 Рекомендации:")
        for rec in recommendations:
            print(f"      • {rec}")
    else:
        print("   ✅ Рекомендации отсутствуют - система работает оптимально")
    
    print("\n🎉 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")