#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление __init__.py - обернуть все импорты агентов в try/except
"""

from pathlib import Path

init_file = Path('/opt/aladdin-backend/security/ai_agents/__init__.py')

if not init_file.exists():
    print('❌ __init__.py не найден')
    exit(1)

with open(init_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Создать backup
backup = init_file.with_suffix('.py.backup_fix')
with open(backup, 'w', encoding='utf-8') as f:
    f.write(content)
print(f'✅ Backup создан: {backup}')

# Простое решение: обернуть каждый импорт агента в try/except
lines = content.split('\n')
new_lines = []
skip_next = False

for idx, line in enumerate(lines):
    # Пропустить строки внутри try/except блока
    if skip_next:
        if line.strip().startswith('except') or (line.strip() and not line.startswith(' ') and not line.startswith('\t')):
            skip_next = False
        new_lines.append(line)
        continue
    
    # Проверяем импорты агентов (кроме ai_categories_agent)
    if 'from .' in line and '_agent import' in line and 'ai_categories_agent' not in line:
        # Обернуть в try/except
        indent = len(line) - len(line.lstrip())
        indent_str = ' ' * indent
        new_lines.append(f'{indent_str}try:')
        new_lines.append(f'{indent_str}    {line.strip()}')
        new_lines.append(f'{indent_str}except ImportError:')
        new_lines.append(f'{indent_str}    pass  # Зависимости не установлены')
        skip_next = True
    else:
        new_lines.append(line)

content = '\n'.join(new_lines)

# Сохранить
with open(init_file, 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ __init__.py исправлен - все импорты обернуты в try/except')
