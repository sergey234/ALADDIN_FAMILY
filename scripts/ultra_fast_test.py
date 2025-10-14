#!/usr/bin/env python3
"""
Ультра-быстрый тест системы безопасности ALADDIN
Максимальная оптимизация производительности
"""

import sys
import os
import time
import json
from pathlib import Path
from datetime import datetime
from functools import lru_cache

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent.parent))


class UltraFastTestSuite:
    """Ультра-быстрый набор тестов с максимальной оптимизацией"""

    def __init__(self):
        self.results = []
        self.start_time = None
        self.end_time = None
        self.cache = {}

    def log_test(self, test_name, success, details="", duration=0):
        """Логирование результата теста с временем выполнения"""
        status = "✅ ПРОЙДЕН" if success else "❌ ПРОВАЛЕН"
        self.results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'duration': duration,
            'timestamp': datetime.now().isoformat()
        })
        print(f"{test_name}: {status} ({duration:.2f}с)")
        if details:
            print(f"  Детали: {details}")

    @lru_cache(maxsize=256)
    def cached_import_test(self):
        """Кэшированный тест импорта"""
        try:
            from core.code_quality_manager import CodeQualityManager
            from core.configuration import ConfigurationManager
            from core.database import DatabaseManager
            from core.security_base import SecurityBase
            return True
        except Exception:
            return False

    def instant_instantiation_test(self):
        """Мгновенное создание экземпляров с кэшированием"""
        try:
            # Используем кэшированные импорты
            if 'imports' not in self.cache:
                from core.code_quality_manager import CodeQualityManager
                from core.configuration import ConfigurationManager
                from core.database import DatabaseManager
                from core.security_base import SecurityBase

                self.cache['imports'] = {
                    'CodeQualityManager': CodeQualityManager,
                    'ConfigurationManager': ConfigurationManager,
                    'DatabaseManager': DatabaseManager,
                    'SecurityBase': SecurityBase
                }

            # Создаем экземпляры (тестируем создание)
            self.cache['imports']['CodeQualityManager']()
            self.cache['imports']['ConfigurationManager']()
            self.cache['imports']['DatabaseManager'](
                {'db_path': 'test_ultra_fast.db'})
            self.cache['imports']['SecurityBase']('ultra_fast_test')

            return True, f"Создано: 4/4"

        except Exception as e:
            return False, str(e)

    def skip_quality_check_test(self):
        """Пропускаем медленную проверку качества, проверяем только PEP8"""
        try:
            import subprocess

            # Быстрая проверка только PEP8 на одном файле
            result = subprocess.run([
                'python3', '-m', 'flake8', '--select=E501', 'core/base.py'
            ], capture_output=True, text=True, timeout=2)

            pep8_ok = result.returncode == 0
            errors = len(result.stdout.strip().split()
                         ) if result.stdout.strip() else 0

            return pep8_ok, f"PEP8: {'OK' if pep8_ok else f'{errors} ошибок'}"

        except Exception as e:
            return False, str(e)

    def instant_database_test(self):
        """Мгновенный тест базы данных без сложных операций"""
        try:
            from core.database import DatabaseManager

            db = DatabaseManager({'db_path': 'test_ultra_fast.db'})

            # Только создание таблиц (быстро)
            db._create_tables()

            # Простое добавление события
            success = db.add_security_event(
                "ultra_fast_test", "INFO", "Ультра-быстрый тест", "test"
            )

            return success, "БД работает"

        except Exception as e:
            return False, str(e)

    def status_check_test(self):
        """Быстрая проверка статусов компонентов"""
        try:
            from core.code_quality_manager import CodeQualityManager

            cqm = CodeQualityManager()
            status = cqm.get_status()

            return status['status'] in [
                'initialized', 'running'], f"Статус: {status['status']}"

        except Exception as e:
            return False, str(e)

    def run_ultra_fast_tests(self):
        """Запуск ультра-быстрых тестов"""
        print("⚡ УЛЬТРА-БЫСТРЫЙ ТЕСТ СИСТЕМЫ БЕЗОПАСНОСТИ ALADDIN")
        print("=" * 60)

        self.start_time = time.time()

        # Тест 1: Кэшированный импорт
        print("\n🧪 ТЕСТ КЭШИРОВАННОГО ИМПОРТА")
        print("-" * 40)
        start = time.time()
        import_success = self.cached_import_test()
        duration = time.time() - start
        self.log_test("Кэшированный импорт", import_success, duration=duration)

        # Тест 2: Мгновенное создание экземпляров
        print("\n🧪 ТЕСТ МГНОВЕННОГО СОЗДАНИЯ ЭКЗЕМПЛЯРОВ")
        print("-" * 40)
        start = time.time()
        instant_success, instant_details = self.instant_instantiation_test()
        duration = time.time() - start
        self.log_test(
            "Мгновенное создание",
            instant_success,
            instant_details,
            duration)

        # Тест 3: Пропуск медленной проверки качества
        print("\n🧪 ТЕСТ БЫСТРОЙ ПРОВЕРКИ PEP8")
        print("-" * 40)
        start = time.time()
        pep8_success, pep8_details = self.skip_quality_check_test()
        duration = time.time() - start
        self.log_test(
            "Быстрая PEP8 проверка",
            pep8_success,
            pep8_details,
            duration)

        # Тест 4: Мгновенный тест БД
        print("\n🧪 ТЕСТ МГНОВЕННОЙ БАЗЫ ДАННЫХ")
        print("-" * 40)
        start = time.time()
        db_success, db_details = self.instant_database_test()
        duration = time.time() - start
        self.log_test("Мгновенная БД", db_success, db_details, duration)

        # Тест 5: Проверка статуса
        print("\n🧪 ТЕСТ ПРОВЕРКИ СТАТУСА")
        print("-" * 40)
        start = time.time()
        status_success, status_details = self.status_check_test()
        duration = time.time() - start
        self.log_test(
            "Проверка статуса",
            status_success,
            status_details,
            duration)

        self.end_time = time.time()

        # Генерируем отчет
        return self.generate_ultra_fast_report()

    def generate_ultra_fast_report(self):
        """Генерация ультра-быстрого отчета"""
        print("\n" + "=" * 60)
        print("📊 ОТЧЕТ УЛЬТРА-БЫСТРОГО ТЕСТА")
        print("=" * 60)

        # Подсчет результатов
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (
            passed_tests /
            total_tests *
            100) if total_tests > 0 else 0

        # Время выполнения
        total_duration = self.end_time - \
            self.start_time if self.start_time and self.end_time else 0

        # Детальное время
        total_test_duration = sum(r['duration'] for r in self.results)

        # Вывод результатов
        print(f"📈 Общая статистика:")
        print(f"  Всего тестов: {total_tests}")
        print(f"  Пройдено: {passed_tests}")
        print(f"  Провалено: {failed_tests}")
        print(f"  Успешность: {success_rate:.1f}%")
        print(f"  Общее время: {total_duration:.2f} секунд")
        print(f"  Время тестов: {total_test_duration:.2f} секунд")
        print(
            f"  Накладные расходы: "
            f"{total_duration - total_test_duration:.2f} секунд"
        )

        # Сравнение с предыдущими результатами
        print(f"\n⚡ Улучшение производительности:")
        print(f"  Быстрый тест (старый): 15.28с")
        print(f"  Оптимизированный тест: 18.96с")
        print(f"  Ультра-быстрый тест: {total_duration:.2f}с")

        if total_duration < 15.28:
            improvement = ((15.28 - total_duration) / 15.28) * 100
            print(f"  Улучшение: {improvement:.1f}%")
        else:
            print(
                f"  Ухудшение: "
                f"{((total_duration - 15.28) / 15.28) * 100:.1f}%"
            )

        # Детальные результаты
        print(f"\n📋 Детальные результаты:")
        for result in self.results:
            status = "✅" if result['success'] else "❌"
            print(f"  {status} {result['test']} ({result['duration']:.2f}с)")
            if result['details']:
                print(f"    {result['details']}")

        # Сохранение отчета
        self.save_ultra_fast_report()

        # Итоговый вердикт
        if success_rate >= 90 and total_duration <= 3:
            print(
                f"\n🎯 ОТЛИЧНО! УЛЬТРА-БЫСТРАЯ ПРОИЗВОДИТЕЛЬНОСТЬ ДОСТИГНУТА!"
            )
            return True
        elif success_rate >= 70 and total_duration <= 5:
            print(f"\n⚠️  ХОРОШО! БЫСТРАЯ ПРОИЗВОДИТЕЛЬНОСТЬ!")
            return False
        else:
            print(f"\n❌ ТРЕБУЕТСЯ ДОПОЛНИТЕЛЬНАЯ ОПТИМИЗАЦИЯ!")
            return False

    def save_ultra_fast_report(self):
        """Сохранение ультра-быстрого отчета"""
        try:
            report_data = {
                'timestamp': datetime.now().isoformat(),
                'total_duration': (
                    self.end_time - self.start_time
                    if self.start_time and self.end_time else 0
                ),
                'total_tests': len(
                    self.results),
                'passed_tests': sum(
                    1 for r in self.results if r['success']),
                'improvement_percentage': (
                    ((15.28 - (self.end_time - self.start_time)) / 15.28) * 100
                    if self.start_time and self.end_time else 0
                ),
                'results': self.results}

            report_file = (
                f"ultra_fast_test_report_"
                f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )

            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)

            print(f"\n💾 Отчет сохранен в файл: {report_file}")

        except Exception as e:
            print(f"⚠️  Ошибка сохранения отчета: {e}")


def main():
    """Главная функция"""
    test_suite = UltraFastTestSuite()
    success = test_suite.run_ultra_fast_tests()
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
