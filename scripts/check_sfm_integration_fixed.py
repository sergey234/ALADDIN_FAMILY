#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка реальной интеграции в SFM (исправленная версия)
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
        
        # Показываем все функции
        print("\n📋 ВСЕ ФУНКЦИИ В SFM:")
        for i, func_info in enumerate(all_functions):
            print(f"  {i+1}. {func_info}")
        
        # Проверяем статус функций
        enabled_count = sum(1 for func_info in all_functions 
                          if hasattr(func_info, 'status') and func_info.status == 'enabled')
        sleeping_count = sum(1 for func_info in all_functions 
                           if hasattr(func_info, 'status') and func_info.status == 'sleeping')
        disabled_count = sum(1 for func_info in all_functions 
                           if hasattr(func_info, 'status') and func_info.status == 'disabled')
        
        print(f"\n📊 СТАТУС ФУНКЦИЙ:")
        print(f"  ✅ Активных: {enabled_count}")
        print(f"  😴 Спящих: {sleeping_count}")
        print(f"  ❌ Отключенных: {disabled_count}")
        
        # Проверяем методы SFM
        print(f"\n🔧 ДОСТУПНЫЕ МЕТОДЫ SFM:")
        methods = [method for method in dir(sfm) if not method.startswith('_')]
        for method in methods[:10]:  # Показываем первые 10
            print(f"  - {method}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при проверке SFM: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    check_sfm_integration()
