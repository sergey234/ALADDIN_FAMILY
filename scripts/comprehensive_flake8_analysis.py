#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Комплексный анализ всех 326 функций с flake8
Генерация детального отчета по каждой функции
"""

import os
import subprocess
import json
from pathlib import Path
from collections import defaultdict
import re

def run_flake8_on_file(file_path, max_line_length=120):
    """Запуск flake8 на конкретном файле"""
    try:
        result = subprocess.run([
            'python3', '-m', 'flake8', 
            str(file_path), 
            f'--max-line-length={max_line_length}'
        ], capture_output=True, text=True, cwd='/Users/sergejhlystov/ALADDIN_NEW')
        
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def analyze_flake8_output(output):
    """Анализ вывода flake8"""
    errors = defaultdict(int)
    error_details = []
    
    if not output.strip():
        return errors, error_details
    
    lines = output.strip().split('\n')
    for line in lines:
        if ':' in line:
            parts = line.split(':')
            if len(parts) >= 4:
                error_code = parts[3].strip().split()[0]
                errors[error_code] += 1
                error_details.append({
                    'line': parts[1],
                    'column': parts[2],
                    'error': error_code,
                    'message': ':'.join(parts[3:]).strip(),
                    'file': parts[0]
                })
    
    return errors, error_details

def find_python_files():
    """Поиск всех Python файлов в системе"""
    python_files = []
    
    # Основные директории
    directories = [
        'core',
        'security',
        'security/ai_agents',
        'security/bots',
        'security/microservices',
        'security/managers',
        'security/privacy',
        'security/ci_cd',
        'tests'
    ]
    
    for directory in directories:
        if os.path.exists(directory):
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith('.py') and not file.startswith('__'):
                        python_files.append(os.path.join(root, file))
    
    return python_files

def get_function_info_from_file(file_path):
    """Получение информации о функциях из файла"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Поиск классов
        class_pattern = r'^class\s+(\w+)'
        classes = re.findall(class_pattern, content, re.MULTILINE)
        
        # Поиск функций
        func_pattern = r'^def\s+(\w+)'
        functions = re.findall(func_pattern, content, re.MULTILINE)
        
        return classes, functions
    except Exception as e:
        return [], []

def main():
    """Основная функция анализа"""
    print("🔍 КОМПЛЕКСНЫЙ АНАЛИЗ ВСЕХ ФУНКЦИЙ С FLAKE8")
    print("=" * 60)
    
    # Поиск всех Python файлов
    python_files = find_python_files()
    print(f"📁 Найдено {len(python_files)} Python файлов")
    
    # Результаты анализа
    analysis_results = {
        'total_files': len(python_files),
        'clean_files': 0,
        'files_with_errors': 0,
        'total_errors': 0,
        'error_types': defaultdict(int),
        'file_details': [],
        'summary_by_category': defaultdict(lambda: {
            'total_files': 0,
            'clean_files': 0,
            'files_with_errors': 0,
            'total_errors': 0,
            'error_types': defaultdict(int)
        })
    }
    
    print(f"\n🔍 АНАЛИЗ ФАЙЛОВ:")
    print("-" * 60)
    
    for i, file_path in enumerate(python_files, 1):
        print(f"[{i:3d}/{len(python_files)}] {file_path}")
        
        # Запуск flake8
        returncode, stdout, stderr = run_flake8_on_file(file_path)
        
        # Анализ результатов
        errors, error_details = analyze_flake8_output(stdout)
        
        # Определение категории файла
        category = 'other'
        if '/core/' in file_path:
            category = 'core'
        elif '/security/ai_agents/' in file_path:
            category = 'ai_agent'
        elif '/security/bots/' in file_path:
            category = 'bot'
        elif '/security/microservices/' in file_path:
            category = 'microservice'
        elif '/security/managers/' in file_path:
            category = 'manager'
        elif '/security/privacy/' in file_path:
            category = 'privacy'
        elif '/security/' in file_path:
            category = 'security'
        elif '/tests/' in file_path:
            category = 'test'
        
        # Получение информации о функциях
        classes, functions = get_function_info_from_file(file_path)
        
        # Подсчет ошибок
        total_errors = sum(errors.values())
        
        # Статус файла
        is_clean = total_errors == 0
        if is_clean:
            analysis_results['clean_files'] += 1
            analysis_results['summary_by_category'][category]['clean_files'] += 1
        else:
            analysis_results['files_with_errors'] += 1
            analysis_results['summary_by_category'][category]['files_with_errors'] += 1
        
        analysis_results['total_errors'] += total_errors
        analysis_results['summary_by_category'][category]['total_errors'] += total_errors
        
        # Обновление счетчиков
        analysis_results['summary_by_category'][category]['total_files'] += 1
        
        for error_type, count in errors.items():
            analysis_results['error_types'][error_type] += count
            analysis_results['summary_by_category'][category]['error_types'][error_type] += count
        
        # Детали файла
        file_detail = {
            'file_path': file_path,
            'category': category,
            'is_clean': is_clean,
            'total_errors': total_errors,
            'error_types': dict(errors),
            'error_details': error_details,
            'classes': classes,
            'functions': functions,
            'classes_count': len(classes),
            'functions_count': len(functions)
        }
        
        analysis_results['file_details'].append(file_detail)
        
        # Вывод статуса
        status = "✅ ЧИСТЫЙ" if is_clean else f"❌ {total_errors} ошибок"
        print(f"     {status}")
        
        if not is_clean and total_errors <= 5:  # Показываем детали для файлов с небольшим количеством ошибок
            for error_type, count in errors.items():
                print(f"       {error_type}: {count}")
    
    # Сохранение результатов
    with open('COMPREHENSIVE_FLAKE8_ANALYSIS_REPORT.json', 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, indent=2, ensure_ascii=False)
    
    # Вывод итогового отчета
    print(f"\n📊 ИТОГОВЫЙ ОТЧЕТ:")
    print("=" * 60)
    print(f"Всего файлов: {analysis_results['total_files']}")
    print(f"Чистых файлов: {analysis_results['clean_files']} ({analysis_results['clean_files']/analysis_results['total_files']*100:.1f}%)")
    print(f"Файлов с ошибками: {analysis_results['files_with_errors']} ({analysis_results['files_with_errors']/analysis_results['total_files']*100:.1f}%)")
    print(f"Всего ошибок: {analysis_results['total_errors']}")
    
    print(f"\n📈 ОШИБКИ ПО ТИПАМ:")
    for error_type, count in sorted(analysis_results['error_types'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {error_type}: {count}")
    
    print(f"\n📁 СТАТИСТИКА ПО КАТЕГОРИЯМ:")
    for category, stats in analysis_results['summary_by_category'].items():
        if stats['total_files'] > 0:
            clean_percent = stats['clean_files'] / stats['total_files'] * 100
            print(f"  {category}: {stats['clean_files']}/{stats['total_files']} чистых ({clean_percent:.1f}%), {stats['total_errors']} ошибок")
    
    print(f"\n💾 Детальный отчет сохранен в: COMPREHENSIVE_FLAKE8_ANALYSIS_REPORT.json")

if __name__ == "__main__":
    main()