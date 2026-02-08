#!/usr/bin/env python3
import re
from collections import Counter

# Читаем файл
with open('Core/Localization/LocalizationManager.swift', 'r', encoding='utf-8') as f:
    content = f.read()

# Находим все ключи в словарях
# Паттерн для поиска ключей: "ключ": "значение"
pattern = r'"([^"]+)":\s*"[^"]*"'
keys = re.findall(pattern, content)

# Считаем частоту
key_counts = Counter(keys)

# Находим дубликаты
duplicates = {k: v for k, v in key_counts.items() if v > 1}

if duplicates:
    print('🔍 Найдены дубликаты ключей:')
    print('=' * 60)
    for key, count in sorted(duplicates.items()):
        print(f'❌ "{key}": встречается {count} раз(а)')
    
    # Находим строки с дубликатами
    print('\n📍 Позиции дубликатов:')
    print('=' * 60)
    lines = content.split('\n')
    for key in duplicates.keys():
        print(f'\n🔑 Ключ: "{key}"')
        found = 0
        for i, line in enumerate(lines, 1):
            if f'"{key}":' in line:
                found += 1
                print(f'  Строка {i}: {line.strip()[:100]}')
                if found >= 10:  # Ограничиваем вывод
                    print(f'  ... (и еще {duplicates[key] - 10} вхождений)')
                    break
else:
    print('✅ Дубликаты не найдены!')
