#!/usr/bin/env python3
"""
Скрипт для анализа всех файлов системы безопасности
"""

import subprocess
import sys
import os
from pathlib import Path

def analyze_file(file_path):
    """Анализирует один файл и возвращает детальную информацию об ошибках"""
    try:
        # Запускаем flake8 для файла
        result = subprocess.run([
            'python3', '-m', 'flake8', 
            '--count', '--statistics', '--max-line-length=79',
            str(file_path)
        ], capture_output=True, text=True, cwd='/Users/sergejhlystov/ALADDIN_NEW')
        
        if result.returncode == 0:
            return {
                'file': file_path,
                'total_errors': 0,
                'error_details': {},
                'raw_output': ''
            }
        
        # Парсим вывод flake8
        lines = result.stdout.strip().split('\n')
        total_errors = 0
        error_details = {}
        
        for line in lines:
            if ':' in line and any(code in line for code in ['E', 'W', 'F']):
                # Извлекаем код ошибки
                parts = line.split(':')
                if len(parts) >= 3:
                    error_code = parts[2].strip().split()[0]
                    if error_code in error_details:
                        error_details[error_code] += 1
                    else:
                        error_details[error_code] = 1
                    total_errors += 1
        
        return {
            'file': file_path,
            'total_errors': total_errors,
            'error_details': error_details,
            'raw_output': result.stdout
        }
        
    except Exception as e:
        return {
            'file': file_path,
            'total_errors': -1,
            'error_details': {},
            'raw_output': f'Error: {str(e)}'
        }

def main():
    """Основная функция"""
    print("🔍 АНАЛИЗ ВСЕХ ФАЙЛОВ СИСТЕМЫ БЕЗОПАСНОСТИ")
    print("=" * 60)
    
    # Получаем список всех файлов
    result = subprocess.run([
        'find', 'security/', 'core/', 'config/', '-name', '*.py'
    ], capture_output=True, text=True, cwd='/Users/sergejhlystov/ALADDIN_NEW')
    
    files = [f for f in result.stdout.strip().split('\n') 
             if f and not any(x in f for x in ['backup', '.bak', '.backup', '__pycache__'])]
    
    print(f"📊 Найдено файлов: {len(files)}")
    print()
    
    # Анализируем каждый файл
    all_results = []
    for i, file_path in enumerate(files, 1):
        print(f"⏳ Анализ {i}/{len(files)}: {os.path.basename(file_path)}")
        result = analyze_file(file_path)
        all_results.append(result)
    
    print("\n" + "=" * 60)
    print("📋 РЕЗУЛЬТАТЫ АНАЛИЗА")
    print("=" * 60)
    
    # Сортируем по количеству ошибок
    all_results.sort(key=lambda x: x['total_errors'], reverse=True)
    
    # Выводим результаты
    for result in all_results:
        if result['total_errors'] > 0:
            print(f"\n🔴 {os.path.basename(result['file'])} - {result['total_errors']} ошибок")
            for error_code, count in sorted(result['error_details'].items()):
                print(f"   {error_code}: {count}")
        elif result['total_errors'] == 0:
            print(f"✅ {os.path.basename(result['file'])} - 0 ошибок")
        else:
            print(f"❌ {os.path.basename(result['file'])} - ОШИБКА АНАЛИЗА")
    
    # Статистика
    total_errors = sum(r['total_errors'] for r in all_results if r['total_errors'] > 0)
    files_with_errors = len([r for r in all_results if r['total_errors'] > 0])
    files_perfect = len([r for r in all_results if r['total_errors'] == 0])
    
    print(f"\n📊 ОБЩАЯ СТАТИСТИКА:")
    print(f"   Всего файлов: {len(files)}")
    print(f"   Файлов с ошибками: {files_with_errors}")
    print(f"   Идеальных файлов: {files_perfect}")
    print(f"   Всего ошибок: {total_errors}")
    
    # Сохраняем результаты в файл
    with open('/Users/sergejhlystov/ALADDIN_NEW/all_files_analysis.txt', 'w', encoding='utf-8') as f:
        f.write("🔍 ДЕТАЛЬНЫЙ АНАЛИЗ ВСЕХ ФАЙЛОВ СИСТЕМЫ БЕЗОПАСНОСТИ\n")
        f.write("=" * 60 + "\n\n")
        
        for result in all_results:
            f.write(f"📁 {result['file']}\n")
            f.write(f"   Ошибок: {result['total_errors']}\n")
            if result['error_details']:
                for error_code, count in sorted(result['error_details'].items()):
                    f.write(f"   {error_code}: {count}\n")
            f.write("\n")
    
    print(f"\n💾 Результаты сохранены в: all_files_analysis.txt")

if __name__ == "__main__":
    main()