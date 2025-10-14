#!/usr/bin/env python3
"""
Тесты для CodeQualityManager ALADDIN Security System
Восстановлены после создания идеального CodeQualityManager
"""

import os
import sys
import unittest
from pathlib import Path

# Добавляем корневую папку в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from core.code_quality_manager import (
        CODE_QUALITY_MANAGER,
        CodeQualityManager,
        QualityMetrics,
        QualityReport,
    )

    class TestCodeQualityManager(unittest.TestCase):
        """Тесты для CodeQualityManager"""

        def setUp(self):
            """Настройка тестов"""
            self.manager = CodeQualityManager()
            self.test_file = "test_file.py"

            # Создаем тестовый файл
            with open(self.test_file, "w") as f:
                f.write('print("Hello, World!")\n')

        def tearDown(self):
            """Очистка после тестов"""
            if os.path.exists(self.test_file):
                os.remove(self.test_file)

        def test_manager_initialization(self):
            """Тест инициализации менеджера"""
            self.assertIsNotNone(self.manager)
            self.assertEqual(self.manager.name, "ALADDIN.CodeQualityManager")
            self.assertEqual(self.manager.status, "initialized")

        def test_manager_start_stop(self):
            """Тест запуска и остановки"""
            self.manager.start()
            self.assertEqual(self.manager.status, "running")

            self.manager.stop()
            self.assertEqual(self.manager.status, "stopped")

        def test_quality_metrics(self):
            """Тест метрик качества"""
            metrics = QualityMetrics()
            self.assertEqual(metrics.flake8_score, 0.0)
            self.assertEqual(metrics.mypy_score, 0.0)
            self.assertEqual(metrics.overall_score, 0.0)

        def test_quality_report(self):
            """Тест отчета о качестве"""
            metrics = QualityMetrics(flake8_score=95.0, mypy_score=90.0)
            report = QualityReport(file_path=self.test_file, metrics=metrics, issues=[], recommendations=[])

            self.assertEqual(report.file_path, self.test_file)
            self.assertEqual(report.metrics.flake8_score, 95.0)
            self.assertEqual(len(report.issues), 0)

        def test_global_instance(self):
            """Тест глобального экземпляра"""
            self.assertIsNotNone(CODE_QUALITY_MANAGER)
            self.assertEqual(CODE_QUALITY_MANAGER.name, "ALADDIN.CodeQualityManager")

        def test_status_method(self):
            """Тест метода получения статуса"""
            status = self.manager.get_status()
            self.assertIn("name", status)
            self.assertIn("status", status)
            self.assertIn("start_time", status)

        def test_log_activity(self):
            """Тест логирования активности"""
            initial_time = self.manager.last_activity
            self.manager.log_activity("Test message")
            self.assertGreater(self.manager.last_activity, initial_time)

    def run_tests():
        """Запуск тестов"""
        print("🧪 Запуск тестов CodeQualityManager...")
        unittest.main(verbosity=2, exit=False)
        print("✅ Тесты завершены!")

    if __name__ == "__main__":
        run_tests()

except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Убедитесь, что CodeQualityManager установлен")
    sys.exit(1)
except Exception as e:
    print(f"❌ Ошибка выполнения тестов: {e}")
    sys.exit(1)
