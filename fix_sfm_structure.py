#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SFM Structure Fixer - Исправление структуры SFM реестра
Перемещает все функции внутрь блока functions
"""

import json
import re
from datetime import datetime

def fix_sfm_structure():
    """Исправление структуры SFM реестра"""
    try:
        print("🔧 ИСПРАВЛЕНИЕ СТРУКТУРЫ SFM РЕЕСТРА")
        print("=" * 50)
        
        # Загружаем файл
        with open('data/sfm/function_registry.json', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Найдем позицию блока functions
        functions_pos = content.find('"functions":')
        print(f"Позиция блока functions: {functions_pos}")
        
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
        
        # Найдем все функции после блока functions
        after_functions = content[functions_end:]
        
        # Найдем функции для перемещения
        functions_to_move = []
        function_patterns = [
            r'"smart_monitoring_system":\s*{[^}]*}(?:\s*,\s*"[^"]*":\s*{[^}]*})*',
            r'"intrusion_prevention":\s*{[^}]*}(?:\s*,\s*"[^"]*":\s*{[^}]*})*',
            r'"circuit_breaker":\s*{[^}]*}(?:\s*,\s*"[^"]*":\s*{[^}]*})*'
        ]
        
        for pattern in function_patterns:
            matches = re.findall(pattern, after_functions, re.DOTALL)
            functions_to_move.extend(matches)
        
        print(f"Найдено функций для перемещения: {len(functions_to_move)}")
        
        if not functions_to_move:
            print("✅ Все функции уже в правильном месте")
            return
        
        # Создадим новый контент
        before_functions = content[:functions_end]
        after_functions_clean = content[functions_end:]
        
        # Удалим функции из неправильного места
        for func_content in functions_to_move:
            after_functions_clean = after_functions_clean.replace(func_content, '')
        
        # Добавим функции внутрь блока functions
        functions_to_add = ',\n  ' + ',\n  '.join(functions_to_move)
        new_content = before_functions + functions_to_add + after_functions_clean
        
        # Очистим лишние запятые
        new_content = re.sub(r',\s*,', ',', new_content)
        new_content = re.sub(r',\s*}', '}', new_content)
        
        # Создадим резервную копию
        backup_name = f"data/sfm/function_registry_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(backup_name, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Резервная копия создана: {backup_name}")
        
        # Сохраним исправленный файл
        with open('data/sfm/function_registry.json', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Структура SFM реестра исправлена")
        
        # Проверим результат
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
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    fix_sfm_structure()