#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏥 ПРОВЕРКА РАБОТОСПОСОБНОСТИ СИСТЕМЫ
====================================

Проверка работоспособности всех активных компонентов
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

def system_health_check():
    """Проверка работоспособности системы"""
    
    print("🏥 ПРОВЕРКА РАБОТОСПОСОБНОСТИ СИСТЕМЫ")
    print("=" * 50)
    
    # Загружаем SFM реестр
    sfm_path = "data/sfm/function_registry.json"
    
    if not os.path.exists(sfm_path):
        print(f"❌ Файл {sfm_path} не найден!")
        return False
    
    with open(sfm_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    functions = data.get('functions', {})
    
    # Анализируем активные функции
    active_functions = []
    ml_functions = []
    critical_functions = []
    
    for func_id, func_data in functions.items():
        status = func_data.get('status', 'unknown')
        is_critical = func_data.get('is_critical', False)
        
        if status == 'active':
            active_functions.append(func_id)
            
            if is_critical:
                critical_functions.append(func_id)
            
            # Проверяем ML функции
            if ('ml' in func_id.lower() or 'ai' in func_id.lower() or 
                'model' in func_id.lower() or 'analyzer' in func_id.lower()):
                ml_functions.append(func_id)
    
    print(f"📊 СТАТИСТИКА:")
    print(f"   Всего функций: {len(functions)}")
    print(f"   Активных функций: {len(active_functions)}")
    print(f"   Критических активных: {len(critical_functions)}")
    print(f"   ML функций активных: {len(ml_functions)}")
    print()
    
    # Проверяем ключевые компоненты
    key_components = {
        'core_base': 'Ядро системы',
        'database': 'База данных',
        'authentication': 'Аутентификация',
        'safe_function_manager': 'Менеджер функций',
        'enhanced_alerting_system': 'Система оповещений',
        'emergencymlanalyzer': 'ML анализатор',
        'mobile_security_agent': 'Мобильный агент',
        'threat_detection_agent': 'Агент обнаружения угроз'
    }
    
    print("🔍 ПРОВЕРКА КЛЮЧЕВЫХ КОМПОНЕНТОВ:")
    all_ok = True
    
    for component, description in key_components.items():
        if component in functions:
            func_data = functions[component]
            status = func_data.get('status', 'unknown')
            is_critical = func_data.get('is_critical', False)
            
            if status == 'active':
                critical_mark = " 🔴" if is_critical else ""
                print(f"   ✅ {description} ({component}){critical_mark}")
            else:
                print(f"   ❌ {description} ({component}) - {status}")
                all_ok = False
        else:
            print(f"   ⚠️  {description} ({component}) - не найден")
            all_ok = False
    
    print()
    
    # Проверяем ML компоненты
    print("🤖 ПРОВЕРКА ML КОМПОНЕНТОВ:")
    ml_ok = True
    
    for ml_func in ml_functions[:10]:  # Показываем первые 10
        func_data = functions.get(ml_func, {})
        status = func_data.get('status', 'unknown')
        
        if status == 'active':
            print(f"   ✅ {ml_func}")
        else:
            print(f"   ❌ {ml_func} - {status}")
            ml_ok = False
    
    if len(ml_functions) > 10:
        print(f"   ... и еще {len(ml_functions) - 10} ML функций")
    
    print()
    
    # Проверяем спящие функции
    sleeping_functions = [f for f in functions.values() if f.get('status') == 'sleeping']
    critical_sleeping = [f for f in sleeping_functions if f.get('is_critical', False)]
    
    print("😴 СПЯЩИЕ ФУНКЦИИ:")
    print(f"   Всего спящих: {len(sleeping_functions)}")
    print(f"   Критических спящих: {len(critical_sleeping)}")
    
    if critical_sleeping:
        print("   ⚠️  ВНИМАНИЕ! Критические функции в спящем режиме:")
        for func in critical_sleeping[:5]:
            print(f"   - {func.get('name', 'Unknown')}")
        all_ok = False
    else:
        print("   ✅ Все критические функции активны")
    
    print()
    
    # Итоговый результат
    if all_ok and ml_ok and len(critical_sleeping) == 0:
        print("🎉 СИСТЕМА РАБОТАЕТ КОРРЕКТНО!")
        print("   ✅ Все критические компоненты активны")
        print("   ✅ ML компоненты работают")
        print("   ✅ Нет критических функций в спящем режиме")
        return True
    else:
        print("⚠️  ОБНАРУЖЕНЫ ПРОБЛЕМЫ!")
        if not all_ok:
            print("   ❌ Некоторые ключевые компоненты неактивны")
        if not ml_ok:
            print("   ❌ Некоторые ML компоненты неактивны")
        if critical_sleeping:
            print("   ❌ Критические функции в спящем режиме")
        return False

if __name__ == "__main__":
    success = system_health_check()
    sys.exit(0 if success else 1)