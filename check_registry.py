#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка регистрации в SFM
"""

import json
from pathlib import Path

registry_path = Path('/opt/aladdin-backend/data/sfm/function_registry.json')

if not registry_path.exists():
    print('❌ Registry не найден!')
    exit(1)

with open(registry_path, 'r', encoding='utf-8') as f:
    registry = json.load(f)

print(f'📊 Тип registry: {type(registry).__name__}')

if isinstance(registry, dict):
    if 'agents' in registry:
        agents = registry['agents']
        print(f'\n📊 Всего агентов: {len(agents)}\n')
        for i, agent in enumerate(agents, 1):
            name = agent.get('name', 'unknown')
            status = agent.get('status', 'unknown')
            funcs = len(agent.get('functions', []))
            print(f'{i}. {name}')
            print(f'   Статус: {status}')
            print(f'   Функций: {funcs}')
            print()
    else:
        print(f'📊 Ключей в словаре: {len(registry)}')
        for key in list(registry.keys())[:10]:
            print(f'  - {key}')
elif isinstance(registry, list):
    print(f'\n📊 Всего записей: {len(registry)}\n')
    for i, item in enumerate(registry, 1):
        if isinstance(item, dict):
            name = item.get('name', 'unknown')
            status = item.get('status', 'unknown')
            funcs = len(item.get('functions', []))
            print(f'{i}. {name}')
            print(f'   Статус: {status}')
            print(f'   Функций: {funcs}')
            print()

# Проверить наш агент
print('\n🔍 Поиск dark_web_monitoring_agent:')
if isinstance(registry, list):
    agent = next((a for a in registry if a.get('name') == 'dark_web_monitoring_agent'), None)
elif isinstance(registry, dict):
    if 'agents' in registry:
        agent = next((a for a in registry['agents'] if a.get('name') == 'dark_web_monitoring_agent'), None)
    else:
        agent = registry.get('dark_web_monitoring_agent')

if agent:
    print('✅ Агент найден!')
    print(f'   Имя: {agent.get("name")}')
    print(f'   Статус: {agent.get("status")}')
    print(f'   Путь: {agent.get("path")}')
    print(f'   Класс: {agent.get("class")}')
    print(f'   Функций: {len(agent.get("functions", []))}')
    
    # Сравнить структуру с первым агентом
    if isinstance(registry, list) and len(registry) > 1:
        sample = registry[0]
    elif isinstance(registry, dict) and 'agents' in registry and len(registry['agents']) > 1:
        sample = registry['agents'][0]
    else:
        sample = None
    
    if sample and sample.get('name') != 'dark_web_monitoring_agent':
        print(f'\n📋 Сравнение со структурой другого агента ({sample.get("name")}):')
        our_keys = set(agent.keys())
        sample_keys = set(sample.keys())
        missing = sample_keys - our_keys
        extra = our_keys - sample_keys
        if missing:
            print(f'   ⚠️  Отсутствуют ключи: {missing}')
        if extra:
            print(f'   ✅ Дополнительные ключи: {extra}')
        if not missing and not extra:
            print('   ✅ Структура идентична!')
else:
    print('❌ Агент НЕ найден!')
