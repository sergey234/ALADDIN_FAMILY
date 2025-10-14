#!/usr/bin/env python3
"""
Скрипт для безопасного переименования backup файлов в formatting_work
Заменяет _backup на _enhanced для устранения путаницы
"""

import os
import shutil
from pathlib import Path
import json
from datetime import datetime

def create_backup_renaming_script():
    """Создает скрипт для переименования backup файлов"""
    
    # Определяем пути
    backup_dir = Path("security/formatting_work/backup_files")
    log_file = backup_dir / "RENAMING_LOG.json"
    
    # Список файлов для переименования
    rename_mappings = [
        {
            "old_name": "mobile_security_agent_original_backup_20250103.py",
            "new_name": "mobile_security_agent_enhanced.py"
        },
        {
            "old_name": "financial_protection_hub_original_backup_20250103.py", 
            "new_name": "financial_protection_hub_enhanced.py"
        },
        {
            "old_name": "malware_detection_agent_original_backup_20250103.py",
            "new_name": "malware_detection_agent_enhanced.py"
        },
        {
            "old_name": "safe_quality_analyzer_original_backup_20250103.py",
            "new_name": "safe_quality_analyzer_enhanced.py"
        },
        {
            "old_name": "security_quality_analyzer_original_backup_20250103.py",
            "new_name": "security_quality_analyzer_enhanced.py"
        },
        {
            "old_name": "family_communication_hub_a_plus_backup.py",
            "new_name": "family_communication_hub_enhanced.py"
        },
        {
            "old_name": "parental_control_bot_v2_original_backup_20250103.py",
            "new_name": "parental_control_bot_v2_enhanced.py"
        },
        {
            "old_name": "notification_service_original_backup_20250103.py",
            "new_name": "notification_service_enhanced.py"
        },
        {
            "old_name": "time_monitor_original_backup_20250103.py",
            "new_name": "time_monitor_enhanced.py"
        },
        {
            "old_name": "elderly_interface_manager_backup_original_backup_20250103.py",
            "new_name": "elderly_interface_manager_enhanced.py"
        },
        {
            "old_name": "content_analyzer_original_backup_20250103.py",
            "new_name": "content_analyzer_enhanced.py"
        },
        {
            "old_name": "put_to_sleep_backup.py",
            "new_name": "put_to_sleep_enhanced.py"
        },
        {
            "old_name": "user_interface_manager_extra_backup.py",
            "new_name": "user_interface_manager_extra_enhanced.py"
        }
    ]
    
    # Создаем лог
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "script_version": "1.0",
        "total_files": len(rename_mappings),
        "renamed_files": 0,
        "failed_files": 0,
        "rename_details": []
    }
    
    print("🔄 НАЧИНАЕМ ПЕРЕИМЕНОВАНИЕ BACKUP ФАЙЛОВ")
    print("=" * 60)
    
    # Проверяем существование папки
    if not backup_dir.exists():
        print(f"❌ Папка {backup_dir} не найдена!")
        return False
    
    # Переименовываем файлы
    for i, mapping in enumerate(rename_mappings, 1):
        old_path = backup_dir / mapping["old_name"]
        new_path = backup_dir / mapping["new_name"]
        
        print(f"\n{i:2d}. {mapping['old_name']}")
        print(f"    → {mapping['new_name']}")
        
        if old_path.exists():
            try:
                # Проверяем, что новый файл не существует
                if new_path.exists():
                    print(f"    ⚠️  Файл {mapping['new_name']} уже существует!")
                    log_data["rename_details"].append({
                        "old_name": mapping["old_name"],
                        "new_name": mapping["new_name"],
                        "status": "failed",
                        "reason": "Target file already exists",
                        "timestamp": datetime.now().isoformat()
                    })
                    log_data["failed_files"] += 1
                    continue
                
                # Переименовываем файл
                old_path.rename(new_path)
                
                # Проверяем размер файла
                file_size = new_path.stat().st_size
                
                print(f"    ✅ Успешно переименован ({file_size:,} байт)")
                
                log_data["rename_details"].append({
                    "old_name": mapping["old_name"],
                    "new_name": mapping["new_name"],
                    "status": "success",
                    "file_size": file_size,
                    "timestamp": datetime.now().isoformat()
                })
                log_data["renamed_files"] += 1
                
            except Exception as e:
                print(f"    ❌ Ошибка: {str(e)}")
                log_data["rename_details"].append({
                    "old_name": mapping["old_name"],
                    "new_name": mapping["new_name"],
                    "status": "failed",
                    "reason": str(e),
                    "timestamp": datetime.now().isoformat()
                })
                log_data["failed_files"] += 1
        else:
            print(f"    ❌ Файл не найден!")
            log_data["rename_details"].append({
                "old_name": mapping["old_name"],
                "new_name": mapping["new_name"],
                "status": "failed",
                "reason": "Source file not found",
                "timestamp": datetime.now().isoformat()
            })
            log_data["failed_files"] += 1
    
    # Сохраняем лог
    try:
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
        print(f"\n📝 Лог сохранен: {log_file}")
    except Exception as e:
        print(f"\n⚠️  Ошибка сохранения лога: {e}")
    
    # Итоговая статистика
    print(f"\n📊 ИТОГОВАЯ СТАТИСТИКА:")
    print(f"   • Всего файлов: {log_data['total_files']}")
    print(f"   • Успешно переименовано: {log_data['renamed_files']}")
    print(f"   • Ошибок: {log_data['failed_files']}")
    
    if log_data["failed_files"] == 0:
        print(f"\n🎉 ВСЕ ФАЙЛЫ УСПЕШНО ПЕРЕИМЕНОВАНЫ!")
        return True
    else:
        print(f"\n⚠️  ЕСТЬ ОШИБКИ! Проверьте лог для деталей.")
        return False

if __name__ == "__main__":
    success = create_backup_renaming_script()
    exit(0 if success else 1)
