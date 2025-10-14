#!/usr/bin/env python3
"""
Скрипт для исправления вызовов logger.log
"""

import re

def fix_logging_calls(file_path):
    """Исправляет вызовы logger.log в файле"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Паттерн для поиска logger.log с level параметром
    pattern1 = r'logger\.log\(([^,]+),\s*level="([^"]+)"\)'
    replacement1 = r'logger.log("\2", \1)'
    content = re.sub(pattern1, replacement1, content)
    
    # Паттерн для поиска logger.log без level параметра
    pattern2 = r'logger\.log\(([^,)]+)\)(?!\s*,\s*level)'
    replacement2 = r'logger.log("INFO", \1)'
    content = re.sub(pattern2, replacement2, content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Исправлен файл: {file_path}")

# Исправляем файлы
files_to_fix = [
    "russian_apis_server.py",
    "scripts/integrate_russian_apis.py",
    "tests/test_russian_apis.py"
]

for file_path in files_to_fix:
    try:
        fix_logging_calls(file_path)
    except Exception as e:
        print(f"Ошибка исправления {file_path}: {e}")

print("Исправление завершено!")