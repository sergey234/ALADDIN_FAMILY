#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка статистики SFM для Crash Detection Agent
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, '/opt/aladdin-backend')
registry_path = Path('/opt/aladdin-backend/data/sfm/function_registry.json')

if not registry_path.exists():
    print('❌ Registry не найден')
    sys.exit(1)

with open(registry_path, 'r', encoding='utf-8') as f:
    registry = json.load(f)

# Обработка разных форматов registry
if isinstance(registry, list):
    agents = registry
elif isinstance(registry, dict):
    # Исключаем служебные ключи
    agents = {k: v for k, v in registry.items() 
              if k not in ['functions', 'handlers', 'last_updated'] 
              and isinstance(v, dict) and 'functions' in v}
    agents = list(agents.values())
else:
    agents = []

total_agents = len(agents)
total_functions = 0
total_endpoints = 0
agent_details = []

for agent in agents:
    if isinstance(agent, dict):
        agent_name = agent.get('name', 'unknown')
        functions = agent.get('functions', [])
        endpoints = agent.get('api_endpoints', [])
        func_count = len(functions)
        endpoint_count = len(endpoints)
        total_functions += func_count
        total_endpoints += endpoint_count
        agent_details.append((agent_name, func_count, endpoint_count))

print('=' * 80)
print('📊 СТАТИСТИКА SFM (ВСЕ АГЕНТЫ):')
print('=' * 80)
print(f'Всего агентов: {total_agents}')
print(f'Всего функций: {total_functions}')
print(f'Всего API endpoints: {total_endpoints}')
print()
print('Детализация по агентам:')
agent_details.sort(key=lambda x: x[1], reverse=True)
for name, func_count, endpoint_count in agent_details:
    print(f'  • {name}: {func_count} функций, {endpoint_count} endpoints')
print('=' * 80)

# Проверка наличия crash_detection_agent
crash_agent = next((a for a in agents if isinstance(a, dict) and a.get('name') == 'crash_detection_agent'), None)
if crash_agent:
    print('✅ Crash Detection Agent зарегистрирован в SFM')
    print(f'   Функций: {len(crash_agent.get("functions", []))}')
    print(f'   Endpoints: {len(crash_agent.get("api_endpoints", []))}')
else:
    print('❌ Crash Detection Agent НЕ найден в SFM')
print('=' * 80)
