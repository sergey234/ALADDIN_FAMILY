#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import json
from pathlib import Path

def count_functions_in_file(filepath):
    """Подсчитывает функции в Swift файле"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Ищем определения функций Swift
        # func functionName(...)
        # private func functionName(...)
        # public func functionName(...)
        # static func functionName(...)
        # @objc func functionName(...)
        function_pattern = r'(?:@\w+\s+)?(?:private|public|internal|fileprivate|static|class|mutating|nonmutating)?\s*func\s+(\w+)\s*[\(<]'
        functions = re.findall(function_pattern, content, re.MULTILINE)
        
        # Ищем computed properties (var name: Type { get/set })
        computed_property_pattern = r'var\s+(\w+)\s*:\s*\w+\s*\{'
        computed_properties = re.findall(computed_property_pattern, content, re.MULTILINE)
        
        # Ищем init методы
        init_pattern = r'(?:private|public|internal|fileprivate)?\s*init\s*[\(<]'
        inits = re.findall(init_pattern, content, re.MULTILINE)
        
        return {
            'functions': list(set(functions)),
            'computed_properties': list(set(computed_properties)),
            'inits': len(inits),
            'total': len(set(functions)) + len(set(computed_properties)) + len(inits)
        }
    except Exception as e:
        return {'functions': [], 'computed_properties': [], 'inits': 0, 'total': 0, 'error': str(e)}

def analyze_directory(directory, pattern="*.swift"):
    """Анализирует директорию на наличие Swift файлов"""
    results = {}
    total_functions = 0
    
    for root, dirs, files in os.walk(directory):
        # Пропускаем backup директории
        if 'BACKUP' in root or 'backup' in root.lower():
            continue
            
        for file in files:
            if file.endswith('.swift') and not file.endswith('_BACKUP') and 'backup' not in file.lower():
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, directory)
                func_data = count_functions_in_file(filepath)
                results[rel_path] = func_data
                total_functions += func_data['total']
    
    return results, total_functions

# Анализируем основные директории
base_dir = '/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS'

print('=' * 80)
print('АНАЛИЗ МОБИЛЬНОГО ПРИЛОЖЕНИЯ ALADDIN iOS')
print('=' * 80)
print('')

# Экраны
print('📱 АНАЛИЗ ЭКРАНОВ (Screens/)')
print('-' * 80)
screens_dir = os.path.join(base_dir, 'Screens')
screens_results, screens_total = analyze_directory(screens_dir)
print(f'Найдено файлов: {len(screens_results)}')
print(f'Всего функций: {screens_total}')
print('')

# ViewModels
print('🧠 АНАЛИЗ VIEWMODELS (ViewModels/)')
print('-' * 80)
viewmodels_dir = os.path.join(base_dir, 'ViewModels')
viewmodels_results, viewmodels_total = analyze_directory(viewmodels_dir)
print(f'Найдено файлов: {len(viewmodels_results)}')
print(f'Всего функций: {viewmodels_total}')
print('')

# Core
print('⚙️ АНАЛИЗ CORE (Core/)')
print('-' * 80)
core_dir = os.path.join(base_dir, 'Core')
core_results, core_total = analyze_directory(core_dir)
print(f'Найдено файлов: {len(core_results)}')
print(f'Всего функций: {core_total}')
print('')

# Shared
print('🔗 АНАЛИЗ SHARED (Shared/)')
print('-' * 80)
shared_dir = os.path.join(base_dir, 'Shared')
if os.path.exists(shared_dir):
    shared_results, shared_total = analyze_directory(shared_dir)
    print(f'Найдено файлов: {len(shared_results)}')
    print(f'Всего функций: {shared_total}')
else:
    shared_results, shared_total = {}, 0
    print('Директория не найдена')
print('')

# Components
print('🧩 АНАЛИЗ COMPONENTS (Components/)')
print('-' * 80)
components_dir = os.path.join(base_dir, 'Components')
if os.path.exists(components_dir):
    components_results, components_total = analyze_directory(components_dir)
    print(f'Найдено файлов: {len(components_results)}')
    print(f'Всего функций: {components_total}')
else:
    components_results, components_total = {}, 0
    print('Директория не найдена')
print('')

# ИТОГО
total_all = screens_total + viewmodels_total + core_total + shared_total + components_total

print('=' * 80)
print('ИТОГО')
print('=' * 80)
print(f'Экраны: {screens_total} функций')
print(f'ViewModels: {viewmodels_total} функций')
print(f'Core: {core_total} функций')
print(f'Shared: {shared_total} функций')
print(f'Components: {components_total} функций')
print(f'ВСЕГО: {total_all} функций')
print('')

# Сохраняем детальные результаты
output = {
    'screens': {k: {'total': v['total'], 'functions': len(v['functions'])} for k, v in screens_results.items()},
    'viewmodels': {k: {'total': v['total'], 'functions': len(v['functions'])} for k, v in viewmodels_results.items()},
    'core': {k: {'total': v['total'], 'functions': len(v['functions'])} for k, v in core_results.items()},
    'shared': {k: {'total': v['total'], 'functions': len(v['functions'])} for k, v in shared_results.items()},
    'components': {k: {'total': v['total'], 'functions': len(v['functions'])} for k, v in components_results.items()},
    'totals': {
        'screens': screens_total,
        'viewmodels': viewmodels_total,
        'core': core_total,
        'shared': shared_total,
        'components': components_total,
        'all': total_all
    }
}

with open('/tmp/mobile_app_analysis.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print('Детальные результаты сохранены в /tmp/mobile_app_analysis.json')
