#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

print("🔍 ТЕСТ КОНСТРУКТОРА SFM")
print("=" * 50)

try:
    # Патчим метод ДО импорта
    import security.safe_function_manager as sfm_module
    
    original_init_specialized = getattr(sfm_module.SafeFunctionManager, '_init_specialized_functions', None)
    
    def debug_init_specialized(self):
        print("🚀 DEBUG: _init_specialized_functions() ВЫЗВАН!")
        try:
            if original_init_specialized:
                original_init_specialized(self)
            else:
                print("❌ ОРИГИНАЛЬНЫЙ МЕТОД НЕ НАЙДЕН!")
        except Exception as e:
            print(f"❌ ОШИБКА В _init_specialized_functions: {e}")
            import traceback
            traceback.print_exc()
    
    # Заменяем метод
    sfm_module.SafeFunctionManager._init_specialized_functions = debug_init_specialized
    print("✅ Метод _init_specialized_functions патчен")
    
    print("\n📦 Создаем SafeFunctionManager...")
    from security.safe_function_manager import SafeFunctionManager
    
    sfm = SafeFunctionManager()
    print("\n✅ SafeFunctionManager создан!")
    
    # Проверяем атрибуты
    attrs = ['incognito_bot', 'advanced_parental_controls', 'network_protection_manager']
    for attr in attrs:
        if hasattr(sfm, attr):
            value = getattr(sfm, attr)
            if value is not None:
                print(f"✅ {attr}: {type(value).__name__}")
            else:
                print(f"⚠️  {attr}: None")
        else:
            print(f"❌ {attr}: НЕ НАЙДЕН")

except Exception as e:
    print(f"❌ Общая ошибка: {e}")
    import traceback
    traceback.print_exc()
