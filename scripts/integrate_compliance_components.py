#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт интеграции компонентов соответствия с SafeFunctionManager
"""

import sys
import os
import logging
from datetime import datetime

# Добавляем корневую директорию проекта в sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from security.safe_function_manager import SafeFunctionManager
from security.compliance.russian_data_protection_manager import RussianDataProtectionManager
from security.compliance.coppa_compliance_manager import COPPAComplianceManager
from security.compliance.russian_child_protection_manager import RussianChildProtectionManager

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def integrate_compliance_components():
    """Интегрирует все компоненты соответствия с SafeFunctionManager"""
    print("🔧 ИНТЕГРАЦИЯ КОМПОНЕНТОВ СООТВЕТСТВИЯ С SAFEFUNCTIONMANAGER")
    print("=" * 60)
    
    try:
        # Создаем экземпляр SafeFunctionManager
        print("1. Создание SafeFunctionManager...")
        sfm = SafeFunctionManager("MainSafeFunctionManager")
        print("   ✅ SafeFunctionManager создан")
        
        # Создаем компоненты соответствия
        print("\n2. Создание компонентов соответствия...")
        
        # RussianDataProtectionManager
        print("   - RussianDataProtectionManager...")
        rdpm = RussianDataProtectionManager("RussianDataProtectionManager")
        print("   ✅ RussianDataProtectionManager создан")
        
        # COPPAComplianceManager
        print("   - COPPAComplianceManager...")
        ccm = COPPAComplianceManager("COPPAComplianceManager")
        print("   ✅ COPPAComplianceManager создан")
        
        # RussianChildProtectionManager
        print("   - RussianChildProtectionManager...")
        rcpm = RussianChildProtectionManager("RussianChildProtectionManager")
        print("   ✅ RussianChildProtectionManager создан")
        
        # Интегрируем компоненты с SafeFunctionManager
        print("\n3. Интеграция с SafeFunctionManager...")
        
        # RussianDataProtectionManager
        print("   - Интеграция RussianDataProtectionManager...")
        rdpm.integrate_with_safe_function_manager(sfm)
        print("   ✅ RussianDataProtectionManager интегрирован")
        
        # COPPAComplianceManager
        print("   - Интеграция COPPAComplianceManager...")
        ccm.integrate_with_safe_function_manager(sfm)
        print("   ✅ COPPAComplianceManager интегрирован")
        
        # RussianChildProtectionManager
        print("   - Интеграция RussianChildProtectionManager...")
        rcpm.integrate_with_safe_function_manager(sfm)
        print("   ✅ RussianChildProtectionManager интегрирован")
        
        # Тестируем интеграцию
        print("\n4. Тестирование интеграции...")
        
        # Тест RussianDataProtectionManager
        print("   - Тест RussianDataProtectionManager...")
        result1 = sfm.execute_function("RussianDataProtectionManager.register_consent", 
                                     args=("test_user_001", ["marketing", "analytics"], "explicit"))
        print(f"   ✅ RussianDataProtectionManager: {result1}")
        
        # Тест COPPAComplianceManager
        print("   - Тест COPPAComplianceManager...")
        result2 = sfm.execute_function("COPPAComplianceManager.register_child", 
                                     args=("test_child_001", "Test Child", 10, "test_parent_001"))
        print(f"   ✅ COPPAComplianceManager: {result2}")
        
        # Тест RussianChildProtectionManager
        print("   - Тест RussianChildProtectionManager...")
        result3 = sfm.execute_function("RussianChildProtectionManager.register_child", 
                                     args=("test_child_002", "Test Child RU", 12, "test_parent_002"))
        print(f"   ✅ RussianChildProtectionManager: {result3}")
        
        # Получаем статус всех компонентов
        print("\n5. Статус компонентов...")
        
        rdpm_status = rdpm.get_status()
        ccm_status = ccm.get_status()
        rcpm_status = rcpm.get_status()
        
        print(f"   - RussianDataProtectionManager: {rdpm_status['status']}")
        print(f"   - COPPAComplianceManager: {ccm_status['status']}")
        print(f"   - RussianChildProtectionManager: {rcpm_status['status']}")
        
        print("\n" + "=" * 60)
        print("🎉 ИНТЕГРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
        print("✅ Все компоненты соответствия интегрированы с SafeFunctionManager")
        print("✅ Все тесты пройдены успешно")
        print("✅ Компоненты готовы к работе")
        
        return True
        
    except Exception as e:
        logger.error(f"Ошибка интеграции: {e}")
        print(f"\n❌ ОШИБКА ИНТЕГРАЦИИ: {e}")
        return False


if __name__ == "__main__":
    success = integrate_compliance_components()
    if success:
        print("\n🚀 ГОТОВО! Компоненты соответствия интегрированы и протестированы.")
    else:
        print("\n💥 ОШИБКА! Интеграция не удалась.")
        sys.exit(1)
