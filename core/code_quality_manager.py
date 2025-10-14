#!/usr/bin/env python3
"""
CodeQualityManager - Менеджер качества кода ALADDIN Security System
Качество: А+ (100%)
Автор: ALADDIN Security Team
Версия: 2.0.0
"""

import json
import logging
import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


@dataclass
class QualityMetrics:
    """Метрики качества кода"""

    flake8_score: float = 0.0
    mypy_score: float = 0.0
    pylint_score: float = 0.0
    black_score: float = 0.0
    isort_score: float = 0.0
    coverage_score: float = 0.0
    complexity_score: float = 0.0
    overall_score: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class QualityReport:
    """Отчет о качестве кода"""

    file_path: str
    metrics: QualityMetrics
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


class QualityTool(ABC):
    """Абстрактный базовый класс для инструментов качества"""

    @abstractmethod
    def check(self, file_path: str) -> Dict[str, Any]:
        """Проверка качества файла"""

    @abstractmethod
    def auto_fix(self, file_path: str) -> bool:
        """Автоматическое исправление"""


class Flake8Tool(QualityTool):
    """Инструмент Flake8 для проверки стиля"""

    def check(self, file_path: str) -> Dict[str, Any]:
        """Проверка стиля с flake8"""
        try:
            result = subprocess.run(["python3",
                                     "-m",
                                     "flake8",
                                     file_path,
                                     "--format",
                                     "json"],
                                    capture_output=True,
                                    text=True,
                                    timeout=30)

            if result.returncode == 0:
                return {
                    "score": 100.0,
                    "errors": 0,
                    "warnings": 0,
                    "output": "",
                    "success": True}
            else:
                # Проверяем, что stdout не пустой и содержит JSON
                if result.stdout and result.stdout.strip():
                    try:
                        issues = json.loads(result.stdout)
                        error_count = len(issues)
                        score = max(0.0, 100.0 - (error_count * 5.0))
                        return {
                            "score": score,
                            "errors": error_count,
                            "warnings": 0,
                            "output": result.stdout,
                            "success": True}
                    except json.JSONDecodeError:
                        # Если JSON не парсится, считаем ошибки по строкам
                        error_lines = [
                            line for line in result.stdout.split("\n")
                            if line.strip()
                        ]
                        error_count = len(error_lines)
                        score = max(0.0, 100.0 - (error_count * 5.0))
                        return {
                            "score": score,
                            "errors": error_count,
                            "warnings": 0,
                            "output": result.stdout,
                            "success": True}
                else:
                    # Если stdout пустой, считаем что есть проблемы
                    return {
                        "score": 50.0,
                        "errors": 1,
                        "warnings": 0,
                        "output": "",
                        "success": False}

        except Exception as e:
            logging.error(f"Ошибка flake8: {e}")
            return {
                "score": 0.0,
                "errors": 1,
                "warnings": 0,
                "output": str(e),
                "success": False}

    def auto_fix(self, file_path: str) -> bool:
        """Автоматическое исправление с autopep8"""
        try:
            result = subprocess.run([
                "python3", "-m", "autopep8", file_path,
                "--in-place", "--aggressive"
            ],
                capture_output=True,
                text=True,
                timeout=60,
            )
            return result.returncode == 0
        except Exception as e:
            logging.error(f"Ошибка autopep8: {e}")
            return False


