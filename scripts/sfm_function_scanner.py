#!/usr/bin/env python3
"""
🔧 СКАНЕР ФУНКЦИЙ SFM (Safe Function Manager)
============================================

Этот скрипт специально ищет все функции, зарегистрированные в SFM.
Анализирует скрипты регистрации и находит все функции безопасности.

Автор: AI Assistant
Дата: 2024
Версия: 1.0
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Any

class SFMFunctionScanner:
    """Сканер функций SFM"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.exclude_dirs = {
            'backups', 'tests', 'logs', 'formatting_work', 
            '__pycache__', '.git', '.pytest_cache', 'node_modules',
            'venv', 'env', '.env', 'temp', 'tmp'
        }
        self.sfm_functions = []
        self.registration_scripts = []
        self.function_categories = defaultdict(list)

    def should_exclude_path(self, path: Path) -> bool:
        """Проверяет, нужно ли исключить путь"""
        for part in path.parts:
            if part.lower() in self.exclude_dirs:
                return True
        return False

    def scan_sfm_registration_scripts(self) -> None:
        """Сканирует скрипты регистрации SFM"""
        print("🔍 Сканирую скрипты регистрации SFM...")
        
        # Паттерны для поиска SFM функций
        patterns = {
            'register_function': r'register_function\s*\(\s*["\']([^"\']+)["\']',
            'function_id': r'function_id\s*[:=]\s*["\']([^"\']+)["\']',
            'function_name': r'name\s*[:=]\s*["\']([^"\']+)["\']',
            'function_description': r'description\s*[:=]\s*["\']([^"\']+)["\']',
            'function_type': r'type\s*[:=]\s*["\']([^"\']+)["\']',
            'security_level': r'security_level\s*[:=]\s*["\']([^"\']+)["\']',
            'is_critical': r'is_critical\s*[:=]\s*(True|False)',
            'auto_enable': r'auto_enable\s*[:=]\s*(True|False)'
        }
        
        for root, dirs, files in os.walk(self.base_path):
            dirs[:] = [d for d in dirs if d.lower() not in self.exclude_dirs]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    if not self.should_exclude_path(file_path):
                        self.analyze_sfm_file(file_path, patterns)

    def analyze_sfm_file(self, file_path: Path, patterns: Dict[str, str]) -> None:
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
                
                # Ищем функции по паттернам
                current_function = {}
                in_function_block = False
                
                for i, line in enumerate(lines):
                    line = line.strip()
                    
                    # Начало блока функции
                    if 'register_function' in line or 'function_id' in line:
                        in_function_block = True
                        current_function = {
                            'file': str(file_path),
                            'line': i + 1,
                            'raw_content': line
                        }
                    
                    # Поиск параметров функции
                    if in_function_block:
                        for param, pattern in patterns.items():
                            match = re.search(pattern, line)
                            if match:
                                current_function[param] = match.group(1) if match.groups() else match.group(0)
                        
                        # Конец блока функции (пустая строка или новая функция)
                        if not line or ('register_function' in line and current_function.get('function_id')):
                            if current_function.get('function_id'):
                                self.sfm_functions.append(current_function.copy())
                                # Категоризируем функцию
                                func_type = current_function.get('function_type', 'unknown')
                                self.function_categories[func_type].append(current_function)
                            current_function = {}
                            in_function_block = False
                
        except Exception as e:
            print(f"Ошибка анализа {file_path}: {e}")

    def find_functions_by_category(self, category: str) -> List[Dict]:
        """Находит функции по категории"""
        return self.function_categories.get(category, [])

    def find_critical_functions(self) -> List[Dict]:
        """Находит критические функции"""
        return [func for func in self.sfm_functions if func.get('is_critical') == 'True']

    def find_auto_enabled_functions(self) -> List[Dict]:
        """Находит автоматически включаемые функции"""
        return [func for func in self.sfm_functions if func.get('auto_enable') == 'True']

    def get_statistics(self) -> Dict:
        """Получает статистику SFM функций"""
        stats = {
            'total_functions': len(self.sfm_functions),
            'registration_scripts': len(self.registration_scripts),
            'categories': dict(self.function_categories),
            'critical_functions': len(self.find_critical_functions()),
            'auto_enabled_functions': len(self.find_auto_enabled_functions()),
            'functions_by_file': defaultdict(int),
            'functions_by_type': defaultdict(int)
        }
        
        for func in self.sfm_functions:
            stats['functions_by_file'][func['file']] += 1
            func_type = func.get('function_type', 'unknown')
            stats['functions_by_type'][func_type] += 1
        
        return stats

    def print_detailed_report(self) -> None:
        """Выводит детальный отчет"""
        stats = self.get_statistics()
        
        print("\n🔧 ДЕТАЛЬНЫЙ ОТЧЕТ SFM ФУНКЦИЙ:")
        print("=" * 50)
        
        print(f"📊 ОБЩАЯ СТАТИСТИКА:")
        print(f"   🔧 Всего функций: {stats['total_functions']}")
        print(f"   📄 Скриптов регистрации: {stats['registration_scripts']}")
        print(f"   ⚠️  Критических функций: {stats['critical_functions']}")
        print(f"   🚀 Автовключенных функций: {stats['auto_enabled_functions']}")
        
        print(f"\n📁 ФУНКЦИИ ПО КАТЕГОРИЯМ:")
        for category, functions in stats['categories'].items():
            print(f"   {category.upper()}: {len(functions)} функций")
        
        print(f"\n📄 ФУНКЦИИ ПО ФАЙЛАМ:")
        for file_path, count in sorted(stats['functions_by_file'].items(), key=lambda x: x[1], reverse=True):
            print(f"   {file_path}: {count} функций")
        
        print(f"\n🏷️  ФУНКЦИИ ПО ТИПАМ:")
        for func_type, count in sorted(stats['functions_by_type'].items(), key=lambda x: x[1], reverse=True):
            print(f"   {func_type}: {count} функций")

    def print_functions_list(self) -> None:
        """Выводит список всех функций"""
        print("\n📋 СПИСОК ВСЕХ SFM ФУНКЦИЙ:")
        print("=" * 50)
        
        for i, func in enumerate(self.sfm_functions, 1):
            print(f"{i:3d}. {func.get('function_id', 'Unknown')}")
            print(f"     📄 Файл: {func['file']}")
            print(f"     📝 Описание: {func.get('function_description', 'Нет описания')}")
            print(f"     🏷️  Тип: {func.get('function_type', 'Unknown')}")
            print(f"     🔒 Уровень безопасности: {func.get('security_level', 'Unknown')}")
            print(f"     ⚠️  Критическая: {func.get('is_critical', 'Unknown')}")
            print(f"     🚀 Автовключение: {func.get('auto_enable', 'Unknown')}")
            print()

    def export_to_json(self, filename: str = "sfm_functions.json") -> str:
        """Экспортирует результаты в JSON"""
        data = {
            'timestamp': str(Path().cwd()),
            'statistics': self.get_statistics(),
            'functions': self.sfm_functions,
            'registration_scripts': self.registration_scripts
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return filename

    def export_to_txt(self, filename: str = "sfm_functions.txt") -> str:
        """Экспортирует результаты в текстовый файл"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("🔧 ПОЛНЫЙ СПИСОК SFM ФУНКЦИЙ\n")
            f.write("=" * 50 + "\n\n")
            
            stats = self.get_statistics()
            f.write("📊 СТАТИСТИКА:\n")
            f.write(f"   Всего функций: {stats['total_functions']}\n")
            f.write(f"   Скриптов регистрации: {stats['registration_scripts']}\n")
            f.write(f"   Критических функций: {stats['critical_functions']}\n")
            f.write(f"   Автовключенных функций: {stats['auto_enabled_functions']}\n\n")
            
            f.write("📋 ВСЕ ФУНКЦИИ:\n")
            for i, func in enumerate(self.sfm_functions, 1):
                f.write(f"{i:3d}. {func.get('function_id', 'Unknown')}\n")
                f.write(f"     Файл: {func['file']}\n")
                f.write(f"     Описание: {func.get('function_description', 'Нет описания')}\n")
                f.write(f"     Тип: {func.get('function_type', 'Unknown')}\n")
                f.write(f"     Уровень безопасности: {func.get('security_level', 'Unknown')}\n")
                f.write(f"     Критическая: {func.get('is_critical', 'Unknown')}\n")
                f.write(f"     Автовключение: {func.get('auto_enable', 'Unknown')}\n\n")
        
        return filename

    def run_scan(self) -> None:
        """Запускает полное сканирование"""
        print("🚀 ЗАПУСК СКАНИРОВАНИЯ SFM ФУНКЦИЙ")
        print("=" * 40)
        
        # Сканируем функции
        self.scan_sfm_registration_scripts()
        
        # Выводим отчет
        self.print_detailed_report()
        
        # Выводим список функций
        self.print_functions_list()
        
        # Экспортируем результаты
        json_file = self.export_to_json()
        txt_file = self.export_to_txt()
        
        print(f"\n💾 Результаты сохранены:")
        print(f"   📄 JSON: {json_file}")
        print(f"   📝 TXT: {txt_file}")
        print("\n🎉 СКАНИРОВАНИЕ ЗАВЕРШЕНО!")

def main():
    """Главная функция"""
    print("🔧 СКАНЕР ФУНКЦИЙ SFM")
    print("=" * 30)
    
    # Создаем сканер
    scanner = SFMFunctionScanner()
    
    # Запускаем сканирование
    scanner.run_scan()

if __name__ == "__main__":
    main()