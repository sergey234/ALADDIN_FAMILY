#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для добавления AI Categories Router в main.py
"""

from pathlib import Path
import re

main_py_path = Path('/opt/aladdin-backend/api/main.py')

if not main_py_path.exists():
    # Попробовать другие возможные пути
    possible_paths = [
        Path('/opt/aladdin-backend/main.py'),
        Path('/opt/aladdin-backend/app/main.py'),
    ]
    for path in possible_paths:
        if path.exists():
            main_py_path = path
            break
        else:
            print('❌ main.py не найден!')
            exit(1)

print('📝 Работаю с файлом: ' + str(main_py_path))

# Прочитать файл
with open(main_py_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Создать backup
backup_path = main_py_path.with_suffix('.py.backup_ai_categories')
with open(backup_path, 'w', encoding='utf-8') as f:
    f.write(content)
print(f'✅ Backup создан: {backup_path}')

# Проверить есть ли уже импорт
if 'ai_categories_router' in content:
    print('⚠️  Router уже импортирован!')
    exit(0)

# Найти место для добавления импорта (после других импортов routers)
import_pattern = r'(from\s+security\.api\.routers\.\w+\s+import\s+router[^\n]*)'
matches = list(re.finditer(import_pattern, content))

if matches:
    # Добавить после последнего импорта router
    last_match = matches[-1]
    insert_pos = last_match.end()
    new_import = "\nfrom security.api.routers.ai_categories_router import router as ai_categories_router"
    content = content[:insert_pos] + new_import + content[insert_pos:]
    print('✅ Импорт добавлен')
else:
    # Найти место после всех импортов
    import_lines = []
    for i, line in enumerate(content.split('\n')):
        if line.strip().startswith('import ') or line.strip().startswith('from '):
            import_lines.append(i)

    if import_lines:
        last_import_line = import_lines[-1]
        lines = content.split('\n')
        lines.insert(last_import_line + 1, 'from security.api.routers.ai_categories_router import router as ai_categories_router')
        content = '\n'.join(lines)
        print('✅ Импорт добавлен после других импортов')
    else:
        print('⚠️  Не найдено место для импорта, добавлю в начало')
        content = 'from security.api.routers.ai_categories_router import router as ai_categories_router\n' + content

# Найти место для регистрации роутера (app.include_router)
router_pattern = r'app\.include_router\([^)]+\)'
router_matches = list(re.finditer(router_pattern, content))

if router_matches:
    # Добавить после последнего include_router
    last_match = router_matches[-1]
    insert_pos = last_match.end()
    new_router = """
# Регистрация AI Categories Router
try:
    app.include_router(ai_categories_router)
    print("✅ AI Categories Router зарегистрирован")
except Exception as e:
    print(f"⚠️ Не удалось зарегистрировать AI Categories Router: {e}")
"""
    content = content[:insert_pos] + new_router + content[insert_pos:]
    print('✅ Регистрация роутера добавлена')
else:
    # Найти место после создания app
    app_pattern = r'app\s*=\s*FastAPI\([^)]*\)'
    app_match = re.search(app_pattern, content)
    if app_match:
        insert_pos = app_match.end()
        new_router = """

# Регистрация AI Categories Router
try:
    app.include_router(ai_categories_router)
    print("✅ AI Categories Router зарегистрирован")
except Exception as e:
    print(f"⚠️ Не удалось зарегистрировать AI Categories Router: {e}")
"""
        content = content[:insert_pos] + new_router + content[insert_pos:]
        print('✅ Регистрация роутера добавлена после создания app')
    else:
        print('⚠️  Не найдено место для регистрации роутера')
        print('   Добавьте вручную:')
        print('   app.include_router(ai_categories_router)')
        exit(1)

# Сохранение файла
with open(main_py_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ main.py обновлен')
print()
print('📋 Проверка синтаксиса...')
import subprocess  # noqa: E402
result = subprocess.run(
    ['python3', '-m', 'py_compile', str(main_py_path)],
    capture_output=True, text=True
)
if result.returncode == 0:
    print('✅ Синтаксис корректен')
else:
    print(f'❌ Ошибка синтаксиса: {result.stderr}')
    exit(1)

print()
print('✅ AI Categories Router успешно добавлен в main.py!')
