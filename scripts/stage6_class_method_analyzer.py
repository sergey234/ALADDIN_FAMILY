#!/usr/bin/env python3
"""
ЭТАП 6: ПРОВЕРКА МЕТОДОВ И КЛАССОВ
Анализ структуры классов, методов, доступности и функциональности
"""

import ast
import inspect
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Добавляем путь к проекту
sys.path.append('/Users/sergejhlystov/ALADDIN_NEW')

class ClassMethodAnalyzer:
    """Анализатор классов и методов для recovery_service.py"""
    
    def __init__(self, file_path: str = "security/reactive/recovery_service.py"):
        self.file_path = Path(file_path)
        self.analysis_results = {}
        self.errors = []
        self.warnings = []
        
    def analyze_file(self) -> Dict[str, Any]:
        """Полный анализ файла"""
        print("🔍 ЭТАП 6: ПРОВЕРКА МЕТОДОВ И КЛАССОВ")
        print("=" * 50)
        
        # 6.1 - Анализ структуры классов
        print("📋 6.1 - АНАЛИЗ СТРУКТУРЫ КЛАССОВ:")
        classes_info = self._analyze_classes()
        
        # 6.2 - Анализ методов классов
        print("📋 6.2 - АНАЛИЗ МЕТОДОВ КЛАССОВ:")
        methods_info = self._analyze_methods()
        
        # 6.3 - Проверка доступности методов
        print("📋 6.3 - ПРОВЕРКА ДОСТУПНОСТИ МЕТОДОВ:")
        accessibility_info = self._check_method_accessibility()
        
        # 6.4 - Проверка функций (не классов)
        print("📋 6.4 - ПРОВЕРКА ФУНКЦИЙ (НЕ КЛАССОВ):")
        functions_info = self._analyze_functions()
        
        # 6.5 - Проверка импортов и зависимостей
        print("📋 6.5 - ПРОВЕРКА ИМПОРТОВ И ЗАВИСИМОСТЕЙ:")
        imports_info = self._analyze_imports()
        
        # 6.6 - Проверка атрибутов классов
        print("📋 6.6 - ПРОВЕРКА АТРИБУТОВ КЛАССОВ:")
        attributes_info = self._analyze_attributes()
        
        # 6.7 - Проверка специальных методов
        print("📋 6.7 - ПРОВЕРКА СПЕЦИАЛЬНЫХ МЕТОДОВ:")
        special_methods_info = self._analyze_special_methods()
        
        # 6.8 - Проверка документации
        print("📋 6.8 - ПРОВЕРКА ДОКУМЕНТАЦИИ:")
        documentation_info = self._analyze_documentation()
        
        # 6.9 - Проверка обработки ошибок
        print("📋 6.9 - ПРОВЕРКА ОБРАБОТКИ ОШИБОК:")
        error_handling_info = self._analyze_error_handling()
        
        # 6.10 - Финальный тест всех компонентов
        print("📋 6.10 - ФИНАЛЬНЫЙ ТЕСТ ВСЕХ КОМПОНЕНТОВ:")
        integration_test_info = self._run_integration_tests()
        
        # 6.11 - Проверка состояния активного файла
        print("📋 6.11 - ПРОВЕРКА СОСТОЯНИЯ АКТИВНОГО ФАЙЛА:")
        file_state_info = self._check_file_state()
        
        # Собираем все результаты
        self.analysis_results = {
            "timestamp": datetime.now().isoformat(),
            "file_path": str(self.file_path),
            "classes": classes_info,
            "methods": methods_info,
            "accessibility": accessibility_info,
            "functions": functions_info,
            "imports": imports_info,
            "attributes": attributes_info,
            "special_methods": special_methods_info,
            "documentation": documentation_info,
            "error_handling": error_handling_info,
            "integration_tests": integration_test_info,
            "file_state": file_state_info,
            "errors": self.errors,
            "warnings": self.warnings
        }
        
        return self.analysis_results
    
    def _analyze_classes(self) -> Dict[str, Any]:
        """6.1 - Анализ структуры классов"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            classes = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = {
                        "name": node.name,
                        "line_number": node.lineno,
                        "bases": [base.id if isinstance(base, ast.Name) else str(base) for base in node.bases],
                        "docstring": ast.get_docstring(node),
                        "methods_count": len([n for n in node.body if isinstance(n, ast.FunctionDef)]),
                        "attributes_count": len([n for n in node.body if isinstance(n, ast.Assign)])
                    }
                    classes.append(class_info)
                    print(f"   ✅ Класс: {class_info['name']}")
                    print(f"      📍 Строка: {class_info['line_number']}")
                    print(f"      🏗️ Базовые классы: {class_info['bases']}")
                    print(f"      📝 Методов: {class_info['methods_count']}")
                    print(f"      🔧 Атрибутов: {class_info['attributes_count']}")
            
            return {
                "total_classes": len(classes),
                "classes": classes
            }
            
        except Exception as e:
            self.errors.append(f"Ошибка анализа классов: {e}")
            return {"error": str(e)}
    
    def _analyze_methods(self) -> Dict[str, Any]:
        """6.2 - Анализ методов классов"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            methods = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Определяем тип метода
                    method_type = "function"
                    if any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree) if hasattr(parent, 'body') and node in parent.body):
                        if node.name.startswith('_'):
                            if node.name.startswith('__'):
                                method_type = "private"
                            else:
                                method_type = "protected"
                        else:
                            method_type = "public"
                    
                    # Проверяем декораторы
                    decorators = []
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Name):
                            decorators.append(decorator.id)
                        elif isinstance(decorator, ast.Attribute):
                            decorators.append(f"{decorator.attr}")
                    
                    method_info = {
                        "name": node.name,
                        "line_number": node.lineno,
                        "type": method_type,
                        "decorators": decorators,
                        "args": [arg.arg for arg in node.args.args],
                        "defaults_count": len(node.args.defaults),
                        "docstring": ast.get_docstring(node),
                        "is_async": isinstance(node, ast.AsyncFunctionDef)
                    }
                    methods.append(method_info)
                    print(f"   ✅ Метод: {method_info['name']} ({method_info['type']})")
                    print(f"      📍 Строка: {method_info['line_number']}")
                    print(f"      🔧 Аргументы: {method_info['args']}")
                    print(f"      🏷️ Декораторы: {method_info['decorators']}")
                    print(f"      ⚡ Async: {'Да' if method_info['is_async'] else 'Нет'}")
            
            return {
                "total_methods": len(methods),
                "methods": methods,
                "public_methods": len([m for m in methods if m['type'] == 'public']),
                "private_methods": len([m for m in methods if m['type'] == 'private']),
                "protected_methods": len([m for m in methods if m['type'] == 'protected']),
                "async_methods": len([m for m in methods if m['is_async']])
            }
            
        except Exception as e:
            self.errors.append(f"Ошибка анализа методов: {e}")
            return {"error": str(e)}
    
    def _check_method_accessibility(self) -> Dict[str, Any]:
        """6.3 - Проверка доступности методов"""
        try:
            # Импортируем модуль для тестирования
            sys.path.append(str(self.file_path.parent))
            module_name = self.file_path.stem
            
            try:
                module = __import__(module_name)
                classes = [getattr(module, name) for name in dir(module) if isinstance(getattr(module, name), type)]
                
                accessibility_results = []
                
                for cls in classes:
                    if cls.__name__ != 'type':  # Исключаем встроенные типы
                        print(f"   🔍 Тестирование класса: {cls.__name__}")
                        
                        try:
                            # Пытаемся создать экземпляр
                            instance = cls()
                            print(f"      ✅ Экземпляр создан успешно")
                            
                            # Получаем все методы
                            methods = [method for method in dir(instance) if not method.startswith('__')]
                            print(f"      📋 Доступных методов: {len(methods)}")
                            
                            # Тестируем каждый метод
                            working_methods = []
                            broken_methods = []
                            
                            for method_name in methods:
                                try:
                                    method = getattr(instance, method_name)
                                    if callable(method):
                                        # Пытаемся вызвать метод с пустыми аргументами
                                        try:
                                            method()
                                            working_methods.append(method_name)
                                        except TypeError:
                                            # Метод требует аргументы - это нормально
                                            working_methods.append(f"{method_name} (требует аргументы)")
                                        except Exception as e:
                                            broken_methods.append(f"{method_name}: {str(e)}")
                                except Exception as e:
                                    broken_methods.append(f"{method_name}: {str(e)}")
                            
                            accessibility_results.append({
                                "class_name": cls.__name__,
                                "instance_created": True,
                                "total_methods": len(methods),
                                "working_methods": working_methods,
                                "broken_methods": broken_methods
                            })
                            
                            print(f"      ✅ Работающих методов: {len(working_methods)}")
                            if broken_methods:
                                print(f"      ⚠️ Проблемных методов: {len(broken_methods)}")
                                for broken in broken_methods[:3]:  # Показываем первые 3
                                    print(f"         - {broken}")
                            
                        except Exception as e:
                            print(f"      ❌ Ошибка создания экземпляра: {e}")
                            accessibility_results.append({
                                "class_name": cls.__name__,
                                "instance_created": False,
                                "error": str(e)
                            })
                
                return {
                    "classes_tested": len(accessibility_results),
                    "successful_instances": len([r for r in accessibility_results if r.get("instance_created", False)]),
                    "results": accessibility_results
                }
                
            except ImportError as e:
                self.errors.append(f"Ошибка импорта модуля: {e}")
                return {"error": str(e)}
                
        except Exception as e:
            self.errors.append(f"Ошибка проверки доступности: {e}")
            return {"error": str(e)}
    
    def _analyze_functions(self) -> Dict[str, Any]:
        """6.4 - Проверка функций (не классов)"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            functions = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree) if hasattr(parent, 'body') and node in parent.body):
                    function_info = {
                        "name": node.name,
                        "line_number": node.lineno,
                        "args": [arg.arg for arg in node.args.args],
                        "defaults_count": len(node.args.defaults),
                        "docstring": ast.get_docstring(node),
                        "is_async": isinstance(node, ast.AsyncFunctionDef)
                    }
                    functions.append(function_info)
                    print(f"   ✅ Функция: {function_info['name']}")
                    print(f"      📍 Строка: {function_info['line_number']}")
                    print(f"      🔧 Аргументы: {function_info['args']}")
                    print(f"      ⚡ Async: {'Да' if function_info['is_async'] else 'Нет'}")
            
            return {
                "total_functions": len(functions),
                "functions": functions,
                "async_functions": len([f for f in functions if f['is_async']])
            }
            
        except Exception as e:
            self.errors.append(f"Ошибка анализа функций: {e}")
            return {"error": str(e)}
    
    def _analyze_imports(self) -> Dict[str, Any]:
        """6.5 - Проверка импортов и зависимостей"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            imports = []
            unused_imports = []
            
            # Собираем все импорты
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append({
                            "type": "import",
                            "name": alias.name,
                            "alias": alias.asname,
                            "line": node.lineno
                        })
                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        imports.append({
                            "type": "from_import",
                            "module": node.module,
                            "name": alias.name,
                            "alias": alias.asname,
                            "line": node.lineno
                        })
            
            # Проверяем использование импортов
            for imp in imports:
                name_to_check = imp["alias"] if imp["alias"] else imp["name"]
                if name_to_check not in content.replace(imp["line"], ""):  # Простая проверка
                    unused_imports.append(imp)
            
            print(f"   📦 Всего импортов: {len(imports)}")
            print(f"   ❌ Неиспользуемых: {len(unused_imports)}")
            
            if unused_imports:
                for unused in unused_imports[:5]:  # Показываем первые 5
                    print(f"      - {unused['name']} (строка {unused['line']})")
            
            return {
                "total_imports": len(imports),
                "unused_imports": len(unused_imports),
                "imports": imports,
                "unused_list": unused_imports
            }
            
        except Exception as e:
            self.errors.append(f"Ошибка анализа импортов: {e}")
            return {"error": str(e)}
    
    def _analyze_attributes(self) -> Dict[str, Any]:
        """6.6 - Проверка атрибутов классов"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            attributes = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_attributes = []
                    for item in node.body:
                        if isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name):
                                    class_attributes.append({
                                        "name": target.id,
                                        "line": item.lineno,
                                        "value_type": type(item.value).__name__
                                    })
                    
                    if class_attributes:
                        attributes.append({
                            "class_name": node.name,
                            "attributes": class_attributes
                        })
                        print(f"   ✅ Класс {node.name}: {len(class_attributes)} атрибутов")
                        for attr in class_attributes:
                            print(f"      - {attr['name']} ({attr['value_type']})")
            
            return {
                "total_attributes": sum(len(cls["attributes"]) for cls in attributes),
                "class_attributes": attributes
            }
            
        except Exception as e:
            self.errors.append(f"Ошибка анализа атрибутов: {e}")
            return {"error": str(e)}
    
    def _analyze_special_methods(self) -> Dict[str, Any]:
        """6.7 - Проверка специальных методов"""
        special_methods = [
            "__init__", "__str__", "__repr__", "__eq__", "__lt__", "__le__", 
            "__gt__", "__ge__", "__ne__", "__iter__", "__next__", "__enter__", 
            "__exit__", "__len__", "__getitem__", "__setitem__", "__delitem__"
        ]
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            found_methods = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name in special_methods:
                    found_methods.append({
                        "name": node.name,
                        "line": node.lineno,
                        "class": "unknown"  # Можно улучшить определение класса
                    })
                    print(f"   ✅ Специальный метод: {node.name} (строка {node.lineno})")
            
            missing_methods = [method for method in special_methods if not any(m["name"] == method for m in found_methods)]
            
            if missing_methods:
                print(f"   ⚠️ Отсутствующие методы: {missing_methods}")
            
            return {
                "found_methods": found_methods,
                "missing_methods": missing_methods,
                "total_found": len(found_methods),
                "total_missing": len(missing_methods)
            }
            
        except Exception as e:
            self.errors.append(f"Ошибка анализа специальных методов: {e}")
            return {"error": str(e)}
    
    def _analyze_documentation(self) -> Dict[str, Any]:
        """6.8 - Проверка документации"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            doc_stats = {
                "classes_with_docstring": 0,
                "methods_with_docstring": 0,
                "functions_with_docstring": 0,
                "total_classes": 0,
                "total_methods": 0,
                "total_functions": 0
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    doc_stats["total_classes"] += 1
                    if ast.get_docstring(node):
                        doc_stats["classes_with_docstring"] += 1
                        print(f"   ✅ Класс {node.name}: есть docstring")
                    else:
                        print(f"   ⚠️ Класс {node.name}: нет docstring")
                
                elif isinstance(node, ast.FunctionDef):
                    if any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree) if hasattr(parent, 'body') and node in parent.body):
                        doc_stats["total_methods"] += 1
                        if ast.get_docstring(node):
                            doc_stats["methods_with_docstring"] += 1
                    else:
                        doc_stats["total_functions"] += 1
                        if ast.get_docstring(node):
                            doc_stats["functions_with_docstring"] += 1
            
            print(f"   📊 Классы с документацией: {doc_stats['classes_with_docstring']}/{doc_stats['total_classes']}")
            print(f"   📊 Методы с документацией: {doc_stats['methods_with_docstring']}/{doc_stats['total_methods']}")
            print(f"   📊 Функции с документацией: {doc_stats['functions_with_docstring']}/{doc_stats['total_functions']}")
            
            return doc_stats
            
        except Exception as e:
            self.errors.append(f"Ошибка анализа документации: {e}")
            return {"error": str(e)}
    
    def _analyze_error_handling(self) -> Dict[str, Any]:
        """6.9 - Проверка обработки ошибок"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            error_handling = {
                "try_except_blocks": 0,
                "raise_statements": 0,
                "logging_statements": 0,
                "return_error_patterns": 0
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Try):
                    error_handling["try_except_blocks"] += 1
                    print(f"   ✅ Try-except блок (строка {node.lineno})")
                
                elif isinstance(node, ast.Raise):
                    error_handling["raise_statements"] += 1
                
                elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    if node.func.attr in ['error', 'warning', 'critical', 'exception']:
                        error_handling["logging_statements"] += 1
            
            print(f"   📊 Try-except блоков: {error_handling['try_except_blocks']}")
            print(f"   📊 Raise statements: {error_handling['raise_statements']}")
            print(f"   📊 Logging statements: {error_handling['logging_statements']}")
            
            return error_handling
            
        except Exception as e:
            self.errors.append(f"Ошибка анализа обработки ошибок: {e}")
            return {"error": str(e)}
    
    def _run_integration_tests(self) -> Dict[str, Any]:
        """6.10 - Финальный тест всех компонентов"""
        try:
            print("   🧪 Запуск интеграционных тестов...")
            
            # Простой тест импорта
            try:
                sys.path.append(str(self.file_path.parent))
                module = __import__(self.file_path.stem)
                print("      ✅ Модуль импортируется успешно")
                import_success = True
            except Exception as e:
                print(f"      ❌ Ошибка импорта: {e}")
                import_success = False
            
            # Тест создания классов
            class_creation_success = 0
            total_classes = 0
            
            if import_success:
                classes = [getattr(module, name) for name in dir(module) if isinstance(getattr(module, name), type) and name != 'type']
                total_classes = len(classes)
                
                for cls in classes:
                    try:
                        instance = cls()
                        class_creation_success += 1
                        print(f"      ✅ Класс {cls.__name__}: экземпляр создан")
                    except Exception as e:
                        print(f"      ❌ Класс {cls.__name__}: ошибка создания - {e}")
            
            return {
                "import_success": import_success,
                "class_creation_success": class_creation_success,
                "total_classes": total_classes,
                "success_rate": (class_creation_success / total_classes * 100) if total_classes > 0 else 0
            }
            
        except Exception as e:
            self.errors.append(f"Ошибка интеграционных тестов: {e}")
            return {"error": str(e)}
    
    def _check_file_state(self) -> Dict[str, Any]:
        """6.11 - Проверка состояния активного файла"""
        try:
            if not self.file_path.exists():
                return {"error": "Файл не существует"}
            
            stat = self.file_path.stat()
            
            # Сравниваем с резервными копиями
            backup_dir = Path("formatting_work")
            backups = list(backup_dir.glob(f"{self.file_path.stem}*.py")) if backup_dir.exists() else []
            
            print(f"   📁 Файл существует: {self.file_path}")
            print(f"   📊 Размер: {stat.st_size:,} байт")
            print(f"   📅 Изменён: {datetime.fromtimestamp(stat.st_mtime)}")
            print(f"   💾 Резервных копий: {len(backups)}")
            
            return {
                "file_exists": True,
                "file_size": stat.st_size,
                "last_modified": stat.st_mtime,
                "backup_count": len(backups),
                "backups": [str(b) for b in backups]
            }
            
        except Exception as e:
            self.errors.append(f"Ошибка проверки состояния файла: {e}")
            return {"error": str(e)}
    
    def save_analysis_report(self) -> str:
        """Сохранение отчёта анализа"""
        try:
            report_dir = Path("formatting_work")
            report_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = report_dir / f"stage6_analysis_report_{timestamp}.json"
            
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(self.analysis_results, f, indent=2, ensure_ascii=False)
            
            print(f"\n📄 Отчёт анализа сохранён: {report_path}")
            return str(report_path)
            
        except Exception as e:
            print(f"❌ Ошибка сохранения отчёта: {e}")
            return ""

def main():
    """Главная функция"""
    analyzer = ClassMethodAnalyzer()
    results = analyzer.analyze_file()
    
    print(f"\n📊 ИТОГИ АНАЛИЗА:")
    print(f"   • Ошибок: {len(analyzer.errors)}")
    print(f"   • Предупреждений: {len(analyzer.warnings)}")
    
    if analyzer.errors:
        print(f"\n❌ ОШИБКИ:")
        for error in analyzer.errors:
            print(f"   - {error}")
    
    # Сохраняем отчёт
    report_path = analyzer.save_analysis_report()
    
    print(f"\n✅ ЭТАП 6 ЗАВЕРШЁН!")
    print(f"📄 Отчёт: {report_path}")

if __name__ == "__main__":
    main()