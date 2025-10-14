#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сравнение backup файлов с файлами в formatting_work
Анализ по количеству строк кода

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
"""

import os
import json
from pathlib import Path
from datetime import datetime

def count_lines_in_file(file_path):
    """Подсчет строк в файле"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return len(f.readlines())
    except Exception as e:
        print(f"❌ Ошибка чтения {file_path}: {e}")
        return 0

def get_file_size(file_path):
    """Получение размера файла в байтах"""
    try:
        return os.path.getsize(file_path)
    except Exception:
        return 0

def main():
    """Основная функция сравнения"""
    print("🔍 АНАЛИЗ BACKUP ФАЙЛОВ И СРАВНЕНИЕ С formatting_work")
    print("=" * 70)
    
    project_root = Path("/Users/sergejhlystov/ALADDIN_NEW")
    formatting_work = project_root / "security" / "formatting_work"
    
    # Список всех 29 backup файлов для перемещения
    backup_files_to_move = [
        # AI AGENTS BACKUP (19 файлов)
        ("ai_agents", "emergency_security_utils.py.backup_20250927_231342"),
        ("ai_agents", "natural_language_processor.py.backup_20250927_231341"),
        ("ai_agents", "elderly_protection_interface.py.backup_20250928_000215"),
        ("ai_agents", "mobile_security_agent_original_backup_20250103.py"),
        ("ai_agents", "security_quality_analyzer_original_backup_20250103.py"),
        ("ai_agents", "safe_quality_analyzer_original_backup_20250103.py"),
        ("ai_agents", "financial_protection_hub_original_backup_20250103.py"),
        ("ai_agents", "elderly_interface_manager_backup_original_backup_20250103.py"),
        ("ai_agents", "family_communication_hub_a_plus_backup.py"),
        ("ai_agents", "malware_detection_agent.py.backup_20250928_003940"),
        ("ai_agents", "malware_detection_agent_BACKUP.py"),
        ("ai_agents", "mobile_user_ai_agent.py.backup_20250928_005946"),
        ("ai_agents", "voice_security_validator.py.backup_20250927_234616"),
        ("ai_agents", "speech_recognition_engine.py.backup_20250928_003043"),
        ("ai_agents", "voice_response_generator.py.backup_20250928_002228"),
        ("ai_agents", "contextual_alert_system.py.backup_20250927_232629"),
        ("ai_agents", "password_security_agent.py.backup_011225"),
        ("ai_agents", "monitor_manager.py.backup_011225"),
        ("ai_agents", "analytics_manager.py.backup_011225"),
        
        # BOTS BACKUP (2 файла)
        ("bots", "mobile_navigation_bot.py.backup_before_formatting"),
        ("bots", "parental_control_bot_v2_original_backup_20250103.py"),
        
        # FAMILY BACKUP (6 файлов)
        ("family", "family_profile_manager.py.backup_20250926_133852"),
        ("family", "family_profile_manager.py.backup_20250926_133733"),
        ("family", "family_profile_manager.py.backup_20250926_133317"),
        ("family", "family_profile_manager.py.backup_20250926_133258"),
        ("family", "family_profile_manager.py.backup_20250926_132405"),
        ("family", "family_profile_manager.py.backup_20250926_132307"),
        
        # PRELIMINARY BACKUP (2 файла)
        ("preliminary", "zero_trust_service.py.backup_20250927_234000"),
        ("preliminary", "risk_assessment.py.backup_20250927_233351")
    ]
    
    comparison_results = {
        "timestamp": datetime.now().isoformat(),
        "total_backup_files": len(backup_files_to_move),
        "files_already_moved": 0,
        "files_already_in_formatting_work": 0,
        "files_need_moving": 0,
        "files_not_found": 0,
        "comparison_details": []
    }
    
    print(f"📋 Всего backup файлов для анализа: {len(backup_files_to_move)}")
    print()
    
    for i, (subdir, backup_filename) in enumerate(backup_files_to_move, 1):
        print(f"[{i}/{len(backup_files_to_move)}] Анализ: {backup_filename}")
        
        backup_path = project_root / "security" / subdir / backup_filename
        backup_files_path = formatting_work / "backup_files" / backup_filename
        
        # Проверяем различные места в formatting_work
        duplicates_path = formatting_work / "duplicates"
        
        # Ищем файлы в formatting_work с похожими именами
        similar_files_in_formatting_work = []
        
        # Поиск в duplicates
        for file_in_duplicates in duplicates_path.rglob("*.py"):
            if any(keyword in file_in_duplicates.name.lower() for keyword in [
                backup_filename.replace(".backup_", "_").replace("_backup_", "_").replace("_original_", "_").replace(".py", "").lower(),
                backup_filename.split(".")[0].lower()
            ]):
                similar_files_in_formatting_work.append(file_in_duplicates)
        
        # Поиск в корне formatting_work
        for file_in_root in formatting_work.rglob("*.py"):
            if file_in_root.parent != duplicates_path and file_in_root.parent != formatting_work / "backup_files":
                if any(keyword in file_in_root.name.lower() for keyword in [
                    backup_filename.replace(".backup_", "_").replace("_backup_", "_").replace("_original_", "_").replace(".py", "").lower(),
                    backup_filename.split(".")[0].lower()
                ]):
                    similar_files_in_formatting_work.append(file_in_root)
        
        comparison_detail = {
            "backup_filename": backup_filename,
            "backup_subdir": subdir,
            "backup_exists": backup_path.exists(),
            "backup_moved": backup_files_path.exists(),
            "backup_lines": 0,
            "backup_size": 0,
            "similar_files_in_formatting_work": [],
            "status": "unknown"
        }
        
        if backup_path.exists():
            comparison_detail["backup_lines"] = count_lines_in_file(backup_path)
            comparison_detail["backup_size"] = get_file_size(backup_path)
            comparison_detail["status"] = "exists"
        else:
            comparison_detail["status"] = "not_found"
            comparison_results["files_not_found"] += 1
        
        if backup_files_path.exists():
            comparison_detail["backup_moved"] = True
            comparison_detail["status"] = "already_moved"
            comparison_results["files_already_moved"] += 1
        
        # Анализ похожих файлов в formatting_work
        for similar_file in similar_files_in_formatting_work:
            similar_info = {
                "path": str(similar_file),
                "name": similar_file.name,
                "lines": count_lines_in_file(similar_file),
                "size": get_file_size(similar_file),
                "relative_path": str(similar_file.relative_to(formatting_work))
            }
            comparison_detail["similar_files_in_formatting_work"].append(similar_info)
        
        if comparison_detail["similar_files_in_formatting_work"]:
            comparison_results["files_already_in_formatting_work"] += 1
            comparison_detail["status"] = "similar_exists_in_formatting_work"
        elif comparison_detail["backup_exists"] and not comparison_detail["backup_moved"]:
            comparison_results["files_need_moving"] += 1
            comparison_detail["status"] = "needs_moving"
        
        comparison_results["comparison_details"].append(comparison_detail)
        
        # Вывод краткой информации
        if comparison_detail["backup_exists"]:
            print(f"  ✅ Backup найден: {comparison_detail['backup_lines']} строк")
        else:
            print(f"  ❌ Backup не найден")
            
        if comparison_detail["backup_moved"]:
            print(f"  ✅ Уже перемещен в backup_files/")
        elif comparison_detail["similar_files_in_formatting_work"]:
            print(f"  ⚠️  Найдено похожих файлов в formatting_work: {len(comparison_detail['similar_files_in_formatting_work'])}")
            for similar in comparison_detail["similar_files_in_formatting_work"]:
                print(f"    - {similar['name']}: {similar['lines']} строк")
        else:
            print(f"  🔄 Нужно переместить")
        
        print()
    
    # Итоговая статистика
    print("=" * 70)
    print("📊 ИТОГОВАЯ СТАТИСТИКА:")
    print(f"📁 Всего backup файлов: {comparison_results['total_backup_files']}")
    print(f"✅ Уже перемещены в backup_files/: {comparison_results['files_already_moved']}")
    print(f"⚠️  Похожие файлы в formatting_work: {comparison_results['files_already_in_formatting_work']}")
    print(f"🔄 Нужно переместить: {comparison_results['files_need_moving']}")
    print(f"❌ Не найдены: {comparison_results['files_not_found']}")
    print("=" * 70)
    
    # Сохранение результатов
    results_file = formatting_work / "backup_files" / "BACKUP_COMPARISON_ANALYSIS.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(comparison_results, f, ensure_ascii=False, indent=2)
    
    print(f"📋 Детальный анализ сохранен: {results_file}")
    
    return comparison_results

if __name__ == "__main__":
    main()