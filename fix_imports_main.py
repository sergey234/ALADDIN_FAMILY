#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Исправление импортов в main.py - перемещение импортов роутеров в начало
"""

# Читаем main.py
with open('/opt/aladdin-backend/main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Находим где находятся импорты роутеров в начале (около строки 885)
import_section_end = None
for idx, line in enumerate(lines):
    if 'from security.api.routers.location_bubble_router' in line:
        import_section_end = idx
        break

# Находим импорты после if __name__
late_imports = []
if __name__ = None
for idx, line in enumerate(lines):
    if 'if __name__' in line:
        # Ищем импорты после этой строки
        for j in range(idx+1, len(lines)):
            if 'from security.api.routers' in lines[j]:
                late_imports.append((j, lines[j]))
            elif lines[j].strip() and not lines[j].strip().startswith('#'):
                break
        break

# Удаляем дубликаты и перемещаем недостающие
if late_imports and import_section_end is not None:
    # Собираем уже импортированные роутеры
    existing_imports = set()
    for idx in range(import_section_end - 5, import_section_end + 1):
        if idx >= 0 and idx < len(lines) and 'from security.api.routers' in lines[idx]:
            existing_imports.add(lines[idx].strip())
    
    # Удаляем поздние импорты (в обратном порядке чтобы индексы не сбились)
    for idx, _ in reversed(late_imports):
        lines.pop(idx)
    
    # Добавляем недостающие импорты после других
    for idx, import_line in late_imports:
        if import_line.strip() not in existing_imports:
            lines.insert(import_section_end + 1, import_line)
            import_section_end += 1

# Сохраняем
with open('/opt/aladdin-backend/main.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('✅ Импорты исправлены')
