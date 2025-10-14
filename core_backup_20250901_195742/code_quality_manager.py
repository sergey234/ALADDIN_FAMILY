# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Code Quality Manager
Менеджер контроля качества кода Python по лучшим стандартам

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from typing import Any, Dict, Optional

from .base import ComponentStatus, CoreBase


class CodeQualityManager(CoreBase):
    """Менеджер контроля качества кода Python по лучшим стандартам"""

    def __init__(self, name: str = "CodeQualityManager",
                 config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)

        # Конфигурация качества кода
        self.quality_tools = {
            "flake8": "flake8",
            "pylint": "pylint",
            "black": "black",
            "mypy": "mypy",
            "isort": "isort",
        }

        # Стандарты качества
        self.quality_standards = {
            "pep8_compliance": 95.0,  # Соответствие PEP 8
            "pylint_score": 8.0,  # Оценка pylint (0-10)
            "type_coverage": 80.0,  # Покрытие типов mypy
            "complexity_score": 7.0,  # Максимальная сложность
            "docstring_coverage": 90.0,  # Покрытие документацией
        }

        # Результаты проверок
        self.quality_reports: Dict[str, Any] = {}
        self.overall_score = 0.0
        self.status = ComponentStatus.INITIALIZING

    def initialize(self) -> bool:
        """Инициализация менеджера контроля качества"""
        try:
            self.log_activity("Инициализация менеджера контроля качества кода")
            self.status = ComponentStatus.INITIALIZING

            # Проверяем доступность инструментов
            for tool_name, tool_command in self.quality_tools.items():
                try:
                    result = subprocess.run(
                        [sys.executable, "-m", tool_command, "--version"],
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )
                    if result.returncode == 0:
                        self.log_activity(f"Инструмент {tool_name} доступен")
                    else:
                        self.log_activity(
                            f"Инструмент {tool_name} недоступен", "warning")
                except Exception as e:
                    self.log_activity(
                        f"Ошибка проверки {tool_name}: {str(e)}", "warning")

            self.status = ComponentStatus.INITIALIZING
            self.log_activity(
                "Менеджер контроля качества успешно инициализирован")
            return True

        except Exception as e:
            self.log_activity(f"Ошибка инициализации: {str(e)}", "error")
            self.status = ComponentStatus.ERROR
            return False

    def start(self) -> bool:
        """Запуск менеджера контроля качества"""
        try:
            self.log_activity("Запуск менеджера контроля качества кода")
            self.status = ComponentStatus.RUNNING
            self.start_time = datetime.now()
            self.log_activity("Менеджер контроля качества запущен")
            return True

        except Exception as e:
            self.log_activity(f"Ошибка запуска: {str(e)}", "error")
            self.status = ComponentStatus.ERROR
            return False

    def stop(self) -> bool:
        """Остановка менеджера контроля качества"""
        try:
            self.log_activity("Остановка менеджера контроля качества кода")
            self.status = ComponentStatus.STOPPED
            self.log_activity("Менеджер контроля качества остановлен")
            return True

        except Exception as e:
            self.log_activity(f"Ошибка остановки: {str(e)}", "error")
            return False

    def check_flake8_compliance(self, file_path: str) -> Dict[str, Any]:
        """Проверка соответствия PEP 8 с помощью flake8"""
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "flake8",
                    "--format=json",
                    "--max-line-length=88",  # Black стандарт
                    file_path,
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                return {
                    "status": "passed",
                    "score": 100.0,
                    "issues": 0,
                    "details": "Соответствует PEP 8",
                }
            else:
                try:
                    issues = json.loads(result.stdout)
                    issue_count = len(issues)
                    # -2 балла за каждую проблему
                    score = max(0, 100 - (issue_count * 2))

                    return {
                        "status": "failed",
                        "score": score,
                        "issues": issue_count,
                        "details": f"Найдено {issue_count} проблем с PEP 8",
                    }
                except json.JSONDecodeError:
                    return {
                        "status": "error",
                        "score": 0.0,
                        "issues": 0,
                        "details": "Ошибка парсинга flake8",
                    }

        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "score": 0.0,
                "issues": 0,
                "details": "Превышено время выполнения flake8",
            }
        except Exception as e:
            return {
                "status": "error",
                "score": 0.0,
                "issues": 0,
                "details": f"Ошибка flake8: {str(e)}",
            }

    def check_pylint_score(self, file_path: str) -> Dict[str, Any]:
        """Проверка качества кода с помощью pylint"""
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pylint",
                    "--output-format=json",
                    "--score=y",
                    "--disable=C0114,C0116",  # Отключаем проверку docstring
                    file_path,
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

            try:
                output = json.loads(result.stdout)
                if output:
                    # Извлекаем оценку из последней строки
                    last_line = result.stdout.strip().split("\n")[-1]
                    if "Your code has been rated at" in last_line:
                        score_str = last_line.split("at ")[1].split("/")[0]
                        score = float(score_str)
                    else:
                        score = 0.0

                    return {
                        "status": "completed",
                        "score": score,
                        "issues": len(output),
                        "details": f"Оценка pylint: {score}/10",
                    }
                else:
                    return {
                        "status": "completed",
                        "score": 10.0,
                        "issues": 0,
                        "details": "Отличная оценка pylint: 10/10",
                    }

            except json.JSONDecodeError:
                return {
                    "status": "error",
                    "score": 0.0,
                    "issues": 0,
                    "details": "Ошибка парсинга pylint",
                }

        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "score": 0.0,
                "issues": 0,
                "details": "Превышено время выполнения pylint",
            }
        except Exception as e:
            return {
                "status": "error",
                "score": 0.0,
                "issues": 0,
                "details": f"Ошибка pylint: {str(e)}",
            }

    def check_black_formatting(self, file_path: str) -> Dict[str, Any]:
        """Проверка форматирования кода с помощью black"""
        try:
            # Проверяем, нужно ли форматирование
            result = subprocess.run(
                [sys.executable, "-m", "black", "--check", "--diff", file_path],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                return {
                    "status": "passed",
                    "score": 100.0,
                    "issues": 0,
                    "details": "Код отформатирован по стандарту Black",
                }
            else:
                # Подсчитываем количество строк, которые нужно изменить
                diff_lines = result.stdout.count(
                    "+") + result.stdout.count("-")
                score = max(0, 100 - (diff_lines * 0.5))

                return {
                    "status": "needs_formatting",
                    "score": score,
                    "issues": diff_lines,
                    "details": f"Требуется форматирование: {diff_lines} изменений",
                }

        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "score": 0.0,
                "issues": 0,
                "details": "Превышено время выполнения black",
            }
        except Exception as e:
            return {
                "status": "error",
                "score": 0.0,
                "issues": 0,
                "details": f"Ошибка black: {str(e)}",
            }

    def check_mypy_types(self, file_path: str) -> Dict[str, Any]:
        """Проверка типов с помощью mypy"""
        try:
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "mypy",
                    "--json-report",
                    "--no-error-summary",
                    file_path,
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

            try:
                # mypy создает файл с отчетом
                report_file = "mypy-report.json"
                if os.path.exists(report_file):
                    with open(report_file, "r") as f:
                        report = json.load(f)

                    total_issues = len(
                        report.get(
                            "summary", {}).get(
                            "errors", []))
                    # -5 баллов за каждую ошибку типов
                    score = max(0, 100 - (total_issues * 5))

                    # Удаляем временный файл
                    os.remove(report_file)

                    return {
                        "status": "completed",
                        "score": score,
                        "issues": total_issues,
                        "details": f"Проверка типов: {total_issues} ошибок",
                    }
                else:
                    return {
                        "status": "completed",
                        "score": 100.0,
                        "issues": 0,
                        "details": "Проверка типов: ошибок не найдено",
                    }

            except Exception as e:
                return {
                    "status": "error",
                    "score": 0.0,
                    "issues": 0,
                    "details": f"Ошибка парсинга mypy: {str(e)}",
                }

        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "score": 0.0,
                "issues": 0,
                "details": "Превышено время выполнения mypy",
            }
        except Exception as e:
            return {
                "status": "error",
                "score": 0.0,
                "issues": 0,
                "details": f"Ошибка mypy: {str(e)}",
            }

    def check_isort_imports(self, file_path: str) -> Dict[str, Any]:
        """Проверка сортировки импортов с помощью isort"""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "isort", "--check-only", "--diff", file_path],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                return {
                    "status": "passed",
                    "score": 100.0,
                    "issues": 0,
                    "details": "Импорты отсортированы правильно",
                }
            else:
                # Подсчитываем количество строк, которые нужно изменить
                diff_lines = result.stdout.count(
                    "+") + result.stdout.count("-")
                score = max(0, 100 - (diff_lines * 0.5))

                return {
                    "status": "needs_sorting",
                    "score": score,
                    "issues": diff_lines,
                    "details": f"Требуется сортировка импортов: {diff_lines} изменений",
                }

        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "score": 0.0,
                "issues": 0,
                "details": "Превышено время выполнения isort",
            }
        except Exception as e:
            return {
                "status": "error",
                "score": 0.0,
                "issues": 0,
                "details": f"Ошибка isort: {str(e)}",
            }

    def analyze_file_quality(self, file_path: str) -> Dict[str, Any]:
        """Полный анализ качества одного файла"""
        if not file_path.endswith(".py"):
            return {
                "status": "skipped",
                "score": 0.0,
                "details": "Не Python файл"}

        self.log_activity(f"Анализ качества файла: {file_path}")

        # Проводим все проверки
        flake8_result = self.check_flake8_compliance(file_path)
        pylint_result = self.check_pylint_score(file_path)
        black_result = self.check_black_formatting(file_path)
        mypy_result = self.check_mypy_types(file_path)
        isort_result = self.check_isort_imports(file_path)

        # Вычисляем общий балл
        scores = [
            flake8_result["score"],
            pylint_result["score"] * 10,  # Приводим к 100-балльной шкале
            black_result["score"],
            mypy_result["score"],
            isort_result["score"],
        ]

        overall_score = sum(scores) / len(scores)

        return {
            "file_path": file_path,
            "overall_score": overall_score,
            "checks": {
                "flake8": flake8_result,
                "pylint": pylint_result,
                "black": black_result,
                "mypy": mypy_result,
                "isort": isort_result,
            },
            "timestamp": datetime.now().isoformat(),
        }

    def analyze_project_quality(
            self, project_path: Optional[str] = None) -> Dict[str, Any]:
        """Полный анализ качества всего проекта"""
        if project_path is None:
            project_path = os.getcwd()

        self.log_activity(f"Анализ качества проекта: {project_path}")
        self.status = ComponentStatus.RUNNING

        # Находим все Python файлы
        python_files = []
        for root, dirs, files in os.walk(project_path):
            # Исключаем системные директории
            dirs[:] = [d for d in dirs if not d.startswith(
                ".") and d not in ["__pycache__", "venv", "env"]]

            for file in files:
                if file.endswith(".py"):
                    python_files.append(os.path.join(root, file))

        self.log_activity(
            f"Найдено {len(python_files)} Python файлов для анализа")

        # Анализируем каждый файл
        file_reports = []
        total_score = 0.0

        for file_path in python_files:
            try:
                report = self.analyze_file_quality(file_path)
                file_reports.append(report)
                total_score += report["overall_score"]

                self.log_activity(
                    f"Файл {file_path}: {report['overall_score']:.1f}/100")

            except Exception as e:
                self.log_activity(
                    f"Ошибка анализа {file_path}: {str(e)}", "error")
                file_reports.append(
                    {
                        "file_path": file_path,
                        "overall_score": 0.0,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat(),
                    }
                )

        # Вычисляем общий балл проекта
        if file_reports:
            project_score = total_score / len(file_reports)
        else:
            project_score = 0.0

        # Создаем итоговый отчет
        project_report = {
            "project_path": project_path,
            "total_files": len(python_files),
            "analyzed_files": len(file_reports),
            "project_score": project_score,
            "file_reports": file_reports,
            "quality_grade": self._get_quality_grade(project_score),
            "timestamp": datetime.now().isoformat(),
        }

        self.quality_reports[project_path] = project_report
        self.overall_score = project_score

        self.log_activity(
            f"Анализ завершен. Общий балл проекта: {project_score:.1f}/100")
        self.status = ComponentStatus.RUNNING

        return project_report

    def _get_quality_grade(self, score: float) -> str:
        """Получение буквенной оценки качества"""
        if score >= 95:
            return "A+ (Отлично)"
        elif score >= 90:
            return "A (Отлично)"
        elif score >= 85:
            return "A- (Хорошо)"
        elif score >= 80:
            return "B+ (Хорошо)"
        elif score >= 75:
            return "B (Хорошо)"
        elif score >= 70:
            return "B- (Удовлетворительно)"
        elif score >= 65:
            return "C+ (Удовлетворительно)"
        elif score >= 60:
            return "C (Удовлетворительно)"
        elif score >= 55:
            return "C- (Неудовлетворительно)"
        else:
            return "F (Неудовлетворительно)"

    def get_quality_statistics(self) -> Dict[str, Any]:
        """Получение статистики качества кода"""
        return {
            "overall_score": self.overall_score,
            "quality_grade": self._get_quality_grade(self.overall_score),
            "reports_count": len(self.quality_reports),
            "last_analysis": (max(self.quality_reports.keys()) if self.quality_reports else None),
            "status": self.status.value,
        }

    def generate_quality_report(
            self, output_file: Optional[str] = None) -> str:
        """Генерация отчета о качестве кода"""
        if not self.quality_reports:
            return "Отчеты о качестве кода отсутствуют"

        # Берем последний отчет
        latest_report = max(
            self.quality_reports.values(),
            key=lambda x: x["timestamp"])

        report_content = f"""
# 📊 ОТЧЕТ О КАЧЕСТВЕ КОДА ALADDIN

**Дата анализа:** {latest_report['timestamp']}
**Проект:** {latest_report['project_path']}
**Общий балл:** {latest_report['project_score']:.1f}/100
**Оценка:** {latest_report['quality_grade']}

## 📈 СТАТИСТИКА:
- **Всего файлов:** {latest_report['total_files']}
- **Проанализировано:** {latest_report['analyzed_files']}
- **Средний балл:** {latest_report['project_score']:.1f}/100

## 🔍 ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ:
"""

        # Добавляем результаты по файлам
        # Показываем первые 10
        for file_report in latest_report["file_reports"][:10]:
            report_content += f"""
### 📁 {file_report['file_path']}
- **Балл:** {file_report['overall_score']:.1f}/100
- **Оценка:** {self._get_quality_grade(file_report['overall_score'])}
"""

            if "checks" in file_report:
                for tool, result in file_report["checks"].items():
                    report_content += f"  - **{tool.upper()}:** {result['score']:.1f}/100\n"

        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(report_content)
            return f"Отчет сохранен в {output_file}"

        return report_content


# Создаем глобальный экземпляр
CODE_QUALITY_MANAGER = CodeQualityManager()
CODE_QUALITY_MANAGER.initialize()
CODE_QUALITY_MANAGER.start()
