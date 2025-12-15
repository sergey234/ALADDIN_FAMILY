#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простое исправление - добавить logger перед использованием
"""

from pathlib import Path

main_py_path = Path('/opt/aladdin-backend/main.py')

with open(main_py_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Простое решение: заменить logger на print в блоке dark_web, ИЛИ добавить проверку

# Найти блок с dark_web_router
lines = content.split('\n')

# Найти строку с dark_web
for i, line in enumerate(lines):
    if 'dark_web_router' in line and 'app.include_router' in line:
        # Найти начало try блока
        try_line = i - 1
        while try_line >= 0 and not lines[try_line].strip().startswith('try:'):
            try_line -= 1
        
        if try_line >= 0:
            # Проверить есть ли logger перед try
            before_try = '\n'.join(lines[:try_line])
            if 'logger' not in before_try or 'logger =' not in before_try:
                # Найти где определены logger или добавить
                # Поиск import logging
                logging_line = None
                for j in range(try_line):
                    if 'import logging' in lines[j]:
                        logging_line = j
                        break
                
                if logging_line is not None:
                    # Проверить есть ли logger после импорта
                    found_logger = False
                    for j in range(logging_line + 1, try_line):
                        if 'logger = logging.getLogger' in lines[j]:
                            found_logger = True
                            break
                    
                    if not found_logger:
                        lines.insert(logging_line + 1, 'logger = logging.getLogger(__name__)')
                        print(f'✅ Добавлен logger после импорта logging (строка {logging_line + 2})')
                else:
                    # Добавить и logging и logger
                    # Найти последний импорт
                    last_import = None
                    for j in range(try_line):
                        if lines[j].strip().startswith('import ') or lines[j].strip().startswith('from '):
                            last_import = j
                    
                    if last_import is not None:
                        lines.insert(last_import + 1, 'import logging')
                        lines.insert(last_import + 2, 'logger = logging.getLogger(__name__)')
                        print(f'✅ Добавлены import logging и logger')
            else:
                print('✅ Logger уже определен')
        
        break

content = '\n'.join(lines)

# Сохранить
with open(main_py_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ main.py обновлен!')

# Проверка
import py_compile
try:
    py_compile.compile(str(main_py_path), doraise=True)
    print('✅ Синтаксис правильный!')
except Exception as e:
    print(f'❌ Ошибка: {e}')
    exit(1)
