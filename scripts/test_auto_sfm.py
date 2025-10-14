#!/usr/bin/env python3
"""
Тест автоматической инициализации Safe Function Manager (SFM)
Проверяем, что SFM инициализируется автоматически при создании
"""

import sys
import os
sys.path.insert(0, '/Users/sergejhlystov/ALADDIN_NEW')

from security.safe_function_manager import SafeFunctionManager
import time

def test_auto_sfm():
    """Тест автоматической инициализации SFM"""
    print("=" * 80)
    print("🧪 ТЕСТ АВТОМАТИЧЕСКОЙ ИНИЦИАЛИЗАЦИИ SFM")
    print("=" * 80)
    
    try:
        # Создаем SFM - должен инициализироваться автоматически
        print("1. Создание SFM (автоматическая инициализация)...")
        sfm = SafeFunctionManager("AutoSFM")
        
        # Ждем немного для завершения инициализации
        print("2. Ожидание завершения инициализации...")
        time.sleep(2)
        
        # Проверяем статус
        print("3. Проверка статуса SFM...")
        status = sfm.get_status()
        print(f"   Статус: {status.get('status', 'N/A')}")
        
        # Получаем функции
        print("4. Получение функций...")
        all_functions = sfm.get_all_functions_status()
        
        print(f"\n📊 РЕЗУЛЬТАТ АВТОМАТИЧЕСКОЙ ИНИЦИАЛИЗАЦИИ:")
        print(f"   Всего функций: {len(all_functions)}")
        
        if len(all_functions) > 0:
            print("✅ SFM инициализировался автоматически!")
            print("✅ Функции зарегистрированы автоматически!")
        else:
            print("❌ SFM НЕ инициализировался автоматически!")
            print("❌ Функции НЕ зарегистрированы!")
        
        # Показываем функции
        print(f"\n📋 ЗАРЕГИСТРИРОВАННЫЕ ФУНКЦИИ:")
        print("-" * 60)
        
        for i, function in enumerate(all_functions, 1):
            function_id = function.get('function_id', 'N/A')
            name = function.get('name', 'N/A')
            status = function.get('status', 'N/A')
            is_critical = function.get('is_critical', False)
            
            # Статус иконка
            status_icon = "🟢" if status == 'enabled' else "🔴" if status == 'disabled' else "😴"
            critical_icon = "⚠️" if is_critical else "  "
            
            print(f"{i:2d}. {status_icon} {critical_icon} {name} ({function_id})")
        
        # Статистика
        enabled_count = len([f for f in all_functions if f.get('status') == 'enabled'])
        disabled_count = len([f for f in all_functions if f.get('status') == 'disabled'])
        sleeping_count = len([f for f in all_functions if f.get('status') == 'sleeping'])
        
        print(f"\n📊 СТАТИСТИКА:")
        print(f"   🟢 Активные: {enabled_count}")
        print(f"   🔴 Отключенные: {disabled_count}")
        print(f"   😴 В спящем режиме: {sleeping_count}")
        
        print("\n" + "=" * 80)
        if len(all_functions) > 0:
            print("✅ ТЕСТ ПРОЙДЕН - SFM работает автоматически!")
        else:
            print("❌ ТЕСТ НЕ ПРОЙДЕН - SFM НЕ работает автоматически!")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Ошибка теста: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_auto_sfm()