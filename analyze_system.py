#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ПОЛНЫЙ АНАЛИЗ СИСТЕМЫ ALADDIN
"""

import os
import sys
from collections import defaultdict

def analyze_system():
    print('🔍 ПОЛНОЕ СКАНИРОВАНИЕ СИСТЕМЫ ALADDIN')
    print('=' * 80)

    # Сканируем все Python файлы
    all_py_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                all_py_files.append(os.path.join(root, file))

    print(f'📊 ВСЕГО PYTHON ФАЙЛОВ: {len(all_py_files)}')

    # Группируем по категориям
    categories = {
        'CORE': [],
        'SECURITY': [],
        'AI_AGENTS': [],
        'BOTS': [],
        'MICROSERVICES': [],
        'FAMILY': [],
        'COMPLIANCE': [],
        'PRIVACY': [],
        'REACTIVE': [],
        'ACTIVE': [],
        'PRELIMINARY': [],
        'ORCHESTRATION': [],
        'SCALING': [],
        'TESTS': [],
        'SCRIPTS': [],
        'CONFIG': [],
        'OTHER': []
    }

    for file_path in all_py_files:
        if 'core/' in file_path:
            categories['CORE'].append(file_path)
        elif 'security/ai_agents/' in file_path:
            categories['AI_AGENTS'].append(file_path)
        elif 'security/bots/' in file_path:
            categories['BOTS'].append(file_path)
        elif 'security/microservices/' in file_path:
            categories['MICROSERVICES'].append(file_path)
        elif 'security/family/' in file_path:
            categories['FAMILY'].append(file_path)
        elif 'security/compliance/' in file_path:
            categories['COMPLIANCE'].append(file_path)
        elif 'security/privacy/' in file_path:
            categories['PRIVACY'].append(file_path)
        elif 'security/reactive/' in file_path:
            categories['REACTIVE'].append(file_path)
        elif 'security/active/' in file_path:
            categories['ACTIVE'].append(file_path)
        elif 'security/preliminary/' in file_path:
            categories['PRELIMINARY'].append(file_path)
        elif 'security/orchestration/' in file_path:
            categories['ORCHESTRATION'].append(file_path)
        elif 'security/scaling/' in file_path:
            categories['SCALING'].append(file_path)
        elif 'security/' in file_path:
            categories['SECURITY'].append(file_path)
        elif 'tests/' in file_path:
            categories['TESTS'].append(file_path)
        elif 'scripts/' in file_path:
            categories['SCRIPTS'].append(file_path)
        elif 'config/' in file_path:
            categories['CONFIG'].append(file_path)
        else:
            categories['OTHER'].append(file_path)

    # Показываем статистику
    print('\n📋 СТАТИСТИКА ПО КАТЕГОРИЯМ:')
    print('-' * 50)
    total_core = 0
    for category, files in categories.items():
        if files:
            print(f'{category:15s}: {len(files):3d} файлов')
            total_core += len(files)

    print(f'{"TOTAL CORE":15s}: {total_core:3d} файлов')
    print(f'{"OTHER":15s}: {len(categories["OTHER"]):3d} файлов')
    print(f'{"TOTAL":15s}: {len(all_py_files):3d} файлов')

    # Показываем детали по категориям
    print('\n📋 ДЕТАЛЬНАЯ РАЗБИВКА:')
    print('=' * 80)

    for category, files in categories.items():
        if files and category != 'OTHER':
            print(f'\n🏗️ {category} ({len(files)} файлов):')
            print('-' * 50)
            for i, file_path in enumerate(files[:10], 1):  # Показываем первые 10
                filename = os.path.basename(file_path)
                print(f'{i:2d}. {filename}')
            if len(files) > 10:
                print(f'    ... и еще {len(files) - 10} файлов')

    print(f'\n📊 ИТОГОВАЯ СТАТИСТИКА:')
    print(f'   Всего Python файлов: {len(all_py_files)}')
    print(f'   Основных компонентов: {total_core}')
    print(f'   Дополнительных файлов: {len(categories["OTHER"])}')

if __name__ == "__main__":
    analyze_system()
