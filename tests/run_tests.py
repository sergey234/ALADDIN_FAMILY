#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для запуска unit тестов Service Mesh Manager

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

def run_tests(test_type="all", verbose=False, coverage=False, parallel=False):
    """Запуск тестов"""
    
    # Добавляем корневую директорию в PYTHONPATH
    root_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(root_dir))
    
    # Базовые аргументы pytest
    cmd = ["python3", "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=security.microservices.service_mesh_manager", "--cov-report=html", "--cov-report=term"])
    
    if parallel:
        cmd.extend(["-n", "auto"])
    
    # Выбор типа тестов
    if test_type == "unit":
        cmd.append("test_service_mesh_manager.py")
    elif test_type == "integration":
        cmd.append("test_integration.py")
    elif test_type == "performance":
        cmd.extend(["-m", "performance"])
    elif test_type == "slow":
        cmd.extend(["-m", "slow"])
    else:  # all
        cmd.append(".")
    
    # Запуск тестов
    print(f"Запуск тестов: {' '.join(cmd)}")
    print(f"Рабочая директория: {os.getcwd()}")
    
    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent)
        return result.returncode
    except Exception as e:
        print(f"Ошибка запуска тестов: {e}")
        return 1

def main():
    """Основная функция"""
    parser = argparse.ArgumentParser(description="Запуск unit тестов Service Mesh Manager")
    parser.add_argument("--type", choices=["all", "unit", "integration", "performance", "slow"], 
                       default="all", help="Тип тестов для запуска")
    parser.add_argument("--verbose", "-v", action="store_true", help="Подробный вывод")
    parser.add_argument("--coverage", "-c", action="store_true", help="Покрытие кода")
    parser.add_argument("--parallel", "-p", action="store_true", help="Параллельный запуск")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("ALADDIN Security Team - Unit Tests")
    print("Service Mesh Manager Test Suite")
    print("=" * 60)
    
    exit_code = run_tests(
        test_type=args.type,
        verbose=args.verbose,
        coverage=args.coverage,
        parallel=args.parallel
    )
    
    if exit_code == 0:
        print("\n✅ Все тесты прошли успешно!")
    else:
        print("\n❌ Некоторые тесты не прошли!")
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())
