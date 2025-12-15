#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для перевода Anti-Tracker Agent в спящий режим на сервере
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import shutil

# Путь к registry на сервере
REGISTRY_PATH = Path("/opt/aladdin-backend/data/sfm/function_registry.json")
AGENT_NAME = "anti_tracker_agent"

def put_agent_to_sleep():
    """Перевод агента в спящий режим"""
    
    print("=" * 60)
    print("😴 ПЕРЕВОД ANTI-TRACKER AGENT В СПЯЩИЙ РЕЖИМ")
    print("=" * 60)
    print()
    
    # Проверка существования registry
    if not REGISTRY_PATH.exists():
        print(f"❌ Registry не найден: {REGISTRY_PATH}")
        return False
    
    # Создание backup
    backup_path = REGISTRY_PATH.with_suffix(
        f".json.backup_sleep_{AGENT_NAME}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    print(f"📦 Создание backup: {backup_path}")
    shutil.copy2(REGISTRY_PATH, backup_path)
    print("✅ Backup создан")
    print()
    
    # Загрузка registry
    print(f"📖 Загрузка registry: {REGISTRY_PATH}")
    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    # Поиск агента
    if AGENT_NAME not in registry:
        print(f"❌ Агент '{AGENT_NAME}' не найден в registry")
        return False
    
    agent_entry = registry[AGENT_NAME]
    
    # Проверка текущего статуса
    current_status = agent_entry.get("status", "unknown")
    print(f"📊 Текущий статус: {current_status}")
    
    if current_status == "sleep":
        print("⚠️ Агент уже в спящем режиме")
        return True
    
    # Изменение статуса
    print(f"🔄 Изменение статуса: {current_status} → sleep")
    agent_entry["status"] = "sleep"
    agent_entry["sleep_since"] = datetime.now().isoformat()
    
    # Обновление метаданных
    registry["last_updated"] = datetime.now().isoformat()
    
    # Сохранение
    print(f"\n💾 Сохранение registry...")
    with open(REGISTRY_PATH, 'w', encoding='utf-8') as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)
    
    print("✅ Registry обновлен")
    print()
    
    # Статистика
    print("=" * 60)
    print("📊 СТАТИСТИКА")
    print("=" * 60)
    
    # Подсчет агентов по статусам
    agents = {k: v for k, v in registry.items() 
              if k not in ["functions", "handlers", "last_updated"] 
              and isinstance(v, dict) and "functions" in v}
    
    status_counts = {}
    for agent in agents.values():
        status = agent.get("status", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print(f"Всего агентов: {len(agents)}")
    print("Статусы:")
    for status, count in status_counts.items():
        print(f"  • {status}: {count}")
    
    print()
    print(f"✅ Anti-Tracker Agent переведен в спящий режим!")
    print(f"   Статус: sleep")
    print(f"   С: {agent_entry.get('sleep_since', 'N/A')}")
    
    return True


if __name__ == "__main__":
    try:
        success = put_agent_to_sleep()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
