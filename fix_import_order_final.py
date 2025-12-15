#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление порядка импортов - импорты должны быть ДО использования
"""
import re

def main():
    main_py_path = "/opt/aladdin-backend/main.py"
    
    print("=== ИСПРАВЛЕНИЕ ПОРЯДКА ИМПОРТОВ ===")
    print("")
    
    with open(main_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Находим все импорты router
    import_pattern = r'(from security\.api\.routers\.\w+_router import router as \w+_router)'
    imports = list(re.finditer(import_pattern, content))
    
    # Находим использование location_bubble_router
    use_pattern = r'app\.include_router\(location_bubble_router\)'
    use_match = re.search(use_pattern, content)
    
    if not use_match:
        print("❌ Не найдено использование location_bubble_router")
        return 1
    
    use_pos = use_match.start()
    
    # Проверяем, есть ли импорт location_bubble_router ДО использования
    location_import = None
    for imp in imports:
        if 'location_bubble_router' in imp.group(0):
            location_import = imp
            break
    
    if location_import and location_import.start() > use_pos:
        print(f"⚠️  Импорт на позиции {location_import.start()}, использование на {use_pos}")
        
        # Удаляем импорт из текущего места
        import_line = location_import.group(0)
        content = content[:location_import.start()] + content[location_import.end():]
        
        # Находим последний router импорт ДО использования
        insert_pos = None
        for imp in imports:
            if imp.start() < use_pos and 'location_bubble_router' not in imp.group(0):
                insert_pos = imp.end()
        
        if insert_pos:
            # Вставляем импорт после последнего router импорта
            content = content[:insert_pos] + '\n' + import_line + content[insert_pos:]
            print(f"✅ Импорт перемещен на позицию {insert_pos}")
        else:
            print("❌ Не найдено место для импорта")
            return 1
    elif not location_import:
        print("❌ Импорт location_bubble_router не найден")
        return 1
    else:
        print("✅ Импорт уже в правильном месте")
    
    # Сохранение
    with open(main_py_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Проверка синтаксиса
    import subprocess
    result = subprocess.run(['python3', '-m', 'py_compile', main_py_path], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Синтаксис проверен")
        
        # Проверяем порядок
        with open(main_py_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        import_line_num = None
        use_line_num = None
        
        for i, line in enumerate(lines, 1):
            if 'from security.api.routers.location_bubble_router import' in line:
                import_line_num = i
            if 'app.include_router(location_bubble_router)' in line:
                use_line_num = i
        
        if import_line_num and use_line_num:
            if import_line_num < use_line_num:
                print(f"✅ Импорт на строке {import_line_num}, использование на {use_line_num} - правильно")
            else:
                print(f"❌ Импорт на строке {import_line_num}, использование на {use_line_num} - неправильно!")
                return 1
        
        return 0
    else:
        print(f"❌ Ошибка синтаксиса: {result.stderr}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
