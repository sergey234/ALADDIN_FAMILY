#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SFM Universal Statistics - Универсальный скрипт статистики SFM
Автоматически находит и анализирует SFM реестр
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

class SFMUniversalStats:
    """Универсальный анализатор статистики SFM"""
    
    def __init__(self):
        self.registry_path = None
        self.registry_data = None
        self.find_registry()
    
    def find_registry(self):
        """Автоматический поиск SFM реестра"""
        possible_paths = [
            'data/sfm/function_registry.json',
            '../data/sfm/function_registry.json',
            '../../data/sfm/function_registry.json',
            'ALADDIN_NEW/data/sfm/function_registry.json'
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                self.registry_path = path
                print(f"✅ SFM реестр найден: {path}")
                break
        
        if not self.registry_path:
            print("❌ SFM реестр не найден!")
            print("Поиск в следующих местах:")
            for path in possible_paths:
                print(f"  - {path}")
            sys.exit(1)
    
    def load_registry(self):
        """Загрузка SFM реестра"""
        try:
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                self.registry_data = json.load(f)
            return True
        except Exception as e:
            print(f"❌ Ошибка загрузки реестра: {e}")
            return False
    
    def get_basic_stats(self):
        """Получение базовой статистики"""
        if not self.registry_data:
            return None
        
        functions = self.registry_data.get('functions', {})
        
        stats = {
            'total_functions': len(functions),
            'active_functions': 0,
            'sleeping_functions': 0,
            'critical_functions': 0,
            'functions_by_type': {},
            'functions_by_status': {},
            'last_updated': self.registry_data.get('last_updated', 'unknown')
        }
        
        for func_id, func_data in functions.items():
            if isinstance(func_data, dict):
                status = func_data.get('status', 'unknown')
                func_type = func_data.get('function_type', 'unknown')
                is_critical = func_data.get('is_critical', False)
                
                # Подсчет по статусу
                if status == 'active':
                    stats['active_functions'] += 1
                elif status == 'sleeping':
                    stats['sleeping_functions'] += 1
                
                # Подсчет критических
                if is_critical:
                    stats['critical_functions'] += 1
                
                # Подсчет по типам
                stats['functions_by_type'][func_type] = stats['functions_by_type'].get(func_type, 0) + 1
                stats['functions_by_status'][status] = stats['functions_by_status'].get(status, 0) + 1
        
        return stats
    
    def get_detailed_analysis(self):
        """Детальный анализ SFM"""
        if not self.registry_data:
            return None
        
        functions = self.registry_data.get('functions', {})
        
        analysis = {
            'total_functions': len(functions),
            'valid_functions': 0,
            'invalid_functions': 0,
            'functions_with_errors': [],
            'quality_metrics': {
                'a_plus_functions': 0,
                'functions_with_tests': 0,
                'functions_with_docs': 0
            },
            'security_analysis': {
                'high_security': 0,
                'critical_functions': 0,
                'auto_enable_functions': 0
            }
        }
        
        for func_id, func_data in functions.items():
            if isinstance(func_data, dict) and 'function_id' in func_data:
                analysis['valid_functions'] += 1
                
                # Качество
                quality_grade = func_data.get('quality_grade', '')
                if quality_grade == 'A+':
                    analysis['quality_metrics']['a_plus_functions'] += 1
                
                test_coverage = func_data.get('test_coverage', '')
                if test_coverage and test_coverage != '0%':
                    analysis['quality_metrics']['functions_with_tests'] += 1
                
                if 'description' in func_data and func_data['description']:
                    analysis['quality_metrics']['functions_with_docs'] += 1
                
                # Безопасность
                security_level = func_data.get('security_level', '')
                if security_level in ['high', 'critical']:
                    analysis['security_analysis']['high_security'] += 1
                
                if func_data.get('is_critical', False):
                    analysis['security_analysis']['critical_functions'] += 1
                
                if func_data.get('auto_enable', False):
                    analysis['security_analysis']['auto_enable_functions'] += 1
            else:
                analysis['invalid_functions'] += 1
                analysis['functions_with_errors'].append(func_id)
        
        return analysis
    
    def print_basic_stats(self):
        """Вывод базовой статистики"""
        stats = self.get_basic_stats()
        if not stats:
            return
        
        print("📊 УНИВЕРСАЛЬНАЯ СТАТИСТИКА SFM")
        print("=" * 50)
        print(f"Реестр: {self.registry_path}")
        print(f"Обновлено: {stats['last_updated']}")
        print()
        
        print("Параметр                Значение        Процент")
        print("-" * 50)
        print(f"{'Всего функций':<25} {stats['total_functions']:<15} 100.0%")
        
        if stats['total_functions'] > 0:
            active_pct = (stats['active_functions'] / stats['total_functions']) * 100
            sleeping_pct = (stats['sleeping_functions'] / stats['total_functions']) * 100
            critical_pct = (stats['critical_functions'] / stats['total_functions']) * 100
            
            print(f"{'Активные':<25} {stats['active_functions']:<15} {active_pct:.1f}%")
            print(f"{'Спящие':<25} {stats['sleeping_functions']:<15} {sleeping_pct:.1f}%")
            print(f"{'Критические':<25} {stats['critical_functions']:<15} {critical_pct:.1f}%")
        
        print()
        print("Функции по типам:")
        for func_type, count in sorted(stats['functions_by_type'].items()):
            pct = (count / stats['total_functions']) * 100 if stats['total_functions'] > 0 else 0
            print(f"  {func_type:<20} {count:<10} {pct:.1f}%")
    
    def print_detailed_analysis(self):
        """Вывод детального анализа"""
        analysis = self.get_detailed_analysis()
        if not analysis:
            return
        
        print("\n🔍 ДЕТАЛЬНЫЙ АНАЛИЗ SFM")
        print("=" * 50)
        
        print(f"Всего функций: {analysis['total_functions']}")
        print(f"Валидных: {analysis['valid_functions']}")
        print(f"Невалидных: {analysis['invalid_functions']}")
        
        if analysis['functions_with_errors']:
            print(f"Функции с ошибками: {', '.join(analysis['functions_with_errors'])}")
        
        print("\nКачество:")
        print(f"  A+ функции: {analysis['quality_metrics']['a_plus_functions']}")
        print(f"  С тестами: {analysis['quality_metrics']['functions_with_tests']}")
        print(f"  С документацией: {analysis['quality_metrics']['functions_with_docs']}")
        
        print("\nБезопасность:")
        print(f"  Высокий уровень: {analysis['security_analysis']['high_security']}")
        print(f"  Критические: {analysis['security_analysis']['critical_functions']}")
        print(f"  Автовключение: {analysis['security_analysis']['auto_enable_functions']}")
    
    def save_report(self):
        """Сохранение отчета"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"data/sfm/universal_stats_report_{timestamp}.json"
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'registry_path': self.registry_path,
            'basic_stats': self.get_basic_stats(),
            'detailed_analysis': self.get_detailed_analysis()
        }
        
        try:
            os.makedirs(os.path.dirname(report_file), exist_ok=True)
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"\n✅ Отчет сохранен: {report_file}")
        except Exception as e:
            print(f"❌ Ошибка сохранения отчета: {e}")

def main():
    """Главная функция"""
    print("🚀 SFM UNIVERSAL STATISTICS")
    print("=" * 50)
    
    sfm = SFMUniversalStats()
    
    if not sfm.load_registry():
        sys.exit(1)
    
    sfm.print_basic_stats()
    sfm.print_detailed_analysis()
    sfm.save_report()
    
    print("\n🎉 Анализ завершен!")

if __name__ == "__main__":
    main()