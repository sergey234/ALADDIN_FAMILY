#!/usr/bin/env python3
"""
Исправление путей к отсутствующим файлам в SFM реестре
Находит реальные файлы и обновляет пути в реестре
"""

import json
import os
import sys
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional
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
        return data
    except Exception as e:
        print(f"❌ Ошибка загрузки реестра: {e}")
        return {}

def save_sfm_registry(data: Dict) -> bool:
    """Сохраняет SFM реестр в JSON файл"""
    registry_path = Path("data/sfm/function_registry.json")
    
    # Создаем резервную копию
    backup_path = registry_path.with_suffix(f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
    shutil.copy2(registry_path, backup_path)
    print(f"📁 Создана резервная копия: {backup_path}")
    
    try:
        with open(registry_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения реестра: {e}")
        return False

def find_actual_file(missing_path: str, base_dir: Path) -> Optional[Path]:
    """Находит реальный файл по похожему имени"""
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
        return found_files[0][1]  # Возвращаем относительный путь
    
    return None

def fix_file_paths():
    """Основная функция исправления путей"""
    print("🔧 ИСПРАВЛЕНИЕ ПУТЕЙ К ОТСУТСТВУЮЩИМ ФАЙЛАМ")
    print("=" * 60)
    
    # Загружаем реестр
    registry_data = load_sfm_registry()
    if not registry_data:
        print("❌ Не удалось загрузить SFM реестр")
        return
    
    functions = registry_data.get('functions', {})
    base_dir = Path.cwd()
    
    print(f"📁 Базовая директория: {base_dir}")
    print(f"📊 Всего функций в реестре: {len(functions)}")
    print()
    
    fixed_count = 0
    removed_count = 0
    fixed_files = []
    removed_files = []
    
    # Проходим по всем функциям
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
            print(f"🔍 Ищу файл для: {func_id}")
            print(f"   Оригинальный путь: {file_path_str}")
            
            # Ищем реальный файл
            actual_path = find_actual_file(file_path_str, base_dir)
            
            if actual_path:
                # Обновляем путь в реестре
                new_path = f"./{actual_path}"
                func_data['file_path'] = new_path
                func_data['last_updated'] = datetime.now().isoformat()
                
                print(f"   ✅ Найден: {actual_path}")
                print(f"   🔄 Обновлен путь: {new_path}")
                
                fixed_count += 1
                fixed_files.append({
                    'function_id': func_id,
                    'original_path': file_path_str,
                    'new_path': str(actual_path),
                    'status': 'fixed'
                })
            else:
                print(f"   ❌ Файл не найден, помечаю для удаления")
                
                # Помечаем функцию как удаленную
                func_data['status'] = 'removed'
                func_data['removed_at'] = datetime.now().isoformat()
                func_data['removal_reason'] = 'file_not_found'
                
                removed_count += 1
                removed_files.append({
                    'function_id': func_id,
                    'original_path': file_path_str,
                    'status': 'removed'
                })
            
            print()
    
    # Сохраняем обновленный реестр
    if fixed_count > 0 or removed_count > 0:
        if save_sfm_registry(registry_data):
            print(f"✅ Реестр успешно обновлен!")
        else:
            print(f"❌ Ошибка сохранения реестра")
            return
    
    # Выводим статистику
    print("📊 РЕЗУЛЬТАТЫ ИСПРАВЛЕНИЯ:")
    print("-" * 60)
    print(f"✅ Исправлено путей: {fixed_count}")
    print(f"🗑️ Удалено записей: {removed_count}")
    print(f"📊 Всего обработано: {fixed_count + removed_count}")
    
    # Сохраняем отчет
    report_data = {
        'timestamp': datetime.now().isoformat(),
        'base_directory': str(base_dir),
        'total_processed': fixed_count + removed_count,
        'fixed_files': fixed_count,
        'removed_files': removed_count,
        'fixed_details': fixed_files,
        'removed_details': removed_files
    }
    
    report_path = f"data/reports/file_paths_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 Отчет сохранен: {report_path}")
    
    # Показываем примеры исправлений
    if fixed_files:
        print(f"\n🔧 ПРИМЕРЫ ИСПРАВЛЕННЫХ ПУТЕЙ:")
        print("-" * 60)
        for i, fix in enumerate(fixed_files[:10], 1):  # Показываем первые 10
            print(f"{i:2d}. {fix['function_id']}")
            print(f"    Было: {fix['original_path']}")
            print(f"    Стало: {fix['new_path']}")
            print()
    
    if removed_files:
        print(f"\n🗑️ ПРИМЕРЫ УДАЛЕННЫХ ЗАПИСЕЙ:")
        print("-" * 60)
        for i, removed in enumerate(removed_files[:10], 1):  # Показываем первые 10
            print(f"{i:2d}. {removed['function_id']}")
            print(f"    Путь: {removed['original_path']}")
            print()

if __name__ == "__main__":
    try:
        fix_file_paths()
        print(f"\n🎯 ИСПРАВЛЕНИЕ ЗАВЕРШЕНО")
    except Exception as e:
        print(f"❌ Ошибка выполнения: {e}")
        sys.exit(1)