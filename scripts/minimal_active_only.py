#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 МИНИМАЛЬНАЯ АКТИВНАЯ СИСТЕМА
===============================

Оставляем активными только:
- Ядро системы (core_base, database, authentication)
- ML компоненты (AI агенты, микросервисы, боты)
- Управление системой (SleepModeManager, SafeFunctionManager)
"""

import json
import os
from datetime import datetime
from typing import Set

def minimal_active_system():
    """Создание минимальной активной системы"""
    
    print("🎯 СОЗДАНИЕ МИНИМАЛЬНОЙ АКТИВНОЙ СИСТЕМЫ")
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
    
    # Определяем функции для активации
    active_functions: Set[str] = set()
    
    # 1. ЯДРО СИСТЕМЫ
    core_functions = {
        'core_base', 'service_base', 'security_base', 
        'database', 'authentication'
    }
    active_functions.update(core_functions)
    print(f"🏗️  Ядро системы: {len(core_functions)} функций")
    
    # 2. ML КОМПОНЕНТЫ - AI АГЕНТЫ
    ai_agent_functions = set()
    for func_id in functions.keys():
        if func_id.startswith('ai_agent_') and 'ml' in func_id.lower():
            ai_agent_functions.add(func_id)
    active_functions.update(ai_agent_functions)
    print(f"🤖 AI агенты с ML: {len(ai_agent_functions)} функций")
    
    # 3. ML КОМПОНЕНТЫ - МИКРОСЕРВИСЫ
    microservice_ml_functions = set()
    for func_id in functions.keys():
        if (func_id.startswith('microservice_') and 
            ('ml' in func_id.lower() or 'model' in func_id.lower() or 
             'analyzer' in func_id.lower() or 'isolation' in func_id.lower())):
            microservice_ml_functions.add(func_id)
    active_functions.update(microservice_ml_functions)
    print(f"⚙️  Микросервисы с ML: {len(microservice_ml_functions)} функций")
    
    # 4. ML КОМПОНЕНТЫ - БОТЫ
    bot_ml_functions = set()
    for func_id in functions.keys():
        if (func_id.startswith('bot_') and 
            ('ml' in func_id.lower() or 'ai' in func_id.lower() or 
             'analyzer' in func_id.lower())):
            bot_ml_functions.add(func_id)
    active_functions.update(bot_ml_functions)
    print(f"🤖 Боты с ML: {len(bot_ml_functions)} функций")
    
    # 5. УПРАВЛЕНИЕ СИСТЕМОЙ
    management_functions = {
        'sleep_mode_manager', 'safe_function_manager', 'enhanced_safe_function_manager',
        'all_bots_sleep_manager', 'safe_sleep_mode_optimizer'
    }
    active_functions.update(management_functions)
    print(f"🎛️  Управление системой: {len(management_functions)} функций")
    
    # 6. КРИТИЧЕСКИЕ ML АНАЛИЗАТОРЫ
    ml_analyzer_functions = set()
    for func_id in functions.keys():
        if ('ml' in func_id.lower() and 'analyzer' in func_id.lower()):
            ml_analyzer_functions.add(func_id)
    active_functions.update(ml_analyzer_functions)
    print(f"🔬 ML анализаторы: {len(ml_analyzer_functions)} функций")
    
    # 7. СИСТЕМЫ ОПОВЕЩЕНИЙ
    alerting_functions = {
        'enhanced_alerting_system', 'advanced_alerting_system',
        'emergency_notification_manager'
    }
    active_functions.update(alerting_functions)
    print(f"🚨 Системы оповещений: {len(alerting_functions)} функций")
    
    print(f"\n📋 ИТОГО ДЛЯ АКТИВАЦИИ: {len(active_functions)} функций")
    
    # Переводим все функции в спящий режим
    sleeping_count = 0
    active_count = 0
    
    for func_id, func_data in functions.items():
        if func_id in active_functions:
            func_data['status'] = 'active'
            func_data['wake_time'] = datetime.now().isoformat()
            func_data['minimal_system_active'] = True
            active_count += 1
            print(f"✅ {func_id} - активирована")
        else:
            func_data['status'] = 'sleeping'
            func_data['sleep_time'] = datetime.now().isoformat()
            func_data['minimal_system_sleep'] = True
            sleeping_count += 1
    
    # Сохраняем обновленный реестр
    data['functions'] = functions
    data['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data['minimal_system_mode'] = True
    data['active_functions_count'] = active_count
    data['sleeping_functions_count'] = sleeping_count
    
    with open(sfm_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n🎯 РЕЗУЛЬТАТ:")
    print(f"   Активировано: {active_count}")
    print(f"   Переведено в сон: {sleeping_count}")
    print(f"   SFM реестр обновлен: {sfm_path}")
    
    # Создаем отчет
    report = {
        "timestamp": datetime.now().isoformat(),
        "minimal_system_mode": True,
        "total_functions": total_functions,
        "active_functions": list(active_functions),
        "active_count": active_count,
        "sleeping_count": sleeping_count,
        "core_functions": list(core_functions),
        "ai_agent_functions": list(ai_agent_functions),
        "microservice_ml_functions": list(microservice_ml_functions),
        "bot_ml_functions": list(bot_ml_functions),
        "management_functions": list(management_functions),
        "ml_analyzer_functions": list(ml_analyzer_functions),
        "alerting_functions": list(alerting_functions)
    }
    
    report_path = f"logs/minimal_system_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs("logs", exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"📋 Отчет сохранен: {report_path}")
    
    return active_count, sleeping_count

if __name__ == "__main__":
    minimal_active_system()