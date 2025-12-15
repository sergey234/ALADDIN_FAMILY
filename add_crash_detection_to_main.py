#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для добавления Crash Detection Router в main.py

Использование:
    python3 add_crash_detection_to_main.py

Дата создания: 12 декабря 2025
"""

import re
import shutil
from pathlib import Path
from datetime import datetime

# Пути
MAIN_PY_PATH = Path("/opt/aladdin-backend/main.py")
BACKUP_PATH = MAIN_PY_PATH.with_suffix(f".py.backup_crash_detection_{datetime.now().strftime('%Y%m%d_%H%M%S')}")


def main():
    print("=" * 60)
    print("ДОБАВЛЕНИЕ CRASH DETECTION ROUTER В MAIN.PY")
    print("=" * 60)

    if not MAIN_PY_PATH.exists():
        print(f"❌ main.py не найден: {MAIN_PY_PATH}")
        return False

    # Создание backup
    print(f"\n📦 Создание backup: {BACKUP_PATH}")
    shutil.copy2(MAIN_PY_PATH, BACKUP_PATH)
    print("✅ Backup создан")

    # Чтение main.py
    print("\n📖 Чтение main.py...")
    with open(MAIN_PY_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # Проверка существования
    if "crash_detection_router" in content:
        print("⚠️ Crash Detection Router уже добавлен в main.py")
        response = input("Продолжить? (y/n): ")
        if response.lower() != 'y':
            print("❌ Отменено")
            return False

    # Поиск места для импорта (после других router импортов)
    import_pattern = r'(from security\.api\.routers\.\w+_router import router as \w+_router)'
    imports = list(re.finditer(import_pattern, content))

    if imports:
        # Вставляем после последнего импорта router
        last_import = imports[-1]
        insert_pos = last_import.end()
        new_import = "\nfrom security.api.routers.crash_detection_router import router as crash_detection_router"
        content = content[:insert_pos] + new_import + content[insert_pos:]
        print("✅ Импорт добавлен")
    else:
        # Если нет других router импортов, ищем место после других импортов
        import_section = re.search(r'(^from .* import .*$)', content, re.MULTILINE)
        if import_section:
            insert_pos = import_section.end()
            new_import = "\nfrom security.api.routers.crash_detection_router import router as crash_detection_router"
            content = content[:insert_pos] + new_import + content[insert_pos:]
            print("✅ Импорт добавлен")
        else:
            print("⚠️ Не найдено место для импорта, добавляем в начало")
            content = "from security.api.routers.crash_detection_router import router as crash_detection_router\n" + content

    # Поиск места для регистрации router (после других router регистраций)
    router_pattern = r'(app\.include_router\(\w+_router\))'
    routers = list(re.finditer(router_pattern, content))

    if routers:
        # Вставляем после последнего router
        last_router = routers[-1]
        # Находим конец блока try/except для последнего router
        after_router = content[last_router.end():]
        # Ищем конец try/except блока
        except_match = re.search(r'except.*?:\s*.*?print\(.*?\)', after_router, re.DOTALL)
        if except_match:
            insert_pos = last_router.end() + except_match.end()
        else:
            insert_pos = last_router.end()

        new_router = """
try:
    app.include_router(crash_detection_router)
    print("✅ Crash Detection Router зарегистрирован")
except Exception as e:
    print(f"⚠️ Не удалось зарегистрировать Crash Detection Router: {e}")
"""
        content = content[:insert_pos] + new_router + content[insert_pos:]
        print("✅ Регистрация router добавлена")
    else:
        # Если нет других router, ищем место после создания app
        app_pattern = r'(app\s*=\s*FastAPI\([^)]*\))'
        app_match = re.search(app_pattern, content)
        if app_match:
            insert_pos = app_match.end()
            new_router = """
try:
    app.include_router(crash_detection_router)
    print("✅ Crash Detection Router зарегистрирован")
except Exception as e:
    print(f"⚠️ Не удалось зарегистрировать Crash Detection Router: {e}")
"""
            content = content[:insert_pos] + new_router + content[insert_pos:]
            print("✅ Регистрация router добавлена")
        else:
            print("❌ Не найдено место для регистрации router")
            return False

    # Сохранение
    print("\n💾 Сохранение main.py...")
    with open(MAIN_PY_PATH, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ main.py обновлен")

    # Проверка синтаксиса
    print("\n🔍 Проверка синтаксиса...")
    import subprocess
    result = subprocess.run(
        ['python3', '-m', 'py_compile', str(MAIN_PY_PATH)],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print("✅ Синтаксис корректен")
    else:
        print(f"❌ Ошибка синтаксиса: {result.stderr}")
        print("🔄 Восстановление из backup...")
        shutil.copy2(BACKUP_PATH, MAIN_PY_PATH)
        return False

    print("\n✅ Интеграция завершена успешно!")
    return True


if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
