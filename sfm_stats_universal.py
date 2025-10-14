#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SFM Stats Universal - Универсальный анализатор SFM
Работает из любой директории, автоматически находит реестр функций
"""

import json
import os
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path


def find_registry_file():
    """Поиск файла реестра функций в различных возможных местах"""
    possible_paths = [
        # Текущая директория
        'data/sfm/function_registry.json',
        './data/sfm/function_registry.json',
        
        # Относительно скрипта
        os.path.join(os.path.dirname(__file__), 'data/sfm/function_registry.json'),
        os.path.join(os.path.dirname(__file__), '..', 'data/sfm/function_registry.json'),
        
        # Абсолютные пути
        '/Users/sergejhlystov/ALADDIN_NEW/data/sfm/function_registry.json',
        '/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/data/sfm/function_registry.json',
        
        # Поиск в родительских директориях
        os.path.join(os.path.dirname(__file__), '..', '..', 'data/sfm/function_registry.json'),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # Поиск рекурсивно
    current_dir = Path(__file__).parent
    for registry_file in current_dir.rglob('function_registry.json'):
        if 'sfm' in str(registry_file):
            return str(registry_file)
    
    return None


def get_sfm_stats():
    """Получение быстрой статистики SFM"""
    registry_path = find_registry_file()
    
    if not registry_path:
        print("❌ Файл реестра функций не найден!")
        print("Искал в следующих местах:")
        print("  - data/sfm/function_registry.json")
        print("  - ./data/sfm/function_registry.json")
        print("  - /Users/sergejhlystov/ALADDIN_NEW/data/sfm/function_registry.json")
        print("  - рекурсивно в текущей директории")
        return None
    
    try:
        print(f"📁 Используется файл: {registry_path}")
        
        with open(registry_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        functions = registry.get('functions', {})
        total = len(functions)
        
        # Подсчитываем статусы
        statuses = Counter()
        for func_data in functions.values():
            status = func_data.get('status', 'unknown')
            statuses[status] += 1
        
        # Основные статусы
        active = statuses.get('active', 0)
        sleeping = statuses.get('sleeping', 0)
        running = statuses.get('running', 0)
        
        # Дополнительная статистика
        critical = sum(1 for f in functions.values() if f.get('is_critical', False))
        
        return {
            'total': total,
            'active': active,
            'sleeping': sleeping,
            'running': running,
            'critical': critical,
            'last_updated': registry.get('last_updated', 'unknown'),
            'version': registry.get('version', 'unknown'),
            'registry_path': registry_path
        }
    
    except Exception as e:
        print(f"❌ Ошибка чтения файла {registry_path}: {e}")
        return None


def print_stats():
    """Вывод статистики в табличном формате"""
    stats = get_sfm_stats()
    if not stats:
        return
    
    print("📊 АКТУАЛЬНАЯ СТАТИСТИКА SFM")
    print("=" * 50)
    print(f"Версия реестра: {stats['version']}")
    print(f"Обновлено: {stats['last_updated']}")
    print(f"Файл: {stats['registry_path']}")
    print()
    print("Параметр\t\tЗначение\tПроцент")
    print("-" * 50)
    
    total = stats['total']
    print(f"Всего функций\t\t{total}\t\t100.0%")
    print(f"Активные\t\t{stats['active']}\t\t{(stats['active']/total)*100:.1f}%")
    print(f"Спящие\t\t\t{stats['sleeping']}\t\t{(stats['sleeping']/total)*100:.1f}%")
    print(f"Работающие\t\t{stats['running']}\t\t{(stats['running']/total)*100:.1f}%")
    print(f"Критические\t\t{stats['critical']}\t\t{(stats['critical']/total)*100:.1f}%")


def print_detailed_stats():
    """Вывод детальной статистики"""
    stats = get_sfm_stats()
    if not stats:
        return
    
    print_stats()
    
    try:
        with open(stats['registry_path'], 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        functions = registry.get('functions', {})
        total = stats['total']
        
        # Типы функций
        function_types = Counter(f.get('function_type', 'unknown') for f in functions.values())
        
        # Уровни безопасности
        security_levels = Counter(f.get('security_level', 'unknown') for f in functions.values())
        
        print("\n" + "=" * 50)
        print("📈 ДЕТАЛЬНАЯ СТАТИСТИКА")
        print("=" * 50)
        
        print(f"\n📋 Топ-5 типов функций:")
        for func_type, count in function_types.most_common(5):
            print(f"  {func_type}: {count} ({(count/total)*100:.1f}%)")
        
        print(f"\n🛡️ Уровни безопасности:")
        for level, count in security_levels.most_common():
            print(f"  {level}: {count} ({(count/total)*100:.1f}%)")
    
    except Exception as e:
        print(f"❌ Ошибка детального анализа: {e}")


def main():
    """Главная функция"""
    if len(sys.argv) > 1 and sys.argv[1] == '--detailed':
        print_detailed_stats()
    else:
        print_stats()


if __name__ == "__main__":
    main()