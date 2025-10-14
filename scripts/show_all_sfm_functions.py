#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для отображения всех функций в SafeFunctionManager
Показывает активные, спящие и отключенные функции
"""

import sys
import os
from datetime import datetime

# Добавляем путь к модулям
sys.path.append('/Users/sergejhlystov/ALADDIN_NEW')

try:
    from security.safe_function_manager import SafeFunctionManager, FunctionStatus
    from core.base import SecurityLevel
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    sys.exit(1)

def show_all_functions():
    """Показать все функции в SafeFunctionManager"""
    print("🔍 ПОЛНЫЙ СПИСОК ФУНКЦИЙ В SAFEFUNCTIONMANAGER")
    print("=" * 60)
    
    try:
        # Создаем экземпляр SafeFunctionManager
        sfm = SafeFunctionManager("MainSafeFunctionManager")
        
        # Инициализируем менеджер
        if not sfm.initialize():
            print("❌ Ошибка инициализации SafeFunctionManager")
            return
        
        # Получаем все функции
        all_functions = sfm.get_all_functions_status()
        
        if not all_functions:
            print("📭 Функции не найдены в SafeFunctionManager")
            return
        
        # Группируем функции по статусу
        enabled_functions = []
        sleeping_functions = []
        disabled_functions = []
        testing_functions = []
        error_functions = []
        maintenance_functions = []
        
        for func in all_functions:
            status = func.get('status', 'unknown')
            if status == 'enabled':
                enabled_functions.append(func)
            elif status == 'sleeping':
                sleeping_functions.append(func)
            elif status == 'disabled':
                disabled_functions.append(func)
            elif status == 'testing':
                testing_functions.append(func)
            elif status == 'error':
                error_functions.append(func)
            elif status == 'maintenance':
                maintenance_functions.append(func)
        
        # Общая статистика
        print(f"📊 ОБЩАЯ СТАТИСТИКА:")
        print(f"   Всего функций: {len(all_functions)}")
        print(f"   ✅ Активных: {len(enabled_functions)}")
        print(f"   😴 Спящих: {len(sleeping_functions)}")
        print(f"   ❌ Отключенных: {len(disabled_functions)}")
        print(f"   🧪 Тестируемых: {len(testing_functions)}")
        print(f"   ⚠️  С ошибками: {len(error_functions)}")
        print(f"   🔧 На обслуживании: {len(maintenance_functions)}")
        print()
        
        # Активные функции
        if enabled_functions:
            print("✅ АКТИВНЫЕ ФУНКЦИИ:")
            print("-" * 40)
            for func in enabled_functions:
                critical = "🔴 КРИТИЧЕСКАЯ" if func.get('is_critical', False) else "🟢 Обычная"
                security_level = func.get('security_level', 'unknown')
                func_type = func.get('function_type', 'unknown')
                print(f"   • {func.get('name', 'Unknown')} ({func.get('function_id', 'unknown')})")
                print(f"     {critical} | Безопасность: {security_level} | Тип: {func_type}")
                print(f"     Описание: {func.get('description', 'Нет описания')}")
                if func.get('execution_count', 0) > 0:
                    print(f"     Выполнений: {func.get('execution_count', 0)} | Успешных: {func.get('success_count', 0)}")
                print()
        
        # Спящие функции
        if sleeping_functions:
            print("😴 СПЯЩИЕ ФУНКЦИИ:")
            print("-" * 40)
            for func in sleeping_functions:
                critical = "🔴 КРИТИЧЕСКАЯ" if func.get('is_critical', False) else "🟢 Обычная"
                security_level = func.get('security_level', 'unknown')
                func_type = func.get('function_type', 'unknown')
                auto_sleep = "🤖 Авто-сон" if func.get('auto_sleep', False) else "👤 Ручной сон"
                sleep_hours = func.get('sleep_after_hours', 24)
                print(f"   • {func.get('name', 'Unknown')} ({func.get('function_id', 'unknown')})")
                print(f"     {critical} | Безопасность: {security_level} | Тип: {func_type}")
                print(f"     {auto_sleep} | Сон через: {sleep_hours}ч")
                print(f"     Описание: {func.get('description', 'Нет описания')}")
                if func.get('last_activity'):
                    print(f"     Последняя активность: {func.get('last_activity')}")
                print()
        
        # Отключенные функции
        if disabled_functions:
            print("❌ ОТКЛЮЧЕННЫЕ ФУНКЦИИ:")
            print("-" * 40)
            for func in disabled_functions:
                critical = "🔴 КРИТИЧЕСКАЯ" if func.get('is_critical', False) else "🟢 Обычная"
                security_level = func.get('security_level', 'unknown')
                func_type = func.get('function_type', 'unknown')
                print(f"   • {func.get('name', 'Unknown')} ({func.get('function_id', 'unknown')})")
                print(f"     {critical} | Безопасность: {security_level} | Тип: {func_type}")
                print(f"     Описание: {func.get('description', 'Нет описания')}")
                print()
        
        # Функции с ошибками
        if error_functions:
            print("⚠️  ФУНКЦИИ С ОШИБКАМИ:")
            print("-" * 40)
            for func in error_functions:
                critical = "🔴 КРИТИЧЕСКАЯ" if func.get('is_critical', False) else "🟢 Обычная"
                security_level = func.get('security_level', 'unknown')
                func_type = func.get('function_type', 'unknown')
                error_count = func.get('error_count', 0)
                print(f"   • {func.get('name', 'Unknown')} ({func.get('function_id', 'unknown')})")
                print(f"     {critical} | Безопасность: {security_level} | Тип: {func_type}")
                print(f"     Ошибок: {error_count}")
                print(f"     Описание: {func.get('description', 'Нет описания')}")
                print()
        
        # Функции на обслуживании
        if maintenance_functions:
            print("🔧 ФУНКЦИИ НА ОБСЛУЖИВАНИИ:")
            print("-" * 40)
            for func in maintenance_functions:
                critical = "🔴 КРИТИЧЕСКАЯ" if func.get('is_critical', False) else "🟢 Обычная"
                security_level = func.get('security_level', 'unknown')
                func_type = func.get('function_type', 'unknown')
                print(f"   • {func.get('name', 'Unknown')} ({func.get('function_id', 'unknown')})")
                print(f"     {critical} | Безопасность: {security_level} | Тип: {func_type}")
                print(f"     Описание: {func.get('description', 'Нет описания')}")
                print()
        
        # Тестируемые функции
        if testing_functions:
            print("🧪 ТЕСТИРУЕМЫЕ ФУНКЦИИ:")
            print("-" * 40)
            for func in testing_functions:
                critical = "🔴 КРИТИЧЕСКАЯ" if func.get('is_critical', False) else "🟢 Обычная"
                security_level = func.get('security_level', 'unknown')
                func_type = func.get('function_type', 'unknown')
                print(f"   • {func.get('name', 'Unknown')} ({func.get('function_id', 'unknown')})")
                print(f"     {critical} | Безопасность: {security_level} | Тип: {func_type}")
                print(f"     Описание: {func.get('description', 'Нет описания')}")
                print()
        
        # Статистика по типам функций
        print("📈 СТАТИСТИКА ПО ТИПАМ ФУНКЦИЙ:")
        print("-" * 40)
        function_types = {}
        for func in all_functions:
            func_type = func.get('function_type', 'unknown')
            if func_type not in function_types:
                function_types[func_type] = {'total': 0, 'enabled': 0, 'sleeping': 0, 'disabled': 0, 'error': 0}
            
            function_types[func_type]['total'] += 1
            status = func.get('status', 'unknown')
            if status in function_types[func_type]:
                function_types[func_type][status] += 1
        
        for func_type, stats in function_types.items():
            print(f"   📦 {func_type.upper()}:")
            print(f"      Всего: {stats['total']} | Активных: {stats['enabled']} | Спящих: {stats['sleeping']} | Отключенных: {stats['disabled']}")
            if stats['error'] > 0:
                print(f"      ⚠️  С ошибками: {stats['error']}")
            print()
        
        # Статистика по уровням безопасности
        print("🛡️  СТАТИСТИКА ПО УРОВНЯМ БЕЗОПАСНОСТИ:")
        print("-" * 40)
        security_levels = {}
        for func in all_functions:
            level = func.get('security_level', 'unknown')
            if level not in security_levels:
                security_levels[level] = {'total': 0, 'enabled': 0, 'sleeping': 0, 'disabled': 0}
            
            security_levels[level]['total'] += 1
            status = func.get('status', 'unknown')
            if status in security_levels[level]:
                security_levels[level][status] += 1
        
        for level, stats in security_levels.items():
            level_name = {
                'high': '🔴 ВЫСОКИЙ',
                'medium': '🟡 СРЕДНИЙ', 
                'low': '🟢 НИЗКИЙ'
            }.get(level, f'❓ {level.upper()}')
            
            print(f"   {level_name}:")
            print(f"      Всего: {stats['total']} | Активных: {stats['enabled']} | Спящих: {stats['sleeping']} | Отключенных: {stats['disabled']}")
            print()
        
        # Общая статистика SFM
        print("📊 ОБЩАЯ СТАТИСТИКА SFM:")
        print("-" * 40)
        sfm_stats = sfm.get_safe_function_stats()
        print(f"   Всего выполнений: {sfm_stats.get('total_executions', 0)}")
        print(f"   Успешных выполнений: {sfm_stats.get('successful_executions', 0)}")
        print(f"   Неудачных выполнений: {sfm_stats.get('failed_executions', 0)}")
        print(f"   Активных выполнений: {sfm_stats.get('active_executions', 0)}")
        success_rate = sfm_stats.get('execution_success_rate', 0)
        print(f"   Процент успеха: {success_rate:.1f}%")
        print()
        
        # Статистика спящего режима
        print("😴 СТАТИСТИКА СПЯЩЕГО РЕЖИМА:")
        print("-" * 40)
        sleep_stats = sfm.get_sleep_statistics()
        print(f"   Переходов в сон: {sleep_stats.get('sleep_transitions', 0)}")
        print(f"   Пробуждений: {sleep_stats.get('wake_transitions', 0)}")
        print(f"   Автоматических снов: {sleep_stats.get('auto_sleep_count', 0)}")
        print(f"   Ручных снов: {sleep_stats.get('manual_sleep_count', 0)}")
        print(f"   Ручных пробуждений: {sleep_stats.get('manual_wake_count', 0)}")
        print(f"   Управление сном активно: {'Да' if sleep_stats.get('sleep_management_active', False) else 'Нет'}")
        print(f"   Интервал проверки: {sleep_stats.get('sleep_check_interval', 0)}с")
        print(f"   Время до сна по умолчанию: {sleep_stats.get('default_sleep_hours', 0)}ч")
        print()
        
        print("✅ Анализ завершен успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка при получении функций: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    show_all_functions()