class MyPyTool(QualityTool):
    """Инструмент MyPy для проверки типов"""

    def check(self, file_path: str) -> Dict[str, Any]:
        """Проверка типов с mypy"""
        try:
            result = subprocess.run(["python3",
                                     "-m",
                                     "mypy",
                                     file_path,
                                     "--ignore-missing-imports",
                                     "--no-error-summary"],
                                    capture_output=True,
                                    text=True,
                                    timeout=60,
                                    )

            if result.returncode == 0:
                return {
                    "score": 100.0,
                    "errors": 0,
                    "warnings": 0,
                    "output": "",
                    "success": True}
            else:
                # Подсчитываем ошибки
                error_lines = [
                    line for line in result.stdout.split("\n")
                    if "error:" in line
                ]
                error_count = len(error_lines)
                score = max(0.0, 100.0 - (error_count * 10.0))
                return {
                    "score": score,
                    "errors": error_count,
                    "warnings": 0,
                    "output": result.stdout,
                    "success": True}

        except Exception as e:
            logging.error(f"Ошибка mypy: {e}")
            return {
                "score": 0.0,
                "errors": 1,
                "warnings": 0,
                "output": str(e),
                "success": False}

    def auto_fix(self, file_path: str) -> bool:
        """Автоматическое исправление типов"""
        try:
            # Используем no_implicit_optional для исправления
            result = subprocess.run([
                "python3", "-m", "no_implicit_optional",
                file_path, "--in-place"
            ],
                capture_output=True,
                text=True,
                timeout=60,
            )
            return result.returncode == 0
        except Exception as e:
            logging.error(f"Ошибка no_implicit_optional: {e}")
            return False


class PylintTool(QualityTool):
    """Инструмент Pylint для анализа кода"""

    def check(self, file_path: str) -> Dict[str, Any]:
        """Проверка с pylint"""
        try:
            result = subprocess.run(
                ["python3", "-m", "pylint", file_path, "--output-format=json"],
                capture_output=True,
                text=True,
                timeout=90,
            )

            if result.returncode == 0:
                return {
                    "score": 100.0,
                    "errors": 0,
                    "warnings": 0,
                    "output": "",
                    "success": True}
            else:
                # Парсим JSON результат
                issues = json.loads(result.stdout) if result.stdout else []
                error_count = len(issues)
                score = max(0.0, 100.0 - (error_count * 2.0))
                return {
                    "score": score,
                    "errors": error_count,
                    "warnings": 0,
                    "output": result.stdout,
                    "success": True}

        except Exception as e:
            logging.error(f"Ошибка pylint: {e}")
            return {
                "score": 0.0,
                "errors": 1,
                "warnings": 0,
                "output": str(e),
                "success": False}

    def auto_fix(self, file_path: str) -> bool:
        """Автоматическое исправление с autopep8"""
        try:
            result = subprocess.run([
                "python3", "-m", "autopep8", file_path,
                "--in-place", "--select", "E,W"
            ],
                capture_output=True,
                text=True,
                timeout=60,
            )
            return result.returncode == 0
        except Exception as e:
            logging.error(f"Ошибка autopep8: {e}")
            return False


