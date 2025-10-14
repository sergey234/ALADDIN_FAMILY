#!/usr/bin/env python3
"""
🔍 ИСТИННЫЙ СЧЕТЧИК ФУНКЦИЙ SFM
===============================

Этот скрипт находит ВСЕ функции, зарегистрированные в SFM,
включая спящие функции и все скрипты регистрации.

Автор: AI Assistant
Дата: 2024
Версия: 1.0
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict, Counter
from typing import List, Dict, Any

class TrueSFMFunctionCounter:
    """Истинный счетчик функций SFM"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.exclude_dirs = {
            'backups', 'tests', 'logs', 'formatting_work', 
            '__pycache__', '.git', '.pytest_cache', 'node_modules',
            'venv', 'env', '.env', 'temp', 'tmp', 'analysis_results'
        }
        self.sfm_functions = []
        self.registration_scripts = []
        self.function_categories = defaultdict(list)
        self.sleep_functions = []
        self.active_functions = []

    def should_exclude_path(self, path: Path) -> bool:
        """Проверяет, нужно ли исключить путь"""
        for part in path.parts:
            if part.lower() in self.exclude_dirs:
                return True
        return False

    def find_all_sfm_functions(self) -> None:
        """Находит ВСЕ функции SFM во всех файлах"""
        print("🔍 Ищу ВСЕ функции SFM во всех файлах...")
        
        # Паттерны для поиска SFM функций
        patterns = {
            'register_function': r'register_function\s*\(\s*["\']([^"\']+)["\']',
            'function_id': r'function_id\s*[:=]\s*["\']([^"\']+)["\']',
            'id":': r'"id":\s*["\']([^"\']+)["\']',
            'function_name': r'name\s*[:=]\s*["\']([^"\']+)["\']',
            'sleep_function': r'put_.*_to_sleep',
            'wake_function': r'wake_up_.*',
            'disable_function': r'disable_.*',
            'enable_function': r'enable_.*'
        }
        
        for root, dirs, files in os.walk(self.base_path):
            dirs[:] = [d for d in dirs if d.lower() not in self.exclude_dirs]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    if not self.should_exclude_path(file_path):
                        self.analyze_file_for_sfm_functions(file_path, patterns)

    def analyze_file_for_sfm_functions(self, file_path: Path, patterns: Dict[str, str]) -> None:
        """Анализирует файл на предмет SFM функций"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
                # Проверяем, является ли файл скриптом регистрации
                is_registration_script = any(keyword in content.lower() for keyword in [
                    'register_function', 'function_id', 'sfm', 'safe_function_manager'
                ])
                
                if is_registration_script:
                    self.registration_scripts.append(str(file_path))
                
                # Ищем функции по всем паттернам
                for i, line in enumerate(lines):
                    line = line.strip()
                    
                    # Поиск по всем паттернам
                    for pattern_name, pattern in patterns.items():
                        matches = re.findall(pattern, line, re.IGNORECASE)
                        for match in matches:
                            if isinstance(match, tuple):
                                match = match[0]
                            
                            # Добавляем функцию
                            func_info = {
                                'function_id': match,
                                'file': str(file_path),
                                'line': i + 1,
                                'pattern': pattern_name,
                                'content': line,
                                'is_sleep': 'sleep' in pattern_name.lower(),
                                'is_wake': 'wake' in pattern_name.lower(),
                                'is_disable': 'disable' in pattern_name.lower(),
                                'is_enable': 'enable' in pattern_name.lower()
                            }
                            
                            # Проверяем, не дублируется ли функция
                            if not any(f['function_id'] == match and f['file'] == str(file_path) for f in self.sfm_functions):
                                self.sfm_functions.append(func_info)
                                
                                # Категоризируем
                                if func_info['is_sleep']:
                                    self.sleep_functions.append(func_info)
                                elif func_info['is_wake'] or func_info['is_enable']:
                                    self.active_functions.append(func_info)
                                
                                # Определяем категорию по файлу
                                category = self.categorize_function_by_file(file_path)
                                self.function_categories[category].append(func_info)
                
        except Exception as e:
            print(f"Ошибка анализа {file_path}: {e}")

    def categorize_function_by_file(self, file_path: Path) -> str:
        """Определяет категорию функции по файлу"""
        path_str = str(file_path).lower()
        
        if 'family' in path_str:
            return 'FAMILY'
        elif 'vpn' in path_str:
            return 'VPN'
        elif 'ai_agents' in path_str:
            return 'AI_AGENTS'
        elif 'bots' in path_str:
            return 'BOTS'
        elif 'managers' in path_str:
            return 'MANAGERS'
        elif 'microservices' in path_str:
            return 'MICROSERVICES'
        elif 'antivirus' in path_str:
            return 'ANTIVIRUS'
        elif 'privacy' in path_str:
            return 'PRIVACY'
        elif 'compliance' in path_str:
            return 'COMPLIANCE'
        elif 'mobile' in path_str:
            return 'MOBILE'
        elif 'scripts' in path_str:
            return 'SCRIPTS'
        elif 'security' in path_str:
            return 'SECURITY'
        else:
            return 'OTHER'

    def get_detailed_statistics(self) -> Dict:
        """Получает детальную статистику"""
        stats = {
            'total_functions': len(self.sfm_functions),
            'registration_scripts': len(self.registration_scripts),
            'sleep_functions': len(self.sleep_functions),
            'active_functions': len(self.active_functions),
            'categories': dict(self.function_categories),
            'functions_by_file': defaultdict(int),
            'functions_by_pattern': defaultdict(int),
            'unique_functions': len(set(f['function_id'] for f in self.sfm_functions))
        }
        
        for func in self.sfm_functions:
            stats['functions_by_file'][func['file']] += 1
            stats['functions_by_pattern'][func['pattern']] += 1
        
        return stats

    def print_comprehensive_report(self) -> None:
        """Выводит комплексный отчет"""
        stats = self.get_detailed_statistics()
        
        print("\n🔍 ИСТИННЫЙ ОТЧЕТ О ФУНКЦИЯХ SFM")
        print("=" * 60)
        
        print(f"📊 ОБЩАЯ СТАТИСТИКА:")
        print(f"   🔧 Всего функций: {stats['total_functions']}")
        print(f"   🎯 Уникальных функций: {stats['unique_functions']}")
        print(f"   📄 Скриптов регистрации: {stats['registration_scripts']}")
        print(f"   😴 Спящих функций: {stats['sleep_functions']}")
        print(f"   🚀 Активных функций: {stats['active_functions']}")
        
        print(f"\n📁 ФУНКЦИИ ПО КАТЕГОРИЯМ:")
        for category, functions in stats['categories'].items():
            print(f"   {category}: {len(functions)} функций")
        
        print(f"\n📄 ТОП ФАЙЛОВ ПО КОЛИЧЕСТВУ ФУНКЦИЙ:")
        top_files = sorted(stats['functions_by_file'].items(), key=lambda x: x[1], reverse=True)[:10]
        for file_path, count in top_files:
            print(f"   {file_path}: {count} функций")
        
        print(f"\n🏷️  ФУНКЦИИ ПО ПАТТЕРНАМ:")
        for pattern, count in stats['functions_by_pattern'].items():
            print(f"   {pattern}: {count} функций")
        
        print(f"\n😴 СПЯЩИЕ ФУНКЦИИ:")
        for func in self.sleep_functions[:10]:  # Показываем первые 10
            print(f"   {func['function_id']} - {func['file']}")
        
        print(f"\n🚀 АКТИВНЫЕ ФУНКЦИИ:")
        for func in self.active_functions[:10]:  # Показываем первые 10
            print(f"   {func['function_id']} - {func['file']}")

    def export_results(self) -> None:
        """Экспортирует результаты"""
        stats = self.get_detailed_statistics()
        
        # JSON экспорт
        json_data = {
            'timestamp': str(Path().cwd()),
            'statistics': stats,
            'functions': self.sfm_functions,
            'sleep_functions': self.sleep_functions,
            'active_functions': self.active_functions,
            'registration_scripts': self.registration_scripts
        }
        
        with open('true_sfm_functions.json', 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        # TXT экспорт
        with open('true_sfm_functions.txt', 'w', encoding='utf-8') as f:
            f.write("🔍 ИСТИННЫЙ ОТЧЕТ О ФУНКЦИЯХ SFM\n")
            f.write("=" * 60 + "\n\n")
            
            f.write("📊 СТАТИСТИКА:\n")
            f.write(f"   Всего функций: {stats['total_functions']}\n")
            f.write(f"   Уникальных функций: {stats['unique_functions']}\n")
            f.write(f"   Скриптов регистрации: {stats['registration_scripts']}\n")
            f.write(f"   Спящих функций: {stats['sleep_functions']}\n")
            f.write(f"   Активных функций: {stats['active_functions']}\n\n")
            
            f.write("📋 ВСЕ ФУНКЦИИ:\n")
            for i, func in enumerate(self.sfm_functions, 1):
                f.write(f"{i:3d}. {func['function_id']}\n")
                f.write(f"     Файл: {func['file']}\n")
                f.write(f"     Паттерн: {func['pattern']}\n")
                f.write(f"     Спящая: {func['is_sleep']}\n")
                f.write(f"     Активная: {func['is_wake'] or func['is_enable']}\n\n")
        
        print(f"\n💾 Результаты сохранены:")
        print(f"   📄 JSON: true_sfm_functions.json")
        print(f"   📝 TXT: true_sfm_functions.txt")

    def run_analysis(self) -> None:
        """Запускает полный анализ"""
        print("🚀 ЗАПУСК ИСТИННОГО АНАЛИЗА SFM ФУНКЦИЙ")
        print("=" * 50)
        
        # Находим все функции
        self.find_all_sfm_functions()
        
        # Выводим отчет
        self.print_comprehensive_report()
        
        # Экспортируем результаты
        self.export_results()
        
        print("\n🎉 АНАЛИЗ ЗАВЕРШЕН!")

def main():
    """Главная функция"""
    print("🔍 ИСТИННЫЙ СЧЕТЧИК ФУНКЦИЙ SFM")
    print("=" * 40)
    
    # Создаем счетчик
    counter = TrueSFMFunctionCounter()
    
    # Запускаем анализ
    counter.run_analysis()

if __name__ == "__main__":
    main()