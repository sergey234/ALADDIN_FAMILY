#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Правильное добавление Location Bubble Router в main.py
"""
import re
import sys

def main():
    main_py_path = "/opt/aladdin-backend/main.py"
    
    print("=== ДОБАВЛЕНИЕ LOCATION BUBBLE ROUTER ===")
    print("")
    
    # Чтение файла
    with open(main_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверка, не добавлен ли уже
    if "location_bubble_router" in content:
        print("⚠️  Location Bubble Router уже добавлен!")
        return 0
    
    # 1. Добавление импорта
    if "from security.api.routers.location_bubble_router import router as location_bubble_router" not in content:
        # Ищем последний router импорт
        pattern = r'(from security\.api\.routers\.\w+_router import router as \w+_router)'
        matches = list(re.finditer(pattern, content))
        if matches:
            last_match = matches[-1]
            insert_pos = last_match.end()
            content = content[:insert_pos] + '\nfrom security.api.routers.location_bubble_router import router as location_bubble_router' + content[insert_pos:]
            print("✅ Импорт добавлен")
    
    # 2. Добавление регистрации после последнего except блока
    # Ищем паттерн: except Exception as e:\n    print(f"⚠️ Не удалось зарегистрировать Crash Detection Router: {e}")
    pattern = r'(except Exception as e:\s*\n\s*print\(f"⚠️ Не удалось зарегистрировать Crash Detection Router: \{e\}"\)\s*\n)'
    match = re.search(pattern, content)
    
    if match:
        insert_pos = match.end()
        new_code = '''try:
    app.include_router(location_bubble_router)
    print("✅ Location Bubble Router зарегистрирован")
except Exception as e:
    print(f"⚠️ Не удалось зарегистрировать Location Bubble Router: {e}")

'''
        content = content[:insert_pos] + new_code + content[insert_pos:]
        print("✅ Регистрация router добавлена")
    else:
        print("❌ Не найдено место для вставки")
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
