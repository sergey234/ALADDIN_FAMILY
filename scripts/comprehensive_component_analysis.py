#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Полный анализ всех компонентов для интеграции в SFM
Анализ 191 класса в security + 9 классов в core = 200 компонентов для интеграции

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-11
"""

import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple, Set

def analyze_security_components():
    """Анализ всех компонентов безопасности для интеграции в SFM"""
    
    project_root = Path('/Users/sergejhlystov/ALADDIN_NEW')
    
    # Статистика по категориям
    categories = {
        'core': {'files': 0, 'classes': 0, 'functions': 0, 'components': []},
        'security_main': {'files': 0, 'classes': 0, 'functions': 0, 'components': []},
        'ai_agents': {'files': 0, 'classes': 0, 'functions': 0, 'components': []},
        'bots': {'files': 0, 'classes': 0, 'functions': 0, 'components': []},
        'microservices': {'files': 0, 'classes': 0, 'functions': 0, 'components': []},
        'family': {'files': 0, 'classes': 0, 'functions': 0, 'components': []},
        'compliance': {'files': 0, 'classes': 0, 'functions': 0, 'components': []},
        'privacy': {'files': 0, 'classes': 0, 'functions': 0, 'components': []},
        'reactive': {'files': 0, 'classes': 0, 'functions': 0, 'components': []},
        'active': {'files': 0, 'classes': 0, 'functions': 0, 'components': []},
        'preliminary': {'files': 0, 'classes': 0, 'functions': 0, 'components': []},
        'orchestration': {'files': 0, 'classes': 0, 'functions': 0, 'components': []},
        'scaling': {'files': 0, 'classes': 0, 'functions': 0, 'components': []}
    }
    
    # Анализ CORE компонентов
    print("🔍 АНАЛИЗ CORE КОМПОНЕНТОВ...")
    core_files = list(project_root.glob('core/*.py'))
    for file_path in core_files:
        if file_path.name != '__init__.py':
            categories['core']['files'] += 1
            classes, functions = analyze_file(file_path)
            categories['core']['classes'] += classes
            categories['core']['functions'] += functions
            categories['core']['components'].append({
                'file': file_path.name,
                'path': str(file_path),
                'classes': classes,
                'functions': functions
            })
    
    # Анализ SECURITY компонентов
    print("🔍 АНАЛИЗ SECURITY КОМПОНЕНТОВ...")
    security_files = list(project_root.glob('security/*.py'))
    for file_path in security_files:
        if file_path.name != '__init__.py':
            categories['security_main']['files'] += 1
            classes, functions = analyze_file(file_path)
            categories['security_main']['classes'] += classes
            categories['security_main']['functions'] += functions
            categories['security_main']['components'].append({
                'file': file_path.name,
                'path': str(file_path),
                'classes': classes,
                'functions': functions
            })
    
    # Анализ AI AGENTS
    print("🔍 АНАЛИЗ AI AGENTS...")
    ai_agent_files = list(project_root.glob('security/ai_agents/*.py'))
    for file_path in ai_agent_files:
        if file_path.name != '__init__.py':
            categories['ai_agents']['files'] += 1
            classes, functions = analyze_file(file_path)
            categories['ai_agents']['classes'] += classes
            categories['ai_agents']['functions'] += functions
            categories['ai_agents']['components'].append({
                'file': file_path.name,
                'path': str(file_path),
                'classes': classes,
                'functions': functions
            })
    
    # Анализ BOTS
    print("🔍 АНАЛИЗ BOTS...")
    bot_files = list(project_root.glob('security/bots/*.py'))
    for file_path in bot_files:
        if file_path.name != '__init__.py':
            categories['bots']['files'] += 1
            classes, functions = analyze_file(file_path)
            categories['bots']['classes'] += classes
            categories['bots']['functions'] += functions
            categories['bots']['components'].append({
                'file': file_path.name,
                'path': str(file_path),
                'classes': classes,
                'functions': functions
            })
    
    # Анализ MICROSERVICES
    print("🔍 АНАЛИЗ MICROSERVICES...")
    microservice_files = list(project_root.glob('security/microservices/*.py'))
    for file_path in microservice_files:
        if file_path.name != '__init__.py':
            categories['microservices']['files'] += 1
            classes, functions = analyze_file(file_path)
            categories['microservices']['classes'] += classes
            categories['microservices']['functions'] += functions
            categories['microservices']['components'].append({
                'file': file_path.name,
                'path': str(file_path),
                'classes': classes,
                'functions': functions
            })
    
    # Анализ дополнительных категорий
    additional_categories = [
        ('family', 'security/family'),
        ('compliance', 'security/compliance'),
        ('privacy', 'security/privacy'),
        ('reactive', 'security/reactive'),
        ('active', 'security/active'),
        ('preliminary', 'security/preliminary'),
        ('orchestration', 'security/orchestration'),
        ('scaling', 'security/scaling')
    ]
    
    for cat_name, cat_path in additional_categories:
        print(f"🔍 АНАЛИЗ {cat_name.upper()}...")
        cat_files = list(project_root.glob(f'{cat_path}/*.py'))
        for file_path in cat_files:
            if file_path.name != '__init__.py':
                categories[cat_name]['files'] += 1
                classes, functions = analyze_file(file_path)
                categories[cat_name]['classes'] += classes
                categories[cat_name]['functions'] += functions
                categories[cat_name]['components'].append({
                    'file': file_path.name,
                    'path': str(file_path),
                    'classes': classes,
                    'functions': functions
                })
    
    return categories

def analyze_file(file_path: Path) -> Tuple[int, int]:
    """Анализ файла на количество классов и функций"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Подсчет классов
        class_count = len(re.findall(r'^class\s+\w+', content, re.MULTILINE))
        
        # Подсчет функций
        function_count = len(re.findall(r'^def\s+\w+', content, re.MULTILINE))
        
        return class_count, function_count
    except Exception as e:
        print(f"Ошибка анализа файла {file_path}: {e}")
        return 0, 0

