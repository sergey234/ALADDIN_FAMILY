#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление порядка импортов в main.py
"""
import re

def main():
    main_py_path = "/opt/aladdin-backend/main.py"
    
    print("=== ИСПРАВЛЕНИЕ ПОРЯДКА ИМПОРТОВ ===")
    print("")
    
    with open(main_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Удаляем импорт location_bubble_router если он в неправильном месте
    content = re.sub(r'^from security\.api\.routers\.location_bubble_router import router as location_bubble_router\s*\n', '', content, flags=re.MULTILINE)
    
    # Находим место для импорта (после других router импортов)
    pattern = r'(from security\.api\.routers\.\w+_router import router as \w+_router)'
    matches = list(re.finditer(pattern, content))
    
    if matches:
        last_match = matches[-1]
        insert_pos = last_match.end()
        # Добавляем импорт после последнего router импорта
        content = content[:insert_pos] + '\nfrom security.api.routers.location_bubble_router import router as location_bubble_router' + content[insert_pos:]
        print("✅ Импорт перемещен в правильное место")
    else:
        print("❌ Не найдено место для импорта")
        return 1
    
    # Сохранение
    with open(main_py_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Проверка синтаксиса
    import subprocess
    result = subprocess.run(['python3', '-m', 'py_compile', main_py_path], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Синтаксис проверен")
        return 0
    else:
        print(f"❌ Ошибка синтаксиса: {result.stderr}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
