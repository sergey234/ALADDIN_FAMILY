#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой анализ функций password_security_agent.py
"""

import ast
import sys
sys.path.append('.')

def analyze_functions():
    # Читаем файл
    with open('security/ai_agents/password_security_agent.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Парсим AST
    tree = ast.parse(content)

    print('🔍 АНАЛИЗ ФУНКЦИЙ (НЕ КЛАССОВ)')
    print('=' * 50)

    # Находим все функции
    all_functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            all_functions.append(node)

    print(f'Всего функций в файле: {len(all_functions)}')
    
    # Функции на верхнем уровне (не в классах)
    top_level_functions = []
    for func in all_functions:
        # Проверяем, находится ли функция в классе
        in_class = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if func in node.body:
                    in_class = True
                    break
        
        if not in_class:
            top_level_functions.append(func)

    if top_level_functions:
        print(f'\\nФункций на верхнем уровне: {len(top_level_functions)}')
        for func in top_level_functions:
            args = [arg.arg for arg in func.args.args]
            has_docstring = ast.get_docstring(func) is not None
            doc_str = '📝' if has_docstring else '❌'
            args_str = f'({", ".join(args)})' if args else '()'
            print(f'  • {func.name}{args_str} {doc_str}')
    else:
        print('\\nФункций на верхнем уровне не найдено')

    print(f'\\n📊 ВСЕ ФУНКЦИИ В ФАЙЛЕ:')
    for i, func in enumerate(all_functions[:15]):  # Показываем первые 15
        args = [arg.arg for arg in func.args.args]
        has_docstring = ast.get_docstring(func) is not None
        doc_str = '📝' if has_docstring else '❌'
        args_str = f'({", ".join(args)})' if args else '()'
        print(f'  {i+1:2d}. {func.name}{args_str} {doc_str}')
    
    if len(all_functions) > 15:
        print(f'  ... и еще {len(all_functions) - 15} функций')

if __name__ == '__main__':
    analyze_functions()