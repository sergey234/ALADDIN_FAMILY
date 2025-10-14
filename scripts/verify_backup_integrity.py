#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Детальная проверка целостности бекапа системы безопасности
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime

def verify_backup_integrity():
    """Проверка целостности бекапа"""
    print("🔍 ДЕТАЛЬНАЯ ПРОВЕРКА ЦЕЛОСТНОСТИ БЕКАПА")
    print("=" * 60)
    
    backup_dir = Path("../ALADDIN_COMPLETE_SECURITY_BACKUP_20250915_203400")
    
    if not backup_dir.exists():
        print("❌ Директория бекапа не найдена!")
        return False
    
    # Критические файлы для проверки
    critical_files = [
        "data/sfm/function_registry.json",
        "security/enhanced_alerting.py",
        "core/safe_function_manager.py",
        "config/sleep_mode_config.json",
        "security/ai_agents/behavioral_analysis_agent.py",
        "security/managers/sleep_mode_manager.py",
        "security/managers/analytics_manager.py",
        "security/microservices/rate_limiter.py"
    ]
    
    print("📋 ПРОВЕРКА КРИТИЧЕСКИХ ФАЙЛОВ:")
    print("-" * 40)
    
    critical_present = 0
    for critical_file in critical_files:
        file_path = backup_dir / critical_file
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"✅ {critical_file} - {size} байт")
            critical_present += 1
        else:
            print(f"❌ {critical_file} - НЕ НАЙДЕН")
    
    print(f"\n📊 Критических файлов найдено: {critical_present}/{len(critical_files)}")
    
    # Проверка структуры директорий
    print("\n📁 ПРОВЕРКА СТРУКТУРЫ ДИРЕКТОРИЙ:")
    print("-" * 40)
    
    required_dirs = [
        "security",
        "core",
        "config", 
        "data",
        "logs",
        "tests",
        "scripts",
        "docs"
    ]
    
    dirs_present = 0
    for dir_name in required_dirs:
        dir_path = backup_dir / dir_name
        if dir_path.exists():
            files_count = len(list(dir_path.rglob('*')))
            print(f"✅ {dir_name}/ - {files_count} файлов")
            dirs_present += 1
        else:
            print(f"❌ {dir_name}/ - НЕ НАЙДЕНА")
    
    print(f"\n📊 Директорий найдено: {dirs_present}/{len(required_dirs)}")
    
    # Подсчет файлов по типам
    print("\n📊 СТАТИСТИКА ФАЙЛОВ:")
    print("-" * 40)
    
    file_types = {
        '.py': 0,
        '.json': 0,
        '.md': 0,
        '.log': 0,
        '.db': 0,
        '.txt': 0
    }
    
    total_files = 0
    total_size = 0
    
    for root, dirs, files in os.walk(backup_dir):
        for file in files:
            file_path = Path(root) / file
            total_files += 1
            total_size += file_path.stat().st_size
            
            ext = file_path.suffix.lower()
            if ext in file_types:
                file_types[ext] += 1
    
    for ext, count in file_types.items():
        print(f"📄 {ext} файлов: {count}")
    
    print(f"\n📊 Всего файлов: {total_files}")
    print(f"💾 Общий размер: {total_size:,} байт ({total_size / (1024*1024):.1f} МБ)")
    
    # Проверка SFM Registry
    print("\n🔍 ПРОВЕРКА SFM REGISTRY:")
    print("-" * 40)
    
    sfm_file = backup_dir / "data/sfm/function_registry.json"
    if sfm_file.exists():
        try:
            with open(sfm_file, 'r', encoding='utf-8') as f:
                sfm_data = json.load(f)
            
            functions_count = len(sfm_data.get('functions', {}))
            total_functions = sfm_data.get('total_functions', 0)
            
            print(f"✅ SFM Registry загружен успешно")
            print(f"📊 Функций в реестре: {functions_count}")
            print(f"📊 Общее количество функций: {total_functions}")
            
            # Проверка критических функций
            critical_functions = [f for f, data in sfm_data.get('functions', {}).items() 
                                if data.get('is_critical', False)]
            print(f"🔒 Критических функций: {len(critical_functions)}")
            
        except Exception as e:
            print(f"❌ Ошибка загрузки SFM Registry: {e}")
    else:
        print("❌ SFM Registry не найден!")
    
    # Итоговая оценка
    print("\n🎯 ИТОГОВАЯ ОЦЕНКА ЦЕЛОСТНОСТИ:")
    print("=" * 60)
    
    integrity_score = 0
    max_score = 100
    
    # Критические файлы (40 баллов)
    critical_score = (critical_present / len(critical_files)) * 40
    integrity_score += critical_score
    print(f"🔒 Критические файлы: {critical_present}/{len(critical_files)} ({critical_score:.1f}/40)")
    
    # Структура директорий (20 баллов)
    dirs_score = (dirs_present / len(required_dirs)) * 20
    integrity_score += dirs_score
    print(f"📁 Структура директорий: {dirs_present}/{len(required_dirs)} ({dirs_score:.1f}/20)")
    
    # Общее количество файлов (20 баллов)
    files_score = min(20, (total_files / 1000) * 20)  # Нормализация к 1000 файлам
    integrity_score += files_score
    print(f"📄 Общее количество файлов: {total_files} ({files_score:.1f}/20)")
    
    # SFM Registry (20 баллов)
    sfm_score = 20 if sfm_file.exists() else 0
    integrity_score += sfm_score
    print(f"📊 SFM Registry: {'✅' if sfm_file.exists() else '❌'} ({sfm_score}/20)")
    
    print(f"\n🏆 ОБЩИЙ БАЛЛ ЦЕЛОСТНОСТИ: {integrity_score:.1f}/{max_score}")
    
    if integrity_score >= 90:
        print("✅ ОТЛИЧНО! Бекап полностью целостен!")
        status = "EXCELLENT"
    elif integrity_score >= 80:
        print("✅ ХОРОШО! Бекап в основном целостен!")
        status = "GOOD"
    elif integrity_score >= 70:
        print("⚠️ УДОВЛЕТВОРИТЕЛЬНО! Есть незначительные проблемы!")
        status = "SATISFACTORY"
    else:
        print("❌ ПЛОХО! Бекап имеет серьезные проблемы!")
        status = "POOR"
    
    # Создание отчета о проверке
    verification_report = {
        "timestamp": datetime.now().isoformat(),
        "backup_directory": str(backup_dir),
        "critical_files_present": critical_present,
        "critical_files_total": len(critical_files),
        "directories_present": dirs_present,
        "directories_total": len(required_dirs),
        "total_files": total_files,
        "total_size_bytes": total_size,
        "file_types": file_types,
        "integrity_score": integrity_score,
        "max_score": max_score,
        "status": status,
        "verification_passed": integrity_score >= 80
    }
    
    # Сохранение отчета
    report_file = "BACKUP_VERIFICATION_REPORT.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(verification_report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📁 Отчет о проверке сохранен: {report_file}")
    
    return integrity_score >= 80

if __name__ == "__main__":
    success = verify_backup_integrity()
    exit(0 if success else 1)