#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

registry_path = '/opt/aladdin-backend/data/sfm/function_registry.json'
with open(registry_path, 'r', encoding='utf-8') as f:
    registry = json.load(f)

new_agents = [
    'location_bubble_agent',
    'personal_data_cleanup_agent',
    'roadside_assistance_agent',
    'ai_categories_agent',
    'anti_tracker_agent',
    'crash_detection_agent',
    'dark_web_monitoring_agent',
    'driving_reports_agent',
    'russian_identity_theft_protection_agent'
]

print('=' * 80)
print('ПРОВЕРКА 9 НОВЫХ АГЕНТОВ')
print('=' * 80)
print('')

# Проверяем в структуре 'agents'
if 'agents' in registry:
    agents_list = registry['agents']
    found = []
    for agent in agents_list:
        name = agent.get('name', '')
        if name in new_agents:
            status = agent.get('status', 'unknown')
            funcs = len(agent.get('functions', []))
            endpoints = len(agent.get('api_endpoints', []))
            found.append((name, status, funcs, endpoints))
    
    print('✅ НАЙДЕННЫЕ АГЕНТЫ В СТРУКТУРЕ "agents":')
    for name, status, funcs, endpoints in found:
        print(f'   ✅ {name} - Статус: {status}, Функций: {funcs}, Endpoints: {endpoints}')
    print('')
    print(f'ИТОГО: {len(found)} из {len(new_agents)} найдено')
else:
    print('Структура "agents" не найдена')

# Проверяем в структуре 'functions'
functions_dict = registry.get('functions', {})
found_in_functions = []
for agent_name in new_agents:
    for func_id, func_data in functions_dict.items():
        name = func_data.get('name', '')
        if agent_name in func_id.lower() or agent_name.replace('_', '') in func_id.lower():
            status = func_data.get('status', 'unknown')
            found_in_functions.append((agent_name, func_id, status))
            break

if found_in_functions:
    print('')
    print('✅ НАЙДЕННЫЕ АГЕНТЫ В СТРУКТУРЕ "functions":')
    for agent_name, func_id, status in found_in_functions:
        print(f'   ✅ {agent_name} - ID: {func_id}, Статус: {status}')
