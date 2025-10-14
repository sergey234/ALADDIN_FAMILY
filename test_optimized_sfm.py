#!/usr/bin/env python3
"""
Тест оптимизированной версии SafeFunctionManager
"""

import os
import sys
import time
import psutil
import json

# Добавляем корневую директорию проекта в sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

print('🚀 ТЕСТИРОВАНИЕ ОПТИМИЗИРОВАННОГО SFM')
print('=' * 70)

print('\n🧪 ТЕСТИРОВАНИЕ ОПТИМИЗИРОВАННОЙ ВЕРСИИ SFM')
print('-' * 50)

start_time = time.time()
start_memory = psutil.Process().memory_info().rss / 1024 / 1024

try:
    from security.safe_function_manager import SafeFunctionManager
    sfm = SafeFunctionManager()
    sfm.initialize()
    
    load_time = time.time() - start_time
    memory = psutil.Process().memory_info().rss / 1024 / 1024
    memory_used = memory - start_memory
    
    print(f'   ⏱️  Время загрузки: {load_time:.3f} сек')
    print(f'   💾 Память: {memory_used:.2f} MB')
    print(f'   📦 Функций: {len(sfm.functions)}')
    
    # Получаем статистику оптимизации
    optimization_stats = sfm.get_optimization_stats()
    print(f'   🔧 Компоненты оптимизации:')
    print(f'      Memory Pool: {optimization_stats["memory_pool"]["size"]} объектов')
    print(f'      Import Cache: {optimization_stats["import_optimizer"]["cached_imports"]} модулей')
    print(f'      Performance Optimizer: {"✅" if optimization_stats["performance_optimizer"] else "❌"}')
    print(f'      Redis Cache: {"✅" if optimization_stats["redis_cache"] else "❌"}')
    print(f'      Async IO: {"✅" if optimization_stats["async_io"] else "❌"}')
    
    success = True
    
except Exception as e:
    print(f'   ❌ Ошибка: {e}')
    import traceback
    traceback.print_exc()
    success = False
    load_time = 0
    memory_used = 0

print('\n📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ')
print('=' * 70)

if success:
    print(f'✅ SFM успешно инициализирован!')
    print(f'⏱️  Время загрузки: {load_time:.3f} сек')
    print(f'💾 Память: {memory_used:.2f} MB')
    print(f'📦 Функций: {len(sfm.functions)}')
    print(f'🔧 Компоненты оптимизации: {len(optimization_stats)}')
    
    # Анализ производительности
    print(f'\n🎯 АНАЛИЗ ПРОИЗВОДИТЕЛЬНОСТИ:')
    if load_time < 5.0:
        print(f'   ✅ Время загрузки отличное: {load_time:.3f} сек')
    elif load_time < 10.0:
        print(f'   ⚠️  Время загрузки приемлемое: {load_time:.3f} сек')
    else:
        print(f'   ❌ Время загрузки медленное: {load_time:.3f} сек')
    
    if memory_used < 100:
        print(f'   ✅ Память используется эффективно: {memory_used:.2f} MB')
    elif memory_used < 200:
        print(f'   ⚠️  Память используется умеренно: {memory_used:.2f} MB')
    else:
        print(f'   ❌ Память используется много: {memory_used:.2f} MB')
        
else:
    print(f'❌ Ошибка инициализации SFM')

print(f'\n�� АНАЛИЗ ПРОБЛЕМ:')
if not success:
    print('   ❌ Оптимизированная версия не работает')
    print('   🔧 Проверьте логи и исправьте ошибки')
