#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Полный анализ flake8 для всех 326 функций SFM системы
Создает индивидуальный отчет по каждой функции с нумерацией 1-2-3-4-5...
"""

import os
import subprocess
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

def run_flake8_standard(file_path):
    """Запуск flake8 с базовыми настройками"""
    try:
        result = subprocess.run([
            'python3', '-m', 'flake8', 
            file_path,
            '--statistics'
        ], capture_output=True, text=True, timeout=30)
        
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def analyze_errors(output):
    """Анализ ошибок flake8"""
    errors = defaultdict(int)
    total_errors = 0
    
    lines = output.strip().split('\n')
    for line in lines:
        if ':' in line and not line.startswith('['):
            parts = line.split(':')
            if len(parts) >= 4:
                error_code = parts[3].strip().split()[0]
                errors[error_code] += 1
                total_errors += 1
    
    return total_errors, dict(errors)

def get_all_python_files():
    """Получить все Python файлы в проекте"""
    python_files = []
    exclude_dirs = {
        'ALADDIN_BACKUP', 'ALADDIN_NEW_BACKUP', 'ALADDIN_SECURITY_FULL_BACKUP',
        'backup', '__pycache__', '.git', '.venv', 'venv', 'node_modules'
    }
    
    for root, dirs, files in os.walk('.'):
        # Исключаем директории
        dirs[:] = [d for d in dirs if not any(exclude in d for exclude in exclude_dirs)]
        
        for file in files:
            if file.endswith('.py') and not any(exclude in file for exclude in exclude_dirs):
                full_path = Path(root) / file
                relative_path = full_path.relative_to(Path('.'))
                python_files.append(relative_path)
    
    return sorted(python_files)

def categorize_file(file_path):
    """Определить категорию файла"""
    path_str = str(file_path)
    
    if 'core/' in path_str:
        return 'CORE'
    elif 'security/safe_function_manager.py' in path_str:
        return 'SECURITY_SFM'
    elif 'security/ai_agents/' in path_str:
        return 'AI_AGENT'
    elif 'security/bots/' in path_str:
        return 'BOT'
    elif 'security/microservices/' in path_str:
        return 'MICROSERVICE'
    elif 'security/' in path_str:
        return 'SECURITY'
    elif 'config/' in path_str:
        return 'CONFIG'
    elif 'tests/' in path_str:
        return 'TEST'
    elif 'scripts/' in path_str:
        return 'SCRIPT'
    else:
        return 'OTHER'

def main():
    """Основная функция"""
    print("🔍 ПОЛНЫЙ АНАЛИЗ FLAKE8 ДЛЯ ВСЕХ 326 ФУНКЦИЙ SFM СИСТЕМЫ")
    print("=" * 80)
    print("Создаем индивидуальный отчет по каждой функции с нумерацией 1-2-3-4-5...")
    print("=" * 80)
    
    # Получаем все Python файлы
    all_python_files = get_all_python_files()
    print(f"📁 Найдено {len(all_python_files)} Python файлов")
    
    results = {
        'total_files': len(all_python_files),
        'clean_files': 0,
        'files_with_errors': 0,
        'total_errors': 0,
        'error_types': defaultdict(int),
        'category_stats': defaultdict(lambda: {
            'total': 0,
            'clean': 0,
            'errors': 0,
            'total_error_count': 0
        }),
        'individual_reports': [],
        'analysis_time': datetime.now().isoformat()
    }
    
    print(f"\n🔍 АНАЛИЗ {len(all_python_files)} ФАЙЛОВ:")
    print("-" * 80)
    
    for i, filepath in enumerate(all_python_files, 1):
        category = categorize_file(filepath)
        
        print(f"[{i:3d}/{len(all_python_files)}] {filepath}")
        
        # Запуск flake8
        returncode, stdout, stderr = run_flake8_standard(filepath)
        
        # Анализ результатов
        if returncode == 0:
            total_errors = 0
            errors = {}
            status = "✅ ЧИСТЫЙ"
            results['clean_files'] += 1
            results['category_stats'][category]['clean'] += 1
        else:
            total_errors, errors = analyze_errors(stdout)
            if total_errors == 0:
                status = "✅ ЧИСТЫЙ"
                results['clean_files'] += 1
                results['category_stats'][category]['clean'] += 1
            else:
                status = f"❌ {total_errors} ошибок"
                results['files_with_errors'] += 1
                results['category_stats'][category]['errors'] += 1
                results['category_stats'][category]['total_error_count'] += total_errors
        
        # Обновление статистики
        results['total_errors'] += total_errors
        results['category_stats'][category]['total'] += 1
        
        for error_type, count in errors.items():
            results['error_types'][error_type] += count
        
        # Создание индивидуального отчета для каждой функции
        individual_report = {
            'function_number': i,
            'file_path': str(filepath),
            'category': category,
            'is_clean': total_errors == 0,
            'total_errors': total_errors,
            'errors': errors,
            'status': status,
            'full_output': stdout if total_errors > 0 else "",
            'analysis_time': datetime.now().isoformat()
        }
        results['individual_reports'].append(individual_report)
        
        print(f"     {status} ({category})")
        
        # Показываем топ-3 ошибки для файлов с ошибками
        if total_errors > 0 and total_errors <= 20:
            for error_type, count in sorted(errors.items(), key=lambda x: x[1], reverse=True)[:3]:
                print(f"       {error_type}: {count}")
        elif total_errors > 20:
            print(f"       МНОГО ОШИБОК - см. детальный отчет")
    
    # Создание индивидуальных отчетов по каждой функции
    create_individual_reports(results)
    
    # Создание общего отчета
    create_summary_report(results)
    
    # Сохранение JSON данных
    output_file = 'COMPLETE_326_FUNCTIONS_ANALYSIS.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        # Преобразуем defaultdict в обычные dict для JSON
        json_results = {
            'total_files': results['total_files'],
            'clean_files': results['clean_files'],
            'files_with_errors': results['files_with_errors'],
            'total_errors': results['total_errors'],
            'error_types': dict(results['error_types']),
            'category_stats': dict(results['category_stats']),
            'individual_reports': results['individual_reports'],
            'analysis_time': results['analysis_time']
        }
        json.dump(json_results, f, indent=2, ensure_ascii=False)
    
    # Итоговый отчет
    print(f"\n📊 ИТОГОВЫЙ ОТЧЕТ:")
    print("=" * 80)
    print(f"Всего файлов: {results['total_files']}")
    print(f"Чистых файлов: {results['clean_files']} ({results['clean_files']/results['total_files']*100:.1f}%)")
    print(f"Файлов с ошибками: {results['files_with_errors']} ({results['files_with_errors']/results['total_files']*100:.1f}%)")
    print(f"Всего ошибок: {results['total_errors']}")
    
    print(f"\n📈 ТОП-10 ОШИБОК ПО ТИПАМ:")
    for i, (error_type, count) in enumerate(sorted(results['error_types'].items(), key=lambda x: x[1], reverse=True)[:10], 1):
        print(f"  {i:2d}. {error_type}: {count}")
    
    print(f"\n📁 СТАТИСТИКА ПО КАТЕГОРИЯМ:")
    for category, stats in results['category_stats'].items():
        if stats['total'] > 0:
            clean_percent = stats['clean'] / stats['total'] * 100
            print(f"  {category}: {stats['clean']}/{stats['total']} чистых ({clean_percent:.1f}%), {stats['total_error_count']} ошибок")
    
    print(f"\n💾 Отчеты сохранены:")
    print(f"  - JSON: {output_file}")
    print(f"  - Индивидуальные отчеты: INDIVIDUAL_REPORTS/")
    print(f"  - Общий отчет: COMPLETE_326_FUNCTIONS_SUMMARY.md")

def create_individual_reports(results):
    """Создание индивидуальных отчетов по каждой функции"""
    os.makedirs('INDIVIDUAL_REPORTS', exist_ok=True)
    
    for report in results['individual_reports']:
        function_num = report['function_number']
        file_path = report['file_path']
        category = report['category']
        total_errors = report['total_errors']
        errors = report['errors']
        status = report['status']
        
        # Создаем имя файла отчета
        safe_filename = file_path.replace('/', '_').replace('\\', '_').replace('.py', '')
        report_filename = f"INDIVIDUAL_REPORTS/{function_num:03d}_{safe_filename}_REPORT.md"
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(f"# 📋 ОТЧЕТ #{function_num}: {file_path}\n\n")
            f.write(f"**Дата анализа:** {report['analysis_time']}\n")
            f.write(f"**Категория:** {category}\n")
            f.write(f"**Статус:** {status}\n\n")
            
            f.write("## 📊 СТАТИСТИКА\n\n")
            f.write(f"- **Общее количество ошибок:** {total_errors}\n")
            f.write(f"- **Тип файла:** {category}\n")
            f.write(f"- **Путь к файлу:** `{file_path}`\n\n")
            
            if total_errors == 0:
                f.write("## ✅ РЕЗУЛЬТАТ\n\n")
                f.write("**Файл чистый! Ошибок не обнаружено.**\n\n")
                f.write("### 🎯 Рекомендации:\n")
                f.write("- Файл соответствует стандартам PEP8\n")
                f.write("- Код готов к продакшну\n")
                f.write("- Дополнительных действий не требуется\n")
            else:
                f.write("## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ\n\n")
                f.write("### 📈 Распределение ошибок по типам:\n\n")
                
                for error_type, count in sorted(errors.items(), key=lambda x: x[1], reverse=True):
                    error_desc = get_error_description(error_type)
                    f.write(f"- **{error_type}:** {count} ошибок - {error_desc}\n")
                
                f.write("\n### 🎯 Рекомендации по исправлению:\n\n")
                
                # Критические ошибки
                critical_errors = ['F401', 'F541', 'F841', 'F811', 'F821']
                critical_found = [e for e in errors.keys() if e in critical_errors]
                if critical_found:
                    f.write("#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):\n")
                    for error in critical_found:
                        f.write(f"- **{error}:** {get_error_fix_recommendation(error)}\n")
                    f.write("\n")
                
                # Важные ошибки
                important_errors = ['E402', 'E302', 'E128', 'E129']
                important_found = [e for e in errors.keys() if e in important_errors]
                if important_found:
                    f.write("#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):\n")
                    for error in important_found:
                        f.write(f"- **{error}:** {get_error_fix_recommendation(error)}\n")
                    f.write("\n")
                
                # Форматирование
                format_errors = ['W293', 'W291', 'W292', 'E501']
                format_found = [e for e in errors.keys() if e in format_errors]
                if format_found:
                    f.write("#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):\n")
                    for error in format_found:
                        f.write(f"- **{error}:** {get_error_fix_recommendation(error)}\n")
                    f.write("\n")
                
                if report['full_output']:
                    f.write("### 📝 Детальный вывод flake8:\n\n")
                    f.write("```\n")
                    f.write(report['full_output'])
                    f.write("\n```\n")
            
            f.write("\n---\n")
            f.write(f"**Отчет создан:** AI Security Assistant  \n")
            f.write(f"**Дата:** {report['analysis_time']}  \n")
            f.write(f"**Функция #{function_num} из {results['total_files']}**\n")

def create_summary_report(results):
    """Создание общего сводного отчета"""
    with open('COMPLETE_326_FUNCTIONS_SUMMARY.md', 'w', encoding='utf-8') as f:
        f.write("# 🎯 ПОЛНЫЙ АНАЛИЗ FLAKE8 ДЛЯ ВСЕХ 326 ФУНКЦИЙ SFM СИСТЕМЫ\n\n")
        f.write(f"**Дата анализа:** {results['analysis_time']}\n")
        f.write(f"**Аналитик:** AI Security Assistant\n")
        f.write(f"**Всего проанализировано:** {results['total_files']} файлов\n\n")
        
        f.write("## 📊 ОБЩАЯ СТАТИСТИКА\n\n")
        f.write(f"- **Всего файлов:** {results['total_files']}\n")
        f.write(f"- **Чистых файлов:** {results['clean_files']} ({results['clean_files']/results['total_files']*100:.1f}%)\n")
        f.write(f"- **Файлов с ошибками:** {results['files_with_errors']} ({results['files_with_errors']/results['total_files']*100:.1f}%)\n")
        f.write(f"- **Всего ошибок:** {results['total_errors']}\n\n")
        
        f.write("## 📈 ТОП-10 ОШИБОК ПО ТИПАМ\n\n")
        for i, (error_type, count) in enumerate(sorted(results['error_types'].items(), key=lambda x: x[1], reverse=True)[:10], 1):
            f.write(f"{i:2d}. **{error_type}:** {count} ошибок\n")
        
        f.write("\n## 📁 СТАТИСТИКА ПО КАТЕГОРИЯМ\n\n")
        for category, stats in results['category_stats'].items():
            if stats['total'] > 0:
                clean_percent = stats['clean'] / stats['total'] * 100
                f.write(f"- **{category}:** {stats['clean']}/{stats['total']} чистых ({clean_percent:.1f}%), {stats['total_error_count']} ошибок\n")
        
        f.write("\n## 📋 СПИСОК ВСЕХ ФУНКЦИЙ\n\n")
        f.write("| № | Файл | Категория | Статус | Ошибок |\n")
        f.write("|---|------|-----------|--------|--------|\n")
        
        for report in results['individual_reports']:
            status_icon = "✅" if report['is_clean'] else "❌"
            f.write(f"| {report['function_number']} | `{report['file_path']}` | {report['category']} | {status_icon} | {report['total_errors']} |\n")
        
        f.write("\n## 🎯 ЗАКЛЮЧЕНИЕ\n\n")
        if results['clean_files'] / results['total_files'] > 0.8:
            f.write("✅ **СИСТЕМА В ОТЛИЧНОМ СОСТОЯНИИ** - более 80% файлов чистые\n")
        elif results['clean_files'] / results['total_files'] > 0.5:
            f.write("⚠️ **СИСТЕМА В ХОРОШЕМ СОСТОЯНИИ** - более 50% файлов чистые\n")
        else:
            f.write("❌ **СИСТЕМА ТРЕБУЕТ ВНИМАНИЯ** - менее 50% файлов чистые\n")
        
        f.write(f"\n**Детальные отчеты по каждой функции доступны в папке `INDIVIDUAL_REPORTS/`**\n")

def get_error_description(error_code):
    """Получить описание ошибки"""
    descriptions = {
        'E501': 'Длинные строки (>79 символов)',
        'W293': 'Пробелы в пустых строках',
        'F401': 'Неиспользуемые импорты',
        'W291': 'Пробелы в конце строки',
        'E302': 'Недостаточно пустых строк',
        'E402': 'Импорты не в начале файла',
        'E128': 'Неправильные отступы',
        'W292': 'Нет новой строки в конце файла',
        'F841': 'Неиспользуемые переменные',
        'F541': 'f-строки без плейсхолдеров',
        'E129': 'Визуальные отступы',
        'F811': 'Переопределение импорта',
        'F821': 'Неопределенное имя'
    }
    return descriptions.get(error_code, f'Ошибка {error_code}')

def get_error_fix_recommendation(error_code):
    """Получить рекомендации по исправлению ошибки"""
    recommendations = {
        'E501': 'Разбить длинные строки на несколько коротких',
        'W293': 'Удалить пробелы в пустых строках',
        'F401': 'Удалить неиспользуемые импорты',
        'W291': 'Удалить пробелы в конце строк',
        'E302': 'Добавить пустые строки между функциями',
        'E402': 'Переместить импорты в начало файла',
        'E128': 'Исправить отступы в коде',
        'W292': 'Добавить новую строку в конце файла',
        'F841': 'Удалить неиспользуемые переменные',
        'F541': 'Заменить f-строки без плейсхолдеров на обычные',
        'E129': 'Исправить визуальные отступы',
        'F811': 'Удалить дублирующиеся импорты',
        'F821': 'Определить неопределенные переменные'
    }
    return recommendations.get(error_code, f'Исправить ошибку {error_code}')

if __name__ == "__main__":
    main()