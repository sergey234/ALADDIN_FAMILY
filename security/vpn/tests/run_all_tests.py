#!/usr/bin/env python3
"""
ALADDIN VPN - Test Runner
Запуск всех тестов VPN системы

Автор: ALADDIN Security Team
Версия: 1.0.0
Дата: 01.10.2025
"""

import unittest
import sys
import os
import time
import json
from datetime import datetime
from io import StringIO

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# ============================================================================
# КОНФИГУРАЦИЯ ТЕСТОВ
# ============================================================================

class TestConfig:
    """Конфигурация тестов"""
    
    # Типы тестов
    UNIT_TESTS = "unit"
    INTEGRATION_TESTS = "integration"
    E2E_TESTS = "e2e"
    PERFORMANCE_TESTS = "performance"
    
    # Уровни детализации
    QUIET = 0
    NORMAL = 1
    VERBOSE = 2
    
    # Форматы вывода
    TEXT = "text"
    JSON = "json"
    HTML = "html"

class TestRunner:
    """Запуск тестов"""
    
    def __init__(self, config: TestConfig = None):
        self.config = config or TestConfig()
        self.results = {}
        self.start_time = None
        self.end_time = None
    
    def discover_tests(self, test_type: str = None) -> unittest.TestSuite:
        """Обнаружение тестов"""
        test_dir = os.path.join(os.path.dirname(__file__), test_type or "")
        
        if not os.path.exists(test_dir):
            return unittest.TestSuite()
        
        loader = unittest.TestLoader()
        suite = loader.discover(
            start_dir=test_dir,
            pattern="test_*.py",
            top_level_dir=os.path.dirname(__file__)
        )
        
        return suite
    
    def run_unit_tests(self) -> dict:
        """Запуск unit тестов"""
        print("🧪 Запуск Unit тестов...")
        
        suite = self.discover_tests(TestConfig.UNIT_TESTS)
        result = self._run_test_suite(suite, "Unit Tests")
        
        self.results["unit"] = result
        return result
    
    def run_integration_tests(self) -> dict:
        """Запуск интеграционных тестов"""
        print("🔗 Запуск Integration тестов...")
        
        suite = self.discover_tests(TestConfig.INTEGRATION_TESTS)
        result = self._run_test_suite(suite, "Integration Tests")
        
        self.results["integration"] = result
        return result
    
    def run_e2e_tests(self) -> dict:
        """Запуск E2E тестов"""
        print("🌐 Запуск E2E тестов...")
        
        suite = self.discover_tests(TestConfig.E2E_TESTS)
        result = self._run_test_suite(suite, "E2E Tests")
        
        self.results["e2e"] = result
        return result
    
    def run_performance_tests(self) -> dict:
        """Запуск performance тестов"""
        print("⚡ Запуск Performance тестов...")
        
        suite = self.discover_tests(TestConfig.PERFORMANCE_TESTS)
        result = self._run_test_suite(suite, "Performance Tests")
        
        self.results["performance"] = result
        return result
    
    def _run_test_suite(self, suite: unittest.TestSuite, test_name: str) -> dict:
        """Запуск набора тестов"""
        if suite.countTestCases() == 0:
            return {
                "name": test_name,
                "tests_run": 0,
                "failures": 0,
                "errors": 0,
                "skipped": 0,
                "success_rate": 100.0,
                "duration": 0.0,
                "status": "no_tests"
            }
        
        # Захватываем вывод
        stream = StringIO()
        runner = unittest.TextTestRunner(
            stream=stream,
            verbosity=2 if self.config.verbosity == TestConfig.VERBOSE else 1
        )
        
        # Запускаем тесты
        start_time = time.time()
        result = runner.run(suite)
        end_time = time.time()
        
        # Собираем результаты
        test_result = {
            "name": test_name,
            "tests_run": result.testsRun,
            "failures": len(result.failures),
            "errors": len(result.errors),
            "skipped": len(result.skipped) if hasattr(result, 'skipped') else 0,
            "success_rate": ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 100.0,
            "duration": end_time - start_time,
            "status": "passed" if len(result.failures) == 0 and len(result.errors) == 0 else "failed",
            "output": stream.getvalue(),
            "failure_details": [{"test": str(test), "traceback": traceback} for test, traceback in result.failures],
            "error_details": [{"test": str(test), "traceback": traceback} for test, traceback in result.errors]
        }
        
        return test_result
    
    def run_all_tests(self) -> dict:
        """Запуск всех тестов"""
        print("🚀 Запуск всех тестов ALADDIN VPN...")
        print("=" * 60)
        
        self.start_time = time.time()
        
        # Запускаем все типы тестов
        self.run_unit_tests()
        self.run_integration_tests()
        self.run_e2e_tests()
        self.run_performance_tests()
        
        self.end_time = time.time()
        
        # Собираем общую статистику
        total_tests = sum(result["tests_run"] for result in self.results.values())
        total_failures = sum(result["failures"] for result in self.results.values())
        total_errors = sum(result["errors"] for result in self.results.values())
        total_duration = self.end_time - self.start_time
        
        overall_result = {
            "summary": {
                "total_tests": total_tests,
                "total_failures": total_failures,
                "total_errors": total_errors,
                "total_skipped": sum(result["skipped"] for result in self.results.values()),
                "success_rate": ((total_tests - total_failures - total_errors) / total_tests * 100) if total_tests > 0 else 100.0,
                "total_duration": total_duration,
                "status": "passed" if total_failures == 0 and total_errors == 0 else "failed"
            },
            "test_results": self.results,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return overall_result
    
    def print_results(self, results: dict):
        """Вывод результатов тестов"""
        print("\n" + "=" * 60)
        print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
        print("=" * 60)
        
        # Общая статистика
        summary = results["summary"]
        print(f"\n📈 Общая статистика:")
        print(f"   Всего тестов: {summary['total_tests']}")
        print(f"   Успешно: {summary['total_tests'] - summary['total_failures'] - summary['total_errors']}")
        print(f"   Неудачно: {summary['total_failures']}")
        print(f"   Ошибок: {summary['total_errors']}")
        print(f"   Пропущено: {summary['total_skipped']}")
        print(f"   Процент успеха: {summary['success_rate']:.1f}%")
        print(f"   Время выполнения: {summary['total_duration']:.2f}с")
        
        # Статус
        status_emoji = "✅" if summary['status'] == 'passed' else "❌"
        print(f"\n🎯 Общий статус: {status_emoji} {summary['status'].upper()}")
        
        # Детали по типам тестов
        print(f"\n📋 Детали по типам тестов:")
        for test_type, result in results["test_results"].items():
            status_emoji = "✅" if result['status'] == 'passed' else "❌"
            print(f"   {test_type.upper()}: {status_emoji} {result['tests_run']} тестов, {result['success_rate']:.1f}% успех, {result['duration']:.2f}с")
        
        # Детали ошибок
        if summary['total_failures'] > 0 or summary['total_errors'] > 0:
            print(f"\n❌ Детали ошибок:")
            for test_type, result in results["test_results"].items():
                if result['failures'] > 0:
                    print(f"\n   {test_type.upper()} - Неудачи:")
                    for failure in result['failure_details']:
                        print(f"     • {failure['test']}")
                
                if result['errors'] > 0:
                    print(f"\n   {test_type.upper()} - Ошибки:")
                    for error in result['error_details']:
                        print(f"     • {error['test']}")
    
    def save_results(self, results: dict, filename: str = None):
        """Сохранение результатов в файл"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_results_{timestamp}.json"
        
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Результаты сохранены в: {filepath}")
        return filepath

# ============================================================================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================================================================

def main():
    """Главная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ALADDIN VPN Test Runner")
    parser.add_argument("--type", choices=["unit", "integration", "e2e", "performance", "all"], 
                       default="all", help="Тип тестов для запуска")
    parser.add_argument("--verbosity", type=int, choices=[0, 1, 2], default=1,
                       help="Уровень детализации вывода")
    parser.add_argument("--output", choices=["text", "json", "html"], default="text",
                       help="Формат вывода результатов")
    parser.add_argument("--save", action="store_true", help="Сохранить результаты в файл")
    parser.add_argument("--coverage", action="store_true", help="Запустить с анализом покрытия")
    
    args = parser.parse_args()
    
    # Создаем конфигурацию
    config = TestConfig()
    config.verbosity = args.verbosity
    config.output_format = args.output
    
    # Создаем runner
    runner = TestRunner(config)
    
    # Запускаем тесты
    if args.type == "all":
        results = runner.run_all_tests()
    elif args.type == "unit":
        results = {"test_results": {"unit": runner.run_unit_tests()}}
    elif args.type == "integration":
        results = {"test_results": {"integration": runner.run_integration_tests()}}
    elif args.type == "e2e":
        results = {"test_results": {"e2e": runner.run_e2e_tests()}}
    elif args.type == "performance":
        results = {"test_results": {"performance": runner.run_performance_tests()}}
    
    # Выводим результаты
    if args.output == "text":
        runner.print_results(results)
    elif args.output == "json":
        print(json.dumps(results, indent=2, ensure_ascii=False))
    
    # Сохраняем результаты
    if args.save:
        runner.save_results(results)
    
    # Возвращаем код выхода
    summary = results.get("summary", {})
    if summary.get("status") == "passed":
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()