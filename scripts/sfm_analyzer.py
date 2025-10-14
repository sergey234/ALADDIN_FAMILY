#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SFM Analyzer - Анализатор реестра функций SFM
Предоставляет актуальную статистику по функциям в System Function Manager

Использование:
    python3 scripts/sfm_analyzer.py
    python3 scripts/sfm_analyzer.py --detailed
    python3 scripts/sfm_analyzer.py --export csv
    python3 scripts/sfm_analyzer.py --status active
"""

import json
import argparse
import csv
from collections import Counter
from datetime import datetime
from pathlib import Path


class SFMAnalyzer:
    """Анализатор реестра функций SFM"""
    
    def __init__(self, registry_path: str = "data/sfm/function_registry.json"):
        self.registry_path = registry_path
        self.registry = None
        self.functions = {}
        self.load_registry()
    
    def load_registry(self):
        """Загрузка реестра функций"""
        try:
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                self.registry = json.load(f)
            self.functions = self.registry.get('functions', {})
        except FileNotFoundError:
            print(f"❌ Файл реестра не найден: {self.registry_path}")
            exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Ошибка парсинга JSON: {e}")
            exit(1)
    
    def get_basic_stats(self):
        """Получение базовой статистики"""
        total = len(self.functions)
        
        # Подсчет статусов
        statuses = Counter()
        for func_data in self.functions.values():
            status = func_data.get('status', 'unknown')
            statuses[status] += 1
        
        return {
            'total': total,
            'statuses': statuses,
            'version': self.registry.get('version', 'unknown'),
            'last_updated': self.registry.get('last_updated', 'unknown')
        }
    
    def get_detailed_stats(self):
        """Получение детальной статистики"""
        stats = self.get_basic_stats()
        
        # Дополнительная статистика
        critical_count = sum(1 for f in self.functions.values() if f.get('is_critical', False))
        auto_enable_count = sum(1 for f in self.functions.values() if f.get('auto_enable', False))
        emergency_wake_count = sum(1 for f in self.functions.values() if f.get('emergency_wake_up', False))
        
        # Типы функций
        function_types = Counter(f.get('function_type', 'unknown') for f in self.functions.values())
        
        # Уровни безопасности
        security_levels = Counter(f.get('security_level', 'unknown') for f in self.functions.values())
        
        # Анализ по датам создания
        creation_dates = []
        for func_data in self.functions.values():
            created_at = func_data.get('created_at', '')
            if created_at:
                try:
                    date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    creation_dates.append(date_obj.strftime('%Y-%m-%d'))
                except:
                    pass
        
        date_counts = Counter(creation_dates)
        
        stats.update({
            'critical_functions': critical_count,
            'auto_enable_functions': auto_enable_count,
            'emergency_wake_functions': emergency_wake_count,
            'function_types': function_types,
            'security_levels': security_levels,
            'creation_dates': date_counts
        })
        
        return stats
    
    def print_basic_report(self):
        """Вывод базового отчета"""
        stats = self.get_basic_stats()
        
        print("=" * 50)
        print("📊 АКТУАЛЬНАЯ СТАТИСТИКА SFM")
        print("=" * 50)
        print(f"Версия реестра: {stats['version']}")
        print(f"Последнее обновление: {stats['last_updated']}")
        print()
        
        total = stats['total']
        statuses = stats['statuses']
        
        print("Параметр\t\tЗначение\tПроцент")
        print("-" * 50)
        print(f"Всего функций\t\t{total}\t\t100.0%")
        
        # Основные статусы
        active = statuses.get('active', 0)
        sleeping = statuses.get('sleeping', 0)
        running = statuses.get('running', 0)
        
        print(f"Активные\t\t{active}\t\t{(active/total)*100:.1f}%")
        print(f"Спящие\t\t\t{sleeping}\t\t{(sleeping/total)*100:.1f}%")
        print(f"Работающие\t\t{running}\t\t{(running/total)*100:.1f}%")
        
        # Другие статусы
        other_statuses = {k: v for k, v in statuses.items() if k not in ['active', 'sleeping', 'running']}
        if other_statuses:
            print("\nДругие статусы:")
            for status, count in sorted(other_statuses.items()):
                print(f"{status}\t\t\t{count}\t\t{(count/total)*100:.1f}%")
    
    def print_detailed_report(self):
        """Вывод детального отчета"""
        self.print_basic_report()
        
        stats = self.get_detailed_stats()
        total = stats['total']
        
        print("\n" + "=" * 50)
        print("📈 ДЕТАЛЬНАЯ СТАТИСТИКА")
        print("=" * 50)
        
        # Критические функции
        print(f"\n🔴 Критические функции: {stats['critical_functions']} ({(stats['critical_functions']/total)*100:.1f}%)")
        print(f"🔄 Автоматически включаемые: {stats['auto_enable_functions']} ({(stats['auto_enable_functions']/total)*100:.1f}%)")
        print(f"🚨 Экстренное пробуждение: {stats['emergency_wake_functions']} ({(stats['emergency_wake_functions']/total)*100:.1f}%)")
        
        # Типы функций
        print(f"\n📋 Топ-5 типов функций:")
        for func_type, count in stats['function_types'].most_common(5):
            print(f"  {func_type}: {count} ({(count/total)*100:.1f}%)")
        
        # Уровни безопасности
        print(f"\n🛡️ Уровни безопасности:")
        for level, count in stats['security_levels'].most_common():
            print(f"  {level}: {count} ({(count/total)*100:.1f}%)")
        
        # Даты создания
        if stats['creation_dates']:
            print(f"\n📅 Функции по датам создания:")
            for date, count in sorted(stats['creation_dates'].items()):
                print(f"  {date}: {count} функций")
    
    def print_functions_by_status(self, status: str):
        """Вывод функций по конкретному статусу"""
        functions_with_status = {
            func_id: func_data for func_id, func_data in self.functions.items()
            if func_data.get('status') == status
        }
        
        if not functions_with_status:
            print(f"❌ Функции со статусом '{status}' не найдены")
            return
        
        print(f"\n📋 ФУНКЦИИ СО СТАТУСОМ: {status.upper()} ({len(functions_with_status)} функций)")
        print("=" * 60)
        
        # Группируем по типам
        type_groups = {}
        for func_id, func_data in functions_with_status.items():
            func_type = func_data.get('function_type', 'unknown')
            if func_type not in type_groups:
                type_groups[func_type] = []
            type_groups[func_type].append({
                'id': func_id,
                'name': func_data.get('name', 'Unknown'),
                'critical': func_data.get('is_critical', False)
            })
        
        for func_type, funcs in type_groups.items():
            print(f"\n--- {func_type.upper()} ({len(funcs)} функций) ---")
            critical_count = sum(1 for f in funcs if f['critical'])
            if critical_count > 0:
                print(f"  (критических: {critical_count})")
            
            for func in funcs:
                critical_mark = ' [КРИТИЧЕСКАЯ]' if func['critical'] else ''
                print(f"  - {func['name']} ({func['id']}){critical_mark}")
    
    def export_to_csv(self, filename: str = None):
        """Экспорт статистики в CSV"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sfm_statistics_{timestamp}.csv"
        
        stats = self.get_detailed_stats()
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Заголовки
            writer.writerow(['Параметр', 'Значение', 'Процент'])
            writer.writerow([])
            
            # Основная статистика
            total = stats['total']
            statuses = stats['statuses']
            
            writer.writerow(['Всего функций', total, '100.0%'])
            writer.writerow(['Активные', statuses.get('active', 0), f"{(statuses.get('active', 0)/total)*100:.1f}%"])
            writer.writerow(['Спящие', statuses.get('sleeping', 0), f"{(statuses.get('sleeping', 0)/total)*100:.1f}%"])
            writer.writerow(['Работающие', statuses.get('running', 0), f"{(statuses.get('running', 0)/total)*100:.1f}%"])
            writer.writerow([])
            
            # Дополнительная статистика
            writer.writerow(['Критические функции', stats['critical_functions'], f"{(stats['critical_functions']/total)*100:.1f}%"])
            writer.writerow(['Автоматически включаемые', stats['auto_enable_functions'], f"{(stats['auto_enable_functions']/total)*100:.1f}%"])
            writer.writerow(['Экстренное пробуждение', stats['emergency_wake_functions'], f"{(stats['emergency_wake_functions']/total)*100:.1f}%"])
            writer.writerow([])
            
            # Типы функций
            writer.writerow(['ТИПЫ ФУНКЦИЙ'])
            for func_type, count in stats['function_types'].most_common():
                writer.writerow([func_type, count, f"{(count/total)*100:.1f}%"])
            writer.writerow([])
            
            # Уровни безопасности
            writer.writerow(['УРОВНИ БЕЗОПАСНОСТИ'])
            for level, count in stats['security_levels'].most_common():
                writer.writerow([level, count, f"{(count/total)*100:.1f}%"])
        
        print(f"✅ Статистика экспортирована в файл: {filename}")
    
    def get_quick_stats(self):
        """Быстрая статистика для API"""
        stats = self.get_basic_stats()
        total = stats['total']
        statuses = stats['statuses']
        
        return {
            'total_functions': total,
            'active': statuses.get('active', 0),
            'sleeping': statuses.get('sleeping', 0),
            'running': statuses.get('running', 0),
            'active_percent': (statuses.get('active', 0)/total)*100,
            'sleeping_percent': (statuses.get('sleeping', 0)/total)*100,
            'running_percent': (statuses.get('running', 0)/total)*100,
            'last_updated': stats['last_updated']
        }


def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(description='Анализатор реестра функций SFM')
    parser.add_argument('--detailed', '-d', action='store_true', 
                       help='Показать детальную статистику')
    parser.add_argument('--status', '-s', type=str, 
                       help='Показать функции с определенным статусом (active, sleeping, running)')
    parser.add_argument('--export', '-e', type=str, choices=['csv'], 
                       help='Экспортировать статистику в файл')
    parser.add_argument('--registry', '-r', type=str, default='data/sfm/function_registry.json',
                       help='Путь к файлу реестра функций')
    
    args = parser.parse_args()
    
    # Создаем анализатор
    analyzer = SFMAnalyzer(args.registry)
    
    # Выполняем действия в зависимости от аргументов
    if args.status:
        analyzer.print_functions_by_status(args.status)
    elif args.export:
        if args.export == 'csv':
            analyzer.export_to_csv()
    elif args.detailed:
        analyzer.print_detailed_report()
    else:
        analyzer.print_basic_report()


if __name__ == "__main__":
    main()