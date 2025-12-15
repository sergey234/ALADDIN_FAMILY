#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление отступов в main.py
"""

from pathlib import Path

main_py_path = Path('/opt/aladdin-backend/main.py')

with open(main_py_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Найти блок if __name__ == "__main__":
for i, line in enumerate(lines):
    if 'if __name__' in line:
        # Проверить следующие строки
        j = i + 1
        while j < len(lines) and j < i + 10:
            if 'uvicorn.run' in lines[j]:
                # Проверить отступ
                if lines[j].startswith('    ') and lines[i].startswith('if'):
                    # Правильный отступ - все ок
                    pass
                elif not lines[j].startswith('    '):
                    # Неправильный отступ - исправить
                    lines[j] = '    ' + lines[j].lstrip()
                    print(f'✅ Исправлен отступ на строке {j+1}')
            if 'import uvicorn' in lines[j]:
                # Проверить отступ
                if not lines[j].startswith('    '):
                    lines[j] = '    ' + lines[j].lstrip()
                    print(f'✅ Исправлен отступ import uvicorn на строке {j+1}')
            j += 1

# Сохранить
with open(main_py_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('✅ Отступы исправлены!')

# Проверка
import py_compile
try:
    py_compile.compile(str(main_py_path), doraise=True)
    print('✅ Синтаксис правильный!')
except Exception as e:
    print(f'❌ Ошибка: {e}')
    exit(1)
