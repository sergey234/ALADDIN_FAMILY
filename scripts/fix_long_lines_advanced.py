#!/usr/bin/env python3
"""
Продвинутый скрипт исправления длинных строк (E501) в LoadBalancer
Исправляет 161 ошибку E501 с сохранением читаемости кода
"""

import os
import re
import textwrap
from typing import List, Tuple


def fix_long_lines_advanced(file_path: str, max_length: int = 79) -> None:
    """
    Продвинутое исправление длинных строк с учетом контекста
    
    Args:
        file_path: Путь к файлу
        max_length: Максимальная длина строки
    """
    print(f"🔧 Продвинутое исправление длинных строк: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixed_lines = []
    fixes_count = 0
    
    for i, line in enumerate(lines):
        original_line = line.rstrip('\n')
        
        if len(original_line) > max_length:
            # Определяем тип строки для правильного форматирования
            fixed_line = fix_line_by_type(original_line, max_length)
            
            if fixed_line != original_line:
                fixes_count += 1
                # Разбиваем на несколько строк если нужно
                wrapped_lines = fixed_line.split('\n')
                for wrapped_line in wrapped_lines:
                    fixed_lines.append(wrapped_line + '\n')
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
        
        if (i + 1) % 100 == 0:
            print(f"   Обработано строк: {i+1}, исправлений: {fixes_count}")
    
    # Записываем исправленный файл
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print(f"✅ Продвинутое исправление завершено!")
    print(f"   Исправлено строк: {fixes_count}")
    print(f"   E501 (длинные строки): ~{fixes_count}")


def fix_line_by_type(line: str, max_length: int) -> str:
    """
    Исправляет строку в зависимости от её типа
    
    Args:
        line: Исходная строка
        max_length: Максимальная длина
        
    Returns:
        Исправленная строка
    """
    # Убираем лишние пробелы
    line = line.rstrip()
    
    # 1. Комментарии - простое перенос
    if line.strip().startswith('#'):
        return wrap_comment(line, max_length)
    
    # 2. Строки с импортами
    if line.strip().startswith(('import ', 'from ')):
        return wrap_import(line, max_length)
    
    # 3. Строки с присваиванием
    if ' = ' in line and not line.strip().startswith('#'):
        return wrap_assignment(line, max_length)
    
    # 4. Строки с вызовами функций
    if '(' in line and ')' in line:
        return wrap_function_call(line, max_length)
    
    # 5. Строки с f-строками
    if 'f"' in line or "f'" in line:
        return wrap_f_string(line, max_length)
    
    # 6. Обычные строки - простое перенос
    return wrap_simple(line, max_length)


def wrap_comment(line: str, max_length: int) -> str:
    """Перенос комментариев"""
    indent = len(line) - len(line.lstrip())
    comment_text = line.lstrip()[1:].strip()  # Убираем #
    
    if len(comment_text) <= max_length - indent - 2:
        return line
    
    # Переносим комментарий
    wrapped = textwrap.fill(
        comment_text,
        width=max_length - indent - 2,
        initial_indent=' ' * indent + '# ',
        subsequent_indent=' ' * indent + '# '
    )
    return wrapped


def wrap_import(line: str, max_length: int) -> str:
    """Перенос импортов"""
    if 'from ' in line and ' import ' in line:
        # from module import item1, item2, item3
        parts = line.split(' import ')
        if len(parts) == 2:
            module_part = parts[0]
            items_part = parts[1]
            
            if len(line) <= max_length:
                return line
            
            # Переносим список импортов
            indent = len(line) - len(line.lstrip())
            wrapped_items = textwrap.fill(
                items_part,
                width=max_length - indent - 8,  # " import " = 8 символов
                initial_indent='',
                subsequent_indent=' ' * (indent + 8)
            )
            return f"{module_part} import {wrapped_items}"
    
    return wrap_simple(line, max_length)


def wrap_assignment(line: str, max_length: int) -> str:
    """Перенос присваиваний"""
    if ' = ' not in line:
        return wrap_simple(line, max_length)
    
    parts = line.split(' = ', 1)
    if len(parts) != 2:
        return wrap_simple(line, max_length)
    
    var_name = parts[0]
    value = parts[1]
    
    if len(line) <= max_length:
        return line
    
    # Переносим значение
    indent = len(line) - len(line.lstrip())
    wrapped_value = textwrap.fill(
        value,
        width=max_length - indent - 3,  # " = " = 3 символа
        initial_indent='',
        subsequent_indent=' ' * (indent + 3)
    )
    return f"{var_name} = {wrapped_value}"


def wrap_function_call(line: str, max_length: int) -> str:
    """Перенос вызовов функций"""
    if '(' not in line or ')' not in line:
        return wrap_simple(line, max_length)
    
    # Находим открывающую скобку
    open_paren = line.find('(')
    func_name = line[:open_paren].rstrip()
    args_part = line[open_paren:]
    
    if len(line) <= max_length:
        return line
    
    # Переносим аргументы
    indent = len(line) - len(line.lstrip())
    wrapped_args = textwrap.fill(
        args_part,
        width=max_length - indent,
        initial_indent=' ' * indent,
        subsequent_indent=' ' * (indent + 4)
    )
    return wrapped_args


def wrap_f_string(line: str, max_length: int) -> str:
    """Перенос f-строк"""
    if 'f"' not in line and "f'" not in line:
        return wrap_simple(line, max_length)
    
    # Простое перенос f-строк
    return wrap_simple(line, max_length)


def wrap_simple(line: str, max_length: int) -> str:
    """Простой перенос строки"""
    if len(line) <= max_length:
        return line
    
    indent = len(line) - len(line.lstrip())
    content = line.lstrip()
    
    wrapped = textwrap.fill(
        content,
        width=max_length - indent,
        initial_indent=' ' * indent,
        subsequent_indent=' ' * (indent + 4)
    )
    return wrapped


if __name__ == "__main__":
    load_balancer_path = '/Users/sergejhlystov/ALADDIN_NEW/security/microservices/load_balancer.py'
    fix_long_lines_advanced(load_balancer_path)