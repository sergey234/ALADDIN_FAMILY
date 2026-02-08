#!/usr/bin/env python3
import re

file_path = "Core/Localization/LocalizationManager.swift"

print("🔍 Проверка словарей для каждого языка на дубликаты...")
print("=" * 60)

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Ищем основной словарь translations
main_pattern = r'var\s+translations:\s*\[Language:\s*\[String:\s*String\]\]\s*=\s*\{'

match = re.search(main_pattern, content)
if not match:
    print("❌ Не найден словарь translations")
    exit(1)

start_pos = match.end()
print(f"✅ Найден словарь translations на позиции {start_pos}")

# Находим закрывающую скобку основного словаря
brace_count = 1
pos = start_pos
while pos < len(content) and brace_count > 0:
    if content[pos] == '{':
        brace_count += 1
    elif content[pos] == '}':
        brace_count -= 1
    pos += 1

if brace_count != 0:
    print("❌ Не удалось найти закрывающую скобку")
    exit(1)

main_dict_content = content[start_pos:pos-1]
print(f"✅ Размер содержимого: {len(main_dict_content)} символов")

# Ищем каждый языковой словарь: .russian: [...], .english: [...]
lang_pattern = r'\.(russian|english|arabic|turkish|kazakh|uzbek|kyrgyz|tajik|azerbaijani|armenian|georgian|mongolian|chinese|japanese|korean):\s*\['

all_duplicates = []

for lang_match in re.finditer(lang_pattern, main_dict_content):
    lang = lang_match.group(1)
    lang_start = lang_match.end()
    
    # Находим закрывающую скобку этого языкового словаря
    brace_count = 1
    lang_pos = lang_start
    while lang_pos < len(main_dict_content) and brace_count > 0:
        if main_dict_content[lang_pos] == '[':
            brace_count += 1
        elif main_dict_content[lang_pos] == ']':
            brace_count -= 1
        lang_pos += 1
    
    if brace_count == 0:
        lang_dict_content = main_dict_content[lang_start:lang_pos-1]
        
        # Находим все ключи в этом словаре
        key_pattern = r'["\']([^"\']+)["\']\s*:'
        keys = re.findall(key_pattern, lang_dict_content)
        
        # Проверяем дубликаты
        seen = {}
        duplicates = []
        for key in keys:
            if key in seen:
                if key not in duplicates:
                    duplicates.append(key)
                    all_duplicates.append((lang, key))
            else:
                seen[key] = True
        
        if duplicates:
            print(f"\n❌ Язык '{lang}': найдено {len(duplicates)} дубликатов:")
            for dup_key in duplicates[:10]:
                # Находим все вхождения этого ключа
                key_matches = list(re.finditer(key_pattern, lang_dict_content))
                occurrences = [i for i, km in enumerate(key_matches) if km.group(1) == dup_key]
                print(f"   • Ключ '{dup_key}' встречается {len(occurrences)} раз(а)")
                # Показываем первые несколько вхождений
                for i, occ in enumerate(occurrences[:3]):
                    match_pos = key_matches[occ].start()
                    line_num = content[:start_pos + lang_start + match_pos].count('\n') + 1
                    print(f"     - Вхождение #{i+1} на строке ~{line_num}")
        else:
            print(f"✅ Язык '{lang}': дубликатов не найдено ({len(keys)} ключей)")

if all_duplicates:
    print(f"\n" + "=" * 60)
    print(f"❌ ВСЕГО НАЙДЕНО {len(all_duplicates)} ДУБЛИКАТОВ!")
    print("🔧 НУЖНО ИСПРАВИТЬ!")
    exit(1)
else:
    print("\n✅ Дубликатов не найдено во всех языковых словарях!")
