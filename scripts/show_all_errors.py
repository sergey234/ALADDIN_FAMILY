#!/usr/bin/env python3
"""
Показ ВСЕХ ошибок flake8 по файлам
"""

import subprocess
from pathlib import Path
from collections import defaultdict

def show_all_errors():
    """Показать ВСЕ ошибки flake8 сгруппированные по файлам"""
    security_dir = Path("/Users/sergejhlystov/ALADDIN_NEW/security")
    
    print("🔍 ПОЛНЫЙ АНАЛИЗ ОШИБОК FLAKE8 ПО ВСЕМ ФАЙЛАМ")
    print("=" * 80)
    
    try:
        # Команда flake8 с правильными исключениями
        cmd = [
            "python3", "-m", "flake8",
            "--max-line-length=120",
            "--exclude=*/backup*,*/test*,*/logs*,*/formatting_work*",
            str(security_dir)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("✅ Ошибок не найдено!")
            return
        
        output = result.stdout
        error_lines = [line for line in output.split('\n') if line.strip()]
        
        # Группировка ошибок по файлам
        file_errors = defaultdict(list)
        for line in error_lines:
            if ':' in line:
                file_path = line.split(':')[0]
                file_errors[file_path].append(line)
        
        # Сортировка по количеству ошибок
        sorted_files = sorted(file_errors.items(), key=lambda x: len(x[1]), reverse=True)
        
        print(f"📊 НАЙДЕНО {len(error_lines)} ОШИБОК В {len(file_errors)} ФАЙЛАХ")
        print("=" * 80)
        
        # Показ ВСЕХ файлов с ошибками
        for i, (file_path, errors) in enumerate(sorted_files, 1):
            print(f"\n{i:3d}. {file_path}")
            print(f"     Ошибок: {len(errors)}")
            
            # Показ всех ошибок для каждого файла
            for error in errors:
                print(f"     • {error}")
        
        # Статистика по типам ошибок
        print(f"\n📊 СТАТИСТИКА ПО ТИПАМ ОШИБОК:")
        error_types = defaultdict(int)
        for line in error_lines:
            if ':' in line and len(line.split(':')) >= 3:
                error_code = line.split(':')[2].strip().split()[0]
                error_types[error_code] += 1
        
        for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  {error_type}: {count} ошибок")
        
        print(f"\n🎯 ИТОГО: {len(error_lines)} ошибок в {len(file_errors)} файлах")
        
    except Exception as e:
        print(f"❌ Ошибка при анализе: {e}")

if __name__ == "__main__":
    show_all_errors()