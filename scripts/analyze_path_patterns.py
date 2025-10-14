#!/usr/bin/env python3
"""
Анализ паттернов путей в SFM реестре
Выясняет, почему были созданы именно такие пути
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

def load_sfm_registry() -> Dict:
    """Загружает SFM реестр из JSON файла"""
    registry_path = Path("data/sfm/function_registry.json")
    
    if not registry_path.exists():
        print(f"❌ Файл реестра не найден: {registry_path}")
        return {}
    
    try:
        with open(registry_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('functions', {})
    except Exception as e:
        print(f"❌ Ошибка загрузки реестра: {e}")
        return {}

def analyze_path_patterns():
    """Анализирует паттерны путей в SFM реестре"""
    print("🔍 АНАЛИЗ ПАТТЕРНОВ ПУТЕЙ В SFM РЕЕСТРЕ")
    print("=" * 70)
    
    # Загружаем реестр
    functions = load_sfm_registry()
    if not functions:
        print("❌ Не удалось загрузить SFM реестр")
        return
    
    base_dir = Path.cwd()
    print(f"📁 Базовая директория: {base_dir}")
    print(f"📊 Всего функций в реестре: {len(functions)}")
    print()
    
    # Анализируем паттерны
    path_patterns = {
        'underscore_vs_camelcase': {'underscore': 0, 'camelcase': 0, 'mixed': 0},
        'directory_structure': {},
        'naming_conventions': {},
        'file_extensions': {},
        'creation_dates': {},
        'function_types': {}
    }
    
    existing_files = []
    missing_files = []
    path_analysis = []
    
    for func_id, func_data in functions.items():
        file_path_str = func_data.get('file_path', '')
        if not file_path_str:
            continue
        
        # Нормализуем путь
        if file_path_str.startswith('./'):
            file_path_str = file_path_str[2:]
        
        normalized_path = base_dir / file_path_str
        file_exists = normalized_path.exists() and normalized_path.is_file()
        
        # Анализируем паттерн имени файла
        file_name = Path(file_path_str).name
        file_stem = Path(file_path_str).stem
        
        # Проверяем стиль именования
        if '_' in file_stem:
            path_patterns['underscore_vs_camelcase']['underscore'] += 1
            naming_style = 'underscore'
        elif any(c.isupper() for c in file_stem[1:]):
            path_patterns['underscore_vs_camelcase']['camelcase'] += 1
            naming_style = 'camelcase'
        else:
            path_patterns['underscore_vs_camelcase']['mixed'] += 1
            naming_style = 'mixed'
        
        # Анализируем структуру директорий
        dir_path = str(Path(file_path_str).parent)
        if dir_path not in path_patterns['directory_structure']:
            path_patterns['directory_structure'][dir_path] = 0
        path_patterns['directory_structure'][dir_path] += 1
        
        # Анализируем типы функций
        func_type = func_data.get('function_type', 'unknown')
        if func_type not in path_patterns['function_types']:
            path_patterns['function_types'][func_type] = {'total': 0, 'existing': 0, 'missing': 0}
        path_patterns['function_types'][func_type]['total'] += 1
        
        if file_exists:
            path_patterns['function_types'][func_type]['existing'] += 1
            existing_files.append(func_id)
        else:
            path_patterns['function_types'][func_type]['missing'] += 1
            missing_files.append(func_id)
        
        # Анализируем даты создания
        created_at = func_data.get('created_at', '')
        if created_at:
            date_part = created_at[:10]  # YYYY-MM-DD
            if date_part not in path_patterns['creation_dates']:
                path_patterns['creation_dates'][date_part] = 0
            path_patterns['creation_dates'][date_part] += 1
        
        # Сохраняем анализ для детального изучения
        path_analysis.append({
            'function_id': func_id,
            'file_path': file_path_str,
            'file_name': file_name,
            'file_stem': file_stem,
            'naming_style': naming_style,
            'directory': dir_path,
            'function_type': func_type,
            'exists': file_exists,
            'created_at': created_at,
            'status': func_data.get('status', 'unknown')
        })
    
    # Выводим результаты анализа
    print("📊 АНАЛИЗ ПАТТЕРНОВ ИМЕНОВАНИЯ:")
    print("-" * 70)
    
    naming_stats = path_patterns['underscore_vs_camelcase']
    total_naming = sum(naming_stats.values())
    
    print(f"📝 Стили именования файлов:")
    print(f"   Подчеркивания (_): {naming_stats['underscore']:3d} ({naming_stats['underscore']/total_naming*100:.1f}%)")
    print(f"   CamelCase:         {naming_stats['camelcase']:3d} ({naming_stats['camelcase']/total_naming*100:.1f}%)")
    print(f"   Смешанный:         {naming_stats['mixed']:3d} ({naming_stats['mixed']/total_naming*100:.1f}%)")
    
    print(f"\n📂 СТРУКТУРА ДИРЕКТОРИЙ:")
    print("-" * 70)
    
    sorted_dirs = sorted(path_patterns['directory_structure'].items(), key=lambda x: x[1], reverse=True)
    for dir_path, count in sorted_dirs[:15]:  # Показываем топ-15
        print(f"   {dir_path:30} | {count:3d} файлов")
    
    print(f"\n📊 СТАТИСТИКА ПО ТИПАМ ФУНКЦИЙ:")
    print("-" * 70)
    
    for func_type, stats in sorted(path_patterns['function_types'].items()):
        existing_pct = (stats['existing'] / stats['total'] * 100) if stats['total'] > 0 else 0
        print(f"   {func_type:20} | Всего: {stats['total']:3d} | Существуют: {stats['existing']:3d} ({existing_pct:5.1f}%)")
    
    print(f"\n📅 РАСПРЕДЕЛЕНИЕ ПО ДАТАМ СОЗДАНИЯ:")
    print("-" * 70)
    
    sorted_dates = sorted(path_patterns['creation_dates'].items(), reverse=True)
    for date, count in sorted_dates[:10]:  # Показываем последние 10 дат
        print(f"   {date} | {count:3d} функций")
    
    # Анализируем проблемные паттерны
    print(f"\n🔍 АНАЛИЗ ПРОБЛЕМНЫХ ПАТТЕРНОВ:")
    print("-" * 70)
    
    # Ищем функции с неправильными путями
    problematic_patterns = {
        'missing_underscores': [],
        'wrong_directories': [],
        'camelcase_files': [],
        'old_paths': []
    }
    
    for analysis in path_analysis:
        if not analysis['exists']:
            # Анализируем, почему файл не найден
            if analysis['naming_style'] == 'camelcase':
                problematic_patterns['camelcase_files'].append(analysis)
            elif 'security' in analysis['directory'] and analysis['function_type'] in ['ai_agent', 'bot', 'manager']:
                # Возможно, файл в неправильной директории
                expected_dirs = {
                    'ai_agent': 'security/ai_agents',
                    'bot': 'security/bots',
                    'manager': 'security/managers'
                }
                expected_dir = expected_dirs.get(analysis['function_type'])
                if expected_dir and expected_dir not in analysis['directory']:
                    problematic_patterns['wrong_directories'].append(analysis)
    
    print(f"❌ Проблемные паттерны:")
    print(f"   CamelCase файлы: {len(problematic_patterns['camelcase_files'])}")
    print(f"   Неправильные директории: {len(problematic_patterns['wrong_directories'])}")
    
    # Показываем примеры проблемных паттернов
    if problematic_patterns['camelcase_files']:
        print(f"\n🔸 ПРИМЕРЫ CAMELCASE ФАЙЛОВ:")
        for analysis in problematic_patterns['camelcase_files'][:5]:
            print(f"   {analysis['function_id']} → {analysis['file_path']}")
    
    if problematic_patterns['wrong_directories']:
        print(f"\n🔸 ПРИМЕРЫ НЕПРАВИЛЬНЫХ ДИРЕКТОРИЙ:")
        for analysis in problematic_patterns['wrong_directories'][:5]:
            print(f"   {analysis['function_id']} → {analysis['file_path']} (тип: {analysis['function_type']})")
    
    # Анализируем эволюцию системы
    print(f"\n📈 ЭВОЛЮЦИЯ СИСТЕМЫ:")
    print("-" * 70)
    
    # Группируем по периодам создания
    periods = {
        '2025-09-01 - 2025-09-10': 0,
        '2025-09-11 - 2025-09-20': 0,
        '2025-09-21 - 2025-09-30': 0,
        '2025-10-01 - 2025-10-10': 0
    }
    
    for date_str, count in path_patterns['creation_dates'].items():
        if '2025-09-01' <= date_str <= '2025-09-10':
            periods['2025-09-01 - 2025-09-10'] += count
        elif '2025-09-11' <= date_str <= '2025-09-20':
            periods['2025-09-11 - 2025-09-20'] += count
        elif '2025-09-21' <= date_str <= '2025-09-30':
            periods['2025-09-21 - 2025-09-30'] += count
        elif '2025-10-01' <= date_str <= '2025-10-10':
            periods['2025-10-01 - 2025-10-10'] += count
    
    for period, count in periods.items():
        print(f"   {period} | {count:3d} функций")
    
    # Сохраняем детальный анализ
    analysis_report = {
        'timestamp': datetime.now().isoformat(),
        'total_functions': len(functions),
        'existing_files': len(existing_files),
        'missing_files': len(missing_files),
        'path_patterns': path_patterns,
        'path_analysis': path_analysis,
        'problematic_patterns': {
            key: [{'function_id': item['function_id'], 'file_path': item['file_path']} 
                  for item in items] 
            for key, items in problematic_patterns.items()
        }
    }
    
    report_path = f"data/reports/path_patterns_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(analysis_report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 Детальный анализ сохранен: {report_path}")
    
    return analysis_report

if __name__ == "__main__":
    try:
        analysis_report = analyze_path_patterns()
        print(f"\n🎯 АНАЛИЗ ПАТТЕРНОВ ЗАВЕРШЕН")
    except Exception as e:
        print(f"❌ Ошибка выполнения: {e}")
        import traceback
        traceback.print_exc()