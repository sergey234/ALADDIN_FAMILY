#!/usr/bin/env python3
"""
Автоматические тесты форматирования для системы ALADDIN
Проверяет качество кода, форматирование и соответствие стандартам
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

class FormattingTester:
    def __init__(self, project_root="/Users/sergejhlystov/ALADDIN_NEW"):
        self.project_root = Path(project_root)
        self.security_dir = self.project_root / "security"
        self.scripts_dir = self.project_root / "scripts"
        self.core_dir = self.project_root / "core"
        self.config_dir = self.project_root / "config"
        
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "total_files": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "tests": []
        }
        
        self.exclude_dirs = {
            "backup", "backups", "test", "tests", "logs", 
            "formatting_work", "__pycache__", ".git"
        }

    def find_python_files(self) -> List[Path]:
        """Найти все Python файлы для тестирования"""
        python_files = []
        
        for directory in [self.security_dir, self.scripts_dir, self.core_dir, self.config_dir]:
            if directory.exists():
                for file_path in directory.rglob("*.py"):
                    if not any(exclude in str(file_path) for exclude in self.exclude_dirs):
                        python_files.append(file_path)
        
        return python_files

    def test_black_formatting(self, file_path: Path) -> Tuple[bool, str]:
        """Тест форматирования Black"""
        try:
            result = subprocess.run([
                "black", 
                "--check", 
                "--line-length=120",
                str(file_path)
            ], capture_output=True, text=True, timeout=30)
            
            return result.returncode == 0, result.stderr
        except subprocess.TimeoutExpired:
            return False, "Timeout"
        except Exception as e:
            return False, str(e)

    def test_autopep8_formatting(self, file_path: Path) -> Tuple[bool, str]:
        """Тест форматирования autopep8"""
        try:
            result = subprocess.run([
                "autopep8",
                "--diff",
                "--max-line-length=120",
                str(file_path)
            ], capture_output=True, text=True, timeout=30)
            
            return result.returncode == 0, result.stdout
        except subprocess.TimeoutExpired:
            return False, "Timeout"
        except Exception as e:
            return False, str(e)

    def test_isort_imports(self, file_path: Path) -> Tuple[bool, str]:
        """Тест сортировки импортов isort"""
        try:
            result = subprocess.run([
                "isort",
                "--check-only",
                "--profile=black",
                "--line-length=120",
                str(file_path)
            ], capture_output=True, text=True, timeout=30)
            
            return result.returncode == 0, result.stdout
        except subprocess.TimeoutExpired:
            return False, "Timeout"
        except Exception as e:
            return False, str(e)

    def test_flake8_errors(self, file_path: Path) -> Tuple[bool, str, int]:
        """Тест ошибок flake8"""
        try:
            result = subprocess.run([
                "flake8",
                "--max-line-length=120",
                "--exclude=*/backup*,*/test*,*/logs*,*/formatting_work*",
                str(file_path)
            ], capture_output=True, text=True, timeout=30)
            
            error_count = len(result.stdout.split('\n')) if result.stdout else 0
            return result.returncode == 0, result.stdout, error_count
        except subprocess.TimeoutExpired:
            return False, "Timeout", 0
        except Exception as e:
            return False, str(e), 0

    def test_file_syntax(self, file_path: Path) -> Tuple[bool, str]:
        """Тест синтаксиса Python"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                compile(f.read(), str(file_path), 'exec')
            return True, ""
        except SyntaxError as e:
            return False, f"SyntaxError: {e}"
        except Exception as e:
            return False, f"Error: {e}"

    def test_line_length(self, file_path: Path) -> Tuple[bool, List[int]]:
        """Тест длины строк"""
        long_lines = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if len(line.rstrip()) > 120:
                        long_lines.append(line_num)
            return len(long_lines) == 0, long_lines
        except Exception:
            return False, []

    def test_trailing_whitespace(self, file_path: Path) -> Tuple[bool, List[int]]:
        """Тест пробелов в конце строк"""
        trailing_lines = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if line.rstrip() != line.rstrip(' \t'):
                        trailing_lines.append(line_num)
            return len(trailing_lines) == 0, trailing_lines
        except Exception:
            return False, []

    def test_file_encoding(self, file_path: Path) -> Tuple[bool, str]:
        """Тест кодировки файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read()
            return True, "UTF-8"
        except UnicodeDecodeError as e:
            return False, f"Encoding error: {e}"
        except Exception as e:
            return False, f"Error: {e}"

    def run_tests_for_file(self, file_path: Path) -> Dict:
        """Запустить все тесты для одного файла"""
        relative_path = file_path.relative_to(self.project_root)
        
        test_result = {
            "file": str(relative_path),
            "passed": 0,
            "failed": 0,
            "total": 0,
            "tests": []
        }
        
        # Список тестов
        tests = [
            ("syntax", self.test_file_syntax),
            ("encoding", self.test_file_encoding),
            ("black", self.test_black_formatting),
            ("autopep8", self.test_autopep8_formatting),
            ("isort", self.test_isort_imports),
            ("flake8", self.test_flake8_errors),
            ("line_length", self.test_line_length),
            ("trailing_whitespace", self.test_trailing_whitespace)
        ]
        
        for test_name, test_func in tests:
            test_result["total"] += 1
            
            try:
                if test_name == "flake8":
                    success, output, error_count = test_func(file_path)
                    test_info = {
                        "name": test_name,
                        "passed": success,
                        "output": output,
                        "error_count": error_count
                    }
                elif test_name in ["line_length", "trailing_whitespace"]:
                    success, lines = test_func(file_path)
                    test_info = {
                        "name": test_name,
                        "passed": success,
                        "problem_lines": lines
                    }
                else:
                    success, output = test_func(file_path)
                    test_info = {
                        "name": test_name,
                        "passed": success,
                        "output": output
                    }
                
                if success:
                    test_result["passed"] += 1
                else:
                    test_result["failed"] += 1
                
                test_result["tests"].append(test_info)
                
            except Exception as e:
                test_result["failed"] += 1
                test_result["tests"].append({
                    "name": test_name,
                    "passed": False,
                    "error": str(e)
                })
        
        return test_result

    def run_all_tests(self) -> Dict:
        """Запустить все тесты"""
        print("🧪 ЗАПУСК АВТОМАТИЧЕСКИХ ТЕСТОВ ФОРМАТИРОВАНИЯ")
        print("=" * 60)
        
        python_files = self.find_python_files()
        self.test_results["total_files"] = len(python_files)
        
        print(f"📁 Найдено {len(python_files)} файлов для тестирования")
        print()
        
        for i, file_path in enumerate(python_files, 1):
            print(f"🔍 Тестирование {i}/{len(python_files)}: {file_path.relative_to(self.project_root)}")
            
            test_result = self.run_tests_for_file(file_path)
            self.test_results["tests"].append(test_result)
            
            if test_result["failed"] == 0:
                self.test_results["passed_tests"] += 1
                print(f"✅ Все тесты пройдены ({test_result['passed']}/{test_result['total']})")
            else:
                self.test_results["failed_tests"] += 1
                print(f"❌ Провалено тестов: {test_result['failed']}/{test_result['total']}")
                
                # Показать детали проваленных тестов
                for test in test_result["tests"]:
                    if not test["passed"]:
                        print(f"   ⚠️  {test['name']}: {test.get('output', test.get('error', 'Unknown error'))}")
            
            print()
        
        return self.test_results

    def generate_report(self, output_file: str = "formatting_test_report.json"):
        """Создать отчет о тестах"""
        report_path = self.project_root / output_file
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Отчет сохранен: {report_path}")
        return report_path

    def print_summary(self):
        """Вывести сводку результатов"""
        total_tests = self.test_results["passed_tests"] + self.test_results["failed_tests"]
        success_rate = (self.test_results["passed_tests"] / total_tests * 100) if total_tests > 0 else 0
        
        print("=" * 60)
        print("📊 СВОДКА ТЕСТОВ ФОРМАТИРОВАНИЯ")
        print("=" * 60)
        print(f"📁 Всего файлов: {self.test_results['total_files']}")
        print(f"✅ Успешных тестов: {self.test_results['passed_tests']}")
        print(f"❌ Проваленных тестов: {self.test_results['failed_tests']}")
        print(f"📈 Процент успеха: {success_rate:.1f}%")
        print("=" * 60)
        
        if self.test_results["failed_tests"] > 0:
            print("\n🔧 РЕКОМЕНДАЦИИ:")
            print("1. Запустите: python3 scripts/auto_format_all.py")
            print("2. Проверьте: pre-commit run --all-files")
            print("3. Исправьте ошибки вручную при необходимости")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Тесты форматирования ALADDIN")
    parser.add_argument("--project-root", default="/Users/sergejhlystov/ALADDIN_NEW",
                       help="Корневая директория проекта")
    parser.add_argument("--output", default="formatting_test_report.json",
                       help="Файл отчета")
    
    args = parser.parse_args()
    
    tester = FormattingTester(args.project_root)
    results = tester.run_all_tests()
    tester.generate_report(args.output)
    tester.print_summary()
    
    # Возвращаем код выхода на основе результатов
    sys.exit(0 if results["failed_tests"] == 0 else 1)

if __name__ == "__main__":
    main()