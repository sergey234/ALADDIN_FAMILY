#!/usr/bin/env python3
"""
Автоматическое исправление ошибок импортов
"""

import os
import re
import subprocess
from pathlib import Path

def fix_import_errors_in_file(file_path):
    """Исправляет ошибки импортов в одном файле"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Проверяем, есть ли sys.path.append() в файле
        if 'sys.path.append(' in content:
            print(f"  🔧 Исправляем {file_path}")
            
            # Разделяем на части
            lines = content.split('\n')
            
            # Находим импорты и sys.path.append
            imports = []
            sys_path_lines = []
            other_lines = []
            
            in_imports = False
            for i, line in enumerate(lines):
                stripped = line.strip()
                
                if stripped.startswith('import ') or stripped.startswith('from '):
                    imports.append(line)
                    in_imports = True
                elif stripped.startswith('sys.path.append('):
                    sys_path_lines.append(line)
                    in_imports = False
                elif stripped and not stripped.startswith('#') and not stripped.startswith('"""') and not stripped.startswith("'''"):
                    if in_imports:
                        # Продолжение импорта
                        imports.append(line)
                    else:
                        other_lines.append(line)
                        in_imports = False
                else:
                    other_lines.append(line)
                    in_imports = False
            
            # Создаем новый контент
            new_content = []
            
            # Добавляем заголовок файла
            for line in lines:
                if line.strip().startswith('# -*-') or line.strip().startswith('"""') or line.strip().startswith("'''"):
                    new_content.append(line)
                elif line.strip() == '':
                    new_content.append(line)
                else:
                    break
            
            # Добавляем пустую строку
            new_content.append('')
            
            # Добавляем все импорты
            for imp in imports:
                new_content.append(imp)
            
            # Добавляем пустую строку
            new_content.append('')
            
            # Добавляем sys.path.append
            for sys_line in sys_path_lines:
                new_content.append(sys_line)
            
            # Добавляем пустую строку
            new_content.append('')
            
            # Добавляем остальной код
            for line in other_lines:
                if not (line.strip().startswith('import ') or 
                       line.strip().startswith('from ') or 
                       line.strip().startswith('sys.path.append(')):
                    new_content.append(line)
            
            # Объединяем
            new_content_str = '\n'.join(new_content)
            
            # Проверяем, изменился ли файл
            if new_content_str != original_content:
                # Создаем резервную копию
                backup_path = f"{file_path}.backup"
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original_content)
                
                # Записываем исправленный файл
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content_str)
                
                print(f"    ✅ Исправлен (резервная копия: {backup_path})")
                return True
            else:
                print(f"    ℹ️  Файл уже исправлен")
                return False
                
    except Exception as e:
        print(f"    ❌ Ошибка: {e}")
        return False

def fix_import_errors_in_directory(directory):
    """Исправляет ошибки импортов в директории"""
    print(f"🔍 ИСПРАВЛЕНИЕ ОШИБОК ИМПОРТОВ В {directory}")
    print("=" * 60)
    
    fixed_files = 0
    total_files = 0
    
    for py_file in Path(directory).rglob("*.py"):
        if any(exclude in str(py_file) for exclude in ['backup', 'test', 'logs', '__pycache__']):
            continue
            
        total_files += 1
        
        # Проверяем, есть ли ошибки E402 в файле
        try:
            result = subprocess.run([
                "python3", "-m", "flake8", "--select=E402", str(py_file)
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                if fix_import_errors_in_file(str(py_file)):
                    fixed_files += 1
            else:
                print(f"  ✅ {py_file.name} - без ошибок E402")
                
        except Exception as e:
            print(f"  ❌ {py_file.name} - ошибка проверки: {e}")
    
    print(f"\n📊 ИТОГИ:")
    print(f"  • Проверено файлов: {total_files}")
    print(f"  • Исправлено файлов: {fixed_files}")
    print(f"  • Процент исправления: {(fixed_files/total_files*100):.1f}%")

def main():
    """Основная функция"""
    print("🔧 АВТОМАТИЧЕСКОЕ ИСПРАВЛЕНИЕ ОШИБОК ИМПОРТОВ")
    print("=" * 60)
    
    # Исправляем security/
    fix_import_errors_in_directory("security")
    
    print("\n" + "=" * 60)
    
    # Исправляем formatting_work/
    fix_import_errors_in_directory("formatting_work")
    
    print("\n🎯 РЕКОМЕНДАЦИИ:")
    print("1. Проверьте исправленные файлы")
    print("2. Удалите .backup файлы после проверки")
    print("3. Настройте PYTHONPATH для избежания sys.path.append()")
    print("4. Используйте относительные импорты где возможно")

if __name__ == "__main__":
    main()