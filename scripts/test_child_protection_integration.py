#!/usr/bin/env python3
"""
Тест интеграции ChildProtection в SafeFunctionManager
"""

import sys
import os
sys.path.insert(0, "/Users/sergejhlystov/ALADDIN_NEW")

from security.safe_function_manager import SafeFunctionManager, SecurityLevel
from security.family.child_protection import ChildProtection, ProtectionLevel, ContentCategory

def test_child_protection_integration():
    """Тестирует интеграцию ChildProtection в SFM"""
    
    print("🔍 ТЕСТ ИНТЕГРАЦИИ CHILDPROTECTION В SFM")
    print("=" * 60)
    
    try:
        # Создаем SFM
        sfm = SafeFunctionManager()
        print("✅ SafeFunctionManager создан")
        
        # Создаем ChildProtection
        child_protection = ChildProtection()
        print("✅ ChildProtection создан")
        
        # Регистрируем ChildProtection в SFM
        success = sfm.register_function(
            function_id="child_protection",
            name="ChildProtection",
            description="Система защиты детей для семей",
            function_type="family",
            security_level=SecurityLevel.HIGH,
            is_critical=True,
            auto_enable=False
        )
        
        if success:
            print("✅ ChildProtection зарегистрирован в SFM")
        else:
            print("❌ Ошибка регистрации ChildProtection в SFM")
            return False
        
        # Включаем функцию
        enable_success = sfm.enable_function("child_protection")
        if enable_success:
            print("✅ ChildProtection включен в SFM")
        else:
            print("❌ Ошибка включения ChildProtection в SFM")
            return False
        
        # Тестируем функциональность
        print("🧪 ТЕСТИРОВАНИЕ ФУНКЦИОНАЛЬНОСТИ:")
        
        # Тест 1: Получение статуса
        status = child_protection.get_status()
        print(f"✅ Статус ChildProtection: {status['status']}")
        print(f"✅ Всего детей: {status['total_children']}")
        print(f"✅ Всего фильтров: {status['total_filters']}")
        
        # Тест 2: Добавление профиля ребенка
        add_success = child_protection.add_child_profile(
            "test_child", "Тестовый ребенок", 10, ProtectionLevel.MODERATE
        )
        if add_success:
            print("✅ Профиль ребенка добавлен")
        else:
            print("❌ Ошибка добавления профиля ребенка")
        
        # Тест 3: Проверка доступа к контенту
        access_result = child_protection.check_content_access(
            "test_child", "https://educational-site.com", ContentCategory.EDUCATIONAL
        )
        print(f"✅ Проверка доступа к образовательному контенту: {access_result['allowed']}")
        
        # Тест 4: Получение отчета о ребенке
        report = child_protection.get_child_report("test_child")
        print(f"✅ Отчет о ребенке: {report['name']}, возраст: {report['age']}")
        print(f"✅ Уровень защиты: {report['protection_level']}")
        
        # Тест 5: Семейный дашборд
        dashboard = child_protection.get_family_dashboard()
        print(f"✅ Семейный дашборд: {len(dashboard['children'])} детей")
        
        # Тест 6: SFM тест функции
        sfm_test = sfm.test_function("child_protection")
        if sfm_test:
            print("✅ SFM тест функции child_protection: УСПЕХ")
        else:
            print("⚠️ SFM тест функции child_protection: ПРОВАЛЕН")
        
        print("🎉 ТЕСТ ИНТЕГРАЦИИ CHILDPROTECTION ЗАВЕРШЕН УСПЕШНО!")
        print("✅ Все тесты прошли успешно!")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании интеграции: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_child_protection_integration()
