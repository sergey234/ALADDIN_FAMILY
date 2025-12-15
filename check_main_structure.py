#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка структуры main.py на сервере
"""

from pathlib import Path

main_py_path = Path('/opt/aladdin-backend/main.py')

with open(main_py_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("📋 Проверка структуры main.py:")
print(f"   Всего строк: {len(lines)}")
print()

# Найти импорты
print("📋 Импорты:")
for i, line in enumerate(lines[:50], 1):
    if 'import' in line or 'from' in line:
        print(f"   {i}: {line.strip()}")

print()
print("📋 Поиск dark_web:")
for i, line in enumerate(lines, 1):
    if 'dark_web' in line.lower():
        print(f"   {i}: {line.strip()}")
        # Показать контекст
        start = max(0, i-3)
        end = min(len(lines), i+3)
        print(f"      Контекст ({start}-{end}):")
        for j in range(start, end):
            marker = ">>>" if j == i-1 else "   "
            print(f"      {marker} {j+1}: {lines[j].rstrip()}")

print()
print("📋 Поиск logger:")
for i, line in enumerate(lines, 1):
    if 'logger' in line.lower() and ('=' in line or 'import' in line):
        print(f"   {i}: {line.strip()}")

print()
print("📋 Проверка around line 993 (где ошибка):")
for i in range(988, min(len(lines), 1000)):
    print(f"   {i+1}: {lines[i].rstrip()}")
