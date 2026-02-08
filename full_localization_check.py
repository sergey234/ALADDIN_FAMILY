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
        return set(), []
    
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
    return set(keys), keys

# Сравниваем файлы
current_file = 'Core/Localization/LocalizationManager.swift'
backup_file = 'BACKUPS/BACKUP_MOBILE_20260129_172920/Core/Localization/LocalizationManager.swift'

print("=" * 80)
print("ПОЛНАЯ ПРОВЕРКА ЛОКАЛИЗАЦИИ")
print("=" * 80)

total_removed = 0
total_added = 0

for lang in ['russian', 'english', 'chinese', 'arabic']:
    print(f"\n{'='*80}")
    print(f"ЯЗЫК: {lang.upper()}")
    print(f"{'='*80}")
    
    current_keys_set, current_keys_list = extract_keys(current_file, lang)
    backup_keys_set, backup_keys_list = extract_keys(backup_file, lang)
    
    print(f"Текущий файл: {len(current_keys_set)} уникальных ключей ({len(current_keys_list)} всего)")
    print(f"Бэкап:        {len(backup_keys_set)} уникальных ключей ({len(backup_keys_list)} всего)")
    
    # Находим удаленные ключи
    removed = backup_keys_set - current_keys_set
    added = current_keys_set - backup_keys_set
    
    # Проверяем дубликаты в текущем файле
    current_counts = Counter(current_keys_list)
    duplicates = {k: v for k, v in current_counts.items() if v > 1}
    
    if removed:
        total_removed += len(removed)
        print(f"\n🔴 УДАЛЕННЫЕ КЛЮЧИ ({len(removed)}):")
        for key in sorted(removed):
            print(f"  - {key}")
    
    if added:
        total_added += len(added)
        print(f"\n🟢 ДОБАВЛЕННЫЕ КЛЮЧИ ({len(added)}):")
        for key in sorted(added):
            print(f"  - {key}")
    
    if duplicates:
        print(f"\n⚠️ ДУБЛИКАТЫ В ТЕКУЩЕМ ФАЙЛЕ ({len(duplicates)}):")
        for key, count in sorted(duplicates.items()):
            print(f"  - {key}: {count} раз(а)")
    
    if not removed and not added and not duplicates:
        print(f"\n✅ Все ключи на месте, дубликатов нет!")

print(f"\n{'='*80}")
print("ИТОГОВАЯ СТАТИСТИКА")
print(f"{'='*80}")
print(f"Всего удалено ключей: {total_removed}")
print(f"Всего добавлено ключей: {total_added}")

if total_removed == 0 and total_added == 0:
    print("\n✅ ВСЕ КЛЮЧИ ВОССТАНОВЛЕНЫ! Пробелов в локализации нет!")
else:
    print(f"\n⚠️ ЕСТЬ РАЗЛИЧИЯ! Нужно восстановить {total_removed} ключей.")
