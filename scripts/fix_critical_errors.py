#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление критических ошибок для достижения A+ качества
Автоматическое исправление E999, F821 и других критических ошибок

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-11
"""

import os
import sys
import re
import ast
from datetime import datetime

# Добавляем путь к проекту
sys.path.insert(0, '/Users/sergejhlystov/ALADDIN_NEW')

def create_backup():
    """Создает резервную копию перед исправлениями"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"/Users/sergejhlystov/ALADDIN_NEW_BACKUP_CRITICAL_FIXES_{timestamp}"
    
    print(f"🔄 Создаем резервную копию в {backup_dir}...")
    
    try:
        import shutil
        shutil.copytree(
            "/Users/sergejhlystov/ALADDIN_NEW",
            backup_dir,
            ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.git', '*.log')
        )
        print(f"✅ Резервная копия создана: {backup_dir}")
        return backup_dir
    except Exception as e:
        print(f"❌ Ошибка создания резервной копии: {e}")
        return None

def fix_undefined_imports(file_path):
    """Исправляет неопределенные импорты"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Добавляем недостающие импорты
        imports_to_add = []
        
        # Проверяем какие импорты нужны
        if 'np.' in content and 'import numpy' not in content:
            imports_to_add.append('import numpy as np')
        
        if 'pd.' in content and 'import pandas' not in content:
            imports_to_add.append('import pandas as pd')
        
        if 'datetime.' in content and 'from datetime import datetime' not in content:
            imports_to_add.append('from datetime import datetime')
        
        if 'Dict[' in content and 'from typing import Dict' not in content:
            imports_to_add.append('from typing import Dict, Any')
        
        if 'Any' in content and 'from typing import Any' not in content:
            imports_to_add.append('from typing import Any')
        
        if 'os.' in content and 'import os' not in content:
            imports_to_add.append('import os')
        
        if 'threading.' in content and 'import threading' not in content:
            imports_to_add.append('import threading')
        
        if 'time.' in content and 'import time' not in content:
            imports_to_add.append('import time')
        
        if 'SecurityBase' in content and 'from security.base import SecurityBase' not in content:
            imports_to_add.append('from security.base import SecurityBase')
        
        if 'ComponentStatus' in content and 'from security.base import ComponentStatus' not in content:
            imports_to_add.append('from security.base import ComponentStatus')
        
        # Добавляем импорты в начало файла
        if imports_to_add:
            lines = content.split('\n')
            # Находим место для вставки импортов
            insert_index = 0
            for i, line in enumerate(lines):
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    insert_index = i + 1
                elif line.strip() and not line.strip().startswith('#'):
                    break
            
            # Вставляем импорты
            for imp in reversed(imports_to_add):
                lines.insert(insert_index, imp)
            
            content = '\n'.join(lines)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return len(imports_to_add)
        
        return 0
        
    except Exception as e:
        print(f"   ❌ Ошибка исправления импортов {file_path}: {e}")
        return 0

def fix_indentation_errors(file_path):
    """Исправляет ошибки отступов"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Исправляем основные проблемы с отступами
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # Исправляем неожиданные отступы в начале файла
            if i == 0 and line.startswith('    '):
                fixed_lines.append(line.lstrip())
            # Исправляем пустые строки с отступами
            elif line.strip() == '' and i > 0 and lines[i-1].strip() != '':
                fixed_lines.append('')
            # Исправляем строки с неправильными отступами
            elif line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                # Проверяем контекст
                if i > 0 and lines[i-1].strip().endswith(':'):
                    fixed_lines.append('    ' + line)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        content = '\n'.join(fixed_lines)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return 1
        
        return 0
        
    except Exception as e:
        print(f"   ❌ Ошибка исправления отступов {file_path}: {e}")
        return 0

