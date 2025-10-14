#!/usr/bin/env python3
"""
Скрипт для безопасного удаления старых семейных функций
"""

import json
import os
import shutil
from datetime import datetime
from typing import Dict, Any, List

def safe_remove_old_family_functions():
    """Безопасное удаление старых семейных функций"""
    
    print("🗑️ БЕЗОПАСНОЕ УДАЛЕНИЕ СТАРЫХ СЕМЕЙНЫХ ФУНКЦИЙ")
    print("=" * 50)
    
    # Путь к реестру
    registry_path = "data/sfm/function_registry.json"
    
    # Создание резервной копии реестра
    backup_path = f"data/sfm/function_registry_backup_before_cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    shutil.copy2(registry_path, backup_path)
    print(f"✅ Создана резервная копия: {backup_path}")
    
    # Загрузка текущего реестра
    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    # Функции для удаления
    functions_to_remove = [
        "family_communication_hub",  # Старая версия
        # "family_group_manager" - уже удалена
    ]
    
    # Файлы для удаления
    files_to_remove = [
        "security/ai_agents/family_communication_hub.py",
        # "security/family/family_group_manager.py" - уже удален
    ]
    
    removed_functions = []
    removed_files = []
    
    # Удаление функций из реестра
    for function_id in functions_to_remove:
        if function_id in registry["functions"]:
            # Сохранение информации об удаленной функции
            removed_function = registry["functions"][function_id].copy()
            removed_function["removed_at"] = datetime.now().isoformat()
            removed_function["removal_reason"] = "Заменена на enhanced версию"
            removed_functions.append(removed_function)
            
            # Удаление из реестра
            del registry["functions"][function_id]
            print(f"✅ Удалена функция из реестра: {function_id}")
        else:
            print(f"⚠️ Функция не найдена в реестре: {function_id}")
    
    # Удаление файлов
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            # Создание резервной копии файла
            backup_file_path = f"formatting_work/family_integration_analysis/removed_{os.path.basename(file_path)}"
            shutil.copy2(file_path, backup_file_path)
            print(f"✅ Создана резервная копия файла: {backup_file_path}")
            
            # Удаление файла
            os.remove(file_path)
            removed_files.append(file_path)
            print(f"✅ Удален файл: {file_path}")
        else:
            print(f"⚠️ Файл не найден: {file_path}")
    
    # Обновление метаданных реестра
    registry["metadata"] = {
        "total_functions": len(registry["functions"]),
        "last_updated": datetime.now().isoformat(),
        "version": "2.5",
        "cleanup_performed": True,
        "removed_functions": len(removed_functions),
        "removed_files": len(removed_files)
    }
    
    # Сохранение обновленного реестра
    with open(registry_path, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    # Создание отчета об удалении
    cleanup_report = {
        "cleanup_date": datetime.now().isoformat(),
        "removed_functions": removed_functions,
        "removed_files": removed_files,
        "backup_files": [
            backup_path,
            f"formatting_work/family_integration_analysis/removed_family_communication_hub.py"
        ],
        "remaining_family_functions": [
            "family_profile_manager",
            "family_profile_manager_enhanced", 
            "family_communication_hub_a_plus",
            "family_integration_layer"
        ],
        "total_functions_after_cleanup": len(registry["functions"])
    }
    
    # Сохранение отчета
    report_path = f"formatting_work/family_integration_analysis/cleanup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(cleanup_report, f, indent=2, ensure_ascii=False)
    
    print(f"\n🎉 ОЧИСТКА ЗАВЕРШЕНА УСПЕШНО!")
    print(f"📊 Удалено функций: {len(removed_functions)}")
    print(f"📁 Удалено файлов: {len(removed_files)}")
    print(f"📈 Осталось функций в реестре: {len(registry['functions'])}")
    print(f"📋 Отчет сохранен: {report_path}")
    
    return True

def verify_cleanup():
    """Проверка результатов очистки"""
    
    print("\n🔍 ПРОВЕРКА РЕЗУЛЬТАТОВ ОЧИСТКИ")
    print("=" * 40)
    
    # Проверка файлов
    files_to_check = [
        "security/ai_agents/family_communication_hub.py",
        "security/family/family_group_manager.py"
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"❌ Файл все еще существует: {file_path}")
        else:
            print(f"✅ Файл успешно удален: {file_path}")
    
    # Проверка реестра
    registry_path = "data/sfm/function_registry.json"
    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    functions_to_check = [
        "family_communication_hub",
        "family_group_manager"
    ]
    
    for function_id in functions_to_check:
        if function_id in registry["functions"]:
            print(f"❌ Функция все еще в реестре: {function_id}")
        else:
            print(f"✅ Функция успешно удалена из реестра: {function_id}")
    
    # Проверка новых функций
    new_functions = [
        "family_profile_manager_enhanced",
        "family_communication_hub_a_plus", 
        "family_integration_layer"
    ]
    
    print(f"\n✅ НОВЫЕ ФУНКЦИИ В РЕЕСТРЕ:")
    for function_id in new_functions:
        if function_id in registry["functions"]:
            status = registry["functions"][function_id]["status"]
            quality = registry["functions"][function_id]["quality_grade"]
            print(f"  ✅ {function_id}: {status} ({quality})")
        else:
            print(f"  ❌ {function_id}: НЕ НАЙДЕНА")

if __name__ == "__main__":
    safe_remove_old_family_functions()
    verify_cleanup()