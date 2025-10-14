#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 ПРОВЕРКА РЕАЛЬНОГО СТАТУСА СИСТЕМЫ
====================================

Анализ реального состояния функций в SFM
"""

import json
import os
from collections import Counter
from datetime import datetime

def check_real_status():
    """Проверка реального статуса системы"""
    
    print("🔍 ПРОВЕРКА РЕАЛЬНОГО СТАТУСА СИСТЕМЫ")
    print("=" * 50)
    
    # Загружаем SFM реестр
    sfm_path = "data/sfm/function_registry.json"
    
    if not os.path.exists(sfm_path):
        print(f"❌ Файл {sfm_path} не найден!")
        return
    
    with open(sfm_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    functions = data.get('functions', {})
    total_functions = len(functions)
    
    print(f"📊 ОБЩАЯ СТАТИСТИКА:")
    print(f"   Всего функций в реестре: {total_functions}")
    print()
    
    # Анализ статусов
    statuses = Counter()
    critical_statuses = Counter()
    security_levels = Counter()
    function_types = Counter()
    
    active_functions = []
    sleeping_functions = []
    critical_functions = []
    ml_functions = []
    
    for func_id, func_data in functions.items():
        status = func_data.get('status', 'unknown')
        is_critical = func_data.get('is_critical', False)
        security_level = func_data.get('security_level', 'unknown')
        function_type = func_data.get('function_type', 'unknown')
        
        statuses[status] += 1
        security_levels[security_level] += 1
        function_types[function_type] += 1
        
        if is_critical:
            critical_statuses[status] += 1
            critical_functions.append(func_id)
        
        if status == 'active':
            active_functions.append(func_id)
        elif status == 'sleeping':
            sleeping_functions.append(func_id)
        
        # Проверяем ML функции
        if 'ml' in func_id.lower() or 'ai' in func_id.lower() or 'model' in func_id.lower():
            ml_functions.append(func_id)
    
    print("📈 СТАТУСЫ ФУНКЦИЙ:")
    for status, count in statuses.items():
        percentage = (count / total_functions) * 100
        print(f"   {status.upper()}: {count} ({percentage:.1f}%)")
    
    print()
    print("🔒 КРИТИЧЕСКИЕ ФУНКЦИИ:")
    for status, count in critical_statuses.items():
        percentage = (count / len(critical_functions)) * 100 if critical_functions else 0
        print(f"   {status.upper()}: {count} ({percentage:.1f}%)")
    
    print()
    print("🛡️ УРОВНИ БЕЗОПАСНОСТИ:")
    for level, count in security_levels.items():
        percentage = (count / total_functions) * 100
        print(f"   {level.upper()}: {count} ({percentage:.1f}%)")
    
    print()
    print("⚙️ ТИПЫ ФУНКЦИЙ:")
    for ftype, count in function_types.items():
        percentage = (count / total_functions) * 100
        print(f"   {ftype.upper()}: {count} ({percentage:.1f}%)")
    
    print()
    print("🤖 ML ФУНКЦИИ:")
    print(f"   Найдено ML функций: {len(ml_functions)}")
    for ml_func in ml_functions[:10]:  # Показываем первые 10
        func_data = functions.get(ml_func, {})
        status = func_data.get('status', 'unknown')
        print(f"   - {ml_func}: {status}")
    
    print()
    print("🎯 КРИТИЧЕСКИЕ ФУНКЦИИ В СПЯЩЕМ РЕЖИМЕ:")
    critical_sleeping = [f for f in critical_functions if functions.get(f, {}).get('status') == 'sleeping']
    print(f"   Критических в спящем режиме: {len(critical_sleeping)}")
    
    if critical_sleeping:
        print("   ⚠️  ВНИМАНИЕ! Критические функции в спящем режиме:")
        for func in critical_sleeping[:10]:  # Показываем первые 10
            print(f"   - {func}")
    
    print()
    print("✅ АКТИВНЫЕ ФУНКЦИИ:")
    print(f"   Активных функций: {len(active_functions)}")
    for func in active_functions[:10]:  # Показываем первые 10
        func_data = functions.get(func, {})
        is_critical = func_data.get('is_critical', False)
        critical_mark = " 🔴" if is_critical else ""
        print(f"   - {func}{critical_mark}")
    
    print()
    print("😴 СПЯЩИЕ ФУНКЦИИ:")
    print(f"   Спящих функций: {len(sleeping_functions)}")
    
    # Сохраняем детальный отчет
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_functions": total_functions,
        "statuses": dict(statuses),
        "critical_statuses": dict(critical_statuses),
        "security_levels": dict(security_levels),
        "function_types": dict(function_types),
        "active_functions": active_functions,
        "sleeping_functions": sleeping_functions,
        "critical_functions": critical_functions,
        "ml_functions": ml_functions,
        "critical_sleeping": critical_sleeping
    }
    
    report_path = f"logs/real_status_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs("logs", exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"📋 Детальный отчет сохранен: {report_path}")
    
    return report

if __name__ == "__main__":
    check_real_status()