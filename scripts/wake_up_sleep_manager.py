#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
😴 ПРОБУЖДЕНИЕ МЕНЕДЖЕРА СНА
============================

Пробуждение SleepModeManager и SFM
"""

import json
import os
from datetime import datetime

def wake_up_sleep_manager():
    """Пробуждение менеджера сна и SFM"""
    
    print("😴 ПРОБУЖДЕНИЕ МЕНЕДЖЕРА СНА И SFM")
    print("=" * 50)
    
    # Загружаем SFM реестр
    sfm_path = "data/sfm/function_registry.json"
    
    if not os.path.exists(sfm_path):
        print(f"❌ Файл {sfm_path} не найден!")
        return
    
    with open(sfm_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    functions = data.get('functions', {})
    
    # Находим менеджеры сна и SFM
    sleep_managers = [
        'sleep_mode_manager',
        'all_bots_sleep_manager', 
        'safe_sleep_mode_optimizer',
        'safe_function_manager',
        'enhanced_safe_function_manager',
        'security_safefunctionmanager'
    ]
    
    print(f"🔍 Поиск менеджеров сна и SFM...")
    
    woken_up = 0
    for manager in sleep_managers:
        if manager in functions:
            functions[manager]['status'] = 'active'
            functions[manager]['wake_time'] = datetime.now().isoformat()
            functions[manager]['sleep_manager_wake'] = True
            woken_up += 1
            print(f"✅ {manager} - пробужден")
        else:
            print(f"⚠️  {manager} - не найден")
    
    # Сохраняем обновленный реестр
    data['functions'] = functions
    data['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data['sleep_managers_woken'] = woken_up
    
    with open(sfm_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n🎯 РЕЗУЛЬТАТ:")
    print(f"   Пробуждено менеджеров: {woken_up}")
    print(f"   SFM реестр обновлен: {sfm_path}")
    
    return woken_up

if __name__ == "__main__":
    wake_up_sleep_manager()