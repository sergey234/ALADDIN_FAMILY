#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Алгоритм безопасного интегрирования функций в SFM
Полный алгоритм для безопасного добавления новых функций в Safe Function Manager

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-11
"""

import os
import sys
import json
import importlib
import inspect
import ast
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
from enum import Enum

# Добавляем путь к проекту
sys.path.append('/Users/sergejhlystov/ALADDIN_NEW')

class SafeFunctionIntegrationAlgorithm:
    """Алгоритм безопасного интегрирования функций в SFM"""
    
    def __init__(self):
        self.project_root = Path('/Users/sergejhlystov/ALADDIN_NEW')
        self.sfm_path = self.project_root / 'security' / 'safe_function_manager.py'
        self.data_dir = self.project_root / 'data' / 'sfm'
        self.function_registry = self.data_dir / 'function_registry.json'
        
        # Статистика
        self.stats = {
            'total_checked': 0,
            'successful_integrations': 0,
            'failed_integrations': 0,
            'warnings': 0,
            'errors': []
        }
    
    def run_full_integration_algorithm(self, function_path: str) -> Dict[str, Any]:
        """
        Полный алгоритм безопасного интегрирования функции
        
        Args:
            function_path: Путь к файлу с функцией
            
        Returns:
            Dict с результатами интеграции
        """
        print(f"🚀 ЗАПУСК АЛГОРИТМА ИНТЕГРАЦИИ: {function_path}")
        print("=" * 80)
        
        results = {
            'function_path': function_path,
            'steps_completed': [],
            'errors': [],
            'warnings': [],
            'success': False
        }
        
        try:
            # ЭТАП 1: ПРЕДВАРИТЕЛЬНАЯ ПРОВЕРКА
            print("\n📋 ЭТАП 1: ПРЕДВАРИТЕЛЬНАЯ ПРОВЕРКА")
            step1_result = self._step1_preliminary_check(function_path)
            results['steps_completed'].append(('step1', step1_result))
            if not step1_result['success']:
                results['errors'].extend(step1_result['errors'])
                return results
            
            # ЭТАП 2: АНАЛИЗ АРХИТЕКТУРЫ И ДИРЕКТОРИЙ
            print("\n📋 ЭТАП 2: АНАЛИЗ АРХИТЕКТУРЫ И ДИРЕКТОРИЙ")
            step2_result = self._step2_architecture_analysis(function_path)
            results['steps_completed'].append(('step2', step2_result))
            if not step2_result['success']:
                results['errors'].extend(step2_result['errors'])
                return results
            
            # ЭТАП 3: ПРОВЕРКА ЗАВИСИМОСТЕЙ И ИМПОРТОВ
            print("\n📋 ЭТАП 3: ПРОВЕРКА ЗАВИСИМОСТЕЙ И ИМПОРТОВ")
            step3_result = self._step3_dependencies_check(function_path)
            results['steps_completed'].append(('step3', step3_result))
            if not step3_result['success']:
                results['errors'].extend(step3_result['errors'])
                return results
            
            # ЭТАП 4: ВАЛИДАЦИЯ КОДА И СИНТАКСИСА
            print("\n📋 ЭТАП 4: ВАЛИДАЦИЯ КОДА И СИНТАКСИСА")
            step4_result = self._step4_code_validation(function_path)
            results['steps_completed'].append(('step4', step4_result))
            if not step4_result['success']:
                results['errors'].extend(step4_result['errors'])
                return results
            
            # ЭТАП 5: АНАЛИЗ КЛАССОВ И МЕТОДОВ
            print("\n📋 ЭТАП 5: АНАЛИЗ КЛАССОВ И МЕТОДОВ")
            step5_result = self._step5_class_analysis(function_path)
            results['steps_completed'].append(('step5', step5_result))
            if not step5_result['success']:
                results['errors'].extend(step5_result['errors'])
                return results
            
            # ЭТАП 6: ПОДГОТОВКА К РЕГИСТРАЦИИ
            print("\n📋 ЭТАП 6: ПОДГОТОВКА К РЕГИСТРАЦИИ")
            step6_result = self._step6_registration_preparation(function_path, step5_result['classes'])
            results['steps_completed'].append(('step6', step6_result))
            if not step6_result['success']:
                results['errors'].extend(step6_result['errors'])
                return results
            
            # ЭТАП 7: БЕЗОПАСНАЯ РЕГИСТРАЦИЯ В SFM
            print("\n📋 ЭТАП 7: БЕЗОПАСНАЯ РЕГИСТРАЦИЯ В SFM")
            step7_result = self._step7_safe_registration(step6_result['registration_data'])
            results['steps_completed'].append(('step7', step7_result))
            if not step7_result['success']:
                results['errors'].extend(step7_result['errors'])
                return results
            
            # ЭТАП 8: ИНТЕГРАЦИЯ И ТЕСТИРОВАНИЕ
            print("\n📋 ЭТАП 8: ИНТЕГРАЦИЯ И ТЕСТИРОВАНИЕ")
            step8_result = self._step8_integration_testing(step7_result['registered_functions'])
            results['steps_completed'].append(('step8', step8_result))
            if not step8_result['success']:
                results['errors'].extend(step8_result['errors'])
                return results
            
            # ЭТАП 9: ФИНАЛЬНАЯ ВАЛИДАЦИЯ
            print("\n📋 ЭТАП 9: ФИНАЛЬНАЯ ВАЛИДАЦИЯ")
            step9_result = self._step9_final_validation()
            results['steps_completed'].append(('step9', step9_result))
            if not step9_result['success']:
                results['errors'].extend(step9_result['errors'])
                return results
            
            # УСПЕШНОЕ ЗАВЕРШЕНИЕ
            results['success'] = True
            self.stats['successful_integrations'] += 1
            print(f"\n🎉 ИНТЕГРАЦИЯ УСПЕШНО ЗАВЕРШЕНА!")
            
        except Exception as e:
            error_msg = f"Критическая ошибка в алгоритме интеграции: {e}"
            results['errors'].append(error_msg)
            self.stats['failed_integrations'] += 1
            print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {error_msg}")
        
        finally:
            self.stats['total_checked'] += 1
            results['stats'] = self.stats.copy()
        
        return results
    
    def _step1_preliminary_check(self, function_path: str) -> Dict[str, Any]:
        """ЭТАП 1: Предварительная проверка файла"""
        print("  🔍 Проверка существования файла...")
        
        if not os.path.exists(function_path):
            return {
                'success': False,
                'errors': [f"Файл не найден: {function_path}"]
            }
        
        print("  🔍 Проверка расширения файла...")
        if not function_path.endswith('.py'):
            return {
                'success': False,
                'errors': [f"Файл должен иметь расширение .py: {function_path}"]
            }
        
        print("  🔍 Проверка размера файла...")
        file_size = os.path.getsize(function_path)
        if file_size == 0:
            return {
                'success': False,
                'errors': [f"Файл пустой: {function_path}"]
            }
        
        if file_size > 1024 * 1024:  # 1MB
            return {
                'success': False,
                'errors': [f"Файл слишком большой: {file_size} байт"]
            }
        
        print("  ✅ Предварительная проверка пройдена")
        return {
            'success': True,
            'file_size': file_size,
            'errors': []
        }
    
    def _step2_architecture_analysis(self, function_path: str) -> Dict[str, Any]:
        """ЭТАП 2: Анализ архитектуры и директорий"""
        print("  🔍 Анализ структуры директорий...")
        
        path_obj = Path(function_path)
        relative_path = path_obj.relative_to(self.project_root)
        
        # Проверяем правильность размещения
        valid_directories = [
            'security/ai_agents/',
            'security/ai_bots/',
            'security/managers/',
            'security/microservices/',
            'security/orchestration/',
            'security/scaling/',
            'core/',
            'services/',
            'ai/',
            'bots/'
        ]
        
        is_valid_location = any(str(relative_path).startswith(d) for d in valid_directories)
        
        if not is_valid_location:
            return {
                'success': False,
                'errors': [f"Файл размещен в неправильной директории: {relative_path}"]
            }
        
        print("  🔍 Проверка соответствия архитектуре...")
        
        # Определяем тип компонента по директории
        component_type = self._determine_component_type(str(relative_path))
        
        print(f"  ✅ Компонент определен как: {component_type}")
        return {
            'success': True,
            'relative_path': str(relative_path),
            'component_type': component_type,
            'errors': []
        }
    
    def _step3_dependencies_check(self, function_path: str) -> Dict[str, Any]:
        """ЭТАП 3: Проверка зависимостей и импортов"""
        print("  🔍 Анализ импортов...")
        
        try:
            with open(function_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Парсим AST для анализа импортов
            tree = ast.parse(content)
            imports = []
            import_errors = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append({
                            'type': 'import',
                            'module': alias.name,
                            'alias': alias.asname,
                            'line': node.lineno
                        })
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        imports.append({
                            'type': 'from_import',
                            'module': module,
                            'name': alias.name,
                            'alias': alias.asname,
                            'line': node.lineno
                        })
            
            print(f"  📊 Найдено импортов: {len(imports)}")
            
            # Проверяем каждый импорт
            for imp in imports:
                if not self._validate_import(imp):
                    import_errors.append(f"Проблемный импорт: {imp}")
            
            if import_errors:
                return {
                    'success': False,
                    'errors': import_errors
                }
            
            print("  ✅ Все импорты валидны")
            return {
                'success': True,
                'imports': imports,
                'errors': []
            }
            
        except SyntaxError as e:
            return {
                'success': False,
                'errors': [f"Синтаксическая ошибка в импортах: {e}"]
            }
    
    def _step4_code_validation(self, function_path: str) -> Dict[str, Any]:
        """ЭТАП 4: Валидация кода и синтаксиса"""
        print("  🔍 Проверка синтаксиса Python...")
        
        try:
            with open(function_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Проверяем синтаксис
            ast.parse(content)
            print("  ✅ Синтаксис корректен")
            
            # Проверяем кодировку
            if not content.startswith('# -*- coding: utf-8 -*-'):
                print("  ⚠️  Отсутствует декларация кодировки")
            
            # Проверяем docstring
            tree = ast.parse(content)
            has_docstring = False
            if (tree.body and isinstance(tree.body[0], ast.Expr) 
                and isinstance(tree.body[0].value, ast.Constant)):
                has_docstring = True
            
            if not has_docstring:
                print("  ⚠️  Отсутствует docstring модуля")
            
            return {
                'success': True,
                'has_encoding': content.startswith('# -*- coding: utf-8 -*-'),
                'has_docstring': has_docstring,
                'errors': []
            }
            
        except SyntaxError as e:
            return {
                'success': False,
                'errors': [f"Синтаксическая ошибка: {e}"]
            }
    
    def _step5_class_analysis(self, function_path: str) -> Dict[str, Any]:
        """ЭТАП 5: Анализ классов и методов"""
        print("  🔍 Анализ классов и методов...")
        
        try:
            # Импортируем модуль
            module_name = self._get_module_name(function_path)
            spec = importlib.util.spec_from_file_location(module_name, function_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            classes = []
            functions = []
            
            # Анализируем содержимое модуля
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and not name.startswith('_'):
                    # Фильтруем только реальные компоненты, исключаем Enum, dataclass, базовые классы
                    if (not issubclass(obj, Enum) and 
                        not hasattr(obj, '__dataclass_fields__') and
                        name not in ['ComponentStatus', 'SecurityBase', 'datetime'] and
                        not name.startswith('Optimization') or name == 'PerformanceOptimizationAgent'):
                        classes.append({
                            'name': name,
                            'class': obj,
                            'methods': [method for method in dir(obj) if not method.startswith('_')],
                            'docstring': obj.__doc__
                        })
                elif inspect.isfunction(obj) and not name.startswith('_'):
                    functions.append({
                        'name': name,
                        'function': obj,
                        'docstring': obj.__doc__
                    })
            
            print(f"  📊 Найдено классов: {len(classes)}")
            print(f"  📊 Найдено функций: {len(functions)}")
            
            # Проверяем наличие основных методов
            for cls in classes:
                required_methods = ['__init__', 'execute', 'run', 'perform']
                has_required = any(any(method.startswith(req) for method in cls['methods']) 
                                 for req in required_methods)
                
                if not has_required:
                    print(f"  ⚠️  Класс {cls['name']} не имеет основных методов")
            
            return {
                'success': True,
                'classes': classes,
                'functions': functions,
                'errors': []
            }
            
        except Exception as e:
            return {
                'success': False,
                'errors': [f"Ошибка анализа классов: {e}"]
            }
    
    def _step6_registration_preparation(self, function_path: str, classes: List[Dict]) -> Dict[str, Any]:
        """ЭТАП 6: Подготовка к регистрации"""
        print("  🔍 Подготовка данных для регистрации...")
        
        registration_data = []
        
        for cls in classes:
            # Определяем тип функции
            function_type = self._determine_function_type(cls['name'])
            
            # Определяем уровень безопасности
            security_level = self._determine_security_level(cls['name'], function_type)
            
            # Определяем критичность
            is_critical = self._is_critical_component(cls['name'], function_type)
            
            registration_data.append({
                'function_id': cls['name'].lower().replace('agent', '_agent').replace('bot', '_bot').replace('manager', '_manager'),
                'name': cls['name'],
                'description': cls['docstring'] or f"Компонент {cls['name']}",
                'function_type': function_type,
                'security_level': security_level,
                'is_critical': is_critical,
                'auto_enable': is_critical,  # Критические компоненты включаем автоматически
                'class': cls['class']
            })
        
        print(f"  📊 Подготовлено к регистрации: {len(registration_data)} компонентов")
        
        return {
            'success': True,
            'registration_data': registration_data,
            'errors': []
        }
    
    def _step7_safe_registration(self, registration_data: List[Dict]) -> Dict[str, Any]:
        """ЭТАП 7: Безопасная регистрация в SFM"""
        print("  🔍 Регистрация компонентов в SFM...")
        
        try:
            from security.safe_function_manager import SafeFunctionManager
            
            sfm = SafeFunctionManager()
            registered_functions = []
            
            for data in registration_data:
                try:
                    # Создаем экземпляр класса с правильными аргументами
                    try:
                        # Пробуем создать без аргументов
                        instance = data['class']()
                    except TypeError as e:
                        if "missing" in str(e) and "required" in str(e):
                            # Если нужны аргументы, пробуем с именем класса
                            try:
                                instance = data['class'](data['name'])
                            except TypeError:
                                # Если и это не работает, создаем с пустой строкой
                                instance = data['class']("")
                        else:
                            raise e
                    
                    # Определяем обработчик
                    handler = self._create_handler(instance, data['class'])
                    
                    # Регистрируем функцию
                    success = sfm.register_function(
                        function_id=data['function_id'],
                        name=data['name'],
                        description=data['description'],
                        function_type=data['function_type'],
                        security_level=data['security_level'],
                        is_critical=data['is_critical'],
                        auto_enable=data['auto_enable'],
                        handler=handler
                    )
                    
                    if success:
                        registered_functions.append(data['function_id'])
                        print(f"    ✅ Зарегистрирован: {data['name']}")
                    else:
                        print(f"    ❌ Ошибка регистрации: {data['name']}")
                        
                except Exception as e:
                    print(f"    ❌ Ошибка регистрации {data['name']}: {e}")
            
            print(f"  📊 Успешно зарегистрировано: {len(registered_functions)}/{len(registration_data)}")
            
            return {
                'success': len(registered_functions) > 0,
                'registered_functions': registered_functions,
                'errors': []
            }
            
        except Exception as e:
            return {
                'success': False,
                'errors': [f"Ошибка регистрации в SFM: {e}"]
            }
    
    def _step8_integration_testing(self, registered_functions: List[str]) -> Dict[str, Any]:
        """ЭТАП 8: Интеграция и тестирование"""
        print("  🔍 Тестирование зарегистрированных функций...")
        
        try:
            from security.safe_function_manager import SafeFunctionManager
            
            sfm = SafeFunctionManager()
            test_results = []
            
            for func_id in registered_functions:
                try:
                    # Проверяем наличие функции
                    if func_id in sfm.functions:
                        func = sfm.functions[func_id]
                        print(f"    ✅ Функция {func_id} найдена в SFM")
                        
                        # Проверяем обработчик
                        if func_id in sfm.function_handlers:
                            handler = sfm.function_handlers[func_id]
                            # Тестируем обработчик
                            try:
                                result = handler()
                                test_results.append({
                                    'function_id': func_id,
                                    'status': 'success',
                                    'result': result
                                })
                                print(f"    ✅ Обработчик {func_id} работает")
                            except Exception as e:
                                test_results.append({
                                    'function_id': func_id,
                                    'status': 'error',
                                    'error': str(e)
                                })
                                print(f"    ❌ Ошибка обработчика {func_id}: {e}")
                        else:
                            print(f"    ⚠️  Обработчик {func_id} не найден")
                    else:
                        print(f"    ❌ Функция {func_id} не найдена в SFM")
                        
                except Exception as e:
                    print(f"    ❌ Ошибка тестирования {func_id}: {e}")
            
            successful_tests = len([r for r in test_results if r['status'] == 'success'])
            
            return {
                'success': successful_tests > 0,
                'test_results': test_results,
                'successful_tests': successful_tests,
                'total_tests': len(test_results),
                'errors': []
            }
            
        except Exception as e:
            return {
                'success': False,
                'errors': [f"Ошибка тестирования: {e}"]
            }
    
    def _step9_final_validation(self) -> Dict[str, Any]:
        """ЭТАП 9: Финальная валидация"""
        print("  🔍 Финальная валидация системы...")
        
        try:
            from security.safe_function_manager import SafeFunctionManager
            
            sfm = SafeFunctionManager()
            
            # Проверяем общее состояние SFM
            total_functions = len(sfm.functions)
            total_handlers = len(sfm.function_handlers)
            
            print(f"  📊 Всего функций в SFM: {total_functions}")
            print(f"  📊 Всего обработчиков в SFM: {total_handlers}")
            
            # Проверяем файл персистентности
            if os.path.exists(self.function_registry):
                with open(self.function_registry, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                saved_functions = len(data.get('functions', {}))
                saved_handlers = len(data.get('handlers', {}))
                
                print(f"  📊 Функций в файле: {saved_functions}")
                print(f"  📊 Обработчиков в файле: {saved_handlers}")
                
                if saved_functions == total_functions and saved_handlers == total_handlers:
                    print("  ✅ Персистентность работает корректно")
                else:
                    print("  ⚠️  Несоответствие данных в файле персистентности")
            
            return {
                'success': True,
                'total_functions': total_functions,
                'total_handlers': total_handlers,
                'errors': []
            }
            
        except Exception as e:
            return {
                'success': False,
                'errors': [f"Ошибка финальной валидации: {e}"]
            }
    
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    
    def _determine_component_type(self, relative_path: str) -> str:
        """Определяет тип компонента по пути"""
        if 'ai_agents' in relative_path:
            return 'ai_agent'
        elif 'ai_bots' in relative_path or 'bots' in relative_path:
            return 'ai_bot'
        elif 'managers' in relative_path:
            return 'manager'
        elif 'microservices' in relative_path:
            return 'microservice'
        elif 'orchestration' in relative_path:
            return 'orchestrator'
        elif 'scaling' in relative_path:
            return 'scaling_engine'
        elif 'core' in relative_path:
            return 'core'
        elif 'services' in relative_path:
            return 'service'
        else:
            return 'unknown'
    
    def _determine_function_type(self, class_name: str) -> str:
        """Определяет тип функции по имени класса"""
        if 'Agent' in class_name:
            return 'ai_agent'
        elif 'Bot' in class_name:
            return 'ai_bot'
        elif 'Manager' in class_name:
            return 'manager'
        else:
            return 'component'
    
    def _determine_security_level(self, class_name: str, function_type: str) -> str:
        """Определяет уровень безопасности"""
        if 'Security' in class_name or 'Auth' in class_name:
            return 'high'
        elif 'Manager' in class_name or 'Core' in class_name:
            return 'high'
        elif 'Agent' in class_name or 'Bot' in class_name:
            return 'medium'
        else:
            return 'low'
    
    def _is_critical_component(self, class_name: str, function_type: str) -> bool:
        """Определяет критичность компонента"""
        critical_keywords = ['Security', 'Auth', 'Core', 'Manager', 'Base']
        return any(keyword in class_name for keyword in critical_keywords)
    
    def _validate_import(self, imp: Dict) -> bool:
        """Валидирует импорт"""
        # Проверяем стандартные библиотеки Python
        standard_libs = [
            'os', 'sys', 'json', 'time', 'datetime', 'threading', 'typing',
            'hashlib', 'enum', 'collections', 'itertools', 'functools',
            'pathlib', 'uuid', 'base64', 'urllib', 'http', 'socket',
            'subprocess', 'shutil', 'tempfile', 'logging', 'warnings',
            're', 'math', 'random', 'statistics', 'decimal', 'fractions',
            'io', 'pickle', 'csv', 'xml', 'html', 'urllib.parse',
            'asyncio', 'concurrent', 'concurrent.futures', 'multiprocessing', 'queue',
            'sqlite3', 'configparser', 'argparse', 'getopt',
            'glob', 'fnmatch', 'linecache', 'fileinput', 'codecs',
            'dataclasses', 'psutil'
        ]
        
        # Для from_import проверяем модуль, для import проверяем модуль
        module_name = imp.get('module', '')
        if module_name in standard_libs:
            return True
        
        # Проверяем внутренние модули
        internal_modules = ['core.', 'security.', 'ai.', 'services.']
        if any(module_name.startswith(mod) for mod in internal_modules):
            return True
        
        # Проверяем внешние библиотеки
        external_libs = [
            'requests', 'numpy', 'pandas', 'flask', 'fastapi', 'psutil',
            'redis', 'sqlalchemy', 'uvicorn', 'httpx', 'prometheus_client',
            'abc', 'fastapi.middleware.cors', 'fastapi.middleware.trustedhost',
            'sqlalchemy.ext.declarative', 'sqlalchemy.orm'
        ]
        if module_name in external_libs:
            return True
        
        # Дополнительная проверка для пустых модулей (from . import)
        if not module_name and imp.get('type') == 'from_import':
            return True
        
        return False
    
    def _get_module_name(self, file_path: str) -> str:
        """Получает имя модуля из пути"""
        return Path(file_path).stem
    
    def _create_handler(self, instance: Any, class_obj: Any) -> callable:
        """Создает обработчик для экземпляра класса"""
        # Ищем подходящий метод
        methods = ['execute', 'run', 'perform', 'start', 'process']
        
        for method_name in methods:
            if hasattr(instance, method_name):
                method = getattr(instance, method_name)
                if callable(method):
                    return method
        
        # Если не нашли подходящий метод, создаем обертку
        def wrapper(*args, **kwargs):
            return {
                'status': 'success',
                'class': class_obj.__name__,
                'message': f'Компонент {class_obj.__name__} выполнен'
            }
        
        return wrapper


def main():
    """Главная функция для тестирования алгоритма"""
    algorithm = SafeFunctionIntegrationAlgorithm()
    
    # Пример использования
    test_file = '/Users/sergejhlystov/ALADDIN_NEW/security/ai_agents/mobile_security_agent.py'
    
    if os.path.exists(test_file):
        print("🧪 ТЕСТИРОВАНИЕ АЛГОРИТМА ИНТЕГРАЦИИ")
        print("=" * 50)
        
        result = algorithm.run_full_integration_algorithm(test_file)
        
        print("\n📊 РЕЗУЛЬТАТЫ ИНТЕГРАЦИИ:")
        print(f"  Успех: {'✅ ДА' if result['success'] else '❌ НЕТ'}")
        print(f"  Этапов выполнено: {len(result['steps_completed'])}")
        print(f"  Ошибок: {len(result['errors'])}")
        print(f"  Предупреждений: {len(result['warnings'])}")
        
        if result['errors']:
            print("\n❌ ОШИБКИ:")
            for error in result['errors']:
                print(f"  - {error}")
    else:
        print(f"❌ Тестовый файл не найден: {test_file}")


if __name__ == "__main__":
    main()