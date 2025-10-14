#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для анализа неиспользуемых импортов в LoadBalancer
"""

import re
import ast
import sys
from pathlib import Path

def analyze_imports(file_path):
    """Анализирует импорты в файле"""
    print(f"🔍 АНАЛИЗ ИМПОРТОВ: {file_path}")
    print("=" * 60)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Парсим AST
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        print(f"❌ Ошибка синтаксиса: {e}")
        return
    
    # Собираем все импорты
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            for alias in node.names:
                imports.append(f"{module}.{alias.name}" if module else alias.name)
    
    # Собираем все имена, используемые в коде
    used_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            used_names.add(node.id)
        elif isinstance(node, ast.Attribute):
            used_names.add(node.attr)
    
    # Анализируем каждый импорт
    unused_imports = []
    used_imports = []
    
    for imp in imports:
        # Проверяем, используется ли импорт
        if '.' in imp:
            # Для импортов типа "module.name"
            module, name = imp.split('.', 1)
            if name in used_names or module in used_names:
                used_imports.append(imp)
            else:
                unused_imports.append(imp)
        else:
            # Для простых импортов
            if imp in used_names:
                used_imports.append(imp)
            else:
                unused_imports.append(imp)
    
    # Выводим результаты
    print(f"📊 СТАТИСТИКА:")
    print(f"   • Всего импортов: {len(imports)}")
    print(f"   • Используемых: {len(used_imports)}")
    print(f"   • Неиспользуемых: {len(unused_imports)}")
    print()
    
    if unused_imports:
        print("❌ НЕИСПОЛЬЗУЕМЫЕ ИМПОРТЫ:")
        for imp in sorted(unused_imports):
            print(f"   • {imp}")
        print()
    
    if used_imports:
        print("✅ ИСПОЛЬЗУЕМЫЕ ИМПОРТЫ:")
        for imp in sorted(used_imports):
            print(f"   • {imp}")
        print()
    
    return unused_imports, used_imports

if __name__ == "__main__":
    file_path = "security/microservices/load_balancer.py"
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    
    unused, used = analyze_imports(file_path)
    
    print("🎯 РЕКОМЕНДАЦИИ:")
    if unused:
        print("   1. Удалить неиспользуемые импорты")
        print("   2. Проверить функциональность")
        print("   3. Запустить тесты")
    else:
        print("   ✅ Все импорты используются!")