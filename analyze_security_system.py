#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Глубокий анализ системы безопасности ALADDIN
Подсчет всех агентов, менеджеров, ботов и функций
"""

import json
import os
import re
from pathlib import Path

def count_functions_in_file(filepath):
    """Подсчет функций в Python файле"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        # Ищем определения функций и методов
        function_pattern = r'^\s*(async\s+)?def\s+\w+'
        functions = re.findall(function_pattern, content, re.MULTILINE)
        return len(functions)
    except Exception as e:
        return 0

def count_functions_in_directory(directory, pattern):
    """Подсчет функций во всех файлах директории"""
    total = 0
    files = []
    for root, dirs, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith('.py') and pattern in filename:
                filepath = os.path.join(root, filename)
                func_count = count_functions_in_file(filepath)
                total += func_count
                if func_count > 0:
                    files.append((filename, func_count))
    return total, files

def analyze_sfm_registry(registry_path):
    """Анализ SFM registry"""
    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    agents = registry.get('agents', [])
    total_functions = 0
    total_endpoints = 0
    
    print('=== АНАЛИЗ SFM REGISTRY ===')
    print(f'Всего агентов в registry: {len(agents)}')
    print('')
    
    for agent in agents:
        name = agent.get('name', 'N/A')
        funcs = agent.get('functions', [])
        endpoints = agent.get('api_endpoints', [])
        total_functions += len(funcs)
        total_endpoints += len(endpoints)
        print(f'{name}:')
        print(f'  - Функций: {len(funcs)}')
        print(f'  - Endpoints: {len(endpoints)}')
    
    print('')
    print(f'ИТОГО В SFM REGISTRY:')
    print(f'  - Функций: {total_functions}')
    print(f'  - Endpoints: {total_endpoints}')
    print('')
    
    return agents, total_functions, total_endpoints

def main():
    security_dir = '/opt/aladdin-backend/security'
    registry_path = '/opt/aladdin-backend/data/sfm/function_registry.json'
    
    print('=' * 60)
    print('ГЛУБОКИЙ АНАЛИЗ СИСТЕМЫ БЕЗОПАСНОСТИ ALADDIN')
    print('=' * 60)
    print('')
    
    # Анализ SFM registry
    agents_registry, funcs_registry, endpoints_registry = analyze_sfm_registry(registry_path)
    
    # Подсчет файлов
    print('=== ПОДСЧЕТ ФАЙЛОВ НА СЕРВЕРЕ ===')
    
    agent_files = []
    manager_files = []
    bot_files = []
    
    for root, dirs, filenames in os.walk(security_dir):
        for filename in filenames:
            if filename.endswith('_agent.py'):
                agent_files.append(os.path.join(root, filename))
            elif filename.endswith('_manager.py'):
                manager_files.append(os.path.join(root, filename))
            elif filename.endswith('_bot.py'):
                bot_files.append(os.path.join(root, filename))
    
    print(f'Агенты (файлы): {len(agent_files)}')
    print(f'Менеджеры (файлы): {len(manager_files)}')
    print(f'Боты (файлы): {len(bot_files)}')
    print('')
    
    # Подсчет функций
    print('=== ПОДСЧЕТ ФУНКЦИЙ ===')
    
    agents_total, agents_list = count_functions_in_directory(security_dir, '_agent.py')
    managers_total, managers_list = count_functions_in_directory(security_dir, '_manager.py')
    bots_total, bots_list = count_functions_in_directory(security_dir, '_bot.py')
    
    print(f'🤖 АГЕНТЫ: {agents_total} функций')
    if agents_list:
        print('  Топ-10 агентов по количеству функций:')
        for filename, count in sorted(agents_list, key=lambda x: x[1], reverse=True)[:10]:
            print(f'    - {os.path.basename(filename)}: {count} функций')
    
    print('')
    print(f'👔 МЕНЕДЖЕРЫ: {managers_total} функций')
    if managers_list:
        print('  Топ-10 менеджеров по количеству функций:')
        for filename, count in sorted(managers_list, key=lambda x: x[1], reverse=True)[:10]:
            print(f'    - {os.path.basename(filename)}: {count} функций')
    
    print('')
    print(f'🤖 БОТЫ: {bots_total} функций')
    if bots_list:
        print('  Топ-10 ботов по количеству функций:')
        for filename, count in sorted(bots_list, key=lambda x: x[1], reverse=True)[:10]:
            print(f'    - {os.path.basename(filename)}: {count} функций')
    
    print('')
    print('=' * 60)
    print('ИТОГОВАЯ СТАТИСТИКА')
    print('=' * 60)
    print(f'📁 Компоненты:')
    print(f'  - Агенты: {len(agent_files)} файлов')
    print(f'  - Менеджеры: {len(manager_files)} файлов')
    print(f'  - Боты: {len(bot_files)} файлов')
    print(f'  - Всего компонентов: {len(agent_files) + len(manager_files) + len(bot_files)}')
    print('')
    print(f'📊 Функции:')
    print(f'  - Агенты: {agents_total} функций')
    print(f'  - Менеджеры: {managers_total} функций')
    print(f'  - Боты: {bots_total} функций')
    print(f'  - ВСЕГО ФУНКЦИЙ: {agents_total + managers_total + bots_total}')
    print('')
    print(f'📡 API Endpoints (в SFM registry): {endpoints_registry}')
    print('')
    print(f'📝 Примечание:')
    print(f'  - В SFM registry зарегистрировано только {len(agents_registry)} новых агентов')
    print(f'  - Старые агенты, менеджеры и боты могут иметь функции,')
    print(f'    которые не зарегистрированы в SFM registry')
    print('=' * 60)

if __name__ == "__main__":
    main()
