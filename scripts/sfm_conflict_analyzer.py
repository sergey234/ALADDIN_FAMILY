#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SFM Conflict Analyzer - Анализатор конфликтов функций в SFM
Проверяет дублирование функций, конфликты имен и наложения

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-11
"""

import os
import sys
import ast
import hashlib
from typing import Dict, List, Set, Tuple, Any
from collections import defaultdict
import json
from datetime import datetime

# Добавляем путь к проекту
sys.path.append('/Users/sergejhlystov/ALADDIN_NEW')

class SFMConflictAnalyzer:
    """Анализатор конфликтов функций в SFM"""
    
    def __init__(self):
        self.conflicts = []
        self.function_registry = {}
        self.class_registry = {}
        self.method_registry = defaultdict(list)
        self.file_checksums = {}
        self.duplicate_files = []
        
    def analyze_sfm_conflicts(self) -> Dict[str, Any]:
        """Основной анализ конфликтов в SFM"""
        print("🔍 Анализ конфликтов функций в SFM...")
        
        # 1. Анализ зарегистрированных функций в SFM
        sfm_functions = self.analyze_sfm_registry()
        
        # 2. Анализ файлов системы
        system_functions = self.analyze_system_files()
        
        # 3. Поиск дублирования функций
        duplicates = self.find_function_duplicates(sfm_functions, system_functions)
        
        # 4. Поиск конфликтов имен классов
        class_conflicts = self.find_class_conflicts()
        
        # 5. Поиск конфликтов методов
        method_conflicts = self.find_method_conflicts()
        
        # 6. Поиск дублирующихся файлов
        file_duplicates = self.find_file_duplicates()
        
        # 7. Анализ зависимостей
        dependency_conflicts = self.analyze_dependencies()
        
        # 8. Генерация отчета
        report = self.generate_conflict_report({
            'sfm_functions': sfm_functions,
            'system_functions': system_functions,
            'duplicates': duplicates,
            'class_conflicts': class_conflicts,
            'method_conflicts': method_conflicts,
            'file_duplicates': file_duplicates,
            'dependency_conflicts': dependency_conflicts
        })
        
        return report
    
    def analyze_sfm_registry(self) -> Dict[str, Any]:
        """Анализ зарегистрированных функций в SFM"""
        print("📋 Анализ реестра SFM...")
        
        try:
            from security.safe_function_manager import SafeFunctionManager
            
            # Создаем экземпляр SFM
            sfm = SafeFunctionManager("ConflictAnalyzer")
            
            # Получаем зарегистрированные функции
            registered_functions = {}
            for func_id, func_info in sfm.functions.items():
                registered_functions[func_id] = {
                    'name': func_info.name,
                    'type': func_info.function_type,
                    'status': func_info.status.value,
                    'security_level': func_info.security_level.value,
                    'is_critical': getattr(func_info, 'is_critical', False),
                    'file_path': getattr(func_info, 'file_path', 'unknown')
                }
            
            print(f"✅ Найдено {len(registered_functions)} зарегистрированных функций в SFM")
            return registered_functions
            
        except Exception as e:
            print(f"❌ Ошибка анализа SFM: {e}")
            return {}
    
    def analyze_system_files(self) -> Dict[str, Any]:
        """Анализ файлов системы на предмет функций"""
        print("📁 Анализ файлов системы...")
        
        system_functions = {}
        directories = [
            '/Users/sergejhlystov/ALADDIN_NEW/security',
            '/Users/sergejhlystov/ALADDIN_NEW/core',
            '/Users/sergejhlystov/ALADDIN_NEW/family'
        ]
        
        for directory in directories:
            if os.path.exists(directory):
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        if file.endswith('.py'):
                            file_path = os.path.join(root, file)
                            functions = self.extract_functions_from_file(file_path)
                            if functions:
                                system_functions[file_path] = functions
        
        print(f"✅ Найдено {len(system_functions)} файлов с функциями")
        return system_functions
    
    def extract_functions_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Извлечение функций из файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            functions = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Анализ классов
                    class_info = {
                        'type': 'class',
                        'name': node.name,
                        'line': node.lineno,
                        'methods': []
                    }
                    
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_info = {
                                'type': 'method',
                                'name': item.name,
                                'line': item.lineno,
                                'class': node.name
                            }
                            class_info['methods'].append(method_info)
                            functions.append(method_info)
                    
                    functions.append(class_info)
                
                elif isinstance(node, ast.FunctionDef):
                    # Анализ функций
                    func_info = {
                        'type': 'function',
                        'name': node.name,
                        'line': node.lineno,
                        'class': None
                    }
                    functions.append(func_info)
            
            return functions
            
        except Exception as e:
            print(f"⚠️ Ошибка анализа файла {file_path}: {e}")
            return []
    
    def find_function_duplicates(self, sfm_functions: Dict, system_functions: Dict) -> List[Dict]:
        """Поиск дублирующихся функций"""
        print("🔍 Поиск дублирующихся функций...")
        
        duplicates = []
        sfm_names = set(sfm_functions.keys())
        
        for file_path, functions in system_functions.items():
            for func in functions:
                func_name = func['name']
                
                # Проверка дублирования с SFM
                if func_name in sfm_names:
                    duplicates.append({
                        'type': 'sfm_duplicate',
                        'function_name': func_name,
                        'sfm_id': func_name,
                        'file_path': file_path,
                        'line': func['line'],
                        'severity': 'high'
                    })
                
                # Проверка дублирования внутри файла
                same_name_functions = [f for f in functions if f['name'] == func_name]
                if len(same_name_functions) > 1:
                    duplicates.append({
                        'type': 'file_duplicate',
                        'function_name': func_name,
                        'file_path': file_path,
                        'count': len(same_name_functions),
                        'lines': [f['line'] for f in same_name_functions],
                        'severity': 'medium'
                    })
        
        print(f"✅ Найдено {len(duplicates)} дублирующихся функций")
        return duplicates
    
    def find_class_conflicts(self) -> List[Dict]:
        """Поиск конфликтов имен классов"""
        print("🏗️ Поиск конфликтов имен классов...")
        
        class_conflicts = []
        class_locations = defaultdict(list)
        
        # Сбор всех классов из системы
        directories = [
            '/Users/sergejhlystov/ALADDIN_NEW/security',
            '/Users/sergejhlystov/ALADDIN_NEW/core',
            '/Users/sergejhlystov/ALADDIN_NEW/family'
        ]
        
        for directory in directories:
            if os.path.exists(directory):
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        if file.endswith('.py'):
                            file_path = os.path.join(root, file)
                            classes = self.extract_classes_from_file(file_path)
                            
                            for class_info in classes:
                                class_locations[class_info['name']].append({
                                    'file_path': file_path,
                                    'line': class_info['line']
                                })
        
        # Поиск конфликтов
        for class_name, locations in class_locations.items():
            if len(locations) > 1:
                class_conflicts.append({
                    'class_name': class_name,
                    'locations': locations,
                    'count': len(locations),
                    'severity': 'high' if len(locations) > 2 else 'medium'
                })
        
        print(f"✅ Найдено {len(class_conflicts)} конфликтов имен классов")
        return class_conflicts
    
    def extract_classes_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Извлечение классов из файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            classes = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append({
                        'name': node.name,
                        'line': node.lineno,
                        'file_path': file_path
                    })
            
            return classes
            
        except Exception as e:
            print(f"⚠️ Ошибка извлечения классов из {file_path}: {e}")
            return []
    
    def find_method_conflicts(self) -> List[Dict]:
        """Поиск конфликтов методов"""
        print("⚙️ Поиск конфликтов методов...")
        
        method_conflicts = []
        method_locations = defaultdict(list)
        
        # Сбор всех методов из системы
        directories = [
            '/Users/sergejhlystov/ALADDIN_NEW/security',
            '/Users/sergejhlystov/ALADDIN_NEW/core',
            '/Users/sergejhlystov/ALADDIN_NEW/family'
        ]
        
        for directory in directories:
            if os.path.exists(directory):
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        if file.endswith('.py'):
                            file_path = os.path.join(root, file)
                            methods = self.extract_methods_from_file(file_path)
                            
                            for method_info in methods:
                                method_key = f"{method_info['class']}.{method_info['name']}"
                                method_locations[method_key].append({
                                    'file_path': file_path,
                                    'line': method_info['line'],
                                    'class': method_info['class']
                                })
        
        # Поиск конфликтов
        for method_key, locations in method_locations.items():
            if len(locations) > 1:
                method_conflicts.append({
                    'method_key': method_key,
                    'locations': locations,
                    'count': len(locations),
                    'severity': 'high' if len(locations) > 2 else 'medium'
                })
        
        print(f"✅ Найдено {len(method_conflicts)} конфликтов методов")
        return method_conflicts
    
    def extract_methods_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Извлечение методов из файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            methods = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            methods.append({
                                'name': item.name,
                                'class': node.name,
                                'line': item.lineno,
                                'file_path': file_path
                            })
            
            return methods
            
        except Exception as e:
            print(f"⚠️ Ошибка извлечения методов из {file_path}: {e}")
            return []
    
    def find_file_duplicates(self) -> List[Dict]:
        """Поиск дублирующихся файлов"""
        print("📄 Поиск дублирующихся файлов...")
        
        file_duplicates = []
        file_checksums = {}
        
        directories = [
            '/Users/sergejhlystov/ALADDIN_NEW/security',
            '/Users/sergejhlystov/ALADDIN_NEW/core',
            '/Users/sergejhlystov/ALADDIN_NEW/family'
        ]
        
        for directory in directories:
            if os.path.exists(directory):
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        if file.endswith('.py'):
                            file_path = os.path.join(root, file)
                            checksum = self.calculate_file_checksum(file_path)
                            
                            if checksum in file_checksums:
                                file_duplicates.append({
                                    'checksum': checksum,
                                    'original_file': file_checksums[checksum],
                                    'duplicate_file': file_path,
                                    'severity': 'high'
                                })
                            else:
                                file_checksums[checksum] = file_path
        
        print(f"✅ Найдено {len(file_duplicates)} дублирующихся файлов")
        return file_duplicates
    
    def calculate_file_checksum(self, file_path: str) -> str:
        """Вычисление контрольной суммы файла"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            return hashlib.md5(content).hexdigest()
        except Exception:
            return ""
    
    def analyze_dependencies(self) -> List[Dict]:
        """Анализ конфликтов зависимостей"""
        print("🔗 Анализ конфликтов зависимостей...")
        
        dependency_conflicts = []
        
        # Анализ импортов
        import_conflicts = self.analyze_import_conflicts()
        dependency_conflicts.extend(import_conflicts)
        
        # Анализ циклических зависимостей
        circular_deps = self.analyze_circular_dependencies()
        dependency_conflicts.extend(circular_deps)
        
        print(f"✅ Найдено {len(dependency_conflicts)} конфликтов зависимостей")
        return dependency_conflicts
    
    def analyze_import_conflicts(self) -> List[Dict]:
        """Анализ конфликтов импортов"""
        import_conflicts = []
        import_usage = defaultdict(list)
        
        directories = [
            '/Users/sergejhlystov/ALADDIN_NEW/security',
            '/Users/sergejhlystov/ALADDIN_NEW/core',
            '/Users/sergejhlystov/ALADDIN_NEW/family'
        ]
        
        for directory in directories:
            if os.path.exists(directory):
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        if file.endswith('.py'):
                            file_path = os.path.join(root, file)
                            imports = self.extract_imports_from_file(file_path)
                            
                            for import_name in imports:
                                import_usage[import_name].append(file_path)
        
        # Поиск конфликтов импортов
        for import_name, files in import_usage.items():
            if len(files) > 5:  # Если импорт используется в более чем 5 файлах
                import_conflicts.append({
                    'import_name': import_name,
                    'usage_count': len(files),
                    'files': files,
                    'severity': 'medium'
                })
        
        return import_conflicts
    
    def extract_imports_from_file(self, file_path: str) -> List[str]:
        """Извлечение импортов из файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
            
            return imports
            
        except Exception as e:
            print(f"⚠️ Ошибка извлечения импортов из {file_path}: {e}")
            return []
    
    def analyze_circular_dependencies(self) -> List[Dict]:
        """Анализ циклических зависимостей"""
        # Упрощенная проверка циклических зависимостей
        # В реальной реализации нужен более сложный алгоритм
        return []
    
    def generate_conflict_report(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация отчета о конфликтах"""
        print("📊 Генерация отчета о конфликтах...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_sfm_functions': len(analysis_data['sfm_functions']),
                'total_system_functions': len(analysis_data['system_functions']),
                'duplicate_functions': len(analysis_data['duplicates']),
                'class_conflicts': len(analysis_data['class_conflicts']),
                'method_conflicts': len(analysis_data['method_conflicts']),
                'file_duplicates': len(analysis_data['file_duplicates']),
                'dependency_conflicts': len(analysis_data['dependency_conflicts'])
            },
            'conflicts': {
                'duplicate_functions': analysis_data['duplicates'],
                'class_conflicts': analysis_data['class_conflicts'],
                'method_conflicts': analysis_data['method_conflicts'],
                'file_duplicates': analysis_data['file_duplicates'],
                'dependency_conflicts': analysis_data['dependency_conflicts']
            },
            'recommendations': self.generate_recommendations(analysis_data)
        }
        
        # Сохранение отчета
        report_path = '/Users/sergejhlystov/ALADDIN_NEW/SFM_CONFLICT_ANALYSIS_REPORT.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Отчет сохранен: {report_path}")
        return report
    
    def generate_recommendations(self, analysis_data: Dict[str, Any]) -> List[str]:
        """Генерация рекомендаций по устранению конфликтов"""
        recommendations = []
        
        # Рекомендации по дублирующимся функциям
        if analysis_data['duplicates']:
            recommendations.append("🔧 Устранить дублирующиеся функции в SFM")
            recommendations.append("🔧 Проверить уникальность function_id")
        
        # Рекомендации по конфликтам классов
        if analysis_data['class_conflicts']:
            recommendations.append("🏗️ Переименовать конфликтующие классы")
            recommendations.append("🏗️ Использовать пространства имен")
        
        # Рекомендации по конфликтам методов
        if analysis_data['method_conflicts']:
            recommendations.append("⚙️ Переименовать конфликтующие методы")
            recommendations.append("⚙️ Использовать полные имена методов")
        
        # Рекомендации по дублирующимся файлам
        if analysis_data['file_duplicates']:
            recommendations.append("📄 Удалить дублирующиеся файлы")
            recommendations.append("📄 Создать единую версию файлов")
        
        # Общие рекомендации
        recommendations.extend([
            "🛡️ Внедрить систему проверки конфликтов в CI/CD",
            "🛡️ Использовать уникальные префиксы для модулей",
            "🛡️ Регулярно проводить анализ конфликтов",
            "🛡️ Создать политику именования компонентов"
        ])
        
        return recommendations

