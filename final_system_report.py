#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ПОЛНЫЙ ОТЧЕТ О СИСТЕМЕ ALADDIN
"""

import os
import ast
import sys
from collections import defaultdict

def generate_final_report():
    print('🔍 ПОЛНЫЙ ОТЧЕТ О СИСТЕМЕ ALADDIN')
    print('=' * 100)
    
    # Сканируем все Python файлы
    all_py_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                all_py_files.append(os.path.join(root, file))

    print(f'📊 ОБЩАЯ СТАТИСТИКА:')
    print(f'   Всего Python файлов: {len(all_py_files)}')
    print()

    # Анализируем классы и функции
    total_classes = 0
    total_functions = 0
    total_methods = 0
    total_ai_agents = 0
    total_bots = 0
    total_security_components = 0

    class_details = []
    function_details = []

    for file_path in all_py_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Парсим AST
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    total_classes += 1
                    class_name = node.name
                    class_methods = 0
                    
                    # Считаем методы в классе
                    for item in node.body:
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            class_methods += 1
                            total_methods += 1
                    
                    class_details.append({
                        'name': class_name,
                        'file': file_path,
                        'methods': class_methods
                    })
                    
                    # Определяем тип компонента
                    if 'agent' in class_name.lower() or 'ai' in class_name.lower():
                        total_ai_agents += 1
                    elif 'bot' in class_name.lower():
                        total_bots += 1
                    elif 'security' in class_name.lower() or 'protection' in class_name.lower():
                        total_security_components += 1
                        
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Проверяем, что функция не внутри класса
                    is_class_method = False
                    for parent in ast.walk(tree):
                        if isinstance(parent, ast.ClassDef):
                            if node in parent.body:
                                is_class_method = True
                                break
                    
                    if not is_class_method:
                        total_functions += 1
                        function_details.append({
                            'name': node.name,
                            'file': file_path
                        })
                        
        except Exception as e:
            # Пропускаем файлы с ошибками парсинга
            continue

    print(f'📊 СТАТИСТИКА КЛАССОВ И ФУНКЦИЙ:')
    print(f'   Всего классов: {total_classes}')
    print(f'   Всего функций: {total_functions}')
    print(f'   Всего методов: {total_methods}')
    print(f'   AI агентов: {total_ai_agents}')
    print(f'   Ботов: {total_bots}')
    print(f'   Компонентов безопасности: {total_security_components}')
    print(f'   ВСЕГО ДЕЙСТВИЙ: {total_functions + total_methods}')
    print()

    # Показываем топ-10 классов по количеству методов
    print(f'📋 ТОП-10 КЛАССОВ ПО КОЛИЧЕСТВУ МЕТОДОВ:')
    print('-' * 80)
    sorted_classes = sorted(class_details, key=lambda x: x['methods'], reverse=True)
    for i, cls in enumerate(sorted_classes[:10], 1):
        print(f'{i:2d}. {cls["name"]} - {cls["methods"]} методов ({os.path.basename(cls["file"])})')

    # Показываем топ-10 AI агентов
    print(f'\n🤖 ТОП-10 AI АГЕНТОВ:')
    print('-' * 80)
    ai_agents = [cls for cls in class_details if 'agent' in cls['name'].lower() or 'ai' in cls['name'].lower()]
    sorted_ai_agents = sorted(ai_agents, key=lambda x: x['methods'], reverse=True)
    for i, agent in enumerate(sorted_ai_agents[:10], 1):
        print(f'{i:2d}. {agent["name"]} - {agent["methods"]} методов ({os.path.basename(agent["file"])})')

    # Показываем топ-10 ботов
    print(f'\n🤖 ТОП-10 БОТОВ:')
    print('-' * 80)
    bots = [cls for cls in class_details if 'bot' in cls['name'].lower()]
    sorted_bots = sorted(bots, key=lambda x: x['methods'], reverse=True)
    for i, bot in enumerate(sorted_bots[:10], 1):
        print(f'{i:2d}. {bot["name"]} - {bot["methods"]} методов ({os.path.basename(bot["file"])})')

    # Показываем топ-10 компонентов безопасности
    print(f'\n🛡️ ТОП-10 КОМПОНЕНТОВ БЕЗОПАСНОСТИ:')
    print('-' * 80)
    security_components = [cls for cls in class_details if 'security' in cls['name'].lower() or 'protection' in cls['name'].lower()]
    sorted_security = sorted(security_components, key=lambda x: x['methods'], reverse=True)
    for i, comp in enumerate(sorted_security[:10], 1):
        print(f'{i:2d}. {comp["name"]} - {comp["methods"]} методов ({os.path.basename(comp["file"])})')

    print(f'\n📊 ИТОГОВАЯ СТАТИСТИКА:')
    print(f'   Всего Python файлов: {len(all_py_files)}')
    print(f'   Всего классов: {total_classes}')
    print(f'   Всего функций: {total_functions}')
    print(f'   Всего методов: {total_methods}')
    print(f'   AI агентов: {total_ai_agents}')
    print(f'   Ботов: {total_bots}')
    print(f'   Компонентов безопасности: {total_security_components}')
    print(f'   ВСЕГО ДЕЙСТВИЙ: {total_functions + total_methods}')

if __name__ == "__main__":
    generate_final_report()
