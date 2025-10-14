#!/usr/bin/env python3
"""
Исправление пробелов в пустых строках (W293) для TrustScoring
"""

import re

def fix_w293_errors():
    """Исправляет W293 ошибки в trust_scoring.py"""
    
    file_path = "security/preliminary/trust_scoring.py"
    
    try:
        # Читаем файл
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Исправляем W293 - убираем пробелы в пустых строках
        # Заменяем строки, содержащие только пробелы, на пустые строки
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Если строка содержит только пробелы или табы - делаем её пустой
            if line.strip() == '':
                fixed_lines.append('')
            else:
                fixed_lines.append(line)
        
        # Объединяем строки обратно
        fixed_content = '\n'.join(fixed_lines)
        
        # Записываем исправленный файл
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print(f"✅ Исправлены W293 ошибки в {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при исправлении W293: {e}")
        return False

if __name__ == "__main__":
    fix_w293_errors()
