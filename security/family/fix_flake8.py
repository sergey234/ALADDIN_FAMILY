#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для исправления ошибок flake8
"""

import re
import os

def fix_long_lines(file_path, max_length=79):
    """Исправление длинных строк в файле"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        if len(line) > max_length:
            # Разбиваем длинные строки
            if 'logger.info(' in line and 'f"' in line:
                # Разбиваем логирование
                parts = line.split('logger.info(')
                if len(parts) == 2:
                    indent = len(parts[0])
                    log_content = parts[1]
                    if log_content.endswith(')'):
                        log_content = log_content[:-1]
                    
                    # Разбиваем на части
                    if len(log_content) > max_length - indent - 15:
                        # Находим место для разбивки
                        if ' с ролью ' in log_content:
                            parts2 = log_content.split(' с ролью ')
                            if len(parts2) == 2:
                                new_line = f"{' ' * indent}logger.info({parts2[0]} с ролью \\\n"
                                new_line += f"{' ' * (indent + 4)}{parts2[1]})"
                                fixed_lines.append(new_line)
                                continue
                    
            # Общие случаи разбивки
            if 'assert ' in line and len(line) > max_length:
                # Разбиваем assert
                indent = len(line) - len(line.lstrip())
                if ' == True' in line:
                    parts = line.split(' == True')
                    if len(parts) == 2:
                        new_line = f"{' ' * indent}{parts[0]} == \\\n"
                        new_line += f"{' ' * (indent + 4)}True{parts[1]}"
                        fixed_lines.append(new_line)
                        continue
            
            # Если не удалось разбить, оставляем как есть
            fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    # Убираем лишние пробелы в пустых строках
    cleaned_lines = []
    for line in fixed_lines:
        if line.strip() == '':
            cleaned_lines.append('')
        else:
            cleaned_lines.append(line.rstrip())
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(cleaned_lines))
    
    print(f"Исправлен файл: {file_path}")

def main():
    """Основная функция"""
    files = [
        'family_registration.py',
        'family_notification_manager.py', 
        'test_simple.py',
        '__init__.py'
    ]
    
    for file_path in files:
        if os.path.exists(file_path):
            print(f"Обрабатываю {file_path}...")
            fix_long_lines(file_path)
        else:
            print(f"Файл {file_path} не найден")

if __name__ == "__main__":
    main()