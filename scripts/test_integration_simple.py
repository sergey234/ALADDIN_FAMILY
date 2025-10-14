#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

print("🔍 ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ СПЕЦИАЛИЗИРОВАННЫХ ФУНКЦИЙ")
print("=" * 60)

try:
    from security.bots.incognito_protection_bot import IncognitoProtectionBot
    incognito = IncognitoProtectionBot("test")
    print(f"✅ IncognitoProtectionBot: {type(incognito)}")
except Exception as e:
    print(f"❌ IncognitoProtectionBot: {e}")

try:
    from security.family.advanced_parental_controls import AdvancedParentalControls
    parental = AdvancedParentalControls("test")
    print(f"✅ AdvancedParentalControls: {type(parental)}")
except Exception as e:
    print(f"❌ AdvancedParentalControls: {e}")

try:
    from security.system.network_protection_manager import NetworkProtectionManager
    network = NetworkProtectionManager()
    print(f"✅ NetworkProtectionManager: {type(network)}")
except Exception as e:
    print(f"❌ NetworkProtectionManager: {e}")

print("\n🔍 ТЕСТИРОВАНИЕ SFM ИНТЕГРАЦИИ:")
try:
    from security.safe_function_manager import SafeFunctionManager
    sfm = SafeFunctionManager()
    
    attrs = ['incognito_bot', 'advanced_parental_controls', 'network_protection_manager']
    for attr in attrs:
        if hasattr(sfm, attr):
            value = getattr(sfm, attr)
            print(f"✅ {attr}: {type(value) if value else 'None'}")
        else:
            print(f"❌ {attr}: НЕ НАЙДЕН")
            
except Exception as e:
    print(f"❌ SFM ошибка: {e}")
    import traceback
    traceback.print_exc()
