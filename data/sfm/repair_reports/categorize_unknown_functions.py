#!/usr/bin/env python3
"""
Скрипт для категоризации UNKNOWN функций в SFM реестре
Анализирует содержимое файлов и определяет правильные типы
"""

import json
import os
import re
from datetime import datetime
from collections import Counter

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

def categorize_unknown_functions(registry_file, root_dir, max_fixes=5):
    """Категоризирует UNKNOWN функции в SFM реестре."""
    
    # Загружаем реестр
    with open(registry_file, 'r', encoding='utf-8') as f:
        registry_data = json.load(f)
    
    functions = registry_data.get("functions", {})
    unknown_functions = []
    
    # Находим UNKNOWN функции
    for func_id, func_data in functions.items():
        func_type = func_data.get('function_type', '')
        if func_type == 'unknown':
            unknown_functions.append((func_id, func_data))
    
    print(f"🔍 КАТЕГОРИЗАЦИЯ UNKNOWN ФУНКЦИЙ (ТЕСТ НА 5)")
    print(f"================================================")
    print(f"Всего функций в реестре: {len(functions)}")
    print(f"UNKNOWN функций: {len(unknown_functions)}")
    print(f"Максимум исправлений за раз: {max_fixes}")
    print("")
    
    fixed_count = 0
    type_changes = Counter()
    
    for func_id, func_data in unknown_functions:
        if fixed_count >= max_fixes:
            break
            
        file_path = func_data.get('file_path', '')
        if not file_path:
            print(f"⏩ Пропускаем {func_id} - нет пути к файлу")
            continue
        
        print(f"🔍 Анализируем {func_id}...")
        print(f"   Файл: {file_path}")
        
        # Анализируем содержимое файла
        new_type = analyze_file_content(file_path, root_dir)
        
        if new_type != "unknown" and new_type != "file_not_found" and new_type != "unreadable":
            # Обновляем тип функции
            old_type = func_data.get('function_type', 'unknown')
            func_data['function_type'] = new_type
            func_data['last_updated'] = datetime.now().isoformat()
            
            type_changes[new_type] += 1
            fixed_count += 1
            
            print(f"✅ {func_id}: {old_type} → {new_type}")
        else:
            print(f"❌ {func_id}: не удалось определить тип ({new_type})")
        
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
    print(f"   Исправлено: {fixed_count} из {max_fixes} запланированных")
    print(f"   Осталось UNKNOWN функций: {remaining_unknown}")
    
    if type_changes:
        print(f"\n📊 НОВЫЕ ТИПЫ:")
        for func_type, count in type_changes.most_common():
            print(f"   {func_type}: +{count}")

if __name__ == "__main__":
    # Указываем путь к файлу реестра и корневой директории проекта
    registry_path = 'data/sfm/function_registry.json'
    project_root = '.' # Текущая директория

    # Запускаем категоризацию (тестируем на 5 функциях)
    categorize_unknown_functions(registry_path, project_root, max_fixes=5)
