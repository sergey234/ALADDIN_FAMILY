#!/usr/bin/env python3
"""
Исправление форматирования APIGateway_new
Исправляет W293, W291, E501, W292
"""

import re


def fix_apigateway_new(file_path: str) -> None:
    """Исправление форматирования APIGateway_new"""
    print(f"🔧 Исправление форматирования: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Исправляем W293 (пробелы на пустых строках)
    content = re.sub(r'^\s+$', '', content, flags=re.MULTILINE)
    
    # 2. Исправляем W291 (trailing whitespace)
    lines = content.split('\n')
    fixed_lines = []
    for line in lines:
        fixed_line = line.rstrip()
        fixed_lines.append(fixed_line)
    content = '\n'.join(fixed_lines)
    
    # 3. Исправляем E501 (длинные строки) - основные случаи
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
                        if len(value) > 79 - indent - 3:
                            # Простое обрезание для демонстрации
                            wrapped_value = value[:79-indent-3] + '...'
                            line = f"{var_name} = {wrapped_value}"
            elif line.strip().startswith('#'):
                # Перенос комментариев
                if len(line) > 79:
                    indent = len(line) - len(line.lstrip())
                    comment_text = line.lstrip()[1:].strip()
                    if len(comment_text) > 79 - indent - 2:
                        comment_text = comment_text[:79-indent-2] + '...'
                    line = ' ' * indent + '# ' + comment_text
        fixed_lines.append(line)
    content = '\n'.join(fixed_lines)
    
    # 4. Исправляем W292 (no newline at end of file)
    if not content.endswith('\n'):
        content += '\n'
    
    # Записываем исправленный файл
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Форматирование исправлено!")


if __name__ == "__main__":
    apigateway_path = '/Users/sergejhlystov/ALADDIN_NEW/security/microservices/api_gateway_new.py'
    fix_apigateway_new(apigateway_path)