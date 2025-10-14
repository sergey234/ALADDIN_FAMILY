#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализ качества LoadBalancer
"""

import ast
import os
import sys

def analyze_load_balancer_quality():
    """Анализ качества LoadBalancer"""
    
    file_path = 'security/microservices/load_balancer.py'
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        # Подсчет метрик
        total_lines = len(content.splitlines())
        comment_lines = 0
        docstring_lines = 0
        function_lines = 0
        class_lines = 0
        
        # Анализ узлов AST
        functions = []
        classes = []
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node)
                function_lines += len(node.body)
                if ast.get_docstring(node):
                    docstring_lines += len(ast.get_docstring(node).splitlines())
            elif isinstance(node, ast.ClassDef):
                classes.append(node)
                class_lines += len(node.body)
                if ast.get_docstring(node):
                    docstring_lines += len(ast.get_docstring(node).splitlines())
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(node)
        
        # Подсчет комментариев
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith('#') and not stripped.startswith('#!/'):
                comment_lines += 1
        
        # Анализ type hints
        type_hint_functions = 0
        for func in functions:
            if func.returns or any(arg.annotation for arg in func.args.args):
                type_hint_functions += 1
        
        # Анализ сложности
        complex_functions = 0
        ml_algorithms = 0
        mathematical_operations = 0
        exception_handlers = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if len(node.body) > 10:  # Сложные функции
                    complex_functions += 1
            if isinstance(node, (ast.Call, ast.Attribute)):
                if any(ml_keyword in ast.dump(node) for ml_keyword in ['fit', 'predict', 'transform', 'score', 'cluster', 'regressor', 'classifier']):
                    ml_algorithms += 1
            if isinstance(node, (ast.BinOp, ast.AugAssign)) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow)):
                mathematical_operations += 1
            if isinstance(node, ast.ExceptHandler):
                exception_handlers += 1
        
        # Расчет оценок
        documentation_score = min(100, (docstring_lines + comment_lines) * 100 / max(total_lines, 1))
        type_hints_score = min(100, type_hint_functions * 100 / max(len(functions), 1))
        complexity_score = min(100, (complex_functions + ml_algorithms + mathematical_operations + exception_handlers) * 100 / max(len(functions), 1))
        structure_score = min(100, (len(classes) * 20 + len(functions) * 2 + len(imports) * 1))
        
        # Общий балл
        total_score = (documentation_score * 0.3 + type_hints_score * 0.2 + complexity_score * 0.3 + structure_score * 0.2)
        
        # Определение оценки
        if total_score >= 90:
            grade = "A+"
        elif total_score >= 80:
            grade = "A"
        elif total_score >= 70:
            grade = "B"
        elif total_score >= 60:
            grade = "C"
        else:
            grade = "D"
        
        return {
            'total_lines': total_lines,
            'comment_lines': comment_lines,
            'docstring_lines': docstring_lines,
            'functions': len(functions),
            'classes': len(classes),
            'imports': len(imports),
            'documentation_score': documentation_score,
            'type_hints_score': type_hints_score,
            'complexity_score': complexity_score,
            'structure_score': structure_score,
            'total_score': total_score,
            'grade': grade,
            'complex_functions': complex_functions,
            'ml_algorithms': ml_algorithms,
            'mathematical_operations': mathematical_operations,
            'exception_handlers': exception_handlers
        }
        
    except Exception as e:
        print(f"Ошибка анализа: {e}")
        return None

if __name__ == "__main__":
    result = analyze_load_balancer_quality()
    if result:
        print("🔍 АНАЛИЗ КАЧЕСТВА LOADBALANCER")
        print("=" * 50)
        print(f"📊 Строки кода: {result['total_lines']}")
        print(f"📝 Комментарии: {result['comment_lines']}")
        print(f"📖 Docstrings: {result['docstring_lines']}")
        print(f"🏗️  Классы: {result['classes']}")
        print(f"⚙️  Функции: {result['functions']}")
        print(f"📦 Импорты: {result['imports']}")
        print()
        print("🎯 ДЕТАЛЬНЫЕ МЕТРИКИ:")
        print(f"  📖 Документация: {result['documentation_score']:.1f}%")
        print(f"  🏷️  Type hints: {result['type_hints_score']:.1f}%")
        print(f"  🧠 Сложность: {result['complexity_score']:.1f}%")
        print(f"  🏗️  Структура: {result['structure_score']:.1f}%")
        print()
        print("🔬 АНАЛИЗ СЛОЖНОСТИ:")
        print(f"  🔄 Сложные функции: {result['complex_functions']}")
        print(f"  🤖 ML алгоритмы: {result['ml_algorithms']}")
        print(f"  🧮 Математические операции: {result['mathematical_operations']}")
        print(f"  ⚠️  Обработка исключений: {result['exception_handlers']}")
        print()
        print(f"🎯 ИТОГОВЫЙ БАЛЛ: {result['total_score']:.1f}%")
        print(f"🏆 КАЧЕСТВО: {result['grade']}")
    else:
        print("❌ Ошибка анализа качества")