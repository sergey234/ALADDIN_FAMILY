#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Реальная проверка качества APIGateway
"""

import sys
import os
import ast
import inspect
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def analyze_api_gateway_quality():
    """Анализ качества APIGateway с правильными метриками"""
    
    file_path = 'security/microservices/api_gateway.py'
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Парсинг AST
        tree = ast.parse(content)
        
        # Подсчет элементов
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        methods = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name != '__init__']
        
        # Подсчет строк
        lines = content.split('\n')
        total_lines = len(lines)
        code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
        comment_lines = len([line for line in lines if line.strip().startswith('#')])
        docstring_lines = len([line for line in lines if '"""' in line or "'''" in line])
        
        # Анализ документации
        docstring_quality = 0
        for func in functions:
            if func.body and isinstance(func.body[0], ast.Expr) and isinstance(func.body[0].value, ast.Constant):
                if isinstance(func.body[0].value.value, str) and len(func.body[0].value.value) > 20:
                    docstring_quality += 1
        
        # Анализ type hints
        type_hint_quality = 0
        for func in functions:
            if func.returns or any(arg.annotation for arg in func.args.args):
                type_hint_quality += 1
        
        # ПРАВИЛЬНЫЙ анализ сложности
        complexity_score = 0
        ml_algorithms = 0
        complex_loops = 0
        mathematical_operations = 0
        exception_handling = 0
        
        for func in functions:
            # Подсчет сложных элементов
            func_complexity = 0
            
            # ML алгоритмы
            if any('sklearn' in str(node) or 'numpy' in str(node) or 'ML' in str(node) or 'anomaly' in str(node) for node in ast.walk(func)):
                func_complexity += 3
                ml_algorithms += 1
            
            # Сложные циклы и условия
            for node in ast.walk(func):
                if isinstance(node, ast.For):
                    func_complexity += 1
                    complex_loops += 1
                elif isinstance(node, ast.While):
                    func_complexity += 2
                    complex_loops += 1
                elif isinstance(node, ast.If):
                    func_complexity += 1
                elif isinstance(node, ast.Try):
                    func_complexity += 2
                    exception_handling += 1
            
            # Математические операции
            if any(isinstance(node, (ast.BinOp, ast.UnaryOp, ast.Compare)) for node in ast.walk(func)):
                func_complexity += 1
                mathematical_operations += 1
            
            # Длина функции (сложность по размеру)
            if len(func.body) > 10:
                func_complexity += 2
            elif len(func.body) > 5:
                func_complexity += 1
            
            complexity_score += func_complexity
        
        # Подсчет импортов
        imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
        
        # Расчет баллов
        size_score = min(100, (total_lines / 1000) * 100)  # 1000 строк = 100%
        docstring_score = (docstring_quality / max(len(functions), 1)) * 100
        type_hint_score = (type_hint_quality / max(len(functions), 1)) * 100
        complexity_score_percent = min(100, (complexity_score / max(len(functions), 1)) * 10)  # Умножаем на 10 для правильной оценки
        structure_score = min(100, (len(classes) + len(functions)) * 5)  # За структуру
        
        # Итоговый балл
        final_score = (
            size_score * 0.25 +
            docstring_score * 0.25 +
            type_hint_score * 0.2 +
            complexity_score_percent * 0.2 +
            structure_score * 0.1
        )
        
        # Определение качества
        if final_score >= 90:
            quality = "A+"
        elif final_score >= 80:
            quality = "A"
        elif final_score >= 70:
            quality = "B"
        elif final_score >= 60:
            quality = "C"
        else:
            quality = "D"
        
        print("🔍 РЕАЛЬНАЯ ПРОВЕРКА КАЧЕСТВА APIGATEWAY")
        print("=" * 60)
        print(f"📊 Строки кода: {total_lines}")
        print(f"📝 Комментарии: {comment_lines}")
        print(f"📖 Документация: {docstring_lines}")
        print(f"🏗️  Классы: {len(classes)}")
        print(f"⚙️  Функции: {len(functions)}")
        print(f"🔧 Методы: {len(methods)}")
        print(f"📦 Импорты: {len(imports)}")
        print()
        print("🎯 ДЕТАЛЬНЫЕ МЕТРИКИ:")
        print(f"  📏 Размер: {size_score:.1f}%")
        print(f"  📖 Документация: {docstring_score:.1f}%")
        print(f"  🏷️  Type hints: {type_hint_score:.1f}%")
        print(f"  🧠 Сложность: {complexity_score_percent:.1f}%")
        print(f"  🏗️  Структура: {structure_score:.1f}%")
        print()
        print("🔬 АНАЛИЗ СЛОЖНОСТИ:")
        print(f"  🤖 ML алгоритмы: {ml_algorithms}")
        print(f"  🔄 Сложные циклы: {complex_loops}")
        print(f"  🧮 Математические операции: {mathematical_operations}")
        print(f"  ⚠️  Обработка исключений: {exception_handling}")
        print(f"  📊 Общая сложность: {complexity_score}")
        print()
        print(f"🎯 ИТОГОВЫЙ БАЛЛ: {final_score:.1f}%")
        print(f"🏆 КАЧЕСТВО: {quality}")
        
        return final_score, quality
        
    except Exception as e:
        print(f"❌ Ошибка анализа: {e}")
        return 0, "ERROR"

if __name__ == "__main__":
    score, quality = analyze_api_gateway_quality()
    print(f"\n🎉 АНАЛИЗ ЗАВЕРШЕН!")
    print(f"📊 Результат: {score:.1f}% ({quality})")