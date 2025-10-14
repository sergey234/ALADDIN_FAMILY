#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка интеграции системы алертов с SafeFunctionManager
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.safe_function_manager import SafeFunctionManager

def check_integration():
    """Проверка интеграции"""
    print("🔍 Проверка интеграции AdvancedAlertingSystem...")
    
    try:
        # Получаем SafeFunctionManager
        safe_manager = SafeFunctionManager()
        
        # Проверяем статус функции
        function_status = safe_manager.get_function_status("advanced_alerting_system")
        
        if function_status:
            print("✅ Функция найдена в SafeFunctionManager")
            print(f"📊 Статус: {function_status.get('status', 'unknown')}")
            print(f"🔒 Уровень безопасности: {function_status.get('security_level', 'unknown')}")
            print(f"📝 Описание: {function_status.get('description', 'unknown')}")
            print(f"🏷️ Тип: {function_status.get('function_type', 'unknown')}")
            print(f"📅 Создана: {function_status.get('created_at', 'unknown')}")
            print(f"🔄 Выполнений: {function_status.get('execution_count', 0)}")
            print(f"✅ Успешных: {function_status.get('success_count', 0)}")
            
            # Получаем общую статистику
            stats = safe_manager.get_safe_function_stats()
            print(f"\n📈 Общая статистика SafeFunctionManager:")
            print(f"  - Всего функций: {stats.get('total_functions', 0)}")
            print(f"  - Включенных: {stats.get('enabled_functions', 0)}")
            print(f"  - Отключенных: {stats.get('disabled_functions', 0)}")
            print(f"  - Критических: {stats.get('critical_functions', 0)}")
            
            # Получаем функции по типу security
            security_functions = safe_manager.get_functions_by_type("security")
            print(f"\n🔒 Функции безопасности: {len(security_functions)}")
            for func in security_functions:
                print(f"  - {func.get('name', 'unknown')} ({func.get('status', 'unknown')})")
            
            return True
        else:
            print("❌ Функция не найдена в SafeFunctionManager")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка проверки: {e}")
        return False

if __name__ == '__main__':
    success = check_integration()
    if success:
        print("\n🎉 Интеграция подтверждена!")
    else:
        print("\n💥 Интеграция не найдена!")
        sys.exit(1)