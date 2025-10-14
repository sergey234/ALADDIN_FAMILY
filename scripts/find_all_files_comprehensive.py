#!/usr/bin/env python3
"""
Комплексный поиск всех файлов в системе ALADDIN
Находит все Python файлы в основных рабочих директориях
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime

def should_exclude_path(path: Path) -> bool:
    """Проверяет, нужно ли исключить путь из поиска"""
    path_str = str(path).lower()
    
    # Исключаем директории
    exclude_dirs = {
        'backups', 'backup', 'temp', 'tmp', 'cache', 'logs', 
        '__pycache__', '.git', 'node_modules',
        'formatting_work', 'backup_sys_path_removal',
        'old_files_removal', 'registry_merge_backup',
        'fixed_registry_merge_backup', 'aladdin_',
        'test', 'tests', 'docs', 'documentation',
        '.pytest_cache', '.mypy_cache'
    }
    
    # Проверяем каждую часть пути
    for part in path.parts:
        if any(exclude_dir in part.lower() for exclude_dir in exclude_dirs):
            return True
    
    # Исключаем файлы с определенными расширениями (кроме .py)
    exclude_extensions = {
        '.pyc', '.pyo', '.log', '.tmp', '.bak', '.backup',
        '.md', '.txt', '.json', '.yaml', '.yml', '.cfg',
        '.ini', '.env', '.gitignore', '.dockerignore',
        '.html', '.css', '.js', '.sql', '.csv'
    }
    
    if path.suffix.lower() in exclude_extensions:
        return True
    
    # Исключаем файлы с backup в названии
    if 'backup' in path.name.lower() or path.name.endswith('.backup'):
        return True
    
    return False

def get_file_category(file_path: Path) -> str:
    """Определяет категорию файла на основе его пути"""
    path_str = str(file_path).lower()
    
    if 'ai_agents' in path_str or 'ai_agent' in path_str:
        return 'AI_AGENT'
    elif 'bots' in path_str or 'bot' in path_str:
        return 'BOT'
    elif 'managers' in path_str or 'manager' in path_str:
        return 'MANAGER'
    elif 'microservices' in path_str or 'microservice' in path_str:
        return 'MICROSERVICE'
    elif 'vpn' in path_str:
        return 'VPN'
    elif 'family' in path_str:
        return 'FAMILY'
    elif 'compliance' in path_str:
        return 'COMPLIANCE'
    elif 'security' in path_str:
        return 'SECURITY'
    elif 'core' in path_str:
        return 'CORE'
    elif 'config' in path_str:
        return 'CONFIG'
    elif 'data' in path_str:
        return 'DATA'
    elif 'models' in path_str:
        return 'MODELS'
    elif 'active' in path_str:
        return 'ACTIVE'
    elif 'reactive' in path_str:
        return 'REACTIVE'
    elif 'integration' in path_str:
        return 'INTEGRATION'
    else:
        return 'OTHER'

def find_all_files_comprehensive():
    """Комплексный поиск всех файлов"""
    print("🔍 КОМПЛЕКСНЫЙ ПОИСК ВСЕХ ФАЙЛОВ В СИСТЕМЕ ALADDIN")
    print("=" * 70)
    
    base_dir = Path.cwd()
    all_files = []
    categories = {}
    
    print(f"📁 Базовая директория: {base_dir}")
    print("🚫 Исключаем: backups, logs, cache, temp, tests, docs")
    print()
    
    # Ищем во всех поддиректориях
    print("📂 Сканируем все директории...")
    
    for root, dirs, files in os.walk(base_dir):
        root_path = Path(root)
        
        # Исключаем ненужные поддиректории
        dirs[:] = [d for d in dirs if not should_exclude_path(root_path / d)]
        
        # Пропускаем исключенные директории
        if should_exclude_path(root_path):
            continue
        
        for file in files:
            file_path = root_path / file
            
            # Исключаем ненужные файлы
            if should_exclude_path(file_path):
                continue
            
            # Только Python файлы
            if file.endswith('.py'):
                try:
                    rel_path = file_path.relative_to(base_dir)
                    category = get_file_category(rel_path)
                    
                    # Получаем размер файла
                    file_size = file_path.stat().st_size
                    file_modified = datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    
                    file_info = {
                        'path': str(rel_path),
                        'full_path': str(file_path),
                        'name': file,
                        'category': category,
                        'size_bytes': file_size,
                        'size_kb': round(file_size / 1024, 1),
                        'modified': file_modified,
                        'lines_of_code': count_lines_of_code(file_path)
                    }
                    
                    all_files.append(file_info)
                    
                    if category not in categories:
                        categories[category] = []
                    categories[category].append(file_info)
                    
                except Exception as e:
                    print(f"⚠️ Ошибка обработки файла {file_path}: {e}")
                    continue
    
    # Выводим результаты
    print(f"\n📊 НАЙДЕННЫЕ ФАЙЛЫ ПО КАТЕГОРИЯМ:")
    print("-" * 70)
    
    total_files = 0
    total_size = 0
    total_lines = 0
    
    for category, files in sorted(categories.items()):
        category_size = sum(f['size_bytes'] for f in files)
        category_lines = sum(f['lines_of_code'] for f in files)
        
        print(f"{category:15} | {len(files):3d} файлов | {category_size/1024:.0f} KB | {category_lines:,} строк")
        total_files += len(files)
        total_size += category_size
        total_lines += category_lines
    
    print("-" * 70)
    print(f"{'ВСЕГО':15} | {total_files:3d} файлов | {total_size/1024:.0f} KB | {total_lines:,} строк")
    
    # Показываем топ файлы по размеру
    print(f"\n📋 ТОП ФАЙЛОВ ПО РАЗМЕРУ:")
    print("-" * 70)
    
    sorted_files = sorted(all_files, key=lambda x: x['size_bytes'], reverse=True)
    for i, file_info in enumerate(sorted_files[:10], 1):
        print(f"{i:2d}. {file_info['path']} ({file_info['size_kb']} KB, {file_info['lines_of_code']:,} строк)")
    
    # Показываем примеры по категориям
    print(f"\n📋 ПРИМЕРЫ ФАЙЛОВ ПО КАТЕГОРИЯМ:")
    print("-" * 70)
    
    for category, files in sorted(categories.items()):
        if files:
            print(f"\n🔸 {category} ({len(files)} файлов):")
            for file_info in files[:3]:  # Показываем первые 3 файла
                print(f"   📄 {file_info['path']} ({file_info['size_kb']} KB)")
            
            if len(files) > 3:
                print(f"   ... и еще {len(files) - 3} файлов")
    
    # Сохраняем полный отчет
    report_data = {
        'timestamp': datetime.now().isoformat(),
        'base_directory': str(base_dir),
        'total_files': total_files,
        'total_size_bytes': total_size,
        'total_size_kb': round(total_size / 1024, 1),
        'total_lines_of_code': total_lines,
        'categories': {
            category: {
                'count': len(files),
                'size_bytes': sum(f['size_bytes'] for f in files),
                'size_kb': round(sum(f['size_bytes'] for f in files) / 1024, 1),
                'lines_of_code': sum(f['lines_of_code'] for f in files),
                'files': files
            }
            for category, files in categories.items()
        },
        'all_files': all_files
    }
    
    report_path = f"data/reports/comprehensive_files_found_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 Полный отчет сохранен: {report_path}")
    
    return all_files, categories, report_data

def count_lines_of_code(file_path: Path) -> int:
    """Подсчитывает количество строк кода в файле"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return len(f.readlines())
    except:
        return 0

if __name__ == "__main__":
    try:
        all_files, categories, report_data = find_all_files_comprehensive()
        print(f"\n🎯 КОМПЛЕКСНЫЙ ПОИСК ЗАВЕРШЕН")
        print(f"Найдено {len(all_files)} файлов")
        print(f"Общий размер: {report_data['total_size_kb']} KB")
        print(f"Общее количество строк: {report_data['total_lines_of_code']:,}")
    except Exception as e:
        print(f"❌ Ошибка выполнения: {e}")
        sys.exit(1)