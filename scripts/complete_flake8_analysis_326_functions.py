#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Полный анализ flake8 для всех 326 функций SFM системы
Использует правильные настройки (базовый flake8 без параметров)
"""

import os
import subprocess
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

def run_flake8_standard(file_path):
    """Запуск flake8 с базовыми настройками (как в pyproject.toml)"""
    try:
        result = subprocess.run([
            'python3', '-m', 'flake8', 
            file_path,
            '--statistics'
        ], capture_output=True, text=True, timeout=60)
        
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

def get_all_python_files(directory):
    """Получить все Python файлы в проекте"""
    python_files = []
    exclude_dirs = {
        'ALADDIN_BACKUP', 'ALADDIN_NEW_BACKUP', 'ALADDIN_SECURITY_FULL_BACKUP',
        'backup', 'test', '__pycache__', '.git', '.venv', 'venv'
    }
    
    for root, dirs, files in os.walk(directory):
        # Исключаем директории
        dirs[:] = [d for d in dirs if not any(exclude in d for exclude in exclude_dirs)]
        
        for file in files:
            if file.endswith('.py') and not any(exclude in file for exclude in exclude_dirs):
                python_files.append(Path(root) / file)
    
    return python_files

def categorize_file(file_path):
    """Определить категорию файла"""
    path_str = str(file_path)
    
    if 'core/' in path_str:
        return 'core'
    elif 'security/safe_function_manager.py' in path_str:
        return 'security_sfm'
    elif 'security/ai_agents/' in path_str:
        return 'ai_agent'
    elif 'security/bots/' in path_str:
        return 'bot'
    elif 'security/microservices/' in path_str:
        return 'microservice'
    elif 'security/' in path_str:
        return 'security'
    elif 'config/' in path_str:
        return 'config'
    elif 'tests/' in path_str:
        return 'test'
    elif 'scripts/' in path_str:
        return 'script'
    else:
        return 'other'

def main():
    """Основная функция"""
    print("🔍 ПОЛНЫЙ АНАЛИЗ FLAKE8 ДЛЯ ВСЕХ 326 ФУНКЦИЙ SFM СИСТЕМЫ")
    print("=" * 70)
    print("Используем правильные настройки: базовый flake8 (pyproject.toml)")
    print("=" * 70)
    
    project_root = Path(os.getcwd())
    
    # Получаем все Python файлы
    all_python_files = get_all_python_files(project_root)
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
        'file_details': [],
        'critical_files': [],
        'analysis_time': datetime.now().isoformat()
    }
    
    print(f"\n🔍 АНАЛИЗ {len(all_python_files)} ФАЙЛОВ:")
    print("-" * 70)
    
    for i, filepath in enumerate(all_python_files, 1):
        relative_path = filepath.relative_to(project_root)
        category = categorize_file(filepath)
        
        print(f"[{i:3d}/{len(all_python_files)}] {relative_path}")
        
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
                
                # Добавляем в критические файлы если много ошибок
                if total_errors > 50:
                    results['critical_files'].append({
                        'file': str(relative_path),
                        'category': category,
                        'errors': total_errors,
                        'error_types': errors
                    })
        
        # Обновление статистики
        results['total_errors'] += total_errors
        results['category_stats'][category]['total'] += 1
        
        for error_type, count in errors.items():
            results['error_types'][error_type] += count
        
        # Сохранение деталей
        file_detail = {
            'file_path': str(relative_path),
            'category': category,
            'is_clean': total_errors == 0,
            'total_errors': total_errors,
            'errors': errors,
            'full_output': stdout if total_errors > 0 else ""
        }
        results['file_details'].append(file_detail)
        
        print(f"     {status} ({category})")
        
        # Показываем топ-3 ошибки для файлов с ошибками
        if total_errors > 0 and total_errors <= 20:
            for error_type, count in sorted(errors.items(), key=lambda x: x[1], reverse=True)[:3]:
                print(f"       {error_type}: {count}")
        elif total_errors > 20:
            print(f"       МНОГО ОШИБОК - см. детальный отчет")
    
    # Сохранение результатов
    output_file = 'COMPLETE_FLAKE8_ANALYSIS_326_FUNCTIONS.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        # Преобразуем defaultdict в обычные dict для JSON
        json_results = {
            'total_files': results['total_files'],
            'clean_files': results['clean_files'],
            'files_with_errors': results['files_with_errors'],
            'total_errors': results['total_errors'],
            'error_types': dict(results['error_types']),
            'category_stats': dict(results['category_stats']),
            'file_details': results['file_details'],
            'critical_files': results['critical_files'],
            'analysis_time': results['analysis_time']
        }
        json.dump(json_results, f, indent=2, ensure_ascii=False)
    
    # Создание текстового отчета
    report_file = 'COMPLETE_FLAKE8_REPORT_326_FUNCTIONS.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# 🔍 ПОЛНЫЙ АНАЛИЗ FLAKE8 ДЛЯ ВСЕХ 326 ФУНКЦИЙ SFM СИСТЕМЫ\n\n")
        f.write(f"**Дата анализа:** {results['analysis_time']}\n")
        f.write(f"**Аналитик:** AI Security Assistant\n")
        f.write(f"**Настройки:** Базовый flake8 (pyproject.toml)\n\n")
        
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
        
        f.write("\n## 🚨 КРИТИЧЕСКИЕ ФАЙЛЫ (более 50 ошибок)\n\n")
        if results['critical_files']:
            for file_info in results['critical_files']:
                f.write(f"- **{file_info['file']}** ({file_info['category']}): {file_info['errors']} ошибок\n")
        else:
            f.write("Нет файлов с критическим количеством ошибок.\n")
    
    # Итоговый отчет
    print(f"\n📊 ИТОГОВЫЙ ОТЧЕТ:")
    print("=" * 70)
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
    
    print(f"\n🚨 КРИТИЧЕСКИЕ ФАЙЛЫ (более 50 ошибок):")
    if results['critical_files']:
        for file_info in results['critical_files']:
            print(f"  {file_info['file']} ({file_info['category']}): {file_info['errors']} ошибок")
    else:
        print("  Нет файлов с критическим количеством ошибок.")
    
    print(f"\n💾 Детальные отчеты сохранены:")
    print(f"  - JSON: {output_file}")
    print(f"  - Markdown: {report_file}")

if __name__ == "__main__":
    main()