#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка реальной интеграции в SFM
"""

import sys
import os
sys.path.insert(0, '/Users/sergejhlystov/ALADDIN_NEW')

from security.safe_function_manager import SafeFunctionManager

def check_sfm_integration():
    """Проверяем реальную интеграцию в SFM"""
    print("🔍 ПРОВЕРКА ИНТЕГРАЦИИ В SFM:")
    print("================================================")
    
    try:
        # Создаем SFM
        sfm = SafeFunctionManager()
        print("✅ SFM создан успешно")
        
        # Проверяем количество функций
        all_functions = sfm.get_all_functions_status()
        print(f"📊 Всего функций в SFM: {len(all_functions)}")
        
        # Показываем первые 10 функций
        print("\n📋 ПЕРВЫЕ 10 ФУНКЦИЙ В SFM:")
        for i, (func_id, func_info) in enumerate(all_functions.items()):
            if i >= 10:
                break
            print(f"  {i+1}. {func_id}: {func_info.get('name', 'N/A')}")
        
        # Проверяем статус функций
        enabled_count = sum(1 for func_info in all_functions.values() 
                          if func_info.get('status') == 'enabled')
        sleeping_count = sum(1 for func_info in all_functions.values() 
                           if func_info.get('status') == 'sleeping')
        disabled_count = sum(1 for func_info in all_functions.values() 
                           if func_info.get('status') == 'disabled')
        
        print(f"\n📊 СТАТУС ФУНКЦИЙ:")
        print(f"  ✅ Активных: {enabled_count}")
        print(f"  😴 Спящих: {sleeping_count}")
        print(f"  ❌ Отключенных: {disabled_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при проверке SFM: {e}")
        return False

if __name__ == "__main__":
    check_sfm_integration()
