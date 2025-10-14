#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализ методов классов password_security_agent.py
"""

import ast
import sys
sys.path.append('.')

def analyze_methods():
    # Читаем файл
    with open('security/ai_agents/password_security_agent.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Парсим AST
    tree = ast.parse(content)

    print('🔍 АНАЛИЗ МЕТОДОВ КЛАССОВ')
    print('=' * 60)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            print(f'\n🏗️ КЛАСС: {node.name}')
            
            methods = []
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    method_name = item.name
                    is_private = method_name.startswith('_')
                    is_dunder = method_name.startswith('__') and method_name.endswith('__')
                    
                    # Определяем тип метода
                    if is_dunder:
                        method_type = 'special'
                    elif is_private:
                        method_type = 'private'
                    else:
                        method_type = 'public'
                    
                    # Проверяем декораторы
                    decorators = []
                    for decorator in item.decorator_list:
                        if isinstance(decorator, ast.Name):
                            decorators.append(decorator.id)
                        elif isinstance(decorator, ast.Attribute):
                            decorators.append(decorator.attr)
                    
                    # Аргументы
                    args = [arg.arg for arg in item.args.args]
                    if 'self' in args:
                        args.remove('self')
                    
                    methods.append({
                        'name': method_name,
                        'type': method_type,
                        'decorators': decorators,
                        'args': args,
                        'line': item.lineno,
                        'has_docstring': ast.get_docstring(item) is not None
                    })
            
            # Сортируем методы по типу
            public_methods = [m for m in methods if m['type'] == 'public']
            private_methods = [m for m in methods if m['type'] == 'private']
            special_methods = [m for m in methods if m['type'] == 'special']
            
            print(f'   📊 Всего методов: {len(methods)}')
            print(f'   🔓 Public: {len(public_methods)}')
            print(f'   🔒 Private: {len(private_methods)}')
            print(f'   ⚡ Special: {len(special_methods)}')
            
            if public_methods:
                print(f'   \n   🔓 PUBLIC МЕТОДЫ:')
                for method in public_methods[:5]:  # Показываем первые 5
                    decorators_str = f' @{", ".join(method["decorators"])}' if method['decorators'] else ''
                    args_str = f'({", ".join(method["args"])})' if method['args'] else '()'
                    doc_str = '📝' if method['has_docstring'] else '❌'
                    print(f'     • {method["name"]}{args_str}{decorators_str} {doc_str}')
            
            if special_methods:
                print(f'   \n   ⚡ SPECIAL МЕТОДЫ:')
                for method in special_methods:
                    decorators_str = f' @{", ".join(method["decorators"])}' if method['decorators'] else ''
                    args_str = f'({", ".join(method["args"])})' if method['args'] else '()'
                    doc_str = '📝' if method['has_docstring'] else '❌'
                    print(f'     • {method["name"]}{args_str}{decorators_str} {doc_str}')

if __name__ == '__main__':
    analyze_methods()