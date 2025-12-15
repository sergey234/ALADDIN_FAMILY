#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import json

def get_functions_from_file(filepath):
    """Извлекает список функций из Python файла"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Ищем определения функций
        function_pattern = r'^\s*(?:async\s+)?def\s+(\w+)\s*\('
        functions = re.findall(function_pattern, content, re.MULTILINE)
        
        # Фильтруем приватные функции (начинающиеся с _)
        public_functions = [f for f in functions if not f.startswith('_')]
        
        return public_functions[:15]  # Берем первые 15 функций
    except Exception as e:
        return []

def analyze_component(filepath):
    """Анализирует компонент и возвращает его функции"""
    filename = os.path.basename(filepath)
    functions = get_functions_from_file(filepath)
    return filename, functions

security_dir = '/opt/aladdin-backend/security'

print('=' * 80)
print('ВСЕ АГЕНТЫ, МЕНЕДЖЕРЫ И БОТЫ С ОСНОВНЫМИ ФУНКЦИЯМИ')
print('=' * 80)
print('')

# Агенты
agent_files = []
for root, dirs, filenames in os.walk(security_dir):
    for filename in filenames:
        if filename.endswith('_agent.py'):
            filepath = os.path.join(root, filename)
            agent_files.append(filepath)

print('🤖 АГЕНТЫ (29 файлов):')
print('-' * 80)
agents_data = []
for filepath in sorted(agent_files):
    filename, functions = analyze_component(filepath)
    agents_data.append((filename, functions))
    print(f'\n{filename}:')
    for i, func in enumerate(functions[:10], 1):
        print(f'  {i}. {func}')

print('')
print('=' * 80)
print('👔 МЕНЕДЖЕРЫ (57 файлов):')
print('-' * 80)
managers_data = []
manager_files = []
for root, dirs, filenames in os.walk(security_dir):
    for filename in filenames:
        if filename.endswith('_manager.py'):
            filepath = os.path.join(root, filename)
            manager_files.append(filepath)

for filepath in sorted(manager_files):
    filename, functions = analyze_component(filepath)
    managers_data.append((filename, functions))
    print(f'\n{filename}:')
    for i, func in enumerate(functions[:10], 1):
        print(f'  {i}. {func}')

print('')
print('=' * 80)
print('🤖 БОТЫ (18 файлов):')
print('-' * 80)
bots_data = []
bot_files = []
for root, dirs, filenames in os.walk(security_dir):
    for filename in filenames:
        if filename.endswith('_bot.py'):
            filepath = os.path.join(root, filename)
            bot_files.append(filepath)

for filepath in sorted(bot_files):
    filename, functions = analyze_component(filepath)
    bots_data.append((filename, functions))
    print(f'\n{filename}:')
    for i, func in enumerate(functions[:10], 1):
        print(f'  {i}. {func}')

# Сохраняем в JSON для дальнейшей обработки
output = {
    'agents': [{'name': name, 'functions': funcs} for name, funcs in agents_data],
    'managers': [{'name': name, 'functions': funcs} for name, funcs in managers_data],
    'bots': [{'name': name, 'functions': funcs} for name, funcs in bots_data]
}

with open('/tmp/components_functions.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print('')
print('=' * 80)
print('Данные сохранены в /tmp/components_functions.json')
print('=' * 80)
