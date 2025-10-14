#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📍 ОТЧЕТ О РАСПОЛОЖЕНИИ КОМПОНЕНТОВ
===================================

Анализ расположения активных и спящих компонентов
"""

import json
import os
from datetime import datetime
from collections import defaultdict

def component_location_report():
    """Отчет о расположении компонентов"""
    
    print("📍 ОТЧЕТ О РАСПОЛОЖЕНИИ КОМПОНЕНТОВ")
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
    ml_components = []
    ai_agents = []
    bots = []
    microservices = []
    managers = []
    
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
            'is_critical': func_data.get('is_critical', False)
        }
        
        if status == 'active':
            active_components.append(component_info)
        else:
            sleeping_components.append(component_info)
        
        # Категоризация
        if 'ml' in func_id.lower() or 'analyzer' in func_id.lower():
            ml_components.append(component_info)
        
        if func_id.startswith('ai_agent_'):
            ai_agents.append(component_info)
        
        if func_id.startswith('bot_'):
            bots.append(component_info)
        
        if func_id.startswith('microservice_'):
            microservices.append(component_info)
        
        if 'manager' in func_id.lower():
            managers.append(component_info)
    
    print(f"📊 ОБЩАЯ СТАТИСТИКА:")
    print(f"   Всего компонентов: {len(functions)}")
    print(f"   Активных: {len(active_components)}")
    print(f"   Спящих: {len(sleeping_components)}")
    print()
    
    # Активные компоненты
    print("✅ АКТИВНЫЕ КОМПОНЕНТЫ:")
    print(f"   Всего активных: {len(active_components)}")
    
    # Группируем по типам
    active_by_type = defaultdict(list)
    for comp in active_components:
        active_by_type[comp['type']].append(comp)
    
    for comp_type, comps in active_by_type.items():
        print(f"\n   📁 {comp_type.upper()} ({len(comps)} компонентов):")
        for comp in comps[:5]:  # Показываем первые 5
            critical_mark = " 🔴" if comp['is_critical'] else ""
            print(f"      ✅ {comp['name']} ({comp['id']}){critical_mark}")
            print(f"         📂 Путь: {comp['file_path']}")
        if len(comps) > 5:
            print(f"      ... и еще {len(comps) - 5} компонентов")
    
    # ML компоненты
    print(f"\n🤖 ML КОМПОНЕНТЫ:")
    print(f"   Всего ML: {len(ml_components)}")
    ml_active = [c for c in ml_components if c['status'] == 'active']
    ml_sleeping = [c for c in ml_components if c['status'] == 'sleeping']
    print(f"   Активных ML: {len(ml_active)}")
    print(f"   Спящих ML: {len(ml_sleeping)}")
    
    print(f"\n   🔬 АКТИВНЫЕ ML КОМПОНЕНТЫ:")
    for comp in ml_active[:10]:
        print(f"      ✅ {comp['name']} ({comp['id']})")
        print(f"         📂 Путь: {comp['file_path']}")
    
    # AI агенты
    print(f"\n🤖 AI АГЕНТЫ:")
    print(f"   Всего AI агентов: {len(ai_agents)}")
    ai_active = [c for c in ai_agents if c['status'] == 'active']
    ai_sleeping = [c for c in ai_agents if c['status'] == 'sleeping']
    print(f"   Активных AI агентов: {len(ai_active)}")
    print(f"   Спящих AI агентов: {len(ai_sleeping)}")
    
    # Боты
    print(f"\n🤖 БОТЫ:")
    print(f"   Всего ботов: {len(bots)}")
    bot_active = [c for c in bots if c['status'] == 'active']
    bot_sleeping = [c for c in bots if c['status'] == 'sleeping']
    print(f"   Активных ботов: {len(bot_active)}")
    print(f"   Спящих ботов: {len(bot_sleeping)}")
    
    # Микросервисы
    print(f"\n⚙️  МИКРОСЕРВИСЫ:")
    print(f"   Всего микросервисов: {len(microservices)}")
    micro_active = [c for c in microservices if c['status'] == 'active']
    micro_sleeping = [c for c in microservices if c['status'] == 'sleeping']
    print(f"   Активных микросервисов: {len(micro_active)}")
    print(f"   Спящих микросервисов: {len(micro_sleeping)}")
    
    # Менеджеры
    print(f"\n🎛️  МЕНЕДЖЕРЫ:")
    print(f"   Всего менеджеров: {len(managers)}")
    manager_active = [c for c in managers if c['status'] == 'active']
    manager_sleeping = [c for c in managers if c['status'] == 'sleeping']
    print(f"   Активных менеджеров: {len(manager_active)}")
    print(f"   Спящих менеджеров: {len(manager_sleeping)}")
    
    # Пути к файлам
    print(f"\n📂 ОСНОВНЫЕ ПУТИ К ФАЙЛАМ:")
    print(f"   SFM реестр: {sfm_path}")
    print(f"   Ядро системы: core/")
    print(f"   Безопасность: security/")
    print(f"   AI агенты: security/ai_agents/")
    print(f"   Боты: security/bots/")
    print(f"   Микросервисы: security/microservices/")
    print(f"   Конфигурация: config/")
    print(f"   Логи: logs/")
    print(f"   Скрипты: scripts/")
    
    # Создаем детальный отчет
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_components": len(functions),
        "active_components": active_components,
        "sleeping_components": sleeping_components,
        "ml_components": ml_components,
        "ai_agents": ai_agents,
        "bots": bots,
        "microservices": microservices,
        "managers": managers,
        "statistics": {
            "active_count": len(active_components),
            "sleeping_count": len(sleeping_components),
            "ml_active": len(ml_active),
            "ml_sleeping": len(ml_sleeping),
            "ai_active": len(ai_active),
            "ai_sleeping": len(ai_sleeping),
            "bot_active": len(bot_active),
            "bot_sleeping": len(bot_sleeping),
            "micro_active": len(micro_active),
            "micro_sleeping": len(micro_sleeping),
            "manager_active": len(manager_active),
            "manager_sleeping": len(manager_sleeping)
        }
    }
    
    report_path = f"logs/component_location_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs("logs", exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📋 Детальный отчет сохранен: {report_path}")
    
    return report

if __name__ == "__main__":
    component_location_report()