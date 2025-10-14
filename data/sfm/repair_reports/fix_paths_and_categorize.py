#!/usr/bin/env python3
"""
Комбинированный скрипт: исправление путей + категоризация UNKNOWN функций
Сначала исправляет пути, потом категоризирует по 5-10 функций за раз
"""

import json
import os
import re
from datetime import datetime
from collections import Counter

def find_file_in_project(filename, root_dir):
    """Ищет файл по имени во всем проекте."""
    for dirpath, _, filenames in os.walk(root_dir):
        if filename in filenames:
            return os.path.relpath(os.path.join(dirpath, filename), root_dir)
    return None

def analyze_file_content(file_path, root_dir):
    """Анализирует содержимое файла для определения типа функции."""
    full_path = os.path.join(root_dir, file_path)
    
    if not os.path.exists(full_path):
        return "file_not_found"
    
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()
    except:
        return "unreadable"
    
    # Паттерны для определения типов
    patterns = {
        'ai_agent': [
            r'class.*agent', r'def.*agent', r'ai.*agent', r'behavioral.*analysis',
            r'threat.*detection', r'incident.*response', r'password.*security',
            r'mobile.*security', r'compliance.*agent', r'data.*protection'
        ],
        'bot': [
            r'class.*bot', r'def.*bot', r'telegram.*bot', r'whatsapp.*bot',
            r'instagram.*bot', r'gaming.*bot', r'parental.*control.*bot',
            r'emergency.*response.*bot', r'notification.*bot'
        ],
        'manager': [
            r'class.*manager', r'def.*manager', r'function.*manager', r'safe.*function.*manager',
            r'user.*interface.*manager', r'data.*protection.*manager', r'network.*protection.*manager'
        ],
        'security': [
            r'security.*system', r'security.*service', r'security.*module',
            r'encryption', r'authentication', r'authorization', r'access.*control'
        ],
        'service': [
            r'class.*service', r'def.*service', r'notification.*service',
            r'emergency.*service', r'vpn.*service'
        ],
        'integration': [
            r'integration', r'api.*integration', r'external.*service',
            r'russian.*api', r'banking.*integration', r'messenger.*integration'
        ],
        'monitoring': [
            r'monitoring', r'analytics', r'metrics', r'performance.*monitor',
            r'health.*check', r'alert.*system'
        ],
        'vpn': [
            r'vpn', r'wireguard', r'openvpn', r'shadowsocks', r'v2ray',
            r'tunnel', r'proxy'
        ],
        'utility': [
            r'utility', r'helper', r'utils', r'common', r'base.*class',
            r'config', r'configuration'
        ],
        'core': [
            r'core', r'base', r'foundation', r'fundamental', r'primary'
        ]
    }
    
    # Подсчитываем совпадения для каждого типа
    type_scores = {}
    for func_type, pattern_list in patterns.items():
        score = 0
        for pattern in pattern_list:
            matches = len(re.findall(pattern, content))
            score += matches
        type_scores[func_type] = score
    
    # Возвращаем тип с наибольшим количеством совпадений
    if type_scores:
        best_type = max(type_scores, key=type_scores.get)
        if type_scores[best_type] > 0:
            return best_type
    
    return "unknown"

def fix_paths_and_categorize(registry_file, root_dir, max_fixes=10):
    """Исправляет пути и категоризирует UNKNOWN функции."""
    
    # Загружаем реестр
    with open(registry_file, 'r', encoding='utf-8') as f:
        registry_data = json.load(f)
    
    functions = registry_data.get("functions", {})
    unknown_functions = []
    
    # Находим UNKNOWN функции без путей
    for func_id, func_data in functions.items():
        func_type = func_data.get('function_type', '')
        file_path = func_data.get('file_path', '')
        if func_type == 'unknown' and not file_path:
            unknown_functions.append((func_id, func_data))
    
    print(f"🔧 ИСПРАВЛЕНИЕ ПУТЕЙ + КАТЕГОРИЗАЦИЯ")
    print(f"================================================")
    print(f"Всего функций в реестре: {len(functions)}")
    print(f"UNKNOWN функций без путей: {len(unknown_functions)}")
    print(f"Максимум исправлений за раз: {max_fixes}")
    print("")
    
    fixed_paths = 0
    categorized = 0
    type_changes = Counter()
    
    for func_id, func_data in unknown_functions:
        if fixed_paths >= max_fixes:
            break
            
        print(f"🔍 Обрабатываем {func_id}...")
        
        # Шаг 1: Ищем файл
        filename = f"{func_id}.py"
        new_path = find_file_in_project(filename, root_dir)
        
        if new_path:
            # Шаг 2: Исправляем путь
            func_data['file_path'] = new_path
            func_data['last_updated'] = datetime.now().isoformat()
            fixed_paths += 1
            print(f"   ✅ Путь исправлен: {new_path}")
            
            # Шаг 3: Анализируем содержимое и категоризируем
            new_type = analyze_file_content(new_path, root_dir)
            
            if new_type != "unknown" and new_type != "file_not_found" and new_type != "unreadable":
                old_type = func_data.get('function_type', 'unknown')
                func_data['function_type'] = new_type
                type_changes[new_type] += 1
                categorized += 1
                print(f"   ✅ Тип изменен: {old_type} → {new_type}")
            else:
                print(f"   ⚠️ Тип не определен: {new_type}")
        else:
            print(f"   ❌ Файл не найден: {filename}")
        
        print()
    
    # Сохраняем изменения
    with open(registry_file, 'w', encoding='utf-8') as f:
        json.dump(registry_data, f, ensure_ascii=False, indent=4)
    
    print(f"💾 Изменения сохранены в {registry_file}")
    
    # Подсчитываем оставшиеся UNKNOWN
    remaining_unknown = 0
    for func_id, func_data in functions.items():
        if func_data.get('function_type', '') == 'unknown':
            remaining_unknown += 1
    
    print(f"\n🎯 РЕЗУЛЬТАТ:")
    print(f"   Путей исправлено: {fixed_paths}")
    print(f"   Функций категоризировано: {categorized}")
    print(f"   Осталось UNKNOWN функций: {remaining_unknown}")
    
    if type_changes:
        print(f"\n📊 НОВЫЕ ТИПЫ:")
        for func_type, count in type_changes.most_common():
            print(f"   {func_type}: +{count}")

if __name__ == "__main__":
    # Указываем путь к файлу реестра и корневой директории проекта
    registry_path = 'data/sfm/function_registry.json'
    project_root = '.' # Текущая директория

    # Запускаем комбинированный процесс (тестируем на 10 функциях)
    fix_paths_and_categorize(registry_path, project_root, max_fixes=10)
