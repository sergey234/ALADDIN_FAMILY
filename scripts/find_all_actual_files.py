#!/usr/bin/env python3
"""
Поиск всех реальных файлов в основных директориях ALADDIN
Исключает бэкапы, временные файлы, скрипты и тестовые данные
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
        'scripts', '__pycache__', '.git', 'node_modules',
        'formatting_work', 'backup_sys_path_removal',
        'old_files_removal', 'registry_merge_backup',
        'fixed_registry_merge_backup', 'aladdin_',
        'test', 'tests', 'docs', 'documentation'
    }
    
    # Проверяем каждую часть пути
    for part in path.parts:
        if any(exclude_dir in part.lower() for exclude_dir in exclude_dirs):
            return True
    
    # Исключаем файлы с определенными паттернами
    exclude_patterns = {
        '.pyc', '.pyo', '.log', '.tmp', '.bak', '.backup',
        '.md', '.txt', '.json', '.yaml', '.yml', '.cfg',
        '.ini', '.env', '.gitignore', '.dockerignore'
    }
    
    if path.suffix.lower() in exclude_patterns:
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
    elif 'security' in path_str:
        if 'vpn' in path_str:
            return 'VPN'
        elif 'family' in path_str:
            return 'FAMILY'
        elif 'compliance' in path_str:
            return 'COMPLIANCE'
        else:
            return 'SECURITY'
    elif 'core' in path_str:
        return 'CORE'
    elif 'config' in path_str:
        return 'CONFIG'
    elif 'data' in path_str:
        return 'DATA'
    else:
        return 'OTHER'

def find_all_files():
    """Основная функция поиска всех файлов"""
    print("🔍 ПОИСК ВСЕХ ФАЙЛОВ В СИСТЕМЕ ALADDIN")
    print("=" * 60)
    
    base_dir = Path.cwd()
    all_files = []
    categories = {}
    
    print(f"📁 Базовая директория: {base_dir}")
    print("🚫 Исключаем: backups, scripts, logs, cache, temp, tests")
    print()
    
    # Основные директории для поиска
    search_dirs = [
        'security',
        'core', 
        'config',
        'data',
        'models'
    ]
    
    for search_dir in search_dirs:
        search_path = base_dir / search_dir
        if search_path.exists():
            print(f"📂 Сканируем: {search_dir}/")
            
            for root, dirs, files in os.walk(search_path):
                # Исключаем ненужные поддиректории
                dirs[:] = [d for d in dirs if not should_exclude_path(Path(root) / d)]
                
                for file in files:
                    file_path = Path(root) / file
                    
                    # Исключаем ненужные файлы
                    if should_exclude_path(file_path):
                        continue
                    
                    # Только Python файлы
                    if file.endswith('.py'):
                        rel_path = file_path.relative_to(base_dir)
                        category = get_file_category(rel_path)
                        
                        file_info = {
                            'path': str(rel_path),
                            'full_path': str(file_path),
                            'name': file,
                            'category': category,
                            'size': file_path.stat().st_size,
                            'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                        }
                        
                        all_files.append(file_info)
                        
                        if category not in categories:
                            categories[category] = []
                        categories[category].append(file_info)
    
    # Также проверим корневые файлы
    print(f"📂 Сканируем корневые файлы")
    for file in os.listdir(base_dir):
        if file.endswith('.py') and not should_exclude_path(Path(file)):
            file_path = base_dir / file
            category = 'ROOT'
            
            file_info = {
                'path': file,
                'full_path': str(file_path),
                'name': file,
                'category': category,
                'size': file_path.stat().st_size,
                'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            }
            
            all_files.append(file_info)
            
            if category not in categories:
                categories[category] = []
            categories[category].append(file_info)
    
    # Выводим результаты
    print(f"\n📊 НАЙДЕННЫЕ ФАЙЛЫ ПО КАТЕГОРИЯМ:")
    print("-" * 60)
    
    total_files = 0
    for category, files in sorted(categories.items()):
        print(f"{category:15} | {len(files):3d} файлов")
        total_files += len(files)
    
    print(f"{'ВСЕГО':15} | {total_files:3d} файлов")
    
    # Показываем примеры файлов в каждой категории
    print(f"\n📋 ПРИМЕРЫ ФАЙЛОВ ПО КАТЕГОРИЯМ:")
    print("-" * 60)
    
    for category, files in sorted(categories.items()):
        if files:
            print(f"\n🔸 {category} ({len(files)} файлов):")
            for file_info in files[:5]:  # Показываем первые 5 файлов
                size_kb = file_info['size'] / 1024
                print(f"   📄 {file_info['path']} ({size_kb:.1f} KB)")
            
            if len(files) > 5:
                print(f"   ... и еще {len(files) - 5} файлов")
    
    # Сохраняем полный отчет
    report_data = {
        'timestamp': datetime.now().isoformat(),
        'base_directory': str(base_dir),
        'total_files': total_files,
        'categories': {
            category: {
                'count': len(files),
                'files': files
            }
            for category, files in categories.items()
        },
        'all_files': all_files
    }
    
    report_path = f"data/reports/all_files_found_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 Полный отчет сохранен: {report_path}")
    
    # Создаем список для SFM реестра
    sfm_candidates = []
    for file_info in all_files:
        # Создаем ID функции на основе имени файла
        func_id = Path(file_info['name']).stem.lower().replace(' ', '_').replace('-', '_')
        
        sfm_candidate = {
            'function_id': func_id,
            'name': func_id.replace('_', ' ').title(),
            'file_path': f"./{file_info['path']}",
            'category': file_info['category'],
            'size_bytes': file_info['size'],
            'last_modified': file_info['modified']
        }
        sfm_candidates.append(sfm_candidate)
    
    candidates_path = f"data/reports/sfm_candidates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(candidates_path, 'w', encoding='utf-8') as f:
        json.dump(sfm_candidates, f, ensure_ascii=False, indent=2)
    
    print(f"📋 Кандидаты для SFM реестра: {candidates_path}")
    
    return all_files, categories, sfm_candidates

if __name__ == "__main__":
    try:
        all_files, categories, sfm_candidates = find_all_files()
        print(f"\n🎯 ПОИСК ЗАВЕРШЕН")
        print(f"Найдено {len(all_files)} файлов")
        print(f"Создано {len(sfm_candidates)} кандидатов для SFM")
    except Exception as e:
        print(f"❌ Ошибка выполнения: {e}")
        sys.exit(1)