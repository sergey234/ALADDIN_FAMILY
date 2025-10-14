#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete SFM Registry Migration - Полная миграция SFM реестра
Мигрирует все 115 функций со старой схемы на новую
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
    return problem_functions, registry

def migrate_function(func_name, func_data):
    """Миграция одной функции со старой схемы на новую"""
    
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
    
    return new_func

def migrate_all_functions():
    """Миграция всех проблемных функций"""
    print("🚀 ПОЛНАЯ МИГРАЦИЯ SFM РЕЕСТРА")
    print("=" * 60)
    
    # 1. Создаем резервную копию
    backup_file = backup_registry()
    
    # 2. Анализируем проблемные функции
    problem_functions, registry = analyze_problem_functions()
    
    if not problem_functions:
        print("✅ Проблемных функций не найдено!")
        return True
    
    print(f"\n🔧 Начинаем миграцию {len(problem_functions)} функций...")
    
    # 3. Мигрируем все функции
    migrated_count = 0
    for i, (func_name, func_data) in enumerate(problem_functions, 1):
        print(f"\n[{i}/{len(problem_functions)}] Миграция: {func_name}")
        
        # Мигрируем функцию
        migrated_func = migrate_function(func_name, func_data)
        
        # Заменяем в реестре
        registry['functions'][func_name] = migrated_func
        migrated_count += 1
        
        if i % 10 == 0:  # Показываем прогресс каждые 10 функций
            print(f"📊 Прогресс: {i}/{len(problem_functions)} ({i/len(problem_functions)*100:.1f}%)")
    
    # 4. Сохраняем обновленный реестр
    print(f"\n💾 Сохранение обновленного реестра...")
    with open('data/sfm/function_registry.json', 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ МИГРАЦИЯ ЗАВЕРШЕНА!")
    print(f"📊 Мигрировано функций: {migrated_count}")
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
    print("🔧 ПОЛНАЯ МИГРАЦИЯ SFM РЕЕСТРА")
    print("=" * 50)
    
    # Мигрируем все функции
    if migrate_all_functions():
        print("\n🎯 МИГРАЦИЯ ВСЕХ ФУНКЦИЙ УСПЕШНА!")
        
        # Проверяем результат
        if validate_migration():
            print("\n🎉 ВСЯ МИГРАЦИЯ ПРОШЛА УСПЕШНО!")
            print("✅ SFM реестр полностью исправлен!")
        else:
            print("\n❌ МИГРАЦИЯ НЕ УДАЛАСЬ!")
            print("🔧 Требуется дополнительная проверка")
    else:
        print("\n❌ ОШИБКА МИГРАЦИИ!")

if __name__ == "__main__":
    main()