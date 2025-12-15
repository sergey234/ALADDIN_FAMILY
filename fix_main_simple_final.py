#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простое финальное исправление
"""

from pathlib import Path

main_py_path = Path('/opt/aladdin-backend/main.py')

with open(main_py_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Найти блок if __name__ и исправить полностью
for i, line in enumerate(lines):
    if 'if __name__' in line:
        # Убедиться что следующая строка - это import uvicorn с правильным отступом
        if i + 1 < len(lines):
            if 'import uvicorn' not in lines[i + 1]:
                # Добавить import uvicorn
                lines.insert(i + 1, '    import uvicorn\n')
                print(f'✅ Добавлен import uvicorn на строке {i+2}')
        
        # Найти uvicorn.run и исправить отступ
        for j in range(i + 1, min(i + 10, len(lines))):
            if 'uvicorn.run' in lines[j]:
                # Должен быть отступ 4 пробела
                if not lines[j].startswith('    '):
                    lines[j] = '    ' + lines[j].lstrip()
                    print(f'✅ Исправлен отступ uvicorn.run на строке {j+1}')
                break
        
        # Удалить все дубликаты import uvicorn после этого блока
        found_first = False
        for j in range(i, min(i + 10, len(lines))):
            if 'import uvicorn' in lines[j]:
                if found_first:
                    # Это дубликат - удалить
                    lines[j] = ''
                    print(f'✅ Удален дубликат import uvicorn на строке {j+1}')
                else:
                    found_first = True
        break

# Удалить пустые строки
lines = [line for line in lines if line.strip() or line == '\n']

# Сохранить
with open(main_py_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('✅ main.py обновлен!')

# Проверка
try:
    compile(''.join(lines), str(main_py_path), 'exec')
    print('✅ Синтаксис правильный!')
except SyntaxError as e:
    print(f'❌ Ошибка синтаксиса на строке {e.lineno}')
    # Показать проблемную область
    start = max(0, e.lineno - 3)
    end = min(len(lines), e.lineno + 2)
    for i in range(start, end):
        marker = '>>>' if i == e.lineno - 1 else '   '
        print(f'{marker} {i+1}: {lines[i].rstrip()}')
    exit(1)
