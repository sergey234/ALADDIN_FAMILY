#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performance Tests Runner для ALADDIN Dashboard
Запуск всех тестов производительности и интеграции

Автор: ALADDIN Security Team
Версия: 1.0.0
Дата: 2025-01-27
Качество: A+
"""

# import asyncio  # Не используется
import os
import subprocess
import sys
import time
from datetime import datetime
# from pathlib import Path  # Не используется
from typing import Any, Dict, List  # Optional не используется


class PerformanceTestRunner:
    """Запускатель тестов производительности"""

    def __init__(self):
        """Инициализация запускателя тестов"""
        self.start_time = datetime.now()
        self.test_results: List[Dict[str, Any]] = []
        self.test_files = [
            "tests/test_load_performance.py",
            "tests/test_dashboard_performance.py",
            "tests/test_sfm_integration.py",
            "tests/test_memory_optimization.py",
            "tests/test_response_time_optimization.py",
            "tests/test_memory_profiling.py",
            "tests/test_cache_optimization.py",
            "tests/test_sfm_advanced_integration.py",
            "tests/test_sfm_function_lifecycle.py",
            "tests/test_sfm_security_integration.py",
            "tests/test_sfm_monitoring_integration.py",
            "tests/test_sfm_api_integration.py",
            "tests/test_dashboard_v2_endpoints.py",
            "tests/test_dashboard_integration.py",
            "tests/test_dashboard_new_features.py",
        ]

    def check_prerequisites(self) -> bool:
        """
        Проверка предварительных условий

        Returns:
            True если все условия выполнены
        """
        print("🔍 Проверка предварительных условий...")

        # Проверяем наличие Python
        try:
            python_version = sys.version_info
            print(
                f"✅ Python версия: {python_version.major}.{python_version.minor}.{python_version.micro}"
            )

            if python_version < (3, 8):
                print("❌ Требуется Python 3.8 или выше")
                return False

        except Exception as e:
            print(f"❌ Ошибка проверки Python: {e}")
            return False

        # Проверяем наличие pip
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "--version"],
                check=True,
                capture_output=True,
            )
            print("✅ pip доступен")
        except subprocess.CalledProcessError:
            print("❌ pip недоступен")
            return False

        # Проверяем наличие pytest
        try:
            subprocess.run(
                [sys.executable, "-m", "pytest", "--version"],
                check=True,
                capture_output=True,
            )
            print("✅ pytest доступен")
        except subprocess.CalledProcessError:
            print("⚠️ pytest не установлен - будет установлен автоматически")

        # Проверяем наличие файлов тестов
        for test_file in self.test_files:
            if os.path.exists(test_file):
                print(f"✅ Файл теста найден: {test_file}")
            else:
                print(f"❌ Файл теста не найден: {test_file}")
                return False

        print("✅ Все предварительные условия выполнены")
        return True

    def install_dependencies(self) -> bool:
        """
        Установка зависимостей для тестирования

        Returns:
            True если установка прошла успешно
        """
        print("\n📦 Установка зависимостей для тестирования...")

        requirements_files = ["requirements-test.txt", "requirements.txt"]

        for req_file in requirements_files:
            if os.path.exists(req_file):
                try:
                    print(f"📦 Установка зависимостей из {req_file}...")
                    result = subprocess.run(
                        [
                            sys.executable,
                            "-m",
                            "pip",
                            "install",
                            "-r",
                            req_file,
                        ],
                        capture_output=True,
                        text=True,
                    )

                    if result.returncode == 0:
                        print(f"✅ Зависимости из {req_file} установлены")
                    else:
                        print(
                            f"⚠️ Предупреждения при установке {req_file}: {result.stderr}"
                        )

                except Exception as e:
                    print(f"❌ Ошибка установки {req_file}: {e}")
                    return False
            else:
                print(f"⚠️ Файл {req_file} не найден")

        print("✅ Установка зависимостей завершена")
        return True

    def run_single_test(self, test_file: str) -> Dict[str, Any]:
        """
        Запуск одного теста

        Args:
            test_file: Путь к файлу теста

        Returns:
            Результат выполнения теста
        """
        print(f"\n🧪 Запуск теста: {test_file}")

        start_time = time.time()

        try:
            # Запускаем тест через pytest
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    test_file,
                    "-v",
                    "--tb=short",
                    "--html=reports/"
                    + os.path.basename(test_file).replace(
                        ".py", "_report.html"
                    ),
                    "--self-contained-html",
                ],
                capture_output=True,
                text=True,
                timeout=300,
            )  # 5 минут таймаут

            duration = time.time() - start_time

            test_result = {
                "test_file": test_file,
                "success": result.returncode == 0,
                "duration": duration,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
            }

            if result.returncode == 0:
                print(
                    f"✅ Тест {test_file} выполнен успешно за {duration:.2f}s"
                )
            else:
                print(
                    f"❌ Тест {test_file} завершился с ошибкой за {duration:.2f}s"
                )
                print(f"Ошибка: {result.stderr[:200]}...")

            return test_result

        except subprocess.TimeoutExpired:
            print(f"⏰ Тест {test_file} превысил время ожидания (5 минут)")
            return {
                "test_file": test_file,
                "success": False,
                "duration": 300,
                "error": "Timeout",
                "return_code": -1,
            }

        except Exception as e:
            print(f"❌ Ошибка запуска теста {test_file}: {e}")
            return {
                "test_file": test_file,
                "success": False,
                "duration": 0,
                "error": str(e),
                "return_code": -1,
            }

    def run_all_tests(self) -> bool:
        """
        Запуск всех тестов

        Returns:
            True если все тесты прошли успешно
        """
        print("\n🚀 Запуск всех тестов производительности...")

        # Создаем директорию для отчетов
        os.makedirs("reports", exist_ok=True)

        all_success = True

        for test_file in self.test_files:
            result = self.run_single_test(test_file)
            self.test_results.append(result)

            if not result["success"]:
                all_success = False

        return all_success

    def generate_summary_report(self) -> Dict[str, Any]:
        """
        Генерация сводного отчета

        Returns:
            Сводный отчет
        """
        print("\n📊 Генерация сводного отчета...")

        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - successful_tests

        total_duration = sum(r["duration"] for r in self.test_results)

        report = {
            "test_run_date": self.start_time.isoformat(),
            "total_duration": total_duration,
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "success_rate": (
                successful_tests / total_tests * 100 if total_tests > 0 else 0
            ),
            "test_results": self.test_results,
            "summary": {
                "overall_status": (
                    "PASS" if successful_tests == total_tests else "FAIL"
                ),
                "performance_grade": self._calculate_performance_grade(),
                "recommendations": self._generate_recommendations(),
            },
        }

        return report

    def _calculate_performance_grade(self) -> str:
        """Расчет оценки производительности"""
        if not self.test_results:
            return "N/A"

        success_rate = sum(1 for r in self.test_results if r["success"]) / len(
            self.test_results
        )

        if success_rate >= 0.95:
            return "A+"
        elif success_rate >= 0.90:
            return "A"
        elif success_rate >= 0.80:
            return "B+"
        elif success_rate >= 0.70:
            return "B"
        else:
            return "C"

    def _generate_recommendations(self) -> List[str]:
        """Генерация рекомендаций"""
        recommendations = []

        failed_tests = [r for r in self.test_results if not r["success"]]

        if failed_tests:
            recommendations.append("Исправить ошибки в неудачных тестах")

            for test in failed_tests:
                if "timeout" in test.get("error", "").lower():
                    recommendations.append(
                        f"Оптимизировать производительность {test['test_file']}"
                    )
                elif "connection" in test.get("stderr", "").lower():
                    recommendations.append(
                        f"Проверить доступность сервисов для {test['test_file']}"
                    )

        successful_tests = [r for r in self.test_results if r["success"]]
        slow_tests = [r for r in successful_tests if r["duration"] > 60]

        if slow_tests:
            recommendations.append("Оптимизировать медленные тесты")

        if not recommendations:
            recommendations.append(
                "Все тесты выполнены успешно - система готова к продакшн"
            )

        return recommendations

    def save_report(self, report: Dict[str, Any]) -> str:
        """
        Сохранение отчета

        Args:
            report: Отчет для сохранения

        Returns:
            Путь к сохраненному файлу
        """
        import json

        report_file = f"reports/performance_test_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)

        print(f"✅ Сводный отчет сохранен: {report_file}")
        return report_file

    def print_final_summary(self, report: Dict[str, Any]):
        """
        Вывод финальной сводки

        Args:
            report: Сводный отчет
        """
        print("\n" + "=" * 60)
        print("📊 ФИНАЛЬНАЯ СВОДКА ТЕСТОВ ПРОИЗВОДИТЕЛЬНОСТИ")
        print("=" * 60)

        print(f"📅 Дата выполнения: {report['test_run_date']}")
        print(f"⏱️ Общее время: {report['total_duration']:.2f} секунд")
        print(f"🧪 Всего тестов: {report['total_tests']}")
        print(f"✅ Успешных: {report['successful_tests']}")
        print(f"❌ Неудачных: {report['failed_tests']}")
        print(f"📈 Процент успеха: {report['success_rate']:.1f}%")
        print(f"🎯 Общая оценка: {report['summary']['overall_status']}")
        print(
            f"⭐ Оценка производительности: {report['summary']['performance_grade']}"
        )

        print("\n📋 РЕКОМЕНДАЦИИ:")
        for i, rec in enumerate(report["summary"]["recommendations"], 1):
            print(f"  {i}. {rec}")

        print("\n" + "=" * 60)

        if report["summary"]["overall_status"] == "PASS":
            print("🎉 ВСЕ ТЕСТЫ ВЫПОЛНЕНЫ УСПЕШНО!")
            print("🚀 Система готова к продакшн!")
        else:
            print("⚠️ ЕСТЬ ПРОБЛЕМЫ, ТРЕБУЮЩИЕ ВНИМАНИЯ")
            print("🔧 Рекомендуется исправить ошибки перед продакшн")

        print("=" * 60)


def main():
    """Главная функция запуска тестов"""
    print("🚀 ALADDIN Dashboard Performance Tests Runner")
    print("📊 Тестирование производительности и интеграции")
    print("🛡️ Проверка готовности к продакшн")
    print("=" * 60)

    runner = PerformanceTestRunner()

    try:
        # Проверяем предварительные условия
        if not runner.check_prerequisites():
            print("❌ Предварительные условия не выполнены")
            return False

        # Устанавливаем зависимости
        if not runner.install_dependencies():
            print("❌ Ошибка установки зависимостей")
            return False

        # Запускаем все тесты
        all_success = runner.run_all_tests()

        # Генерируем отчет
        report = runner.generate_summary_report()

        # Сохраняем отчет
        # report_file = runner.save_report(report)  # Не используется

        # Выводим финальную сводку
        runner.print_final_summary(report)

        return all_success

    except KeyboardInterrupt:
        print("\n⏹️ Тестирование прервано пользователем")
        return False

    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
