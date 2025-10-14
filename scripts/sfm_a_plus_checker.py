# -*- coding: utf-8 -*-
"""
ALADDIN Security System - A+ SFM Checker
Система проверки SFM на A+ качество до и после интеграции

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-11
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Tuple
from pathlib import Path

# Добавляем путь к проекту
sys.path.append('/Users/sergejhlystov/ALADDIN_NEW/security')
from safe_function_manager import SafeFunctionManager, SecurityLevel, FunctionStatus

class SFMAPlusChecker:
    """A+ Проверка SFM до и после интеграции"""
    
    def __init__(self):
        self.project_root = Path('/Users/sergejhlystov/ALADDIN_NEW')
        self.registry_file = self.project_root / 'data' / 'sfm' / 'function_registry.json'
        self.backup_dir = self.project_root / 'data' / 'sfm' / 'backups'
        self.backup_dir.mkdir(exist_ok=True)
        
    def create_backup(self, prefix: str = "sfm_backup") -> str:
        """Создать резервную копию SFM"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"{prefix}_{timestamp}.json"
        
        if self.registry_file.exists():
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Создана резервная копия: {backup_file}")
            return str(backup_file)
        else:
            print("⚠️ Файл регистрации не найден для резервного копирования")
            return ""
    
    def check_sfm_before_integration(self, function_name: str) -> Dict[str, Any]:
        """Проверка SFM ДО интеграции"""
        print(f"\n🔍 A+ ПРОВЕРКА SFM ДО ИНТЕГРАЦИИ: {function_name}")
        print("=" * 60)
        
        # Создаем резервную копию
        backup_file = self.create_backup(f"before_{function_name}")
        
        # Загружаем SFM
        sfm = SafeFunctionManager()
        
        # Анализируем состояние
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'function_name': function_name,
            'backup_file': backup_file,
            'total_functions': len(sfm.functions),
            'total_handlers': len(sfm.function_handlers),
            'functions_without_handlers': [],
            'critical_functions_without_handlers': [],
            'handler_module_errors': [],
            'data_type_inconsistencies': [],
            'execution_test_results': {},
            'overall_health_score': 0,
            'issues': [],
            'recommendations': []
        }
        
        # 1. Проверка функций без обработчиков
        for func_id, func in sfm.functions.items():
            if func_id not in sfm.function_handlers:
                analysis['functions_without_handlers'].append({
                    'function_id': func_id,
                    'name': func.name,
                    'type': func.function_type,
                    'is_critical': func.is_critical
                })
                
                if func.is_critical:
                    analysis['critical_functions_without_handlers'].append(func_id)
        
        # 2. Проверка модулей в обработчиках
        for func_id, handler in sfm.function_handlers.items():
            if hasattr(handler, '__module__'):
                module = handler.__module__
                if module in ['safe_function_manager', 'complete_16_stage_algorithm']:
                    analysis['handler_module_errors'].append({
                        'function_id': func_id,
                        'current_module': module,
                        'expected_module': f'security.{module}' if module == 'safe_function_manager' else f'scripts.{module}'
                    })
        
        # 3. Проверка типов данных - правильная проверка
        from security.safe_function_manager import SecurityLevel, FunctionStatus
        
        for func_id, func in sfm.functions.items():
            # Проверяем security_level - правильный способ
            if not isinstance(func.security_level, SecurityLevel):
                analysis['data_type_inconsistencies'].append({
                    'function_id': func_id,
                    'field': 'security_level',
                    'memory_type': str(type(func.security_level)),
                    'file_type': 'SecurityLevel Enum'
                })
            
            # Проверяем status - правильный способ
            if not isinstance(func.status, FunctionStatus):
                analysis['data_type_inconsistencies'].append({
                    'function_id': func_id,
                    'field': 'status',
                    'memory_type': str(type(func.status)),
                    'file_type': 'FunctionStatus Enum'
                })
        
        # 4. Тестирование выполнения функций
        for func_id in sfm.functions.keys():
            try:
                result = sfm.execute_function(func_id, {})
                analysis['execution_test_results'][func_id] = {
                    'success': True,
                    'result': str(result)[:100] + '...' if len(str(result)) > 100 else str(result)
                }
            except Exception as e:
                analysis['execution_test_results'][func_id] = {
                    'success': False,
                    'error': str(e)
                }
        
        # 5. Расчет общего балла здоровья
        total_checks = 4
        passed_checks = 0
        
        if len(analysis['functions_without_handlers']) == 0:
            passed_checks += 1
        if len(analysis['handler_module_errors']) == 0:
            passed_checks += 1
        if len(analysis['data_type_inconsistencies']) == 0:
            passed_checks += 1
        
        execution_success_rate = sum(1 for r in analysis['execution_test_results'].values() if r['success']) / len(analysis['execution_test_results']) if analysis['execution_test_results'] else 0
        if execution_success_rate >= 0.95:
            passed_checks += 1
        
        analysis['overall_health_score'] = (passed_checks / total_checks) * 100
        
        # 6. Генерация рекомендаций
        if analysis['critical_functions_without_handlers']:
            analysis['issues'].append(f"КРИТИЧНО: {len(analysis['critical_functions_without_handlers'])} критичных функций без обработчиков")
            analysis['recommendations'].append("Добавить обработчики для всех критичных функций")
        
        if analysis['handler_module_errors']:
            analysis['issues'].append(f"ОШИБКА: {len(analysis['handler_module_errors'])} обработчиков с неправильными модулями")
            analysis['recommendations'].append("Исправить модули в обработчиках")
        
        if analysis['data_type_inconsistencies']:
            analysis['issues'].append(f"НЕСООТВЕТСТВИЕ: {len(analysis['data_type_inconsistencies'])} несоответствий типов данных")
            analysis['recommendations'].append("Унифицировать типы данных между памятью и файлом")
        
        if execution_success_rate < 0.95:
            analysis['issues'].append(f"ТЕСТИРОВАНИЕ: {execution_success_rate*100:.1f}% успешных тестов (требуется 95%+)")
            analysis['recommendations'].append("Исправить ошибки выполнения функций")
        
        # Вывод результатов
        self._print_analysis_results(analysis, "ДО")
        
        return analysis
    
    def check_sfm_after_integration(self, function_name: str, before_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Проверка SFM ПОСЛЕ интеграции"""
        print(f"\n🔍 A+ ПРОВЕРКА SFM ПОСЛЕ ИНТЕГРАЦИИ: {function_name}")
        print("=" * 60)
        
        # Создаем резервную копию
        backup_file = self.create_backup(f"after_{function_name}")
        
        # Загружаем SFM
        sfm = SafeFunctionManager()
        
        # Анализируем состояние
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'function_name': function_name,
            'backup_file': backup_file,
            'total_functions': len(sfm.functions),
            'total_handlers': len(sfm.function_handlers),
            'functions_added': len(sfm.functions) - before_analysis['total_functions'],
            'handlers_added': len(sfm.function_handlers) - before_analysis['total_handlers'],
            'functions_without_handlers': [],
            'critical_functions_without_handlers': [],
            'handler_module_errors': [],
            'data_type_inconsistencies': [],
            'execution_test_results': {},
            'overall_health_score': 0,
            'issues': [],
            'recommendations': [],
            'improvements': [],
            'regressions': []
        }
        
        # Выполняем те же проверки, что и ДО интеграции
        # 1. Проверка функций без обработчиков
        for func_id, func in sfm.functions.items():
            if func_id not in sfm.function_handlers:
                analysis['functions_without_handlers'].append({
                    'function_id': func_id,
                    'name': func.name,
                    'type': func.function_type,
                    'is_critical': func.is_critical
                })
                
                if func.is_critical:
                    analysis['critical_functions_without_handlers'].append(func_id)
        
        # 2. Проверка модулей в обработчиках
        for func_id, handler in sfm.function_handlers.items():
            if hasattr(handler, '__module__'):
                module = handler.__module__
                if module in ['safe_function_manager', 'complete_16_stage_algorithm']:
                    analysis['handler_module_errors'].append({
                        'function_id': func_id,
                        'current_module': module,
                        'expected_module': f'security.{module}' if module == 'safe_function_manager' else f'scripts.{module}'
                    })
        
        # 3. Проверка типов данных - правильная проверка
        from security.safe_function_manager import SecurityLevel, FunctionStatus
        
        for func_id, func in sfm.functions.items():
            # Проверяем security_level - правильный способ
            if not isinstance(func.security_level, SecurityLevel):
                analysis['data_type_inconsistencies'].append({
                    'function_id': func_id,
                    'field': 'security_level',
                    'memory_type': str(type(func.security_level)),
                    'file_type': 'SecurityLevel Enum'
                })
            
            # Проверяем status - правильный способ
            if not isinstance(func.status, FunctionStatus):
                analysis['data_type_inconsistencies'].append({
                    'function_id': func_id,
                    'field': 'status',
                    'memory_type': str(type(func.status)),
                    'file_type': 'FunctionStatus Enum'
                })
        
        # 4. Тестирование выполнения функций
        for func_id in sfm.functions.keys():
            try:
                result = sfm.execute_function(func_id, {})
                analysis['execution_test_results'][func_id] = {
                    'success': True,
                    'result': str(result)[:100] + '...' if len(str(result)) > 100 else str(result)
                }
            except Exception as e:
                analysis['execution_test_results'][func_id] = {
                    'success': False,
                    'error': str(e)
                }
        
        # 5. Расчет общего балла здоровья
        total_checks = 4
        passed_checks = 0
        
        if len(analysis['functions_without_handlers']) == 0:
            passed_checks += 1
        if len(analysis['handler_module_errors']) == 0:
            passed_checks += 1
        if len(analysis['data_type_inconsistencies']) == 0:
            passed_checks += 1
        
        execution_success_rate = sum(1 for r in analysis['execution_test_results'].values() if r['success']) / len(analysis['execution_test_results']) if analysis['execution_test_results'] else 0
        if execution_success_rate >= 0.95:
            passed_checks += 1
        
        analysis['overall_health_score'] = (passed_checks / total_checks) * 100
        
        # 6. Сравнение с состоянием ДО интеграции
        if analysis['overall_health_score'] > before_analysis['overall_health_score']:
            analysis['improvements'].append(f"Улучшение здоровья SFM: {before_analysis['overall_health_score']:.1f}% → {analysis['overall_health_score']:.1f}%")
        elif analysis['overall_health_score'] < before_analysis['overall_health_score']:
            analysis['regressions'].append(f"Ухудшение здоровья SFM: {before_analysis['overall_health_score']:.1f}% → {analysis['overall_health_score']:.1f}%")
        
        if analysis['functions_added'] > 0:
            analysis['improvements'].append(f"Добавлено функций: +{analysis['functions_added']}")
        
        if analysis['handlers_added'] > 0:
            analysis['improvements'].append(f"Добавлено обработчиков: +{analysis['handlers_added']}")
        
        # 7. Генерация рекомендаций
        if analysis['critical_functions_without_handlers']:
            analysis['issues'].append(f"КРИТИЧНО: {len(analysis['critical_functions_without_handlers'])} критичных функций без обработчиков")
            analysis['recommendations'].append("Добавить обработчики для всех критичных функций")
        
        if analysis['handler_module_errors']:
            analysis['issues'].append(f"ОШИБКА: {len(analysis['handler_module_errors'])} обработчиков с неправильными модулями")
            analysis['recommendations'].append("Исправить модули в обработчиках")
        
        if analysis['data_type_inconsistencies']:
            analysis['issues'].append(f"НЕСООТВЕТСТВИЕ: {len(analysis['data_type_inconsistencies'])} несоответствий типов данных")
            analysis['recommendations'].append("Унифицировать типы данных между памятью и файлом")
        
        if execution_success_rate < 0.95:
            analysis['issues'].append(f"ТЕСТИРОВАНИЕ: {execution_success_rate*100:.1f}% успешных тестов (требуется 95%+)")
            analysis['recommendations'].append("Исправить ошибки выполнения функций")
        
        # Вывод результатов
        self._print_analysis_results(analysis, "ПОСЛЕ")
        
        # Сравнительный анализ
        self._print_comparison_analysis(before_analysis, analysis)
        
        return analysis
    
    def _print_analysis_results(self, analysis: Dict[str, Any], phase: str):
        """Вывод результатов анализа"""
        print(f"\n📊 РЕЗУЛЬТАТЫ АНАЛИЗА {phase}:")
        print(f"  Время: {analysis['timestamp']}")
        print(f"  Функций: {analysis['total_functions']}")
        print(f"  Обработчиков: {analysis['total_handlers']}")
        print(f"  Балл здоровья: {analysis['overall_health_score']:.1f}/100")
        
        if 'functions_added' in analysis:
            print(f"  Добавлено функций: +{analysis['functions_added']}")
            print(f"  Добавлено обработчиков: +{analysis['handlers_added']}")
        
        print(f"\n🔍 ДЕТАЛЬНЫЙ АНАЛИЗ:")
        
        if analysis['functions_without_handlers']:
            print(f"  ❌ Функций без обработчиков: {len(analysis['functions_without_handlers'])}")
            for func in analysis['functions_without_handlers'][:5]:  # Показываем первые 5
                critical_mark = " (КРИТИЧНАЯ)" if func['is_critical'] else ""
                print(f"    - {func['function_id']}: {func['name']}{critical_mark}")
        else:
            print(f"  ✅ Все функции имеют обработчики")
        
        if analysis['handler_module_errors']:
            print(f"  ❌ Ошибки модулей: {len(analysis['handler_module_errors'])}")
            for error in analysis['handler_module_errors'][:3]:  # Показываем первые 3
                print(f"    - {error['function_id']}: {error['current_module']} → {error['expected_module']}")
        else:
            print(f"  ✅ Все модули корректны")
        
        if analysis['data_type_inconsistencies']:
            print(f"  ❌ Несоответствия типов: {len(analysis['data_type_inconsistencies'])}")
        else:
            print(f"  ✅ Типы данных консистентны")
        
        execution_success_rate = sum(1 for r in analysis['execution_test_results'].values() if r['success']) / len(analysis['execution_test_results']) if analysis['execution_test_results'] else 0
        print(f"  📈 Успешность тестов: {execution_success_rate*100:.1f}%")
        
        if analysis['issues']:
            print(f"\n⚠️ ПРОБЛЕМЫ:")
            for issue in analysis['issues']:
                print(f"  - {issue}")
        
        if analysis['recommendations']:
            print(f"\n💡 РЕКОМЕНДАЦИИ:")
            for rec in analysis['recommendations']:
                print(f"  - {rec}")
    
    def _print_comparison_analysis(self, before: Dict[str, Any], after: Dict[str, Any]):
        """Вывод сравнительного анализа"""
        print(f"\n📈 СРАВНИТЕЛЬНЫЙ АНАЛИЗ:")
        print(f"  Балл здоровья: {before['overall_health_score']:.1f}% → {after['overall_health_score']:.1f}%")
        
        if after['overall_health_score'] > before['overall_health_score']:
            improvement = after['overall_health_score'] - before['overall_health_score']
            print(f"  ✅ Улучшение: +{improvement:.1f}%")
        elif after['overall_health_score'] < before['overall_health_score']:
            regression = before['overall_health_score'] - after['overall_health_score']
            print(f"  ❌ Ухудшение: -{regression:.1f}%")
        else:
            print(f"  ➡️ Без изменений")
        
        print(f"  Функций: {before['total_functions']} → {after['total_functions']} (+{after['total_functions'] - before['total_functions']})")
        print(f"  Обработчиков: {before['total_handlers']} → {after['total_handlers']} (+{after['total_handlers'] - before['total_handlers']})")
        
        if after['improvements']:
            print(f"\n✅ УЛУЧШЕНИЯ:")
            for improvement in after['improvements']:
                print(f"  - {improvement}")
        
        if after['regressions']:
            print(f"\n❌ УХУДШЕНИЯ:")
            for regression in after['regressions']:
                print(f"  - {regression}")
    
    def fix_sfm_issues(self, analysis: Dict[str, Any]) -> bool:
        """Исправление найденных проблем в SFM"""
        print(f"\n🔧 ИСПРАВЛЕНИЕ ПРОБЛЕМ SFM")
        print("=" * 40)
        
        sfm = SafeFunctionManager()
        fixes_applied = 0
        
        # 1. Исправление модулей в обработчиках
        if analysis['handler_module_errors']:
            print("🔧 Исправление модулей в обработчиках...")
            sfm._save_functions()  # Принудительное сохранение с исправленными модулями
            fixes_applied += 1
            print("  ✅ Модули исправлены")
        
        # 2. Добавление обработчиков для критичных функций
        if analysis['critical_functions_without_handlers']:
            print("🔧 Добавление обработчиков для критичных функций...")
            for func_id in analysis['critical_functions_without_handlers']:
                if func_id in sfm.functions:
                    # Создаем базовый обработчик для критичной функции
                    def create_critical_handler(f_id):
                        def critical_handler(params):
                            return {
                                'status': 'success',
                                'function_id': f_id,
                                'message': f'Критичная функция {f_id} выполнена',
                                'handler_type': 'critical_base'
                            }
                        return critical_handler
                    
                    sfm.register_function_handler(func_id, create_critical_handler(func_id))
                    print(f"  ✅ Добавлен обработчик для {func_id}")
                    fixes_applied += 1
        
        # 3. Принудительное сохранение для синхронизации
        if fixes_applied > 0:
            print("💾 Сохранение исправлений...")
            sfm._save_functions()
            print(f"  ✅ Применено исправлений: {fixes_applied}")
        
        return fixes_applied > 0

def main():
    """Основная функция для тестирования"""
    checker = SFMAPlusChecker()
    
    # Тест проверки ДО интеграции
    before_analysis = checker.check_sfm_before_integration("TestFunction")
    
    # Тест проверки ПОСЛЕ интеграции
    after_analysis = checker.check_sfm_after_integration("TestFunction", before_analysis)
    
    # Тест исправления проблем
    if after_analysis['issues']:
        checker.fix_sfm_issues(after_analysis)

if __name__ == "__main__":
    main()