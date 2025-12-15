#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление позиции импорта location_bubble_router
"""
import re

def main():
    main_py_path = "/opt/aladdin-backend/main.py"
    
    print("=== ИСПРАВЛЕНИЕ ПОЗИЦИИ ИМПОРТА ===")
    print("")
    
    with open(main_py_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Находим строки с location_bubble_router
    import_line_idx = None
    use_line_idx = None
    
    for i, line in enumerate(lines):
        if 'from security.api.routers.location_bubble_router import router as location_bubble_router' in line:
            import_line_idx = i
        if 'app.include_router(location_bubble_router)' in line and import_line_idx is not None:
            use_line_idx = i
    
    if import_line_idx is None or use_line_idx is None:
        print("❌ Не найдены строки с location_bubble_router")
        return 1
    
    # Если импорт после использования - перемещаем
    if import_line_idx > use_line_idx:
        print(f"⚠️  Импорт на строке {import_line_idx+1}, использование на {use_line_idx+1}")
        
        # Удаляем импорт из текущего места
        import_line = lines.pop(import_line_idx)
        
        # Находим место для импорта (после других router импортов)
        insert_pos = None
        for i, line in enumerate(lines):
            if 'from security.api.routers.crash_detection_router import router as crash_detection_router' in line:
                insert_pos = i + 1
                break
        
        if insert_pos:
            lines.insert(insert_pos, import_line)
            print(f"✅ Импорт перемещен на строку {insert_pos+1}")
        else:
            print("❌ Не найдено место для импорта")
            return 1
    
    # Сохранение
    with open(main_py_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
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
