#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Правильное исправление main.py
"""

from pathlib import Path

main_py_path = Path('/opt/aladdin-backend/main.py')

with open(main_py_path, 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')

# Найти блок if __name__ и исправить его
for i, line in enumerate(lines):
    if 'if __name__' in line:
        print(f'📋 Найден if __name__ на строке {i+1}')
        # Проверить следующие строки
        for j in range(i+1, min(i+10, len(lines))):
            if 'import uvicorn' in lines[j] or 'uvicorn.run' in lines[j]:
                # Должен быть отступ 4 пробела
                if not lines[j].startswith('    '):
                    lines[j] = '    ' + lines[j].lstrip()
                    print(f'✅ Исправлен отступ на строке {j+1}: {lines[j][:50]}')
        break

# Проверить нет ли дубликатов import uvicorn
uvicorn_imports = []
for i, line in enumerate(lines):
    if 'import uvicorn' in line:
        uvicorn_imports.append(i)

if len(uvicorn_imports) > 1:
    print(f'⚠️  Найдено {len(uvicorn_imports)} импортов uvicorn')
    # Оставить только первый (в блоке if __name__)
    for idx in uvicorn_imports[1:]:
        lines[idx] = ''
        print(f'✅ Удален дубликат на строке {idx+1}')

content = '\n'.join(lines)

# Сохранить
with open(main_py_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ main.py обновлен!')

# Проверка
try:
    compile(content, str(main_py_path), 'exec')
    print('✅ Синтаксис правильный!')
except SyntaxError as e:
    print(f'❌ Ошибка синтаксиса: {e}')
    print(f'   Строка {e.lineno}: {e.text}')
    exit(1)
