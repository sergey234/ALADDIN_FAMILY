#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Отладка SafeFunctionManager
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.safe_function_manager import SafeFunctionManager

def debug_safe_manager():
    """Отладка SafeFunctionManager"""
    print("🔍 Отладка SafeFunctionManager...")
    
    try:
        # Создаем новый экземпляр
        safe_manager = SafeFunctionManager()
        print("✅ SafeFunctionManager создан")
        
        # Получаем общую статистику
        stats = safe_manager.get_safe_function_stats()
        print(f"📊 Статистика: {stats}")
        
        # Получаем все функции
        all_functions = safe_manager.get_all_functions_status()
        print(f"📋 Всего функций: {len(all_functions)}")
        
        for func in all_functions:
            print(f"  - {func.get('function_id', 'unknown')}: {func.get('status', 'unknown')}")
        
        # Проверяем конкретную функцию
        function_status = safe_manager.get_function_status("advanced_alerting_system")
        print(f"🔍 Статус advanced_alerting_system: {function_status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    debug_safe_manager()