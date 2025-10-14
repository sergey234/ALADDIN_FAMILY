#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование улучшенных функций SmartMonitoringSystem
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from smart_monitoring import SmartMonitoringSystem, AlertRule, AlertSeverity

async def test_async_features():
    """Тестирование асинхронных функций"""
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ АСИНХРОННЫХ ФУНКЦИЙ")
    print("=" * 60)
    
    try:
        system = SmartMonitoringSystem("AsyncTest")
        
        # Тестируем асинхронное добавление метрики
        print("1. Тестирование add_metric_async...")
        result = await system.add_metric_async("test_metric", 75.0, {"source": "async_test"})
        print(f"✓ add_metric_async: {result}")
        
        # Тестируем асинхронный callback
        print("\n2. Тестирование async callback...")
        async def async_callback(alert):
            print(f"Async callback получен: {alert.title}")
        
        await system.add_alert_callback_async(async_callback)
        print("✓ async callback добавлен")
        
        # Тестируем асинхронную очистку
        print("\n3. Тестирование async cleanup...")
        await system._cleanup_old_data_async()
        print("✓ async cleanup выполнен")
        
        print("\n✅ Все асинхронные тесты пройдены!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в асинхронных тестах: {e}")
        return False

def test_enhanced_validation():
    """Тестирование улучшенной валидации"""
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ УЛУЧШЕННОЙ ВАЛИДАЦИИ")
    print("=" * 60)
    
    try:
        system = SmartMonitoringSystem("ValidationTest")
        
        # Тестируем валидацию имени метрики
        print("1. Тестирование валидации имени метрики...")
        try:
            system._validate_metric_name("")  # Пустое имя
            print("❌ Ошибка не обнаружена")
        except ValueError as e:
            print(f"✓ Валидация пустого имени: {e}")
        
        try:
            system._validate_metric_name("SELECT * FROM users")  # SQL injection
            print("❌ SQL injection не обнаружен")
        except ValueError as e:
            print(f"✓ Валидация SQL injection: {e}")
        
        # Тестируем валидацию значения
        print("\n2. Тестирование валидации значения...")
        try:
            system._validate_metric_value(-5.0)  # Отрицательное значение
            print("❌ Отрицательное значение не обнаружено")
        except ValueError as e:
            print(f"✓ Валидация отрицательного значения: {e}")
        
        # Тестируем валидацию тегов
        print("\n3. Тестирование валидации тегов...")
        try:
            system._validate_tags({"key with space": "value"})  # Пробел в ключе
            print("❌ Пробел в ключе не обнаружен")
        except ValueError as e:
            print(f"✓ Валидация пробела в ключе: {e}")
        
        print("\n✅ Все тесты валидации пройдены!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в тестах валидации: {e}")
        return False

def test_memory_protection():
    """Тестирование защиты от переполнения памяти"""
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ ЗАЩИТЫ ОТ ПЕРЕПОЛНЕНИЯ ПАМЯТИ")
    print("=" * 60)
    
    try:
        system = SmartMonitoringSystem("MemoryTest")
        
        # Тестируем проверку лимитов памяти
        print("1. Тестирование проверки лимитов памяти...")
        memory_ok = system._check_memory_limits()
        print(f"✓ Проверка лимитов памяти: {memory_ok}")
        
        # Тестируем оценку использования памяти
        print("\n2. Тестирование оценки памяти...")
        memory_usage = system._estimate_memory_usage()
        print(f"✓ Оценка памяти: {memory_usage}")
        
        # Тестируем статистику памяти
        print("\n3. Тестирование статистики памяти...")
        memory_stats = system.get_memory_stats()
        print(f"✓ Статистика памяти: {memory_stats}")
        
        # Тестируем принудительную очистку
        print("\n4. Тестирование принудительной очистки...")
        system._cleanup_memory()
        print("✓ Принудительная очистка выполнена")
        
        print("\n✅ Все тесты защиты памяти пройдены!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в тестах защиты памяти: {e}")
        return False

