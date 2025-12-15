#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Чистое исправление main.py - удалить все ошибки
"""

from pathlib import Path

main_py_path = Path('/opt/aladdin-backend/main.py')

with open(main_py_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Найти и удалить все uvicorn.run которые не в блоке if __name__
lines = content.split('\n')

# Найти все uvicorn.run
uvicorn_runs = []
for i, line in enumerate(lines):
    if 'uvicorn.run' in line:
        uvicorn_runs.append(i)

# Найти блок if __name__
if_main_line = None
for i, line in enumerate(lines):
    if 'if __name__' in line:
        if_main_line = i
        break

if if_main_line is None:
    print('❌ Блок if __name__ не найден!')
    exit(1)

print(f'📋 Блок if __name__ на строке {if_main_line + 1}')

# Удалить все uvicorn.run которые не в блоке if __name__
for uvicorn_line in uvicorn_runs:
    if uvicorn_line < if_main_line or uvicorn_line > if_main_line + 10:
        print(f'✅ Удален uvicorn.run на строке {uvicorn_line + 1} (не в блоке if __name__)')
        lines[uvicorn_line] = ''

# Убедиться что в блоке if __name__ есть import uvicorn и uvicorn.run
found_import = False
found_run = False
for i in range(if_main_line, min(if_main_line + 10, len(lines))):
    if 'import uvicorn' in lines[i]:
        found_import = True
        # Проверить отступ
        if not lines[i].startswith('    '):
            lines[i] = '    ' + lines[i].lstrip()
            print(f'✅ Исправлен отступ import uvicorn на строке {i+1}')
    if 'uvicorn.run' in lines[i]:
        found_run = True
        # Проверить отступ
        if not lines[i].startswith('    '):
            lines[i] = '    ' + lines[i].lstrip()
            print(f'✅ Исправлен отступ uvicorn.run на строке {i+1}')

# Добавить если нет
if not found_import:
    lines.insert(if_main_line + 1, '    import uvicorn')
    print(f'✅ Добавлен import uvicorn')
    if_main_line += 1

if not found_run:
    # Найти где вставить (после import uvicorn)
    for i in range(if_main_line, min(if_main_line + 10, len(lines))):
        if 'import uvicorn' in lines[i]:
            lines.insert(i + 1, '    uvicorn.run(app, host="0.0.0.0", port=8000)')
            print(f'✅ Добавлен uvicorn.run')
            break

# Удалить пустые строки но оставить структуру
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
    print(f'❌ Ошибка на строке {e.lineno}')
    exit(1)
