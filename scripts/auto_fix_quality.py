#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Автоматическое исправление основных проблем качества кода
"""

import os
import sys
import subprocess
from datetime import datetime

def fix_imports():
    """Исправление импортов"""
    print("🔧 ИСПРАВЛЕНИЕ ИМПОРТОВ")
    print("-" * 50)
    
    # Файлы с проблемами импортов
    files_to_fix = [
        "security/authentication.py",
        "security/access_control.py", 
        "security/security_monitoring.py",
        "security/safe_function_manager.py",
        "security/family/child_protection.py",
        "security/ai_agents/monitor_manager.py",
        "security/bots/notification_bot.py",
        "security/microservices/api_gateway.py"
    ]
    
    for file_path in files_to_fix:
        full_path = os.path.join("/Users/sergejhlystov/ALADDIN_NEW", file_path)
        if os.path.exists(full_path):
            print(f"📄 Исправляем: {file_path}")
            
            try:
                # Удаляем неиспользуемые импорты
                result = subprocess.run([
                    'python3', '-m', 'autoflake', 
                    '--in-place', 
                    '--remove-all-unused-imports',
                    '--remove-unused-variables',
                    full_path
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    print(f"   ✅ Импорты исправлены")
                else:
                    print(f"   ⚠️  Предупреждения: {result.stderr}")
                    
            except Exception as e:
                print(f"   ❌ Ошибка: {str(e)}")
        else:
            print(f"❌ Файл не найден: {file_path}")

def fix_formatting():
    """Исправление форматирования"""
    print("\n🔧 ИСПРАВЛЕНИЕ ФОРМАТИРОВАНИЯ")
    print("-" * 50)
    
    files_to_fix = [
        "security/authentication.py",
        "security/access_control.py", 
        "security/security_monitoring.py",
        "security/safe_function_manager.py",
        "security/family/child_protection.py",
        "security/ai_agents/monitor_manager.py",
        "security/bots/notification_bot.py",
        "security/microservices/api_gateway.py"
    ]
    
    for file_path in files_to_fix:
        full_path = os.path.join("/Users/sergejhlystov/ALADDIN_NEW", file_path)
        if os.path.exists(full_path):
            print(f"📄 Форматируем: {file_path}")
            
            try:
                # Исправляем форматирование
                result = subprocess.run([
                    'python3', '-m', 'autopep8', 
                    '--in-place',
                    '--aggressive',
                    '--aggressive',
                    '--max-line-length=120',
                    full_path
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    print(f"   ✅ Форматирование исправлено")
                else:
                    print(f"   ⚠️  Предупреждения: {result.stderr}")
                    
            except Exception as e:
                print(f"   ❌ Ошибка: {str(e)}")
        else:
            print(f"❌ Файл не найден: {file_path}")

def add_missing_imports():
    """Добавление недостающих импортов"""
    print("\n🔧 ДОБАВЛЕНИЕ НЕДОСТАЮЩИХ ИМПОРТОВ")
    print("-" * 50)
    
    # Исправления для конкретных файлов
    fixes = {
        "security/authentication.py": [
            ("import os", "import os\n")
        ],
        "security/access_control.py": [
            ("import os", "import os\n")
        ],
        "security/security_monitoring.py": [
            ("import time", "import time\n"),
            ("import threading", "import threading\n"),
            ("from core.base import ComponentStatus", "from core.base import ComponentStatus\n")
        ]
    }
    
    for file_path, imports in fixes.items():
        full_path = os.path.join("/Users/sergejhlystov/ALADDIN_NEW", file_path)
        if os.path.exists(full_path):
            print(f"📄 Добавляем импорты в: {file_path}")
            
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Добавляем импорты в начало файла
                for import_line, replacement in imports:
                    if import_line not in content:
                        # Находим место для вставки импорта
                        lines = content.split('\n')
                        insert_index = 0
                        
                        # Ищем последний импорт
                        for i, line in enumerate(lines):
                            if line.strip().startswith('import ') or line.strip().startswith('from '):
                                insert_index = i + 1
                        
                        # Вставляем импорт
                        lines.insert(insert_index, import_line)
                        content = '\n'.join(lines)
                        
                        print(f"   ✅ Добавлен: {import_line}")
                
                # Сохраняем файл
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
            except Exception as e:
                print(f"   ❌ Ошибка: {str(e)}")
        else:
            print(f"❌ Файл не найден: {file_path}")

def check_quality_after_fix():
    """Проверка качества после исправлений"""
    print("\n🔍 ПРОВЕРКА КАЧЕСТВА ПОСЛЕ ИСПРАВЛЕНИЙ")
    print("-" * 50)
    
    files_to_check = [
        "security/authentication.py",
        "security/access_control.py", 
        "security/security_monitoring.py",
        "security/safe_function_manager.py",
        "security/family/child_protection.py",
        "security/ai_agents/monitor_manager.py",
        "security/bots/notification_bot.py",
        "security/microservices/api_gateway.py"
    ]
    
    total_issues = 0
    
    for file_path in files_to_check:
        full_path = os.path.join("/Users/sergejhlystov/ALADDIN_NEW", file_path)
        if os.path.exists(full_path):
            print(f"📄 Проверяем: {file_path}")
            
            try:
                result = subprocess.run([
                    'python3', '-m', 'flake8', 
                    '--max-line-length=120',
                    full_path
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    print(f"   ✅ Качество: A+ (0 проблем)")
                else:
                    output = result.stdout
                    lines = output.split('\n')
                    file_issues = len([l for l in lines if l.strip()])
                    total_issues += file_issues
                    
                    if file_issues <= 5:
                        grade = "A"
                    elif file_issues <= 15:
                        grade = "B"
                    elif file_issues <= 30:
                        grade = "C"
                    else:
                        grade = "D"
                    
                    print(f"   📊 Качество: {grade} ({file_issues} проблем)")
                    
                    # Показываем первые 3 проблемы
                    for i, line in enumerate(lines[:3]):
                        if line.strip():
                            print(f"   ⚠️  {line}")
                    if len(lines) > 3:
                        print(f"   ... и еще {len(lines) - 3} проблем")
                        
            except Exception as e:
                print(f"   ❌ Ошибка проверки: {str(e)}")
        else:
            print(f"❌ Файл не найден: {file_path}")
    
    print(f"\n📊 Общее количество проблем после исправлений: {total_issues}")
    
    if total_issues < 100:
        print("🎉 Отличный результат! Качество значительно улучшено!")
    elif total_issues < 300:
        print("✅ Хороший результат! Качество улучшено.")
    else:
        print("⚠️  Требуется дополнительная работа по улучшению качества.")

def main():
    """Основная функция"""
    print("🚀 АВТОМАТИЧЕСКОЕ ИСПРАВЛЕНИЕ КАЧЕСТВА КОДА")
    print("=" * 60)
    print(f"📅 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Проверяем наличие необходимых инструментов
    try:
        subprocess.run(['python3', '-m', 'autoflake', '--version'], 
                      capture_output=True, check=True)
        subprocess.run(['python3', '-m', 'autopep8', '--version'], 
                      capture_output=True, check=True)
    except subprocess.CalledProcessError:
        print("❌ Необходимые инструменты не установлены!")
        print("Установите: pip3 install autoflake autopep8")
        return
    
    # Выполняем исправления
    fix_imports()
    add_missing_imports()
    fix_formatting()
    check_quality_after_fix()
    
    print()
    print("=" * 60)
    print("✅ АВТОМАТИЧЕСКОЕ ИСПРАВЛЕНИЕ ЗАВЕРШЕНО!")
    print("=" * 60)
    print()
    print("💡 РЕКОМЕНДАЦИИ:")
    print("1. Проверьте результат: python3 -m flake8 --max-line-length=120 security/")
    print("2. При необходимости выполните ручные исправления")
    print("3. Запустите тесты для проверки функциональности")
    print("4. Проведите code review")

if __name__ == "__main__":
    main()