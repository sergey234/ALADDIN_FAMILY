#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для регистрации AI Categories Agent в SFM на сервере
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Путь к registry на сервере
REGISTRY_PATH = Path("/opt/aladdin-backend/data/sfm/function_registry.json")
ENTRY_PATH = Path("/tmp/function_registry_entry_ai_categories.json")


def register_agent():
    """Регистрация агента в SFM"""

    print("🔍 Регистрация AI Categories Agent в SFM...")
    print()

    # Проверка существования registry
    if not REGISTRY_PATH.exists():
        print(f"❌ Registry не найден: {REGISTRY_PATH}")
        print("   Создаем новый registry...")
        registry = {"agents": [], "last_updated": datetime.now().isoformat()}
    else:
        # Загрузка существующего registry
        try:
            with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
                registry = json.load(f)
            print(f"✅ Registry загружен: {REGISTRY_PATH}")
        except Exception as e:
            print(f"❌ Ошибка загрузки registry: {e}")
            return False

    # Загрузка новой entry
    if not ENTRY_PATH.exists():
        print(f"❌ Entry файл не найден: {ENTRY_PATH}")
        print("   Убедитесь, что файл скопирован на сервер!")
        return False

    try:
        with open(ENTRY_PATH, 'r', encoding='utf-8') as f:
            new_entry = json.load(f)
        print(f"✅ Entry загружен: {ENTRY_PATH}")
    except Exception as e:
        print(f"❌ Ошибка загрузки entry: {e}")
        return False

    # Проверка, не зарегистрирован ли уже
    agent_name = new_entry.get("name")

    if isinstance(registry, list):
        existing = next((a for a in registry if a.get("name") == agent_name), None)
        agents_list = registry
    elif isinstance(registry, dict):
        if "agents" in registry:
            agents_list = registry["agents"]
            existing = next((a for a in agents_list if a.get("name") == agent_name), None)
        else:
            existing = registry.get(agent_name)
            agents_list = None
    else:
        print("❌ Неподдерживаемый формат registry")
        return False

    if existing:
        print(f"⚠️  Агент '{agent_name}' уже зарегистрирован!")
        response = input("   Обновить существующую запись? (y/n): ")
        if response.lower() != 'y':
            print("❌ Регистрация отменена")
            return False

        # Обновление существующей записи
        if isinstance(registry, list):
            index = next((i for i, a in enumerate(registry) if a.get("name") == agent_name), None)
            if index is not None:
                registry[index] = new_entry
        elif isinstance(registry, dict):
            if "agents" in registry:
                index = next((i for i, a in enumerate(registry["agents"]) if a.get("name") == agent_name), None)
                if index is not None:
                    registry["agents"][index] = new_entry
            else:
                registry[agent_name] = new_entry

        print("✅ Запись обновлена")
    else:
        # Добавление новой записи
        if isinstance(registry, list):
            registry.append(new_entry)
        elif isinstance(registry, dict):
            if "agents" in registry:
                registry["agents"].append(new_entry)
            else:
                registry[agent_name] = new_entry

        print("✅ Новая запись добавлена")

    # Обновление метаданных
    if isinstance(registry, dict):
        registry["last_updated"] = datetime.now().isoformat()

    # Backup существующего registry
    backup_path = REGISTRY_PATH.with_suffix(f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    try:
        if REGISTRY_PATH.exists():
            import shutil
            shutil.copy2(REGISTRY_PATH, backup_path)
            print(f"✅ Backup создан: {backup_path}")
    except Exception as e:
        print(f"⚠️  Не удалось создать backup: {e}")

    # Сохранение registry
    try:
        REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(REGISTRY_PATH, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
        print(f"✅ Registry сохранен: {REGISTRY_PATH}")
    except Exception as e:
        print(f"❌ Ошибка сохранения registry: {e}")
        return False

    # Подсчет функций
    if isinstance(registry, list):
        total_agents = len(registry)
        total_functions = sum(len(a.get("functions", [])) for a in registry)
    elif isinstance(registry, dict):
        if "agents" in registry:
            total_agents = len(registry["agents"])
            total_functions = sum(len(a.get("functions", [])) for a in registry["agents"])
        else:
            total_agents = len(registry)
            total_functions = sum(len(a.get("functions", [])) for a in registry.values() if isinstance(a, dict))
    else:
        total_agents = 0
        total_functions = 0

    print()
    print("=" * 80)
    print("📊 СТАТИСТИКА SFM:")
    print("=" * 80)
    print(f"   Всего агентов: {total_agents}")
    print(f"   Всего функций: {total_functions}")
    print(f"   AI Categories функций: {len(new_entry.get('functions', []))}")
    print("=" * 80)
    print()
    print("✅ AI Categories Agent успешно зарегистрирован в SFM!")

    return True


if __name__ == "__main__":
    success = register_agent()
    sys.exit(0 if success else 1)
