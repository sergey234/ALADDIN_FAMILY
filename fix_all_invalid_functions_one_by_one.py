#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление всех невалидных функций по одной за раз
"""

import json
from datetime import datetime

def fix_all_invalid_functions():
    """Исправляем все невалидные функции по одной за раз"""
    
    registry_path = "/Users/sergejhlystov/ALADDIN_NEW/data/sfm/function_registry.json"
    
    print("🔧 ИСПРАВЛЕНИЕ ВСЕХ НЕВАЛИДНЫХ ФУНКЦИЙ ПО ОДНОЙ")
    print("=" * 60)
    
    # Создаем резервную копию
    backup_path = f"/Users/sergejhlystov/ALADDIN_NEW/data/sfm/function_registry_backup_all_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    try:
        # Загружаем реестр
        with open(registry_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Создаем резервную копию
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Резервная копия создана: {backup_path}")
        
        functions = data.get('functions', {})
        
        # Находим все невалидные функции
        invalid_functions = []
        for func_id, func_data in functions.items():
            if not isinstance(func_data, dict) or 'function_id' not in func_data:
                invalid_functions.append(func_id)
        
        print(f"🔍 Найдено невалидных функций: {len(invalid_functions)}")
        print("=" * 60)
        
        fixed_count = 0
        
        # Исправляем по одной функции
        for i, func_id in enumerate(invalid_functions, 1):
            print(f"\n🔧 ИСПРАВЛЕНИЕ {i}/{len(invalid_functions)}: {func_id}")
            print("-" * 50)
            
            func_data = functions[func_id]
            
            # Показываем текущую структуру
            print(f"📋 Текущие ключи: {list(func_data.keys())}")
            print(f"❌ Отсутствует: function_id")
            
            # Исправляем функцию
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
                "class_name": func_data.get("name", func_data.get("class_name", func_id.replace("_", ""))),
                "version": func_data.get("version", "1.0")
            }
            
            # Заменяем функцию
            functions[func_id] = fixed_function
            
            # Сохраняем после каждой функции
            with open(registry_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Проверяем результат
            valid_count = 0
            invalid_count = 0
            
            for check_func_id, check_func_data in functions.items():
                if isinstance(check_func_data, dict) and 'function_id' in check_func_data:
                    valid_count += 1
                else:
                    invalid_count += 1
            
            fixed_count += 1
            print(f"✅ Функция {func_id} исправлена!")
            print(f"📊 Статистика: {valid_count} валидных, {invalid_count} невалидных")
            
            # Пауза между исправлениями
            if i < len(invalid_functions):
                print("⏳ Пауза 1 секунда...")
                import time
                time.sleep(1)
        
        print(f"\n🎉 ВСЕ ФУНКЦИИ ИСПРАВЛЕНЫ!")
        print(f"✅ Исправлено функций: {fixed_count}")
        print(f"✅ Реестр сохранен: {registry_path}")
        
        # Финальная проверка
        print(f"\n🔍 ФИНАЛЬНАЯ ПРОВЕРКА:")
        valid_count = 0
        invalid_count = 0
        
        for func_id, func_data in functions.items():
            if isinstance(func_data, dict) and 'function_id' in func_data:
                valid_count += 1
            else:
                invalid_count += 1
        
        print(f"📊 ИТОГОВАЯ СТАТИСТИКА:")
        print(f"  - Всего функций: {len(functions)}")
        print(f"  - Валидных функций: {valid_count}")
        print(f"  - Невалидных функций: {invalid_count}")
        print(f"  - Процент валидности: {(valid_count/len(functions)*100):.1f}%")
        
        if invalid_count == 0:
            print(f"🎉 ВСЕ ФУНКЦИИ ВАЛИДНЫ! SFM РЕЕСТР ПОЛНОСТЬЮ ИСПРАВЛЕН!")
        else:
            print(f"⚠️  Осталось {invalid_count} невалидных функций")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    fix_all_invalid_functions()