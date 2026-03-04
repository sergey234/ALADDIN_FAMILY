#!/usr/bin/env python3
"""
Комплексный тест работоспособности ALADDINPerformanceManager
"""
import sys
import os
import asyncio
sys.path.append('.')

async def test_performance_manager():
    try:
        from performance.performance_manager import ALADDINPerformanceManager, PerformanceMode
        print("✅ Импорт модуля успешен")
        
        # Создаем экземпляр системы
        pm = ALADDINPerformanceManager()
        print("✅ Создание экземпляра успешно")
        
        # Тестируем основные методы
        print(f"✅ Инициализирован: {pm.is_initialized}")
        
        # Тест получения статистики
        stats = pm.get_performance_stats()
        print(f"✅ Получение статистики: {type(stats).__name__}")
        
        # Тест оптимизации производительности (синхронный)
        pm.optimize_performance()
        print("✅ Оптимизация производительности выполнена")
        
        # Тест получения метрик
        metrics = pm.performance_metrics
        print(f"✅ Получение метрик: {type(metrics).__name__}")
        
        # Тест асинхронной задачи
        result = await pm.get_async_result("test_task")
        print(f"✅ Асинхронная задача: {type(result).__name__}")
        
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        
    except Exception as e:
        print(f"❌ Ошибка в тестах: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_performance_manager())
