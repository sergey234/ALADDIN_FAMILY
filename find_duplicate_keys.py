#!/usr/bin/env python3
import re
import sys

file_path = "Core/Localization/LocalizationManager.swift"

print("🔍 Поиск дубликатов ключей в LocalizationManager.swift...")
print("=" * 60)

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    content = ''.join(lines)

# Ищем все словари локализации
# Паттерн: var name: [String: String] = { ... }
dict_pattern = r'var\s+(\w+)\s*:\s*\[String:\s*String\]\s*=\s*\{([^}]+)\}'

duplicates_found = []
all_duplicates = []

for match in re.finditer(dict_pattern, content, re.DOTALL):
    dict_name = match.group(1)
    dict_content = match.group(2)
    
    # Находим все ключи в этом словаре
    key_pattern = r'["\']([^"\']+)["\']\s*:'
    keys = re.findall(key_pattern, dict_content)
    
    # Проверяем дубликаты
    seen = {}
    for key in keys:
        if key in seen:
            line_num = content[:match.start()].count('\n') + 1
            dup_info = f"Словарь '{dict_name}': дубликат ключа '{key}'"
            if dup_info not in all_duplicates:
                all_duplicates.append(dup_info)
                duplicates_found.append((dict_name, key, line_num))
        else:
            seen[key] = True

if duplicates_found:
    print(f"❌ НАЙДЕНО {len(duplicates_found)} ДУБЛИКАТОВ:\n")
    for dict_name, key, line_num in duplicates_found[:30]:
        print(f"  • {dict_name}: ключ '{key}' (строка ~{line_num})")
    
    # Показываем первые несколько для исправления
    print("\n" + "=" * 60)
    print("🔧 НАЧИНАЕМ ИСПРАВЛЕНИЕ...")
    sys.exit(1)
else:
    print("✅ Дубликаты не найдены в словарях локализации")
    print("Проверяем другие возможные места...")
    
    # Проверяем все ключи в кавычках в файле
    all_keys = re.findall(r'["\']([^"\']+)["\']\s*:', content)
    seen_all = {}
    file_duplicates = []
    
    for i, key in enumerate(all_keys):
        if key in seen_all:
            file_duplicates.append((key, seen_all[key], i))
        else:
            seen_all[key] = i
    
    if file_duplicates:
        print(f"\n⚠️  Найдено {len(file_duplicates)} потенциальных дубликатов в файле:")
        for key, first_pos, second_pos in file_duplicates[:20]:
            print(f"  • Ключ '{key}' встречается несколько раз")
    else:
        print("✅ Дубликаты не найдены")
