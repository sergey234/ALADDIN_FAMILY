#!/usr/bin/env python3
"""
Скрипт проверки качества кода ALADDIN Security System
Восстановлен после создания идеального CodeQualityManager
"""

import sys
from pathlib import Path

# Добавляем корневую папку в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from core.code_quality_manager import CODE_QUALITY_MANAGER

    def main():
        """Основная функция проверки качества"""
        print("🔧 ALADDIN Security System - Проверка качества кода")
        print("=" * 60)

        # Проверяем качество проекта
        report = CODE_QUALITY_MANAGER.check_project_quality(".")

        print(f"📊 Общий балл качества: {report['overall_score']:.1f}/100")
        print(f"📁 Всего файлов: {report['total_files']}")
        print()

        print("📈 Детальные метрики:")
        metrics = report["metrics"]
        print(f"  Flake8: {metrics['flake8']:.1f}/100")
        print(f"  MyPy: {metrics['mypy']:.1f}/100")
        print(f"  Pylint: {metrics['pylint']:.1f}/10")
        print(f"  Black: {metrics['black']:.1f}/100")
        print(f"  Isort: {metrics['isort']:.1f}/100")

        # Генерируем полный отчет
        print("\n📋 Генерация полного отчета...")
        CODE_QUALITY_MANAGER.generate_quality_report(".")
        print("✅ Отчет сгенерирован!")

        return 0

    if __name__ == "__main__":
        sys.exit(main())

except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Убедитесь, что CodeQualityManager установлен")
    sys.exit(1)
except Exception as e:
    print(f"❌ Ошибка выполнения: {e}")
    sys.exit(1)
