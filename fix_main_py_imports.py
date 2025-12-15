#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление импортов в main.py
"""

from pathlib import Path
import re

main_py_path = Path('/opt/aladdin-backend/main.py')

if not main_py_path.exists():
    print(f'❌ main.py не найден!')
    exit(1)

print(f'📝 Работаю с файлом: {main_py_path}')

# Прочитать файл
with open(main_py_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Проверить что logger определен
if 'logger' not in content or 'import logging' not in content:
    print('⚠️  logger не найден, нужно добавить')
    # Найти место для добавления
    if 'import logging' not in content:
        # Добавить после других импортов
        import_pattern = r'(^from\s+\w+.*$)'
        matches = list(re.finditer(import_pattern, content, re.MULTILINE))
        if matches:
            last_import = matches[-1]
            insert_pos = last_import.end()
            content = content[:insert_pos] + '\nimport logging\n\nlogger = logging.getLogger(__name__)\n' + content[insert_pos:]
            print('✅ Добавлен import logging и logger')

# Найти проблемный блок с dark_web_router
# Проблема: dark_web_router используется в try, но импорт может быть внутри try
pattern = r'(try:\s*\n\s*app\.include_router\(dark_web_router\))'

if re.search(pattern, content):
    print('❌ Найдена проблема: dark_web_router используется без импорта')
    
    # Найти где должен быть импорт
    # Ищем все импорты routers
    router_import_pattern = r'from\s+security\.api\.routers\.\w+\s+import\s+router'
    router_imports = list(re.finditer(router_import_pattern, content))
    
    if router_imports:
        # Добавить импорт после последнего импорта router
        last_import = router_imports[-1]
        if 'dark_web_monitoring_router' not in content[:last_import.end()]:
            insert_pos = last_import.end()
            content = content[:insert_pos] + '\nfrom security.api.routers.dark_web_monitoring_router import router as dark_web_router' + content[insert_pos:]
            print('✅ Добавлен импорт dark_web_router')
    
    # Исправить блок try/except - убедиться что импорт есть
    try_pattern = r'try:\s*\n\s*from security\.api\.routers\.dark_web_monitoring_router import router as dark_web_router'
    if not re.search(try_pattern, content):
        # Найти блок try с dark_web_router
        try_block_pattern = r'(try:\s*\n\s*app\.include_router\(dark_web_router\))'
        match = re.search(try_block_pattern, content)
        if match:
            # Заменить на правильный блок
            old_block = match.group(1)
            new_block = '''try:
    app.include_router(dark_web_router)
    logger.info("✅ Dark Web Monitoring Router зарегистрирован")'''
            content = content.replace(old_block, new_block)
            print('✅ Исправлен блок try/except')

# Проверить что logger используется правильно в except
if 'logger.warning' in content and 'logger = logging.getLogger' not in content[:content.find('logger.warning')]:
    # Найти где используется logger.warning для dark_web
    warning_pattern = r'logger\.warning\(f"⚠️.*dark.*web.*router.*:.*{e}"\)'
    if re.search(warning_pattern, content, re.IGNORECASE):
        print('✅ logger используется для dark_web')

# Сохранить
with open(main_py_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ main.py обновлен!')

# Проверка синтаксиса
import py_compile
try:
    py_compile.compile(str(main_py_path), doraise=True)
    print('✅ Синтаксис правильный!')
except py_compile.PyCompileError as e:
    print(f'❌ Ошибка синтаксиса: {e}')
    exit(1)
