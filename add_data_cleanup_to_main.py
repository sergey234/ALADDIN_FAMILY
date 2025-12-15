#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для интеграции Personal Data Cleanup Router в main.py

Использование:
    python3 add_data_cleanup_to_main.py

Запускать на сервере после регистрации в SFM.
"""

import os
import re
import shutil
from datetime import datetime

# Пути к main.py (проверяем оба возможных расположения)
MAIN_PY_PATHS = [
    "/opt/aladdin-backend/api/main.py",
    "/opt/aladdin-backend/main.py"
]

MAIN_PY_PATH = None
BACKUP_PATH = None

# Находим main.py
for path in MAIN_PY_PATHS:
    if os.path.exists(path):
        MAIN_PY_PATH = path
        BACKUP_PATH = f"{path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        break

if not MAIN_PY_PATH:
    print("❌ Файл main.py не найден ни в одном из мест:")
    for path in MAIN_PY_PATHS:
        print(f"   - {path}")
    exit(1)

print(f"📖 Найден main.py: {MAIN_PY_PATH}")
print("")

# Создание резервной копии
print(f"📋 Создание резервной копии: {BACKUP_PATH}")
shutil.copy2(MAIN_PY_PATH, BACKUP_PATH)
print("✅ Резервная копия создана")
print("")

# Чтение main.py
print("📖 Чтение main.py...")
with open(MAIN_PY_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# Проверка, не добавлен ли уже роутер
if "data_cleanup_router" in content:
    print("⚠️  Router data_cleanup_router уже добавлен в main.py")
    print("   Пропускаю добавление...")
    exit(0)

# Добавление импорта
print("➕ Добавление импорта...")
import_pattern = r"(from security\.api\.routers\.\w+ import router as \w+)"
imports = re.findall(import_pattern, content)

if imports:
    # Находим последний импорт роутера
    last_import = imports[-1]
    new_import = "from security.api.routers.data_cleanup_router import router as data_cleanup_router"
    
    # Добавляем после последнего импорта
    content = content.replace(last_import, f"{last_import}\n{new_import}")
    print(f"✅ Импорт добавлен после: {last_import.split()[-1]}")
else:
    # Если нет других роутеров, добавляем в начало файла после других импортов
    import_section = "from security.api.routers.data_cleanup_router import router as data_cleanup_router"
    # Ищем место после импортов FastAPI
    fastapi_import = re.search(r"(from fastapi import.*?\n)", content)
    if fastapi_import:
        insert_pos = fastapi_import.end()
        content = content[:insert_pos] + import_section + "\n" + content[insert_pos:]
        print("✅ Импорт добавлен после импортов FastAPI")
    else:
        # Добавляем в начало
        content = import_section + "\n\n" + content
        print("✅ Импорт добавлен в начало файла")

print("")

# Добавление регистрации роутера
print("➕ Добавление регистрации роутера...")
router_pattern = r"(app\.include_router\(.*?\)\s*\n)"

# Ищем последнюю регистрацию роутера
router_registrations = re.findall(router_pattern, content, re.MULTILINE)

if router_registrations:
    # Находим последнюю регистрацию
    last_router = router_registrations[-1]
    
    # Добавляем новую регистрацию после последней
    new_router = """try:
    app.include_router(data_cleanup_router)
    print("✅ Data Cleanup Router зарегистрирован")
except Exception as e:
    print(f"⚠️ Не удалось зарегистрировать Data Cleanup Router: {e}")
"""
    
    content = content.replace(last_router, last_router + "\n" + new_router)
    print(f"✅ Регистрация роутера добавлена")
else:
    # Если нет других роутеров, добавляем после создания app
    app_creation = re.search(r"(app\s*=\s*FastAPI\(.*?\)\s*\n)", content)
    if app_creation:
        insert_pos = app_creation.end()
        new_router = """
try:
    app.include_router(data_cleanup_router)
    print("✅ Data Cleanup Router зарегистрирован")
except Exception as e:
    print(f"⚠️ Не удалось зарегистрировать Data Cleanup Router: {e}")
"""
        content = content[:insert_pos] + new_router + content[insert_pos:]
        print("✅ Регистрация роутера добавлена после создания app")
    else:
        print("❌ Не удалось найти место для добавления роутера")
        exit(1)

print("")

# Проверка синтаксиса
print("🔍 Проверка синтаксиса...")
import py_compile
try:
    py_compile.compile(MAIN_PY_PATH, doraise=True)
    print("✅ Синтаксис валиден")
except py_compile.PyCompileError as e:
    print(f"❌ Ошибка синтаксиса: {e}")
    print("🔄 Восстановление из резервной копии...")
    shutil.copy2(BACKUP_PATH, MAIN_PY_PATH)
    exit(1)

print("")

# Сохранение изменений
print("💾 Сохранение изменений...")
with open(MAIN_PY_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ main.py обновлен")
print("")
print("📝 Следующий шаг: Перезапустить сервис")
print("   systemctl restart aladdin-backend")
