#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт интеграции Location Bubble Router в main.py
Дата: 12 декабря 2025
"""

import os
import shutil
import re
from datetime import datetime
from pathlib import Path

# Пути (проверяем оба возможных расположения)
MAIN_PY_PATHS = [
    "/opt/aladdin-backend/api/main.py",
    "/opt/aladdin-backend/main.py"
]
MAIN_PY_PATH = None
BACKUP_PATH = None

# Импорт и регистрация router
IMPORT_LINE = "from security.api.routers.location_bubble_router import router as location_bubble_router"
REGISTER_LINE = "app.include_router(location_bubble_router)"

def main():
    global MAIN_PY_PATH, BACKUP_PATH
    
    print("=== ИНТЕГРАЦИЯ LOCATION BUBBLE ROUTER В MAIN.PY ===\n")
    
    # 1. Поиск main.py
    for path in MAIN_PY_PATHS:
        if os.path.exists(path):
            MAIN_PY_PATH = path
            BACKUP_PATH = f"{path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            break
    
    if MAIN_PY_PATH is None:
        print(f"❌ Файл main.py не найден ни в одном из мест:")
        for path in MAIN_PY_PATHS:
            print(f"   - {path}")
        return 1
    
    print(f"✅ Найден main.py: {MAIN_PY_PATH}")
    
    # Создание backup
    shutil.copy2(MAIN_PY_PATH, BACKUP_PATH)
    print(f"✅ Backup создан: {BACKUP_PATH}")
    
    # 2. Чтение файла
    with open(MAIN_PY_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 3. Проверка, не добавлен ли уже
    if "location_bubble_router" in content:
        print("⚠️  Location Bubble Router уже интегрирован!")
        response = input("Перезаписать? (y/n): ")
        if response.lower() != 'y':
            print("Отменено")
            return 0
    
    # 4. Добавление импорта
    if IMPORT_LINE not in content:
        # Ищем место для импорта (после других router импортов)
        import_pattern = r'(from security\.api\.routers\.\w+_router import router as \w+_router)'
        matches = list(re.finditer(import_pattern, content))
        
        if matches:
            # Добавляем после последнего router импорта
            last_match = matches[-1]
            insert_pos = last_match.end()
            content = content[:insert_pos] + '\n' + IMPORT_LINE + content[insert_pos:]
            print("✅ Импорт добавлен")
        else:
            # Добавляем в начало файла после других импортов
            import_section = re.search(r'(^from fastapi import.*?\n)', content, re.MULTILINE)
            if import_section:
                insert_pos = import_section.end()
                content = content[:insert_pos] + '\n' + IMPORT_LINE + '\n' + content[insert_pos:]
                print("✅ Импорт добавлен")
            else:
                print("⚠️  Не найдено место для импорта, добавьте вручную")
    
    # 5. Добавление регистрации router
    if REGISTER_LINE not in content:
        # Ищем место для регистрации (после других router регистраций)
        # Важно: ищем строки, которые НЕ внутри try/except блоков
        register_pattern = r'(app\.include_router\(\w+_router\))'
        matches = list(re.finditer(register_pattern, content))
        
        if matches:
            # Находим последнюю регистрацию, которая НЕ внутри try блока
            last_match = None
            for match in reversed(matches):
                # Проверяем, что это не внутри try блока
                before_match = content[:match.start()]
                # Считаем открывающие и закрывающие try/except
                try_count = before_match.count('try:') - before_match.count('except')
                if try_count == 0:
                    last_match = match
                    break
            
            if last_match:
                # Добавляем после последней регистрации
                insert_pos = last_match.end()
                # Находим конец строки
                next_newline = content.find('\n', insert_pos)
                if next_newline != -1:
                    insert_pos = next_newline + 1
                content = content[:insert_pos] + REGISTER_LINE + '\n' + content[insert_pos:]
                print("✅ Регистрация router добавлена")
            else:
                # Если все регистрации внутри try, добавляем после последнего except
                except_pattern = r'(except\s+.*?:\s*\n\s*print\([^)]*\)\s*\n)'
                except_match = re.search(except_pattern, content, re.MULTILINE | re.DOTALL)
                if except_match:
                    insert_pos = except_match.end()
                    content = content[:insert_pos] + '\n' + REGISTER_LINE + '\n' + content[insert_pos:]
                    print("✅ Регистрация router добавлена после except блока")
                else:
                    print("⚠️  Не найдено безопасное место для регистрации")
        else:
            # Ищем место после создания app, но вне try блоков
            app_pattern = r'(app\s*=\s*FastAPI\([^)]*\))'
            match = re.search(app_pattern, content)
            if match:
                insert_pos = match.end()
                # Ищем конец строки
                next_newline = content.find('\n', insert_pos)
                if next_newline != -1:
                    insert_pos = next_newline + 1
                # Проверяем, что не внутри try
                before_pos = content[:insert_pos]
                if before_pos.count('try:') == before_pos.count('except'):
                    content = content[:insert_pos] + '\n' + REGISTER_LINE + '\n' + content[insert_pos:]
                    print("✅ Регистрация router добавлена")
                else:
                    print("⚠️  Не найдено безопасное место для регистрации")
            else:
                print("⚠️  Не найдено место для регистрации, добавьте вручную")
    
    # 6. Сохранение
    with open(MAIN_PY_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 7. Проверка синтаксиса
    import subprocess
    result = subprocess.run(['python3', '-m', 'py_compile', MAIN_PY_PATH], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Синтаксис проверен")
    else:
        print(f"⚠️  Ошибка синтаксиса: {result.stderr}")
        print("Восстановление из backup...")
        shutil.copy2(BACKUP_PATH, MAIN_PY_PATH)
        return 1
    
    print("\n✅ Интеграция завершена!")
    print(f"   - Импорт: {IMPORT_LINE}")
    print(f"   - Регистрация: {REGISTER_LINE}")
    
    return 0

if __name__ == "__main__":
    exit(main())
