#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Правильное исправление main.py
"""

from pathlib import Path

main_py_path = Path('/opt/aladdin-backend/main.py')

print(f'📝 Читаю файл: {main_py_path}')

with open(main_py_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Проверить есть ли logger
has_logger = 'logger = logging.getLogger' in content or 'logging.getLogger(__name__)' in content
has_logging = 'import logging' in content

if not has_logger:
    # Найти место для добавления logger
    # После всех импортов, перед app = FastAPI
    app_pos = content.find('app = FastAPI')
    if app_pos > 0:
        # Найти последний импорт перед app
        import_section = content[:app_pos]
        last_import_line = import_section.rfind('\nfrom ') or import_section.rfind('\nimport ')
        if last_import_line > 0:
            insert_pos = content.find('\n', last_import_line + 1)
            if insert_pos > 0:
                if not has_logging:
                    content = content[:insert_pos] + '\nimport logging\n' + content[insert_pos:]
                    insert_pos += len('\nimport logging\n')
                content = content[:insert_pos] + '\nlogger = logging.getLogger(__name__)\n' + content[insert_pos:]
                print('✅ Добавлен logger')

# Проверить импорт dark_web_router
if 'from security.api.routers.dark_web_monitoring_router import router as dark_web_router' not in content:
    # Найти место после других импортов роутеров
    router_imports = []
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'from security.api.routers' in line or 'from app.routers' in line:
            router_imports.append(i)
    
    if router_imports:
        # Вставить после последнего импорта роутера
        last_router_import = router_imports[-1]
        lines.insert(last_router_import + 1, 'from security.api.routers.dark_web_monitoring_router import router as dark_web_router')
        content = '\n'.join(lines)
        print('✅ Добавлен импорт dark_web_router')

# Исправить блок try/except - убедиться что импорт есть ДО try
# Найти блок с dark_web_router
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'app.include_router(dark_web_router)' in line:
        # Проверить что перед этим есть импорт
        before_lines = '\n'.join(lines[:i])
        if 'dark_web_router' not in before_lines.replace('app.include_router(dark_web_router)', ''):
            print(f'❌ Проблема на строке {i+1}: dark_web_router используется без импорта')
            # Найти try блок
            try_line = i - 1
            while try_line >= 0 and not lines[try_line].strip().startswith('try:'):
                try_line -= 1
            
            if try_line >= 0:
                # Импорт должен быть ДО try
                # Проверить есть ли импорт до try
                before_try = '\n'.join(lines[:try_line])
                if 'from security.api.routers.dark_web_monitoring_router import router as dark_web_router' not in before_try:
                    # Добавить импорт перед try
                    lines.insert(try_line, 'from security.api.routers.dark_web_monitoring_router import router as dark_web_router')
                    print('✅ Добавлен импорт перед try блоком')
                    break
        
        # Проверить except блок - должен использовать logger
        for j in range(i, min(i+10, len(lines))):
            if 'except' in lines[j] and 'logger.warning' in lines[j+1] if j+1 < len(lines) else False:
                # Проверить что logger определен
                if not has_logger:
                    # Добавить logger
                    if not has_logging:
                        # Найти место для logging импорта
                        for k in range(j-50, j):
                            if k >= 0 and ('import' in lines[k] or 'from' in lines[k]):
                                lines.insert(k+1, 'import logging')
                                lines.insert(k+2, 'logger = logging.getLogger(__name__)')
                                print('✅ Добавлен logger перед except')
                                break

content = '\n'.join(lines)

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
