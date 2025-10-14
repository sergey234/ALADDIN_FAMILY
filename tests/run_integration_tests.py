#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для запуска интеграционных тестов Service Mesh Manager

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

def run_integration_tests(test_type="all", verbose=False, performance=False, timeout=300):
    """Запуск интеграционных тестов"""
    
    # Добавляем корневую директорию в PYTHONPATH
    root_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(root_dir))
    
    # Базовые аргументы pytest
    cmd = ["python3", "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    
    if performance:
        cmd.extend(["-m", "performance"])
    
    # Таймаут для тестов
    cmd.extend(["--timeout", str(timeout)])
    
    # Выбор типа тестов
    if test_type == "integration":
        cmd.append("test_integration.py")
    elif test_type == "scenarios":
        cmd.append("test_integration_scenarios.py")
    elif test_type == "performance":
        cmd.append("test_performance_integration.py")
    elif test_type == "ecommerce":
        cmd.extend(["-m", "ecommerce"])
    elif test_type == "iot":
        cmd.extend(["-m", "iot"])
    elif test_type == "financial":
        cmd.extend(["-m", "financial"])
    elif test_type == "resilience":
        cmd.extend(["-m", "resilience"])
    elif test_type == "stress":
        cmd.extend(["-m", "stress"])
    elif test_type == "endurance":
        cmd.extend(["-m", "endurance"])
    elif test_type == "scalability":
        cmd.extend(["-m", "scalability"])
    else:  # all
        cmd.extend(["test_integration*.py", "test_performance_integration.py"])
    
    # Запуск тестов
    print(f"Запуск интеграционных тестов: {' '.join(cmd)}")
    print(f"Рабочая директория: {os.getcwd()}")
    
    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent)
        return result.returncode
    except Exception as e:
        print(f"Ошибка запуска интеграционных тестов: {e}")
        return 1

def main():
    """Основная функция"""
    parser = argparse.ArgumentParser(description="Запуск интеграционных тестов Service Mesh Manager")
    parser.add_argument("--type", 
                       choices=["all", "integration", "scenarios", "performance", 
                               "ecommerce", "iot", "financial", "resilience", 
                               "stress", "endurance", "scalability"], 
                       default="all", help="Тип тестов для запуска")
    parser.add_argument("--verbose", "-v", action="store_true", help="Подробный вывод")
    parser.add_argument("--performance", "-p", action="store_true", help="Запуск тестов производительности")
    parser.add_argument("--timeout", "-t", type=int, default=300, help="Таймаут для тестов в секундах")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("ALADDIN Security Team - Integration Tests")
    print("Service Mesh Manager Integration Test Suite")
    print("=" * 60)
    
    exit_code = run_integration_tests(
        test_type=args.type,
        verbose=args.verbose,
        performance=args.performance,
        timeout=args.timeout
    )
    
    if exit_code == 0:
        print("\n✅ Все интеграционные тесты прошли успешно!")
    else:
        print("\n❌ Некоторые интеграционные тесты не прошли!")
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())
