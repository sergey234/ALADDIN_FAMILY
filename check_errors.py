#!/usr/bin/env python3
import re
from collections import Counter

with open('Core/Localization/LocalizationManager.swift', 'r', encoding='utf-8') as f:
    content = f.read()

# Проверяем дубликаты в каждой секции
for lang in ['russian', 'english', 'chinese', 'arabic']:
    pattern = rf'\.{lang}:\s*\[(.*?)\]'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        section = match.group(1)
        keys = re.findall(r'"([^"]+)":', section)
        counts = Counter(keys)
        duplicates = {k: v for k, v in counts.items() if v > 1}
        if duplicates:
            print(f"\n🔴 ДУБЛИКАТЫ В СЕКЦИИ .{lang} ({len(duplicates)}):")
            for k, v in sorted(duplicates.items()):
                print(f"  - {k}: {v} раз(а)")
        else:
            print(f"✅ .{lang}: дубликатов нет ({len(set(keys))} уникальных ключей)")
