#!/usr/bin/env python3
"""
Скрипт для анализа всех функций в Safe Function Manager (SFM)
Показывает: зарегистрированные функции, их статус, спящий режим, активность
"""

import sys
import os
sys.path.insert(0, '/Users/sergejhlystov/ALADDIN_NEW')

from security.safe_function_manager import SafeFunctionManager

# Локальные определения для совместимости
from enum import Enum

class FunctionStatus(Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"
    SLEEPING = "sleeping"

class SecurityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
import json
from datetime import datetime

def analyze_sfm_functions():
    """Анализ всех функций в SFM"""
    print("=" * 80)
    print("🔍 АНАЛИЗ ВСЕХ ФУНКЦИЙ В SAFE FUNCTION MANAGER (SFM)")
    print("=" * 80)
    
    try:
        # Инициализируем SFM
        sfm = SafeFunctionManager("MainSFM")
        
        # Получаем все функции
        all_functions = sfm.get_all_functions_status()
        
        print(f"\n📊 ОБЩАЯ СТАТИСТИКА:")
        print(f"   Всего функций: {len(all_functions)}")
        
        # Анализируем по статусам
        enabled_count = 0
        disabled_count = 0
        sleeping_count = 0
        
        # Анализируем по типам
        function_types = {}
        security_levels = {}
        
        print(f"\n📋 ДЕТАЛЬНЫЙ СПИСОК ФУНКЦИЙ:")
        print("-" * 80)
        
        for i, function in enumerate(all_functions, 1):
            function_id = function.get('function_id', 'N/A')
            name = function.get('name', 'N/A')
            status = function.get('status', 'N/A')
            function_type = function.get('function_type', 'N/A')
            security_level = function.get('security_level', 'N/A')
            is_critical = function.get('is_critical', False)
            last_activity = function.get('last_activity', 'N/A')
            
            # Подсчет статусов
            if status == 'enabled':
                enabled_count += 1
            elif status == 'disabled':
                disabled_count += 1
            elif status == 'sleeping':
                sleeping_count += 1
            
            # Подсчет типов
            if function_type not in function_types:
                function_types[function_type] = 0
            function_types[function_type] += 1
            
            # Подсчет уровней безопасности
            if security_level not in security_levels:
                security_levels[security_level] = 0
            security_levels[security_level] += 1
            
            # Статус иконка
            status_icon = "🟢" if status == 'enabled' else "🔴" if status == 'disabled' else "😴"
            critical_icon = "⚠️" if is_critical else "  "
            
            print(f"{i:2d}. {status_icon} {critical_icon} {name}")
            print(f"     ID: {function_id}")
            print(f"     Тип: {function_type}")
            print(f"     Безопасность: {security_level}")
            print(f"     Статус: {status}")
            print(f"     Последняя активность: {last_activity}")
            print()
        
        # Статистика по статусам
        print("=" * 80)
        print("📊 СТАТИСТИКА ПО СТАТУСАМ:")
        print("=" * 80)
        print(f"🟢 АКТИВНЫЕ (enabled): {enabled_count}")
        print(f"🔴 ОТКЛЮЧЕННЫЕ (disabled): {disabled_count}")
        print(f"😴 В СПЯЩЕМ РЕЖИМЕ (sleeping): {sleeping_count}")
        
        # Статистика по типам
        print(f"\n📊 СТАТИСТИКА ПО ТИПАМ ФУНКЦИЙ:")
        print("-" * 40)
        for func_type, count in sorted(function_types.items()):
            print(f"   {func_type}: {count}")
        
        # Статистика по уровням безопасности
        print(f"\n📊 СТАТИСТИКА ПО УРОВНЯМ БЕЗОПАСНОСТИ:")
        print("-" * 40)
        for level, count in sorted(security_levels.items()):
            print(f"   {level}: {count}")
        
        # Получаем спящие функции
        print(f"\n😴 ФУНКЦИИ В СПЯЩЕМ РЕЖИМЕ:")
        print("-" * 40)
        sleeping_functions = [f for f in all_functions if f.get('status') == 'sleeping']
        if sleeping_functions:
            for i, function in enumerate(sleeping_functions, 1):
                print(f"{i}. {function.get('name', 'N/A')} ({function.get('function_id', 'N/A')})")
        else:
            print("   Нет функций в спящем режиме")
        
        # Получаем активные функции
        print(f"\n🟢 АКТИВНЫЕ ФУНКЦИИ:")
        print("-" * 40)
        active_functions = [f for f in all_functions if f.get('status') == 'enabled']
        if active_functions:
            for i, function in enumerate(active_functions, 1):
                print(f"{i}. {function.get('name', 'N/A')} ({function.get('function_id', 'N/A')})")
        else:
            print("   Нет активных функций")
        
        # Получаем отключенные функции
        print(f"\n🔴 ОТКЛЮЧЕННЫЕ ФУНКЦИИ:")
        print("-" * 40)
        disabled_functions = [f for f in all_functions if f.get('status') == 'disabled']
        if disabled_functions:
            for i, function in enumerate(disabled_functions, 1):
                print(f"{i}. {function.get('name', 'N/A')} ({function.get('function_id', 'N/A')})")
        else:
            print("   Нет отключенных функций")
        
        # Получаем критические функции
        print(f"\n⚠️ КРИТИЧЕСКИЕ ФУНКЦИИ:")
        print("-" * 40)
        critical_functions = [f for f in all_functions if f.get('is_critical', False)]
        if critical_functions:
            for i, function in enumerate(critical_functions, 1):
                status = function.get('status', 'N/A')
                status_icon = "🟢" if status == 'enabled' else "🔴" if status == 'disabled' else "😴"
                print(f"{i}. {status_icon} {function.get('name', 'N/A')} ({function.get('function_id', 'N/A')})")
        else:
            print("   Нет критических функций")
        
        # Получаем общую статистику SFM
        print(f"\n📈 ОБЩАЯ СТАТИСТИКА SFM:")
        print("-" * 40)
        stats = sfm.get_safe_function_stats()
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        print("\n" + "=" * 80)
        print("✅ АНАЛИЗ ЗАВЕРШЕН")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Ошибка анализа SFM: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_sfm_functions()