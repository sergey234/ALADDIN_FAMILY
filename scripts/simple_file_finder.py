#!/usr/bin/env python3
"""
Простой поиск файлов для диагностики
"""

import os
from pathlib import Path

def simple_find():
    print("🔍 ПРОСТОЙ ПОИСК ФАЙЛОВ")
    print("=" * 50)
    
    base_dir = Path.cwd()
    print(f"📁 Базовая директория: {base_dir}")
    
    # Проверим основные директории
    main_dirs = ['security', 'core', 'config', 'data']
    
    for main_dir in main_dirs:
        dir_path = base_dir / main_dir
        if dir_path.exists():
            print(f"\n📂 {main_dir}/")
            py_files = list(dir_path.rglob("*.py"))
            print(f"   Найдено {len(py_files)} Python файлов")
            
            for py_file in py_files[:5]:  # Показываем первые 5
                rel_path = py_file.relative_to(base_dir)
                print(f"   📄 {rel_path}")
            
            if len(py_files) > 5:
                print(f"   ... и еще {len(py_files) - 5} файлов")
        else:
            print(f"\n📂 {main_dir}/ - НЕ НАЙДЕНА")
    
    # Проверим корневые файлы
    print(f"\n📂 Корневые файлы:")
    root_files = [f for f in os.listdir(base_dir) if f.endswith('.py')]
    print(f"   Найдено {len(root_files)} Python файлов")
    
    for root_file in root_files[:10]:  # Показываем первые 10
        print(f"   📄 {root_file}")
    
    if len(root_files) > 10:
        print(f"   ... и еще {len(root_files) - 10} файлов")

if __name__ == "__main__":
    simple_find()