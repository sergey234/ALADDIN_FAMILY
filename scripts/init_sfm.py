#!/usr/bin/env python3
"""
Скрипт для принудительной инициализации Safe Function Manager (SFM)
Регистрирует все функции и показывает их статус
"""

import sys
import os
sys.path.insert(0, '/Users/sergejhlystov/ALADDIN_NEW')

from security.safe_function_manager import SafeFunctionManager
import time

def initialize_sfm():
    """Принудительная инициализация SFM"""
    print("=" * 80)
    print("🚀 ПРИНУДИТЕЛЬНАЯ ИНИЦИАЛИЗАЦИЯ SAFE FUNCTION MANAGER (SFM)")
    print("=" * 80)
    
    try:
        # Создаем SFM
        print("1. Создание SFM...")
        sfm = SafeFunctionManager("MainSFM")
        
        # Принудительно инициализируем
        print("2. Принудительная инициализация...")
        success = sfm.initialize()
        
        if success:
            print("✅ SFM успешно инициализирован!")
        else:
            print("❌ Ошибка инициализации SFM!")
            return
        
        # Ждем немного для завершения инициализации
        print("3. Ожидание завершения инициализации...")
        time.sleep(2)
        
        # Получаем статистику
        print("4. Получение статистики...")
        all_functions = sfm.get_all_functions_status()
        
        print(f"\n📊 РЕЗУЛЬТАТ ИНИЦИАЛИЗАЦИИ:")
        print(f"   Всего функций: {len(all_functions)}")
        
        # Показываем все функции
        print(f"\n📋 ЗАРЕГИСТРИРОВАННЫЕ ФУНКЦИИ:")
        print("-" * 60)
        
        for i, function in enumerate(all_functions, 1):
            function_id = function.get('function_id', 'N/A')
            name = function.get('name', 'N/A')
            status = function.get('status', 'N/A')
            function_type = function.get('function_type', 'N/A')
            security_level = function.get('security_level', 'N/A')
            is_critical = function.get('is_critical', False)
            
            # Статус иконка
            status_icon = "🟢" if status == 'enabled' else "🔴" if status == 'disabled' else "😴"
            critical_icon = "⚠️" if is_critical else "  "
            
            print(f"{i:2d}. {status_icon} {critical_icon} {name}")
            print(f"     ID: {function_id}")
            print(f"     Тип: {function_type}")
            print(f"     Безопасность: {security_level}")
            print(f"     Статус: {status}")
            print()
        
        # Статистика по статусам
        enabled_count = len([f for f in all_functions if f.get('status') == 'enabled'])
        disabled_count = len([f for f in all_functions if f.get('status') == 'disabled'])
        sleeping_count = len([f for f in all_functions if f.get('status') == 'sleeping'])
        
        print("=" * 80)
        print("📊 СТАТИСТИКА ПО СТАТУСАМ:")
        print("=" * 80)
        print(f"🟢 АКТИВНЫЕ (enabled): {enabled_count}")
        print(f"🔴 ОТКЛЮЧЕННЫЕ (disabled): {disabled_count}")
        print(f"😴 В СПЯЩЕМ РЕЖИМЕ (sleeping): {sleeping_count}")
        
        # Получаем общую статистику SFM
        print(f"\n📈 ОБЩАЯ СТАТИСТИКА SFM:")
        print("-" * 40)
        stats = sfm.get_safe_function_stats()
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        print("\n" + "=" * 80)
        print("✅ ИНИЦИАЛИЗАЦИЯ ЗАВЕРШЕНА")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Ошибка инициализации SFM: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    initialize_sfm()