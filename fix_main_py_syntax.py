#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление синтаксической ошибки в main.py и правильная интеграция AI Categories Router
"""

from pathlib import Path
import re

main_py_path = Path('/opt/aladdin-backend/main.py')

if not main_py_path.exists():
    print(f'❌ main.py не найден: {main_py_path}')
    exit(1)

print(f'📝 Работаю с файлом: {main_py_path}')

# Прочитать файл
with open(main_py_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Проверить есть ли уже ai_categories_router
if 'ai_categories_router' in content:
    print('⚠️  Router уже импортирован!')
    # Но проверим синтаксис
    import subprocess
    result = subprocess.run(['python3', '-m', 'py_compile', str(main_py_path)], 
                           capture_output=True, text=True)
    if result.returncode == 0:
        print('✅ Синтаксис корректен')
        exit(0)
    else:
        print('❌ Есть синтаксическая ошибка, исправляю...')

# Создать backup
backup_path = main_py_path.with_suffix('.py.backup_ai_categories_fix')
with open(backup_path, 'w', encoding='utf-8') as f:
    f.write(content)
print(f'✅ Backup создан: {backup_path}')

# Добавить импорт после dark_web_monitoring_router
if 'from security.api.routers.ai_categories_router' not in content:
    # Найти импорт dark_web_monitoring_router
    dark_web_import_pattern = r'(from\s+security\.api\.routers\.dark_web_monitoring_router\s+import\s+router[^\n]*)'
    match = re.search(dark_web_import_pattern, content)
    if match:
        insert_pos = match.end()
        new_import = "\nfrom security.api.routers.ai_categories_router import router as ai_categories_router"
        content = content[:insert_pos] + new_import + content[insert_pos:]
        print('✅ Импорт добавлен')
    else:
        # Найти любой импорт router
        import_pattern = r'(from\s+security\.api\.routers\.\w+\s+import\s+router[^\n]*)'
        matches = list(re.finditer(import_pattern, content))
        if matches:
            last_match = matches[-1]
            insert_pos = last_match.end()
            new_import = "\nfrom security.api.routers.ai_categories_router import router as ai_categories_router"
            content = content[:insert_pos] + new_import + content[insert_pos:]
            print('✅ Импорт добавлен')

# Найти место для регистрации - после последнего полного блока try/except
# Ищем все блоки try/except
lines = content.split('\n')
router_insert_line = None

# Найти последний include_router
for i in range(len(lines) - 1, -1, -1):
    if 'app.include_router' in lines[i]:
        # Найти конец блока try/except для этого router
        j = i
        # Ищем соответствующий except
        try_level = 0
        found_try = False
        while j < len(lines):
            if 'try:' in lines[j] and not found_try:
                try_level = 1
                found_try = True
            elif 'try:' in lines[j]:
                try_level += 1
            elif ('except' in lines[j] or 'finally' in lines[j]) and try_level > 0:
                try_level -= 1
                if try_level == 0:
                    # Нашли конец блока
                    router_insert_line = j + 1
                    break
            j += 1
        
        if router_insert_line is None:
            # Если не нашли except, добавим после следующей пустой строки
            for k in range(i + 1, min(i + 10, len(lines))):
                if lines[k].strip() == '':
                    router_insert_line = k + 1
                    break
            if router_insert_line is None:
                router_insert_line = i + 5
        
        break

if router_insert_line is None:
    # Добавить в конец перед if __name__
    if '__name__' in content:
        name_pos = content.find('if __name__')
        router_insert_line = content[:name_pos].count('\n')
    else:
        router_insert_line = len(lines)

# Вставить регистрацию router
new_router_lines = [
    '',
    '# Регистрация AI Categories Router',
    'try:',
    '    app.include_router(ai_categories_router)',
    '    print("✅ AI Categories Router зарегистрирован")',
    'except Exception as e:',
    '    print(f"⚠️ Не удалось зарегистрировать AI Categories Router: {e}")',
    ''
]

for line in reversed(new_router_lines):
    lines.insert(router_insert_line, line)

content = '\n'.join(lines)

# Сохранить
with open(main_py_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'✅ main.py обновлен')

# Проверка синтаксиса
import subprocess
result = subprocess.run(['python3', '-m', 'py_compile', str(main_py_path)], 
                       capture_output=True, text=True)
if result.returncode == 0:
    print('✅ Синтаксис корректен')
else:
    print(f'❌ Ошибка синтаксиса: {result.stderr}')
    exit(1)
