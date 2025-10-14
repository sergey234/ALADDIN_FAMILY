#!/usr/bin/env python3
"""
Скрипт для копирования enhanced файлов обратно в основную систему
и проверки SFM регистрации
"""

import os
import shutil
from pathlib import Path
import json
from datetime import datetime

def copy_enhanced_files():
    """Копирует enhanced файлы обратно в основную систему"""
    
    # Определяем пути
    source_dir = Path("security/formatting_work/backup_files")
    log_file = source_dir / "COPY_ENHANCED_LOG.json"
    
    # Маппинг файлов: enhanced файл -> оригинальное расположение
    file_mappings = [
        {
            "enhanced_file": "mobile_security_agent_enhanced.py",
            "original_path": "security/ai_agents/mobile_security_agent_enhanced.py"
        },
        {
            "enhanced_file": "financial_protection_hub_enhanced.py",
            "original_path": "security/ai_agents/financial_protection_hub_enhanced.py"
        },
        {
            "enhanced_file": "malware_detection_agent_enhanced.py",
            "original_path": "security/ai_agents/malware_detection_agent_enhanced.py"
        },
        {
            "enhanced_file": "safe_quality_analyzer_enhanced.py",
            "original_path": "security/ai_agents/safe_quality_analyzer_enhanced.py"
        },
        {
            "enhanced_file": "security_quality_analyzer_enhanced.py",
            "original_path": "security/ai_agents/security_quality_analyzer_enhanced.py"
        },
        {
            "enhanced_file": "family_communication_hub_enhanced.py",
            "original_path": "security/family/family_communication_hub_enhanced.py"
        },
        {
            "enhanced_file": "parental_control_bot_v2_enhanced.py",
            "original_path": "security/bots/parental_control_bot_v2_enhanced.py"
        },
        {
            "enhanced_file": "notification_service_enhanced.py",
            "original_path": "security/microservices/notification_service_enhanced.py"
        },
        {
            "enhanced_file": "time_monitor_enhanced.py",
            "original_path": "security/active/time_monitor_enhanced.py"
        },
        {
            "enhanced_file": "elderly_interface_manager_enhanced.py",
            "original_path": "security/managers/elderly_interface_manager_enhanced.py"
        },
        {
            "enhanced_file": "content_analyzer_enhanced.py",
            "original_path": "security/ai_agents/content_analyzer_enhanced.py"
        },
        {
            "enhanced_file": "put_to_sleep_enhanced.py",
            "original_path": "security/microservices/put_to_sleep_enhanced.py"
        },
        {
            "enhanced_file": "user_interface_manager_extra_enhanced.py",
            "original_path": "security/microservices/user_interface_manager_extra_enhanced.py"
        }
    ]
    
    # Создаем лог
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "script_version": "1.0",
        "total_files": len(file_mappings),
        "copied_files": 0,
        "failed_files": 0,
        "copy_details": []
    }
    
    print("🔄 КОПИРОВАНИЕ ENHANCED ФАЙЛОВ В ОСНОВНУЮ СИСТЕМУ")
    print("=" * 60)
    
    # Проверяем существование папки
    if not source_dir.exists():
        print(f"❌ Папка {source_dir} не найдена!")
        return False
    
    # Копируем файлы
    for i, mapping in enumerate(file_mappings, 1):
        source_path = source_dir / mapping["enhanced_file"]
        dest_path = Path(mapping["original_path"])
        
        print(f"\n{i:2d}. {mapping['enhanced_file']}")
        print(f"    → {mapping['original_path']}")
        
        if source_path.exists():
            try:
                # Создаем директорию если не существует
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Копируем файл
                shutil.copy2(source_path, dest_path)
                
                # Проверяем размер файла
                file_size = dest_path.stat().st_size
                
                print(f"    ✅ Успешно скопирован ({file_size:,} байт)")
                
                log_data["copy_details"].append({
                    "enhanced_file": mapping["enhanced_file"],
                    "original_path": mapping["original_path"],
                    "status": "success",
                    "file_size": file_size,
                    "timestamp": datetime.now().isoformat()
                })
                log_data["copied_files"] += 1
                
            except Exception as e:
                print(f"    ❌ Ошибка: {str(e)}")
                log_data["copy_details"].append({
                    "enhanced_file": mapping["enhanced_file"],
                    "original_path": mapping["original_path"],
                    "status": "failed",
                    "reason": str(e),
                    "timestamp": datetime.now().isoformat()
                })
                log_data["failed_files"] += 1
        else:
            print(f"    ❌ Файл не найден!")
            log_data["copy_details"].append({
                "enhanced_file": mapping["enhanced_file"],
                "original_path": mapping["original_path"],
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
    print(f"   • Успешно скопировано: {log_data['copied_files']}")
    print(f"   • Ошибок: {log_data['failed_files']}")
    
    if log_data["failed_files"] == 0:
        print(f"\n🎉 ВСЕ ФАЙЛЫ УСПЕШНО СКОПИРОВАНЫ!")
        return True
    else:
        print(f"\n⚠️  ЕСТЬ ОШИБКИ! Проверьте лог для деталей.")
        return False

if __name__ == "__main__":
    success = copy_enhanced_files()
    exit(0 if success else 1)
