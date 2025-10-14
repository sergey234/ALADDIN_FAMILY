#!/usr/bin/env python3
"""
Создание таблицы сравнения backup файлов с оригиналами
"""

import os
import json
from pathlib import Path

def create_comparison_table():
    # Пути
    backup_dir = Path('/Users/sergejhlystov/ALADDIN_NEW/security/formatting_work/backup_files')
    base_dir = Path('/Users/sergejhlystov/ALADDIN_NEW')

    # Получаем список backup файлов
    backup_files = []
    for file in backup_dir.glob('*.py'):
        if file.is_file():
            backup_files.append(file)

    # Сортируем по размеру
    backup_files.sort(key=lambda x: x.stat().st_size, reverse=True)

    print('📊 ТАБЛИЦА СРАВНЕНИЯ: BACKUP vs ОРИГИНАЛ')
    print('=' * 120)
    print(f'{"№":<3} | {"BACKUP ФАЙЛ":<50} | {"РАЗМЕР":<8} | {"ОРИГИНАЛ":<50} | {"РАЗМЕР":<8} | {"СТАТУС":<10}')
    print('-' * 120)

    found_count = 0
    not_found_count = 0

    for i, backup_file in enumerate(backup_files, 1):
        backup_name = backup_file.name
        backup_size = backup_file.stat().st_size
        
        # Очищаем имя от backup суффиксов
        original_name = backup_name
        for suffix in [
            '_backup_original_backup_20250103',
            '.backup_20250909_212030',
            '.backup_20250909_212748', 
            '.backup_20250909_213215',
            '.backup_20250928_003043',
            '.backup_20250928_002228',
            '.backup_20250927_231340',
            '.backup_20250927_231341',
            '.backup_20250927_231342',
            '.backup_20250927_232629',
            '.backup_20250927_233351',
            '.backup_20250927_234000',
            '.backup_20250927_234616',
            '.backup_20250928_000215',
            '.backup_20250928_003940',
            '.backup_20250928_005946',
            '_before_formatting',
            '.backup_011225',
            '_BACKUP',
            '_backup'
        ]:
            original_name = original_name.replace(suffix, '')
        
        # Ищем оригинал
        original_found = False
        original_size = 0
        original_path = ''
        
        for root, dirs, files in os.walk(base_dir / 'security'):
            if 'formatting_work' in root:
                continue
            for file in files:
                if file == original_name:
                    original_path = os.path.join(root, file)
                    original_size = os.path.getsize(original_path)
                    original_found = True
                    break
            if original_found:
                break
        
        if original_found:
            found_count += 1
            status = '✅ НАЙДЕН'
        else:
            not_found_count += 1
            status = '❌ НЕ НАЙДЕН'
        
        # Обрезаем длинные имена
        original_display = original_name[:47] + '...' if len(original_name) > 50 else original_name
        backup_display = backup_name[:47] + '...' if len(backup_name) > 50 else backup_name
        
        print(f'{i:<3} | {backup_display:<50} | {backup_size:<8} | {original_display:<50} | {original_size:<8} | {status:<10}')

    print('-' * 120)
    print(f'📈 ИТОГО BACKUP ФАЙЛОВ: {len(backup_files)}')
    print(f'✅ НАЙДЕНО ОРИГИНАЛОВ: {found_count}')
    print(f'❌ НЕ НАЙДЕНО: {not_found_count}')
    print(f'📊 ПРОЦЕНТ НАЙДЕННЫХ: {(found_count/len(backup_files)*100):.1f}%')

if __name__ == "__main__":
    create_comparison_table()