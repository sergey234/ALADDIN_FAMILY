#!/usr/bin/env python3
"""
Правильный анализ flake8 только для системы безопасности
"""

import subprocess
import re
from collections import Counter
import json

def run_flake8_security():
    """Запуск flake8 только для системы безопасности"""
    print("🔍 ЗАПУСК FLAKE8 ДЛЯ СИСТЕМЫ БЕЗОПАСНОСТИ")
    print("=" * 50)
    
    try:
        # Запускаем flake8 для системы безопасности
        result = subprocess.run([
            'python3', '-m', 'flake8', 
            '--count', '--statistics', '--max-line-length=79',
            'security/', 'core/', 'ai/', 'config/'
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Ошибок flake8 не найдено!")
            return Counter(), 0, 0
        else:
            # Парсим ошибки
            error_counts = Counter()
            total_errors = 0
            files_with_errors = set()
            
            for line in result.stdout.split('\n'):
                if ':' in line and any(code in line for code in ['E', 'W', 'F']):
                    # Парсим строку вида: file.py:line:col: E123 error message
                    match = re.match(r'^([^:]+):(\d+):(\d+):\s+([EWF]\d+)\s+(.*)$', line)
                    if match:
                        file_path = match.group(1)
                        error_code = match.group(4)
                        error_counts[error_code] += 1
                        total_errors += 1
                        files_with_errors.add(file_path)
            
            return error_counts, total_errors, len(files_with_errors)
            
    except Exception as e:
        print(f"❌ Ошибка при запуске flake8: {e}")
        return Counter(), 0, 0

def analyze_security_files():
    """Анализ файлов системы безопасности"""
    print("\n📊 АНАЛИЗ ФАЙЛОВ СИСТЕМЫ БЕЗОПАСНОСТИ")
    print("-" * 40)
    
    # Подсчитываем файлы
    import os
    from pathlib import Path
    
    security_dirs = ['security', 'core', 'ai', 'config']
    total_files = 0
    python_files = []
    
    for dir_name in security_dirs:
        if os.path.exists(dir_name):
            for root, dirs, files in os.walk(dir_name):
                for file in files:
                    if file.endswith('.py'):
                        python_files.append(os.path.join(root, file))
                        total_files += 1
    
    print(f"📁 Найдено Python файлов: {total_files}")
    print(f"📁 Директории: {', '.join(security_dirs)}")
    
    return total_files, python_files

def main():
    """Основная функция"""
    print("🔒 ПРАВИЛЬНЫЙ АНАЛИЗ СИСТЕМЫ БЕЗОПАСНОСТИ")
    print("=" * 60)
    
    # Анализируем файлы
    total_files, python_files = analyze_security_files()
    
    # Запускаем flake8
    error_counts, total_errors, files_with_errors = run_flake8_security()
    
    print(f"\n📊 РЕЗУЛЬТАТЫ АНАЛИЗА FLAKE8")
    print("-" * 40)
    print(f"Всего файлов: {total_files}")
    print(f"Файлов с ошибками: {files_with_errors}")
    print(f"Всего ошибок: {total_errors}")
    print(f"Процент файлов с ошибками: {(files_with_errors/total_files*100):.1f}%")
    
    if total_errors > 0:
        print(f"\n🔴 ТОП-10 ОШИБОК:")
        print("-" * 20)
        for error_code, count in error_counts.most_common(10):
            percentage = (count / total_errors) * 100
            print(f"{error_code}: {count} ({percentage:.1f}%)")
        
        print(f"\n📋 ДЕТАЛЬНАЯ СТАТИСТИКА:")
        print("-" * 30)
        for error_code, count in error_counts.most_common():
            percentage = (count / total_errors) * 100
            print(f"{error_code}: {count} ошибок ({percentage:.1f}%)")
    
    # Сохраняем результаты
    results = {
        "analysis_timestamp": "2025-09-13T23:00:00",
        "total_files": total_files,
        "files_with_errors": files_with_errors,
        "total_errors": total_errors,
        "error_percentage": (files_with_errors/total_files*100) if total_files > 0 else 0,
        "error_breakdown": dict(error_counts)
    }
    
    with open("security_flake8_analysis.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Результаты сохранены: security_flake8_analysis.json")
    
    # Вывод рекомендаций
    if total_errors > 0:
        print(f"\n🎯 РЕКОМЕНДАЦИИ ПО ИСПРАВЛЕНИЮ:")
        print("-" * 40)
        
        if 'E501' in error_counts:
            print(f"1. Исправить длинные строки (E501): {error_counts['E501']} ошибок")
        if 'W293' in error_counts:
            print(f"2. Удалить пробелы из пустых строк (W293): {error_counts['W293']} ошибок")
        if 'F401' in error_counts:
            print(f"3. Удалить неиспользуемые импорты (F401): {error_counts['F401']} ошибок")
        if 'W291' in error_counts:
            print(f"4. Удалить пробелы в конце строк (W291): {error_counts['W291']} ошибок")
        if 'E302' in error_counts:
            print(f"5. Добавить пустые строки (E302): {error_counts['E302']} ошибок")
    
    print(f"\n✅ Анализ завершен!")

if __name__ == "__main__":
    main()