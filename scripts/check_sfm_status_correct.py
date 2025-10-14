#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Правильная проверка статусов SFM
"""

import sys
import os
sys.path.insert(0, '/Users/sergejhlystov/ALADDIN_NEW')

from security.safe_function_manager import SafeFunctionManager

def check_sfm_status_correct():
    """Правильная проверка статусов SFM"""
    print("🔍 ПРАВИЛЬНАЯ ПРОВЕРКА СТАТУСОВ SFM:")
    print("================================================")
    
    try:
        # Создаем SFM
        sfm = SafeFunctionManager()
        print("✅ SFM создан успешно")
        
        # Получаем все функции
        all_functions = sfm.get_all_functions_status()
        print(f"📊 Всего функций в SFM: {len(all_functions)}")
        
        # ПРАВИЛЬНЫЙ подсчет статусов
        enabled_count = sum(1 for func_info in all_functions 
                          if func_info.get('status') == 'enabled')
        sleeping_count = sum(1 for func_info in all_functions 
                           if func_info.get('status') == 'sleeping')
        disabled_count = sum(1 for func_info in all_functions 
                           if func_info.get('status') == 'disabled')
        testing_count = sum(1 for func_info in all_functions 
                          if func_info.get('status') == 'testing')
        error_count = sum(1 for func_info in all_functions 
                        if func_info.get('status') == 'error')
        maintenance_count = sum(1 for func_info in all_functions 
                              if func_info.get('status') == 'maintenance')
        
        print(f"\n📊 ПРАВИЛЬНЫЕ СТАТУСЫ ФУНКЦИЙ:")
        print(f"  ✅ Активных (enabled): {enabled_count}")
        print(f"  😴 Спящих (sleeping): {sleeping_count}")
        print(f"  ❌ Отключенных (disabled): {disabled_count}")
        print(f"  🧪 Тестируемых (testing): {testing_count}")
        print(f"  💥 Ошибок (error): {error_count}")
        print(f"  🔧 Обслуживание (maintenance): {maintenance_count}")
        
        # Показываем детали каждой функции
        print(f"\n📋 ДЕТАЛИ ФУНКЦИЙ:")
        for i, func_info in enumerate(all_functions):
            print(f"  {i+1}. {func_info.get('name', 'N/A')} - {func_info.get('status', 'N/A')}")
        
        # Проверяем критические функции
        critical_functions = sfm.get_critical_functions()
        print(f"\n🚨 КРИТИЧЕСКИЕ ФУНКЦИИ: {len(critical_functions)}")
        for func in critical_functions:
            print(f"  - {func.get('name', 'N/A')} ({func.get('status', 'N/A')})")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при проверке SFM: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    check_sfm_status_correct()
