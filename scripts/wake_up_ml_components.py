#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 ПРОБУЖДЕНИЕ ML КОМПОНЕНТОВ
=============================

Пробуждение всех ML компонентов и AI агентов
"""

import json
import os
from datetime import datetime
from typing import Set

def wake_up_ml_components():
    """Пробуждение всех ML компонентов"""
    
    print("🤖 ПРОБУЖДЕНИЕ ML КОМПОНЕНТОВ")
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
    
    # Находим ML компоненты
    ml_functions = set()
    ai_agent_functions = set()
    bot_ml_functions = set()
    microservice_ml_functions = set()
    
    for func_id, func_data in functions.items():
        # ML функции
        if ('ml' in func_id.lower() or 'analyzer' in func_id.lower() or 
            'model' in func_id.lower() or 'isolation' in func_id.lower()):
            ml_functions.add(func_id)
        
        # AI агенты
        if func_id.startswith('ai_agent_'):
            ai_agent_functions.add(func_id)
        
        # Боты с ML
        if (func_id.startswith('bot_') and 
            ('ml' in func_id.lower() or 'ai' in func_id.lower() or 
             'analyzer' in func_id.lower())):
            bot_ml_functions.add(func_id)
        
        # Микросервисы с ML
        if (func_id.startswith('microservice_') and 
            ('ml' in func_id.lower() or 'model' in func_id.lower() or 
             'analyzer' in func_id.lower() or 'isolation' in func_id.lower())):
            microservice_ml_functions.add(func_id)
    
    print(f"🔬 ML функций найдено: {len(ml_functions)}")
    print(f"🤖 AI агентов найдено: {len(ai_agent_functions)}")
    print(f"🤖 Ботов с ML найдено: {len(bot_ml_functions)}")
    print(f"⚙️  Микросервисов с ML найдено: {len(microservice_ml_functions)}")
    
    # Объединяем все ML компоненты
    all_ml_components = ml_functions | ai_agent_functions | bot_ml_functions | microservice_ml_functions
    
    print(f"\n📋 ВСЕГО ML КОМПОНЕНТОВ ДЛЯ ПРОБУЖДЕНИЯ: {len(all_ml_components)}")
    
    # Пробуждаем ML компоненты
    woken_up = 0
    for func_id in all_ml_components:
        if func_id in functions:
            functions[func_id]['status'] = 'active'
            functions[func_id]['wake_time'] = datetime.now().isoformat()
            functions[func_id]['ml_component_wake'] = True
            woken_up += 1
            print(f"✅ {func_id} - пробужден")
    
    # Сохраняем обновленный реестр
    data['functions'] = functions
    data['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data['ml_components_woken'] = woken_up
    
    with open(sfm_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n🎯 РЕЗУЛЬТАТ:")
    print(f"   Пробуждено ML компонентов: {woken_up}")
    print(f"   SFM реестр обновлен: {sfm_path}")
    
    return woken_up

if __name__ == "__main__":
    wake_up_ml_components()