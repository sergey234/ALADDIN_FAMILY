#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Правильный подсчет всех компонентов в SFM Registry
"""

import json

def main():
    registry_path = '/opt/aladdin-backend/data/sfm/function_registry.json'
    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    print('=' * 80)
    print('ПРАВИЛЬНЫЙ ПОДСЧЕТ SFM REGISTRY')
    print('=' * 80)
    print('')
    
    # Проверяем структуру
    if 'functions' in registry:
        functions_dict = registry['functions']
        print(f'Найдено функций в словаре: {len(functions_dict)}')
        print('')
        
        # Группируем по типам
        agents = []
        managers = []
        bots = []
        others = []
        
        for function_id, function_data in functions_dict.items():
            func_type = function_data.get('function_type', 'unknown')
            name = function_data.get('name', 'N/A')
            status = function_data.get('status', 'unknown')
            
            if func_type == 'ai_agent':
                agents.append((function_id, name, status))
            elif func_type == 'manager':
                managers.append((function_id, name, status))
            elif func_type == 'bot':
                bots.append((function_id, name, status))
            else:
                others.append((function_id, name, func_type, status))
        
        print('=' * 80)
        print('РАСПРЕДЕЛЕНИЕ ПО ТИПАМ:')
        print('=' * 80)
        print(f'АГЕНТЫ: {len(agents)}')
        print(f'МЕНЕДЖЕРЫ: {len(managers)}')
        print(f'БОТЫ: {len(bots)}')
        if others:
            print(f'ДРУГИЕ: {len(others)}')
        print('')
        
        print('=' * 80)
        print('ДЕТАЛЬНЫЙ СПИСОК АГЕНТОВ:')
        print('=' * 80)
        for i, (func_id, name, status) in enumerate(sorted(agents), 1):
            print(f'{i}. {name} ({func_id}) - {status}')
        print('')
        
        print('=' * 80)
        print('ДЕТАЛЬНЫЙ СПИСОК МЕНЕДЖЕРОВ:')
        print('=' * 80)
        for i, (func_id, name, status) in enumerate(sorted(managers), 1):
            print(f'{i}. {name} ({func_id}) - {status}')
        print('')
        
        print('=' * 80)
        print('ДЕТАЛЬНЫЙ СПИСОК БОТОВ:')
        print('=' * 80)
        for i, (func_id, name, status) in enumerate(sorted(bots), 1):
            print(f'{i}. {name} ({func_id}) - {status}')
        print('')
        
        if others:
            print('=' * 80)
            print('ДРУГИЕ КОМПОНЕНТЫ:')
            print('=' * 80)
            for i, (func_id, name, func_type, status) in enumerate(sorted(others), 1):
                print(f'{i}. {name} ({func_id}) - тип: {func_type}, статус: {status}')
            print('')
        
        print('=' * 80)
        print('ИТОГО В SFM REGISTRY:')
        print('=' * 80)
        print(f'  - Всего компонентов: {len(functions_dict)}')
        print(f'  - Агентов: {len(agents)}')
        print(f'  - Менеджеров: {len(managers)}')
        print(f'  - Ботов: {len(bots)}')
        if others:
            print(f'  - Других: {len(others)}')
        print('')
        
        # Подсчитываем активные
        active_agents = sum(1 for _, _, status in agents if status == 'active')
        active_managers = sum(1 for _, _, status in managers if status == 'active')
        active_bots = sum(1 for _, _, status in bots if status == 'active')
        
        print('=' * 80)
        print('СТАТУСЫ:')
        print('=' * 80)
        print(f'  - Активных агентов: {active_agents} из {len(agents)}')
        print(f'  - Активных менеджеров: {active_managers} из {len(managers)}')
        print(f'  - Активных ботов: {active_bots} из {len(bots)}')
        print('')
        
    else:
        print('Структура registry не содержит ключ "functions"')
        print('Доступные ключи:', list(registry.keys()))

if __name__ == "__main__":
    main()