def fix_syntax_errors(file_path):
    """Исправляет синтаксические ошибки"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Исправляем основные синтаксические ошибки
        # EOL while scanning string literal
        content = re.sub(r'""".*?""".*?""".*?"""', '"""Docstring"""', content, flags=re.DOTALL)
        
        # Исправляем неожиданный EOF
        if content.strip().endswith('else:'):
            content += '\n    pass'
        
        # Исправляем неожиданные отступы
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Убираем лишние отступы в начале файла
            if line.startswith('    ') and not any(c.isalpha() for c in line[:4]):
                fixed_lines.append(line.lstrip())
            else:
                fixed_lines.append(line)
        
        content = '\n'.join(fixed_lines)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return 1
        
        return 0
        
    except Exception as e:
        print(f"   ❌ Ошибка исправления синтаксиса {file_path}: {e}")
        return 0

def process_file(file_path):
    """Обрабатывает один файл"""
    filename = os.path.basename(file_path)
    print(f"   🔧 Обрабатываем: {filename}")
    
    # Исправляем неопределенные импорты
    imports_fixed = fix_undefined_imports(file_path)
    
    # Исправляем ошибки отступов
    indentation_fixed = fix_indentation_errors(file_path)
    
    # Исправляем синтаксические ошибки
    syntax_fixed = fix_syntax_errors(file_path)
    
    total_fixed = imports_fixed + indentation_fixed + syntax_fixed
    
    if total_fixed > 0:
        print(f"      ✅ Исправлено: {total_fixed} проблем")
        print(f"         - Импорты: {imports_fixed}")
        print(f"         - Отступы: {indentation_fixed}")
        print(f"         - Синтаксис: {syntax_fixed}")
    else:
        print(f"      ℹ️ Изменений не требуется")
    
    return total_fixed

def find_problem_files():
    """Находит файлы с проблемами"""
    print("\n🔍 ПОИСК ФАЙЛОВ С ПРОБЛЕМАМИ")
    print("-" * 50)
    
    problem_files = []
    
    # Основные директории для проверки
    main_directories = [
        "security/managers",
        "security/ai_agents", 
        "security/bots",
        "security/microservices",
        "security/privacy",
        "security"
    ]
    
    for directory in main_directories:
        dir_path = f"/Users/sergejhlystov/ALADDIN_NEW/{directory}"
        if os.path.exists(dir_path):
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    if file.endswith('.py') and not file.startswith('__'):
                        file_path = os.path.join(root, file)
                        problem_files.append(file_path)
                        print(f"   📄 {os.path.relpath(file_path, '/Users/sergejhlystov/ALADDIN_NEW')}")
    
    print(f"\n📊 Найдено файлов для обработки: {len(problem_files)}")
    return problem_files

def test_after_fixes():
    """Тестирует систему после исправлений"""
    print("\n🧪 ТЕСТИРОВАНИЕ ПОСЛЕ ИСПРАВЛЕНИЙ")
    print("-" * 50)
    
    # Тестируем импорты основных модулей
    test_modules = [
        "security.managers.analytics_manager",
        "security.ai_agents.behavioral_analysis_agent",
        "security.bots.notification_bot",
        "security.microservices.api_gateway",
        "core.singleton",
        "security.safe_function_manager"
    ]
    
    success_count = 0
    
    for module_name in test_modules:
        try:
            __import__(module_name)
            print(f"   ✅ {module_name} - импорт успешен")
            success_count += 1
        except Exception as e:
            print(f"   ❌ {module_name} - ошибка импорта: {e}")
    
    print(f"\n📊 Успешно импортировано: {success_count}/{len(test_modules)}")
    return success_count == len(test_modules)

def run_quality_check():
    """Запускает проверку качества после исправлений"""
    print("\n🔍 ПРОВЕРКА КАЧЕСТВА ПОСЛЕ ИСПРАВЛЕНИЙ")
    print("-" * 50)
    
    try:
        import subprocess
        result = subprocess.run(
            ['python3', 'scripts/quality_check_all.py'],
            cwd='/Users/sergejhlystov/ALADDIN_NEW',
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Проверка качества прошла успешно")
            return True
        else:
            print(f"⚠️ Ошибки в проверке качества: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка запуска проверки качества: {e}")
        return False

def main():
    """Основная функция исправления критических ошибок"""
    print("🔧 ИСПРАВЛЕНИЕ КРИТИЧЕСКИХ ОШИБОК ДЛЯ A+ КАЧЕСТВА")
    print("=" * 70)
    
    # 1. Создаем резервную копию
    backup_dir = create_backup()
    if not backup_dir:
        print("❌ Не удалось создать резервную копию. Прерываем.")
        return False
    
    # 2. Находим файлы с проблемами
    problem_files = find_problem_files()
    
    # 3. Обрабатываем файлы
    total_fixed = 0
    processed_count = 0
    
    for file_path in problem_files:
        fixed = process_file(file_path)
        total_fixed += fixed
        processed_count += 1
    
    # 4. Тестируем после исправлений
    test_success = test_after_fixes()
    
    # 5. Проверяем качество
    quality_success = run_quality_check()
    
    # Итоговый отчет
    print("\n" + "=" * 70)
    print("📊 ИТОГОВЫЙ ОТЧЕТ ИСПРАВЛЕНИЯ КРИТИЧЕСКИХ ОШИБОК:")
    print("=" * 70)
    print(f"✅ Файлов обработано: {processed_count}")
    print(f"✅ Проблем исправлено: {total_fixed}")
    print(f"✅ Тестирование: {'УСПЕШНО' if test_success else 'ОШИБКИ'}")
    print(f"✅ Проверка качества: {'УСПЕШНО' if quality_success else 'ОШИБКИ'}")
    print(f"💾 Резервная копия: {backup_dir}")
    
    if test_success and quality_success:
        print("\n🎉 КРИТИЧЕСКИЕ ОШИБКИ ИСПРАВЛЕНЫ!")
        print("✅ Система готова к дальнейшей оптимизации")
        print("📊 Ожидаемое улучшение качества: +10.0 баллов")
    else:
        print("\n⚠️ ОБНАРУЖЕНЫ ОШИБКИ ПОСЛЕ ИСПРАВЛЕНИЙ")
        print("🔄 Рекомендуется продолжить исправления")
    
    return test_success and quality_success

if __name__ == "__main__":
    main()