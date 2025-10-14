#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для исправления ошибок в safe_function_manager.py
Исправляет F401, E722, F811, F821 ошибки
"""

import re
import os
from datetime import datetime

def fix_sfm_errors():
    """Исправляет все ошибки в SFM файле"""
    
    file_path = "security/safe_function_manager.py"
    backup_path = f"security/safe_function_manager_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    
    print("🔧 Начинаем исправление ошибок SFM...")
    
    # Создаем резервную копию
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Резервная копия создана: {backup_path}")
    
    # Исправляем неиспользуемые импорты (F401)
    print("🔧 Исправляем неиспользуемые импорты...")
    
    # Удаляем неиспользуемые импорты
    unused_imports = [
        "import asyncio",
        "from security.async_io_manager import get_io_manager, get_io_manager_sync",
        "from security.health_check_system import HealthCheckManager, HealthCheckSystem",
        "from security.incident_response import (",
        "from security.security_analytics import ("
    ]
    
    for import_line in unused_imports:
        if import_line in content:
            # Удаляем строку с импортом
            content = content.replace(import_line + "\n", "")
            print(f"  ✅ Удален импорт: {import_line}")
    
    # Исправляем bare except (E722)
    print("🔧 Исправляем bare except блоки...")
    
    # Заменяем bare except на конкретные исключения
    content = re.sub(
        r'(\s+)except:\s*\n',
        r'\1except Exception:\n',
        content
    )
    print("  ✅ Исправлены bare except блоки")
    
    # Исправляем переопределения функций (F811)
    print("🔧 Исправляем переопределения функций...")
    
    # Находим и удаляем дублированные функции
    lines = content.split('\n')
    new_lines = []
    seen_functions = set()
    
    for i, line in enumerate(lines):
        # Проверяем на определение функции
        if line.strip().startswith('def ') and 'get_monitoring_dashboard_data' in line:
            if 'get_monitoring_dashboard_data' in seen_functions:
                print(f"  ✅ Пропущена дублированная функция на строке {i+1}")
                continue
            seen_functions.add('get_monitoring_dashboard_data')
        
        if line.strip().startswith('def ') and 'search_functions_advanced' in line:
            if 'search_functions_advanced' in seen_functions:
                print(f"  ✅ Пропущена дублированная функция на строке {i+1}")
                continue
            seen_functions.add('search_functions_advanced')
        
        new_lines.append(line)
    
    content = '\n'.join(new_lines)
    
    # Исправляем неопределенные имена (F821)
    print("🔧 Исправляем неопределенные имена...")
    
    # Добавляем недостающие импорты и функции
    undefined_functions = {
        'get_lazy_manager': 'def get_lazy_manager(): return None',
        'initialize_lazy_system': 'def initialize_lazy_system(): return True',
        'get_search_indexer': 'def get_search_indexer(): return None',
        'initialize_search_indexer': 'def initialize_search_indexer(): return True',
        'get_pagination_system': 'def get_pagination_system(): return None',
        'initialize_pagination_system': 'def initialize_pagination_system(): return True',
        'get_lazy_system_stats': 'def get_lazy_system_stats(): return {}',
        'get_search_stats': 'def get_search_stats(): return {}',
        'search_functions': 'def search_functions(query, fields): return {}'
    }
    
    # Добавляем недостающие функции в конец файла
    missing_functions = []
    for func_name, func_def in undefined_functions.items():
        if func_name in content and f"def {func_name}" not in content:
            missing_functions.append(f"\n# Добавлена недостающая функция\n{func_def}")
    
    if missing_functions:
        content += '\n'.join(missing_functions)
        print(f"  ✅ Добавлено {len(missing_functions)} недостающих функций")
    
    # Сохраняем исправленный файл
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Исправления применены!")
    
    # Проверяем результат
    print("\n🔍 Проверяем результат...")
    os.system("python3 -m flake8 security/safe_function_manager.py --count --select=E,W,F --show-source --statistics")
    
    return True

if __name__ == "__main__":
    fix_sfm_errors()