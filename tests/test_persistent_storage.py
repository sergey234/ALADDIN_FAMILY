#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест персистентного хранения функций SafeFunctionManager
Проверяет, что функции сохраняются и загружаются корректно

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-09
"""

import os
import sys
import json
import time
import tempfile
import shutil

# Добавить путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.safe_function_manager import SafeFunctionManager, SecurityLevel

class TestPersistentStorage:
    """Тест персистентного хранения функций"""
    
    def __init__(self):
        self.test_dir = tempfile.mkdtemp()
        self.registry_file = os.path.join(self.test_dir, "test_functions_registry.json")
        self.sfm1 = None
        self.sfm2 = None
        
    def cleanup(self):
        """Очистка тестовых файлов"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_persistent_storage(self) -> bool:
        """Тест персистентного хранения"""
        
        print("🧪 ТЕСТ ПЕРСИСТЕНТНОГО ХРАНЕНИЯ")
        print("=" * 40)
        
        try:
            # Тест 1: Создать SFM и зарегистрировать функции
            print("1. Создание SafeFunctionManager...")
            config = {
                "registry_file": self.registry_file,
                "enable_persistence": True
            }
            self.sfm1 = SafeFunctionManager("TestSFM1", config)
            
            print("2. Регистрация тестовых функций...")
            test_functions = [
                {
                    "function_id": "test_function_1",
                    "name": "TestFunction1",
                    "description": "Тестовая функция 1",
                    "function_type": "test",
                    "security_level": SecurityLevel.HIGH,
                    "is_critical": True,
                    "auto_enable": True
                },
                {
                    "function_id": "test_function_2", 
                    "name": "TestFunction2",
                    "description": "Тестовая функция 2",
                    "function_type": "test",
                    "security_level": SecurityLevel.MEDIUM,
                    "is_critical": False,
                    "auto_enable": False
                },
                {
                    "function_id": "test_function_3",
                    "name": "TestFunction3",
                    "description": "Тестовая функция 3",
                    "function_type": "security",
                    "security_level": SecurityLevel.CRITICAL,
                    "is_critical": True,
                    "auto_enable": True
                }
            ]
            
            for func_data in test_functions:
                success = self.sfm1.register_function(
                    function_id=func_data["function_id"],
                    name=func_data["name"],
                    description=func_data["description"],
                    function_type=func_data["function_type"],
                    security_level=func_data["security_level"],
                    is_critical=func_data["is_critical"],
                    auto_enable=func_data["auto_enable"]
                )
                
                if not success:
                    print(f"   ❌ Ошибка регистрации {func_data['name']}")
                    return False
                else:
                    print(f"   ✅ {func_data['name']} зарегистрирована")
            
            print(f"   Зарегистрировано функций: {len(self.sfm1.functions)}")
            
            # Тест 2: Проверить, что файл создан
            if not os.path.exists(self.registry_file):
                print("   ❌ Файл реестра не создан")
                return False
            else:
                print("   ✅ Файл реестра создан")
            
            # Тест 3: Создать новый SFM и проверить загрузку
            print("3. Создание нового SafeFunctionManager...")
            self.sfm2 = SafeFunctionManager("TestSFM2", config)
            
            print(f"   Загружено функций: {len(self.sfm2.functions)}")
            
            # Тест 4: Проверить содержимое
            print("4. Проверка содержимого...")
            if len(self.sfm2.functions) == 3:
                print("   ✅ Функции загружены корректно")
                
                for func_id, func in self.sfm2.functions.items():
                    print(f"   - {func.name} ({func.status.value})")
                
                # Тест 5: Проверить детали функций
                print("5. Проверка деталей функций...")
                for func_data in test_functions:
                    func_id = func_data["function_id"]
                    if func_id in self.sfm2.functions:
                        func = self.sfm2.functions[func_id]
                        
                        # Проверить основные свойства
                        if (func.name == func_data["name"] and 
                            func.description == func_data["description"] and
                            func.function_type == func_data["function_type"] and
                            func.security_level == func_data["security_level"] and
                            func.is_critical == func_data["is_critical"] and
                            func.auto_enable == func_data["auto_enable"]):
                            print(f"   ✅ {func.name} - все свойства корректны")
                        else:
                            print(f"   ❌ {func.name} - ошибка в свойствах")
                            return False
                    else:
                        print(f"   ❌ Функция {func_id} не найдена")
                        return False
                
                return True
            else:
                print("   ❌ Функции не загружены")
                return False
                
        except Exception as e:
            print(f"   ❌ Критическая ошибка: {e}")
            return False
    
    def test_file_format(self) -> bool:
        """Тест формата файла реестра"""
        print("\n6. Проверка формата файла реестра...")
        
        try:
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                registry_data = json.load(f)
            
            # Проверить структуру
            required_keys = ["version", "last_updated", "functions"]
            for key in required_keys:
                if key not in registry_data:
                    print(f"   ❌ Отсутствует ключ: {key}")
                    return False
            
            print("   ✅ Структура файла корректна")
            
            # Проверить версию
            if registry_data["version"] == "1.0":
                print("   ✅ Версия файла корректна")
            else:
                print(f"   ❌ Неверная версия: {registry_data['version']}")
                return False
            
            # Проверить функции
            functions = registry_data["functions"]
            if len(functions) == 3:
                print("   ✅ Количество функций корректно")
            else:
                print(f"   ❌ Неверное количество функций: {len(functions)}")
                return False
            
            return True
            
        except Exception as e:
            print(f"   ❌ Ошибка чтения файла: {e}")
            return False

def run_test():
    """Запуск теста"""
    test = TestPersistentStorage()
    
    try:
        # Основной тест
        success1 = test.test_persistent_storage()
        
        # Тест формата файла
        success2 = test.test_file_format()
        
        # Общий результат
        success = success1 and success2
        
        if success:
            print("\n🎉 ТЕСТ ПРОЙДЕН!")
            print("✅ Персистентное хранение работает корректно")
            print("✅ Функции сохраняются и загружаются правильно")
            print("✅ Формат файла реестра корректен")
        else:
            print("\n💥 ТЕСТ НЕ ПРОЙДЕН!")
            print("❌ Проблемы с персистентным хранением")
        
        return success
        
    finally:
        # Очистка
        test.cleanup()

if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
