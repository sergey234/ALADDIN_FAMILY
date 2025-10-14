#!/usr/bin/env python3
"""
Анализ всех дублированных файлов в системе
Показывает что удалять, что оставлять
"""

import os
import glob
from datetime import datetime

def analyze_duplicates():
    """Анализ всех дублированных файлов"""
    print("=" * 80)
    print("🔍 АНАЛИЗ ВСЕХ ДУБЛИРОВАННЫХ ФАЙЛОВ В СИСТЕМЕ")
    print("=" * 80)
    
    # Паттерны для поиска дублированных файлов
    patterns = [
        "*_old.py",
        "*_new.py", 
        "*_backup_*.py",
        "*_fixed.py",
        "*_patch.py",
        "*_enhanced.py",
        "*_improved.py"
    ]
    
    # Директории для поиска
    search_dirs = [
        "/Users/sergejhlystov/ALADDIN_NEW/security",
        "/Users/sergejhlystov/ALADDIN_NEW/core",
        "/Users/sergejhlystov/ALADDIN_NEW/scripts"
    ]
    
    all_files = {}
    
    for search_dir in search_dirs:
        if os.path.exists(search_dir):
            for pattern in patterns:
                files = glob.glob(os.path.join(search_dir, "**", pattern), recursive=True)
                for file_path in files:
                    relative_path = file_path.replace("/Users/sergejhlystov/ALADDIN_NEW/", "")
                    file_size = os.path.getsize(file_path)
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    if relative_path not in all_files:
                        all_files[relative_path] = {
                            'size': file_size,
                            'time': file_time,
                            'type': pattern.replace("*", "").replace(".py", "")
                        }
    
    # Группируем файлы по базовому имени
    groups = {}
    for file_path, info in all_files.items():
        base_name = file_path.split('/')[-1]
        if '_old' in base_name:
            base = base_name.replace('_old.py', '')
        elif '_new' in base_name:
            base = base_name.replace('_new.py', '')
        elif '_backup_' in base_name:
            base = base_name.split('_backup_')[0]
        elif '_fixed' in base_name:
            base = base_name.replace('_fixed.py', '')
        elif '_patch' in base_name:
            base = base_name.replace('_patch.py', '')
        elif '_enhanced' in base_name:
            base = base_name.replace('_enhanced.py', '')
        elif '_improved' in base_name:
            base = base_name.replace('_improved.py', '')
        else:
            base = base_name.replace('.py', '')
        
        if base not in groups:
            groups[base] = []
        groups[base].append((file_path, info))
    
    # Анализируем каждую группу
    print("\n📊 АНАЛИЗ ПО ГРУППАМ ФАЙЛОВ:")
    print("=" * 80)
    
    files_to_delete = []
    files_to_keep = []
    
    for base_name, files in groups.items():
        if len(files) > 1:
            print(f"\n🔍 ГРУППА: {base_name}")
            print("-" * 60)
            
            # Сортируем по времени (новые первыми)
            files.sort(key=lambda x: x[1]['time'], reverse=True)
            
            for i, (file_path, info) in enumerate(files):
                status = "✅ ОСТАВИТЬ" if i == 0 else "❌ УДАЛИТЬ"
                size_kb = info['size'] / 1024
                print(f"  {status} {file_path}")
                print(f"      Размер: {size_kb:.1f}KB, Время: {info['time'].strftime('%Y-%m-%d %H:%M')}")
                
                if i == 0:
                    files_to_keep.append(file_path)
                else:
                    files_to_delete.append(file_path)
        else:
            # Одиночные файлы
            file_path, info = files[0]
            files_to_keep.append(file_path)
            print(f"\n✅ ОДИНОЧНЫЙ: {file_path}")
    
    # Показываем файлы для удаления
    print(f"\n🗑️ ФАЙЛЫ ДЛЯ УДАЛЕНИЯ ({len(files_to_delete)} файлов):")
    print("=" * 80)
    
    for file_path in sorted(files_to_delete):
        print(f"rm '{file_path}'")
    
    # Показываем файлы для сохранения
    print(f"\n✅ ФАЙЛЫ ДЛЯ СОХРАНЕНИЯ ({len(files_to_keep)} файлов):")
    print("=" * 80)
    
    for file_path in sorted(files_to_keep):
        print(f"KEEP: {file_path}")
    
    # Статистика
    total_size_to_delete = sum(os.path.getsize(f"/Users/sergejhlystov/ALADDIN_NEW/{f}") for f in files_to_delete)
    total_size_to_keep = sum(os.path.getsize(f"/Users/sergejhlystov/ALADDIN_NEW/{f}") for f in files_to_keep)
    
    print(f"\n📊 СТАТИСТИКА:")
    print(f"   Файлов для удаления: {len(files_to_delete)}")
    print(f"   Файлов для сохранения: {len(files_to_keep)}")
    print(f"   Размер для удаления: {total_size_to_delete / 1024 / 1024:.1f}MB")
    print(f"   Размер для сохранения: {total_size_to_keep / 1024 / 1024:.1f}MB")
    
    return files_to_delete, files_to_keep

if __name__ == "__main__":
    analyze_duplicates()