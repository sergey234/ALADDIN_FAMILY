#!/usr/bin/env python3
"""
Проверка ошибок разными анализаторами
"""

import subprocess
import sys
from pathlib import Path

def check_with_different_linters():
    """Проверка с разными линтерами"""
    test_file = "security/ai_agents/family_communication_hub_children_protection_expansion.py"
    
    print("🔍 ПРОВЕРКА ОШИБОК РАЗНЫМИ АНАЛИЗАТОРАМИ")
    print("=" * 60)
    
    # 1. Flake8 с разными настройками
    print("\n1️⃣ FLAKE8 - БАЗОВЫЕ НАСТРОЙКИ:")
    try:
        result = subprocess.run([
            "python3", "-m", "flake8", test_file
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Ошибок не найдено")
        else:
            print(f"❌ Найдено ошибок: {len(result.stdout.splitlines())}")
            print("Первые 3 ошибки:")
            for line in result.stdout.splitlines()[:3]:
                print(f"  • {line}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # 2. Flake8 с настройками 120 символов
    print("\n2️⃣ FLAKE8 - 120 СИМВОЛОВ:")
    try:
        result = subprocess.run([
            "python3", "-m", "flake8", "--max-line-length=120", test_file
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Ошибок не найдено")
        else:
            print(f"❌ Найдено ошибок: {len(result.stdout.splitlines())}")
            print("Первые 3 ошибки:")
            for line in result.stdout.splitlines()[:3]:
                print(f"  • {line}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # 3. Pylint
    print("\n3️⃣ PYLINT:")
    try:
        result = subprocess.run([
            "python3", "-m", "pylint", "--disable=import-error", test_file
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Ошибок не найдено")
        else:
            lines = result.stdout.splitlines()
            error_lines = [line for line in lines if ':' in line and any(x in line for x in ['E', 'W', 'C', 'R'])]
            print(f"❌ Найдено ошибок: {len(error_lines)}")
            print("Первые 3 ошибки:")
            for line in error_lines[:3]:
                print(f"  • {line}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # 4. Black (проверка форматирования)
    print("\n4️⃣ BLACK - ПРОВЕРКА ФОРМАТИРОВАНИЯ:")
    try:
        result = subprocess.run([
            "python3", "-m", "black", "--check", test_file
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Файл отформатирован правильно")
        else:
            print("❌ Файл нуждается в форматировании")
            print("Black предлагает изменения:")
            print(result.stdout)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # 5. Autopep8 (проверка)
    print("\n5️⃣ AUTOPEP8 - ПРОВЕРКА:")
    try:
        result = subprocess.run([
            "python3", "-m", "autopep8", "--diff", test_file
        ], capture_output=True, text=True, timeout=30)
        
        if result.stdout.strip():
            print("❌ Autopep8 предлагает изменения:")
            print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
        else:
            print("✅ Файл не нуждается в изменениях")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # 6. Проверка конкретных строк
    print("\n6️⃣ АНАЛИЗ ПРОБЛЕМНЫХ СТРОК:")
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print("Строки 12-25:")
        for i, line in enumerate(lines[11:25], 12):
            print(f"  {i:2d}: {line.rstrip()}")
        
        print("\nПроблема: Импорты после sys.path.append()")
        print("Решение: Переместить все импорты в начало файла")
        
    except Exception as e:
        print(f"❌ Ошибка чтения файла: {e}")

if __name__ == "__main__":
    check_with_different_linters()