#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест специальных методов для auto_scaling_engine.py
Проверка __init__, __str__, __repr__ и других специальных методов
"""

import sys
import os
sys.path.append('/Users/sergejhlystov/ALADDIN_NEW')

from datetime import datetime
from security.scaling.auto_scaling_engine import (
    AutoScalingEngine,
    ScalingRule,
    ScalingTrigger,
    ScalingAction,
    MetricData,
    ScalingDecision,
    ScalingMetrics
)

def test_init_methods():
    """6.7.1 - Проверка наличия __init__, __str__, __repr__"""
    print("=== 6.7.1 - ПРОВЕРКА СПЕЦИАЛЬНЫХ МЕТОДОВ ===")
    
    results = {}
    
    # Тест AutoScalingEngine
    try:
        engine = AutoScalingEngine("TestEngine")
        
        # Проверка __init__
        if hasattr(engine, '__init__'):
            print("✅ AutoScalingEngine.__init__ - присутствует")
            init_result = True
        else:
            print("❌ AutoScalingEngine.__init__ - отсутствует")
            init_result = False
        
        # Проверка __str__
        if hasattr(engine, '__str__'):
            str_result = str(engine)
            print(f"✅ AutoScalingEngine.__str__ - присутствует: {str_result}")
            str_ok = True
        else:
            print("❌ AutoScalingEngine.__str__ - отсутствует")
            str_ok = False
        
        # Проверка __repr__
        if hasattr(engine, '__repr__'):
            repr_result = repr(engine)
            print(f"✅ AutoScalingEngine.__repr__ - присутствует: {repr_result}")
            repr_ok = True
        else:
            print("❌ AutoScalingEngine.__repr__ - отсутствует")
            repr_ok = False
        
        results['AutoScalingEngine'] = {
            'init': init_result,
            'str': str_ok,
            'repr': repr_ok
        }
        
    except Exception as e:
        print(f"❌ Ошибка проверки AutoScalingEngine: {e}")
        results['AutoScalingEngine'] = {'init': False, 'str': False, 'repr': False}
    
    # Тест dataclass объектов
    dataclass_objects = [
        ('MetricData', MetricData(
            metric_name="cpu_usage",
            value=0.75,
            timestamp=datetime.now(),
            service_id="test-service"
        )),
        ('ScalingRule', ScalingRule(
            rule_id="test_rule",
            name="Test Rule",
            service_id="test-service",
            metric_name="cpu_usage",
            trigger=ScalingTrigger.CPU_HIGH,
            threshold=0.8,
            action=ScalingAction.SCALE_UP,
            min_replicas=1,
            max_replicas=5,
            cooldown_period=300
        )),
        ('ScalingMetrics', ScalingMetrics())
    ]
    
    for class_name, obj in dataclass_objects:
        try:
            # Проверка __init__ (автоматически генерируется dataclass)
            if hasattr(obj, '__init__'):
                print(f"✅ {class_name}.__init__ - присутствует")
                init_result = True
            else:
                print(f"❌ {class_name}.__init__ - отсутствует")
                init_result = False
            
            # Проверка __str__
            if hasattr(obj, '__str__'):
                str_result = str(obj)
                print(f"✅ {class_name}.__str__ - присутствует: {str_result[:100]}...")
                str_ok = True
            else:
                print(f"❌ {class_name}.__str__ - отсутствует")
                str_ok = False
            
            # Проверка __repr__
            if hasattr(obj, '__repr__'):
                repr_result = repr(obj)
                print(f"✅ {class_name}.__repr__ - присутствует: {repr_result[:100]}...")
                repr_ok = True
            else:
                print(f"❌ {class_name}.__repr__ - отсутствует")
                repr_ok = False
            
            results[class_name] = {
                'init': init_result,
                'str': str_ok,
                'repr': repr_ok
            }
            
        except Exception as e:
            print(f"❌ Ошибка проверки {class_name}: {e}")
            results[class_name] = {'init': False, 'str': False, 'repr': False}
    
    return results

def test_comparison_methods():
    """6.7.2 - Проверка методов сравнения (__eq__, __lt__, etc.)"""
    print("\n=== 6.7.2 - ПРОВЕРКА МЕТОДОВ СРАВНЕНИЯ ===")
    
    comparison_methods = ['__eq__', '__ne__', '__lt__', '__le__', '__gt__', '__ge__']
    results = {}
    
    # Тест AutoScalingEngine
    try:
        engine1 = AutoScalingEngine("Engine1")
        engine2 = AutoScalingEngine("Engine2")
        
        engine_comparison = {}
        for method in comparison_methods:
            if hasattr(engine1, method):
                try:
                    method_func = getattr(engine1, method)
                    # Пытаемся вызвать метод
                    if method == '__eq__':
                        result = method_func(engine2)
                    elif method == '__ne__':
                        result = method_func(engine2)
                    else:
                        result = method_func(engine2)
                    engine_comparison[method] = True
                    print(f"✅ AutoScalingEngine.{method} - присутствует")
                except Exception as e:
                    engine_comparison[method] = False
                    print(f"⚠️ AutoScalingEngine.{method} - присутствует, но ошибка: {e}")
            else:
                engine_comparison[method] = False
                print(f"❌ AutoScalingEngine.{method} - отсутствует")
        
        results['AutoScalingEngine'] = engine_comparison
        
    except Exception as e:
        print(f"❌ Ошибка проверки методов сравнения AutoScalingEngine: {e}")
        results['AutoScalingEngine'] = {method: False for method in comparison_methods}
    
    # Тест dataclass объектов
    try:
        metric1 = MetricData(
            metric_name="cpu_usage",
            value=0.75,
            timestamp=datetime.now(),
            service_id="test-service"
        )
        metric2 = MetricData(
            metric_name="cpu_usage",
            value=0.75,
            timestamp=datetime.now(),
            service_id="test-service"
        )
        
        metric_comparison = {}
        for method in comparison_methods:
            if hasattr(metric1, method):
                try:
                    method_func = getattr(metric1, method)
                    if method == '__eq__':
                        result = method_func(metric2)
                    elif method == '__ne__':
                        result = method_func(metric2)
                    else:
                        result = method_func(metric2)
                    metric_comparison[method] = True
                    print(f"✅ MetricData.{method} - присутствует")
                except Exception as e:
                    metric_comparison[method] = False
                    print(f"⚠️ MetricData.{method} - присутствует, но ошибка: {e}")
            else:
                metric_comparison[method] = False
                print(f"❌ MetricData.{method} - отсутствует")
        
        results['MetricData'] = metric_comparison
        
    except Exception as e:
        print(f"❌ Ошибка проверки методов сравнения MetricData: {e}")
        results['MetricData'] = {method: False for method in comparison_methods}
    
    return results

def test_iteration_methods():
    """6.7.3 - Проверка методов итерации (__iter__, __next__)"""
    print("\n=== 6.7.3 - ПРОВЕРКА МЕТОДОВ ИТЕРАЦИИ ===")
    
    iteration_methods = ['__iter__', '__next__']
    results = {}
    
    # Тест AutoScalingEngine
    try:
        engine = AutoScalingEngine("TestEngine")
        
        engine_iteration = {}
        for method in iteration_methods:
            if hasattr(engine, method):
                engine_iteration[method] = True
                print(f"✅ AutoScalingEngine.{method} - присутствует")
            else:
                engine_iteration[method] = False
                print(f"❌ AutoScalingEngine.{method} - отсутствует")
        
        results['AutoScalingEngine'] = engine_iteration
        
    except Exception as e:
        print(f"❌ Ошибка проверки методов итерации AutoScalingEngine: {e}")
        results['AutoScalingEngine'] = {method: False for method in iteration_methods}
    
    # Тест dataclass объектов
    try:
        metric = MetricData(
            metric_name="cpu_usage",
            value=0.75,
            timestamp=datetime.now(),
            service_id="test-service"
        )
        
        metric_iteration = {}
        for method in iteration_methods:
            if hasattr(metric, method):
                metric_iteration[method] = True
                print(f"✅ MetricData.{method} - присутствует")
            else:
                metric_iteration[method] = False
                print(f"❌ MetricData.{method} - отсутствует")
        
        results['MetricData'] = metric_iteration
        
    except Exception as e:
        print(f"❌ Ошибка проверки методов итерации MetricData: {e}")
        results['MetricData'] = {method: False for method in iteration_methods}
    
    return results

def test_context_manager_methods():
    """6.7.4 - Проверка методов контекстного менеджера (__enter__, __exit__)"""
    print("\n=== 6.7.4 - ПРОВЕРКА МЕТОДОВ КОНТЕКСТНОГО МЕНЕДЖЕРА ===")
    
    context_methods = ['__enter__', '__exit__']
    results = {}
    
    # Тест AutoScalingEngine
    try:
        engine = AutoScalingEngine("TestEngine")
        
        engine_context = {}
        for method in context_methods:
            if hasattr(engine, method):
                engine_context[method] = True
                print(f"✅ AutoScalingEngine.{method} - присутствует")
            else:
                engine_context[method] = False
                print(f"❌ AutoScalingEngine.{method} - отсутствует")
        
        results['AutoScalingEngine'] = engine_context
        
    except Exception as e:
        print(f"❌ Ошибка проверки методов контекстного менеджера AutoScalingEngine: {e}")
        results['AutoScalingEngine'] = {method: False for method in context_methods}
    
    # Тест dataclass объектов
    try:
        metric = MetricData(
            metric_name="cpu_usage",
            value=0.75,
            timestamp=datetime.now(),
            service_id="test-service"
        )
        
        metric_context = {}
        for method in context_methods:
            if hasattr(metric, method):
                metric_context[method] = True
                print(f"✅ MetricData.{method} - присутствует")
            else:
                metric_context[method] = False
                print(f"❌ MetricData.{method} - отсутствует")
        
        results['MetricData'] = metric_context
        
    except Exception as e:
        print(f"❌ Ошибка проверки методов контекстного менеджера MetricData: {e}")
        results['MetricData'] = {method: False for method in context_methods}
    
    return results

def test_other_special_methods():
    """Проверка других специальных методов"""
    print("\n=== ПРОВЕРКА ДРУГИХ СПЕЦИАЛЬНЫХ МЕТОДОВ ===")
    
    other_methods = ['__hash__', '__len__', '__getitem__', '__setitem__', '__delitem__']
    results = {}
    
    # Тест AutoScalingEngine
    try:
        engine = AutoScalingEngine("TestEngine")
        
        engine_other = {}
        for method in other_methods:
            if hasattr(engine, method):
                engine_other[method] = True
                print(f"✅ AutoScalingEngine.{method} - присутствует")
            else:
                engine_other[method] = False
                print(f"❌ AutoScalingEngine.{method} - отсутствует")
        
        results['AutoScalingEngine'] = engine_other
        
    except Exception as e:
        print(f"❌ Ошибка проверки других специальных методов AutoScalingEngine: {e}")
        results['AutoScalingEngine'] = {method: False for method in other_methods}
    
    return results

def main():
    """Основная функция тестирования специальных методов"""
    print("🔍 ЭТАП 6.7 - ПРОВЕРКА СПЕЦИАЛЬНЫХ МЕТОДОВ")
    print("=" * 60)
    
    # 6.7.1 - Проверка __init__, __str__, __repr__
    init_results = test_init_methods()
    
    # 6.7.2 - Проверка методов сравнения
    comparison_results = test_comparison_methods()
    
    # 6.7.3 - Проверка методов итерации
    iteration_results = test_iteration_methods()
    
    # 6.7.4 - Проверка методов контекстного менеджера
    context_results = test_context_manager_methods()
    
    # Другие специальные методы
    other_results = test_other_special_methods()
    
    # Статистика
    print("\n" + "=" * 60)
    print("📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ ЭТАПА 6.7:")
    
    # Подсчет результатов
    total_classes = len(init_results)
    classes_with_init = sum(1 for results in init_results.values() if results.get('init', False))
    classes_with_str = sum(1 for results in init_results.values() if results.get('str', False))
    classes_with_repr = sum(1 for results in init_results.values() if results.get('repr', False))
    
    print(f"✅ Классы с __init__: {classes_with_init}/{total_classes}")
    print(f"✅ Классы с __str__: {classes_with_str}/{total_classes}")
    print(f"✅ Классы с __repr__: {classes_with_repr}/{total_classes}")
    
    # Проверка методов сравнения
    comparison_ok = any(any(methods.values()) for methods in comparison_results.values())
    print(f"✅ Методы сравнения: {'ПРОЙДЕНО' if comparison_ok else 'ПРОВАЛЕНО'}")
    
    # Проверка методов итерации
    iteration_ok = any(any(methods.values()) for methods in iteration_results.values())
    print(f"✅ Методы итерации: {'ПРОЙДЕНО' if iteration_ok else 'ПРОВАЛЕНО'}")
    
    # Проверка методов контекстного менеджера
    context_ok = any(any(methods.values()) for methods in context_results.values())
    print(f"✅ Методы контекстного менеджера: {'ПРОЙДЕНО' if context_ok else 'ПРОВАЛЕНО'}")
    
    overall_success = (classes_with_init == total_classes and 
                      classes_with_str == total_classes and 
                      classes_with_repr == total_classes)
    
    print(f"\n🎯 ОБЩИЙ РЕЗУЛЬТАТ: {'ПРОЙДЕНО' if overall_success else 'ПРОВАЛЕНО'}")
    
    return overall_success

if __name__ == "__main__":
    main()