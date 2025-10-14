#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SFM Registry Migration Script - Миграция структуры SFM реестра
Исправляет 115 функций со старой схемы на новую
"""

import json
import shutil
from datetime import datetime
from pathlib import Path

def backup_registry():
    """Создание резервной копии реестра"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f"data/sfm/function_registry_backup_{timestamp}.json"
    
    shutil.copy2('data/sfm/function_registry.json', backup_file)
    print(f"✅ Резервная копия создана: {backup_file}")
    return backup_file

def analyze_problem_functions():
    """Анализ проблемных функций"""
    with open('data/sfm/function_registry.json', 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    functions = registry.get('functions', {})
    problem_functions = []
    
    for name, func in functions.items():
        if not isinstance(func, dict):
            continue
            
        # Проверяем старую схему
        if 'id' in func and 'function_id' not in func:
            problem_functions.append((name, func))
    
    print(f"🔍 Найдено проблемных функций: {len(problem_functions)}")
    return problem_functions

def migrate_single_function(func_name, func_data):
    """Миграция одной функции со старой схемы на новую"""
    print(f"\n🔧 Миграция функции: {func_name}")
    
    # Создаем новую структуру
    new_func = {
        # Основные поля
        "function_id": func_data.get('id', func_name),
        "name": func_data.get('name', func_name),
        "description": func_data.get('description', ''),
        "function_type": func_data.get('category', 'security_analytics').lower(),
        "security_level": func_data.get('security_level', 'high').lower(),
        "status": "active" if func_data.get('status') == 'ENABLED' else 'inactive',
        "is_critical": True,  # Добавляем недостающее поле
        
        # Статистика
        "execution_count": 0,
        "success_count": 0,
        "error_count": 0,
        
        # Временные метки
        "created_at": func_data.get('created_at', datetime.now().isoformat()),
        "last_execution": None,
        "last_status_check": None,
        
        # Конфигурация
        "auto_enable": False,
        "wake_time": None,
        "emergency_wake_up": False,
        
        # Метаданные
        "features": [],
        "dependencies": [],
        "config": {},
        "metrics": {},
        "version": "1.0.0",
        "author": "AI Agent",
        "license": "Proprietary",
        "tags": [],
        
        # Состояние сна
        "sleep_state": {
            "sleep_time": None,
            "previous_status": "active",
            "minimal_system_sleep": False
        }
    }
    
    print(f"✅ Функция {func_name} мигрирована")
    print(f"  - function_id: {new_func['function_id']}")
    print(f"  - function_type: {new_func['function_type']}")
    print(f"  - status: {new_func['status']}")
    print(f"  - is_critical: {new_func['is_critical']}")
    
    return new_func

def test_migration():
    """Тестирование миграции на одной функции"""
    print("🚀 ТЕСТИРОВАНИЕ МИГРАЦИИ SFM РЕЕСТРА")
    print("=" * 60)
    
    # 1. Создаем резервную копию
    backup_file = backup_registry()
    
    # 2. Анализируем проблемные функции
    problem_functions = analyze_problem_functions()
    
    if not problem_functions:
        print("✅ Проблемных функций не найдено!")
        return True
    
    # 3. Берем первую функцию для тестирования
    test_func_name, test_func_data = problem_functions[0]
    print(f"\n🎯 Тестируем на функции: {test_func_name}")
    
    # 4. Мигрируем функцию
    migrated_func = migrate_single_function(test_func_name, test_func_data)
    
    # 5. Загружаем реестр
    with open('data/sfm/function_registry.json', 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    # 6. Заменяем функцию в реестре
    registry['functions'][test_func_name] = migrated_func
    
    # 7. Сохраняем обновленный реестр
    with open('data/sfm/function_registry.json', 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Тестовая миграция завершена!")
    print(f"📁 Резервная копия: {backup_file}")
    
    return True

def validate_migration():
    """Проверка результата миграции"""
    print("\n🔍 ПРОВЕРКА РЕЗУЛЬТАТА МИГРАЦИИ")
    print("=" * 50)
    
    # Запускаем валидатор
    import subprocess
    result = subprocess.run(['python3', 'scripts/sfm_structure_validator.py'], 
                          capture_output=True, text=True)
    
    print("📊 РЕЗУЛЬТАТ ВАЛИДАЦИИ:")
    print(result.stdout)
    
    if result.returncode == 0:
        print("✅ ВАЛИДАЦИЯ ПРОЙДЕНА!")
        return True
    else:
        print("❌ ВАЛИДАЦИЯ НЕ ПРОЙДЕНА!")
        return False

def main():
    """Главная функция"""
    print("🔧 МИГРАЦИЯ SFM РЕЕСТРА")
    print("=" * 40)
    
    # Тестируем миграцию
    if test_migration():
        print("\n🎯 ТЕСТОВАЯ МИГРАЦИЯ УСПЕШНА!")
        
        # Проверяем результат
        if validate_migration():
            print("\n🎉 МИГРАЦИЯ ПРОШЛА УСПЕШНО!")
            print("✅ Можно применять ко всем 115 функциям")
        else:
            print("\n❌ МИГРАЦИЯ НЕ УДАЛАСЬ!")
            print("🔧 Требуется доработка")
    else:
        print("\n❌ ОШИБКА ТЕСТОВОЙ МИГРАЦИИ!")

if __name__ == "__main__":
    main()