#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

print("🔍 ДЕТАЛЬНАЯ ОТЛАДКА SFM ИНТЕГРАЦИИ")
print("=" * 60)

try:
    print("\n1️⃣ Тестирование прямого создания функций:")
    
    from security.bots.incognito_protection_bot import IncognitoProtectionBot
    incognito = IncognitoProtectionBot("test")
    print(f"✅ IncognitoProtectionBot: OK")
    
    from security.family.advanced_parental_controls import AdvancedParentalControls
    parental = AdvancedParentalControls("test")
    print(f"✅ AdvancedParentalControls: OK")
    
    from security.system.network_protection_manager import NetworkProtectionManager
    network = NetworkProtectionManager()
    print(f"✅ NetworkProtectionManager: OK")
    
    print("\n2️⃣ Тестирование создания SFM с отладкой:")
    
    # Патчим метод для отладки
    import security.safe_function_manager as sfm_module
    
    original_method = getattr(sfm_module.SafeFunctionManager, '_init_specialized_functions', None)
    
    def debug_method(self):
        print("🔍 DEBUG: _init_specialized_functions() НАЧАЛСЯ!")
        try:
            # Инициализация IncognitoProtectionBot
            print("🔍 DEBUG: Создаем IncognitoProtectionBot...")
            self.incognito_bot = IncognitoProtectionBot("SafeFunctionIncognito")
            print("✅ IncognitoProtectionBot создан")
            
            # Инициализация AdvancedParentalControls
            print("🔍 DEBUG: Создаем AdvancedParentalControls...")
            self.advanced_parental_controls = AdvancedParentalControls("SafeFunctionParental")
            print("✅ AdvancedParentalControls создан")
            
            # Инициализация NetworkProtectionManager
            print("🔍 DEBUG: Создаем NetworkProtectionManager...")
            self.network_protection_manager = NetworkProtectionManager()
            print("✅ NetworkProtectionManager создан")
            
            print("🔍 DEBUG: _init_specialized_functions() ЗАВЕРШИЛСЯ УСПЕШНО!")
            
        except Exception as e:
            print(f"❌ ОШИБКА в _init_specialized_functions: {e}")
            import traceback
            traceback.print_exc()
    
    # Заменяем метод
    sfm_module.SafeFunctionManager._init_specialized_functions = debug_method
    print("✅ Метод _init_specialized_functions патчен")
    
    print("\n3️⃣ Создаем SFM:")
    from security.safe_function_manager import SafeFunctionManager
    sfm = SafeFunctionManager()
    
    print("\n4️⃣ Проверяем результат:")
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
