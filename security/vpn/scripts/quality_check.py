#!/usr/bin/env python3
"""
ALADDIN VPN - Quality Check Script
Скрипт для проверки качества кода

Автор: ALADDIN Security Team
Версия: 1.0.0
Дата: 01.10.2025
"""

import subprocess
import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Tuple
from pathlib import Path

class QualityChecker:
    """Проверка качества кода"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.results = {
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {},
            "overall_score": 0,
            "status": "unknown"
        }
    
    def run_command(self, command: List[str], cwd: str = None) -> Tuple[bool, str, str]:
        """Запуск команды и получение результата"""
        try:
            result = subprocess.run(
                command,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)
    
    def check_black_formatting(self) -> Dict[str, Any]:
        """Проверка форматирования Black"""
        print("🎨 Проверка форматирования Black...")
        
        success, stdout, stderr = self.run_command([
            "python", "-m", "black", "--check", "--diff", "."
        ])
        
        return {
            "tool": "black",
            "success": success,
            "output": stdout,
            "error": stderr,
            "score": 100 if success else 0
        }
    
    def check_isort_imports(self) -> Dict[str, Any]:
        """Проверка сортировки импортов isort"""
        print("📦 Проверка сортировки импортов isort...")
        
        success, stdout, stderr = self.run_command([
            "python", "-m", "isort", "--check-only", "--diff", "."
        ])
        
        return {
            "tool": "isort",
            "success": success,
            "output": stdout,
            "error": stderr,
            "score": 100 if success else 0
        }
    
    def check_flake8_linting(self) -> Dict[str, Any]:
        """Проверка линтинга Flake8"""
        print("🔍 Проверка линтинга Flake8...")
        
        success, stdout, stderr = self.run_command([
            "python", "-m", "flake8", "."
        ])
        
        # Подсчет ошибок
        error_count = len([line for line in stdout.split('\n') if line.strip()])
        
        # Оценка на основе количества ошибок
        if error_count == 0:
            score = 100
        elif error_count <= 10:
            score = 90
        elif error_count <= 25:
            score = 75
        elif error_count <= 50:
            score = 50
        else:
            score = 25
        
        return {
            "tool": "flake8",
            "success": success,
            "output": stdout,
            "error": stderr,
            "error_count": error_count,
            "score": score
        }
    
    def check_pylint_analysis(self) -> Dict[str, Any]:
        """Проверка анализа Pylint"""
        print("🔬 Проверка анализа Pylint...")
        
        success, stdout, stderr = self.run_command([
            "python", "-m", "pylint", "--score=y", "."
        ])
        
        # Извлечение оценки из вывода
        score = 0
        if "Your code has been rated at" in stdout:
            try:
                score_line = [line for line in stdout.split('\n') if "Your code has been rated at" in line][0]
                score = float(score_line.split("at ")[1].split("/")[0])
            except (IndexError, ValueError):
                pass
        
        return {
            "tool": "pylint",
            "success": success,
            "output": stdout,
            "error": stderr,
            "score": score
        }
    
    def check_mypy_typing(self) -> Dict[str, Any]:
        """Проверка типизации MyPy"""
        print("🔤 Проверка типизации MyPy...")
        
        success, stdout, stderr = self.run_command([
            "python", "-m", "mypy", "--ignore-missing-imports", "."
        ])
        
        # Подсчет ошибок типизации
        error_count = len([line for line in stdout.split('\n') if "error:" in line])
        
        # Оценка на основе количества ошибок
        if error_count == 0:
            score = 100
        elif error_count <= 5:
            score = 90
        elif error_count <= 15:
            score = 75
        elif error_count <= 30:
            score = 50
        else:
            score = 25
        
        return {
            "tool": "mypy",
            "success": success,
            "output": stdout,
            "error": stderr,
            "error_count": error_count,
            "score": score
        }
    
    def check_security_issues(self) -> Dict[str, Any]:
        """Проверка проблем безопасности"""
        print("🔒 Проверка проблем безопасности...")
        
        # Проверяем наличие потенциально опасных паттернов
        dangerous_patterns = [
            "eval(",
            "exec(",
            "__import__",
            "pickle.loads",
            "subprocess.call",
            "os.system",
            "shell=True"
        ]
        
        issues = []
        for root, dirs, files in os.walk(self.project_root):
            # Пропускаем служебные директории
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            for pattern in dangerous_patterns:
                                if pattern in content:
                                    issues.append(f"{file_path}: {pattern}")
                    except Exception:
                        continue
        
        score = max(0, 100 - len(issues) * 10)
        
        return {
            "tool": "security",
            "success": len(issues) == 0,
            "issues": issues,
            "issue_count": len(issues),
            "score": score
        }
    
    def check_test_coverage(self) -> Dict[str, Any]:
        """Проверка покрытия тестами"""
        print("🧪 Проверка покрытия тестами...")
        
        # Запускаем тесты с покрытием
        success, stdout, stderr = self.run_command([
            "python", "-m", "pytest", "--cov=.", "--cov-report=term-missing", "tests/"
        ])
        
        # Извлекаем процент покрытия
        coverage_percent = 0
        if "TOTAL" in stdout:
            try:
                total_line = [line for line in stdout.split('\n') if "TOTAL" in line][0]
                coverage_percent = float(total_line.split()[-1].replace('%', ''))
            except (IndexError, ValueError):
                pass
        
        return {
            "tool": "coverage",
            "success": success,
            "output": stdout,
            "error": stderr,
            "coverage_percent": coverage_percent,
            "score": coverage_percent
        }
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Запуск всех проверок"""
        print("🚀 Запуск проверки качества кода ALADDIN VPN...")
        print("=" * 60)
        
        # Запускаем все проверки
        checks = [
            self.check_black_formatting(),
            self.check_isort_imports(),
            self.check_flake8_linting(),
            self.check_pylint_analysis(),
            self.check_mypy_typing(),
            self.check_security_issues(),
            self.check_test_coverage()
        ]
        
        # Сохраняем результаты
        for check in checks:
            self.results["checks"][check["tool"]] = check
        
        # Вычисляем общую оценку
        scores = [check["score"] for check in checks]
        self.results["overall_score"] = sum(scores) / len(scores)
        
        # Определяем статус
        if self.results["overall_score"] >= 90:
            self.results["status"] = "excellent"
        elif self.results["overall_score"] >= 80:
            self.results["status"] = "good"
        elif self.results["overall_score"] >= 70:
            self.results["status"] = "fair"
        elif self.results["overall_score"] >= 60:
            self.results["status"] = "poor"
        else:
            self.results["status"] = "critical"
        
        return self.results
    
    def print_results(self):
        """Вывод результатов"""
        print("\n" + "=" * 60)
        print("📊 РЕЗУЛЬТАТЫ ПРОВЕРКИ КАЧЕСТВА КОДА")
        print("=" * 60)
        
        # Общая оценка
        overall_score = self.results["overall_score"]
        status = self.results["status"]
        
        status_emoji = {
            "excellent": "🟢",
            "good": "🟡", 
            "fair": "🟠",
            "poor": "🔴",
            "critical": "💀"
        }.get(status, "❓")
        
        print(f"\n🎯 Общая оценка: {status_emoji} {overall_score:.1f}/100 ({status.upper()})")
        
        # Детали по инструментам
        print(f"\n📋 Детали по инструментам:")
        for tool, check in self.results["checks"].items():
            score = check["score"]
            success = check["success"]
            
            emoji = "✅" if success else "❌"
            print(f"   {tool.upper()}: {emoji} {score:.1f}/100")
            
            # Показываем ошибки для неудачных проверок
            if not success and "error_count" in check:
                print(f"     Ошибок: {check['error_count']}")
            elif not success and "issue_count" in check:
                print(f"     Проблем: {check['issue_count']}")
            elif not success and "coverage_percent" in check:
                print(f"     Покрытие: {check['coverage_percent']:.1f}%")
        
        # Рекомендации
        print(f"\n💡 Рекомендации:")
        for tool, check in self.results["checks"].items():
            if check["score"] < 80:
                if tool == "black":
                    print("   • Запустите 'black .' для форматирования кода")
                elif tool == "isort":
                    print("   • Запустите 'isort .' для сортировки импортов")
                elif tool == "flake8":
                    print("   • Исправьте ошибки линтинга, показанные выше")
                elif tool == "pylint":
                    print("   • Улучшите качество кода согласно рекомендациям Pylint")
                elif tool == "mypy":
                    print("   • Добавьте типизацию для улучшения качества кода")
                elif tool == "security":
                    print("   • Проверьте потенциальные проблемы безопасности")
                elif tool == "coverage":
                    print("   • Добавьте тесты для увеличения покрытия")
    
    def save_results(self, filename: str = None):
        """Сохранение результатов в файл"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"quality_check_{timestamp}.json"
        
        filepath = self.project_root / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Результаты сохранены в: {filepath}")
        return filepath

def main():
    """Главная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ALADDIN VPN Quality Check")
    parser.add_argument("--project-root", help="Корневая директория проекта")
    parser.add_argument("--save", action="store_true", help="Сохранить результаты в файл")
    parser.add_argument("--check", choices=["all", "format", "lint", "type", "security", "coverage"], 
                       default="all", help="Тип проверки")
    
    args = parser.parse_args()
    
    # Создаем checker
    checker = QualityChecker(args.project_root)
    
    # Запускаем проверки
    if args.check == "all":
        results = checker.run_all_checks()
    else:
        # Запускаем только выбранную проверку
        if args.check == "format":
            results = {"checks": {"black": checker.check_black_formatting(), "isort": checker.check_isort_imports()}}
        elif args.check == "lint":
            results = {"checks": {"flake8": checker.check_flake8_linting(), "pylint": checker.check_pylint_analysis()}}
        elif args.check == "type":
            results = {"checks": {"mypy": checker.check_mypy_typing()}}
        elif args.check == "security":
            results = {"checks": {"security": checker.check_security_issues()}}
        elif args.check == "coverage":
            results = {"checks": {"coverage": checker.check_test_coverage()}}
    
    # Выводим результаты
    checker.print_results()
    
    # Сохраняем результаты
    if args.save:
        checker.save_results()
    
    # Возвращаем код выхода
    overall_score = results.get("overall_score", 0)
    if overall_score >= 80:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()