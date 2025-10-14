#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Продвинутая проверка качества кода для достижения A+ уровня
"""

import sys
import os
import ast
import inspect
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def analyze_code_quality(file_path: str) -> dict:
    """Анализ качества кода файла"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Парсинг AST
        tree = ast.parse(content)
        
        # Подсчет различных элементов
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
        
        # Анализ сложности
        complexity_score = 0
        for func in functions:
            if len(func.body) > 5:  # Функции с достаточной логикой
                complexity_score += 1
        
        # Подсчет импортов
        imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
        
        # Расчет итогового балла
        size_score = min(100, (total_lines / 600) * 100)  # 600 строк = 100%
        docstring_score = (docstring_quality / max(len(functions), 1)) * 100
        type_hint_score = (type_hint_quality / max(len(functions), 1)) * 100
        complexity_score = (complexity_score / max(len(functions), 1)) * 100
        structure_score = min(100, (len(classes) + len(functions)) * 10)  # За структуру
        
        # Итоговый балл
        final_score = (
            size_score * 0.3 +
            docstring_score * 0.25 +
            type_hint_score * 0.2 +
            complexity_score * 0.15 +
            structure_score * 0.1
        )
        
        return {
            'total_lines': total_lines,
            'code_lines': code_lines,
            'comment_lines': comment_lines,
            'docstring_lines': docstring_lines,
            'classes': len(classes),
            'functions': len(functions),
            'methods': len(methods),
            'imports': len(imports),
            'size_score': round(size_score, 1),
            'docstring_score': round(docstring_score, 1),
            'type_hint_score': round(type_hint_score, 1),
            'complexity_score': round(complexity_score, 1),
            'structure_score': round(structure_score, 1),
            'final_score': round(final_score, 1)
        }
        
    except Exception as e:
        return {'error': str(e), 'final_score': 0}

def test_advanced_quality():
    """Продвинутая проверка качества всех новых компонентов"""
    
    components = [
        {
            'name': 'FamilyCommunicationHub',
            'file': 'security/ai_agents/family_communication_hub.py'
        },
        {
            'name': 'EmergencyResponseInterface', 
            'file': 'security/ai_agents/emergency_response_interface.py'
        },
        {
            'name': 'NotificationBot',
            'file': 'security/ai_agents/notification_bot.py'
        },
        {
            'name': 'APIGateway',
            'file': 'security/microservices/api_gateway.py'
        },
        {
            'name': 'LoadBalancer',
            'file': 'security/microservices/load_balancer.py'
        }
    ]
    
    print("🔍 ПРОДВИНУТАЯ ПРОВЕРКА КАЧЕСТВА КОДА")
    print("=" * 70)
    
    total_score = 0
    total_components = len(components)
    
    for component in components:
        print(f"\n📋 {component['name']}:")
        print("-" * 50)
        
        analysis = analyze_code_quality(component['file'])
        
        if 'error' in analysis:
            print(f"  ❌ Ошибка анализа: {analysis['error']}")
            continue
        
        print(f"  📊 Строки кода: {analysis['code_lines']}")
        print(f"  📝 Комментарии: {analysis['comment_lines']}")
        print(f"  📖 Документация: {analysis['docstring_lines']}")
        print(f"  🏗️  Классы: {analysis['classes']}")
        print(f"  ⚙️  Функции: {analysis['functions']}")
        print(f"  🔧 Методы: {analysis['methods']}")
        print(f"  📦 Импорты: {analysis['imports']}")
        print()
        
        print(f"  🎯 Размер: {analysis['size_score']}%")
        print(f"  📖 Документация: {analysis['docstring_score']}%")
        print(f"  🏷️  Type hints: {analysis['type_hint_score']}%")
        print(f"  🧠 Сложность: {analysis['complexity_score']}%")
        print(f"  🏗️  Структура: {analysis['structure_score']}%")
        print()
        
        final_score = analysis['final_score']
        print(f"  🎯 ИТОГОВЫЙ БАЛЛ: {final_score}%")
        
        # Определяем качество
        if final_score >= 95:
            quality = "A+"
            emoji = "🏆"
        elif final_score >= 90:
            quality = "A"
            emoji = "🥇"
        elif final_score >= 85:
            quality = "B+"
            emoji = "🥈"
        elif final_score >= 80:
            quality = "B"
            emoji = "🥉"
        else:
            quality = "C"
            emoji = "⚠️"
        
        print(f"  {emoji} КАЧЕСТВО: {quality}")
        
        total_score += final_score
    
    # Итоговая статистика
    print(f"\n📊 ИТОГОВАЯ СТАТИСТИКА:")
    print("=" * 70)
    average_score = total_score / total_components
    
    print(f"🎯 Средний балл: {average_score:.1f}%")
    print(f"📈 Общий балл: {total_score:.1f}%")
    print(f"🔢 Компонентов: {total_components}")
    
    if average_score >= 95:
        overall_quality = "A+"
        emoji = "🏆"
        message = "ОТЛИЧНОЕ КАЧЕСТВО! A+ ДОСТИГНУТО!"
    elif average_score >= 90:
        overall_quality = "A"
        emoji = "🥇"
        message = "ОЧЕНЬ ХОРОШЕЕ КАЧЕСТВО!"
    elif average_score >= 85:
        overall_quality = "B+"
        emoji = "🥈"
        message = "ХОРОШЕЕ КАЧЕСТВО!"
    elif average_score >= 80:
        overall_quality = "B"
        emoji = "🥉"
        message = "УДОВЛЕТВОРИТЕЛЬНОЕ КАЧЕСТВО!"
    else:
        overall_quality = "C"
        emoji = "⚠️"
        message = "ТРЕБУЕТ УЛУЧШЕНИЯ!"
    
    print(f"{emoji} ОБЩЕЕ КАЧЕСТВО: {overall_quality}")
    print(f"💬 {message}")
    
    return average_score, overall_quality

if __name__ == "__main__":
    score, quality = test_advanced_quality()
    print(f"\n🎉 ПРОВЕРКА ЗАВЕРШЕНА!")
    print(f"📊 Результат: {score:.1f}% ({quality})")