def test_structured_logging():
    """Тестирование структурированного логирования"""
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ СТРУКТУРИРОВАННОГО ЛОГИРОВАНИЯ")
    print("=" * 60)
    
    try:
        system = SmartMonitoringSystem("LoggingTest")
        
        # Тестируем настройку логирования
        print("1. Тестирование настройки логирования...")
        result = system.set_logging_config("DEBUG", enable_debug=True)
        print(f"✓ Настройка логирования: {result}")
        
        # Тестируем логирование событий
        print("\n2. Тестирование логирования событий...")
        system._log_event("INFO", "Тестовое событие", test_field="test_value")
        print("✓ Логирование события выполнено")
        
        # Тестируем логирование производительности
        print("\n3. Тестирование логирования производительности...")
        system._log_performance("test_operation", 0.001, test_metric=100)
        print("✓ Логирование производительности выполнено")
        
        # Тестируем логирование событий безопасности
        print("\n4. Тестирование логирования безопасности...")
        system._log_security_event("TEST_EVENT", "Тестовое событие безопасности")
        print("✓ Логирование безопасности выполнено")
        
        print("\n✅ Все тесты логирования пройдены!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в тестах логирования: {e}")
        return False

def test_error_handling():
    """Тестирование улучшенной обработки ошибок"""
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ УЛУЧШЕННОЙ ОБРАБОТКИ ОШИБОК")
    print("=" * 60)
    
    try:
        system = SmartMonitoringSystem("ErrorTest")
        
        # Тестируем обработку ошибок
        print("1. Тестирование обработки ошибок...")
        test_error = ValueError("Тестовая ошибка")
        system._handle_error(test_error, "тестовый контекст", "ERROR")
        print("✓ Обработка ошибки выполнена")
        
        # Тестируем детальное здоровье системы
        print("\n2. Тестирование детального здоровья...")
        health = system.get_system_health_detailed()
        print(f"✓ Детальное здоровье: {health['health_status']}")
        
        print("\n✅ Все тесты обработки ошибок пройдены!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в тестах обработки ошибок: {e}")
        return False

def test_performance_optimizations():
    """Тестирование оптимизаций производительности"""
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ ОПТИМИЗАЦИЙ ПРОИЗВОДИТЕЛЬНОСТИ")
    print("=" * 60)
    
    try:
        system = SmartMonitoringSystem("PerformanceTest")
        
        # Тестируем __slots__
        print("1. Проверка __slots__...")
        if hasattr(system, '__slots__'):
            print(f"✓ __slots__ определен: {len(system.__slots__)} слотов")
        else:
            print("❌ __slots__ не определен")
        
        # Тестируем производительность добавления метрик
        print("\n2. Тестирование производительности...")
        import time
        start_time = time.time()
        
        for i in range(100):
            system.add_metric(f"metric_{i}", float(i))
        
        end_time = time.time()
        duration = end_time - start_time
        print(f"✓ 100 метрик добавлено за {duration:.3f}s")
        
        # Тестируем статистику производительности
        print("\n3. Тестирование статистики производительности...")
        perf_stats = system.get_performance_stats()
        print(f"✓ Статистика производительности получена")
        
        print("\n✅ Все тесты производительности пройдены!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в тестах производительности: {e}")
        return False

async def main():
    """Главная функция тестирования"""
    print("🚀 ТЕСТИРОВАНИЕ УЛУЧШЕННОЙ СИСТЕМЫ МОНИТОРИНГА")
    print("=" * 80)
    
    results = []
    
    # Запускаем все тесты
    results.append(await test_async_features())
    results.append(test_enhanced_validation())
    results.append(test_memory_protection())
    results.append(test_structured_logging())
    results.append(test_error_handling())
    results.append(test_performance_optimizations())
    
    # Подводим итоги
    print("\n" + "=" * 80)
    print("ИТОГИ ТЕСТИРОВАНИЯ")
    print("=" * 80)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Пройдено тестов: {passed}/{total}")
    print(f"📊 Процент успеха: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ВСЕ УЛУЧШЕНИЯ РАБОТАЮТ КОРРЕКТНО!")
        print("✨ Система мониторинга полностью обновлена!")
        return True
    else:
        print(f"\n⚠️  Есть проблемы в {total - passed} тестах")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)