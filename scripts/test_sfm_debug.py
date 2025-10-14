#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

print("🔍 ОТЛАДКА SFM ИНИЦИАЛИЗАЦИИ")
print("=" * 60)

# Патчим метод для отладки
import security.safe_function_manager as sfm_module

original_init_specialized = getattr(sfm_module.SafeFunctionManager, '_init_specialized_functions', None)

def debug_init_specialized(self):
    print("🔍 DEBUG: _init_specialized_functions() ВЫЗВАН!")
    try:
        if original_init_specialized:
            return original_init_specialized(self)
        else:
            print("❌ Оригинальный метод не найден!")
    except Exception as e:
        print(f"❌ Ошибка в _init_specialized_functions: {e}")
        import traceback
        traceback.print_exc()

# Патчим метод
if hasattr(sfm_module.SafeFunctionManager, '_init_specialized_functions'):
    sfm_module.SafeFunctionManager._init_specialized_functions = debug_init_specialized
    print("✅ Метод _init_specialized_functions патчен для отладки")
else:
    print("❌ Метод _init_specialized_functions НЕ НАЙДЕН!")

try:
    from security.safe_function_manager import SafeFunctionManager
    print("🔍 Создаем SFM...")
    sfm = SafeFunctionManager()
    print("✅ SFM создан")
    
    # Проверяем атрибуты
    attrs = ['incognito_bot', 'advanced_parental_controls', 'network_protection_manager']
    for attr in attrs:
        if hasattr(sfm, attr):
            value = getattr(sfm, attr)
            print(f"✅ {attr}: {type(value) if value else 'None'}")
        else:
            print(f"❌ {attr}: НЕ НАЙДЕН")
            
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
