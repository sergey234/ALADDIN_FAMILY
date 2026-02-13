#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для обновления main.py на сервере
Добавляет импорты и подключения для Components и System роутеров
"""

import re
import sys

def update_main_py(content: str) -> str:
    """Обновляет main.py, добавляя импорты и подключения роутеров"""
    
    # 1. Добавляем импорты после ai_assistant_router
    if 'from security.api.routers.components_router import router as components_router' not in content:
        # Находим место после импорта ai_assistant_router
        pattern = r'(# ✅ ДОБАВЛЕНО: Импортируем AI Assistant Router\ntry:\n    from security\.api\.routers\.ai_assistant_router import router as ai_assistant_router\n    ai_assistant_available = True\nexcept ImportError as e:\n    print\(f"⚠️ ai_assistant_router недоступен: \{e\}"\)\n    ai_assistant_available = False)'
        replacement = r'''\1

# ✅ ЗАДАЧА 21: Импортируем Components Router
try:
    from security.api.routers.components_router import router as components_router
    components_router_available = True
except ImportError as e:
    print(f"⚠️ components_router недоступен: {e}")
    components_router_available = False
    components_router = None

# ✅ ЗАДАЧА 23: Импортируем System Router
try:
    from security.api.routers.system_router import router as system_router
    system_router_available = True
except ImportError as e:
    print(f"⚠️ system_router недоступен: {e}")
    system_router_available = False
    system_router = None'''
        content = re.sub(pattern, replacement, content)
    
    # 2. Добавляем подключения после ai_assistant_router
    if 'app.include_router(components_router)' not in content:
        # Находим место после подключения ai_assistant_router
        pattern = r'(# ✅ ДОБАВЛЕНО: Подключение AI Assistant Router\nif ai_assistant_available:\n    try:\n        app\.include_router\(ai_assistant_router\)\n        print\("✅ Роутер AI Assistant подключен"\)\n    except Exception as e:\n        print\(f"❌ Ошибка подключения AI Assistant: \{e\}"\))'
        replacement = r'''\1

# ✅ ЗАДАЧА 21: Подключение Components Router
if components_router_available:
    try:
        app.include_router(components_router)
        print("✅ Роутер Components подключен")
    except Exception as e:
        print(f"❌ Ошибка подключения Components: {e}")

# ✅ ЗАДАЧА 23: Подключение System Router
if system_router_available:
    try:
        app.include_router(system_router)
        print("✅ Роутер System подключен")
    except Exception as e:
        print(f"❌ Ошибка подключения System: {e}")'''
        content = re.sub(pattern, replacement, content)
    
    return content

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python3 main_py_update_patch.py <путь_к_main.py>")
        sys.exit(1)
    
    main_py_path = sys.argv[1]
    
    try:
        # Читаем main.py
        with open(main_py_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Обновляем
        updated_content = update_main_py(content)
        
        # Записываем обратно
        with open(main_py_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print("✅ main.py успешно обновлен")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        sys.exit(1)
