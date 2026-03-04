#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Безопасный Универсальный Анализатор Качества
ТОЛЬКО АНАЛИЗ - НЕ ИЗМЕНЯЕТ КОД АВТОМАТИЧЕСКИ
"""

import ast
# import json  # TODO: Добавить при реализации JSON функций
import os
# import re  # TODO: Добавить при реализации regex функций
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class SafetyLevel(Enum):
    """Уровни безопасности для исправлений"""

    SAFE = "safe"  # Безопасно для автоматического исправления
    MANUAL = "manual"  # Требует ручного одобрения
    DANGEROUS = "dangerous"  # Опасно для автоматического исправления
    CRITICAL = "critical"  # Критично для безопасности


@dataclass
class QualityIssue:
    """Проблема качества кода"""

    line_number: int
    issue_type: str
    description: str
    safety_level: SafetyLevel
    suggested_fix: Optional[str] = None
    auto_fixable: bool = False
    security_impact: str = "none"


@dataclass
class SecurityCheck:
    """Проверка безопасности"""

    function_name: str
    is_security_function: bool
    has_encryption: bool
    has_authentication: bool
    has_validation: bool
    has_logging: bool
    risk_level: str


class SafeQualityAnalyzer:
    """Безопасный анализатор качества кода"""

    def __init__(self):
        self.logger = self._setup_logging()
        self.security_keywords = [
            "encrypt",
            "decrypt",
            "hash",
            "password",
            "token",
            "auth",
            "permission",
            "access",
            "security",
            "validate",
            "sanitize",
            "audit",
            "log",
            "monitor",
            "threat",
            "vulnerability",
        ]
        self.critical_functions = [
            "authenticate",
            "authorize",
            "encrypt",
            "decrypt",
            "validate",
            "sanitize",
            "audit",
            "log_security",
            "check_permissions",
        ]

    def _setup_logging(self):
        """Настройка логирования"""
        import logging

        logger = logging.getLogger("SafeQualityAnalyzer")
        logger.setLevel(logging.INFO)
        return logger

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Главная функция анализа файла - ТОЛЬКО АНАЛИЗ"""
        try:
            self.logger.info(f"🔍 Начинаем анализ файла: {file_path}")

            # Проверяем существование файла
            if not os.path.exists(file_path):
                return {"error": f"Файл не найден: {file_path}"}

            # Читаем файл
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Выполняем все проверки
            analysis_result = {
                "file_path": file_path,
                "timestamp": datetime.now().isoformat(),
                "file_size": os.path.getsize(file_path),
                "line_count": len(content.splitlines()),
                "analysis": {
                    "syntax_check": self._check_syntax(file_path),
                    "import_check": self._check_imports(file_path),
                    "flake8_analysis": self._analyze_flake8(file_path),
                    "security_analysis": self._analyze_security(content),
                    "performance_analysis": self._analyze_performance(content),
                    "code_structure": self._analyze_structure(content),
                    "documentation": self._analyze_documentation(content),
                },
                "suggestions": self._generate_safe_suggestions(
                    file_path, content
                ),
                "safety_report": self._generate_safety_report(
                    file_path, content
                ),
                "recommendations": self._generate_recommendations(
                    file_path, content
                ),
            }

            self.logger.info(f"✅ Анализ завершен для файла: {file_path}")
            return analysis_result

        except Exception as e:
            self.logger.error(f"❌ Ошибка анализа файла {file_path}: {e}")
            return {"error": str(e)}

    def _check_syntax(self, file_path: str) -> Dict[str, Any]:
        """Проверка синтаксиса Python"""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", file_path],
                capture_output=True,
                text=True,
                timeout=30,
            )

            return {
                "status": "success" if result.returncode == 0 else "error",
                "error_message": (
                    result.stderr if result.returncode != 0 else None
                ),
                "safe_to_fix": result.returncode == 0,
            }
        except Exception as e:
            return {
                "status": "error",
                "error_message": str(e),
                "safe_to_fix": False,
            }

    def _check_imports(self, file_path: str) -> Dict[str, Any]:
        """Проверка импортов"""
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    f"import {file_path.replace('/', '.').replace('.py', '')}",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            return {
                "status": "success" if result.returncode == 0 else "error",
                "error_message": (
                    result.stderr if result.returncode != 0 else None
                ),
                "safe_to_fix": result.returncode == 0,
            }
        except Exception as e:
            return {
                "status": "error",
                "error_message": str(e),
                "safe_to_fix": False,
            }

    def _analyze_flake8(self, file_path: str) -> Dict[str, Any]:
        """Анализ flake8 - ТОЛЬКО АНАЛИЗ"""
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "flake8",
                    file_path,
                    "--format=%(path)s:%(row)d:%(col)d: %(code)s %(text)s",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            errors = []
            if result.stdout:
                for line in result.stdout.strip().split("\n"):
                    if line:
                        parts = line.split(":", 3)
                        if len(parts) >= 4:
                            errors.append(
                                {
                                    "line": int(parts[1]),
                                    "column": int(parts[2]),
                                    "code": parts[3].split()[0],
                                    "message": (
                                        parts[3].split(" ", 1)[1]
                                        if len(parts[3].split()) > 1
                                        else ""
                                    ),
                                    "safety_level": self._get_safety_level(
                                        parts[3].split()[0]
                                    ),
                                    "auto_fixable": self._is_auto_fixable(
                                        parts[3].split()[0]
                                    ),
                                }
                            )

            return {
                "total_errors": len(errors),
                "errors": errors,
                "safe_errors": [
                    e for e in errors if e["safety_level"] == SafetyLevel.SAFE
                ],
                "manual_errors": [
                    e
                    for e in errors
                    if e["safety_level"] == SafetyLevel.MANUAL
                ],
                "dangerous_errors": [
                    e
                    for e in errors
                    if e["safety_level"] == SafetyLevel.DANGEROUS
                ],
                "critical_errors": [
                    e
                    for e in errors
                    if e["safety_level"] == SafetyLevel.CRITICAL
                ],
            }
        except Exception as e:
            return {"total_errors": 0, "errors": [], "error_message": str(e)}

    def _analyze_security(self, content: str) -> Dict[str, Any]:
        """Анализ безопасности - НЕ ИЗМЕНЯЕТ КОД"""
        security_issues = []
        security_functions = []

        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            line_lower = line.lower()

            # Проверяем на наличие ключевых слов безопасности
            for keyword in self.security_keywords:
                if keyword in line_lower:
                    security_functions.append(
                        {
                            "line": i,
                            "keyword": keyword,
                            "context": line.strip(),
                        }
                    )

            # Проверяем на потенциальные уязвимости
            if "eval(" in line_lower:
                security_issues.append(
                    {
                        "line": i,
                        "type": "dangerous_eval",
                        "description": "Использование eval() может быть "
                        "опасно",
                        "severity": "high",
                    }
                )

            if "exec(" in line_lower:
                security_issues.append(
                    {
                        "line": i,
                        "type": "dangerous_exec",
                        "description": "Использование exec() может быть "
                        "опасно",
                        "severity": "high",
                    }
                )

            if "subprocess.call(" in line_lower and "shell=True" in line_lower:
                security_issues.append(
                    {
                        "line": i,
                        "type": "shell_injection",
                        "description": "Потенциальная уязвимость shell "
                        "injection",
                        "severity": "critical",
                    }
                )

        return {
            "security_functions_found": len(security_functions),
            "security_functions": security_functions,
            "security_issues": security_issues,
            "total_issues": len(security_issues),
            "critical_issues": len(
                [i for i in security_issues if i["severity"] == "critical"]
            ),
        }

    def _analyze_performance(self, content: str) -> Dict[str, Any]:
        """Анализ производительности"""
        performance_issues = []

        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            line_lower = line.lower()

            # Проверяем на неэффективные конструкции
            if "for i in range(len(" in line_lower:
                performance_issues.append(
                    {
                        "line": i,
                        "type": "inefficient_loop",
                        "description": "Использование range(len()) "
                        "неэффективно",
                        "suggestion": "Используйте enumerate() или "
                        "прямую итерацию",
                    }
                )

            if ".keys()" in line_lower and "for" in line_lower:
                performance_issues.append(
                    {
                        "line": i,
                        "type": "unnecessary_keys",
                        "description": "Не нужно вызывать .keys() для "
                        "итерации по словарю",
                        "suggestion": "Итерируйтесь напрямую по словарю",
                    }
                )

        return {
            "performance_issues": performance_issues,
            "total_issues": len(performance_issues),
        }

    def _analyze_structure(self, content: str) -> Dict[str, Any]:
        """Анализ структуры кода"""
        try:
            tree = ast.parse(content)

            classes = []
            functions = []

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(
                        {
                            "name": node.name,
                            "line": node.lineno,
                            "methods": [
                                n.name
                                for n in node.body
                                if isinstance(n, ast.FunctionDef)
                            ],
                        }
                    )
                elif isinstance(node, ast.FunctionDef):
                    functions.append(
                        {
                            "name": node.name,
                            "line": node.lineno,
                            "args": [arg.arg for arg in node.args.args],
                            "is_async": isinstance(node, ast.AsyncFunctionDef),
                        }
                    )

            return {
                "classes": classes,
                "functions": functions,
                "total_classes": len(classes),
                "total_functions": len(functions),
            }
        except Exception as e:
            return {
                "error": str(e),
                "classes": [],
                "functions": [],
                "total_classes": 0,
                "total_functions": 0,
            }

    def _analyze_documentation(self, content: str) -> Dict[str, Any]:
        """Анализ документации"""
        lines = content.split("\n")
        docstring_lines = 0
        comment_lines = 0
        total_lines = len(lines)

        in_docstring = False
        docstring_quote = None

        for line in lines:
            stripped = line.strip()

            # Подсчет комментариев
            if stripped.startswith("#"):
                comment_lines += 1

            # Подсчет docstring
            if '"""' in line or "'''" in line:
                if not in_docstring:
                    in_docstring = True
                    docstring_quote = '"""' if '"""' in line else "'''"
                elif docstring_quote in line:
                    in_docstring = False
                    docstring_quote = None

            if in_docstring:
                docstring_lines += 1

        return {
            "total_lines": total_lines,
            "comment_lines": comment_lines,
            "docstring_lines": docstring_lines,
            "comment_percentage": (
                (comment_lines / total_lines * 100) if total_lines > 0 else 0
            ),
            "docstring_percentage": (
                (docstring_lines / total_lines * 100) if total_lines > 0 else 0
            ),
        }

    def _get_safety_level(self, error_code: str) -> SafetyLevel:
        """Определение уровня безопасности для ошибки flake8"""
        safe_codes = ["E501", "W293", "W292", "E302", "E305", "E128", "E129"]
        manual_codes = ["F401", "F841", "E302", "E305"]
        dangerous_codes = ["F403", "F405", "F811", "F812"]
        critical_codes = ["F999"]  # Пользовательские критические ошибки

        if error_code in safe_codes:
            return SafetyLevel.SAFE
        elif error_code in manual_codes:
            return SafetyLevel.MANUAL
        elif error_code in dangerous_codes:
            return SafetyLevel.DANGEROUS
        elif error_code in critical_codes:
            return SafetyLevel.CRITICAL
        else:
            return SafetyLevel.MANUAL

    def _is_auto_fixable(self, error_code: str) -> bool:
        """Определение возможности автоматического исправления"""
        auto_fixable_codes = [
            "E501",
            "W293",
            "W292",
            "E302",
            "E305",
            "E128",
            "E129",
        ]
        return error_code in auto_fixable_codes

    def _generate_safe_suggestions(
        self, file_path: str, content: str
    ) -> Dict[str, Any]:
        """Генерация БЕЗОПАСНЫХ предложений по исправлению"""
        suggestions = {
            "safe_formatting": [],
            "manual_review_needed": [],
            "security_recommendations": [],
            "performance_optimizations": [],
        }

        # Анализируем flake8 ошибки
        flake8_result = self._analyze_flake8(file_path)

        for error in flake8_result.get("errors", []):
            if error["safety_level"] == SafetyLevel.SAFE:
                suggestions["safe_formatting"].append(
                    {
                        "line": error["line"],
                        "code": error["code"],
                        "message": error["message"],
                        "suggested_fix": self._get_safe_fix_suggestion(
                            error["code"]
                        ),
                    }
                )
            else:
                suggestions["manual_review_needed"].append(
                    {
                        "line": error["line"],
                        "code": error["code"],
                        "message": error["message"],
                        "reason": "Требует ручного анализа безопасности",
                    }
                )

        return suggestions

    def _get_safe_fix_suggestion(self, error_code: str) -> str:
        """Получение безопасного предложения по исправлению"""
        suggestions = {
            "E501": "Разбейте длинную строку на несколько строк",
            "W293": "Удалите пробелы в конце строки",
            "W292": "Добавьте перевод строки в конце файла",
            "E302": "Добавьте 2 пустые строки перед определением "
            "функции/класса",
            "E305": "Добавьте 2 пустые строки после определения "
            "функции/класса",
            "E128": "Исправьте отступы в параметрах функции",
            "E129": "Исправьте отступы в параметрах функции",
        }
        return suggestions.get(error_code, "Требует ручного анализа")

    def _generate_safety_report(
        self, file_path: str, content: str
    ) -> Dict[str, Any]:
        """Генерация отчета о безопасности"""
        security_analysis = self._analyze_security(content)

        return {
            "security_functions_preserved": True,  # Мы не изменяем код
            "encryption_intact": True,  # Мы не изменяем код
            "authentication_preserved": True,  # Мы не изменяем код
            "validation_intact": True,  # Мы не изменяем код
            "logging_preserved": True,  # Мы не изменяем код
            "security_issues_found": security_analysis["total_issues"],
            "critical_issues": security_analysis["critical_issues"],
            "recommendation": "Код не изменен - безопасность сохранена",
        }

    def _generate_recommendations(
        self, file_path: str, content: str
    ) -> List[str]:
        """Генерация рекомендаций по улучшению"""
        recommendations = []

        # Анализируем flake8
        flake8_result = self._analyze_flake8(file_path)
        if flake8_result["total_errors"] > 0:
            recommendations.append(
                f"Исправьте {flake8_result['total_errors']} ошибок flake8"
            )

        # Анализируем документацию
        doc_analysis = self._analyze_documentation(content)
        if doc_analysis["comment_percentage"] < 10:
            recommendations.append("Добавьте больше комментариев к коду")

        if doc_analysis["docstring_percentage"] < 5:
            recommendations.append("Добавьте docstrings к функциям и классам")

        # Анализируем производительность
        perf_analysis = self._analyze_performance(content)
        if perf_analysis["total_issues"] > 0:
            recommendations.append("Оптимизируйте производительность кода")

        return recommendations

    def generate_report(self, analysis_result: Dict[str, Any]) -> str:
        """Генерация текстового отчета"""
        report = []
        report.append("=" * 60)
        report.append("🛡️ БЕЗОПАСНЫЙ АНАЛИЗ КАЧЕСТВА КОДА")
        report.append("=" * 60)
        report.append(f"📁 Файл: {analysis_result['file_path']}")
        report.append(f"⏰ Время анализа: {analysis_result['timestamp']}")
        report.append(f"📊 Размер файла: {analysis_result['file_size']} байт")
        report.append(f"📏 Строк кода: {analysis_result['line_count']}")
        report.append("")

        # Синтаксис
        syntax = analysis_result["analysis"]["syntax_check"]
        report.append("🔍 ПРОВЕРКА СИНТАКСИСА:")
        status_text = ("✅ Успешно" if syntax['status'] == 'success'
                       else "❌ Ошибка")
        report.append(f"   Статус: {status_text}")
        if syntax["error_message"]:
            report.append(f"   Ошибка: {syntax['error_message']}")
        report.append("")

        # Импорты
        imports = analysis_result["analysis"]["import_check"]
        report.append("📦 ПРОВЕРКА ИМПОРТОВ:")
        status_text = ("✅ Успешно" if imports['status'] == 'success'
                       else "❌ Ошибка")
        report.append(f"   Статус: {status_text}")
        if imports["error_message"]:
            report.append(f"   Ошибка: {imports['error_message']}")
        report.append("")

        # Flake8
        flake8 = analysis_result["analysis"]["flake8_analysis"]
        report.append("🔧 АНАЛИЗ FLAKE8:")
        report.append(f"   Всего ошибок: {flake8['total_errors']}")
        report.append(
            f"   Безопасных для исправления: "
            f"{len(flake8.get('safe_errors', []))}"
        )
        report.append(
            f"   Требуют ручного анализа: "
            f"{len(flake8.get('manual_errors', []))}"
        )
        report.append(f"   Опасных: {len(flake8.get('dangerous_errors', []))}")
        report.append(
            f"   Критических: {len(flake8.get('critical_errors', []))}"
        )
        report.append("")

        # Безопасность
        safety = analysis_result["safety_report"]
        report.append("🛡️ ОТЧЕТ О БЕЗОПАСНОСТИ:")
        report.append(
            f"   Функции безопасности сохранены: "
            f"{'✅' if safety['security_functions_preserved'] else '❌'}"
        )
        report.append(
            f"   Шифрование не затронуто: "
            f"{'✅' if safety['encryption_intact'] else '❌'}"
        )
        report.append(
            f"   Аутентификация сохранена: "
            f"{'✅' if safety['authentication_preserved'] else '❌'}"
        )
        report.append(
            f"   Валидация не затронута: "
            f"{'✅' if safety['validation_intact'] else '❌'}"
        )
        report.append(
            f"   Логирование сохранено: "
            f"{'✅' if safety['logging_preserved'] else '❌'}"
        )
        report.append(
            f"   Проблем безопасности найдено: "
            f"{safety['security_issues_found']}"
        )
        report.append(f"   Критических проблем: {safety['critical_issues']}")
        report.append("")

        # Рекомендации
        recommendations = analysis_result["recommendations"]
        if recommendations:
            report.append("💡 РЕКОМЕНДАЦИИ:")
            for i, rec in enumerate(recommendations, 1):
                report.append(f"   {i}. {rec}")
            report.append("")

        report.append("🎯 ЗАКЛЮЧЕНИЕ:")
        report.append("   ✅ Код проанализирован БЕЗОПАСНО")
        report.append("   ✅ Никаких изменений не внесено")
        report.append("   ✅ Безопасность системы сохранена")
        report.append("   ✅ Предложения по улучшению предоставлены")
        report.append("")
        report.append("=" * 60)

        return "\n".join(report)


# Глобальный экземпляр
safe_quality_analyzer = SafeQualityAnalyzer()


def analyze_file_safely(file_path: str) -> Dict[str, Any]:
    """Безопасный анализ файла - ТОЛЬКО АНАЛИЗ"""
    return safe_quality_analyzer.analyze_file(file_path)


def generate_quality_report(file_path: str) -> str:
    """Генерация отчета о качестве"""
    analysis = analyze_file_safely(file_path)
    return safe_quality_analyzer.generate_report(analysis)


if __name__ == "__main__":
    # Тестирование
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        print("🛡️ БЕЗОПАСНЫЙ АНАЛИЗ КАЧЕСТВА КОДА")
        print("=" * 50)
        print(f"Анализируем файл: {file_path}")
        print()

        result = analyze_file_safely(file_path)
        if "error" in result:
            print(f"❌ Ошибка: {result['error']}")
        else:
            report = generate_quality_report(file_path)
            print(report)
    else:
        print("Использование: python3 safe_quality_analyzer.py <путь_к_файлу>")
