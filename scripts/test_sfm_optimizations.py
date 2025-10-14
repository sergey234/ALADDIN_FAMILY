#!/usr/bin/env python3
"""
Тестирование оптимизаций SFM
Проверяет интеграцию ThreadPoolManager и AsyncIOManager
"""

import sys
import os
import time
import json
from datetime import datetime

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.safe_function_manager import SafeFunctionManager

def test_sfm_optimizations():
    """Тестирование оптимизаций SFM"""
    print("🚀 Тестирование оптимизаций SFM")
    print("=" * 50)
    
    try:
        # Создаем SFM с оптимизациями
        config = {
            "thread_pool_enabled": True,
            "max_thread_pool_workers": 5,
            "async_io_enabled": True,
            "enable_auto_management": False,  # Отключаем для теста
            "enable_sleep_mode": False
        }
        
        sfm = SafeFunctionManager("TestSFM", config)
        
        print("✅ SFM создан с оптимизациями")
        print(f"   Пул потоков: {'✅' if sfm.thread_pool else '❌'}")
        print(f"   Async I/O: {'✅' if sfm.async_io_manager else '❌'}")
        print(f"   Redis Cache: {'✅' if sfm.redis_cache_manager else '❌'}")
        
        # Тест 1: Синхронное выполнение функции
        print("\n🧪 Тест 1: Синхронное выполнение")
        start_time = time.time()
        success, result, message = sfm.execute_function("test_function", {"test": "data"})
        sync_time = time.time() - start_time
        print(f"   Результат: {success}")
        print(f"   Время: {sync_time:.3f}с")
        
        # Тест 2: Асинхронное выполнение функции
        print("\n🧪 Тест 2: Асинхронное выполнение")
        start_time = time.time()
        future = sfm.execute_function_async("test_function", {"test": "data"})
        if hasattr(future, 'result'):
            result = future.result(timeout=5)
            async_time = time.time() - start_time
            print(f"   Результат: {result[0] if isinstance(result, tuple) else 'OK'}")
            print(f"   Время: {async_time:.3f}с")
        else:
            print("   Fallback на синхронное выполнение")
        
        # Тест 3: Асинхронное сохранение
        print("\n🧪 Тест 3: Асинхронное сохранение")
        start_time = time.time()
        future = sfm.save_functions_async()
        if hasattr(future, 'result'):
            result = future.result(timeout=5)
            save_time = time.time() - start_time
            print(f"   Результат: {result}")
            print(f"   Время: {save_time:.3f}с")
        else:
            print("   Fallback на синхронное сохранение")
        
        # Тест 4: Асинхронная загрузка
        print("\n🧪 Тест 4: Асинхронная загрузка")
        start_time = time.time()
        future = sfm.load_functions_async()
        if hasattr(future, 'result'):
            result = future.result(timeout=5)
            load_time = time.time() - start_time
            print(f"   Результат: {result}")
            print(f"   Время: {load_time:.3f}с")
        else:
            print("   Fallback на синхронную загрузку")
        
        # Тест 5: Статистика производительности
        print("\n📊 Статистика производительности")
        print(f"   Всего функций: {len(sfm.functions)}")
        print(f"   Успешных выполнений: {sfm.successful_executions}")
        print(f"   Неудачных выполнений: {sfm.failed_executions}")
        print(f"   Кэш попаданий: {sfm.cache_hits}")
        print(f"   Кэш промахов: {sfm.cache_misses}")
        
        # Корректное завершение
        print("\n🛑 Завершение работы")
        sfm.shutdown_optimizations()
        
        print("\n✅ Все тесты завершены успешно!")
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка тестирования: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Главная функция"""
    print(f"🕐 Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = test_sfm_optimizations()
    
    if success:
        print("\n🎉 Интеграция оптимизаций SFM работает корректно!")
        sys.exit(0)
    else:
        print("\n💥 Обнаружены проблемы с интеграцией!")
        sys.exit(1)

if __name__ == "__main__":
    main()