#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для проверки дубликатов ключей в LocalizationManager.swift
"""

import re
import sys

def check_duplicates(file_path):
    """Проверяет дубликаты ключей в словаре локализации"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем русский словарь
    russian_keys = {}
    in_russian = False
    russian_line = 0
    
    for i, line in enumerate(content.split('\n'), 1):
        if '.russian:' in line:
            in_russian = True
            russian_line = i
        elif '.english:' in line:
            in_russian = False
        elif in_russian and '],' in line:
            break
        elif in_russian:
            matches = re.findall(r'"([^"]+)":', line)
            for key in matches:
                if key in russian_keys:
                    print(f'❌ ДУБЛИКАТ в русском словаре: "{key}"')
                    print(f'   Первый раз на строке {russian_keys[key]}, второй раз на строке {i}')
                    return False
                russian_keys[key] = i
    
    # Проверяем английский словарь
    english_keys = {}
    in_english = False
    
    for i, line in enumerate(content.split('\n'), 1):
        if '.english:' in line:
            in_english = True
        elif '.chinese:' in line:
            in_english = False
            break
        elif in_english and '],' in line:
            break
        elif in_english:
            matches = re.findall(r'"([^"]+)":', line)
            for key in matches:
                if key in english_keys:
                    print(f'❌ ДУБЛИКАТ в английском словаре: "{key}"')
                    print(f'   Первый раз на строке {english_keys[key]}, второй раз на строке {i}')
                    return False
                english_keys[key] = i
    
    print(f'✅ ДУБЛИКАТОВ НЕТ!')
    print(f'   Русский словарь: {len(russian_keys)} ключей')
    print(f'   Английский словарь: {len(english_keys)} ключей')
    return True

if __name__ == '__main__':
    file_path = 'Core/Localization/LocalizationManager.swift'
    success = check_duplicates(file_path)
    sys.exit(0 if success else 1)
