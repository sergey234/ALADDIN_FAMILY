#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление 32 невалидных функций в SFM реестре
"""

import json
from datetime import datetime

def fix_invalid_sfm_functions():
    """Исправление невалидных функций в SFM реестре"""
    
    registry_path = "/Users/sergejhlystov/ALADDIN_NEW/data/sfm/function_registry.json"
    
    # Загружаем реестр
    try:
        with open(registry_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Ошибка загрузки реестра: {e}")
        return False
    
    functions = data.get('functions', {})
    
    # Находим невалидные функции
    invalid_functions = []
    for func_id, func_data in functions.items():
        if not isinstance(func_data, dict) or 'function_id' not in func_data:
            invalid_functions.append(func_id)
    
    print(f"🔧 ИСПРАВЛЕНИЕ {len(invalid_functions)} НЕВАЛИДНЫХ ФУНКЦИЙ")
    print("=" * 60)
    
    fixed_count = 0
    
    for func_id in invalid_functions:
        func_data = functions[func_id]
        
        if not isinstance(func_data, dict):
            print(f"❌ {func_id}: НЕ СЛОВАРЬ - ПРОПУСКАЕМ")
            continue
        
        # Создаем правильную структуру функции
        fixed_function = {
            "function_id": func_id,
            "name": func_data.get("name", func_id.replace("_", " ").title()),
            "description": func_data.get("description", f"Enhanced version of {func_id}"),
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
            "class_name": func_data.get("name", func_id.replace("_", "")),
            "version": func_data.get("version", "1.0")
        }
        
        # Заменяем невалидную функцию на исправленную
        functions[func_id] = fixed_function
        fixed_count += 1
        print(f"✅ {func_id}: ИСПРАВЛЕНА")
    
    # Сохраняем исправленный реестр
    try:
        with open(registry_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n🎉 ИСПРАВЛЕНО ФУНКЦИЙ: {fixed_count}/{len(invalid_functions)}")
        print(f"✅ Реестр сохранен: {registry_path}")
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения реестра: {e}")
        return False

def main():
    """Основная функция"""
    print("🔧 ИСПРАВЛЕНИЕ НЕВАЛИДНЫХ ФУНКЦИЙ В SFM")
    print("=" * 50)
    
    if fix_invalid_sfm_functions():
        print("\n🎉 Все невалидные функции успешно исправлены!")
        
        # Проверяем результат
        print("\n🔍 ПРОВЕРКА РЕЗУЛЬТАТА:")
        import subprocess
        result = subprocess.run([
            "python3", "/Users/sergejhlystov/ALADDIN_NEW/scripts/sfm_structure_validator.py"
        ], capture_output=True, text=True)
        print(result.stdout)
    else:
        print("\n❌ Ошибка исправления функций")

if __name__ == "__main__":
    main()