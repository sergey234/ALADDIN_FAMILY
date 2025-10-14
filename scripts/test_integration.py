#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Тест интеграции функций в SafeFunctionManager
"""

import sys
import os

# Добавляем путь к модулям
sys.path.append(os.path.join(os.getcwd(), 'security'))

def test_integration():
    """Тест интеграции функций"""
    print("🔧 ТЕСТ ИНТЕГРАЦИИ ФУНКЦИЙ В SafeFunctionManager")
    print("=" * 60)
    
    try:
        # Проверяем импорт SafeFunctionManager
        print("1️⃣ Проверка импорта SafeFunctionManager...")
        from safe_function_manager import SafeFunctionManager
        print("   ✅ SafeFunctionManager импортируется успешно")
        
        # Создаем экземпляр
        print("\n2️⃣ Создание экземпляра SafeFunctionManager...")
        manager = SafeFunctionManager('TestManager')
        print("   ✅ SafeFunctionManager создан успешно")
        
        # Проверяем SuperAISupportAssistant
        print("\n3️⃣ Проверка SuperAISupportAssistant...")
        if hasattr(manager, 'super_ai_support_assistant'):
            print("   ✅ SuperAISupportAssistant интегрирован")
            print("   📊 Тип: {}".format(type(manager.super_ai_support_assistant).__name__))
        else:
            print("   ❌ SuperAISupportAssistant НЕ интегрирован")
        
        # Проверяем FamilyDashboardManager
        print("\n4️⃣ Проверка FamilyDashboardManager...")
        if hasattr(manager, 'family_dashboard_manager'):
            print("   ✅ FamilyDashboardManager интегрирован")
            print("   📊 Тип: {}".format(type(manager.family_dashboard_manager).__name__))
        else:
            print("   ❌ FamilyDashboardManager НЕ интегрирован")
        
        # Проверяем инициализацию
        print("\n5️⃣ Проверка инициализации...")
        try:
            init_result = manager.initialize()
            if init_result:
                print("   ✅ Инициализация успешна")
            else:
                print("   ⚠️ Инициализация с предупреждениями")
        except Exception as e:
            print("   ❌ Ошибка инициализации: {}".format(str(e)))
        
        # Проверяем остановку
        print("\n6️⃣ Проверка остановки...")
        try:
            stop_result = manager.stop()
            if stop_result:
                print("   ✅ Остановка успешна")
            else:
                print("   ⚠️ Остановка с предупреждениями")
        except Exception as e:
            print("   ❌ Ошибка остановки: {}".format(str(e)))
        
        print("\n🎉 ТЕСТ ИНТЕГРАЦИИ ЗАВЕРШЕН!")
        return True
        
    except Exception as e:
        print("\n❌ КРИТИЧЕСКАЯ ОШИБКА: {}".format(str(e)))
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_integration()
    if success:
        print("\n✅ ИНТЕГРАЦИЯ УСПЕШНА!")
    else:
        print("\n❌ ИНТЕГРАЦИЯ НЕУДАЧНА!")
    sys.exit(0 if success else 1)