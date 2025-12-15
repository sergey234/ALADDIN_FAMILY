#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для регистрации Anti-Tracker Agent в SFM

Использование:
    python3 register_anti_tracker_in_sfm.py

Дата создания: 12 декабря 2025
"""

import json
import shutil
from pathlib import Path
from datetime import datetime

# Пути
REGISTRY_PATH = Path("/opt/aladdin-backend/data/sfm/function_registry.json")
ENTRY_PATH = Path("/tmp/function_registry_entry_anti_tracker.json")
BACKUP_PATH = REGISTRY_PATH.with_suffix(f".json.backup_anti_tracker_{datetime.now().strftime('%Y%m%d_%H%M%S')}")


def main():
    print("=" * 60)
    print("РЕГИСТРАЦИЯ ANTI-TRACKER AGENT В SFM")
    print("=" * 60)

    # Проверка файлов
    if not ENTRY_PATH.exists():
        print(f"❌ Файл регистрации не найден: {ENTRY_PATH}")
        return False

    if not REGISTRY_PATH.exists():
        print(f"❌ Registry не найден: {REGISTRY_PATH}")
        return False

    # Создание backup
    print(f"\n📦 Создание backup: {BACKUP_PATH}")
    shutil.copy2(REGISTRY_PATH, BACKUP_PATH)
    print("✅ Backup создан")

    # Загрузка registry
    print(f"\n📖 Загрузка registry: {REGISTRY_PATH}")
    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        registry = json.load(f)

    # Загрузка новой записи
    print(f"📖 Загрузка записи: {ENTRY_PATH}")
    with open(ENTRY_PATH, 'r', encoding='utf-8') as f:
        new_entry = json.load(f)

    # Проверка существования
    agent_name = new_entry["name"]
    if agent_name in registry:
        print(f"\n⚠️ Агент {agent_name} уже зарегистрирован")
        response = input("Перезаписать? (y/n): ")
        if response.lower() != 'y':
            print("❌ Отменено")
            return False
        print("🔄 Обновление существующей записи...")
    else:
        print("➕ Добавление новой записи...")

    # Добавление/обновление записи
    registry[agent_name] = new_entry
    registry["last_updated"] = datetime.now().isoformat()

    # Сохранение
    print("\n💾 Сохранение registry...")
    with open(REGISTRY_PATH, 'w', encoding='utf-8') as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)

    print("✅ Registry обновлен")

    # Статистика
    print("\n" + "=" * 60)
    print("СТАТИСТИКА SFM")
    print("=" * 60)

    # Подсчет функций
    main_functions = len(registry.get("functions", []))
    agent_functions = len(new_entry.get("functions", []))
    total_functions = main_functions + agent_functions

    # Подсчет агентов
    agents = [k for k, v in registry.items() if isinstance(v, dict) and v.get("type") == "ai_agent"]
    agents_count = len(agents)

    # Подсчет API endpoints
    main_endpoints = len(registry.get("api_endpoints", []))
    agent_endpoints = len(new_entry.get("api_endpoints", []))
    total_endpoints = main_endpoints + agent_endpoints

    print(f"📊 Всего функций: {total_functions}")
    print(f"🤖 Всего агентов: {agents_count}")
    print(f"🔌 Всего API endpoints: {total_endpoints}")
    print(f"📝 Функций в агенте: {agent_functions}")
    print(f"🌐 API endpoints в агенте: {agent_endpoints}")

    print("\n✅ Регистрация завершена успешно!")
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
