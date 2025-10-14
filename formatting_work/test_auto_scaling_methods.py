#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест доступности методов AutoScalingEngine
Проверка всех public методов и их вызовов
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
    MetricData
)

def test_class_instantiation():
    """6.3.1 - Создание экземпляра каждого класса"""
    print("=== 6.3.1 - СОЗДАНИЕ ЭКЗЕМПЛЯРОВ КЛАССОВ ===")
    
    try:
        # Создание основного движка
        engine = AutoScalingEngine("TestEngine")
        print("✅ AutoScalingEngine создан успешно")
        
        # Создание dataclass объектов
        metric = MetricData(
            metric_name="cpu_usage",
            value=0.75,
            timestamp=datetime.now(),
            service_id="test-service"
        )
        print("✅ MetricData создан успешно")
        
        rule = ScalingRule(
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
        )
        print("✅ ScalingRule создан успешно")
        
        return engine, metric, rule
        
    except Exception as e:
        print(f"❌ Ошибка создания экземпляров: {e}")
        return None, None, None

def test_public_methods_accessibility(engine, metric, rule):
    """6.3.2 - Проверка доступности всех public методов"""
    print("\n=== 6.3.2 - ПРОВЕРКА ДОСТУПНОСТИ PUBLIC МЕТОДОВ ===")
    
    if not engine:
        print("❌ Движок не создан, пропускаем тест")
        return False
    
    public_methods = [
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
    
    accessible_methods = []
    for method_name in public_methods:
        if hasattr(engine, method_name):
            method = getattr(engine, method_name)
            if callable(method):
                accessible_methods.append(method_name)
                print(f"✅ {method_name} - доступен и вызываем")
            else:
                print(f"❌ {method_name} - не вызываем")
        else:
            print(f"❌ {method_name} - не найден")
    
    print(f"\n📊 Доступно методов: {len(accessible_methods)}/{len(public_methods)}")
    return len(accessible_methods) == len(public_methods)

def test_method_calls_with_correct_parameters(engine, metric, rule):
    """6.3.3 - Тестирование вызова каждого метода с корректными параметрами"""
    print("\n=== 6.3.3 - ТЕСТИРОВАНИЕ ВЫЗОВОВ МЕТОДОВ ===")
    
    if not engine:
        print("❌ Движок не создан, пропускаем тест")
        return False
    
    test_results = []
    
    try:
        # Тест initialize
        result = engine.initialize()
        test_results.append(("initialize", result, "bool"))
        print(f"✅ initialize() -> {result}")
    except Exception as e:
        test_results.append(("initialize", False, f"Ошибка: {e}"))
        print(f"❌ initialize() -> Ошибка: {e}")
    
    try:
        # Тест add_scaling_rule
        result = engine.add_scaling_rule(rule)
        test_results.append(("add_scaling_rule", result, "bool"))
        print(f"✅ add_scaling_rule() -> {result}")
    except Exception as e:
        test_results.append(("add_scaling_rule", False, f"Ошибка: {e}"))
        print(f"❌ add_scaling_rule() -> Ошибка: {e}")
    
    try:
        # Тест collect_metric
        result = engine.collect_metric(metric)
        test_results.append(("collect_metric", result, "bool"))
        print(f"✅ collect_metric() -> {result}")
    except Exception as e:
        test_results.append(("collect_metric", False, f"Ошибка: {e}"))
        print(f"❌ collect_metric() -> Ошибка: {e}")
    
    try:
        # Тест get_scaling_rules
        result = engine.get_scaling_rules()
        test_results.append(("get_scaling_rules", len(result), f"List[{len(result)}]"))
        print(f"✅ get_scaling_rules() -> {len(result)} правил")
    except Exception as e:
        test_results.append(("get_scaling_rules", 0, f"Ошибка: {e}"))
        print(f"❌ get_scaling_rules() -> Ошибка: {e}")
    
    try:
        # Тест get_scaling_metrics
        result = engine.get_scaling_metrics()
        test_results.append(("get_scaling_metrics", result, "ScalingMetrics"))
        print(f"✅ get_scaling_metrics() -> {type(result).__name__}")
    except Exception as e:
        test_results.append(("get_scaling_metrics", None, f"Ошибка: {e}"))
        print(f"❌ get_scaling_metrics() -> Ошибка: {e}")
    
    try:
        # Тест get_engine_status
        result = engine.get_engine_status()
        test_results.append(("get_engine_status", result, "Dict"))
        print(f"✅ get_engine_status() -> {type(result).__name__}")
    except Exception as e:
        test_results.append(("get_engine_status", None, f"Ошибка: {e}"))
        print(f"❌ get_engine_status() -> Ошибка: {e}")
    
    try:
        # Тест make_scaling_decision
        result = engine.make_scaling_decision("test-service")
        test_results.append(("make_scaling_decision", result, "Optional[ScalingDecision]"))
        print(f"✅ make_scaling_decision() -> {type(result).__name__ if result else 'None'}")
    except Exception as e:
        test_results.append(("make_scaling_decision", None, f"Ошибка: {e}"))
        print(f"❌ make_scaling_decision() -> Ошибка: {e}")
    
    try:
        # Тест get_scaling_decisions
        result = engine.get_scaling_decisions()
        test_results.append(("get_scaling_decisions", len(result), f"List[{len(result)}]"))
        print(f"✅ get_scaling_decisions() -> {len(result)} решений")
    except Exception as e:
        test_results.append(("get_scaling_decisions", 0, f"Ошибка: {e}"))
        print(f"❌ get_scaling_decisions() -> Ошибка: {e}")
    
    try:
        # Тест remove_scaling_rule
        result = engine.remove_scaling_rule("test_rule")
        test_results.append(("remove_scaling_rule", result, "bool"))
        print(f"✅ remove_scaling_rule() -> {result}")
    except Exception as e:
        test_results.append(("remove_scaling_rule", False, f"Ошибка: {e}"))
        print(f"❌ remove_scaling_rule() -> Ошибка: {e}")
    
    try:
        # Тест stop
        result = engine.stop()
        test_results.append(("stop", result, "bool"))
        print(f"✅ stop() -> {result}")
    except Exception as e:
        test_results.append(("stop", False, f"Ошибка: {e}"))
        print(f"❌ stop() -> Ошибка: {e}")
    
    # Статистика тестов
    successful_tests = sum(1 for _, _, result_type in test_results if not result_type.startswith("Ошибка"))
    total_tests = len(test_results)
    
    print(f"\n📊 Успешных тестов: {successful_tests}/{total_tests}")
    
    return successful_tests == total_tests

def test_exception_handling(engine):
    """6.3.4 - Проверка обработки исключений в методах"""
    print("\n=== 6.3.4 - ПРОВЕРКА ОБРАБОТКИ ИСКЛЮЧЕНИЙ ===")
    
    if not engine:
        print("❌ Движок не создан, пропускаем тест")
        return False
    
    exception_tests = []
    
    try:
        # Тест с некорректными параметрами
        result = engine.add_scaling_rule(None)
        exception_tests.append(("add_scaling_rule(None)", "Обработано", result))
        print(f"✅ add_scaling_rule(None) -> Обработано: {result}")
    except Exception as e:
        exception_tests.append(("add_scaling_rule(None)", "Исключение", str(e)))
        print(f"⚠️ add_scaling_rule(None) -> Исключение: {e}")
    
    try:
        # Тест с несуществующим правилом
        result = engine.remove_scaling_rule("nonexistent_rule")
        exception_tests.append(("remove_scaling_rule(nonexistent)", "Обработано", result))
        print(f"✅ remove_scaling_rule(nonexistent) -> Обработано: {result}")
    except Exception as e:
        exception_tests.append(("remove_scaling_rule(nonexistent)", "Исключение", str(e)))
        print(f"⚠️ remove_scaling_rule(nonexistent) -> Исключение: {e}")
    
    try:
        # Тест с некорректной метрикой
        result = engine.collect_metric(None)
        exception_tests.append(("collect_metric(None)", "Обработано", result))
        print(f"✅ collect_metric(None) -> Обработано: {result}")
    except Exception as e:
        exception_tests.append(("collect_metric(None)", "Исключение", str(e)))
        print(f"⚠️ collect_metric(None) -> Исключение: {e}")
    
    # Статистика обработки исключений
    handled_exceptions = sum(1 for _, result, _ in exception_tests if result == "Обработано")
    total_exception_tests = len(exception_tests)
    
    print(f"\n📊 Обработано исключений: {handled_exceptions}/{total_exception_tests}")
    
    return handled_exceptions >= total_exception_tests * 0.8  # 80% должны быть обработаны

def main():
    """Основная функция тестирования"""
    print("🔍 ЭТАП 6.3 - ПРОВЕРКА ДОСТУПНОСТИ МЕТОДОВ")
    print("=" * 60)
    
    # 6.3.1 - Создание экземпляров
    engine, metric, rule = test_class_instantiation()
    
    # 6.3.2 - Проверка доступности
    accessibility_ok = test_public_methods_accessibility(engine, metric, rule)
    
    # 6.3.3 - Тестирование вызовов
    calls_ok = test_method_calls_with_correct_parameters(engine, metric, rule)
    
    # 6.3.4 - Проверка исключений
    exceptions_ok = test_exception_handling(engine)
    
    # Итоговый результат
    print("\n" + "=" * 60)
    print("📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ ЭТАПА 6.3:")
    print(f"✅ Создание экземпляров: {'ПРОЙДЕНО' if engine else 'ПРОВАЛЕНО'}")
    print(f"✅ Доступность методов: {'ПРОЙДЕНО' if accessibility_ok else 'ПРОВАЛЕНО'}")
    print(f"✅ Вызовы методов: {'ПРОЙДЕНО' if calls_ok else 'ПРОВАЛЕНО'}")
    print(f"✅ Обработка исключений: {'ПРОЙДЕНО' if exceptions_ok else 'ПРОВАЛЕНО'}")
    
    overall_success = engine and accessibility_ok and calls_ok and exceptions_ok
    print(f"\n🎯 ОБЩИЙ РЕЗУЛЬТАТ: {'ПРОЙДЕНО' if overall_success else 'ПРОВАЛЕНО'}")
    
    return overall_success

if __name__ == "__main__":
    main()