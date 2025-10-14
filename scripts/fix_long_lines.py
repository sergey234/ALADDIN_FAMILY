#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Автоматическое исправление длинных строк (E501) в LoadBalancer
Исправляет 155 ошибок E501 автоматически
"""

import re
import os

def fix_long_lines(file_path: str):
    """Автоматическое исправление длинных строк"""
    print(f"🔧 Исправляем длинные строки в {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    fixed_lines = []
    fixes_applied = 0
    
    for i, line in enumerate(lines, 1):
        original_line = line
        
        # Проверяем длину строки (больше 79 символов)
        if len(line) > 79:
            # Пропускаем комментарии и docstrings
            if line.strip().startswith('#') or '"""' in line or "'''" in line:
                fixed_lines.append(line)
                continue
            
            # Пропускаем строки с URL или длинными путями
            if 'http' in line or 'file://' in line or len(line.split()) < 3:
                fixed_lines.append(line)
                continue
            
            # Разбиваем длинные строки
            if '=' in line and not line.strip().startswith('#'):
                # Разбиваем присваивания
                if ' = ' in line:
                    parts = line.split(' = ', 1)
                    if len(parts) == 2:
                        var_name = parts[0].strip()
                        value = parts[1].strip()
                        
                        # Если значение длинное, разбиваем его
                        if len(value) > 50:
                            # Ищем подходящее место для разбивки
                            if '(' in value and ')' in value:
                                # Функции - разбиваем по запятым
                                if ',' in value:
                                    # Находим последнюю запятую перед 70 символом
                                    last_comma = value.rfind(',', 0, 70)
                                    if last_comma > 0:
                                        indent = ' ' * (len(var_name) + 3)
                                        new_line = f"{var_name} = {value[:last_comma + 1]}\n{indent}{value[last_comma + 1:].strip()}"
                                        fixed_lines.append(new_line)
                                        fixes_applied += 1
                                        continue
                            
                            # Простое разбиение по словам
                            words = value.split()
                            if len(words) > 1:
                                mid_point = len(words) // 2
                                indent = ' ' * (len(var_name) + 3)
                                new_line = f"{var_name} = {' '.join(words[:mid_point])}\n{indent}{' '.join(words[mid_point:])}"
                                fixed_lines.append(new_line)
                                fixes_applied += 1
                                continue
            
            # Разбиваем длинные строки с операторами
            elif any(op in line for op in [' and ', ' or ', ' + ', ' - ', ' * ', ' / ']):
                # Находим последний оператор перед 70 символом
                for op in [' and ', ' or ', ' + ', ' - ', ' * ', ' / ']:
                    if op in line:
                        last_op = line.rfind(op, 0, 70)
                        if last_op > 0:
                            indent = ' ' * 4  # Базовый отступ
                            new_line = f"{line[:last_op]}\n{indent}{line[last_op:].strip()}"
                            fixed_lines.append(new_line)
                            fixes_applied += 1
                            break
                else:
                    fixed_lines.append(line)
            else:
                # Простое разбиение по словам для остальных случаев
                words = line.split()
                if len(words) > 1:
                    # Находим середину
                    mid_point = len(words) // 2
                    indent = ' ' * 4
                    new_line = f"{' '.join(words[:mid_point])}\n{indent}{' '.join(words[mid_point:])}"
                    fixed_lines.append(new_line)
                    fixes_applied += 1
                else:
                    fixed_lines.append(line)
        else:
            fixed_lines.append(line)
        
        # Показываем прогресс
        if i % 100 == 0:
            print(f"   Обработано строк: {i}, исправлений: {fixes_applied}")
    
    # Записываем исправленный файл
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(fixed_lines))
    
    print(f"✅ Исправление длинных строк завершено!")
    print(f"   Исправлено строк: {fixes_applied}")
    print(f"   E501 (длинные строки): ~{fixes_applied}")

if __name__ == "__main__":
    fix_long_lines('/Users/sergejhlystov/ALADDIN_NEW/security/microservices/load_balancer.py')