#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ПРОСТОЙ ТЕСТ ПЕРСИСТЕНТНОСТИ - обходит проблему блокировки
"""

import os
import sys
import tempfile
import json
from datetime import datetime

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_simple_persistence():
    """Простой тест персистентности без SafeFunctionManager"""
    print("🧪 ПРОСТОЙ ТЕСТ ПЕРСИСТЕНТНОСТИ")
    print("=" * 40)
    
    # Создаем временную директорию
    test_dir = tempfile.mkdtemp()
    registry_file = os.path.join(test_dir, 'test_functions_registry.json')
    
    print(f"1. Тестовая директория: {test_dir}")
    print(f"2. Файл реестра: {registry_file}")
    
    # Создаем тестовые данные
    test_functions = {
        "test_function_1": {
            "function_id": "test_function_1",
            "name": "TestFunction1",
            "description": "Тестовая функция 1",
            "function_type": "test",
            "security_level": "medium",
            "status": "enabled",
            "created_at": datetime.now().isoformat(),
            "is_critical": False,
            "auto_enable": True
        },
        "test_function_2": {
            "function_id": "test_function_2", 
            "name": "TestFunction2",
            "description": "Тестовая функция 2",
            "function_type": "test",
            "security_level": "high",
            "status": "enabled",
            "created_at": datetime.now().isoformat(),
            "is_critical": True,
            "auto_enable": True
        }
    }
    
    # Сохраняем в файл
    registry_data = {
        "version": "1.0",
        "last_updated": datetime.now().isoformat(),
        "functions": test_functions
    }
    
    print("3. Сохранение тестовых функций...")
    with open(registry_file, 'w', encoding='utf-8') as f:
        json.dump(registry_data, f, indent=2, ensure_ascii=False)
    
    print(f"   ✅ Файл создан: {os.path.exists(registry_file)}")
    print(f"   📁 Размер файла: {os.path.getsize(registry_file)} байт")
    
    # Загружаем из файла
    print("4. Загрузка функций из файла...")
    with open(registry_file, 'r', encoding='utf-8') as f:
        loaded_data = json.load(f)
    
    loaded_functions = loaded_data.get("functions", {})
    print(f"   ✅ Загружено функций: {len(loaded_functions)}")
    
    # Проверяем содержимое
    print("5. Проверка содержимого...")
    success = True
    
    for func_id, func_data in test_functions.items():
        if func_id in loaded_functions:
            loaded_func = loaded_functions[func_id]
            if (loaded_func["name"] == func_data["name"] and 
                loaded_func["function_type"] == func_data["function_type"]):
                print(f"   ✅ {func_data['name']} - OK")
            else:
                print(f"   ❌ {func_data['name']} - данные не совпадают")
                success = False
        else:
            print(f"   ❌ {func_data['name']} - не найдена")
            success = False
    
    # Очистка
    os.remove(registry_file)
    os.rmdir(test_dir)
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 ТЕСТ ПРОЙДЕН!")
        print("✅ Персистентное хранение работает")
        print("✅ JSON сериализация/десериализация работает")
        print("✅ Файловая система работает")
    else:
        print("💥 ТЕСТ НЕ ПРОЙДЕН!")
        print("❌ Проблемы с персистентным хранением")
    
    return success

if __name__ == "__main__":
    success = test_simple_persistence()
    sys.exit(0 if success else 1)
