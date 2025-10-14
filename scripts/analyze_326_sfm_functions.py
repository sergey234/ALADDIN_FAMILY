#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализ flake8 для всех 326 функций зарегистрированных в SFM
"""

import json
import subprocess
import os
from pathlib import Path

def run_flake8(file_path):
    """Запуск flake8 на файле"""
    try:
        result = subprocess.run([
            'python3', '-m', 'flake8', 
            file_path,
            '--statistics'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            return 0, [], ""
        else:
            errors = []
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if ':' in line and not line.startswith('['):
                    parts = line.split(':')
                    if len(parts) >= 4:
                        error_code = parts[3].strip().split()[0]
                        errors.append(error_code)
            return len(errors), errors, result.stdout
    except:
        return -1, [], "Timeout or error"

def find_function_file(function_id):
    """Поиск файла функции по ID"""
    search_paths = [
        f"security/{function_id}.py",
        f"core/{function_id}.py",
        f"config/{function_id}.py",
        f"security/ai_agents/{function_id}.py",
        f"security/bots/{function_id}.py",
        f"security/microservices/{function_id}.py",
        f"security/managers/{function_id}.py",
        f"security/privacy/{function_id}.py",
        f"tests/{function_id}.py",
        f"scripts/{function_id}.py",
        f"{function_id}.py"
    ]
    
    for path in search_paths:
        full_path = Path(path)
        if full_path.exists():
            return str(full_path)
    
    return None

def main():
    """Основная функция"""
    print("🔍 АНАЛИЗ FLAKE8 ДЛЯ ВСЕХ 326 ФУНКЦИЙ SFM")
    print("=" * 80)
    
    # Загружаем список всех 326 функций
    with open('ALL_SFM_FUNCTIONS_DETAILED.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    all_functions = []
    for func_type, functions in data['functions_by_type'].items():
        all_functions.extend(functions)
    
    all_functions = sorted(all_functions)
    
    print(f"📊 Найдено {len(all_functions)} функций для анализа")
    print("=" * 80)
    
    results = []
    total_errors = 0
    files_found = 0
    
    for i, func_id in enumerate(all_functions, 1):
        file_path = find_function_file(func_id)
        
        if file_path:
            files_found += 1
            error_count, errors, output = run_flake8(file_path)
            
            if error_count == 0:
                status = "✅ ЧИСТЫЙ"
                print(f"{i:3d}. {func_id:<40} {status}")
            elif error_count == -1:
                status = "❌ ОШИБКА"
                print(f"{i:3d}. {func_id:<40} {status}")
            else:
                total_errors += error_count
                status = f"❌ {error_count} ошибок"
                print(f"{i:3d}. {func_id:<40} {status}")
                
                # Показываем топ-3 ошибки
                if error_count <= 10:
                    error_counts = {}
                    for error in errors:
                        error_counts[error] = error_counts.get(error, 0) + 1
                    
                    top_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:3]
                    error_summary = ", ".join([f"{err}:{count}" for err, count in top_errors])
                    print(f"     └─ {error_summary}")
                else:
                    print(f"     └─ МНОГО ОШИБОК")
            
            results.append({
                'function_id': func_id,
                'file_path': file_path,
                'error_count': error_count,
                'errors': errors,
                'status': status
            })
        else:
            print(f"{i:3d}. {func_id:<40} ⚠️ ФАЙЛ НЕ НАЙДЕН")
            results.append({
                'function_id': func_id,
                'file_path': None,
                'error_count': -1,
                'errors': [],
                'status': "⚠️ ФАЙЛ НЕ НАЙДЕН"
            })
    
    print("=" * 80)
    print(f"📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ:")
    print(f"Всего функций: {len(all_functions)}")
    print(f"Файлов найдено: {files_found}")
    print(f"Всего ошибок: {total_errors}")
    
    # Статистика по ошибкам
    all_errors = []
    for result in results:
        all_errors.extend(result['errors'])
    
    if all_errors:
        error_counts = {}
        for error in all_errors:
            error_counts[error] = error_counts.get(error, 0) + 1
        
        print(f"\n📈 ТОП-10 ОШИБОК:")
        for i, (error, count) in enumerate(sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:10], 1):
            print(f"  {i:2d}. {error}: {count}")

if __name__ == "__main__":
    main()