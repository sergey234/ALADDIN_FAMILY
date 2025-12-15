#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Детальный анализ SFM Registry и всех компонентов
"""

import json
import os
import re

def count_functions_in_file(filepath):
    """Подсчет функций в Python файле"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        function_pattern = r'^\s*(async\s+)?def\s+\w+'
        functions = re.findall(function_pattern, content, re.MULTILINE)
        return len(functions)
    except:
        return 0

def main():
    print('=' * 80)
    print('ДЕТАЛЬНЫЙ АНАЛИЗ SFM REGISTRY И ВСЕХ КОМПОНЕНТОВ')
    print('=' * 80)
    print('')
    
    # 1. Анализ SFM Registry
    registry_path = '/opt/aladdin-backend/data/sfm/function_registry.json'
    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    agents_in_sfm = registry.get('agents', [])
    print('1. ЧТО ЗАРЕГИСТРИРОВАНО В SFM REGISTRY:')
    print('-' * 80)
    print(f'   Агентов: {len(agents_in_sfm)}')
    print('')
    
    sfm_functions = 0
    sfm_endpoints = 0
    registered_names = []
    
    for i, agent in enumerate(agents_in_sfm, 1):
        name = agent.get('name', 'N/A')
        status = agent.get('status', 'unknown')
        funcs = agent.get('functions', [])
        endpoints = agent.get('api_endpoints', [])
        sfm_functions += len(funcs)
        sfm_endpoints += len(endpoints)
        registered_names.append(name)
        
        print(f'   {i}. {name}')
        print(f'      Статус: {status}')
        print(f'      Функций: {len(funcs)}')
        print(f'      Endpoints: {len(endpoints)}')
        print('')
    
    metadata = registry.get('metadata', {})
    print('   МЕТАДАННЫЕ SFM REGISTRY:')
    print(f'      - Всего агентов: {metadata.get("total_agents", 0)}')
    print(f'      - Всего функций: {metadata.get("total_functions", 0)}')
    print(f'      - Всего endpoints: {metadata.get("total_api_endpoints", 0)}')
    print('')
    print(f'   ПОДСЧЕТ ВРУЧНУЮ:')
    print(f'      - Функций: {sfm_functions}')
    print(f'      - Endpoints: {sfm_endpoints}')
    print('')
    
    # 2. Что существует на сервере
    security_dir = '/opt/aladdin-backend/security'
    
    agent_files = []
    manager_files = []
    bot_files = []
    
    for root, dirs, filenames in os.walk(security_dir):
        for filename in filenames:
            if filename.endswith('_agent.py'):
                filepath = os.path.join(root, filename)
                agent_files.append((filepath, filename))
            elif filename.endswith('_manager.py'):
                filepath = os.path.join(root, filename)
                manager_files.append((filepath, filename))
            elif filename.endswith('_bot.py'):
                filepath = os.path.join(root, filename)
                bot_files.append((filepath, filename))
    
    print('=' * 80)
    print('2. ЧТО СУЩЕСТВУЕТ НА СЕРВЕРЕ:')
    print('=' * 80)
    print('')
    
    # Агенты
    print(f'🤖 АГЕНТЫ ({len(agent_files)} файлов):')
    print('-' * 80)
    agents_total = 0
    unregistered_agents = []
    
    for filepath, filename in sorted(agent_files):
        func_count = count_functions_in_file(filepath)
        agents_total += func_count
        agent_name = filename.replace('_agent.py', '').replace('.py', '')
        is_registered = agent_name in registered_names
        status_mark = '✅' if is_registered else '⚠️'
        print(f'   {status_mark} {filename}: {func_count} функций', end='')
        if is_registered:
            print(' [ЗАРЕГИСТРИРОВАН]')
        else:
            print(' [НЕ ЗАРЕГИСТРИРОВАН]')
            unregistered_agents.append((agent_name, func_count))
    
    print(f'   ИТОГО АГЕНТЫ: {agents_total} функций')
    print(f'   Зарегистрировано в SFM: {len(registered_names)} из {len(agent_files)}')
    print('')
    
    # Менеджеры
    print(f'👔 МЕНЕДЖЕРЫ ({len(manager_files)} файлов):')
    print('-' * 80)
    managers_total = 0
    for filepath, filename in sorted(manager_files):
        func_count = count_functions_in_file(filepath)
        managers_total += func_count
        print(f'   {filename}: {func_count} функций')
    print(f'   ИТОГО МЕНЕДЖЕРЫ: {managers_total} функций')
    print('   ⚠️  Менеджеры НЕ регистрируются в SFM (это нормально)')
    print('')
    
    # Боты
    print(f'🤖 БОТЫ ({len(bot_files)} файлов):')
    print('-' * 80)
    bots_total = 0
    for filepath, filename in sorted(bot_files):
        func_count = count_functions_in_file(filepath)
        bots_total += func_count
        print(f'   {filename}: {func_count} функций')
    print(f'   ИТОГО БОТЫ: {bots_total} функций')
    print('   ⚠️  Боты НЕ регистрируются в SFM (это нормально)')
    print('')
    
    # Итоги
    print('=' * 80)
    print('3. ИТОГОВАЯ СТАТИСТИКА:')
    print('=' * 80)
    print('')
    print('   В SFM REGISTRY:')
    print(f'      - Агентов: {len(agents_in_sfm)}')
    print(f'      - Функций: {sfm_functions}')
    print(f'      - Endpoints: {sfm_endpoints}')
    print('')
    print('   НА СЕРВЕРЕ (все компоненты):')
    print(f'      - Агентов: {len(agent_files)} файлов, {agents_total} функций')
    print(f'      - Менеджеров: {len(manager_files)} файлов, {managers_total} функций')
    print(f'      - Ботов: {len(bot_files)} файлов, {bots_total} функций')
    print(f'      - ВСЕГО: {len(agent_files) + len(manager_files) + len(bot_files)} компонентов, {agents_total + managers_total + bots_total} функций')
    print('')
    
    if unregistered_agents:
        print('=' * 80)
        print('4. АГЕНТЫ, НЕ ЗАРЕГИСТРИРОВАННЫЕ В SFM:')
        print('=' * 80)
        for name, func_count in sorted(unregistered_agents):
            print(f'   ⚠️  {name}: {func_count} функций')
        print('')
        print(f'   Всего не зарегистрировано: {len(unregistered_agents)} из {len(agent_files)}')
    else:
        print('=' * 80)
        print('4. ✅ ВСЕ АГЕНТЫ ЗАРЕГИСТРИРОВАНЫ В SFM')
        print('=' * 80)
    
    print('')
    print('=' * 80)
    print('ЗАКЛЮЧЕНИЕ:')
    print('=' * 80)
    print(f'   - В SFM registry зарегистрировано только {len(agents_in_sfm)} новых агентов')
    print(f'   - На сервере существует {len(agent_files)} агентов (включая старые)')
    print(f'   - Менеджеры и боты работают, но не регистрируются в SFM')
    print(f'   - Общая функциональность: {agents_total + managers_total + bots_total} функций')
    print('=' * 80)

if __name__ == "__main__":
    main()
