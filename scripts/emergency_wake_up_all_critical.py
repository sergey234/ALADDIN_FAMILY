#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚨 ЭКСТРЕННОЕ ПРОБУЖДЕНИЕ ВСЕХ КРИТИЧЕСКИХ ФУНКЦИЙ
=================================================

Пробуждение всех критических функций из спящего режима
"""

import json
import os
from datetime import datetime

def emergency_wake_up_critical():
    """Экстренное пробуждение критических функций"""
    
    print("🚨 ЭКСТРЕННОЕ ПРОБУЖДЕНИЕ КРИТИЧЕСКИХ ФУНКЦИЙ")
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
    
    print(f"📊 Всего функций: {total_functions}")
    
    # Находим критические функции
    critical_functions = []
    for func_id, func_data in functions.items():
        is_critical = func_data.get('is_critical', False)
        if is_critical:
            critical_functions.append(func_id)
    
    print(f"🔴 Критических функций: {len(critical_functions)}")
    
    # Пробуждаем критические функции
    woken_up = 0
    for func_id in critical_functions:
        if func_id in functions:
            functions[func_id]['status'] = 'active'
            functions[func_id]['wake_time'] = datetime.now().isoformat()
            functions[func_id]['emergency_wake_up'] = True
            woken_up += 1
            print(f"✅ {func_id} - пробуждена")
    
    # Сохраняем обновленный реестр
    data['functions'] = functions
    data['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open(sfm_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print()
    print(f"🎯 РЕЗУЛЬТАТ:")
    print(f"   Пробуждено критических функций: {woken_up}")
    print(f"   SFM реестр обновлен: {sfm_path}")
    
    # Проверяем результат
    active_count = sum(1 for f in functions.values() if f.get('status') == 'active')
    sleeping_count = sum(1 for f in functions.values() if f.get('status') == 'sleeping')
    
    print(f"   Активных функций: {active_count}")
    print(f"   Спящих функций: {sleeping_count}")
    
    return woken_up

if __name__ == "__main__":
    emergency_wake_up_critical()