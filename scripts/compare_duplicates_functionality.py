#!/usr/bin/env python3
"""
Скрипт для сравнения функциональности дубликатов с оригиналами
"""

import os
import ast
from pathlib import Path
import re

def analyze_file_functionality(file_path):
    """Анализирует функциональность файла"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Подсчет строк
        lines = content.split('\n')
        total_lines = len(lines)
        code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
        comment_lines = len([line for line in lines if line.strip().startswith('#')])
        empty_lines = len([line for line in lines if not line.strip()])
        
        # Анализ AST
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return {
                'total_lines': total_lines,
                'code_lines': code_lines,
                'comment_lines': comment_lines,
                'empty_lines': empty_lines,
                'classes': 0,
                'functions': 0,
                'imports': 0,
                'syntax_error': True
            }
        
        # Подсчет классов
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        
        # Подсчет функций
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        
        # Подсчет импортов
        imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
        
        # Размер файла
        file_size = os.path.getsize(file_path)
        
        return {
            'total_lines': total_lines,
            'code_lines': code_lines,
            'comment_lines': comment_lines,
            'empty_lines': empty_lines,
            'classes': len(classes),
            'functions': len(functions),
            'imports': len(imports),
            'file_size': file_size,
            'syntax_error': False,
            'class_names': [cls.name for cls in classes],
            'function_names': [func.name for func in functions]
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'total_lines': 0,
            'code_lines': 0,
            'comment_lines': 0,
            'empty_lines': 0,
            'classes': 0,
            'functions': 0,
            'imports': 0,
            'file_size': 0,
            'syntax_error': True
        }

def compare_duplicates():
    """Сравнивает дубликаты с оригиналами"""
    
    # Определяем файлы для сравнения
    files_to_compare = [
        {
            'name': 'SECURITY_MONITORING',
            'original': 'security/security_monitoring.py',
            'duplicates': [
                'security/security_monitoring_backup.py',
                'security/security_monitoring_ultimate_a_plus.py.backup_20250927_031440'
            ]
        },
        {
            'name': 'SAFE_FUNCTION_MANAGER',
            'original': 'security/safe_function_manager.py',
            'duplicates': [
                'security/safe_function_manager.py.backup',
                'security/safe_function_manager.py.backup_20250928_195531',
                'security/safe_function_manager_backup_20250909_021153.py'
            ]
        }
    ]
    
    print("🔍 СРАВНЕНИЕ ФУНКЦИОНАЛЬНОСТИ ДУБЛИКАТОВ С ОРИГИНАЛАМИ")
    print("=" * 80)
    
    for group in files_to_compare:
        print(f"\n📁 {group['name']}")
        print("=" * 60)
        
        # Анализируем оригинал
        original_path = group['original']
        if os.path.exists(original_path):
            original_data = analyze_file_functionality(original_path)
            print(f"\n✅ ОРИГИНАЛ: {os.path.basename(original_path)}")
            print(f"   📊 Строк кода: {original_data['code_lines']:,}")
            print(f"   �� Всего строк: {original_data['total_lines']:,}")
            print(f"   💬 Комментарии: {original_data['comment_lines']:,}")
            print(f"   �� Классов: {original_data['classes']}")
            print(f"   🔧 Функций: {original_data['functions']}")
            print(f"   📥 Импортов: {original_data['imports']}")
            print(f"   💾 Размер: {original_data['file_size']:,} байт")
            
            if original_data.get('syntax_error'):
                print(f"   ❌ Синтаксическая ошибка!")
        else:
            print(f"\n❌ ОРИГИНАЛ НЕ НАЙДЕН: {original_path}")
            continue
        
        # Анализируем дубликаты
        print(f"\n📋 ДУБЛИКАТЫ:")
        for i, dup_path in enumerate(group['duplicates'], 1):
            if os.path.exists(dup_path):
                dup_data = analyze_file_functionality(dup_path)
                print(f"\n   {i}. {os.path.basename(dup_path)}")
                print(f"      📊 Строк кода: {dup_data['code_lines']:,}")
                print(f"      📝 Всего строк: {dup_data['total_lines']:,}")
                print(f"      💬 Комментарии: {dup_data['comment_lines']:,}")
                print(f"      📦 Классов: {dup_data['classes']}")
                print(f"      🔧 Функций: {dup_data['functions']}")
                print(f"      📥 Импортов: {dup_data['imports']}")
                print(f"      💾 Размер: {dup_data['file_size']:,} байт")
                
                if dup_data.get('syntax_error'):
                    print(f"      ❌ Синтаксическая ошибка!")
                
                # Сравнение с оригиналом
                if not original_data.get('syntax_error') and not dup_data.get('syntax_error'):
                    code_diff = dup_data['code_lines'] - original_data['code_lines']
                    size_diff = dup_data['file_size'] - original_data['file_size']
                    func_diff = dup_data['functions'] - original_data['functions']
                    class_diff = dup_data['classes'] - original_data['classes']
                    
                    print(f"      📈 Разница с оригиналом:")
                    print(f"         • Строк кода: {code_diff:+d}")
                    print(f"         • Размер: {size_diff:+,d} байт")
                    print(f"         • Функций: {func_diff:+d}")
                    print(f"         • Классов: {class_diff:+d}")
                    
                    # Определяем тип дубликата
                    if abs(code_diff) < 10 and abs(func_diff) < 2:
                        print(f"      ✅ ИДЕНТИЧНЫЙ (незначительные различия)")
                    elif code_diff < -50 or func_diff < -5:
                        print(f"      ⚠️  УПРОЩЕННАЯ ВЕРСИЯ")
                    elif code_diff > 50 or func_diff > 5:
                        print(f"      🔄 РАСШИРЕННАЯ ВЕРСИЯ")
                    else:
                        print(f"      �� МОДИФИЦИРОВАННАЯ ВЕРСИЯ")
            else:
                print(f"\n   {i}. ❌ ФАЙЛ НЕ НАЙДЕН: {os.path.basename(dup_path)}")

if __name__ == "__main__":
    compare_duplicates()
