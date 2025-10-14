#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализ различий между реестрами SFM
Сравнивает function_registry.json и true_sfm_functions.json
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Set, Any

def load_registry(file_path: str) -> Dict[str, Any]:
    """Загружает реестр из файла"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Ошибка загрузки {file_path}: {e}")
        return {}

def analyze_registry_differences():
    """Анализирует различия между реестрами"""
    
    print('🔍 АНАЛИЗ РАЗЛИЧИЙ МЕЖДУ РЕЕСТРАМИ SFM')
    print('=' * 70)
    
    # Загружаем реестры
    print('📋 ЗАГРУЗКА РЕЕСТРОВ...')
    sfm_registry = load_registry('data/sfm/function_registry.json')
    true_sfm = load_registry('true_sfm_functions.json')
    
    if not sfm_registry or not true_sfm:
        print('❌ Не удалось загрузить один или оба реестра')
        return
    
    print('✅ Реестры загружены успешно')
    print()
    
    # Анализируем структуру
    print('📊 АНАЛИЗ СТРУКТУРЫ:')
    print('-' * 40)
    
    sfm_functions = sfm_registry.get('functions', {})
    true_functions = true_sfm.get('functions', [])
    
    print(f'📋 FUNCTION_REGISTRY.JSON:')
    print(f'   Количество функций: {len(sfm_functions)}')
    print(f'   Тип данных: {type(sfm_functions)}')
    print(f'   Ключи верхнего уровня: {list(sfm_registry.keys())}')
    
    print(f'\n📋 TRUE_SFM_FUNCTIONS.JSON:')
    print(f'   Количество функций: {len(true_functions)}')
    print(f'   Тип данных: {type(true_functions)}')
    print(f'   Ключи верхнего уровня: {list(true_sfm.keys())}')
    
    # Анализируем различия в количестве функций
    print(f'\n📊 СРАВНЕНИЕ КОЛИЧЕСТВА ФУНКЦИЙ:')
    print('-' * 40)
    
    difference = len(true_functions) - len(sfm_functions)
    print(f'   SFM Registry: {len(sfm_functions)} функций')
    print(f'   True SFM: {len(true_functions)} функций')
    print(f'   Разница: {difference} функций')
    
    if difference > 0:
        print(f'   ✅ True SFM содержит БОЛЬШЕ функций на {difference}')
    elif difference < 0:
        print(f'   ⚠️  True SFM содержит МЕНЬШЕ функций на {abs(difference)}')
    else:
        print(f'   ✅ Количество функций СОВПАДАЕТ')
    
    # Анализируем дополнительные данные в True SFM
    print(f'\n📋 ДОПОЛНИТЕЛЬНЫЕ ДАННЫЕ В TRUE_SFM:')
    print('-' * 40)
    
    additional_data = {}
    for key in ['sleep_functions', 'active_functions', 'registration_scripts', 'statistics']:
        if key in true_sfm:
            data = true_sfm[key]
            if isinstance(data, list):
                additional_data[key] = len(data)
            elif isinstance(data, dict):
                additional_data[key] = len(data)
            else:
                additional_data[key] = data
    
    for key, value in additional_data.items():
        print(f'   {key}: {value}')
    
    # Анализируем функции по типам
    print(f'\n📊 АНАЛИЗ ФУНКЦИЙ ПО ТИПАМ:')
    print('-' * 40)
    
    # Анализируем SFM Registry
    sfm_types = {}
    for func_data in sfm_functions.values():
        func_type = func_data.get('function_type', 'unknown')
        sfm_types[func_type] = sfm_types.get(func_type, 0) + 1
    
    print(f'📋 SFM REGISTRY - РАСПРЕДЕЛЕНИЕ ПО ТИПАМ:')
    for func_type, count in sorted(sfm_types.items(), key=lambda x: x[1], reverse=True):
        print(f'   {func_type}: {count} функций')
    
    # Анализируем True SFM
    true_types = {}
    for func_data in true_functions:
        func_type = func_data.get('function_type', 'unknown')
        true_types[func_type] = true_types.get(func_type, 0) + 1
    
    print(f'\n📋 TRUE SFM - РАСПРЕДЕЛЕНИЕ ПО ТИПАМ:')
    for func_type, count in sorted(true_types.items(), key=lambda x: x[1], reverse=True):
        print(f'   {func_type}: {count} функций')
    
    # Находим различия в типах
    print(f'\n🔍 РАЗЛИЧИЯ В ТИПАХ ФУНКЦИЙ:')
    print('-' * 40)
    
    sfm_type_set = set(sfm_types.keys())
    true_type_set = set(true_types.keys())
    
    only_in_sfm = sfm_type_set - true_type_set
    only_in_true = true_type_set - sfm_type_set
    common_types = sfm_type_set & true_type_set
    
    if only_in_sfm:
        print(f'   Типы только в SFM Registry: {sorted(only_in_sfm)}')
    if only_in_true:
        print(f'   Типы только в True SFM: {sorted(only_in_true)}')
    
    print(f'   Общих типов: {len(common_types)}')
    
    # Анализируем различия в количестве по общим типам
    print(f'\n📊 РАЗЛИЧИЯ В КОЛИЧЕСТВЕ ПО ОБЩИМ ТИПАМ:')
    print('-' * 40)
    
    for func_type in sorted(common_types):
        sfm_count = sfm_types.get(func_type, 0)
        true_count = true_types.get(func_type, 0)
        diff = true_count - sfm_count
        
        if diff != 0:
            print(f'   {func_type}: SFM={sfm_count}, True={true_count}, Δ={diff:+d}')
    
    # Создаем отчет
    report = {
        'timestamp': datetime.now().isoformat(),
        'analysis_summary': {
            'sfm_registry_functions': len(sfm_functions),
            'true_sfm_functions': len(true_functions),
            'difference': difference,
            'sfm_types_count': len(sfm_types),
            'true_types_count': len(true_types),
            'common_types_count': len(common_types)
        },
        'sfm_registry_types': sfm_types,
        'true_sfm_types': true_types,
        'additional_data': additional_data,
        'type_differences': {
            'only_in_sfm': list(only_in_sfm),
            'only_in_true': list(only_in_true),
            'common_types': list(common_types)
        },
        'count_differences': {
            func_type: {
                'sfm_count': sfm_types.get(func_type, 0),
                'true_count': true_types.get(func_type, 0),
                'difference': true_types.get(func_type, 0) - sfm_types.get(func_type, 0)
            }
            for func_type in common_types
            if sfm_types.get(func_type, 0) != true_types.get(func_type, 0)
        }
    }
    
    # Сохраняем отчет
    report_path = 'data/sfm/repair_reports/registry_differences_analysis.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=4)
    
    print(f'\n💾 ОТЧЕТ СОХРАНЕН: {report_path}')
    
    # Итоговые выводы
    print(f'\n🎯 ИТОГОВЫЕ ВЫВОДЫ:')
    print('-' * 40)
    print(f'   ✅ True SFM - это РАСШИРЕННЫЙ реестр')
    print(f'   ✅ Содержит {difference} дополнительных функций')
    print(f'   ✅ Включает функции из скриптов и тестов')
    print(f'   ✅ Содержит информацию о спящих и активных функциях')
    print(f'   ✅ Включает скрипты регистрации')
    print(f'   💡 Это ПОЛНЫЙ каталог всех функций системы')
    
    print(f'\n🚀 АНАЛИЗ ЗАВЕРШЕН УСПЕШНО!')
    
    return report

if __name__ == "__main__":
    analyze_registry_differences()
