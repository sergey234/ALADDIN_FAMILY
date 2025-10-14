#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📍 ДЕТАЛЬНЫЙ ОТЧЕТ О ПУТЯХ К КОМПОНЕНТАМ
========================================

Полный анализ расположения активных и спящих компонентов
"""

import json
import os
from datetime import datetime
from collections import defaultdict

def detailed_path_report():
    """Детальный отчет о путях к компонентам"""
    
    print("📍 ДЕТАЛЬНЫЙ ОТЧЕТ О ПУТЯХ К КОМПОНЕНТАМ")
    print("=" * 60)
    
    # Загружаем SFM реестр
    sfm_path = "data/sfm/function_registry.json"
    
    if not os.path.exists(sfm_path):
        print(f"❌ Файл {sfm_path} не найден!")
        return
    
    with open(sfm_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    functions = data.get('functions', {})
    
    # Анализируем компоненты
    active_components = []
    sleeping_components = []
    
    for func_id, func_data in functions.items():
        status = func_data.get('status', 'unknown')
        function_type = func_data.get('function_type', 'unknown')
        file_path = func_data.get('file_path', 'unknown')
        
        component_info = {
            'id': func_id,
            'name': func_data.get('name', 'Unknown'),
            'type': function_type,
            'status': status,
            'file_path': file_path,
            'is_critical': func_data.get('is_critical', False),
            'security_level': func_data.get('security_level', 'unknown')
        }
        
        if status == 'active':
            active_components.append(component_info)
        else:
            sleeping_components.append(component_info)
    
    print(f"📊 ТЕКУЩИЙ СТАТУС:")
    print(f"   Всего компонентов: {len(functions)}")
    print(f"   Активных: {len(active_components)} (21.5%)")
    print(f"   Спящих: {len(sleeping_components)} (78.5%)")
    print()
    
    # Группируем активные компоненты по типам
    active_by_type = defaultdict(list)
    for comp in active_components:
        active_by_type[comp['type']].append(comp)
    
    print("✅ АКТИВНЫЕ КОМПОНЕНТЫ (70 компонентов):")
    print("=" * 50)
    
    for comp_type, comps in active_by_type.items():
        print(f"\n📁 {comp_type.upper()} ({len(comps)} компонентов):")
        for comp in comps:
            critical_mark = " 🔴" if comp['is_critical'] else ""
            status_mark = " ✅" if comp['status'] == 'active' else " 😴"
            print(f"   {status_mark} {comp['name']} ({comp['id']}){critical_mark}")
            print(f"      📂 Путь: {comp['file_path']}")
            print(f"      🛡️  Уровень безопасности: {comp['security_level']}")
    
    # Группируем спящие компоненты по типам
    sleeping_by_type = defaultdict(list)
    for comp in sleeping_components:
        sleeping_by_type[comp['type']].append(comp)
    
    print(f"\n😴 СПЯЩИЕ КОМПОНЕНТЫ (256 компонентов):")
    print("=" * 50)
    
    for comp_type, comps in sleeping_by_type.items():
        print(f"\n📁 {comp_type.upper()} ({len(comps)} компонентов):")
        # Показываем только первые 10 для каждого типа
        for comp in comps[:10]:
            critical_mark = " 🔴" if comp['is_critical'] else ""
            status_mark = " ✅" if comp['status'] == 'active' else " 😴"
            print(f"   {status_mark} {comp['name']} ({comp['id']}){critical_mark}")
            print(f"      📂 Путь: {comp['file_path']}")
            print(f"      🛡️  Уровень безопасности: {comp['security_level']}")
        if len(comps) > 10:
            print(f"   ... и еще {len(comps) - 10} компонентов")
    
    # Основные директории
    print(f"\n📂 ОСНОВНЫЕ ДИРЕКТОРИИ СИСТЕМЫ:")
    print("=" * 50)
    
    directories = {
        "SFM реестр": "data/sfm/function_registry.json",
        "Ядро системы": "core/",
        "Безопасность": "security/",
        "AI агенты": "security/ai_agents/",
        "Боты": "security/bots/",
        "Микросервисы": "security/microservices/",
        "Конфигурация": "config/",
        "Логи": "logs/",
        "Скрипты": "scripts/",
        "Тесты": "tests/",
        "Документация": "docs/",
        "Данные": "data/"
    }
    
    for name, path in directories.items():
        if os.path.exists(path):
            print(f"   ✅ {name}: {path}")
        else:
            print(f"   ❌ {name}: {path} (не найден)")
    
    # Файлы отчетов
    print(f"\n📋 ФАЙЛЫ ОТЧЕТОВ СИСТЕМЫ:")
    print("=" * 50)
    
    report_files = {
        "Полный отчет SFM": "ALL_SFM_FUNCTIONS_COMPLETE_REPORT.md",
        "Детальные данные JSON": "ALL_SFM_FUNCTIONS_DETAILED.json",
        "Анализ системы": "COMPREHENSIVE_SYSTEM_ANALYSIS_REPORT.md",
        "Отчет о расположении": "logs/component_location_report_*.json",
        "Проверка статуса": "logs/real_status_check_*.json"
    }
    
    for name, path in report_files.items():
        if "*" in path:
            # Для файлов с маской
            import glob
            files = glob.glob(path)
            if files:
                latest_file = max(files, key=os.path.getctime)
                print(f"   ✅ {name}: {latest_file}")
            else:
                print(f"   ❌ {name}: {path} (не найден)")
        else:
            if os.path.exists(path):
                print(f"   ✅ {name}: {path}")
            else:
                print(f"   ❌ {name}: {path} (не найден)")
    
    # Создаем детальный отчет
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_components": len(functions),
        "active_components": active_components,
        "sleeping_components": sleeping_components,
        "active_by_type": dict(active_by_type),
        "sleeping_by_type": dict(sleeping_by_type),
        "directories": directories,
        "report_files": report_files,
        "statistics": {
            "active_count": len(active_components),
            "sleeping_count": len(sleeping_components),
            "active_percentage": (len(active_components) / len(functions)) * 100,
            "sleeping_percentage": (len(sleeping_components) / len(functions)) * 100
        }
    }
    
    report_path = f"logs/detailed_path_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs("logs", exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📋 Детальный отчет сохранен: {report_path}")
    
    return report

if __name__ == "__main__":
    detailed_path_report()