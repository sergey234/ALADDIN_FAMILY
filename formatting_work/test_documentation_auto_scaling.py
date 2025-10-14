#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест документации для auto_scaling_engine.py
Проверка docstring для классов и методов
"""

import sys
import os
import inspect
sys.path.append('/Users/sergejhlystov/ALADDIN_NEW')

from security.scaling.auto_scaling_engine import (
    AutoScalingEngine,
    ScalingRule,
    ScalingTrigger,
    ScalingAction,
    ScalingStrategy,
    MetricData,
    ScalingDecision,
    ScalingMetrics
)

def test_class_docstrings():
    """6.8.1 - Проверка наличия docstring для каждого класса"""
    print("=== 6.8.1 - ПРОВЕРКА DOCSTRING ДЛЯ КЛАССОВ ===")
    
    classes_to_check = [
        ('ScalingTrigger', ScalingTrigger),
        ('ScalingAction', ScalingAction),
        ('ScalingStrategy', ScalingStrategy),
        ('MetricData', MetricData),
        ('ScalingRule', ScalingRule),
        ('ScalingDecision', ScalingDecision),
        ('ScalingMetrics', ScalingMetrics),
        ('AutoScalingEngine', AutoScalingEngine)
    ]
    
    results = {}
    
    for class_name, class_obj in classes_to_check:
        try:
            docstring = class_obj.__doc__
            if docstring and docstring.strip():
                # Проверяем качество docstring
                doc_length = len(docstring.strip())
                has_description = len(docstring.strip()) > 20
                
                results[class_name] = {
                    'has_docstring': True,
                    'length': doc_length,
                    'has_description': has_description,
                    'docstring': docstring.strip()[:100] + "..." if doc_length > 100 else docstring.strip()
                }
                
                print(f"✅ {class_name}: docstring присутствует ({doc_length} символов)")
                print(f"   Описание: {results[class_name]['docstring']}")
            else:
                results[class_name] = {
                    'has_docstring': False,
                    'length': 0,
                    'has_description': False,
                    'docstring': ""
                }
                print(f"❌ {class_name}: docstring отсутствует")
                
        except Exception as e:
            results[class_name] = {
                'has_docstring': False,
                'length': 0,
                'has_description': False,
                'docstring': f"Ошибка: {e}"
            }
            print(f"❌ {class_name}: ошибка проверки docstring - {e}")
    
    return results

def test_method_docstrings():
    """6.8.2 - Проверка наличия docstring для каждого метода"""
    print("\n=== 6.8.2 - ПРОВЕРКА DOCSTRING ДЛЯ МЕТОДОВ ===")
    
    # Получаем все методы AutoScalingEngine
    engine_methods = []
    for name, method in inspect.getmembers(AutoScalingEngine, predicate=inspect.isfunction):
        if not name.startswith('_'):  # Только public методы
            engine_methods.append((name, method))
    
    print(f"Найдено {len(engine_methods)} public методов в AutoScalingEngine")
    
    results = {}
    
    for method_name, method in engine_methods:
        try:
            docstring = method.__doc__
            if docstring and docstring.strip():
                doc_length = len(docstring.strip())
                has_description = len(docstring.strip()) > 10
                
                results[method_name] = {
                    'has_docstring': True,
                    'length': doc_length,
                    'has_description': has_description,
                    'docstring': docstring.strip()[:100] + "..." if doc_length > 100 else docstring.strip()
                }
                
                print(f"✅ {method_name}: docstring присутствует ({doc_length} символов)")
            else:
                results[method_name] = {
                    'has_docstring': False,
                    'length': 0,
                    'has_description': False,
                    'docstring': ""
                }
                print(f"❌ {method_name}: docstring отсутствует")
                
        except Exception as e:
            results[method_name] = {
                'has_docstring': False,
                'length': 0,
                'has_description': False,
                'docstring': f"Ошибка: {e}"
            }
            print(f"❌ {method_name}: ошибка проверки docstring - {e}")
    
    return results

def test_docstring_quality():
    """6.8.3 - Проверка соответствия docstring реальной функциональности"""
    print("\n=== 6.8.3 - ПРОВЕРКА КАЧЕСТВА DOCSTRING ===")
    
    # Проверяем качество docstring для ключевых методов
    key_methods = [
        'initialize',
        'stop',
        'add_scaling_rule',
        'remove_scaling_rule',
        'collect_metric',
        'make_scaling_decision',
        'get_scaling_rules',
        'get_scaling_decisions',
        'get_scaling_metrics',
        'get_engine_status'
    ]
    
    quality_results = {}
    
    for method_name in key_methods:
        try:
            method = getattr(AutoScalingEngine, method_name)
            docstring = method.__doc__
            
            if docstring and docstring.strip():
                # Проверяем качество docstring
                doc_text = docstring.strip()
                
                # Критерии качества
                has_description = len(doc_text) > 20
                has_return_info = 'return' in doc_text.lower() or 'returns' in doc_text.lower()
                has_parameter_info = 'param' in doc_text.lower() or 'arg' in doc_text.lower()
                has_example = 'example' in doc_text.lower() or 'usage' in doc_text.lower()
                
                quality_score = sum([has_description, has_return_info, has_parameter_info, has_example])
                
                quality_results[method_name] = {
                    'has_description': has_description,
                    'has_return_info': has_return_info,
                    'has_parameter_info': has_parameter_info,
                    'has_example': has_example,
                    'quality_score': quality_score,
                    'max_score': 4
                }
                
                print(f"✅ {method_name}: качество {quality_score}/4")
                print(f"   Описание: {'✅' if has_description else '❌'}")
                print(f"   Возврат: {'✅' if has_return_info else '❌'}")
                print(f"   Параметры: {'✅' if has_parameter_info else '❌'}")
                print(f"   Пример: {'✅' if has_example else '❌'}")
            else:
                quality_results[method_name] = {
                    'has_description': False,
                    'has_return_info': False,
                    'has_parameter_info': False,
                    'has_example': False,
                    'quality_score': 0,
                    'max_score': 4
                }
                print(f"❌ {method_name}: docstring отсутствует")
                
        except Exception as e:
            quality_results[method_name] = {
                'has_description': False,
                'has_return_info': False,
                'has_parameter_info': False,
                'has_example': False,
                'quality_score': 0,
                'max_score': 4
            }
            print(f"❌ {method_name}: ошибка проверки качества - {e}")
    
    return quality_results

def test_type_hints_in_docstrings():
    """6.8.4 - Проверка типов в docstring (type hints)"""
    print("\n=== 6.8.4 - ПРОВЕРКА ТИПОВ В DOCSTRING ===")
    
    # Проверяем наличие type hints в docstring
    methods_with_type_hints = []
    
    for name, method in inspect.getmembers(AutoScalingEngine, predicate=inspect.isfunction):
        if not name.startswith('_'):
            try:
                docstring = method.__doc__
                if docstring and docstring.strip():
                    doc_text = docstring.strip().lower()
                    
                    # Ищем упоминания типов
                    type_indicators = [
                        'str', 'int', 'float', 'bool', 'list', 'dict', 'tuple',
                        'optional', 'union', 'any', 'none', 'datetime'
                    ]
                    
                    found_types = [t for t in type_indicators if t in doc_text]
                    
                    if found_types:
                        methods_with_type_hints.append((name, found_types))
                        print(f"✅ {name}: найдены типы {found_types}")
                    else:
                        print(f"⚠️ {name}: типы не найдены в docstring")
                        
            except Exception as e:
                print(f"❌ {name}: ошибка проверки типов - {e}")
    
    return methods_with_type_hints

def test_docstring_consistency():
    """Проверка консистентности docstring"""
    print("\n=== ПРОВЕРКА КОНСИСТЕНТНОСТИ DOCSTRING ===")
    
    # Проверяем консистентность стиля docstring
    consistency_issues = []
    
    for name, method in inspect.getmembers(AutoScalingEngine, predicate=inspect.isfunction):
        if not name.startswith('_'):
            try:
                docstring = method.__doc__
                if docstring and docstring.strip():
                    doc_text = docstring.strip()
                    
                    # Проверяем стиль docstring
                    if doc_text.startswith('"""') and doc_text.endswith('"""'):
                        style = "triple_double_quotes"
                    elif doc_text.startswith("'''") and doc_text.endswith("'''"):
                        style = "triple_single_quotes"
                    else:
                        style = "other"
                        consistency_issues.append(f"{name}: нестандартный стиль docstring")
                    
                    # Проверяем наличие пустых строк
                    if '\n\n' in doc_text:
                        consistency_issues.append(f"{name}: лишние пустые строки в docstring")
                    
            except Exception as e:
                consistency_issues.append(f"{name}: ошибка проверки консистентности - {e}")
    
    if consistency_issues:
        print("⚠️ Найдены проблемы консистентности:")
        for issue in consistency_issues:
            print(f"   - {issue}")
    else:
        print("✅ Проблем консистентности не найдено")
    
    return consistency_issues

def main():
    """Основная функция тестирования документации"""
    print("🔍 ЭТАП 6.8 - ПРОВЕРКА ДОКУМЕНТАЦИИ")
    print("=" * 60)
    
    # 6.8.1 - Проверка docstring для классов
    class_docs = test_class_docstrings()
    
    # 6.8.2 - Проверка docstring для методов
    method_docs = test_method_docstrings()
    
    # 6.8.3 - Проверка качества docstring
    quality_docs = test_docstring_quality()
    
    # 6.8.4 - Проверка типов в docstring
    type_hints = test_type_hints_in_docstrings()
    
    # Проверка консистентности
    consistency_issues = test_docstring_consistency()
    
    # Статистика
    print("\n" + "=" * 60)
    print("📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ ЭТАПА 6.8:")
    
    # Статистика по классам
    classes_with_docs = sum(1 for result in class_docs.values() if result['has_docstring'])
    total_classes = len(class_docs)
    print(f"✅ Классы с docstring: {classes_with_docs}/{total_classes}")
    
    # Статистика по методам
    methods_with_docs = sum(1 for result in method_docs.values() if result['has_docstring'])
    total_methods = len(method_docs)
    print(f"✅ Методы с docstring: {methods_with_docs}/{total_methods}")
    
    # Статистика качества
    avg_quality = sum(result['quality_score'] for result in quality_docs.values()) / len(quality_docs) if quality_docs else 0
    print(f"✅ Среднее качество docstring: {avg_quality:.1f}/4.0")
    
    # Статистика типов
    methods_with_types = len(type_hints)
    print(f"✅ Методы с типами в docstring: {methods_with_types}/{total_methods}")
    
    # Проблемы консистентности
    print(f"✅ Проблем консистентности: {len(consistency_issues)}")
    
    # Общий результат
    overall_success = (classes_with_docs == total_classes and 
                      methods_with_docs >= total_methods * 0.8 and  # 80% методов должны иметь docstring
                      avg_quality >= 2.0 and  # Среднее качество не менее 2/4
                      len(consistency_issues) == 0)
    
    print(f"\n🎯 ОБЩИЙ РЕЗУЛЬТАТ: {'ПРОЙДЕНО' if overall_success else 'ПРОВАЛЕНО'}")
    
    return overall_success

if __name__ == "__main__":
    main()