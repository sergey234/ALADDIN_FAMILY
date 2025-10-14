#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест обработки ошибок для auto_scaling_engine.py
Проверка try-except блоков и обработки исключений
"""

import sys
import os
import ast
import inspect
sys.path.append('/Users/sergejhlystov/ALADDIN_NEW')

def analyze_error_handling():
    """6.9.1 - Проверка try-except блоков в методах"""
    print("=== 6.9.1 - АНАЛИЗ TRY-EXCEPT БЛОКОВ ===")
    
    file_path = '/Users/sergejhlystov/ALADDIN_NEW/security/scaling/auto_scaling_engine.py'
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # Парсим код
        tree = ast.parse(source_code)
        
        # Находим все try-except блоки
        try_except_blocks = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                try_except_blocks.append(node)
        
        print(f"✅ Найдено {len(try_except_blocks)} try-except блоков")
        
        # Анализируем каждый блок
        block_analysis = []
        for i, block in enumerate(try_except_blocks):
            # Находим строки с try-except
            try_line = block.lineno
            except_lines = [handler.lineno for handler in block.handlers]
            
            # Проверяем типы исключений
            exception_types = []
            for handler in block.handlers:
                if handler.type:
                    if isinstance(handler.type, ast.Name):
                        exception_types.append(handler.type.id)
                    elif isinstance(handler.type, ast.Attribute):
                        exception_types.append(f"{handler.type.value.id}.{handler.type.attr}")
                else:
                    exception_types.append("bare except")
            
            # Проверяем наличие else и finally
            has_else = len(block.orelse) > 0
            has_finally = block.finalbody is not None and len(block.finalbody) > 0
            
            block_info = {
                'line': try_line,
                'exception_types': exception_types,
                'has_else': has_else,
                'has_finally': has_finally,
                'handlers_count': len(block.handlers)
            }
            
            block_analysis.append(block_info)
            
            print(f"   Блок {i+1}: строка {try_line}")
            print(f"     Исключения: {exception_types}")
            print(f"     Else: {'✅' if has_else else '❌'}")
            print(f"     Finally: {'✅' if has_finally else '❌'}")
        
        return block_analysis
        
    except Exception as e:
        print(f"❌ Ошибка анализа try-except блоков: {e}")
        return []

def test_exception_handling_correctness():
    """6.9.2 - Проверка корректности обработки исключений"""
    print("\n=== 6.9.2 - ПРОВЕРКА КОРРЕКТНОСТИ ОБРАБОТКИ ИСКЛЮЧЕНИЙ ===")
    
    # Тестируем обработку исключений в реальных методах
    from security.scaling.auto_scaling_engine import AutoScalingEngine, ScalingRule, ScalingTrigger, ScalingAction, MetricData
    from datetime import datetime
    
    test_results = []
    
    try:
        engine = AutoScalingEngine("TestEngine")
        
        # Тест 1: Инициализация с некорректными параметрами
        try:
            engine.initialize()
            test_results.append(("initialize", True, "Успешно"))
            print("✅ initialize() - обработано успешно")
        except Exception as e:
            test_results.append(("initialize", False, f"Ошибка: {e}"))
            print(f"❌ initialize() - ошибка: {e}")
        
        # Тест 2: Добавление правила с None
        try:
            result = engine.add_scaling_rule(None)
            test_results.append(("add_scaling_rule(None)", True, f"Результат: {result}"))
            print(f"✅ add_scaling_rule(None) - обработано: {result}")
        except Exception as e:
            test_results.append(("add_scaling_rule(None)", False, f"Ошибка: {e}"))
            print(f"❌ add_scaling_rule(None) - ошибка: {e}")
        
        # Тест 3: Удаление несуществующего правила
        try:
            result = engine.remove_scaling_rule("nonexistent")
            test_results.append(("remove_scaling_rule(nonexistent)", True, f"Результат: {result}"))
            print(f"✅ remove_scaling_rule(nonexistent) - обработано: {result}")
        except Exception as e:
            test_results.append(("remove_scaling_rule(nonexistent)", False, f"Ошибка: {e}"))
            print(f"❌ remove_scaling_rule(nonexistent) - ошибка: {e}")
        
        # Тест 4: Сбор метрики с None
        try:
            result = engine.collect_metric(None)
            test_results.append(("collect_metric(None)", True, f"Результат: {result}"))
            print(f"✅ collect_metric(None) - обработано: {result}")
        except Exception as e:
            test_results.append(("collect_metric(None)", False, f"Ошибка: {e}"))
            print(f"❌ collect_metric(None) - ошибка: {e}")
        
        # Тест 5: Получение правил с некорректным service_id
        try:
            result = engine.get_scaling_rules("invalid_service")
            test_results.append(("get_scaling_rules(invalid)", True, f"Результат: {len(result)} правил"))
            print(f"✅ get_scaling_rules(invalid) - обработано: {len(result)} правил")
        except Exception as e:
            test_results.append(("get_scaling_rules(invalid)", False, f"Ошибка: {e}"))
            print(f"❌ get_scaling_rules(invalid) - ошибка: {e}")
        
        # Тест 6: Принятие решения для несуществующего сервиса
        try:
            result = engine.make_scaling_decision("nonexistent_service")
            test_results.append(("make_scaling_decision(nonexistent)", True, f"Результат: {result}"))
            print(f"✅ make_scaling_decision(nonexistent) - обработано: {result}")
        except Exception as e:
            test_results.append(("make_scaling_decision(nonexistent)", False, f"Ошибка: {e}"))
            print(f"❌ make_scaling_decision(nonexistent) - ошибка: {e}")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования обработки исключений: {e}")
        test_results.append(("general", False, f"Ошибка: {e}"))
    
    return test_results

def test_error_logging():
    """6.9.3 - Проверка логирования ошибок"""
    print("\n=== 6.9.3 - ПРОВЕРКА ЛОГИРОВАНИЯ ОШИБОК ===")
    
    # Проверяем, есть ли логирование ошибок в коде
    file_path = '/Users/sergejhlystov/ALADDIN_NEW/security/scaling/auto_scaling_engine.py'
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # Ищем упоминания логирования
        logging_patterns = [
            'log_activity',
            'logging',
            'logger',
            'log.error',
            'log.warning',
            'log.info',
            'print('
        ]
        
        logging_found = []
        for pattern in logging_patterns:
            if pattern in source_code:
                count = source_code.count(pattern)
                logging_found.append((pattern, count))
                print(f"✅ {pattern}: найдено {count} раз")
            else:
                print(f"❌ {pattern}: не найдено")
        
        # Ищем try-except блоки с логированием
        try_except_with_logging = 0
        lines = source_code.split('\n')
        
        in_try_block = False
        for i, line in enumerate(lines):
            if 'try:' in line:
                in_try_block = True
            elif in_try_block and ('except' in line or 'else:' in line or 'finally:' in line):
                # Проверяем, есть ли логирование в этом блоке
                block_lines = lines[i-10:i+10]  # Проверяем 10 строк до и после
                if any(pattern in ' '.join(block_lines) for pattern, _ in logging_found):
                    try_except_with_logging += 1
                in_try_block = False
        
        print(f"✅ Try-except блоков с логированием: {try_except_with_logging}")
        
        return {
            'logging_patterns': logging_found,
            'try_except_with_logging': try_except_with_logging
        }
        
    except Exception as e:
        print(f"❌ Ошибка проверки логирования: {e}")
        return {'logging_patterns': [], 'try_except_with_logging': 0}

def test_error_return_handling():
    """6.9.4 - Проверка возврата ошибок в методах"""
    print("\n=== 6.9.4 - ПРОВЕРКА ВОЗВРАТА ОШИБОК В МЕТОДАХ ===")
    
    from security.scaling.auto_scaling_engine import AutoScalingEngine
    
    try:
        engine = AutoScalingEngine("TestEngine")
        
        # Тестируем методы, которые должны возвращать False при ошибке
        error_return_tests = []
        
        # Тест 1: add_scaling_rule с None
        result = engine.add_scaling_rule(None)
        error_return_tests.append(("add_scaling_rule(None)", result, "bool", result is False))
        print(f"✅ add_scaling_rule(None) -> {result} (ожидается False)")
        
        # Тест 2: remove_scaling_rule с несуществующим ID
        result = engine.remove_scaling_rule("nonexistent")
        error_return_tests.append(("remove_scaling_rule(nonexistent)", result, "bool", result is False))
        print(f"✅ remove_scaling_rule(nonexistent) -> {result} (ожидается False)")
        
        # Тест 3: collect_metric с None
        result = engine.collect_metric(None)
        error_return_tests.append(("collect_metric(None)", result, "bool", result is False))
        print(f"✅ collect_metric(None) -> {result} (ожидается False)")
        
        # Тест 4: initialize
        result = engine.initialize()
        error_return_tests.append(("initialize", result, "bool", result is True))
        print(f"✅ initialize() -> {result} (ожидается True)")
        
        # Тест 5: stop
        result = engine.stop()
        error_return_tests.append(("stop", result, "bool", result is True))
        print(f"✅ stop() -> {result} (ожидается True)")
        
        return error_return_tests
        
    except Exception as e:
        print(f"❌ Ошибка проверки возврата ошибок: {e}")
        return []

def test_exception_specificity():
    """Проверка специфичности обработки исключений"""
    print("\n=== ПРОВЕРКА СПЕЦИФИЧНОСТИ ОБРАБОТКИ ИСКЛЮЧЕНИЙ ===")
    
    file_path = '/Users/sergejhlystov/ALADDIN_NEW/security/scaling/auto_scaling_engine.py'
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # Ищем bare except блоки
        bare_except_count = source_code.count('except:')
        specific_except_count = source_code.count('except ') - bare_except_count
        
        print(f"✅ Bare except блоков: {bare_except_count}")
        print(f"✅ Специфичных except блоков: {specific_except_count}")
        
        # Ищем обработку конкретных исключений
        specific_exceptions = [
            'ValueError',
            'TypeError',
            'AttributeError',
            'KeyError',
            'IndexError',
            'FileNotFoundError',
            'PermissionError',
            'ConnectionError',
            'TimeoutError'
        ]
        
        found_exceptions = []
        for exc in specific_exceptions:
            if exc in source_code:
                count = source_code.count(exc)
                found_exceptions.append((exc, count))
                print(f"✅ {exc}: найдено {count} раз")
        
        return {
            'bare_except': bare_except_count,
            'specific_except': specific_except_count,
            'specific_exceptions': found_exceptions
        }
        
    except Exception as e:
        print(f"❌ Ошибка проверки специфичности исключений: {e}")
        return {'bare_except': 0, 'specific_except': 0, 'specific_exceptions': []}

def main():
    """Основная функция тестирования обработки ошибок"""
    print("🔍 ЭТАП 6.9 - ПРОВЕРКА ОБРАБОТКИ ОШИБОК")
    print("=" * 60)
    
    # 6.9.1 - Проверка try-except блоков
    try_except_analysis = analyze_error_handling()
    
    # 6.9.2 - Проверка корректности обработки исключений
    exception_handling_tests = test_exception_handling_correctness()
    
    # 6.9.3 - Проверка логирования ошибок
    logging_analysis = test_error_logging()
    
    # 6.9.4 - Проверка возврата ошибок
    error_return_tests = test_error_return_handling()
    
    # Дополнительная проверка специфичности
    specificity_analysis = test_exception_specificity()
    
    # Статистика
    print("\n" + "=" * 60)
    print("📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ ЭТАПА 6.9:")
    
    # Статистика try-except блоков
    total_try_except = len(try_except_analysis)
    print(f"✅ Try-except блоков: {total_try_except}")
    
    # Статистика обработки исключений
    successful_handling = sum(1 for _, success, _ in exception_handling_tests if success)
    total_handling_tests = len(exception_handling_tests)
    print(f"✅ Успешная обработка исключений: {successful_handling}/{total_handling_tests}")
    
    # Статистика логирования
    total_logging_patterns = sum(count for _, count in logging_analysis['logging_patterns'])
    print(f"✅ Паттернов логирования: {total_logging_patterns}")
    print(f"✅ Try-except с логированием: {logging_analysis['try_except_with_logging']}")
    
    # Статистика возврата ошибок
    correct_error_returns = sum(1 for _, _, _, correct in error_return_tests if correct)
    total_error_return_tests = len(error_return_tests)
    print(f"✅ Корректный возврат ошибок: {correct_error_returns}/{total_error_return_tests}")
    
    # Статистика специфичности
    print(f"✅ Bare except блоков: {specificity_analysis['bare_except']}")
    print(f"✅ Специфичных except блоков: {specificity_analysis['specific_except']}")
    
    # Общий результат
    overall_success = (
        total_try_except > 0 and
        successful_handling >= total_handling_tests * 0.8 and  # 80% тестов должны пройти
        total_logging_patterns > 0 and
        correct_error_returns >= total_error_return_tests * 0.8 and  # 80% тестов должны пройти
        specificity_analysis['specific_except'] > specificity_analysis['bare_except']  # Больше специфичных, чем bare
    )
    
    print(f"\n🎯 ОБЩИЙ РЕЗУЛЬТАТ: {'ПРОЙДЕНО' if overall_success else 'ПРОВАЛЕНО'}")
    
    return overall_success

if __name__ == "__main__":
    main()