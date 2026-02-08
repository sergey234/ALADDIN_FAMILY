#!/usr/bin/env python3
import re

file_path = "Core/Localization/LocalizationManager.swift"

print("🔍 Поиск дубликатов ключей в словарях локализации...")
print("=" * 60)

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    content = ''.join(lines)

# Ищем .russian: [ или .english: [
lang_pattern = r'\.(russian|english|arabic|turkish|kazakh|uzbek|kyrgyz|tajik|azerbaijani|armenian|georgian|mongolian|chinese|japanese|korean):\s*\['

all_duplicates = []
file_changes = []

for lang_match in re.finditer(lang_pattern, content):
    lang = lang_match.group(1)
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
        
        # Находим все ключи в этом словаре
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
                    all_duplicates.append((lang, key, seen[key], key_positions[i][1]))
            else:
                seen[key] = i
        
        if duplicates:
            print(f"\n❌ Язык '{lang}': найдено {len(duplicates)} дубликатов:")
            for dup_key in duplicates:
                # Находим все вхождения
                occurrences = [i for i, k in enumerate(keys) if k == dup_key]
                print(f"   • Ключ '{dup_key}' встречается {len(occurrences)} раз(а)")
                
                # Показываем строки
                for occ_idx in occurrences:
                    pos = key_positions[occ_idx][1]
                    line_num = content[:pos].count('\n') + 1
                    print(f"     - Строка {line_num}")
                
                # Удаляем все кроме первого вхождения
                first_occ = occurrences[0]
                for occ_idx in reversed(occurrences[1:]):  # В обратном порядке чтобы не сбить индексы
                    key_match = list(re.finditer(key_pattern, lang_dict_content))[occ_idx]
                    # Находим всю строку с этим ключом
                    line_start = lang_dict_content.rfind('\n', 0, key_match.start()) + 1
                    line_end = lang_dict_content.find('\n', key_match.end())
                    if line_end == -1:
                        line_end = len(lang_dict_content)
                    line = lang_dict_content[line_start:line_end].strip()
                    if line and not line.startswith('//'):
                        print(f"     🗑️  Удаляем строку: {line[:80]}")
                        # Удаляем эту строку из содержимого
                        lang_dict_content = lang_dict_content[:line_start] + lang_dict_content[line_end+1:]
                        file_changes.append((lang, dup_key, line_num))
        else:
            print(f"✅ Язык '{lang}': дубликатов не найдено ({len(keys)} ключей)")

if all_duplicates:
    print(f"\n" + "=" * 60)
    print(f"❌ ВСЕГО НАЙДЕНО {len(all_duplicates)} ДУБЛИКАТОВ!")
    print("🔧 Нужно исправить вручную или использовать автоматическое исправление")
    exit(1)
else:
    print("\n✅ Дубликатов не найдено!")
