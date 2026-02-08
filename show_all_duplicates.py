#!/usr/bin/env python3
import re

file_path = "Core/Localization/LocalizationManager.swift"

print("📊 ПОЛНЫЙ СПИСОК ВСЕХ ДУБЛИКАТОВ:")
print("=" * 60)

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    content = ''.join(lines)

# Ищем .english: [
lang_pattern = r'\.english:\s*\['

for lang_match in re.finditer(lang_pattern, content):
    start_pos = lang_match.end()
    
    # Находим закрывающую скобку ]
    bracket_count = 1
    pos = start_pos
    while pos < len(content) and bracket_count > 0:
        if content[pos] == '[':
            bracket_count += 1
        elif content[pos] == ']':
            bracket_count -= 1
        pos += 1
    
    if bracket_count == 0:
        lang_dict_content = content[start_pos:pos-1]
        
        # Находим все ключи
        key_pattern = r'["\']([^"\']+)["\']\s*:'
        keys = []
        key_positions = []
        
        for key_match in re.finditer(key_pattern, lang_dict_content):
            key = key_match.group(1)
            keys.append(key)
            key_positions.append((key, start_pos + key_match.start()))
        
        # Проверяем дубликаты
        seen = {}
        duplicates = []
        for i, key in enumerate(keys):
            if key in seen:
                if key not in duplicates:
                    duplicates.append(key)
                    # Находим все вхождения
                    occurrences = [j for j, k in enumerate(keys) if k == key]
                    print(f"\n❌ ДУБЛИКАТ: '{key}' встречается {len(occurrences)} раз(а):")
                    for occ_idx in occurrences:
                        pos = key_positions[occ_idx][1]
                        line_num = content[:pos].count('\n') + 1
                        # Показываем контекст строки
                        if line_num <= len(lines):
                            line = lines[line_num-1].strip()
                            print(f"   Строка {line_num}: {line[:100]}")
        break

print(f"\n" + "=" * 60)
print(f"✅ Всего дубликатов в английском словаре: {len(duplicates)}")
