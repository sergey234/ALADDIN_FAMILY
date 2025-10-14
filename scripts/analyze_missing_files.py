#!/usr/bin/env python3
"""
Анализ отсутствующих файлов в SFM реестре
Находит все файлы, которые указаны в реестре, но не существуют в файловой системе
"""

import json
import os
import sys
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

def normalize_path(file_path: str, base_dir: Path) -> Path:
    """Нормализует путь к файлу относительно базовой директории"""
    if not file_path:
        return None
    
    # Убираем ./ в начале если есть
    if file_path.startswith('./'):
        file_path = file_path[2:]
    
    # Создаем полный путь
    full_path = base_dir / file_path
    return full_path.resolve()

def check_file_exists(file_path: Path) -> bool:
    """Проверяет существование файла"""
    if not file_path:
        return False
    return file_path.exists() and file_path.is_file()

def find_similar_files(missing_file: str, base_dir: Path) -> List[Path]:
    """Ищет похожие файлы в системе"""
    similar_files = []
    missing_name = Path(missing_file).name.lower()
    
    try:
        # Ищем файлы с похожими именами
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file.lower().endswith('.py'):
                    file_lower = file.lower()
                    if (missing_name in file_lower or 
                        file_lower.replace('_', '') in missing_name.replace('_', '') or
                        missing_name.replace('_', '') in file_lower.replace('_', '')):
                        similar_files.append(Path(root) / file)
    except Exception as e:
        print(f"⚠️ Ошибка поиска похожих файлов: {e}")
    
    return similar_files[:5]  # Возвращаем максимум 5 результатов

def analyze_missing_files():
    """Основная функция анализа отсутствующих файлов"""
    print("🔍 АНАЛИЗ ОТСУТСТВУЮЩИХ ФАЙЛОВ В SFM РЕЕСТРЕ")
    print("=" * 60)
    
    # Загружаем реестр
    functions = load_sfm_registry()
    if not functions:
        print("❌ Не удалось загрузить SFM реестр")
        return
    
    base_dir = Path.cwd()
    missing_files = []
    existing_files = []
    similar_found = {}
    
    print(f"📁 Базовая директория: {base_dir}")
    print(f"📊 Всего функций в реестре: {len(functions)}")
    print()
    
    # Проверяем каждый файл
    for func_id, func_data in functions.items():
        file_path_str = func_data.get('file_path', '')
        if not file_path_str:
            continue
            
        normalized_path = normalize_path(file_path_str, base_dir)
        
        if check_file_exists(normalized_path):
            existing_files.append((func_id, file_path_str, normalized_path))
        else:
            missing_files.append((func_id, file_path_str, normalized_path))
            
            # Ищем похожие файлы
            similar = find_similar_files(file_path_str, base_dir)
            if similar:
                similar_found[func_id] = similar
    
    # Выводим результаты
    print(f"✅ Существующие файлы: {len(existing_files)}")
    print(f"❌ Отсутствующие файлы: {len(missing_files)}")
    print()
    
    if missing_files:
        print("🔍 ОТСУТСТВУЮЩИЕ ФАЙЛЫ:")
        print("-" * 60)
        
        for i, (func_id, original_path, normalized_path) in enumerate(missing_files, 1):
            print(f"{i:3d}. {func_id}")
            print(f"     Оригинальный путь: {original_path}")
            print(f"     Нормализованный:   {normalized_path}")
            
            # Показываем похожие файлы
            if func_id in similar_found:
                print(f"     🔍 Похожие файлы найдены:")
                for similar in similar_found[func_id]:
                    rel_path = similar.relative_to(base_dir)
                    print(f"        - {rel_path}")
            print()
    
    # Статистика по типам файлов
    print("📊 СТАТИСТИКА ПО ТИПАМ ФАЙЛОВ:")
    print("-" * 60)
    
    type_stats = {}
    for func_id, func_data in functions.items():
        func_type = func_data.get('function_type', 'unknown')
        file_path_str = func_data.get('file_path', '')
        
        if func_type not in type_stats:
            type_stats[func_type] = {'total': 0, 'missing': 0, 'existing': 0}
        
        type_stats[func_type]['total'] += 1
        
        if file_path_str:
            normalized_path = normalize_path(file_path_str, base_dir)
            if check_file_exists(normalized_path):
                type_stats[func_type]['existing'] += 1
            else:
                type_stats[func_type]['missing'] += 1
    
    for func_type, stats in sorted(type_stats.items()):
        missing_pct = (stats['missing'] / stats['total'] * 100) if stats['total'] > 0 else 0
        print(f"{func_type:20} | Всего: {stats['total']:3d} | Существуют: {stats['existing']:3d} | Отсутствуют: {stats['missing']:3d} ({missing_pct:5.1f}%)")
    
    # Сохраняем отчет
    report_data = {
        'timestamp': datetime.now().isoformat(),
        'base_directory': str(base_dir),
        'total_functions': len(functions),
        'existing_files': len(existing_files),
        'missing_files': len(missing_files),
        'missing_files_details': [
            {
                'function_id': func_id,
                'original_path': original_path,
                'normalized_path': str(normalized_path),
                'similar_files': [str(s) for s in similar_found.get(func_id, [])]
            }
            for func_id, original_path, normalized_path in missing_files
        ],
        'type_statistics': type_stats
    }
    
    report_path = f"data/reports/missing_files_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 Отчет сохранен: {report_path}")
    
    return missing_files, similar_found

if __name__ == "__main__":
    try:
        missing_files, similar_found = analyze_missing_files()
        print(f"\n🎯 АНАЛИЗ ЗАВЕРШЕН")
        print(f"Найдено {len(missing_files)} отсутствующих файлов")
        print(f"Найдено {len(similar_found)} функций с похожими файлами")
    except Exception as e:
        print(f"❌ Ошибка выполнения: {e}")
        sys.exit(1)