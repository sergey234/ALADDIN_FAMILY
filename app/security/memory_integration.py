#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Integration - Интеграция системы оптимизации памяти с SFM
Автоматическая оптимизация памяти для 14+ функций

Функция: Memory Integration System
Приоритет: ВЫСОКИЙ
Версия: 1.0
Дата: 2025-01-11
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Set

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from memory_optimization_system import (
    MemoryOptimizationSystem,
    MemoryPoolType,
    MemoryStrategy,
)
from safe_function_manager import SafeFunctionManager

logger = logging.getLogger(__name__)


class MemoryIntegrationSystem:
    """Система интеграции оптимизации памяти с SFM"""

    def __init__(
        self,
        sfm: SafeFunctionManager,
        memory_system: MemoryOptimizationSystem,
    ):
        self.sfm = sfm
        self.memory_system = memory_system
        
        # Карта функций для оптимизации памяти
        self.functions_to_optimize = {
            # Функции базы данных
            'database': {
                'pool_name': 'database_pool',
                'pool_type': MemoryPoolType.DATABASE,
                'max_size': 200 * 1024 * 1024,  # 200MB
                'strategy': MemoryStrategy.LRU,
            },
            'security_loadbalancer': {
                'pool_name': 'loadbalancer_pool',
                'pool_type': MemoryPoolType.CONNECTION_POOL,
                'max_size': 50 * 1024 * 1024,  # 50MB
                'strategy': MemoryStrategy.TTL,
            },
            
            # Функции кэширования
            'security_cacheentry': {
                'pool_name': 'cache_pool',
                'pool_type': MemoryPoolType.CACHE,
                'max_size': 100 * 1024 * 1024,  # 100MB
                'strategy': MemoryStrategy.TTL,
            },
            'security_rediscachemanager': {
                'pool_name': 'redis_cache_pool',
                'pool_type': MemoryPoolType.CACHE,
                'max_size': 150 * 1024 * 1024,  # 150MB
                'strategy': MemoryStrategy.LRU,
            },
            'security_cachemetrics': {
                'pool_name': 'cache_metrics_pool',
                'pool_type': MemoryPoolType.CACHE,
                'max_size': 25 * 1024 * 1024,  # 25MB
                'strategy': MemoryStrategy.LFU,
            },
            
            # Функции тестирования
            'test_cache': {
                'pool_name': 'test_pool',
                'pool_type': MemoryPoolType.OBJECT_POOL,
                'max_size': 30 * 1024 * 1024,  # 30MB
                'strategy': MemoryStrategy.LFU,
            },
            'security_testmanager': {
                'pool_name': 'test_manager_pool',
                'pool_type': MemoryPoolType.OBJECT_POOL,
                'max_size': 20 * 1024 * 1024,  # 20MB
                'strategy': MemoryStrategy.TTL,
            },
            'family_testing_system': {
                'pool_name': 'family_test_pool',
                'pool_type': MemoryPoolType.OBJECT_POOL,
                'max_size': 40 * 1024 * 1024,  # 40MB
                'strategy': MemoryStrategy.LRU,
            },
            'run_performance_tests': {
                'pool_name': 'performance_test_pool',
                'pool_type': MemoryPoolType.OBJECT_POOL,
                'max_size': 60 * 1024 * 1024,  # 60MB
                'strategy': MemoryStrategy.SIZE_BASED,
            },
            
            # Функции потоков
            'thread_pool_manager': {
                'pool_name': 'thread_pool',
                'pool_type': MemoryPoolType.THREAD_POOL,
                'max_size': 80 * 1024 * 1024,  # 80MB
                'strategy': MemoryStrategy.LRU,
            },
            
            # Дополнительные функции
            'security_loadbalancingresponse': {
                'pool_name': 'loadbalancing_pool',
                'pool_type': MemoryPoolType.BUFFER,
                'max_size': 30 * 1024 * 1024,  # 30MB
                'strategy': MemoryStrategy.TTL,
            },
            'security_loadbalancingalgorithminterface': {
                'pool_name': 'algorithm_pool',
                'pool_type': MemoryPoolType.OBJECT_POOL,
                'max_size': 15 * 1024 * 1024,  # 15MB
                'strategy': MemoryStrategy.LFU,
            },
            'security_loadbalancingrequest': {
                'pool_name': 'request_pool',
                'pool_type': MemoryPoolType.BUFFER,
                'max_size': 25 * 1024 * 1024,  # 25MB
                'strategy': MemoryStrategy.LRU,
            },
            'test_function': {
                'pool_name': 'general_test_pool',
                'pool_type': MemoryPoolType.OBJECT_POOL,
                'max_size': 10 * 1024 * 1024,  # 10MB
                'strategy': MemoryStrategy.LFU,
            },
            'test_auto_save': {
                'pool_name': 'autosave_pool',
                'pool_type': MemoryPoolType.OBJECT_POOL,
                'max_size': 5 * 1024 * 1024,  # 5MB
                'strategy': MemoryStrategy.TTL,
            },
        }
        
        # Инициализация пулов памяти
        self._initialize_memory_pools()
        
        logger.info("Memory Integration System инициализирован")

    def _initialize_memory_pools(self):
        """Инициализация пулов памяти для всех функций"""
        try:
            for func_id, config in self.functions_to_optimize.items():
                # Создание пула памяти
                pool = self.memory_system.create_memory_pool(
                    name=config['pool_name'],
                    pool_type=config['pool_type'],
                    max_size=config['max_size'],
                    strategy=config['strategy'],
                    ttl_seconds=3600,  # 1 час по умолчанию
                )
                
                logger.info(f"Пул памяти создан для {func_id}: {config['pool_name']}")
                
        except Exception as e:
            logger.error(f"Ошибка инициализации пулов памяти: {e}")

    def register_function_memory_usage(
        self,
        function_id: str,
        memory_usage: int,
        operation_type: str = "general",
    ) -> bool:
        """Регистрация использования памяти функцией"""
        try:
            if function_id not in self.functions_to_optimize:
                logger.warning(f"Функция {function_id} не настроена для оптимизации памяти")
                return False
            
            config = self.functions_to_optimize[function_id]
            pool_name = config['pool_name']
            
            # Регистрация в системе памяти
            success = self.memory_system.register_function_memory(
                function_id=function_id,
                pool_name=pool_name,
                memory_usage=memory_usage,
            )
            
            if success:
                logger.debug(f"Память зарегистрирована: {function_id} -> {pool_name} ({memory_usage} байт)")
            
            return success
            
        except Exception as e:
            logger.error(f"Ошибка регистрации памяти для {function_id}: {e}")
            return False

    def optimize_function_memory(self, function_id: str) -> Dict[str, Any]:
        """Оптимизация памяти для конкретной функции"""
        try:
            if function_id not in self.functions_to_optimize:
                return {'error': f'Функция {function_id} не настроена для оптимизации'}
            
            # Получение текущего использования памяти
            current_usage = self.memory_system.get_memory_usage(function_id)
            
            # Оптимизация памяти
            optimization_result = self.memory_system.optimize_memory(function_id)
            
            # Получение нового использования памяти
            new_usage = self.memory_system.get_memory_usage(function_id)
            
            # Расчет освобожденной памяти
            memory_freed = sum(current_usage.values()) - sum(new_usage.values())
            
            result = {
                'function_id': function_id,
                'memory_freed': memory_freed,
                'current_usage': current_usage,
                'new_usage': new_usage,
                'optimization_result': optimization_result,
            }
            
            logger.info(f"Оптимизация памяти для {function_id}: освобождено {memory_freed} байт")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка оптимизации памяти для {function_id}: {e}")
            return {'error': str(e)}

    def optimize_all_functions_memory(self) -> Dict[str, Any]:
        """Оптимизация памяти для всех функций"""
        try:
            start_time = time.time()
            results = {}
            total_memory_freed = 0
            
            # Оптимизация каждой функции
            for function_id in self.functions_to_optimize.keys():
                result = self.optimize_function_memory(function_id)
                results[function_id] = result
                
                if 'memory_freed' in result:
                    total_memory_freed += result['memory_freed']
            
            # Общая оптимизация системы
            system_optimization = self.memory_system.optimize_memory()
            
            total_result = {
                'functions_optimized': len(self.functions_to_optimize),
                'total_memory_freed': total_memory_freed,
                'optimization_time': time.time() - start_time,
                'system_optimization': system_optimization,
                'individual_results': results,
            }
            
            logger.info(f"Оптимизация памяти завершена: освобождено {total_memory_freed} байт")
            return total_result
            
        except Exception as e:
            logger.error(f"Ошибка общей оптимизации памяти: {e}")
            return {'error': str(e)}

    def get_memory_status_for_functions(self) -> Dict[str, Any]:
        """Получение статуса памяти для всех функций"""
        try:
            status = {}
            
            for function_id in self.functions_to_optimize.keys():
                usage = self.memory_system.get_memory_usage(function_id)
                config = self.functions_to_optimize[function_id]
                
                status[function_id] = {
                    'pool_name': config['pool_name'],
                    'pool_type': config['pool_type'].value,
                    'strategy': config['strategy'].value,
                    'max_size': config['max_size'],
                    'current_usage': usage,
                    'usage_percentage': (sum(usage.values()) / config['max_size']) * 100 if config['max_size'] > 0 else 0,
                }
            
            return status
            
        except Exception as e:
            logger.error(f"Ошибка получения статуса памяти: {e}")
            return {}

    def get_memory_recommendations(self) -> List[str]:
        """Получение рекомендаций по оптимизации памяти"""
        try:
            recommendations = []
            status = self.get_memory_status_for_functions()
            
            for function_id, info in status.items():
                usage_percentage = info['usage_percentage']
                
                if usage_percentage > 90:
                    recommendations.append(f"Критическое использование памяти у {function_id} ({usage_percentage:.1f}%)")
                elif usage_percentage > 75:
                    recommendations.append(f"Высокое использование памяти у {function_id} ({usage_percentage:.1f}%)")
                elif usage_percentage < 10:
                    recommendations.append(f"Низкое использование памяти у {function_id} ({usage_percentage:.1f}%) - можно увеличить лимит")
            
            # Общие рекомендации системы
            system_metrics = self.memory_system.get_memory_metrics()
            if system_metrics['memory_pressure'] > 0.8:
                recommendations.append("Критическое давление памяти в системе - требуется немедленная оптимизация")
            elif system_metrics['memory_pressure'] > 0.6:
                recommendations.append("Высокое давление памяти в системе - рекомендуется очистка")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Ошибка получения рекомендаций: {e}")
            return []

    async def auto_optimize_memory(self):
        """Автоматическая оптимизация памяти"""
        try:
            while True:
                # Проверка каждые 5 минут
                await asyncio.sleep(300)
                
                # Получение метрик системы
                metrics = self.memory_system.get_memory_metrics()
                
                # Автоматическая оптимизация при высоком давлении памяти
                if metrics['memory_pressure'] > 0.7:
                    logger.info("Автоматическая оптимизация памяти запущена")
                    result = self.optimize_all_functions_memory()
                    logger.info(f"Автоматическая оптимизация завершена: {result}")
                
        except Exception as e:
            logger.error(f"Ошибка автоматической оптимизации: {e}")


