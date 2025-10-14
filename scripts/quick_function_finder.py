#!/usr/bin/env python3
"""
🔍 БЫСТРЫЙ ПОИСКОВИК ФУНКЦИЙ СИСТЕМЫ БЕЗОПАСНОСТИ ALADDIN
=======================================================

Этот скрипт быстро находит все функции в системе безопасности ALADDIN.
Используется для быстрого поиска и анализа функций.

Автор: AI Assistant
Дата: 2024
Версия: 1.0
"""

import os
import re
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Tuple

class QuickFunctionFinder:
    """Быстрый поисковик функций"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.exclude_dirs = {
            'backups', 'tests', 'logs', 'formatting_work', 
            '__pycache__', '.git', '.pytest_cache', 'node_modules',
            'venv', 'env', '.env', 'temp', 'tmp'
        }
        self.functions = []
        self.sfm_functions = []
        self.classes = []
        self.imports = []

    def should_exclude_path(self, path: Path) -> bool:
        """Проверяет, нужно ли исключить путь"""
        for part in path.parts:
            if part.lower() in self.exclude_dirs:
                return True
        return False

    def find_functions_in_file(self, file_path: Path) -> List[Dict]:
        """Находит функции в файле"""
        functions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
                for i, line in enumerate(lines):
                    line = line.strip()
                    
                    # Обычные функции
                    if line.startswith('def '):
                        func_match = re.match(r'def\s+(\w+)\s*\(', line)
                        if func_match:
                            func_name = func_match.group(1)
                            functions.append({
                                'name': func_name,
                                'line': i + 1,
                                'type': 'function',
                                'file': str(file_path),
                                'content': line
                            })
                    
                    # Методы классов
                    elif re.match(r'^\s+def\s+\w+', line):
                        func_match = re.match(r'def\s+(\w+)\s*\(', line)
                        if func_match:
                            func_name = func_match.group(1)
                            functions.append({
                                'name': func_name,
                                'line': i + 1,
                                'type': 'method',
                                'file': str(file_path),
                                'content': line
                            })
                    
                    # Классы
                    elif line.startswith('class '):
                        class_match = re.match(r'class\s+(\w+)', line)
                        if class_match:
                            class_name = class_match.group(1)
                            self.classes.append({
                                'name': class_name,
                                'line': i + 1,
                                'file': str(file_path),
                                'content': line
                            })
                    
                    # Импорты
                    elif line.startswith(('import ', 'from ')):
                        self.imports.append({
                            'line': i + 1,
                            'file': str(file_path),
                            'content': line
                        })
                    
                    # SFM функции - только уникальные регистрации
                    if 'register_function' in line and 'function_id' in line:
                        # Ищем function_id в строке
                        func_id_match = re.search(r'function_id\s*[:=]\s*["\']([^"\']+)["\']', line)
                        if func_id_match:
                            func_id = func_id_match.group(1)
                            if func_id not in [sfm['function_id'] for sfm in self.sfm_functions]:
                                self.sfm_functions.append({
                                    'function_id': func_id,
                                    'file': str(file_path),
                                    'line': i + 1,
                                    'content': line
                                })
                
        except Exception as e:
            print(f"Ошибка чтения {file_path}: {e}")
        
        return functions

    def scan_all_files(self) -> None:
        """Сканирует все файлы"""
        print("🔍 Сканирую все файлы...")
        
        for root, dirs, files in os.walk(self.base_path):
            # Исключаем ненужные директории
            dirs[:] = [d for d in dirs if d.lower() not in self.exclude_dirs]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    if not self.should_exclude_path(file_path):
                        functions = self.find_functions_in_file(file_path)
                        self.functions.extend(functions)

    def get_statistics(self) -> Dict:
        """Получает статистику"""
        stats = {
            'total_functions': len(self.functions),
            'total_classes': len(self.classes),
            'total_imports': len(self.imports),
            'total_sfm_functions': len(self.sfm_functions),
            'functions_by_type': defaultdict(int),
            'functions_by_file': defaultdict(int)
        }
        
        for func in self.functions:
            stats['functions_by_type'][func['type']] += 1
            stats['functions_by_file'][func['file']] += 1
        
        return stats

    def print_summary(self) -> None:
        """Выводит краткую сводку"""
        stats = self.get_statistics()
        
        print("\n📊 КРАТКАЯ СВОДКА:")
        print(f"   ⚙️  Всего функций: {stats['total_functions']}")
        print(f"   🏗️  Всего классов: {stats['total_classes']}")
        print(f"   📦 Всего импортов: {stats['total_imports']}")
        print(f"   🔧 SFM функций: {stats['total_sfm_functions']}")
        
        print(f"\n📁 Функции по типам:")
        for func_type, count in stats['functions_by_type'].items():
            print(f"   {func_type}: {count}")
        
        print(f"\n📄 Топ файлов по количеству функций:")
        top_files = sorted(stats['functions_by_file'].items(), key=lambda x: x[1], reverse=True)[:10]
        for file_path, count in top_files:
            print(f"   {file_path}: {count} функций")

    def find_functions_by_name(self, name_pattern: str) -> List[Dict]:
        """Находит функции по имени"""
        pattern = re.compile(name_pattern, re.IGNORECASE)
        found = []
        
        for func in self.functions:
            if pattern.search(func['name']):
                found.append(func)
        
        return found

    def find_functions_by_file(self, file_pattern: str) -> List[Dict]:
        """Находит функции по файлу"""
        pattern = re.compile(file_pattern, re.IGNORECASE)
        found = []
        
        for func in self.functions:
            if pattern.search(func['file']):
                found.append(func)
        
        return found

    def export_to_file(self, filename: str = "functions_export.txt") -> None:
        """Экспортирует результаты в файл"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("🔍 ЭКСПОРТ ФУНКЦИЙ СИСТЕМЫ БЕЗОПАСНОСТИ ALADDIN\n")
            f.write("=" * 60 + "\n\n")
            
            # Статистика
            stats = self.get_statistics()
            f.write("📊 СТАТИСТИКА:\n")
            f.write(f"   Всего функций: {stats['total_functions']}\n")
            f.write(f"   Всего классов: {stats['total_classes']}\n")
            f.write(f"   Всего импортов: {stats['total_imports']}\n")
            f.write(f"   SFM функций: {stats['total_sfm_functions']}\n\n")
            
            # Все функции
            f.write("⚙️  ВСЕ ФУНКЦИИ:\n")
            for func in self.functions:
                f.write(f"   {func['name']} ({func['type']}) - {func['file']}:{func['line']}\n")
            
            f.write("\n🏗️  ВСЕ КЛАССЫ:\n")
            for cls in self.classes:
                f.write(f"   {cls['name']} - {cls['file']}:{cls['line']}\n")
            
            f.write("\n🔧 SFM ФУНКЦИИ:\n")
            for sfm_func in self.sfm_functions:
                f.write(f"   {sfm_func['file']}:{sfm_func['line']} - {sfm_func['content']}\n")
        
        print(f"💾 Результаты экспортированы в: {filename}")

def main():
    """Главная функция"""
    print("🔍 БЫСТРЫЙ ПОИСКОВИК ФУНКЦИЙ ALADDIN")
    print("=" * 40)
    
    # Создаем поисковик
    finder = QuickFunctionFinder()
    
    # Сканируем файлы
    finder.scan_all_files()
    
    # Выводим сводку
    finder.print_summary()
    
    # Экспортируем результаты
    finder.export_to_file()
    
    print("\n🎉 ПОИСК ЗАВЕРШЕН!")

if __name__ == "__main__":
    main()