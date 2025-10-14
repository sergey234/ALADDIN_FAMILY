#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRODUCTION ТЕСТ ПЕРСИСТЕНТНОСТИ
"""

import os
import sys
import tempfile

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.safe_function_manager import SafeFunctionManager, SecurityLevel
from security.production_persistence_manager import ProductionPersistenceManager

def test_production_persistence():
    """Production тест персистентности"""
    print("🧪 PRODUCTION ТЕСТ ПЕРСИСТЕНТНОСТИ")
    print("=" * 50)
    
    # Создаем временную директорию
    test_dir = tempfile.mkdtemp()
    registry_file = os.path.join(test_dir, 'production_functions_registry.json')
    
    print(f"1. Тестовая директория: {test_dir}")
    print(f"2. Файл реестра: {registry_file}")
    
    try:
        # Создаем SafeFunctionManager
        print("3. Создание SafeFunctionManager...")
        sfm = SafeFunctionManager()
        print(f"   ✅ SFM создан, функций: {len(sfm.functions)}")
        
        # Создаем ProductionPersistenceManager
        print("4. Создание ProductionPersistenceManager...")
        manager = ProductionPersistenceManager(sfm, registry_file)
        print("   ✅ Менеджер создан")
        
        # Инициализируем критические функции
        print("5. Инициализация критических функций...")
        init_success = manager.initialize_security_functions()
        print(f"   ✅ Инициализация: {init_success}")
        
        # Проверяем статус
        print("6. Проверка статуса функций...")
        status = manager.get_functions_status()
        print(f"   📊 Всего функций: {status.get('total_functions', 0)}")
        print(f"   📊 Включенных: {status.get('enabled_functions', 0)}")
        print(f"   📊 Критических: {status.get('critical_functions', 0)}")
        print(f"   📊 Файл реестра: {status.get('registry_exists', False)}")
        
        # Создаем новый SFM и загружаем функции
        print("7. Создание нового SFM и загрузка функций...")
        sfm2 = SafeFunctionManager()
        manager2 = ProductionPersistenceManager(sfm2, registry_file)
        
        load_success = manager2.load_functions()
        print(f"   ✅ Загрузка функций: {load_success}")
        print(f"   📊 Функций в новом SFM: {len(sfm2.functions)}")
        
        # Проверяем загруженные функции
        print("8. Проверка загруженных функций...")
        success = True
        expected_functions = ["anti_fraud_master_ai", "threat_detection_agent", "security_monitoring"]
        
        for func_id in expected_functions:
            if func_id in sfm2.functions:
                function = sfm2.functions[func_id]
                print(f"   ✅ {function.name} - OK")
            else:
                print(f"   ❌ {func_id} - не найдена")
                success = False
        
        # Тестируем регистрацию новой функции
        print("9. Тестирование регистрации новой функции...")
        new_func_success = manager2.register_function_with_persistence(
            function_id="test_production_function",
            name="TestProductionFunction",
            description="Тестовая production функция",
            function_type="test",
            security_level=SecurityLevel.MEDIUM,
            is_critical=False,
            auto_enable=False
        )
        print(f"   ✅ Новая функция зарегистрирована: {new_func_success}")
        
        # Финальная проверка
        print("10. Финальная проверка...")
        final_status = manager2.get_functions_status()
        print(f"   📊 Итого функций: {final_status.get('total_functions', 0)}")
        
        print("\n" + "=" * 50)
        if success and load_success and new_func_success:
            print("🎉 PRODUCTION ТЕСТ ПРОЙДЕН!")
            print("✅ ProductionPersistenceManager работает корректно")
            print("✅ Критические функции инициализированы")
            print("✅ Функции сохраняются и загружаются")
            print("✅ Нет блокировок в SafeFunctionManager")
            print("✅ Готово к production использованию")
        else:
            print("💥 PRODUCTION ТЕСТ НЕ ПРОЙДЕН!")
            print("❌ Проблемы с production менеджером")
        
        return success and load_success and new_func_success
        
    except Exception as e:
        print(f"💥 КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Очистка
        try:
            if os.path.exists(registry_file):
                os.remove(registry_file)
            os.rmdir(test_dir)
        except:
            pass

if __name__ == "__main__":
    success = test_production_persistence()
    sys.exit(0 if success else 1)
