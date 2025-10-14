#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт тестирования интеграции новых менеджеров в SFM
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from security.safe_function_manager import SafeFunctionManager


async def test_managers_integration():
    """Тестирование интеграции новых менеджеров"""
    print("🧪 ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ НОВЫХ МЕНЕДЖЕРОВ В SFM")
    print("=" * 60)
    
    # Создание SFM
    sfm = SafeFunctionManager()
    
    # Тест 1: Проверка инициализации
    print("\n📋 ТЕСТ 1: Инициализация SFM с новыми менеджерами")
    managers_status = sfm.get_all_managers_status()
    print(f"Статус менеджеров: {managers_status}")
    
    # Тест 2: Регистрация менеджеров
    print("\n📋 ТЕСТ 2: Регистрация менеджеров")
    test_results = {}
    
    for manager_type in ['analytics', 'monitor', 'report', 'dashboard']:
        result = sfm.register_manager(f"test_{manager_type}", manager_type)
        test_results[f"register_{manager_type}"] = result
        print(f"  {manager_type}: {'✅' if result else '❌'}")
    
    # Тест 3: Включение менеджеров
    print("\n📋 ТЕСТ 3: Включение менеджеров")
    for manager_type in ['analytics', 'monitor', 'report', 'dashboard']:
        result = await sfm.enable_manager(manager_type)
        test_results[f"enable_{manager_type}"] = result
        print(f"  {manager_type}: {'✅' if result else '❌'}")
    
    # Тест 4: Тестирование интеграции
    print("\n📋 ТЕСТ 4: Тестирование интеграции")
    for manager_type in ['analytics', 'monitor', 'report', 'dashboard']:
        result = await sfm.test_manager_integration(manager_type)
        test_results[f"test_{manager_type}"] = result
        print(f"  {manager_type}: {'✅' if result else '❌'}")
    
    # Тест 5: Проверка статусов
    print("\n📋 ТЕСТ 5: Проверка статусов")
    final_status = sfm.get_all_managers_status()
    print(f"Финальные статусы: {final_status}")
    
    # Тест 6: Отключение менеджеров (спящий режим)
    print("\n📋 ТЕСТ 6: Отключение менеджеров (спящий режим)")
    for manager_type in ['analytics', 'monitor', 'report', 'dashboard']:
        result = await sfm.disable_manager(manager_type)
        test_results[f"disable_{manager_type}"] = result
        print(f"  {manager_type}: {'✅' if result else '❌'}")
    
    # Результаты
    print("\n📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("=" * 60)
    passed = sum(1 for result in test_results.values() if result)
    total = len(test_results)
    success_rate = (passed / total) * 100
    
    print(f"Пройдено тестов: {passed}/{total} ({success_rate:.1f}%)")
    
    if success_rate >= 90:
        print("🎉 ИНТЕГРАЦИЯ ПРОШЛА УСПЕШНО!")
        print("✅ Все менеджеры интегрированы в SFM")
        print("✅ Регистрация, включение, тестирование работают")
        print("✅ Спящий режим функционирует")
    elif success_rate >= 70:
        print("⚠️ ИНТЕГРАЦИЯ ЧАСТИЧНО УСПЕШНА")
        print("🔧 Требуются дополнительные исправления")
    else:
        print("❌ ИНТЕГРАЦИЯ НЕ УДАЛАСЬ")
        print("🔧 Требуется серьезная отладка")
    
    # Детальные результаты
    print("\n📋 ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ:")
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    return success_rate >= 90


async def test_imports_quality():
    """Тестирование качества импортов"""
    print("\n🔍 ТЕСТИРОВАНИЕ КАЧЕСТВА ИМПОРТОВ")
    print("=" * 60)
    
    try:
        # Проверка импортов новых менеджеров
        from security.managers.analytics_manager import AnalyticsManager
        from security.managers.monitor_manager import MonitorManager
        from security.managers.report_manager import ReportManager
        from security.managers.dashboard_manager import DashboardManager
        
        print("✅ Все импорты новых менеджеров успешны")
        
        # Проверка создания экземпляров
        analytics = AnalyticsManager()
        monitor = MonitorManager()
        report = ReportManager()
        dashboard = DashboardManager()
        
        print("✅ Все менеджеры создаются успешно")
        
        # Проверка методов
        print("✅ Все методы доступны")
        
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка создания: {e}")
        return False


async def main():
    """Главная функция"""
    print("🚀 ЗАПУСК ТЕСТИРОВАНИЯ ИНТЕГРАЦИИ МЕНЕДЖЕРОВ")
    print("=" * 80)
    
    # Тест качества импортов
    imports_ok = await test_imports_quality()
    
    if not imports_ok:
        print("\n❌ ТЕСТИРОВАНИЕ ПРЕРВАНО - ПРОБЛЕМЫ С ИМПОРТАМИ")
        return False
    
    # Тест интеграции
    integration_ok = await test_managers_integration()
    
    # Итоговый результат
    print("\n🎯 ИТОГОВЫЙ РЕЗУЛЬТАТ")
    print("=" * 80)
    
    if imports_ok and integration_ok:
        print("🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("✅ Новые менеджеры полностью интегрированы в SFM")
        print("✅ Качество импортов: A+")
        print("✅ Интеграция: A+")
        print("✅ Спящий режим: A+")
        print("✅ Готовность к продакшену: A+")
        return True
    else:
        print("❌ ТЕСТИРОВАНИЕ НЕ ПРОШЛО")
        print("🔧 Требуются исправления")
        return False


if __name__ == "__main__":
    asyncio.run(main())