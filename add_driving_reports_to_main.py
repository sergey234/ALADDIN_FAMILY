#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для добавления driving_reports_router в main.py

Использование:
    python3 add_driving_reports_to_main.py

Дата создания: 12 декабря 2025
"""

import shutil
from pathlib import Path
from datetime import datetime

# Пути
MAIN_PY_PATH = Path("/opt/aladdin-backend/main.py")
BACKUP_PATH = MAIN_PY_PATH.with_suffix(f".py.backup_driving_reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

# Импорт и регистрация
IMPORT_LINE = "from security.api.routers.driving_reports_router import driving_reports_router"
ROUTER_LINE = "app.include_router(driving_reports_router, prefix=\"/api/driving-reports\", tags=[\"driving-reports\"])"


def main():
    print("=" * 60)
    print("ДОБАВЛЕНИЕ DRIVING REPORTS ROUTER В MAIN.PY")
    print("=" * 60)

    # Проверка файла
    if not MAIN_PY_PATH.exists():
        print(f"❌ Файл main.py не найден: {MAIN_PY_PATH}")
        return False

    # Создание backup
    print(f"\n📦 Создание backup: {BACKUP_PATH}")
    shutil.copy2(MAIN_PY_PATH, BACKUP_PATH)
    print("✅ Backup создан")

    # Чтение файла
    print(f"\n📖 Чтение файла: {MAIN_PY_PATH}")
    with open(MAIN_PY_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # Проверка существования
    if IMPORT_LINE in content:
        print(f"\n⚠️ Импорт уже существует: {IMPORT_LINE}")
    else:
        # Поиск места для импорта (после других router импортов)
        import_patterns = [
            "from security.api.routers.crash_detection_router import",
            "from security.api.routers.ai_categories_router import",
            "from security.api.routers import"
        ]

        insert_pos = -1
        for pattern in import_patterns:
            pos = content.find(pattern)
            if pos != -1:
                # Находим конец строки
                insert_pos = content.find('\n', pos) + 1
                break

        if insert_pos == -1:
            # Ищем любое место с router импортами
            pos = content.find("from security.api.routers")
            if pos != -1:
                insert_pos = content.find('\n', pos) + 1
            else:
                # Ищем место после импортов FastAPI
                pos = content.find("from fastapi import")
                if pos != -1:
                    insert_pos = content.find('\n', content.find('\n', pos) + 1) + 1

        if insert_pos == -1:
            print("❌ Не найдено место для вставки импорта")
            return False

        content = content[:insert_pos] + IMPORT_LINE + "\n" + content[insert_pos:]
        print("✅ Импорт добавлен: " + IMPORT_LINE)

    if ROUTER_LINE in content:
        print("\n⚠️ Регистрация router уже существует: " + ROUTER_LINE)
    else:
        # Поиск места для регистрации (после других router регистраций)
        router_patterns = [
            "app.include_router(crash_detection_router",
            "app.include_router(ai_categories_router",
            "app.include_router("
        ]

        insert_pos = -1
        for pattern in router_patterns:
            pos = content.find(pattern)
            if pos != -1:
                # Находим конец строки
                insert_pos = content.find('\n', pos) + 1
                break

        if insert_pos == -1:
            # Ищем место после создания app
            pos = content.find("app = FastAPI")
            if pos != -1:
                # Ищем конец блока инициализации
                insert_pos = content.find('\n\n', pos) + 2
            else:
                print("❌ Не найдено место для вставки регистрации router")
                return False

        content = content[:insert_pos] + ROUTER_LINE + "\n" + content[insert_pos:]
        print(f"✅ Регистрация router добавлена: {ROUTER_LINE}")

    # Сохранение
    print("\n💾 Сохранение файла...")
    with open(MAIN_PY_PATH, 'w', encoding='utf-8') as f:
        f.write(content)

    # Проверка синтаксиса
    print("\n🔍 Проверка синтаксиса Python...")
    import py_compile
    try:
        py_compile.compile(str(MAIN_PY_PATH), doraise=True)
        print("✅ Синтаксис корректен")
    except py_compile.PyCompileError as e:
        print("❌ Ошибка синтаксиса: " + str(e))
        print("\n⚠️ Восстановление из backup...")
        shutil.copy2(BACKUP_PATH, MAIN_PY_PATH)
        return False

    print("\n✅ Интеграция в main.py завершена успешно!")
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
