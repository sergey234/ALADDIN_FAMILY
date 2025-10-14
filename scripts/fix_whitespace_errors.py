#!/usr/bin/env python3
"""
Скрипт для исправления ошибок W293 (пробелы в пустых строках)
"""

import re
import sys

def fix_whitespace_errors(file_path):
    """Исправляет ошибки W293 в файле"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Исправляем W293 - убираем пробелы в пустых строках
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Если строка содержит только пробелы, заменяем на пустую строку
            if line.strip() == '':
                fixed_lines.append('')
            else:
                fixed_lines.append(line)
        
        # Исправляем W291 - убираем пробелы в конце строк
        fixed_lines = [line.rstrip() for line in fixed_lines]
        
        # Исправляем W292 - добавляем новую строку в конце файла
        if fixed_lines and fixed_lines[-1] != '':
            fixed_lines.append('')
        
        # Записываем исправленный файл
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(fixed_lines))
        
        print(f"✅ Исправлен файл: {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при исправлении {file_path}: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Использование: python3 fix_whitespace_errors.py <путь_к_файлу>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    fix_whitespace_errors(file_path)