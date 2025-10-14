#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализ качества файлов в бэкапах для поиска лучших версий
"""

import os
import sys
import subprocess
from datetime import datetime

def analyze_backup_quality():
    """Анализ качества файлов в бэкапах"""
    print("🔍 АНАЛИЗ КАЧЕСТВА ФАЙЛОВ В БЭКАПАХ")
    print("=" * 80)
    print(f"📅 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Проблемные файлы из текущей системы
    problematic_files = [
        "security/safe_function_manager.py",
        "security/family/child_protection.py",
        "security/family/elderly_protection.py",
        "security/preliminary/policy_engine.py",
        "security/preliminary/risk_assessment.py",
        "security/preliminary/behavioral_analysis.py",
        "security/preliminary/mfa_service.py",
        "security/preliminary/zero_trust_service.py",
        "security/preliminary/trust_scoring.py",
        "security/preliminary/context_aware_access.py",
        "security/reactive/recovery_service.py",
        "security/microservices/api_gateway.py",
        "security/microservices/load_balancer.py",
        "security/microservices/rate_limiter.py",
        "security/microservices/circuit_breaker.py",
        "security/microservices/user_interface_manager.py",
        "security/ai_agents/monitor_manager.py",
        "security/ai_agents/alert_manager.py",
        "security/ai_agents/report_manager.py",
        "security/ai_agents/analytics_manager.py",
        "security/ai_agents/dashboard_manager.py",
        "security/privacy/universal_privacy_manager.py"
    ]
    
    # Доступные бэкапы
    backups = [
        {
            "name": "ALADDIN_BACKUP_20250908_170629",
            "path": "/Users/sergejhlystov/ALADDIN_BACKUP_20250908_170629",
            "date": "2025-09-08 17:06:29"
        },
        {
            "name": "ALADDIN_CLEAN_BACKUP_20250903_202419",
            "path": "/Users/sergejhlystov/ALADDIN_CLEAN_BACKUP_20250903_202419",
            "date": "2025-09-03 20:24:19"
        },
        {
            "name": "ALADDIN_COMPLETE_BACKUP_20250903_175944",
            "path": "/Users/sergejhlystov/ALADDIN_COMPLETE_BACKUP_20250903_175944",
            "date": "2025-09-03 17:59:44"
        },
        {
            "name": "ALADDIN_FULL_BACKUP_20250903_173136",
            "path": "/Users/sergejhlystov/ALADDIN_FULL_BACKUP_20250903_173136",
            "date": "2025-09-03 17:31:36"
        },
        {
            "name": "ALADDIN_NEW_BACKUP_20250909_170539",
            "path": "/Users/sergejhlystov/ALADDIN_NEW_BACKUP_20250909_170539",
            "date": "2025-09-09 17:05:39"
        },
        {
            "name": "ALADDIN_REFACTORING_BACKUP_20250909_170742",
            "path": "/Users/sergejhlystov/ALADDIN_REFACTORING_BACKUP_20250909_170742",
            "date": "2025-09-09 17:07:42"
        },
        {
            "name": "ALADDIN_REFACTORING_BACKUP_20250909_171503",
            "path": "/Users/sergejhlystov/ALADDIN_REFACTORING_BACKUP_20250909_171503",
            "date": "2025-09-09 17:15:03"
        },
        {
            "name": "ALADDIN_SECURITY_FULL_BACKUP_20250909_122638",
            "path": "/Users/sergejhlystov/ALADDIN_SECURITY_FULL_BACKUP_20250909_122638",
            "date": "2025-09-09 12:26:38"
        },
        {
            "name": "ALADDIN_SECURITY_IDENTICAL_BACKUP_20250906_014537",
            "path": "/Users/sergejhlystov/ALADDIN_SECURITY_IDENTICAL_BACKUP_20250906_014537",
            "date": "2025-09-06 01:45:37"
        }
    ]
    
    # Текущая система
    current_system = {
        "name": "ТЕКУЩАЯ СИСТЕМА",
        "path": "/Users/sergejhlystov/ALADDIN_NEW",
        "date": "2025-09-09 23:30:00"
    }
    
    all_systems = [current_system] + backups
    
    # Результаты анализа
    file_analysis = {}
    
    print("🔍 АНАЛИЗ КАЧЕСТВА ФАЙЛОВ ПО БЭКАПАМ:")
    print("-" * 80)
    
    for file_path in problematic_files:
        print(f"\n📄 {file_path}:")
        file_analysis[file_path] = {}
        
        for system in all_systems:
            full_path = os.path.join(system["path"], file_path)
            
            if os.path.exists(full_path):
                try:
                    result = subprocess.run([
                        'python3', '-m', 'flake8', 
                        '--max-line-length=120',
                        full_path
                    ], capture_output=True, text=True, timeout=30)
                    
                    if result.returncode == 0:
                        issues = 0
                        grade = "A+"
                        desc = "Отлично"
                    else:
                        output = result.stdout
                        lines = output.split('\n')
                        issues = len([l for l in lines if l.strip()])
                        
                        if issues <= 5:
                            grade = "A"
                            desc = "Хорошо"
                        elif issues <= 15:
                            grade = "B"
                            desc = "Удовлетворительно"
                        elif issues <= 30:
                            grade = "C"
                            desc = "Требует улучшения"
                        else:
                            grade = "D"
                            desc = "Критично"
                    
                    file_analysis[file_path][system["name"]] = {
                        "issues": issues,
                        "grade": grade,
                        "description": desc,
                        "path": full_path
                    }
                    
                    print(f"   {system['name']:30} | {grade:2} | {issues:3d} проблем | {desc}")
                    
                except Exception as e:
                    print(f"   {system['name']:30} | ❌ | Ошибка: {str(e)}")
                    file_analysis[file_path][system["name"]] = {
                        "issues": 999,
                        "grade": "ERROR",
                        "description": f"Ошибка: {str(e)}",
                        "path": full_path
                    }
            else:
                print(f"   {system['name']:30} | ❌ | Файл не найден")
                file_analysis[file_path][system["name"]] = {
                    "issues": 999,
                    "grade": "MISSING",
                    "description": "Файл не найден",
                    "path": full_path
                }
    
    # Анализ результатов
    print("\n" + "=" * 80)
    print("📊 РЕКОМЕНДАЦИИ ПО ЗАМЕНЕ ФАЙЛОВ:")
    print("=" * 80)
    
    for file_path in problematic_files:
        print(f"\n📄 {file_path}:")
        print("-" * 60)
        
        # Находим лучшую версию
        best_version = None
        best_issues = 999
        
        for system_name, analysis in file_analysis[file_path].items():
            if analysis["issues"] < best_issues and analysis["grade"] != "ERROR" and analysis["grade"] != "MISSING":
                best_issues = analysis["issues"]
                best_version = system_name
        
        if best_version and best_issues < 999:
            print(f"🏆 ЛУЧШАЯ ВЕРСИЯ: {best_version}")
            print(f"   📊 Качество: {file_analysis[file_path][best_version]['grade']}")
            print(f"   🔍 Проблем: {file_analysis[file_path][best_version]['issues']}")
            print(f"   📁 Путь: {file_analysis[file_path][best_version]['path']}")
            
            # Показываем сравнение с текущей версией
            if "ТЕКУЩАЯ СИСТЕМА" in file_analysis[file_path]:
                current_issues = file_analysis[file_path]["ТЕКУЩАЯ СИСТЕМА"]["issues"]
                improvement = current_issues - best_issues
                if improvement > 0:
                    print(f"   ✅ Улучшение: -{improvement} проблем")
                elif improvement < 0:
                    print(f"   ⚠️  Ухудшение: +{abs(improvement)} проблем")
                else:
                    print(f"   ➡️  Без изменений")
            
            # Команда для замены
            if best_version != "ТЕКУЩАЯ СИСТЕМА":
                source_path = file_analysis[file_path][best_version]["path"]
                target_path = f"/Users/sergejhlystov/ALADDIN_NEW/{file_path}"
                print(f"   🔧 Команда замены:")
                print(f"      cp '{source_path}' '{target_path}'")
        else:
            print("❌ Подходящая версия не найдена")
    
    # Общая статистика
    print("\n" + "=" * 80)
    print("📊 ОБЩАЯ СТАТИСТИКА БЭКАПОВ:")
    print("=" * 80)
    
    backup_stats = {}
    for backup in backups:
        backup_stats[backup["name"]] = {
            "total_files": 0,
            "excellent": 0,
            "good": 0,
            "fair": 0,
            "poor": 0,
            "critical": 0,
            "missing": 0
        }
    
    for file_path in problematic_files:
        for system_name, analysis in file_analysis[file_path].items():
            if system_name in backup_stats:
                backup_stats[system_name]["total_files"] += 1
                
                if analysis["grade"] == "A+":
                    backup_stats[system_name]["excellent"] += 1
                elif analysis["grade"] == "A":
                    backup_stats[system_name]["good"] += 1
                elif analysis["grade"] == "B":
                    backup_stats[system_name]["fair"] += 1
                elif analysis["grade"] == "C":
                    backup_stats[system_name]["poor"] += 1
                elif analysis["grade"] == "D":
                    backup_stats[system_name]["critical"] += 1
                else:
                    backup_stats[system_name]["missing"] += 1
    
    # Выводим статистику
    for backup_name, stats in backup_stats.items():
        if stats["total_files"] > 0:
            print(f"\n📁 {backup_name}:")
            print(f"   📊 Всего файлов: {stats['total_files']}")
            print(f"   🥇 A+ (Отлично): {stats['excellent']}")
            print(f"   🥈 A  (Хорошо): {stats['good']}")
            print(f"   🥉 B  (Удовлетворительно): {stats['fair']}")
            print(f"   ⚠️  C  (Требует улучшения): {stats['poor']}")
            print(f"   🚨 D  (Критично): {stats['critical']}")
            print(f"   ❌ Отсутствует: {stats['missing']}")
            
            # Оценка бэкапа
            total_issues = stats["critical"] * 4 + stats["poor"] * 3 + stats["fair"] * 2 + stats["good"]
            if total_issues == 0:
                backup_grade = "A+"
            elif total_issues <= 5:
                backup_grade = "A"
            elif total_issues <= 15:
                backup_grade = "B"
            elif total_issues <= 30:
                backup_grade = "C"
            else:
                backup_grade = "D"
            
            print(f"   🎯 Общая оценка: {backup_grade}")
    
    print("\n" + "=" * 80)
    print("✅ АНАЛИЗ БЭКАПОВ ЗАВЕРШЕН!")
    print("=" * 80)
    print()
    print("💡 РЕКОМЕНДАЦИИ:")
    print("1. Используйте лучшие версии файлов из бэкапов")
    print("2. Замените проблемные файлы командами cp")
    print("3. Проверьте качество после замены")
    print("4. Создайте новый бэкап после улучшений")

if __name__ == "__main__":
    analyze_backup_quality()