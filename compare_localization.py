#!/usr/bin/env python3
import re
from collections import Counter

def extract_keys(filepath, lang='russian'):
    """Извлекает все ключи из указанной языковой секции"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Находим начало секции
    pattern_start = rf'\.{lang}:\s*\['
    match_start = re.search(pattern_start, content)
    if not match_start:
        return set()
    
    start_pos = match_start.end()
    
    # Находим конец секции (следующая секция или закрывающая скобка)
    depth = 0
    i = start_pos
    end_pos = len(content)
    
    while i < len(content):
        if content[i] == '[':
            depth += 1
        elif content[i] == ']':
            depth -= 1
            if depth == 0:
                end_pos = i
                break
        # Проверяем, не началась ли следующая секция
        if i < len(content) - 20:
            next_section = re.match(r'\.(russian|english|chinese|arabic):\s*\[', content[i:])
            if next_section and depth == 0:
                end_pos = i
                break
        i += 1
    
    # Извлекаем секцию
    section_content = content[start_pos:end_pos]
    
    # Находим все ключи
    keys = re.findall(r'"([^"]+)":', section_content)
    return set(keys)

# Сравниваем файлы
current_file = 'Core/Localization/LocalizationManager.swift'
backup_file = 'BACKUPS/BACKUP_MOBILE_20260129_172920/Core/Localization/LocalizationManager.swift'

current_keys = extract_keys(current_file, 'russian')
backup_keys = extract_keys(backup_file, 'russian')

print(f"Текущий файл: {len(current_keys)} уникальных ключей")
print(f"Бэкап: {len(backup_keys)} уникальных ключей")
print(f"\nРазница: {len(backup_keys) - len(current_keys)} ключей")

# Находим удаленные ключи
removed = backup_keys - current_keys
added = current_keys - backup_keys

if removed:
    print(f"\n🔴 УДАЛЕННЫЕ КЛЮЧИ ({len(removed)}):")
    for key in sorted(removed)[:50]:
        print(f"  - {key}")
    if len(removed) > 50:
        print(f"  ... и еще {len(removed) - 50} ключей")

if added:
    print(f"\n🟢 ДОБАВЛЕННЫЕ КЛЮЧИ ({len(added)}):")
    for key in sorted(added)[:20]:
        print(f"  - {key}")
    if len(added) > 20:
        print(f"  ... и еще {len(added) - 20} ключей")
