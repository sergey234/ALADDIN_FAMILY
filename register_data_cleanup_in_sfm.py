#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для регистрации Personal Data Cleanup Agent в SFM

Использование:
    python3 register_data_cleanup_in_sfm.py

Запускать на сервере после копирования файлов.
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path

# Пути
FUNCTION_REGISTRY_PATH = "/opt/aladdin-backend/data/sfm/function_registry.json"
SFM_ENTRY_PATH = "/opt/aladdin-backend/security/ai_agents/function_registry_entry_data_cleanup.json"
BACKUP_PATH = f"/opt/aladdin-backend/data/sfm/function_registry_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

def main():
    print("🔧 Регистрация Personal Data Cleanup Agent в SFM")
    print("")

    # Проверка существования файлов
    if not os.path.exists(FUNCTION_REGISTRY_PATH):
        print(f"❌ Файл не найден: {FUNCTION_REGISTRY_PATH}")
        return False

    if not os.path.exists(SFM_ENTRY_PATH):
        print(f"❌ Файл не найден: {SFM_ENTRY_PATH}")
        return False

    # Создание резервной копии
    print(f"📋 Создание резервной копии: {BACKUP_PATH}")
    shutil.copy2(FUNCTION_REGISTRY_PATH, BACKUP_PATH)
    print("✅ Резервная копия создана")
    print("")

    # Загрузка существующего реестра
    print("📖 Загрузка function_registry.json...")
    with open(FUNCTION_REGISTRY_PATH, 'r', encoding='utf-8') as f:
        registry = json.load(f)

    # Загрузка новой записи
    print("📖 Загрузка function_registry_entry_data_cleanup.json...")
    with open(SFM_ENTRY_PATH, 'r', encoding='utf-8') as f:
        new_entry = json.load(f)

    # Проверка, не зарегистрирован ли уже
    agent_name = new_entry["name"]
    existing_agents = [a["name"] for a in registry.get("agents", [])]

    if agent_name in existing_agents:
        print(f"⚠️  Агент {agent_name} уже зарегистрирован. Обновляю...")
        # Удаляем старую запись
        registry["agents"] = [a for a in registry.get("agents", []) if a["name"] != agent_name]

    # Добавление новой записи
    print(f"➕ Добавление агента: {agent_name}")
    if "agents" not in registry:
        registry["agents"] = []
    registry["agents"].append(new_entry)

    # Обновление статистики
    total_functions = sum(len(a.get("functions", [])) for a in registry.get("agents", []))
    total_endpoints = sum(len(a.get("api_endpoints", [])) for a in registry.get("agents", []))

    if "metadata" not in registry:
        registry["metadata"] = {}
    registry["metadata"]["total_agents"] = len(registry.get("agents", []))
    registry["metadata"]["total_functions"] = total_functions
    registry["metadata"]["total_api_endpoints"] = total_endpoints
    registry["metadata"]["last_updated"] = datetime.now().isoformat()

    # Сохранение обновленного реестра
    print("💾 Сохранение обновленного реестра...")
    with open(FUNCTION_REGISTRY_PATH, 'w', encoding='utf-8') as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)

    print("✅ Агент зарегистрирован в SFM")
    print("")
    print(f"📊 Статистика:")
    print(f"   - Всего агентов: {registry['metadata']['total_agents']}")
    print(f"   - Всего функций: {registry['metadata']['total_functions']}")
    print(f"   - Всего endpoints: {registry['metadata']['total_api_endpoints']}")
    print("")

    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("✅ Регистрация завершена успешно!")
            exit(0)
        else:
            print("❌ Ошибка при регистрации")
            exit(1)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
