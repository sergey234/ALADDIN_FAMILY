#!/usr/bin/env python3
import re
from collections import Counter

# Читаем файл
with open('Core/Localization/LocalizationManager.swift', 'r', encoding='utf-8') as f:
    content = f.read()

# Находим секции для каждого языка
sections = {
    'russian': None,
    'english': None,
    'chinese': None,
    'arabic': None
}

# Ищем начало каждой секции
russian_match = re.search(r'\.russian:\s*\[', content)
english_match = re.search(r'\.english:\s*\[', content)
chinese_match = re.search(r'\.chinese:\s*\[', content)
arabic_match = re.search(r'\.arabic:\s*\[', content)

# Находим конец каждой секции (следующая секция или закрывающая скобка)
def find_section_end(start_pos, content):
    depth = 0
    i = start_pos
    while i < len(content):
        if content[i] == '[':
            depth += 1
        elif content[i] == ']':
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return len(content)

if russian_match:
    start = russian_match.end()
    end = find_section_end(start, content)
    sections['russian'] = content[start:end]

if english_match:
    start = english_match.end()
    end = find_section_end(start, content)
    sections['english'] = content[start:end]

if chinese_match:
    start = chinese_match.end()
    end = find_section_end(start, content)
    sections['chinese'] = content[start:end]

if arabic_match:
    start = arabic_match.end()
    end = find_section_end(start, content)
    sections['arabic'] = content[start:end]

# Проверяем каждую секцию на дубликаты
found_duplicates = False
for lang, section_content in sections.items():
    if not section_content:
        continue
    
    # Находим все ключи в этой секции
    pattern = r'"([^"]+)":\s*"[^"]*"'
    keys = re.findall(pattern, section_content)
    
    # Считаем частоту
    key_counts = Counter(keys)
    
    # Находим дубликаты
    duplicates = {k: v for k, v in key_counts.items() if v > 1}
    
    if duplicates:
        found_duplicates = True
        print(f'\n🔴 ДУБЛИКАТЫ В СЕКЦИИ {lang.upper()}:')
        print('=' * 60)
        for key, count in sorted(duplicates.items()):
            print(f'❌ "{key}": встречается {count} раз(а)')
            
            # Находим строки с дубликатами
            lines = section_content.split('\n')
            found = 0
            for i, line in enumerate(lines, 1):
                if f'"{key}":' in line:
                    found += 1
                    # Находим реальный номер строки в файле
                    real_line = content[:content.find(section_content)].count('\n') + i + 1
                    print(f'  Строка {real_line}: {line.strip()[:100]}')
                    if found >= 10:
                        print(f'  ... (и еще {duplicates[key] - 10} вхождений)')
                        break

if not found_duplicates:
    print('✅ Дубликаты внутри языковых секций не найдены!')
    print('   (Дубликаты между разными языками - это нормально)')
