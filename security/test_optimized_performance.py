"""
Тест производительности оптимизированной версии SFM
Сравнение: оригинальная vs оптимизированная версия
"""

import os
import sys
import time
import psutil
import json
import asyncio
from typing import Dict, Any

# Добавляем путь к проекту
sys.path.append('/Users/sergejhlystov/ALADDIN_NEW')

def test_original_sfm():
    """Тест оригинальной версии SFM"""
    print('
🔍 ТЕСТИРОВАНИЕ ОРИГИНАЛЬНОЙ ВЕРСИИ SFM')
    print('-' * 50)
    
    start_time = time.time()
    start_memory = psutil.Process().memory_info().rss / 1024 / 1024
    
    try:
        from security.safe_function_manager import SafeFunctionManager
        sfm = SafeFunctionManager()
        sfm.initialize()
        
        load_time = time.time() - start_time
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_used = end_memory - start_memory
        
        print(f'   ⏱️  Время загрузки: {load_time:.3f} сек')
        print(f'   💾 Память: {memory_used:.2f} MB')
        print(f'   📦 Функций загружено: {len(sfm.functions)}')
        
        return {
            'load_time': load_time,
            'memory_used': memory_used,
            'functions_count': len(sfm.functions),
            'success': True
        }
        
    except Exception as e:
        print(f'   ❌ Ошибка: {e}')
        return {
            'load_time': 0,
            'memory_used': 0,
            'functions_count': 0,
            'success': False,
            'error': str(e)
        }

def test_optimized_sfm():
    """Тест оптимизированной версии SFM"""
    print('
🚀 ТЕСТИРОВАНИЕ ОПТИМИЗИРОВАННОЙ ВЕРСИИ SFM')
    print('-' * 50)
    
    start_time = time.time()
    start_memory = psutil.Process().memory_info().rss / 1024 / 1024
    
    try:
        from security.optimized_safe_function_manager import OptimizedSafeFunctionManager
        sfm = OptimizedSafeFunctionManager()
        
        # Асинхронная инициализация
        async def init_sfm():
            await sfm.initialize_async()
            return sfm
        
        # Запускаем асинхронную инициализацию
        sfm = asyncio.run(init_sfm())
        
        load_time = time.time() - start_time
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_used = end_memory - start_memory
        
        print(f'   ⏱️  Время загрузки: {load_time:.3f} сек')
        print(f'   💾 Память: {memory_used:.2f} MB')
        print(f'   📦 Функций загружено: {len(sfm.functions)}')
        
        # Получаем статистику
        stats = sfm.get_stats()
        print(f'   📊 Статистика: {stats}')
        
        return {
            'load_time': load_time,
            'memory_used': memory_used,
            'functions_count': len(sfm.functions),
            'success': True,
            'stats': stats
        }
        
    except Exception as e:
        print(f'   ❌ Ошибка: {e}')
        return {
            'load_time': 0,
            'memory_used': 0,
            'functions_count': 0,
            'success': False,
            'error': str(e)
        }

def main():
    """Основная функция тестирования"""
    print('🧪 КОМПЛЕКСНОЕ ТЕСТИРОВАНИЕ ПРОИЗВОДИТЕЛЬНОСТИ')
    print('=' * 70)
    
    # Тест 1: Оригинальная версия
    original_results = test_original_sfm()
    
    # Тест 2: Оптимизированная версия
    optimized_results = test_optimized_sfm()
    
    # Сравнение результатов
    print('
📊 СРАВНЕНИЕ РЕЗУЛЬТАТОВ')
    print('=' * 70)
    
    if original_results['success'] and optimized_results['success']:
        time_improvement = ((original_results['load_time'] - optimized_results['load_time']) / original_results['load_time']) * 100
        memory_improvement = ((original_results['memory_used'] - optimized_results['memory_used']) / original_results['memory_used']) * 100
        
        print(f'⏱️  ВРЕМЯ ЗАГРУЗКИ:')
        print(f'   Оригинальная: {original_results["load_time"]:.3f} сек')
        print(f'   Оптимизированная: {optimized_results["load_time"]:.3f} сек')
        print(f'   Улучшение: {time_improvement:+.1f}%')
        
        print(f'
💾 ПАМЯТЬ:')
        print(f'   Оригинальная: {original_results["memory_used"]:.2f} MB')
        print(f'   Оптимизированная: {optimized_results["memory_used"]:.2f} MB')
        print(f'   Улучшение: {memory_improvement:+.1f}%')
        
        print(f'
📦 ФУНКЦИИ:')
        print(f'   Оригинальная: {original_results["functions_count"]} функций')
        print(f'   Оптимизированная: {optimized_results["functions_count"]} функций')
    
    # Сохраняем результаты
    test_results = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'original': original_results,
        'optimized': optimized_results
    }
    
    with open('security/performance_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)
    
    print(f'
💾 Результаты сохранены: security/performance_test_results.json')
    print(f'
🎯 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!')

if __name__ == '__main__':
    main()