# ============================================================================
# ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ ПАМЯТИ
# ============================================================================

if __name__ == "__main__":
    print("💾 ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ СИСТЕМЫ ПАМЯТИ")
    print("=" * 60)
    
    # Создание SFM и системы памяти
    sfm = SafeFunctionManager("TestSFM")
    memory_system = MemoryOptimizationSystem("TestMemorySystem")
    integration = MemoryIntegrationSystem(sfm, memory_system)
    
    print(f"📊 Функций настроено для оптимизации: {len(integration.functions_to_optimize)}")
    
    # Симуляция использования памяти
    print("\n1. Симуляция использования памяти:")
    test_functions = [
        ("database", 1024 * 1024 * 10),  # 10MB
        ("security_cacheentry", 1024 * 1024 * 5),  # 5MB
        ("test_cache", 1024 * 1024 * 2),  # 2MB
    ]
    
    for func_id, memory_usage in test_functions:
        success = integration.register_function_memory_usage(func_id, memory_usage)
        if success:
            print(f"   ✅ {func_id}: {memory_usage // 1024}KB зарегистрировано")
        else:
            print(f"   ❌ {func_id}: ошибка регистрации")
    
    # Получение статуса памяти
    print("\n2. Статус памяти функций:")
    status = integration.get_memory_status_for_functions()
    for func_id, info in list(status.items())[:3]:  # Показываем первые 3
        print(f"   📊 {func_id}:")
        print(f"      Пул: {info['pool_name']}")
        print(f"      Использование: {info['usage_percentage']:.1f}%")
        print(f"      Текущее: {sum(info['current_usage'].values()) // 1024}KB")
    
    # Оптимизация памяти
    print("\n3. Оптимизация памяти:")
    optimization_result = integration.optimize_all_functions_memory()
    print(f"   ✅ Оптимизация завершена:")
    print(f"      Функций оптимизировано: {optimization_result['functions_optimized']}")
    print(f"      Памяти освобождено: {optimization_result['total_memory_freed'] // 1024}KB")
    print(f"      Время оптимизации: {optimization_result['optimization_time']:.2f} сек")
    
    # Рекомендации
    print("\n4. Рекомендации по памяти:")
    recommendations = integration.get_memory_recommendations()
    if recommendations:
        for rec in recommendations:
            print(f"   📋 {rec}")
    else:
        print("   ✅ Рекомендации отсутствуют - система работает оптимально")
    
    # Метрики системы
    print("\n5. Метрики системы памяти:")
    metrics = memory_system.get_memory_metrics()
    print(f"   📊 Общее использование: {metrics['usage_percentage']:.1f}%")
    print(f"   📊 Давление памяти: {metrics['memory_pressure']:.2f}")
    print(f"   📊 Пулов памяти: {metrics['pools_count']}")
    print(f"   📊 Оптимизаций выполнено: {metrics['total_optimizations']}")
    
    print("\n🎉 ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ ЗАВЕРШЕНО!")