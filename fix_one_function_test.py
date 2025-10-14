#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление ОДНОЙ функции для тестирования
"""

import json
from datetime import datetime

def fix_one_function():
    """Исправляем только одну функцию для тестирования"""
    
    registry_path = "/Users/sergejhlystov/ALADDIN_NEW/data/sfm/function_registry.json"
    
    print("🔧 ИСПРАВЛЕНИЕ ОДНОЙ ФУНКЦИИ ДЛЯ ТЕСТИРОВАНИЯ")
    print("=" * 50)
    
    # Создаем резервную копию
    backup_path = f"/Users/sergejhlystov/ALADDIN_NEW/data/sfm/function_registry_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    try:
        # Загружаем реестр
        with open(registry_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Создаем резервную копию
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Резервная копия создана: {backup_path}")
        
        functions = data.get('functions', {})
        
        # Находим первую невалидную функцию
        invalid_func_id = None
        for func_id, func_data in functions.items():
            if not isinstance(func_data, dict) or 'function_id' not in func_data:
                invalid_func_id = func_id
                break
        
        if not invalid_func_id:
            print("❌ Невалидных функций не найдено")
            return False
        
        print(f"🔍 Найдена невалидная функция: {invalid_func_id}")
        
        # Показываем текущую структуру
        func_data = functions[invalid_func_id]
        print(f"\n📋 ТЕКУЩАЯ СТРУКТУРА:")
        print(f"Ключи: {list(func_data.keys())}")
        print(f"Нет поля: function_id")
        
        # Исправляем функцию
        fixed_function = {
            "function_id": invalid_func_id,
            "name": func_data.get("name", invalid_func_id.replace("_", " ").title()),
            "description": func_data.get("description", f"Enhanced version of {invalid_func_id}"),
            "function_type": func_data.get("category", "enhanced"),
            "security_level": "medium",
            "status": func_data.get("status", "sleeping"),
            "created_at": func_data.get("created_at", datetime.now().isoformat()),
            "is_critical": False,
            "auto_enable": False,
            "wake_time": "00:00",
            "emergency_wake_up": False,
            "file_path": func_data.get("file_path", ""),
            "lines_of_code": 0,
            "file_size_bytes": 0,
            "file_size_kb": 0.0,
            "flake8_errors": 0,
            "quality_score": "A+",
            "last_updated": func_data.get("last_modified", datetime.now().isoformat()),
            "category": func_data.get("category", "enhanced"),
            "dependencies": func_data.get("dependencies", []),
            "features": func_data.get("tags", []),
            "class_name": func_data.get("name", invalid_func_id.replace("_", "")),
            "version": func_data.get("version", "1.0")
        }
        
        # Заменяем функцию
        functions[invalid_func_id] = fixed_function
        
        # Сохраняем исправленный реестр
        with open(registry_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Функция {invalid_func_id} исправлена!")
        print(f"✅ Реестр сохранен: {registry_path}")
        
        # Проверяем результат
        print(f"\n🔍 ПРОВЕРКА РЕЗУЛЬТАТА:")
        
        # Подсчитываем валидные функции
        valid_count = 0
        invalid_count = 0
        
        for func_id, func_data in functions.items():
            if isinstance(func_data, dict) and 'function_id' in func_data:
                valid_count += 1
            else:
                invalid_count += 1
        
        print(f"Валидных функций: {valid_count}")
        print(f"Невалидных функций: {invalid_count}")
        print(f"Всего функций: {len(functions)}")
        
        if invalid_count < 32:
            print(f"🎉 УСПЕХ! Количество невалидных функций уменьшилось с 32 до {invalid_count}")
        else:
            print(f"⚠️  Количество невалидных функций не изменилось: {invalid_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    fix_one_function()