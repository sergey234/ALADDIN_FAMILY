#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

print("🔍 ПРОВЕРКА МЕТОДОВ SFM")
print("=" * 40)

try:
    from security.safe_function_manager import SafeFunctionManager
    
    print("📋 Проверяем методы класса SafeFunctionManager:")
    methods = [
        '_init_vpn_antivirus',
        '_init_specialized_functions', 
        'load_functions'
    ]
    
    for method_name in methods:
        if hasattr(SafeFunctionManager, method_name):
            print(f"✅ {method_name}: НАЙДЕН")
        else:
            print(f"❌ {method_name}: НЕ НАЙДЕН")
    
    print("\n📋 Все методы класса:")
    all_methods = [name for name in dir(SafeFunctionManager) if name.startswith('_init')]
    for method in all_methods:
        print(f"  - {method}")
    
    print("\n🧪 Пробуем создать экземпляр без патчинга...")
    
    # Создаем экземпляр без патчинга, но с перехватом исключений
    try:
        sfm = SafeFunctionManager()
        print("✅ Экземпляр создан успешно!")
        
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
        print(f"❌ Ошибка создания экземпляра: {e}")
        import traceback
        traceback.print_exc()

except Exception as e:
    print(f"❌ Общая ошибка: {e}")
    import traceback
    traceback.print_exc()
