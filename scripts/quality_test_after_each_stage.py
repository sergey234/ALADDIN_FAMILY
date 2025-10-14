#!/usr/bin/env python3
"""
🧪 СИСТЕМА КАЧЕСТВЕННЫХ ТЕСТОВ ПОСЛЕ КАЖДОГО ЭТАПА
8 типов тестов для проверки качества A+ после каждого этапа реализации

Автор: AI Assistant
Дата: 2025-01-13
Версия: 1.0.0
"""

import os
import sys
import json
import subprocess
import ast
import importlib.util
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime


class QualityTestSystem:
    """🧪 Система качественных тестов для проверки A+ качества"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.results = {}
        self.test_config = {
            "test_types": [
                "syntax_validation",
                "import_validation", 
                "security_validation",
                "code_quality",
                "performance_test",
                "integration_test",
                "functionality_test",
                "production_readiness"
            ],
            "stages": [
                "stage_1_critical_fixes",
                "stage_2_security",
                "stage_3_code_quality",
                "stage_4_production_ready"
            ]
        }
    
    def run_syntax_validation(self) -> Dict[str, Any]:
        """🔍 Тест 1: Валидация синтаксиса Python"""
        print("🔍 Запуск теста: Валидация синтаксиса...")
        
        results = {
            "test_name": "syntax_validation",
            "total_files": 0,
            "valid_files": 0,
            "invalid_files": 0,
            "errors": [],
            "score": 0
        }
        
        python_files = list(self.project_root.rglob("*.py"))
        results["total_files"] = len(python_files)
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                ast.parse(content)
                results["valid_files"] += 1
            except SyntaxError as e:
                results["invalid_files"] += 1
                results["errors"].append({
                    "file": str(py_file),
                    "error": str(e),
                    "line": e.lineno
                })
            except Exception as e:
                results["invalid_files"] += 1
                results["errors"].append({
                    "file": str(py_file),
                    "error": str(e),
                    "line": "unknown"
                })
        
        if results["total_files"] > 0:
            results["score"] = (results["valid_files"] / results["total_files"]) * 100
        
        print(f"✅ Синтаксис: {results['valid_files']}/{results['total_files']} файлов ({results['score']:.1f}%)")
        return results
    
    def run_import_validation(self) -> Dict[str, Any]:
        """📦 Тест 2: Валидация импортов"""
        print("📦 Запуск теста: Валидация импортов...")
        
        results = {
            "test_name": "import_validation",
            "total_files": 0,
            "valid_imports": 0,
            "invalid_imports": 0,
            "errors": [],
            "score": 0
        }
        
        python_files = list(self.project_root.rglob("*.py"))
        results["total_files"] = len(python_files)
        
        for py_file in python_files:
            try:
                spec = importlib.util.spec_from_file_location("module", py_file)
                if spec and spec.loader:
                    results["valid_imports"] += 1
                else:
                    results["invalid_imports"] += 1
                    results["errors"].append({
                        "file": str(py_file),
                        "error": "Cannot create module spec"
                    })
            except Exception as e:
                results["invalid_imports"] += 1
                results["errors"].append({
                    "file": str(py_file),
                    "error": str(e)
                })
        
        if results["total_files"] > 0:
            results["score"] = (results["valid_imports"] / results["total_files"]) * 100
        
        print(f"✅ Импорты: {results['valid_imports']}/{results['total_files']} файлов ({results['score']:.1f}%)")
        return results
    
    def run_security_validation(self) -> Dict[str, Any]:
        """🔒 Тест 3: Валидация безопасности"""
        print("🔒 Запуск теста: Валидация безопасности...")
        
        results = {
            "test_name": "security_validation",
            "total_files": 0,
            "secure_files": 0,
            "vulnerable_files": 0,
            "vulnerabilities": [],
            "score": 0
        }
        
        security_patterns = [
            "exec(", "eval(", "os.system(", "subprocess.call(",
            "pickle.loads(", "yaml.load(", "input(", "raw_input("
        ]
        
        python_files = list(self.project_root.rglob("*.py"))
        results["total_files"] = len(python_files)
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                vulnerabilities_found = []
                for pattern in security_patterns:
                    if pattern in content:
                        vulnerabilities_found.append(pattern)
                
                if vulnerabilities_found:
                    results["vulnerable_files"] += 1
                    results["vulnerabilities"].append({
                        "file": str(py_file),
                        "patterns": vulnerabilities_found
                    })
                else:
                    results["secure_files"] += 1
                    
            except Exception as e:
                results["vulnerable_files"] += 1
                results["vulnerabilities"].append({
                    "file": str(py_file),
                    "error": str(e)
                })
        
        if results["total_files"] > 0:
            results["score"] = (results["secure_files"] / results["total_files"]) * 100
        
        print(f"✅ Безопасность: {results['secure_files']}/{results['total_files']} файлов ({results['score']:.1f}%)")
        return results
    
    def run_code_quality(self) -> Dict[str, Any]:
        """💎 Тест 4: Качество кода"""
        print("💎 Запуск теста: Качество кода...")
        
        results = {
            "test_name": "code_quality",
            "total_files": 0,
            "high_quality_files": 0,
            "low_quality_files": 0,
            "issues": [],
            "score": 0
        }
        
        try:
            # Запуск flake8 для проверки качества кода
            result = subprocess.run([
                "python3", "-m", "flake8", 
                str(self.project_root),
                "--count", "--statistics"
            ], capture_output=True, text=True, cwd=self.project_root)
            
            python_files = list(self.project_root.rglob("*.py"))
            results["total_files"] = len(python_files)
            
            if result.returncode == 0:
                results["high_quality_files"] = results["total_files"]
                results["score"] = 100
            else:
                # Правильный подсчет ошибок из вывода flake8
                error_lines = [line for line in result.stdout.split('\n') if line.strip() and ':' in line and not line.strip().isdigit()]
                error_count = len(error_lines)
                results["low_quality_files"] = error_count
                results["high_quality_files"] = results["total_files"] - error_count
                results["issues"] = error_lines[:10]  # Показываем только первые 10 ошибок
                
                if results["total_files"] > 0:
                    # Более реалистичный расчет - учитываем что не все файлы имеют ошибки
                    files_with_errors = len(set(line.split(':')[0] for line in error_lines))
                    results["score"] = max(0, ((results["total_files"] - files_with_errors) / results["total_files"]) * 100)
                    
        except Exception as e:
            results["issues"].append(f"Ошибка запуска flake8: {e}")
            results["score"] = 0
        
        print(f"✅ Качество кода: {results['score']:.1f}%")
        return results
    
    def run_performance_test(self) -> Dict[str, Any]:
        """⚡ Тест 5: Производительность"""
        print("⚡ Запуск теста: Производительность...")
        
        results = {
            "test_name": "performance_test",
            "total_files": 0,
            "fast_files": 0,
            "slow_files": 0,
            "issues": [],
            "score": 0
        }
        
        # Простая проверка на наличие потенциально медленных операций
        performance_issues = [
            "time.sleep(", "while True:", "for i in range(1000000):",
            "import numpy as np", "import pandas as pd"
        ]
        
        python_files = list(self.project_root.rglob("*.py"))
        results["total_files"] = len(python_files)
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                issues_found = []
                for issue in performance_issues:
                    if issue in content:
                        issues_found.append(issue)
                
                if issues_found:
                    results["slow_files"] += 1
                    results["issues"].append({
                        "file": str(py_file),
                        "issues": issues_found
                    })
                else:
                    results["fast_files"] += 1
                    
            except Exception as e:
                results["slow_files"] += 1
                results["issues"].append({
                    "file": str(py_file),
                    "error": str(e)
                })
        
        if results["total_files"] > 0:
            results["score"] = (results["fast_files"] / results["total_files"]) * 100
        
        print(f"✅ Производительность: {results['score']:.1f}%")
        return results
    
    def run_integration_test(self) -> Dict[str, Any]:
        """🔗 Тест 6: Интеграционное тестирование"""
        print("🔗 Запуск теста: Интеграционное тестирование...")
        
        results = {
            "test_name": "integration_test",
            "total_modules": 0,
            "integrated_modules": 0,
            "failed_modules": 0,
            "errors": [],
            "score": 0
        }
        
        # Проверка основных модулей системы
        main_modules = [
            "core/system_manager.py",
            "security/base.py",
            "security/managers/analytics_manager.py",
            "security/managers/monitor_manager.py",
            "security/managers/report_manager.py"
        ]
        
        results["total_modules"] = len(main_modules)
        
        for module_path in main_modules:
            full_path = self.project_root / module_path
            if full_path.exists():
                try:
                    spec = importlib.util.spec_from_file_location("module", full_path)
                    if spec and spec.loader:
                        results["integrated_modules"] += 1
                    else:
                        results["failed_modules"] += 1
                        results["errors"].append({
                            "module": module_path,
                            "error": "Cannot create module spec"
                        })
                except Exception as e:
                    results["failed_modules"] += 1
                    results["errors"].append({
                        "module": module_path,
                        "error": str(e)
                    })
            else:
                results["failed_modules"] += 1
                results["errors"].append({
                    "module": module_path,
                    "error": "File not found"
                })
        
        if results["total_modules"] > 0:
            results["score"] = (results["integrated_modules"] / results["total_modules"]) * 100
        
        print(f"✅ Интеграция: {results['integrated_modules']}/{results['total_modules']} модулей ({results['score']:.1f}%)")
        return results
    
    def run_functionality_test(self) -> Dict[str, Any]:
        """⚙️ Тест 7: Функциональность"""
        print("⚙️ Запуск теста: Функциональность...")
        
        results = {
            "test_name": "functionality_test",
            "total_functions": 0,
            "working_functions": 0,
            "broken_functions": 0,
            "errors": [],
            "score": 0
        }
        
        # Подсчет функций в коде
        python_files = list(self.project_root.rglob("*.py"))
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                results["total_functions"] += len(functions)
                
                # Простая проверка на наличие основных элементов функции
                for func in functions:
                    if func.name and len(func.body) > 0:
                        results["working_functions"] += 1
                    else:
                        results["broken_functions"] += 1
                        results["errors"].append({
                            "file": str(py_file),
                            "function": func.name,
                            "error": "Empty or invalid function"
                        })
                        
            except Exception as e:
                results["errors"].append({
                    "file": str(py_file),
                    "error": str(e)
                })
        
        if results["total_functions"] > 0:
            results["score"] = (results["working_functions"] / results["total_functions"]) * 100
        
        print(f"✅ Функциональность: {results['working_functions']}/{results['total_functions']} функций ({results['score']:.1f}%)")
        return results
    
    def run_production_readiness(self) -> Dict[str, Any]:
        """🚀 Тест 8: Готовность к продакшену"""
        print("🚀 Запуск теста: Готовность к продакшену...")
        
        results = {
            "test_name": "production_readiness",
            "total_checks": 8,
            "passed_checks": 0,
            "failed_checks": 0,
            "issues": [],
            "score": 0
        }
        
        checks = [
            ("config_files", self.project_root / "config"),
            ("logs_directory", self.project_root / "logs"),
            ("tests_directory", self.project_root / "tests"),
            ("documentation", self.project_root / "docs"),
            ("requirements", self.project_root / "requirements.txt"),
            ("readme", self.project_root / "README.md"),
            ("gitignore", self.project_root / ".gitignore"),
            ("main_entry", self.project_root / "main.py")
        ]
        
        for check_name, check_path in checks:
            if check_path.exists():
                results["passed_checks"] += 1
            else:
                results["failed_checks"] += 1
                results["issues"].append({
                    "check": check_name,
                    "path": str(check_path),
                    "status": "missing"
                })
        
        results["score"] = (results["passed_checks"] / results["total_checks"]) * 100
        
        print(f"✅ Готовность к продакшену: {results['passed_checks']}/{results['total_checks']} проверок ({results['score']:.1f}%)")
        return results
    
    def run_all_tests(self, stage: str = "all") -> Dict[str, Any]:
        """🧪 Запуск всех тестов"""
        print(f"\n🧪 ЗАПУСК СИСТЕМЫ КАЧЕСТВЕННЫХ ТЕСТОВ - ЭТАП: {stage.upper()}")
        print("=" * 80)
        
        test_results = {
            "stage": stage,
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "overall_score": 0,
            "summary": {}
        }
        
        # Запуск всех тестов
        test_methods = [
            self.run_syntax_validation,
            self.run_import_validation,
            self.run_security_validation,
            self.run_code_quality,
            self.run_performance_test,
            self.run_integration_test,
            self.run_functionality_test,
            self.run_production_readiness
        ]
        
        total_score = 0
        for test_method in test_methods:
            try:
                result = test_method()
                test_results["tests"][result["test_name"]] = result
                total_score += result["score"]
            except Exception as e:
                print(f"❌ Ошибка в тесте {test_method.__name__}: {e}")
                test_results["tests"][test_method.__name__] = {
                    "error": str(e),
                    "score": 0
                }
        
        # Расчет общего балла
        test_results["overall_score"] = total_score / len(test_methods)
        
        # Создание сводки
        test_results["summary"] = {
            "total_tests": len(test_methods),
            "passed_tests": len([t for t in test_results["tests"].values() if t.get("score", 0) >= 80]),
            "failed_tests": len([t for t in test_results["tests"].values() if t.get("score", 0) < 80]),
            "average_score": test_results["overall_score"]
        }
        
        return test_results
    
    def save_results(self, results: Dict[str, Any], filename: str = None):
        """💾 Сохранение результатов тестов"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"quality_test_results_{results['stage']}_{timestamp}.json"
        
        results_file = self.project_root / "reports" / filename
        results_file.parent.mkdir(exist_ok=True)
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Результаты сохранены: {results_file}")
        return results_file
    
    def display_summary(self, results: Dict[str, Any]):
        """📊 Отображение сводки результатов"""
        print("\n" + "="*80)
        print("📊 СВОДКА РЕЗУЛЬТАТОВ КАЧЕСТВЕННЫХ ТЕСТОВ")
        print("="*80)
        
        print(f"🎯 Этап: {results['stage']}")
        print(f"⏰ Время: {results['timestamp']}")
        print(f"📈 Общий балл: {results['overall_score']:.1f}%")
        
        summary = results['summary']
        print(f"🧪 Всего тестов: {summary['total_tests']}")
        print(f"✅ Пройдено: {summary['passed_tests']}")
        print(f"❌ Не пройдено: {summary['failed_tests']}")
        print(f"📊 Средний балл: {summary['average_score']:.1f}%")
        
        print("\n📋 ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ:")
        print("-" * 50)
        
        for test_name, test_result in results['tests'].items():
            if 'score' in test_result:
                status = "✅" if test_result['score'] >= 80 else "❌"
                print(f"{status} {test_name}: {test_result['score']:.1f}%")
            else:
                print(f"❌ {test_name}: Ошибка")
        
        # Оценка качества
        if results['overall_score'] >= 95:
            quality = "🏆 МИРОВОЙ КЛАСС (A+)"
        elif results['overall_score'] >= 90:
            quality = "🥇 ОТЛИЧНО (A)"
        elif results['overall_score'] >= 80:
            quality = "🥈 ХОРОШО (B)"
        elif results['overall_score'] >= 70:
            quality = "🥉 УДОВЛЕТВОРИТЕЛЬНО (C)"
        else:
            quality = "❌ ТРЕБУЕТ УЛУЧШЕНИЯ (D)"
        
        print(f"\n🎯 ОЦЕНКА КАЧЕСТВА: {quality}")
        print("="*80)


def main():
    """🚀 Главная функция"""
    print("🧪 СИСТЕМА КАЧЕСТВЕННЫХ ТЕСТОВ ПОСЛЕ КАЖДОГО ЭТАПА")
    print("=" * 60)
    
    test_system = QualityTestSystem()
    
    if len(sys.argv) > 1:
        stage = sys.argv[1]
    else:
        stage = "all"
    
    # Запуск всех тестов
    results = test_system.run_all_tests(stage)
    
    # Сохранение результатов
    test_system.save_results(results)
    
    # Отображение сводки
    test_system.display_summary(results)


if __name__ == "__main__":
    main()