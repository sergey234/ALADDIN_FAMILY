#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для исправления trailing whitespace в SafeFunctionManager
"""

import re

def fix_trailing_whitespace(file_path):
    """Исправить trailing whitespace в файле"""
    print(f"🔧 Исправляем trailing whitespace в {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Удаляем trailing whitespace
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines, 1):
        # Удаляем trailing whitespace
        fixed_line = line.rstrip()
        fixed_lines.append(fixed_line)
        
        # Показываем прогресс для больших файлов
        if i % 100 == 0:
            print(f"   Обработано строк: {i}")
    
    # Записываем исправленный файл
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(fixed_lines))
    
    print(f"✅ Trailing whitespace исправлен!")

if __name__ == "__main__":
    fix_trailing_whitespace('/Users/sergejhlystov/ALADDIN_NEW/security/safe_function_manager.py')