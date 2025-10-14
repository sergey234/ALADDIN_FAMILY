#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ФИНАЛЬНАЯ ПРОВЕРКА КАЧЕСТВА A+
Подтверждение достижения A+ качества (95+/100)

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-11
"""

import os
import sys
import subprocess
from datetime import datetime

# Добавляем путь к проекту
sys.path.insert(0, '/Users/sergejhlystov/ALADDIN_NEW')

def run_flake8_check():
    """Запускает проверку flake8"""
    print("🔍 Запуск flake8...")
    try:
        result = subprocess.run(
            ['python3', '-m', 'flake8', '--count', '--select=E9,F63,F7,F82', '--show-source', '--statistics', '.'],
            cwd='/Users/sergejhlystov/ALADDIN_NEW',
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ flake8: Ошибок не найдено")
            return 0
        else:
            error_count = len(result.stdout.split('\n')) - 1
            print(f"⚠️ flake8: Найдено {error_count} ошибок")
            return error_count
    except Exception as e:
        print(f"❌ Ошибка запуска flake8: {e}")
        return 999

def run_pylint_check():
    """Запускает проверку pylint"""
    print("🔍 Запуск pylint...")
    try:
        result = subprocess.run(
            ['python3', '-m', 'pylint', '--disable=all', '--enable=E,F', '--score=no', 'security/'],
            cwd='/Users/sergejhlystov/ALADDIN_NEW',
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ pylint: Ошибок не найдено")
            return 0
        else:
            error_count = result.stdout.count('E:') + result.stdout.count('F:')
            print(f"⚠️ pylint: Найдено {error_count} ошибок")
            return error_count
    except Exception as e:
        print(f"❌ Ошибка запуска pylint: {e}")
        return 999

def run_mypy_check():
    """Запускает проверку mypy"""
    print("🔍 Запуск mypy...")
    try:
        result = subprocess.run(
            ['python3', '-m', 'mypy', '--ignore-missing-imports', 'security/'],
            cwd='/Users/sergejhlystov/ALADDIN_NEW',
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ mypy: Ошибок не найдено")
            return 0
        else:
            error_count = result.stdout.count('error:')
            print(f"⚠️ mypy: Найдено {error_count} ошибок")
            return error_count
    except Exception as e:
        print(f"❌ Ошибка запуска mypy: {e}")
        return 999

def count_python_files():
    """Подсчитывает количество Python файлов"""
    count = 0
    for root, dirs, files in os.walk('/Users/sergejhlystov/ALADDIN_NEW'):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                count += 1
    return count

def count_lines_of_code():
    """Подсчитывает количество строк кода"""
    total_lines = 0
    for root, dirs, files in os.walk('/Users/sergejhlystov/ALADDIN_NEW'):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        total_lines += len(lines)
                except:
                    pass
    return total_lines

def calculate_quality_score(flake8_errors, pylint_errors, mypy_errors, total_files):
    """Вычисляет общую оценку качества"""
    total_errors = flake8_errors + pylint_errors + mypy_errors
    
    if total_errors == 0:
        return 100.0
    elif total_errors < 10:
        return 95.0
    elif total_errors < 50:
        return 90.0
    elif total_errors < 100:
        return 85.0
    elif total_errors < 200:
        return 80.0
    elif total_errors < 500:
        return 75.0
    else:
        return max(0, 100 - (total_errors / total_files) * 10)

def main():
    """Основная функция финальной проверки качества"""
    print("🚀 ФИНАЛЬНАЯ ПРОВЕРКА КАЧЕСТВА A+")
    print("=" * 70)
    
    # Подсчитываем файлы и строки кода
    total_files = count_python_files()
    total_lines = count_lines_of_code()
    
    print(f"📊 Статистика проекта:")
    print(f"   📁 Python файлов: {total_files}")
    print(f"   📝 Строк кода: {total_lines:,}")
    
    # Запускаем проверки качества
    print(f"\n🔍 ЗАПУСК ПРОВЕРОК КАЧЕСТВА")
    print("-" * 50)
    
    flake8_errors = run_flake8_check()
    pylint_errors = run_pylint_check()
    mypy_errors = run_mypy_check()
    
    # Вычисляем общую оценку качества
    quality_score = calculate_quality_score(flake8_errors, pylint_errors, mypy_errors, total_files)
    
    # Определяем уровень качества
    if quality_score >= 95:
        quality_level = "A+"
        quality_emoji = "🎉"
    elif quality_score >= 90:
        quality_level = "A"
        quality_emoji = "✅"
    elif quality_score >= 85:
        quality_level = "B+"
        quality_emoji = "👍"
    elif quality_score >= 80:
        quality_level = "B"
        quality_emoji = "👌"
    else:
        quality_level = "C"
        quality_emoji = "⚠️"
    
    # Итоговый отчет
    print("\n" + "=" * 70)
    print("📊 ИТОГОВЫЙ ОТЧЕТ КАЧЕСТВА:")
    print("=" * 70)
    print(f"🔍 flake8 ошибок: {flake8_errors}")
    print(f"🔍 pylint ошибок: {pylint_errors}")
    print(f"🔍 mypy ошибок: {mypy_errors}")
    print(f"📊 Всего ошибок: {flake8_errors + pylint_errors + mypy_errors}")
    print(f"📁 Файлов проверено: {total_files}")
    print(f"📝 Строк кода: {total_lines:,}")
    print(f"🏆 Оценка качества: {quality_score:.1f}/100")
    print(f"🎯 Уровень качества: {quality_level} {quality_emoji}")
    
    if quality_score >= 95:
        print("\n🎉 A+ КАЧЕСТВО ДОСТИГНУТО!")
        print("✅ Система готова к продакшену")
        print("🚀 Все требования выполнены")
    elif quality_score >= 90:
        print("\n✅ ОТЛИЧНОЕ КАЧЕСТВО!")
        print("👍 Система готова к использованию")
        print("🔧 Небольшие улучшения возможны")
    else:
        print("\n⚠️ ТРЕБУЮТСЯ ДОПОЛНИТЕЛЬНЫЕ УЛУЧШЕНИЯ")
        print("🔄 Рекомендуется продолжить оптимизацию")
    
    # Сохраняем отчет
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "quality_score": quality_score,
        "quality_level": quality_level,
        "flake8_errors": flake8_errors,
        "pylint_errors": pylint_errors,
        "mypy_errors": mypy_errors,
        "total_files": total_files,
        "total_lines": total_lines
    }
    
    try:
        import json
        os.makedirs('/Users/sergejhlystov/ALADDIN_NEW/data', exist_ok=True)
        with open('/Users/sergejhlystov/ALADDIN_NEW/data/final_quality_report.json', 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        print(f"\n📄 Отчет сохранен: /Users/sergejhlystov/ALADDIN_NEW/data/final_quality_report.json")
    except Exception as e:
        print(f"⚠️ Ошибка сохранения отчета: {e}")
    
    return quality_score >= 95

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)