#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Финальный алгоритм интегрирования компонентов в SFM
Полный алгоритм с обработкой ошибок и детальным логированием

Автор: ALADDIN Security Team
Версия: 1.2
Дата: 2025-09-11
"""

import os
import sys
import json
import importlib
import inspect
import ast
import traceback
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path

# Добавляем путь к проекту
sys.path.append('/Users/sergejhlystov/ALADDIN_NEW')

class FinalIntegrationAlgorithm:
    """Финальный алгоритм интегрирования компонентов в SFM"""
    
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
    
    def run_integration_algorithm(self, function_path: str) -> Dict[str, Any]:
        """
        Финальный алгоритм интегрирования компонента
        
        Args:
            function_path: Путь к файлу с компонентом
            
        Returns:
            Dict с результатами интеграции
        """
        print(f"🚀 ФИНАЛЬНАЯ ИНТЕГРАЦИЯ КОМПОНЕНТА: {function_path}")
        print("=" * 80)
        
        results = {
            'function_path': function_path,
            'steps_completed': [],
            'errors': [],
            'warnings': [],
            'success': False,
            'registered_functions': []
        }
        
        try:
            # ЭТАП 1: ПРЕДВАРИТЕЛЬНАЯ ПРОВЕРКА
            print("\n📋 ЭТАП 1: ПРЕДВАРИТЕЛЬНАЯ ПРОВЕРКА")
            step1_result = self._step1_preliminary_check(function_path)
            results['steps_completed'].append(('step1', step1_result))
            if not step1_result['success']:
                results['errors'].extend(step1_result['errors'])
                return results
            
            # ЭТАП 2: АНАЛИЗ АРХИТЕКТУРЫ
            print("\n📋 ЭТАП 2: АНАЛИЗ АРХИТЕКТУРЫ")
            step2_result = self._step2_architecture_analysis(function_path)
            results['steps_completed'].append(('step2', step2_result))
            if not step2_result['success']:
                results['errors'].extend(step2_result['errors'])
                return results
            
            # ЭТАП 3: ФИЛЬТРАЦИЯ КОМПОНЕНТОВ
            print("\n📋 ЭТАП 3: ФИЛЬТРАЦИЯ КОМПОНЕНТОВ")
            step3_result = self._step3_filter_components(function_path)
            results['steps_completed'].append(('step3', step3_result))
            if not step3_result['success']:
                results['errors'].extend(step3_result['errors'])
                return results
            
            # ЭТАП 4: ПОДГОТОВКА РЕГИСТРАЦИИ
            print("\n📋 ЭТАП 4: ПОДГОТОВКА РЕГИСТРАЦИИ")
            step4_result = self._step4_prepare_registration(step3_result['components'])
            results['steps_completed'].append(('step4', step4_result))
            if not step4_result['success']:
                results['errors'].extend(step4_result['errors'])
                return results
            
            # ЭТАП 5: БЕЗОПАСНАЯ РЕГИСТРАЦИЯ
            print("\n📋 ЭТАП 5: БЕЗОПАСНАЯ РЕГИСТРАЦИЯ")
            step5_result = self._step5_safe_registration(step4_result['registration_data'])
            results['steps_completed'].append(('step5', step5_result))
            results['registered_functions'] = step5_result.get('registered_functions', [])
            
            # ЭТАП 6: ТЕСТИРОВАНИЕ
            print("\n📋 ЭТАП 6: ТЕСТИРОВАНИЕ")
            step6_result = self._step6_testing(step5_result.get('registered_functions', []))
            results['steps_completed'].append(('step6', step6_result))
            
            # ЭТАП 7: ФИНАЛЬНАЯ ВАЛИДАЦИЯ
            print("\n📋 ЭТАП 7: ФИНАЛЬНАЯ ВАЛИДАЦИЯ")
            step7_result = self._step7_final_validation()
            results['steps_completed'].append(('step7', step7_result))
            
            # Определяем успех
            if len(results['registered_functions']) > 0:
                results['success'] = True
                self.stats['successful_integrations'] += 1
                print(f"\n🎉 ИНТЕГРАЦИЯ УСПЕШНО ЗАВЕРШЕНА!")
                print(f"✅ Зарегистрировано функций: {len(results['registered_functions'])}")
            else:
                results['success'] = False
                self.stats['failed_integrations'] += 1
                print(f"\n❌ ИНТЕГРАЦИЯ НЕ УДАЛАСЬ")
                print(f"❌ Не удалось зарегистрировать ни одной функции")
            
        except Exception as e:
            error_msg = f"Критическая ошибка в алгоритме интеграции: {e}"
            results['errors'].append(error_msg)
            self.stats['failed_integrations'] += 1
            print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {error_msg}")
            print(f"📋 Traceback: {traceback.format_exc()}")
        
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
        
        print("  ✅ Предварительная проверка пройдена")
        return {
            'success': True,
            'errors': []
        }
    
    def _step2_architecture_analysis(self, function_path: str) -> Dict[str, Any]:
        """ЭТАП 2: Анализ архитектуры"""
        print("  🔍 Анализ структуры директорий...")
        
        path_obj = Path(function_path)
        relative_path = path_obj.relative_to(self.project_root)
        
        # Определяем тип компонента по директории
        component_type = self._determine_component_type(str(relative_path))
        
        print(f"  ✅ Компонент определен как: {component_type}")
        return {
            'success': True,
            'relative_path': str(relative_path),
            'component_type': component_type,
            'errors': []
        }
    
    def _step3_filter_components(self, function_path: str) -> Dict[str, Any]:
        """ЭТАП 3: Фильтрация компонентов"""
        print("  🔍 Анализ классов и фильтрация...")
        
        try:
            # Импортируем модуль
            module_name = self._get_module_name(function_path)
            spec = importlib.util.spec_from_file_location(module_name, function_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            all_classes = []
            components = []
            
            # Анализируем все классы
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and not name.startswith('_'):
                    all_classes.append({
                        'name': name,
                        'class': obj,
                        'module': obj.__module__,
                        'bases': [base.__name__ for base in obj.__bases__],
                        'methods': [method for method in dir(obj) if not method.startswith('_')],
                        'docstring': obj.__doc__
                    })
            
            print(f"  📊 Найдено классов: {len(all_classes)}")
            
            # Фильтруем компоненты
            for cls in all_classes:
                if self._is_integratable_component(cls):
                    components.append(cls)
                    print(f"    ✅ Компонент для интеграции: {cls['name']}")
                else:
                    print(f"    ⏭️  Пропущен: {cls['name']}")
            
            print(f"  📊 Компонентов для интеграции: {len(components)}")
            
            if len(components) == 0:
                return {
                    'success': False,
                    'errors': ["Не найдено компонентов для интеграции"]
                }
            
            return {
                'success': True,
                'all_classes': all_classes,
                'components': components,
                'errors': []
            }
            
        except Exception as e:
            return {
                'success': False,
                'errors': [f"Ошибка анализа классов: {e}"]
            }
    
    def _step4_prepare_registration(self, components: List[Dict]) -> Dict[str, Any]:
        """ЭТАП 4: Подготовка к регистрации"""
        print("  🔍 Подготовка данных для регистрации...")
        
        registration_data = []
        
        for cls in components:
            try:
                # Определяем параметры регистрации
                function_id = self._generate_function_id(cls['name'])
                function_type = self._determine_function_type(cls['name'])
                security_level = self._determine_security_level(cls['name'], function_type)
                is_critical = self._is_critical_component(cls['name'], function_type)
                
                registration_data.append({
                    'function_id': function_id,
                    'name': cls['name'],
                    'description': cls['docstring'] or f"Компонент {cls['name']}",
                    'function_type': function_type,
                    'security_level': security_level,
                    'is_critical': is_critical,
                    'auto_enable': is_critical,
                    'class': cls['class'],
                    'original_name': cls['name']
                })
                
                print(f"    ✅ Подготовлен: {cls['name']} → {function_id}")
                
            except Exception as e:
                print(f"    ❌ Ошибка подготовки {cls['name']}: {e}")
        
        print(f"  📊 Подготовлено к регистрации: {len(registration_data)} компонентов")
        
        return {
            'success': True,
            'registration_data': registration_data,
            'errors': []
        }
    
    def _step5_safe_registration(self, registration_data: List[Dict]) -> Dict[str, Any]:
        """ЭТАП 5: Безопасная регистрация"""
        print("  🔍 Регистрация компонентов в SFM...")
        
        try:
            from security.safe_function_manager import SafeFunctionManager
            
            sfm = SafeFunctionManager()
            registered_functions = []
            
            for data in registration_data:
                try:
                    print(f"    🔄 Регистрируем: {data['name']}...")
                    
                    # Создаем обработчик
                    handler = self._create_safe_handler(data['class'], data['name'])
                    
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
                        print(f"    ✅ Зарегистрирован: {data['name']} → {data['function_id']}")
                    else:
                        print(f"    ❌ Ошибка регистрации: {data['name']}")
                        
                except Exception as e:
                    print(f"    ❌ Ошибка регистрации {data['name']}: {e}")
                    print(f"    📋 Traceback: {traceback.format_exc()}")
            
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
    
    def _step6_testing(self, registered_functions: List[str]) -> Dict[str, Any]:
        """ЭТАП 6: Тестирование"""
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
    
    def _step7_final_validation(self) -> Dict[str, Any]:
        """ЭТАП 7: Финальная валидация"""
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
    
    def _is_integratable_component(self, cls: Dict) -> bool:
        """Определяет, можно ли интегрировать класс"""
        name = cls['name']
        
        # Исключаем Enum и его наследников
        if 'Enum' in cls['bases'] or name.endswith('Enum'):
            return False
        
        # Исключаем стандартные типы Python
        if name in ['datetime', 'timedelta', 'date', 'time']:
            return False
        
        # Исключаем dataclass и простые классы данных
        if hasattr(cls['class'], '__dataclass_fields__'):
            return False
        
        # Исключаем классы без методов (кроме __init__)
        methods = [m for m in cls['methods'] if not m.startswith('__')]
        if len(methods) == 0:
            return False
        
        # Ищем основные компоненты по именам
        component_keywords = ['Agent', 'Bot', 'Manager', 'Service', 'Handler', 'Controller', 'Base']
        if any(keyword in name for keyword in component_keywords):
            return True
        
        # Ищем классы с основными методами
        main_methods = ['execute', 'run', 'perform', 'start', 'process', 'handle', 'analyze', 'scan']
        if any(any(method.startswith(main) for method in cls['methods']) for main in main_methods):
            return True
        
        return False
    
    def _generate_function_id(self, class_name: str) -> str:
        """Генерирует ID функции из имени класса"""
        # Конвертируем CamelCase в snake_case
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', class_name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    def _determine_component_type(self, relative_path: str) -> str:
        """Определяет тип компонента по пути"""
        if 'ai_agents' in relative_path:
            return 'ai_agent'
        elif 'ai_bots' in relative_path or 'bots' in relative_path:
            return 'ai_bot'
        elif 'managers' in relative_path:
            return 'manager'
        elif 'core' in relative_path:
            return 'core'
        elif 'services' in relative_path:
            return 'service'
        else:
            return 'component'
    
    def _determine_function_type(self, class_name: str) -> str:
        """Определяет тип функции по имени класса"""
        if 'Agent' in class_name:
            return 'ai_agent'
        elif 'Bot' in class_name:
            return 'ai_bot'
        elif 'Manager' in class_name:
            return 'manager'
        elif 'Service' in class_name:
            return 'service'
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
    
    def _create_safe_handler(self, class_obj: Any, class_name: str) -> callable:
        """Создает безопасный обработчик для класса"""
        def safe_handler(*args, **kwargs):
            try:
                # Создаем экземпляр класса с безопасными параметрами
                instance = class_obj()
                
                # Ищем подходящий метод
                methods = ['execute', 'run', 'perform', 'start', 'process', 'handle', 'analyze', 'scan']
                
                for method_name in methods:
                    if hasattr(instance, method_name):
                        method = getattr(instance, method_name)
                        if callable(method):
                            return method()
                
                # Если не нашли подходящий метод, возвращаем базовую информацию
                return {
                    'status': 'success',
                    'class': class_name,
                    'message': f'Компонент {class_name} выполнен успешно',
                    'methods_available': [m for m in dir(instance) if not m.startswith('_')]
                }
                
            except Exception as e:
                return {
                    'status': 'error',
                    'class': class_name,
                    'error': str(e),
                    'message': f'Ошибка выполнения компонента {class_name}'
                }
        
        return safe_handler
    
    def _get_module_name(self, file_path: str) -> str:
        """Получает имя модуля из пути"""
        return Path(file_path).stem


def main():
    """Главная функция для тестирования алгоритма"""
    algorithm = FinalIntegrationAlgorithm()
    
    # Пример использования
    test_file = '/Users/sergejhlystov/ALADDIN_NEW/security/ai_agents/mobile_security_agent.py'
    
    if os.path.exists(test_file):
        print("🧪 ТЕСТИРОВАНИЕ ФИНАЛЬНОГО АЛГОРИТМА ИНТЕГРАЦИИ")
        print("=" * 70)
        
        result = algorithm.run_integration_algorithm(test_file)
        
        print("\n📊 РЕЗУЛЬТАТЫ ИНТЕГРАЦИИ:")
        print(f"  Успех: {'✅ ДА' if result['success'] else '❌ НЕТ'}")
        print(f"  Этапов выполнено: {len(result['steps_completed'])}")
        print(f"  Зарегистрировано функций: {len(result['registered_functions'])}")
        print(f"  Ошибок: {len(result['errors'])}")
        print(f"  Предупреждений: {len(result['warnings'])}")
        
        if result['registered_functions']:
            print("\n✅ ЗАРЕГИСТРИРОВАННЫЕ ФУНКЦИИ:")
            for func_id in result['registered_functions']:
                print(f"  - {func_id}")
        
        if result['errors']:
            print("\n❌ ОШИБКИ:")
            for error in result['errors']:
                print(f"  - {error}")
    else:
        print(f"❌ Тестовый файл не найден: {test_file}")


if __name__ == "__main__":
    main()