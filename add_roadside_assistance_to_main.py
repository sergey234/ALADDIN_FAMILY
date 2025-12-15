#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для добавления Roadside Assistance Router в main.py

Использование:
    python3 add_roadside_assistance_to_main.py

Запускать на сервере после копирования файлов.
"""

import os
import re
from datetime import datetime

# Пути
MAIN_PY_PATH = "/opt/aladdin-backend/main.py"
BACKUP_PATH = f"/opt/aladdin-backend/main.py.backup_roadside_assistance_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def main():
    print("🔧 Добавление Roadside Assistance Router в main.py")
    print("")

    # Проверка существования файла
    if not os.path.exists(MAIN_PY_PATH):
        print(f"❌ Файл не найден: {MAIN_PY_PATH}")
        return False

    # Создание резервной копии
    print(f"📋 Создание резервной копии: {BACKUP_PATH}")
    with open(MAIN_PY_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    with open(BACKUP_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Резервная копия создана")
    print("")

    # Проверка, не добавлен ли уже
    if "roadside_assistance_router" in content:
        print("⚠️  Roadside Assistance Router уже добавлен в main.py")
        return True

    # Поиск места для добавления импорта (после других router импортов)
    import_pattern = r"(from security\.api\.routers\.\w+_router import router as \w+_router)"
    imports = re.findall(import_pattern, content)

    # Поиск последнего router импорта
    last_router_import = None
    for match in re.finditer(import_pattern, content):
        last_router_import = match

    if last_router_import:
        # Добавление импорта после последнего router
        insert_pos = last_router_import.end()
        new_import = "\nfrom security.api.routers.roadside_assistance_router import router as roadside_assistance_router"
        content = content[:insert_pos] + new_import + content[insert_pos:]
        print("✅ Импорт добавлен")
    else:
        # Если не найдены другие router импорты, ищем место после других импортов
        # Ищем блок импортов security
        security_import_pattern = r"(from security\.\w+ import \w+)"
        security_imports = list(re.finditer(security_import_pattern, content))
        if security_imports:
            last_import = security_imports[-1]
            insert_pos = last_import.end()
            new_import = "\nfrom security.api.routers.roadside_assistance_router import router as roadside_assistance_router"
            content = content[:insert_pos] + new_import + content[insert_pos:]
            print("✅ Импорт добавлен (после security импортов)")
        else:
            print("❌ Не найдено место для добавления импорта")
            return False

    # Поиск места для добавления app.include_router
    router_pattern = r"(app\.include_router\(\w+_router\))"
    routers = list(re.finditer(router_pattern, content))

    if routers:
        # Добавление после последнего router
        last_router = routers[-1]
        insert_pos = last_router.end()
        new_router = "\n\ntry:\n    app.include_router(roadside_assistance_router)\n    print(\"✅ Roadside Assistance Router зарегистрирован\")\nexcept Exception as e:\n    print(f\"⚠️ Не удалось зарегистрировать Roadside Assistance Router: {e}\")"
        content = content[:insert_pos] + new_router + content[insert_pos:]
        print("✅ Регистрация router добавлена")
    else:
        print("❌ Не найдено место для добавления app.include_router")
        return False

    # Сохранение обновленного файла
    print("💾 Сохранение обновленного main.py...")
    with open(MAIN_PY_PATH, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ Roadside Assistance Router добавлен в main.py")
    print("")

    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("✅ Интеграция завершена успешно!")
            exit(0)
        else:
            print("❌ Ошибка при интеграции")
            exit(1)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
