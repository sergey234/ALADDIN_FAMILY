#!/usr/bin/env python3
"""
Показ всех функций с проблемными путями в SFM реестре
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Tuple

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

def find_similar_file(missing_path: str, base_dir: Path) -> Tuple[bool, str]:
    """Находит похожий файл для проблемного пути"""
    missing_name = Path(missing_path).name.lower()
    missing_stem = Path(missing_path).stem.lower()
    
    # Паттерны для поиска
    search_patterns = [
        missing_name,
        missing_stem,
        missing_name.replace('_', ''),
        missing_stem.replace('_', ''),
        missing_name.replace('_', '_'),
        missing_stem.replace('_', '_')
    ]
    
    found_files = []
    
    try:
        # Ищем файлы с похожими именами
        for root, dirs, files in os.walk(base_dir):
            # Исключаем ненужные директории
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'backups', 'scripts', 'tests', 'formatting_work']]
            
            for file in files:
                if file.lower().endswith('.py'):
                    file_lower = file.lower()
                    file_stem = Path(file).stem.lower()
                    
                    # Проверяем различные варианты совпадений
                    for pattern in search_patterns:
                        if (pattern in file_lower or 
                            pattern in file_stem or
                            file_lower in pattern or
                            file_stem in pattern):
                            
                            full_path = Path(root) / file
                            rel_path = full_path.relative_to(base_dir)
                            found_files.append((full_path, rel_path, pattern))
    
    except Exception as e:
        print(f"⚠️ Ошибка поиска файлов: {e}")
    
    # Возвращаем лучший результат
    if found_files:
        # Сортируем по близости совпадения
        found_files.sort(key=lambda x: len(x[1].parts))
        return True, str(found_files[0][1])
    
    return False, ""

def show_problematic_functions():
    """Показывает все функции с проблемными путями"""
    print("🔍 ФУНКЦИИ С ПРОБЛЕМНЫМИ ПУТЯМИ В SFM РЕЕСТРЕ")
    print("=" * 70)
    
    # Загружаем реестр
    functions = load_sfm_registry()
    if not functions:
        print("❌ Не удалось загрузить SFM реестр")
        return
    
    base_dir = Path.cwd()
    problematic_functions = []
    
    print(f"📁 Базовая директория: {base_dir}")
    print(f"📊 Всего функций в реестре: {len(functions)}")
    print()
    
    # Проверяем каждый файл
    for func_id, func_data in functions.items():
        file_path_str = func_data.get('file_path', '')
        if not file_path_str:
            continue
            
        # Нормализуем путь
        if file_path_str.startswith('./'):
            file_path_str = file_path_str[2:]
        
        normalized_path = base_dir / file_path_str
        
        # Проверяем существование файла
        if not normalized_path.exists() or not normalized_path.is_file():
            # Ищем похожий файл
            found, similar_path = find_similar_file(file_path_str, base_dir)
            
            problematic_functions.append({
                'function_id': func_id,
                'name': func_data.get('name', func_id),
                'original_path': file_path_str,
                'normalized_path': str(normalized_path),
                'found_similar': found,
                'similar_path': similar_path,
                'category': func_data.get('function_type', 'unknown'),
                'status': func_data.get('status', 'unknown')
            })
    
    print(f"❌ Найдено {len(problematic_functions)} функций с проблемными путями")
    print()
    
    # Группируем по категориям
    categories = {}
    for func in problematic_functions:
        category = func['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(func)
    
    print("📋 ПРОБЛЕМНЫЕ ФУНКЦИИ ПО КАТЕГОРИЯМ:")
    print("-" * 70)
    
    for category, funcs in sorted(categories.items()):
        print(f"\n🔸 {category.upper()} ({len(funcs)} функций):")
        
        for i, func in enumerate(funcs, 1):
            print(f"\n{i:2d}. {func['function_id']}")
            print(f"    Название: {func['name']}")
            print(f"    Оригинальный путь: {func['original_path']}")
            print(f"    Статус: {func['status']}")
            
            if func['found_similar']:
                print(f"    ✅ Найден похожий: {func['similar_path']}")
            else:
                print(f"    ❌ Похожий файл не найден")
    
    # Сохраняем список проблемных функций
    report_data = {
        'timestamp': str(Path.cwd()),
        'total_problematic': len(problematic_functions),
        'categories': {
            category: {
                'count': len(funcs),
                'functions': funcs
            }
            for category, funcs in categories.items()
        },
        'all_problematic': problematic_functions
    }
    
    report_path = f"data/reports/problematic_functions_{len(problematic_functions)}.json"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 Отчет сохранен: {report_path}")
    
    # Показываем топ проблемных функций для исправления
    print(f"\n🎯 ТОП-20 ФУНКЦИЙ ДЛЯ ИСПРАВЛЕНИЯ:")
    print("-" * 70)
    
    # Сортируем по приоритету (с найденными похожими файлами сначала)
    sorted_funcs = sorted(problematic_functions, key=lambda x: (not x['found_similar'], x['category']))
    
    for i, func in enumerate(sorted_funcs[:20], 1):
        status_icon = "✅" if func['found_similar'] else "❌"
        print(f"{i:2d}. {status_icon} {func['function_id']} ({func['category']})")
        print(f"    Было: {func['original_path']}")
        if func['found_similar']:
            print(f"    Стало: {func['similar_path']}")
        print()
    
    return problematic_functions

if __name__ == "__main__":
    try:
        problematic_functions = show_problematic_functions()
        print(f"\n🎯 АНАЛИЗ ЗАВЕРШЕН")
        print(f"Найдено {len(problematic_functions)} функций для исправления")
    except Exception as e:
        print(f"❌ Ошибка выполнения: {e}")
        import traceback
        traceback.print_exc()