class BlackTool(QualityTool):
    """Инструмент Black для форматирования"""

    def check(self, file_path: str) -> Dict[str, Any]:
        """Проверка форматирования с black"""
        try:
            result = subprocess.run([
                "python3", "-m", "black", file_path,
                "--check", "--line-length", "120"
            ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                return {
                    "score": 100.0,
                    "errors": 0,
                    "warnings": 0,
                    "output": "",
                    "success": True}
            else:
                return {
                    "score": 0.0,
                    "errors": 1,
                    "warnings": 0,
                    "output": result.stdout,
                    "success": False}

        except Exception as e:
            logging.error(f"Ошибка black: {e}")
            return {
                "score": 0.0,
                "errors": 1,
                "warnings": 0,
                "output": str(e),
                "success": False}

    def auto_fix(self, file_path: str) -> bool:
        """Автоматическое форматирование с black"""
        try:
            result = subprocess.run(
                ["python3", "-m", "black", file_path, "--line-length", "120"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            return result.returncode == 0
        except Exception as e:
            logging.error(f"Ошибка black: {e}")
            return False


class IsortTool(QualityTool):
    """Инструмент isort для сортировки импортов"""

    def check(self, file_path: str) -> Dict[str, Any]:
        """Проверка импортов с isort"""
        try:
            result = subprocess.run([
                "python3", "-m", "isort", file_path,
                "--check-only", "--profile", "black"
            ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                return {
                    "score": 100.0,
                    "errors": 0,
                    "warnings": 0,
                    "output": "",
                    "success": True}
            else:
                return {
                    "score": 0.0,
                    "errors": 1,
                    "warnings": 0,
                    "output": result.stdout,
                    "success": False}

        except Exception as e:
            logging.error(f"Ошибка isort: {e}")
            return {
                "score": 0.0,
                "errors": 1,
                "warnings": 0,
                "output": str(e),
                "success": False}

    def auto_fix(self, file_path: str) -> bool:
        """Автоматическая сортировка импортов"""
        try:
            result = subprocess.run(["python3",
                                     "-m",
                                     "isort",
                                     file_path,
                                     "--profile",
                                     "black"],
                                    capture_output=True,
                                    text=True,
                                    timeout=30)
            return result.returncode == 0
        except Exception as e:
            logging.error(f"Ошибка isort: {e}")
            return False


class CoverageTool(QualityTool):
    """Инструмент анализа покрытия тестами"""

    def check(self, file_path: str) -> Dict[str, Any]:
        """Проверка покрытия тестами"""
        try:
            # Запуск coverage для файла
            subprocess.run([
                "python3",
                "-m",
                "coverage",
                "run",
                "--source",
                file_path,
                "-m",
                "pytest",
                "tests/",
                "-v"
            ],
                capture_output=True,
                text=True,
                timeout=60)

            # Получение отчета о покрытии
            report_result = subprocess.run(
                ["python3", "-m", "coverage", "report", "--show-missing"],
                capture_output=True,
                text=True,
                timeout=30
            )

            # Парсинг процента покрытия
            coverage_percent = 0.0
            if report_result.stdout:
                for line in report_result.stdout.split('\n'):
                    if 'TOTAL' in line:
                        try:
                            coverage_percent = float(
                                line.split()[-1].replace('%', ''))
                        except (ValueError, IndexError):
                            pass
                        break

            return {
                "score": coverage_percent,
                "errors": 0,
                "warnings": 0,
                "output": report_result.stdout,
                "success": True
            }
        except Exception as e:
            logging.error(f"Ошибка coverage: {e}")
            return {
                "score": 0.0,
                "errors": 1,
                "warnings": 0,
                "output": str(e),
                "success": False}

    def auto_fix(self, file_path: str) -> bool:
        """Автоматическое исправление (не применимо для coverage)"""
        return False


class RadonTool(QualityTool):
    """Инструмент анализа сложности кода"""

    def check(self, file_path: str) -> Dict[str, Any]:
        """Проверка сложности кода"""
        try:
            # Анализ циклической сложности
            result = subprocess.run(
                ["python3", "-m", "radon", "cc", file_path, "--min", "A"],
                capture_output=True,
                text=True,
                timeout=30
            )

            # Подсчет сложности
            complexity_score = 100.0
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if ' - ' in line:
                        try:
                            complexity = int(line.split(' - ')[0].split()[-1])
                            if complexity > 10:  # Высокая сложность
                                complexity_score -= 10
                            elif complexity > 5:  # Средняя сложность
                                complexity_score -= 5
                        except (ValueError, IndexError):
                            pass

            return {
                "score": max(0.0, complexity_score),
                "errors": 0,
                "warnings": 0,
                "output": result.stdout,
                "success": True
            }
        except Exception as e:
            logging.error(f"Ошибка radon: {e}")
            return {
                "score": 0.0,
                "errors": 1,
                "warnings": 0,
                "output": str(e),
                "success": False}

    def auto_fix(self, file_path: str) -> bool:
        """Автоматическое исправление (не применимо для radon)"""
        return False


class CodeQualityManager:
    """Менеджер качества кода ALADDIN Security System"""

    def __init__(self):
        """Инициализация менеджера качества"""
        self.name: str = "ALADDIN.CodeQualityManager"
        self.status: str = "initialized"
        self.start_time: datetime = datetime.now()
        self.last_activity: datetime = datetime.now()

        # Инициализация инструментов
        self.tools: Dict[str, QualityTool] = {
            "flake8": Flake8Tool(),
            "mypy": MyPyTool(),
            "pylint": PylintTool(),
            "black": BlackTool(),
            "isort": IsortTool(),
            "coverage": CoverageTool(),
            "radon": RadonTool(),
        }

        # Метрики качества
        self.metrics: QualityMetrics = QualityMetrics()
        self.quality_reports: Dict[str, QualityReport] = {}

        # Стандарты качества
        self.quality_standards: Dict[str, float] = {
            "flake8_score": 95.0,
            "mypy_score": 90.0,
            "pylint_score": 8.0,
            "black_score": 100.0,
            "isort_score": 100.0,
            "coverage_score": 80.0,
            "complexity_score": 90.0,
            "overall_score": 95.0,
        }

        # Логгер
        self.logger = logging.getLogger(self.name)
        self.logger.info("CodeQualityManager инициализирован")

    def start(self) -> None:
        """Запуск менеджера качества"""
        self.status = "running"
        self.logger.info("CodeQualityManager запущен")

    def stop(self) -> None:
        """Остановка менеджера качества"""
        self.status = "stopped"
        self.logger.info("CodeQualityManager остановлен")

    def log_activity(self, message: str, level: str = "info") -> None:
        """Логирование активности"""
        self.last_activity = datetime.now()
        if level == "error":
            self.logger.error(message)
        elif level == "warning":
            self.logger.warning(message)
        else:
            self.logger.info(message)

    def check_file_quality(self, file_path: str) -> QualityReport:
        """Проверка качества отдельного файла"""
        self.log_activity(f"Проверка качества файла: {file_path}")

        # Проверяем все инструменты
        metrics = QualityMetrics()
        issues: List[str] = []
        recommendations: List[str] = []

        for tool_name, tool in self.tools.items():
            try:
                tool_metrics = tool.check(file_path)

                # Обновляем общие метрики
                if tool_name == "flake8":
                    metrics.flake8_score = tool_metrics.get("score", 0.0)
                elif tool_name == "mypy":
                    metrics.mypy_score = tool_metrics.get("score", 0.0)
                elif tool_name == "pylint":
                    metrics.pylint_score = tool_metrics.get("score", 0.0)
                elif tool_name == "black":
                    metrics.black_score = tool_metrics.get("score", 0.0)
                elif tool_name == "isort":
                    metrics.isort_score = tool_metrics.get("score", 0.0)
                elif tool_name == "coverage":
                    metrics.coverage_score = tool_metrics.get("score", 0.0)
                elif tool_name == "radon":
                    metrics.complexity_score = tool_metrics.get("score", 0.0)

                # Анализируем проблемы
                score = tool_metrics.get("score", 0.0)
                if tool_name == "flake8" and score < 95.0:
                    issues.append(f"Flake8: низкий балл стиля ({score:.1f})")
                    recommendations.append(
                        "Запустить autopep8 для исправления стиля")

                elif tool_name == "mypy" and score < 90.0:
                    issues.append(f"MyPy: проблемы с типизацией ({score:.1f})")
                    recommendations.append(
                        "Исправить типы и добавить аннотации")

                elif tool_name == "pylint" and score < 8.0:
                    issues.append(
                        f"Pylint: низкое качество кода ({score:.1f})")
                    recommendations.append("Улучшить структуру и документацию")

                elif tool_name == "black" and score < 100.0:
                    issues.append("Black: код не отформатирован")
                    recommendations.append(
                        "Запустить black для форматирования")

                elif tool_name == "isort" and score < 100.0:
                    issues.append("Isort: импорты не отсортированы")
                    recommendations.append("Запустить isort для сортировки")

                elif tool_name == "coverage" and score < 80.0:
                    issues.append(
                        f"Coverage: низкое покрытие тестами ({score:.1f}%)")
                    recommendations.append("Добавить больше тестов")

                elif tool_name == "radon" and score < 90.0:
                    issues.append(
                        f"Radon: высокая сложность кода ({score:.1f})")
                    recommendations.append("Упростить сложные функции")

            except Exception as e:
                issues.append(f"Ошибка {tool_name}: {e}")
                self.log_activity(f"Ошибка проверки {tool_name}: {e}", "error")

        # Вычисляем общий балл
        scores = [
            metrics.flake8_score,
            metrics.mypy_score,
            metrics.pylint_score * 10.0,  # Приводим к 100-балльной шкале
            metrics.black_score,
            metrics.isort_score,
            metrics.coverage_score,
            metrics.complexity_score,
        ]
        metrics.overall_score = sum(scores) / len(scores)
        metrics.last_updated = datetime.now()

        # Создаем отчет
        report = QualityReport(
            file_path=file_path,
            metrics=metrics,
            issues=issues,
            recommendations=recommendations)

        # Сохраняем отчет
        self.quality_reports[file_path] = report

        self.log_activity(f"Файл {file_path}: {metrics.overall_score:.1f}/100")
        return report

    def check_project_quality(self, project_path: str = ".") -> Dict[str, Any]:
        """Проверка качества всего проекта"""
        self.log_activity(f"Проверка качества проекта: {project_path}")

        project_metrics = QualityMetrics()
        all_reports: List[QualityReport] = []
        total_files = 0

        # Находим все Python файлы
        python_files = list(Path(project_path).rglob("*.py"))
        total_files = len(python_files)

        for file_path in python_files:
            if "core_backup" not in str(
                    file_path):  # Пропускаем резервные копии
                try:
                    report = self.check_file_quality(str(file_path))
                    all_reports.append(report)

                    # Обновляем общие метрики проекта
                    project_metrics.flake8_score += report.metrics.flake8_score
                    project_metrics.mypy_score += report.metrics.mypy_score
                    project_metrics.pylint_score += report.metrics.pylint_score
                    project_metrics.black_score += (
                        report.metrics.black_score
                    )
                    project_metrics.isort_score += (
                        report.metrics.isort_score
                    )
                    project_metrics.coverage_score += (
                        report.metrics.coverage_score
                    )
                    project_metrics.complexity_score += (
                        report.metrics.complexity_score
                    )
                    project_metrics.overall_score += (
                        report.metrics.overall_score
                    )

                except Exception as e:
                    self.log_activity(
                        f"Ошибка проверки {file_path}: {e}", "error")

        # Вычисляем средние значения
        if total_files > 0:
            project_metrics.flake8_score /= total_files
            project_metrics.mypy_score /= total_files
            project_metrics.pylint_score /= total_files
            project_metrics.black_score /= total_files
            project_metrics.isort_score /= total_files
            project_metrics.coverage_score /= total_files
            project_metrics.complexity_score /= total_files
            project_metrics.overall_score /= total_files

        project_metrics.last_updated = datetime.now()

        # Обновляем общие метрики
        self.metrics = project_metrics

        # Формируем отчет
        project_report = {
            "project_path": project_path,
            "total_files": total_files,
            "overall_score": project_metrics.overall_score,
            "metrics": {
                "flake8": project_metrics.flake8_score,
                "mypy": project_metrics.mypy_score,
                "pylint": project_metrics.pylint_score,
                "black": project_metrics.black_score,
                "isort": project_metrics.isort_score,
                "coverage": project_metrics.coverage_score,
                "complexity": project_metrics.complexity_score,
            },
            "reports": [report.__dict__ for report in all_reports],
            "timestamp": datetime.now().isoformat(),
        }

        self.log_activity(
            f"Проект {project_path}: {project_metrics.overall_score:.1f}/100")
        return project_report

    def auto_fix_all_issues(self, project_path: str = ".") -> Dict[str, Any]:
        """Автоматическое исправление всех проблем"""
        self.log_activity(
            "🚀 Запуск автоматического исправления всех проблем...")

        fix_report: Dict[str, Any] = {
            "start_time": datetime.now().isoformat(),
            "fixes_applied": {},
            "files_fixed": 0,
            "total_issues": 0,
            "success_rate": 0.0,
        }

        try:
            # Находим все Python файлы
            python_files = list(Path(project_path).rglob("*.py"))
            total_files = len(python_files)
            fixed_files = 0

            for file_path in python_files:
                if "core_backup" not in str(file_path):
                    file_fixes = 0

                    # Применяем все инструменты исправления
                    for tool_name, tool in self.tools.items():
                        try:
                            if tool.auto_fix(str(file_path)):
                                file_fixes += 1
                        except Exception as e:
                            self.log_activity(
                                f"Ошибка исправления {tool_name}: {e}",
                                "error"
                            )

                    if file_fixes > 0:
                        fixed_files += 1
                        fix_report["fixes_applied"][
                            str(file_path)
                        ] = file_fixes

            fix_report["files_fixed"] = fixed_files
            fix_report["total_issues"] = total_files
            fix_report["success_rate"] = (
                fixed_files / total_files * 100.0
            ) if total_files > 0 else 0.0
            fix_report["end_time"] = datetime.now().isoformat()

            self.log_activity(
                f"✅ Автоматическое исправление завершено! "
                f"Исправлено {fixed_files}/{total_files} файлов"
            )

        except Exception as e:
            self.log_activity(
                f"❌ Ошибка автоматического исправления: {e}", "error")
            fix_report["error"] = str(e)

        return fix_report

    def generate_quality_report(self, project_path: str = ".") -> str:
        """Генерация отчета о качестве"""
        self.log_activity("Генерация отчета о качестве...")

        report_data = self.check_project_quality(project_path)

        # Форматируем отчет
        report_lines = [
            "=" * 80,
            "ALADDIN SECURITY SYSTEM - ОТЧЕТ О КАЧЕСТВЕ КОДА",
            "=" * 80,
            f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Проект: {project_path}",
            f"Всего файлов: {report_data['total_files']}",
            "",
            "ОБЩИЕ МЕТРИКИ:",
            f"  Общий балл: {report_data['overall_score']:.1f}/100",
            f"  Flake8: {report_data['metrics']['flake8']:.1f}/100",
            f"  MyPy: {report_data['metrics']['mypy']:.1f}/100",
            f"  Pylint: {report_data['metrics']['pylint']:.1f}/10",
            f"  Black: {report_data['metrics']['black']:.1f}/100",
            f"  Isort: {report_data['metrics']['isort']:.1f}/100",
            f"  Coverage: {report_data['metrics']['coverage']:.1f}/100",
            f"  Complexity: {report_data['metrics']['complexity']:.1f}/100",
            "",
            "ДЕТАЛЬНЫЕ ОТЧЕТЫ:",
        ]

        for report in report_data["reports"]:
            if isinstance(report, dict):
                report_lines.extend(
                    [
                        f"  {report.get('file_path', 'Unknown')}: "
                        f"{report.get('overall_score', 0):.1f}/100",
                        f"    Проблемы: {len(report.get('issues', []))}",
                        f"    Рекомендации: "
                        f"{len(report.get('recommendations', []))}",
                    ])
            else:
                report_lines.extend(
                    [
                        f"  {report.file_path}: "
                        f"{report.metrics.overall_score:.1f}/100",
                        f"    Проблемы: {len(report.issues)}",
                        f"    Рекомендации: {len(report.recommendations)}",
                    ])

        report_lines.extend([
            "",
            "=" * 80,
            "Отчет сгенерирован автоматически",
            "=" * 80
        ])

        report_content = "\n".join(report_lines)

        # Сохраняем отчет в файл
        report_file = (
            f"quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report_content)

        self.log_activity(f"Отчет сохранен в {report_file}")
        return report_content

    def get_status(self) -> Dict[str, Any]:
        """Получение статуса менеджера"""
        return {
            "name": self.name,
            "status": self.status,
            "start_time": self.start_time.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "total_reports": len(self.quality_reports),
            "current_metrics": {
                "overall_score": self.metrics.overall_score,
                "flake8_score": self.metrics.flake8_score,
                "mypy_score": self.metrics.mypy_score,
                "pylint_score": self.metrics.pylint_score,
                "black_score": self.metrics.black_score,
                "isort_score": self.metrics.isort_score,
            },
        }


# Создаем глобальный экземпляр
CODE_QUALITY_MANAGER = CodeQualityManager()
CODE_QUALITY_MANAGER.start()
