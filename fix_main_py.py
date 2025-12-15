#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Исправление main.py - закрытие незакрытого try блока для location_bubble_router
"""

# Читаем main.py
with open('/opt/aladdin-backend/main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Исправляем: находим и заменяем проблемный блок
new_lines = []
idx = 0
while idx < len(lines):
    # Ищем паттерн: try: + location_bubble_router + пустая + try:
    if (idx < len(lines) - 3 and 
        lines[idx].strip() == 'try:' and 
        'location_bubble_router' in lines[idx+1] and
        lines[idx+2].strip() == '' and
        lines[idx+3].strip() == 'try:'):
        # Заменяем на правильный блок
        new_lines.append('try:\n')
        new_lines.append('    app.include_router(location_bubble_router)\n')
        new_lines.append('    print("✅ Location Bubble Router зарегистрирован")\n')
        new_lines.append('except Exception as e:\n')
        new_lines.append('    print(f"⚠️ Не удалось зарегистрировать Location Bubble Router: {e}")\n')
        new_lines.append('\n')
        new_lines.append('try:\n')  # Добавляем следующий try
        # Пропускаем: try:, location_bubble_router, пустая, try:
        idx += 4
        continue
    
    new_lines.append(lines[idx])
    idx += 1

# Сохраняем
with open('/opt/aladdin-backend/main.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('✅ main.py исправлен')
