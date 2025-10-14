#!/usr/bin/env python3
"""
Финальный поиск всех файлов - без сложной логики исключения
"""

import os
import json
from pathlib import Path
from datetime import datetime

def final_find_all_files():
    """Находит все Python файлы без сложной логики исключения"""
    print("🔍 ФИНАЛЬНЫЙ ПОИСК ВСЕХ ФАЙЛОВ")
    print("=" * 50)
    
    base_dir = Path.cwd()
    print(f"📁 Базовая директория: {base_dir}")
    
    all_files = []
    
    # Простой поиск всех .py файлов
    for root, dirs, files in os.walk(base_dir):
        # Исключаем только очевидные директории
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'node_modules']]
        
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                try:
                    rel_path = file_path.relative_to(base_dir)
                    
                    # Пропускаем файлы с backup в названии
                    if 'backup' in file.lower():
                        continue
                    
                    # Пропускаем файлы в директориях с backup
                    if any(part.lower().startswith('backup') for part in rel_path.parts):
                        continue
                    
                    file_info = {
                        'path': str(rel_path),
                        'name': file,
                        'stem': Path(file).stem,
                        'size_bytes': file_path.stat().st_size,
                        'size_kb': round(file_path.stat().st_size / 1024, 1)
                    }
                    
                    all_files.append(file_info)
                    
                except Exception as e:
                    print(f"⚠️ Ошибка обработки файла {file_path}: {e}")
                    continue
    
    print(f"📊 Найдено {len(all_files)} Python файлов")
    
    # Группируем по директориям
    directories = {}
    for file_info in all_files:
        path_parts = Path(file_info['path']).parts
        if len(path_parts) > 1:
            dir_name = path_parts[0]
        else:
            dir_name = "ROOT"
        
        if dir_name not in directories:
            directories[dir_name] = []
        directories[dir_name].append(file_info)
    
    print(f"\n📂 ФАЙЛЫ ПО ДИРЕКТОРИЯМ:")
    print("-" * 50)
    
    total_files = 0
    for dir_name, files in sorted(directories.items()):
        print(f"{dir_name:15} | {len(files):3d} файлов")
        total_files += len(files)
        
        # Показываем примеры файлов
        for file_info in files[:3]:
            print(f"   📄 {file_info['path']}")
        if len(files) > 3:
            print(f"   ... и еще {len(files) - 3} файлов")
        print()
    
    print(f"{'ВСЕГО':15} | {total_files:3d} файлов")
    
    # Сохраняем результаты
    report_data = {
        'timestamp': datetime.now().isoformat(),
        'total_files': len(all_files),
        'directories': {
            dir_name: {
                'count': len(files),
                'files': files
            }
            for dir_name, files in directories.items()
        },
        'all_files': all_files
    }
    
    report_path = f"data/reports/final_files_found_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 Отчет сохранен: {report_path}")
    
    return all_files, directories

if __name__ == "__main__":
    try:
        all_files, directories = final_find_all_files()
        print(f"\n🎯 ПОИСК ЗАВЕРШЕН")
        print(f"Найдено {len(all_files)} файлов")
    except Exception as e:
        print(f"❌ Ошибка выполнения: {e}")
        import traceback
        traceback.print_exc()