def generate_integration_plan(categories: Dict) -> None:
    """Генерация плана интеграции по приоритетам"""
    
    print("\n" + "="*80)
    print("📊 ПОЛНЫЙ АНАЛИЗ КОМПОНЕНТОВ ДЛЯ ИНТЕГРАЦИИ В SFM")
    print("="*80)
    
    total_files = sum(cat['files'] for cat in categories.values())
    total_classes = sum(cat['classes'] for cat in categories.values())
    total_functions = sum(cat['functions'] for cat in categories.values())
    
    print(f"\n🎯 ОБЩАЯ СТАТИСТИКА:")
    print(f"  📁 Всего файлов: {total_files}")
    print(f"  🏗️ Всего классов: {total_classes}")
    print(f"  ⚙️ Всего функций: {total_functions}")
    
    # Приоритеты интеграции
    priorities = {
        'ПЕРВЫЙ ПРИОРИТЕТ (КРИТИЧЕСКИЕ)': ['core', 'security_main'],
        'ВТОРОЙ ПРИОРИТЕТ (ВЫСОКИЕ)': ['ai_agents', 'bots', 'microservices'],
        'ТРЕТИЙ ПРИОРИТЕТ (СРЕДНИЕ)': ['family', 'compliance', 'privacy'],
        'ЧЕТВЕРТЫЙ ПРИОРИТЕТ (ДОПОЛНИТЕЛЬНЫЕ)': ['reactive', 'active', 'preliminary', 'orchestration', 'scaling']
    }
    
    for priority_name, priority_categories in priorities.items():
        print(f"\n{priority_name}:")
        print("-" * 50)
        
        priority_total_files = 0
        priority_total_classes = 0
        priority_total_functions = 0
        
        for cat_name in priority_categories:
            if cat_name in categories:
                cat = categories[cat_name]
                priority_total_files += cat['files']
                priority_total_classes += cat['classes']
                priority_total_functions += cat['functions']
                
                print(f"  📂 {cat_name.upper()}: {cat['files']} файлов, {cat['classes']} классов, {cat['functions']} функций")
                
                # Показываем топ-5 компонентов
                if cat['components']:
                    print(f"    🔝 Топ-5 компонентов:")
                    sorted_components = sorted(cat['components'], key=lambda x: x['classes'], reverse=True)[:5]
                    for i, comp in enumerate(sorted_components, 1):
                        print(f"      {i}. {comp['file']} - {comp['classes']} классов, {comp['functions']} функций")
        
        print(f"  📊 ИТОГО: {priority_total_files} файлов, {priority_total_classes} классов, {priority_total_functions} функций")
    
    # Детальная разбивка по компонентам
    print(f"\n📋 ДЕТАЛЬНАЯ РАЗБИВКА ПО КОМПОНЕНТАМ:")
    print("="*80)
    
    for cat_name, cat_data in categories.items():
        if cat_data['files'] > 0:
            print(f"\n🏗️ {cat_name.upper()} КОМПОНЕНТЫ ({cat_data['files']} файлов):")
            
            # Сортируем по количеству классов
            sorted_components = sorted(cat_data['components'], key=lambda x: x['classes'], reverse=True)
            
            for i, comp in enumerate(sorted_components, 1):
                status = "✅" if comp['classes'] > 0 else "⚠️"
                print(f"  {i:2d}. {status} {comp['file']} - {comp['classes']} классов, {comp['functions']} функций")
    
    # Рекомендации по интеграции
    print(f"\n🎯 РЕКОМЕНДАЦИИ ПО ИНТЕГРАЦИИ:")
    print("="*80)
    
    critical_components = categories['core']['classes'] + categories['security_main']['classes']
    high_priority_components = categories['ai_agents']['classes'] + categories['bots']['classes'] + categories['microservices']['classes']
    medium_priority_components = categories['family']['classes'] + categories['compliance']['classes'] + categories['privacy']['classes']
    additional_components = (categories['reactive']['classes'] + categories['active']['classes'] + 
                           categories['preliminary']['classes'] + categories['orchestration']['classes'] + 
                           categories['scaling']['classes'])
    
    print(f"  🔴 КРИТИЧЕСКИЕ (немедленно): {critical_components} классов")
    print(f"  🟡 ВЫСОКИЕ (в течение недели): {high_priority_components} классов")
    print(f"  🟠 СРЕДНИЕ (в течение месяца): {medium_priority_components} классов")
    print(f"  🔵 ДОПОЛНИТЕЛЬНЫЕ (по необходимости): {additional_components} классов")
    
    total_for_integration = critical_components + high_priority_components + medium_priority_components + additional_components
    print(f"\n  📊 ВСЕГО ДЛЯ ИНТЕГРАЦИИ: {total_for_integration} классов из {total_classes} ({total_for_integration/total_classes*100:.1f}%)")

def main():
    """Главная функция"""
    print("🚀 ПОЛНЫЙ АНАЛИЗ КОМПОНЕНТОВ ALADDIN SECURITY SYSTEM")
    print("="*80)
    
    # Анализ компонентов
    categories = analyze_security_components()
    
    # Генерация плана интеграции
    generate_integration_plan(categories)
    
    print(f"\n✅ АНАЛИЗ ЗАВЕРШЕН!")
    print(f"📊 Найдено {sum(cat['classes'] for cat in categories.values())} классов для интеграции в SFM")

if __name__ == "__main__":
    main()