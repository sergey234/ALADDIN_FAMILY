#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для регистрации Dark Web Monitoring Agent в SFM
"""

import json
from pathlib import Path

registry_path = Path('/opt/aladdin-backend/data/sfm/function_registry.json')
entry_path = Path('/tmp/function_registry_entry_dark_web_monitoring.json')

# Проверка существования файлов
if not registry_path.exists():
    print(f'❌ Registry не найден: {registry_path}')
    exit(1)

if not entry_path.exists():
    print(f'❌ Entry не найден: {entry_path}')
    exit(1)

# Загрузить registry
with open(registry_path, 'r', encoding='utf-8') as f:
    registry = json.load(f)

# Загрузить entry
with open(entry_path, 'r', encoding='utf-8') as f:
    new_entry = json.load(f)

# Создать backup
backup_path = registry_path.with_suffix(f'.json.backup_darkweb_{entry_path.stat().st_mtime}')
with open(backup_path, 'w', encoding='utf-8') as f:
    json.dump(registry, f, indent=2, ensure_ascii=False)
print(f'✅ Backup создан: {backup_path}')

# Добавить в registry
if isinstance(registry, list):
    existing = next((a for a in registry if a.get('name') == 'dark_web_monitoring_agent'), None)
    if existing:
        print('⚠️  Агент уже зарегистрирован! Обновляю...')
        idx = registry.index(existing)
        registry[idx] = new_entry
    else:
        registry.append(new_entry)
elif isinstance(registry, dict):
    if 'agents' in registry:
        existing = next((a for a in registry['agents'] if a.get('name') == 'dark_web_monitoring_agent'), None)
        if existing:
            print('⚠️  Агент уже зарегистрирован! Обновляю...')
            idx = registry['agents'].index(existing)
            registry['agents'][idx] = new_entry
        else:
            registry['agents'].append(new_entry)
    else:
        registry[new_entry['name']] = new_entry

# Сохранить
with open(registry_path, 'w', encoding='utf-8') as f:
    json.dump(registry, f, indent=2, ensure_ascii=False)

print('✅ Агент зарегистрирован в SFM!')

# Проверка
if isinstance(registry, list):
    agent = next((a for a in registry if a.get('name') == 'dark_web_monitoring_agent'), None)
elif isinstance(registry, dict):
    if 'agents' in registry:
        agent = next((a for a in registry['agents'] if a.get('name') == 'dark_web_monitoring_agent'), None)
    else:
        agent = registry.get('dark_web_monitoring_agent')

if agent:
    print(f'✅ Проверка: агент найден: {agent["name"]}')
    print(f'   Статус: {agent.get("status")}')
    print(f'   Путь: {agent.get("path")}')
else:
    print('❌ Ошибка: агент не найден после регистрации!')
