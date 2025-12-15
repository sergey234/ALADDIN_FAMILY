#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт регистрации Location Bubble Agent в SFM
Дата: 12 декабря 2025
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path

# Пути
REGISTRY_PATH = "/opt/aladdin-backend/data/sfm/function_registry.json"
ENTRY_PATH = "/tmp/function_registry_entry_location_bubble.json"
BACKUP_PATH = f"/opt/aladdin-backend/data/sfm/function_registry_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

def main():
    print("=== РЕГИСТРАЦИЯ LOCATION BUBBLE AGENT В SFM ===\n")
    
    # 1. Проверка файла записи
    if not os.path.exists(ENTRY_PATH):
        print(f"❌ Файл {ENTRY_PATH} не найден!")
        return 1
    
    with open(ENTRY_PATH, 'r', encoding='utf-8') as f:
        new_entry = json.load(f)
    
    print(f"✅ Запись загружена: {new_entry['name']}")
    
    # 2. Загрузка существующего registry
    if not os.path.exists(REGISTRY_PATH):
        print(f"❌ Файл {REGISTRY_PATH} не найден!")
        return 1
    
    # Создание backup
    shutil.copy2(REGISTRY_PATH, BACKUP_PATH)
    print(f"✅ Backup создан: {BACKUP_PATH}")
    
    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    # 3. Проверка, не зарегистрирован ли уже
    existing_agents = [a.get('name') for a in registry.get('agents', [])]
    if new_entry['name'] in existing_agents:
        print(f"⚠️  Агент {new_entry['name']} уже зарегистрирован!")
        response = input("Перезаписать? (y/n): ")
        if response.lower() != 'y':
            print("Отменено")
            return 0
        
        # Удаляем старую запись
        registry['agents'] = [a for a in registry['agents'] if a.get('name') != new_entry['name']]
    
    # 4. Добавление новой записи
    if 'agents' not in registry:
        registry['agents'] = []
    
    registry['agents'].append(new_entry)
    
    # 5. Подсчет функций
    total_functions = sum(len(agent.get('functions', [])) for agent in registry.get('agents', []))
    total_endpoints = sum(len(agent.get('api_endpoints', [])) for agent in registry.get('agents', []))
    
    # Обновление метаданных
    registry['last_updated'] = datetime.now().isoformat()
    registry['total_agents'] = len(registry['agents'])
    registry['total_functions'] = total_functions
    registry['total_api_endpoints'] = total_endpoints
    
    # 6. Сохранение
    with open(REGISTRY_PATH, 'w', encoding='utf-8') as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Агент зарегистрирован в SFM")
    print(f"   - Всего агентов: {len(registry['agents'])}")
    print(f"   - Всего функций: {total_functions}")
    print(f"   - Всего API endpoints: {total_endpoints}")
    print(f"   - Функций Location Bubble Agent: {len(new_entry.get('functions', []))}")
    print(f"   - API endpoints Location Bubble Agent: {len(new_entry.get('api_endpoints', []))}")
    
    return 0

if __name__ == "__main__":
    exit(main())
