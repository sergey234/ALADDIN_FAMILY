#!/usr/bin/env python3
"""
Исправление длинных строк (E501) для TrustScoring
"""

import re

def fix_e501_errors():
    """Исправляет E501 ошибки в trust_scoring.py"""
    
    file_path = "security/preliminary/trust_scoring.py"
    
    try:
        # Читаем файл
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Исправляем E501 - разбиваем длинные строки
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            if len(line) > 79:
                # Разбиваем длинные строки
                if '=' in line and '#' in line:
                    # Комментарии после присваивания
                    parts = line.split('#', 1)
                    if len(parts) == 2:
                        code_part = parts[0].strip()
                        comment_part = parts[1].strip()
                        if len(code_part) > 79:
                            # Разбиваем код
                            fixed_lines.append(code_part)
                            fixed_lines.append(f"    # {comment_part}")
                        else:
                            fixed_lines.append(line)
                    else:
                        fixed_lines.append(line)
                elif 'def ' in line or 'class ' in line:
                    # Определения функций и классов
                    if len(line) > 79:
                        # Простое разбиение
                        fixed_lines.append(line[:79])
                        if line[79:].strip():
                            fixed_lines.append(f"    {line[79:].strip()}")
                    else:
                        fixed_lines.append(line)
                elif 'return ' in line:
                    # Return statements
                    if len(line) > 79:
                        fixed_lines.append(line[:79])
                        if line[79:].strip():
                            fixed_lines.append(f"    {line[79:].strip()}")
                    else:
                        fixed_lines.append(line)
                elif 'if ' in line or 'elif ' in line or 'else:' in line:
                    # Условные операторы
                    if len(line) > 79:
                        fixed_lines.append(line[:79])
                        if line[79:].strip():
                            fixed_lines.append(f"    {line[79:].strip()}")
                    else:
                        fixed_lines.append(line)
                else:
                    # Обычные строки - простое разбиение
                    if len(line) > 79:
                        fixed_lines.append(line[:79])
                        if line[79:].strip():
                            fixed_lines.append(f"    {line[79:].strip()}")
                    else:
                        fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        # Объединяем строки обратно
        fixed_content = '\n'.join(fixed_lines)
        
        # Записываем исправленный файл
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print(f"✅ Исправлены E501 ошибки в {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при исправлении E501: {e}")
        return False

if __name__ == "__main__":
    fix_e501_errors()
