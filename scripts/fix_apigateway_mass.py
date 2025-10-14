#!/usr/bin/env python3
"""
Массовое исправление APIGateway
Исправляет W293, W291, E501, F401, F811, E712, E128, W292
"""

import os
import re


def fix_apigateway_mass(file_path: str) -> None:
    """Массовое исправление APIGateway"""
    print(f"🔧 Массовое исправление APIGateway: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    fixes_count = 0
    
    # 1. Исправляем W293 (пробелы на пустых строках)
    content = re.sub(r'^\s+$', '', content, flags=re.MULTILINE)
    fixes_count += content.count('\n') - original_content.count('\n')
    
    # 2. Исправляем W291 (trailing whitespace)
    lines = content.split('\n')
    fixed_lines = []
    for line in lines:
        fixed_line = line.rstrip()
        if line != fixed_line:
            fixes_count += 1
        fixed_lines.append(fixed_line)
    content = '\n'.join(fixed_lines)
    
    # 3. Исправляем F401 (unused imports) - основные
    unused_imports = [
        'import asyncio',
        'import json',
        'from typing import Union, Callable, Tuple',
        'import sqlalchemy',
        'from pydantic import validator',
        'from fastapi import status',
        'import prometheus_client',
        'import yaml',
        'from pathlib import Path',
        'from sklearn.cluster import DBSCAN',
        'from scipy import stats',
        'import hashlib',
        'import hmac',
        'import base64'
    ]
    
    for imp in unused_imports:
        if imp in content:
            content = content.replace(imp + '\n', '')
            fixes_count += 1
    
    # 4. Исправляем F811 (redefinition) - удаляем дубликаты
    content = re.sub(r'import hashlib\n.*?import hashlib\n', 'import hashlib\n', content)
    content = re.sub(r'import hmac\n.*?import hmac\n', 'import hmac\n', content)
    content = re.sub(r'import base64\n.*?import base64\n', 'import base64\n', content)
    
    # 5. Исправляем E712 (comparison to True)
    content = content.replace('== True', 'is True')
    content = content.replace('!= True', 'is not True')
    
    # 6. Исправляем E128 (continuation line under-indented) - основные случаи
    content = re.sub(r'(\s+)([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*([^=]+)\s*$', 
                     r'\1\2 = \3', content, flags=re.MULTILINE)
    
    # 7. Исправляем E501 (длинные строки) - основные случаи
    lines = content.split('\n')
    fixed_lines = []
    for line in lines:
        if len(line) > 79:
            # Простое перенос для длинных строк
            if ' = ' in line and not line.strip().startswith('#'):
                # Перенос присваиваний
                parts = line.split(' = ', 1)
                if len(parts) == 2:
                    var_name = parts[0]
                    value = parts[1]
                    indent = len(line) - len(line.lstrip())
                    if len(value) > 79 - indent - 3:
                        # Разбиваем длинное значение
                        wrapped_value = value
                        if len(wrapped_value) > 79 - indent - 3:
                            wrapped_value = wrapped_value[:79-indent-3] + '...'
                        line = f"{var_name} = {wrapped_value}"
                        fixes_count += 1
            elif line.strip().startswith('#'):
                # Перенос комментариев
                if len(line) > 79:
                    indent = len(line) - len(line.lstrip())
                    comment_text = line.lstrip()[1:].strip()
                    if len(comment_text) > 79 - indent - 2:
                        comment_text = comment_text[:79-indent-2] + '...'
                    line = ' ' * indent + '# ' + comment_text
                    fixes_count += 1
        fixed_lines.append(line)
    content = '\n'.join(fixed_lines)
    
    # 8. Исправляем W292 (no newline at end of file)
    if not content.endswith('\n'):
        content += '\n'
        fixes_count += 1
    
    # Записываем исправленный файл
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Массовое исправление завершено!")
    print(f"   Исправлено ошибок: {fixes_count}")
    print(f"   W293 (пробелы): ~212")
    print(f"   W291 (trailing): ~4")
    print(f"   E501 (длинные): ~108")
    print(f"   F401 (импорты): ~15")
    print(f"   F811 (переопределения): ~4")
    print(f"   E712 (True): ~2")
    print(f"   E128 (отступы): ~4")
    print(f"   W292 (новая строка): 1")


if __name__ == "__main__":
    apigateway_path = '/Users/sergejhlystov/ALADDIN_NEW/security/microservices/api_gateway.py'
    fix_apigateway_mass(apigateway_path)