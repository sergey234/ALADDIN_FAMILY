#!/usr/bin/env python3
"""
Скрипт для исправления путей к файлам в SFM реестре
Исправляет по 10 файлов за раз с проверкой
"""

import json
import os
from datetime import datetime

def find_file_in_project(filename: str, root_dir: str):
    """Ищет файл по имени во всем проекте."""
    for dirpath, _, filenames in os.walk(root_dir):
        if filename in filenames:
            return os.path.relpath(os.path.join(dirpath, filename), root_dir)
    return None

def fix_sfm_paths(registry_file: str, root_dir: str, max_fixes: int = 10):
    """Исправляет пути к файлам в SFM реестре."""
    
    # Загружаем реестр
    with open(registry_file, 'r', encoding='utf-8') as f:
        registry_data = json.load(f)
    
    functions = registry_data.get("functions", {})
    fixed_count = 0
    total_functions = len(functions)
    
    print(f"🔧 ИСПРАВЛЕНИЕ ПУТЕЙ К ФАЙЛАМ")
    print(f"================================================")
    print(f"Всего функций в реестре: {total_functions}")
    print(f"Максимум исправлений за раз: {max_fixes}")
    print("")
    
    for func_id, func_data in functions.items():
        if fixed_count >= max_fixes:
            break
            
        old_path = func_data.get("file_path", "")
        
        # Проверяем если путь пустой или файл не существует
        if not old_path or (old_path and not os.path.exists(old_path)):
            # Создаем имя файла на основе ID функции
            filename = f"{func_id}.py"
            print(f"🔍 Ищем файл: {filename}")
            
            new_path = find_file_in_project(filename, root_dir)
            if new_path:
                # Исправляем путь
                func_data["file_path"] = new_path
                func_data["last_updated"] = datetime.now().isoformat()
                fixed_count += 1
                print(f"✅ Исправлен путь для {func_id}: {new_path}")
            else:
                print(f"❌ Файл не найден: {filename}")
    
    # Сохраняем изменения
    if fixed_count > 0:
        registry_data["functions"] = functions
        registry_data["last_updated"] = datetime.now().isoformat()
        
        with open(registry_file, 'w', encoding='utf-8') as f:
            json.dump(registry_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Изменения сохранены в {registry_file}")
    
    print(f"")
    print(f"🎯 РЕЗУЛЬТАТ:")
    print(f"   Исправлено: {fixed_count} из {max_fixes} запланированных")
    print(f"   Осталось функций с неправильными путями: {total_functions - fixed_count}")
    
    return fixed_count

if __name__ == "__main__":
    project_root = os.getcwd()
    registry_path = os.path.join(project_root, "data", "sfm", "function_registry.json")
    
    if not os.path.exists(registry_path):
        print(f"❌ Файл реестра не найден: {registry_path}")
        exit(1)
    
    # Исправляем по 10 файлов за раз
    fix_sfm_paths(registry_path, project_root, max_fixes=10)