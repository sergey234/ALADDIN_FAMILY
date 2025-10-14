#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SFM Manual Fixer - Ручное исправление структуры SFM реестра
"""

import json
import re
from datetime import datetime

def extract_function(content, start_pos):
    """Извлечение функции из контента"""
    brace_count = 0
    pos = start_pos
    while pos < len(content):
        if content[pos] == '{':
            brace_count += 1
        elif content[pos] == '}':
            brace_count -= 1
            if brace_count == 0:
                return content[start_pos:pos+1]
        pos += 1
    return None

def fix_sfm_manual():
    """Ручное исправление структуры SFM реестра"""
    try:
        print("🔧 РУЧНОЕ ИСПРАВЛЕНИЕ СТРУКТУРЫ SFM РЕЕСТРА")
        print("=" * 50)
        
        # Загружаем файл
        with open('data/sfm/function_registry.json', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Найдем позицию блока functions
        functions_pos = content.find('"functions":')
        
        # Найдем закрывающую скобку блока functions
        brace_count = 0
        pos = functions_pos
        while pos < len(content):
            if content[pos] == '{':
                brace_count += 1
            elif content[pos] == '}':
                brace_count -= 1
                if brace_count == 0:
                    functions_end = pos
                    break
            pos += 1
        
        print(f"Блок functions заканчивается на позиции: {functions_end}")
        
        # Найдем функции после блока functions
        after_functions = content[functions_end:]
        
        # Извлечем функции
        functions_to_move = []
        
        # smart_monitoring_system
        smart_monitoring_pos = after_functions.find('"smart_monitoring_system":')
        if smart_monitoring_pos != -1:
            smart_monitoring_func = extract_function(after_functions, smart_monitoring_pos)
            if smart_monitoring_func:
                functions_to_move.append(smart_monitoring_func)
                print("✅ smart_monitoring_system извлечена")
        
        # intrusion_prevention
        intrusion_pos = after_functions.find('"intrusion_prevention":')
        if intrusion_pos != -1:
            intrusion_func = extract_function(after_functions, intrusion_pos)
            if intrusion_func:
                functions_to_move.append(intrusion_func)
                print("✅ intrusion_prevention извлечена")
        
        # circuit_breaker
        circuit_breaker_pos = after_functions.find('"circuit_breaker":')
        if circuit_breaker_pos != -1:
            circuit_breaker_func = extract_function(after_functions, circuit_breaker_pos)
            if circuit_breaker_func:
                functions_to_move.append(circuit_breaker_func)
                print("✅ circuit_breaker извлечена")
        
        if not functions_to_move:
            print("✅ Все функции уже в правильном месте")
            return True
        
        print(f"Найдено функций для перемещения: {len(functions_to_move)}")
        
        # Создадим новый контент
        before_functions = content[:functions_end]
        after_functions_clean = content[functions_end:]
        
        # Удалим функции из неправильного места
        for func_content in functions_to_move:
            after_functions_clean = after_functions_clean.replace(func_content, '')
        
        # Добавим функции внутрь блока functions
        functions_to_add = ',\n  ' + ',\n  '.join(functions_to_move)
        new_content = before_functions + functions_to_add + after_functions_clean
        
        # Очистим лишние запятые и пробелы
        new_content = re.sub(r',\s*,+', ',', new_content)
        new_content = re.sub(r',\s*}', '}', new_content)
        new_content = re.sub(r'{\s*,', '{', new_content)
        
        # Создадим резервную копию
        backup_name = f"data/sfm/function_registry_backup_manual_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(backup_name, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Резервная копия создана: {backup_name}")
        
        # Сохраним исправленный файл
        with open('data/sfm/function_registry.json', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Структура SFM реестра исправлена")
        
        # Проверим результат
        try:
            with open('data/sfm/function_registry.json', 'r', encoding='utf-8') as f:
                registry = json.load(f)
            
            functions = registry.get('functions', {})
            print(f"✅ Всего функций в реестре: {len(functions)}")
            
            # Проверим перемещенные функции
            moved_functions = ['smart_monitoring_system', 'intrusion_prevention', 'circuit_breaker']
            for func_name in moved_functions:
                if func_name in functions:
                    print(f"✅ {func_name} успешно перемещена")
                else:
                    print(f"❌ {func_name} НЕ найдена")
            
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ Ошибка JSON после исправления: {e}")
            print(f"Строка: {e.lineno if hasattr(e, 'lineno') else 'неизвестно'}")
            return False
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    fix_sfm_manual()