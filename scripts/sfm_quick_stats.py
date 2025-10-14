#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SFM Quick Stats - Быстрая статистика SFM
Простой скрипт для получения актуальной статистики SFM одной командой
"""

import json
from collections import Counter
from datetime import datetime


def get_sfm_stats():
    """Получение быстрой статистики SFM"""
    try:
        # Загружаем реестр
        with open('data/sfm/function_registry.json', 'r', encoding='utf-8') as f:
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
            'last_updated': registry.get('last_updated', 'unknown')
        }
    
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None


def print_stats():
    """Вывод статистики в табличном формате"""
    stats = get_sfm_stats()
    if not stats:
        return
    
    print("📊 АКТУАЛЬНАЯ СТАТИСТИКА SFM")
    print("=" * 40)
    print(f"Обновлено: {stats['last_updated']}")
    print()
    print("Параметр\t\tЗначение\tПроцент")
    print("-" * 40)
    
    total = stats['total']
    print(f"Всего функций\t\t{total}\t\t100.0%")
    print(f"Активные\t\t{stats['active']}\t\t{(stats['active']/total)*100:.1f}%")
    print(f"Спящие\t\t\t{stats['sleeping']}\t\t{(stats['sleeping']/total)*100:.1f}%")
    print(f"Работающие\t\t{stats['running']}\t\t{(stats['running']/total)*100:.1f}%")
    print(f"Критические\t\t{stats['critical']}\t\t{(stats['critical']/total)*100:.1f}%")


if __name__ == "__main__":
    print_stats()