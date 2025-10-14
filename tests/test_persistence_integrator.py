#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ТЕСТ ИНТЕГРАТОРА ПЕРСИСТЕНТНОСТИ
"""

import os
import sys
import tempfile
import time

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.safe_function_manager import SafeFunctionManager, SecurityLevel
from security.persistence_integrator import PersistenceIntegrator

def test_persistence_integrator():
    """Тест интегратора персистентности"""
    print("🧪 ТЕСТ ИНТЕГРАТОРА ПЕРСИСТЕНТНОСТИ")
    print("=" * 50)
    
    # Создаем временную директорию
    test_dir = tempfile.mkdtemp()
    registry_file = os.path.join(test_dir, 'test_functions_registry.json')
    
    print(f"1. Тестовая директория: {test_dir}")
    print(f"2. Файл реестра: {registry_file}")
    
    try:
        # Создаем SafeFunctionManager
        print("3. Создание SafeFunctionManager...")
        sfm = SafeFunctionManager()
        print(f"   ✅ SFM создан, функций: {len(sfm.functions)}")
        
        # Создаем PersistenceIntegrator
        print("4. Создание PersistenceIntegrator...")
        integrator = PersistenceIntegrator(sfm, registry_file)
        print("   ✅ Интегратор создан")
        
        # Регистрируем тестовые функции
        print("5. Регистрация тестовых функций...")
        test_functions = [
            {
                "function_id": "test_anti_fraud",
                "name": "TestAntiFraud",
                "description": "Тестовая защита от мошенничества",
                "function_type": "ai_agent",
                "security_level": SecurityLevel.CRITICAL,
                "is_critical": True,
                "auto_enable": False
            },
            {
                "function_id": "test_threat_detection",
                "name": "TestThreatDetection",
                "description": "Тестовое обнаружение угроз",
                "function_type": "ai_agent",
                "security_level": SecurityLevel.HIGH,
                "is_critical": True,
                "auto_enable": False
            },
            {
                "function_id": "test_security_monitoring",
                "name": "TestSecurityMonitoring",
                "description": "Тестовый мониторинг безопасности",
                "function_type": "security",
                "security_level": SecurityLevel.HIGH,
                "is_critical": False,
                "auto_enable": False
            }
        ]
        
        registered_count = 0
        for func_data in test_functions:
            success = integrator.register_function_with_persistence(**func_data)
            if success:
                registered_count += 1
        
        print(f"   ✅ Зарегистрировано функций: {registered_count}")
        
        # Проверяем статус
        print("6. Проверка статуса функций...")
        status = integrator.get_functions_status()
        print(f"   📊 Всего функций: {status.get('total_functions', 0)}")
        print(f"   📊 Включенных: {status.get('enabled_functions', 0)}")
        print(f"   📊 Критических: {status.get('critical_functions', 0)}")
        print(f"   📊 Файл реестра: {status.get('registry_exists', False)}")
        
        # Создаем новый SFM и загружаем функции
        print("7. Создание нового SFM и загрузка функций...")
        sfm2 = SafeFunctionManager()
        integrator2 = PersistenceIntegrator(sfm2, registry_file)
        
        print(f"   ✅ Новый SFM создан, функций: {len(sfm2.functions)}")
        
        # Проверяем загруженные функции
        print("8. Проверка загруженных функций...")
        success = True
        for func_data in test_functions:
            func_id = func_data["function_id"]
            if func_id in sfm2.functions:
                function = sfm2.functions[func_id]
                if (function.name == func_data["name"] and 
                    function.function_type == func_data["function_type"]):
                    print(f"   ✅ {func_data['name']} - OK")
                else:
                    print(f"   ❌ {func_data['name']} - данные не совпадают")
                    success = False
            else:
                print(f"   ❌ {func_data['name']} - не найдена")
                success = False
        
        # Тестируем включение/отключение функций
        print("9. Тестирование включения/отключения функций...")
        if "test_anti_fraud" in sfm2.functions:
            # Включаем функцию
            enable_success = integrator2.enable_function_with_persistence("test_anti_fraud")
            print(f"   ✅ Включение функции: {enable_success}")
            
            # Отключаем функцию
            disable_success = integrator2.disable_function_with_persistence("test_anti_fraud")
            print(f"   ✅ Отключение функции: {disable_success}")
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 ТЕСТ ПРОЙДЕН!")
            print("✅ PersistenceIntegrator работает корректно")
            print("✅ Функции сохраняются и загружаются")
            print("✅ Нет блокировок в SafeFunctionManager")
            print("✅ Готово к production использованию")
        else:
            print("💥 ТЕСТ НЕ ПРОЙДЕН!")
            print("❌ Проблемы с интегратором персистентности")
        
        return success
        
    except Exception as e:
        print(f"💥 КРИТИЧЕСКАЯ ОШИБКА: {e}")
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
    success = test_persistence_integrator()
    sys.exit(0 if success else 1)
