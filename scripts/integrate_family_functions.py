#!/usr/bin/env python3
"""
Интеграция семейных функций с SafeFunctionManager
Регистрирует FamilyProfileManager, ChildProtection, ElderlyProtection
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.safe_function_manager import SafeFunctionManager
from core.base import SecurityLevel
from security.family.family_profile_manager import FamilyProfileManager
from security.family.child_protection import ChildProtection
from security.family.elderly_protection import ElderlyProtection


def integrate_family_functions():
    """Интеграция семейных функций с SafeFunctionManager"""
    
    print("🚀 Начинаем интеграцию семейных функций...")
    
    # Создаем менеджер
    manager = SafeFunctionManager("FamilySecurityManager")
    
    print("✅ SafeFunctionManager создан")
    
    # Регистрируем FamilyProfileManager
    print("📝 Регистрируем FamilyProfileManager...")
    success1 = manager.register_function(
        function_id="family_profile_manager",
        name="FamilyProfileManager",
        description="Управление семейными профилями, членами семьи и ролями",
        function_type="family",
        security_level=SecurityLevel.HIGH,
        is_critical=True,
        auto_enable=True
    )
    print(f"   Результат: {'✅ Успешно' if success1 else '❌ Ошибка'}")
    
    # Регистрируем ChildProtection
    print("📝 Регистрируем ChildProtection...")
    success2 = manager.register_function(
        function_id="child_protection",
        name="ChildProtection", 
        description="Защита детей с родительским контролем и фильтрацией контента",
        function_type="family",
        security_level=SecurityLevel.HIGH,
        is_critical=True,
        auto_enable=True
    )
    print(f"   Результат: {'✅ Успешно' if success2 else '❌ Ошибка'}")
    
    # Регистрируем ElderlyProtection
    print("📝 Регистрируем ElderlyProtection...")
    success3 = manager.register_function(
        function_id="elderly_protection",
        name="ElderlyProtection",
        description="Специальная защита пожилых от социальной инженерии и мошенничества",
        function_type="family", 
        security_level=SecurityLevel.HIGH,
        is_critical=True,
        auto_enable=True
    )
    print(f"   Результат: {'✅ Успешно' if success3 else '❌ Ошибка'}")
    
    # Настраиваем зависимости
    print("🔗 Настраиваем зависимости...")
    try:
        # ChildProtection зависит от FamilyProfileManager
        manager.set_function_dependency("child_protection", "family_profile_manager")
        print("   ✅ ChildProtection → FamilyProfileManager")
        
        # ElderlyProtection зависит от FamilyProfileManager  
        manager.set_function_dependency("elderly_protection", "family_profile_manager")
        print("   ✅ ElderlyProtection → FamilyProfileManager")
        
    except Exception as e:
        print(f"   ⚠️ Ошибка настройки зависимостей: {e}")
    
    # Получаем статус
    print("📊 Получаем статус системы...")
    try:
        status = manager.get_status()
        print(f"   Статус: {status.get('status', 'unknown')}")
        print(f"   Всего функций: {status.get('total_functions', 0)}")
        print(f"   Включено: {status.get('functions_enabled', 0)}")
        print(f"   Отключено: {status.get('functions_disabled', 0)}")
        
        # Статистика по типам
        types_stats = status.get('functions_by_type', {})
        if types_stats:
            print("   По типам:")
            for func_type, count in types_stats.items():
                print(f"     {func_type}: {count}")
                
    except Exception as e:
        print(f"   ⚠️ Ошибка получения статуса: {e}")
    
    # Тестируем функции
    print("🧪 Тестируем семейные функции...")
    try:
        # Создаем экземпляры для тестирования
        family_manager = FamilyProfileManager()
        child_protection = ChildProtection(family_manager)
        elderly_protection = ElderlyProtection()
        
        print("   ✅ FamilyProfileManager создан")
        print("   ✅ ChildProtection создан") 
        print("   ✅ ElderlyProtection создан")
        
        # Тестируем базовую функциональность
        family_status = family_manager.get_status()
        child_status = child_protection.get_status()
        elderly_status = elderly_protection.get_status()
        
        print(f"   FamilyProfileManager статус: {family_status.get('status', 'unknown')}")
        print(f"   ChildProtection статус: {child_status.get('status', 'unknown')}")
        print(f"   ElderlyProtection статус: {elderly_status.get('status', 'unknown')}")
        
    except Exception as e:
        print(f"   ❌ Ошибка тестирования: {e}")
    
    print("\n🎉 Интеграция завершена!")
    return success1 and success2 and success3


if __name__ == "__main__":
    success = integrate_family_functions()
    sys.exit(0 if success else 1)
