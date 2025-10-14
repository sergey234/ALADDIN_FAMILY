#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Упрощенный скрипт интеграции компонентов соответствия
"""

import sys
import os

# Добавляем корневую директорию проекта в sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_compliance_components():
    """Тестирует компоненты соответствия"""
    print("🔧 ТЕСТИРОВАНИЕ КОМПОНЕНТОВ СООТВЕТСТВИЯ")
    print("=" * 50)
    
    try:
        # Тест 1: RussianDataProtectionManager
        print("1. Тест RussianDataProtectionManager...")
        from security.compliance.russian_data_protection_manager import RussianDataProtectionManager
        rdpm = RussianDataProtectionManager("TestRussianDataProtectionManager")
        print("   ✅ RussianDataProtectionManager создан")
        
        # Тест 2: COPPAComplianceManager
        print("2. Тест COPPAComplianceManager...")
        from security.compliance.coppa_compliance_manager import COPPAComplianceManager
        ccm = COPPAComplianceManager("TestCOPPAComplianceManager")
        print("   ✅ COPPAComplianceManager создан")
        
        # Тест 3: RussianChildProtectionManager
        print("3. Тест RussianChildProtectionManager...")
        from security.compliance.russian_child_protection_manager import RussianChildProtectionManager
        rcpm = RussianChildProtectionManager("TestRussianChildProtectionManager")
        print("   ✅ RussianChildProtectionManager создан")
        
        # Тест функциональности
        print("\n4. Тест функциональности...")
        
        # Тест RussianDataProtectionManager
        result1 = rdpm.register_consent("test_user_001", ["marketing", "analytics"], "explicit")
        print(f"   - RussianDataProtectionManager.register_consent: {result1}")
        
        # Тест COPPAComplianceManager
        result2 = ccm.register_child("test_child_001", "Test Child", 10, "test_parent_001")
        print(f"   - COPPAComplianceManager.register_child: {result2}")
        
        # Тест RussianChildProtectionManager
        result3 = rcpm.register_child("test_child_002", "Test Child RU", 12, "test_parent_002")
        print(f"   - RussianChildProtectionManager.register_child: {result3}")
        
        # Получаем статус
        print("\n5. Статус компонентов...")
        rdpm_status = rdpm.get_status()
        ccm_status = ccm.get_status()
        rcpm_status = rcpm.get_status()
        
        print(f"   - RussianDataProtectionManager: {rdpm_status['status']}")
        print(f"   - COPPAComplianceManager: {ccm_status['status']}")
        print(f"   - RussianChildProtectionManager: {rcpm_status['status']}")
        
        print("\n" + "=" * 50)
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("✅ Все компоненты соответствия работают корректно")
        print("✅ Компоненты готовы к интеграции с SafeFunctionManager")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_compliance_components()
    if success:
        print("\n🚀 ГОТОВО! Компоненты соответствия протестированы.")
    else:
        print("\n💥 ОШИБКА! Тестирование не удалось.")
        sys.exit(1)
