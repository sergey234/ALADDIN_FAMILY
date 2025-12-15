#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для исправления отступов в main.py
"""

from pathlib import Path

main_py_path = Path('/opt/aladdin-backend/main.py')

if not main_py_path.exists():
    print(f'❌ main.py не найден!')
    exit(1)

print(f'📝 Работаю с файлом: {main_py_path}')

# Прочитать файл
with open(main_py_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Найти проблемную строку (uvicorn.run с неправильным отступом)
fixed_lines = []
for i, line in enumerate(lines):
    # Исправить отступ для uvicorn.run если он в неправильном блоке
    if 'uvicorn.run' in line and line.startswith('    '):
        # Проверить предыдущие строки - если это конец блока if __name__ == "__main__":
        # то отступ должен быть правильным
        if i > 0 and 'if __name__' in lines[i-1] or '__main__' in lines[i-1]:
            # Правильный отступ для if __name__ блока
            fixed_lines.append('    ' + line.lstrip())
        else:
            # Убрать лишние отступы
            fixed_lines.append(line.lstrip())
    else:
        fixed_lines.append(line)

# Сохранить
with open(main_py_path, 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print('✅ Отступы исправлены!')

# Проверка синтаксиса
import py_compile
try:
    py_compile.compile(str(main_py_path), doraise=True)
    print('✅ Синтаксис правильный!')
except py_compile.PyCompileError as e:
    print(f'❌ Ошибка синтаксиса: {e}')
    exit(1)
