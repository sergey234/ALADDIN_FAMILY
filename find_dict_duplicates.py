#!/usr/bin/env python3
import re

file_path = "Core/Localization/LocalizationManager.swift"

print("🔍 Поиск дубликатов ключей ВНУТРИ словарей...")
print("=" * 60)

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

# Более точный поиск словарей с многострочным содержимым
# Ищем var name: [String: String] = { ... } где ... может быть многострочным
dict_pattern = r'var\s+(\w+)\s*:\s*\[String:\s*String\]\s*=\s*\{'

duplicates_found = []

for match in re.finditer(dict_pattern, content):
    dict_name = match.group(1)
    start_pos = match.end()
    
    # Находим закрывающую скобку этого словаря
    brace_count = 1
    pos = start_pos
    while pos < len(content) and brace_count > 0:
        if content[pos] == '{':
            brace_count += 1
        elif content[pos] == '}':
            brace_count -= 1
        pos += 1
    
    if brace_count == 0:
        dict_content = content[start_pos:pos-1]
        
        # Находим все ключи в этом словаре
        key_pattern = r'["\']([^"\']+)["\']\s*:'
        keys = re.findall(key_pattern, dict_content)
        
        # Проверяем дубликаты внутри этого словаря
        seen = {}
        for key in keys:
            if key in seen:
                line_num = content[:match.start()].count('\n') + 1
                if (dict_name, key) not in duplicates_found:
                    duplicates_found.append((dict_name, key, line_num))
                    print(f"❌ ДУБЛИКАТ: Словарь '{dict_name}' содержит дубликат ключа '{key}'")
                    # Показываем контекст
                    key_matches = list(re.finditer(key_pattern, dict_content))
                    for i, km in enumerate(key_matches):
                        if km.group(1) == key:
                            rel_pos = start_pos + km.start()
                            line = content[:rel_pos].count('\n') + 1
                            print(f"   Вхождение #{i+1} на строке ~{line}")
            else:
                seen[key] = True

if duplicates_found:
    print(f"\n✅ Найдено {len(duplicates_found)} словарей с дубликатами")
    print("\n🔧 Нужно исправить эти словари!")
else:
    print("✅ Дубликатов внутри словарей не найдено")
    print("Проверяем другие возможные места...")
