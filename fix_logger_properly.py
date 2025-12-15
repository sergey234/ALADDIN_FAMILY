#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Правильное исправление logger в main.py
"""

from pathlib import Path

main_py_path = Path('/opt/aladdin-backend/main.py')

print(f'📝 Читаю файл: {main_py_path}')

with open(main_py_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Найти где используется logger для dark_web
dark_web_line = None
for i, line in enumerate(lines):
    if 'dark_web' in line.lower() and 'logger' in line.lower():
        dark_web_line = i
        break

if dark_web_line is None:
    print('❌ Не найдено использование logger для dark_web')
    exit(1)

print(f'📋 Найдено использование logger на строке {dark_web_line + 1}')

# Найти где определен logger
logger_def_line = None
for i in range(dark_web_line):
    if 'logger = logging.getLogger' in lines[i] or 'logger =' in lines[i] and 'logging' in lines[i]:
        logger_def_line = i
        break

if logger_def_line is None:
    print('⚠️  Logger не найден до использования dark_web')
    # Найти импорт logging
    logging_import_line = None
    for i in range(dark_web_line):
        if 'import logging' in lines[i]:
            logging_import_line = i
            break
    
    if logging_import_line is not None:
        # Добавить logger после импорта logging
        lines.insert(logging_import_line + 1, 'logger = logging.getLogger(__name__)\n')
        print(f'✅ Добавлен logger после импорта logging (строка {logging_import_line + 2})')
    else:
        # Добавить и импорт и logger
        # Найти последний импорт
        last_import_line = None
        for i in range(min(50, dark_web_line)):
            if lines[i].strip().startswith('import ') or lines[i].strip().startswith('from '):
                last_import_line = i
        
        if last_import_line is not None:
            lines.insert(last_import_line + 1, 'import logging\n')
            lines.insert(last_import_line + 2, 'logger = logging.getLogger(__name__)\n')
            print(f'✅ Добавлены import logging и logger (после строки {last_import_line + 1})')
else:
    print(f'✅ Logger найден на строке {logger_def_line + 1}')

# Сохранить
with open(main_py_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('✅ main.py обновлен!')

# Проверка синтаксиса
import py_compile
try:
    py_compile.compile(str(main_py_path), doraise=True)
    print('✅ Синтаксис правильный!')
except py_compile.PyCompileError as e:
    print(f'❌ Ошибка синтаксиса: {e}')
    exit(1)
