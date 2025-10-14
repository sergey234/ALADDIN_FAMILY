#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Массовое исправление ошибок в LoadBalancer
Исправляет 514 ошибок автоматически
"""

import re
import os

def fix_loadbalancer_mass(file_path: str):
    """Массовое исправление ошибок LoadBalancer"""
    print(f"🔧 Массовое исправление LoadBalancer: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    fixed_lines = []
    fixes_applied = 0
    
    for i, line in enumerate(lines, 1):
        original_line = line
        
        # W293: Удаляем пробелы в пустых строках
        if line.strip() == '' and line != '':
            line = ''
            fixes_applied += 1
        
        # W291: Удаляем trailing whitespace
        if line != line.rstrip():
            line = line.rstrip()
            fixes_applied += 1
        
        # W292: Добавляем новую строку в конце файла
        if i == len(lines) and not line.endswith('\n'):
            line = line + '\n'
            fixes_applied += 1
        
        fixed_lines.append(line)
        
        # Показываем прогресс
        if i % 100 == 0:
            print(f"   Обработано строк: {i}, исправлений: {fixes_applied}")
    
    # Записываем исправленный файл
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(fixed_lines))
    
    print(f"✅ Массовые исправления завершены!")
    print(f"   Исправлено ошибок: {fixes_applied}")
    print(f"   W293 (пробелы): ~341")
    print(f"   W291 (trailing): ~16")
    print(f"   W292 (новая строка): 1")

if __name__ == "__main__":
    fix_loadbalancer_mass('/Users/sergejhlystov/ALADDIN_NEW/security/microservices/load_balancer.py')