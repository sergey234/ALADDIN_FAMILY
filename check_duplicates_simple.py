#!/usr/bin/env python3
import re
from collections import Counter

with open('Core/Localization/LocalizationManager.swift', 'r', encoding='utf-8') as f:
    content = f.read()

# Находим секции более точно
for lang in ['russian', 'english', 'chinese', 'arabic']:
    # Находим начало секции
    pattern_start = rf'\.{lang}:\s*\['
    match_start = re.search(pattern_start, content)
    if not match_start:
        continue
    
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
        if i < len(content) - 10:
            next_section = re.match(r'\.(russian|english|chinese|arabic):\s*\[', content[i:])
            if next_section and depth == 0:
                end_pos = i
                break
        i += 1
    
    # Извлекаем секцию
    section_content = content[start_pos:end_pos]
    
    # Находим все ключи
    keys = re.findall(r'"([^"]+)":', section_content)
    
    # Проверяем дубликаты
    counts = Counter(keys)
    duplicates = {k: v for k, v in counts.items() if v > 1}
    
    if duplicates:
        print(f'\n🔴 ДУБЛИКАТЫ В СЕКЦИИ .{lang}:')
        for k, v in sorted(duplicates.items()):
            print(f'  ❌ "{k}": {v} раз(а)')
    else:
        print(f'✅ Секция .{lang}: дубликатов не найдено ({len(keys)} ключей)')