def main():
    """Основная функция"""
    print("🚀 SFM Conflict Analyzer - Запуск анализа конфликтов")
    print("=" * 60)
    
    analyzer = SFMConflictAnalyzer()
    report = analyzer.analyze_sfm_conflicts()
    
    print("\n📊 РЕЗУЛЬТАТЫ АНАЛИЗА:")
    print("=" * 60)
    
    summary = report['summary']
    print(f"📋 Функций в SFM: {summary['total_sfm_functions']}")
    print(f"📁 Функций в системе: {summary['total_system_functions']}")
    print(f"🔍 Дублирующихся функций: {summary['duplicate_functions']}")
    print(f"🏗️ Конфликтов классов: {summary['class_conflicts']}")
    print(f"⚙️ Конфликтов методов: {summary['method_conflicts']}")
    print(f"📄 Дублирующихся файлов: {summary['file_duplicates']}")
    print(f"🔗 Конфликтов зависимостей: {summary['dependency_conflicts']}")
    
    print("\n💡 РЕКОМЕНДАЦИИ:")
    print("=" * 60)
    for i, rec in enumerate(report['recommendations'], 1):
        print(f"{i}. {rec}")
    
    print(f"\n✅ Анализ завершен! Отчет сохранен в SFM_CONFLICT_ANALYSIS_REPORT.json")

if __name__ == "__main__":
    main()