#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ПРОСТОЙ ТЕСТ ИНТЕГРАТОРА
"""

import os
import sys
import tempfile

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.safe_function_manager import SafeFunctionManager, SecurityLevel
from security.persistence_integrator import PersistenceIntegrator

def test_simple_integrator():
    """Простой тест интегратора"""
    print("🧪 ПРОСТОЙ ТЕСТ ИНТЕГРАТОРА")
    print("=" * 40)
    
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
        
        # Регистрируем ОДНУ тестовую функцию
        print("5. Регистрация тестовой функции...")
        success = integrator.register_function_with_persistence(
            function_id="test_simple",
            name="TestSimple",
            description="Простая тестовая функция",
            function_type="test",
            security_level=SecurityLevel.MEDIUM,
            is_critical=False,
            auto_enable=False
        )
        
        print(f"   ✅ Функция зарегистрирована: {success}")
        print(f"   📊 Всего функций: {len(sfm.functions)}")
        
        # Проверяем файл
        print("6. Проверка файла реестра...")
        if os.path.exists(registry_file):
            print(f"   ✅ Файл создан: {os.path.getsize(registry_file)} байт")
        else:
            print("   ❌ Файл не создан")
            return False
        
        print("\n" + "=" * 40)
        print("🎉 ПРОСТОЙ ТЕСТ ПРОЙДЕН!")
        print("✅ Интегратор работает")
        print("✅ Функция зарегистрирована")
        print("✅ Файл создан")
        
        return True
        
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
    success = test_simple_integrator()
    sys.exit(0 if success else 1)
