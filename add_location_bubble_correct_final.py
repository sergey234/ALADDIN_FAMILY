#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Правильное добавление Location Bubble Router в main.py
Точно по инструкции из ИНСТРУКЦИЯ_ДЕПЛОЯ_AI_CATEGORIES.md
"""
import re
import sys

def main():
    main_py_path = "/opt/aladdin-backend/main.py"
    
    print("=== ДОБАВЛЕНИЕ LOCATION BUBBLE ROUTER (ПО ИНСТРУКЦИИ) ===")
    print("")
    
    with open(main_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверка, не добавлен ли уже
    if "location_bubble_router" in content:
        print("⚠️  Location Bubble Router уже добавлен!")
        # Удаляем старые добавления
        content = re.sub(r'^from security\.api\.routers\.location_bubble_router import router as location_bubble_router\s*\n', '', content, flags=re.MULTILINE)
        content = re.sub(r'try:\s*\n\s*app\.include_router\(location_bubble_router\)\s*\n\s*print\("✅ Location Bubble Router зарегистрирован"\)\s*\nexcept Exception as e:\s*\n\s*print\(f"⚠️ Не удалось зарегистрировать Location Bubble Router: \{e\}"\)\s*\n', '', content, flags=re.MULTILINE)
        content = re.sub(r'\s*app\.include_router\(location_bubble_router\)\s*\n', '', content)
        print("✅ Старые добавления удалены")
    
    # 1. Добавление импорта (в начале файла, после других router импортов)
    import_line = "from security.api.routers.location_bubble_router import router as location_bubble_router"
    
    if import_line not in content:
        # Ищем последний router импорт
        pattern = r'(from security\.api\.routers\.\w+_router import router as \w+_router)'
        matches = list(re.finditer(pattern, content))
        
        if matches:
            last_match = matches[-1]
            insert_pos = last_match.end()
            # Добавляем после последнего router импорта
            content = content[:insert_pos] + '\n' + import_line + content[insert_pos:]
            print("✅ Импорт добавлен после других router импортов")
        else:
            print("❌ Не найдено место для импорта")
            return 1
    
    # 2. Добавление регистрации (в try/except блоке, как у других routers)
    register_code = '''try:
    app.include_router(location_bubble_router)
    print("✅ Location Bubble Router зарегистрирован")
except Exception as e:
    print(f"⚠️ Не удалось зарегистрировать Location Bubble Router: {e}")
'''
    
    if "app.include_router(location_bubble_router)" not in content:
        # Ищем последний except блок для crash_detection_router
        pattern = r'(except Exception as e:\s*\n\s*print\(f"⚠️ Не удалось зарегистрировать Crash Detection Router: \{e\}"\)\s*\n)'
        match = re.search(pattern, content)
        
        if match:
            insert_pos = match.end()
            content = content[:insert_pos] + register_code + content[insert_pos:]
            print("✅ Регистрация router добавлена в try/except блок")
        else:
            print("❌ Не найдено место для регистрации")
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
    sys.exit(main())
