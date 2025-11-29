#!/usr/bin/env python3
"""
Скрипт для проверки дубликатов ключей в словаре локализации
Использование: python3 scripts/check_localization_duplicates.py
"""

import re
import sys
from collections import defaultdict

def check_duplicates(file_path):
    """Проверяет наличие дубликатов ключей в словаре локализации"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Находим словарь translations
    start = content.find('var translations:')
    if start == -1:
        start = content.find('lazy var translations:')
    if start == -1:
        print('❌ Словарь translations не найден')
        return False
    
    # Находим конец словаря
    dict_start = content.find('[', start)
    if dict_start == -1:
        print('❌ Начало словаря не найдено')
        return False
    
    # Находим все ключи в словаре (включая все языки)
    all_keys = {}
    duplicates = []
    pattern = r'\"([^\"]+)\"\s*:'
    matches = re.finditer(pattern, content[dict_start:])
    
    # Определяем границы каждого языка
    lines = content.split('\n')
    lang_boundaries = {}
    current_lang = None
    
    for i, line in enumerate(lines, 1):
        if '.russian: [' in line:
            current_lang = 'russian'
            lang_boundaries[current_lang] = {'start': i}
        elif '.english: [' in line:
            if current_lang:
                lang_boundaries[current_lang]['end'] = i - 1
            current_lang = 'english'
            lang_boundaries[current_lang] = {'start': i}
        elif '.chinese: [' in line:
            if current_lang:
                lang_boundaries[current_lang]['end'] = i - 1
            current_lang = 'chinese'
            lang_boundaries[current_lang] = {'start': i}
        elif '.arabic: [' in line:
            if current_lang:
                lang_boundaries[current_lang]['end'] = i - 1
            current_lang = 'arabic'
            lang_boundaries[current_lang] = {'start': i}
    
    # Находим конец последнего языка
    if current_lang:
        for i in range(lang_boundaries[current_lang]['start'], len(lines)):
            if '],' in lines[i-1] and i > lang_boundaries[current_lang]['start']:
                lang_boundaries[current_lang]['end'] = i
                break
    
    # Проверяем дубликаты внутри каждого языка
    has_duplicates = False
    for lang_name, boundaries in lang_boundaries.items():
        if 'start' not in boundaries or 'end' not in boundaries:
            continue
        
        keys = {}
        lang_duplicates = []
        
        for i in range(boundaries['start'], boundaries['end'] + 1):
            if i < len(lines):
                line = lines[i-1]
                if '"' in line and ':' in line and not line.strip().startswith('//'):
                    parts = line.split('"')
                    if len(parts) >= 2:
                        key = parts[1]
                        if key in keys:
                            lang_duplicates.append((key, keys[key], i))
                        else:
                            keys[key] = i
        
        if lang_duplicates:
            has_duplicates = True
            print(f'\n❌ {lang_name.upper()}: найдено {len(lang_duplicates)} дубликатов')
            for key, first_line, second_line in lang_duplicates[:10]:
                print(f'  "{key}": строки {first_line} и {second_line}')
            if len(lang_duplicates) > 10:
                print(f'  ... и еще {len(lang_duplicates) - 10} дубликатов')
        else:
            print(f'✅ {lang_name.upper()}: дубликатов не найдено ({len(keys)} уникальных ключей)')
    
    return not has_duplicates

if __name__ == '__main__':
    file_path = 'Core/Localization/LocalizationManager.swift'
    
    print('🔍 Проверка дубликатов ключей в словаре локализации...\n')
    
    if check_duplicates(file_path):
        print('\n✅ Все проверки пройдены! Дубликатов не найдено.')
        sys.exit(0)
    else:
        print('\n❌ Найдены дубликаты! Исправьте их перед коммитом.')
        sys.exit(1)

