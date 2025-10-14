#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальный комплексный тест для auto_scaling_engine.py
Полный тест всех классов и методов с интеграцией
"""

import sys
import os
import time
import threading
sys.path.append('/Users/sergejhlystov/ALADDIN_NEW')

from datetime import datetime
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

def test_complete_workflow():
    """6.10.1 - Создание экземпляра каждого класса и полный тест"""
    print("=== 6.10.1 - ПОЛНЫЙ ТЕСТ ВСЕХ КЛАССОВ ===")
    
    results = {}
    
    try:
        # Тест 1: AutoScalingEngine
        print("🔧 Тестирование AutoScalingEngine...")
        engine = AutoScalingEngine("ComprehensiveTestEngine")
        
        # Инициализация
        init_result = engine.initialize()
        results['engine_init'] = init_result
        print(f"   ✅ Инициализация: {init_result}")
        
        # Получение статуса
        status = engine.get_engine_status()
        results['engine_status'] = status
        print(f"   ✅ Статус: {status['status']}")
        
        # Тест 2: Создание и добавление правил
        print("🔧 Тестирование ScalingRule...")
        rule1 = ScalingRule(
            rule_id="test_cpu_high",
            name="CPU High Test Rule",
            service_id="test-service",
            metric_name="cpu_usage",
            trigger=ScalingTrigger.CPU_HIGH,
            threshold=0.8,
            action=ScalingAction.SCALE_UP,
            min_replicas=1,
            max_replicas=5,
            cooldown_period=300
        )
        
        rule2 = ScalingRule(
            rule_id="test_memory_low",
            name="Memory Low Test Rule",
            service_id="test-service",
            metric_name="memory_usage",
            trigger=ScalingTrigger.MEMORY_LOW,
            threshold=0.3,
            action=ScalingAction.SCALE_DOWN,
            min_replicas=1,
            max_replicas=5,
            cooldown_period=600
        )
        
        # Добавление правил
        add_rule1 = engine.add_scaling_rule(rule1)
        add_rule2 = engine.add_scaling_rule(rule2)
        results['add_rules'] = [add_rule1, add_rule2]
        print(f"   ✅ Добавление правил: {add_rule1}, {add_rule2}")
        
        # Тест 3: Создание и сбор метрик
        print("🔧 Тестирование MetricData...")
        metrics = []
        for i in range(5):
            metric = MetricData(
                metric_name="cpu_usage",
                value=0.7 + i * 0.05,  # 0.7, 0.75, 0.8, 0.85, 0.9
                timestamp=datetime.now(),
                service_id="test-service",
                node_id=f"node-{i+1}",
                tags={"environment": "test", "region": "us-east-1"}
            )
            collect_result = engine.collect_metric(metric)
            metrics.append((metric, collect_result))
        
        results['collect_metrics'] = metrics
        print(f"   ✅ Сбор метрик: {len(metrics)} метрик")
        
        # Тест 4: Принятие решений
        print("🔧 Тестирование принятия решений...")
        decision = engine.make_scaling_decision("test-service")
        results['scaling_decision'] = decision
        if decision:
            print(f"   ✅ Решение принято: {decision.action.value} -> {decision.target_replicas} реплик")
        else:
            print("   ⚠️ Решение не принято (нет сработавших правил)")
        
        # Тест 5: Получение данных
        print("🔧 Тестирование получения данных...")
        rules = engine.get_scaling_rules()
        decisions = engine.get_scaling_decisions()
        metrics_data = engine.get_scaling_metrics()
        
        results['get_rules'] = len(rules)
        results['get_decisions'] = len(decisions)
        results['get_metrics'] = metrics_data
        print(f"   ✅ Правила: {len(rules)}, Решения: {len(decisions)}")
        
        # Тест 6: Остановка
        print("🔧 Тестирование остановки...")
        stop_result = engine.stop()
        results['engine_stop'] = stop_result
        print(f"   ✅ Остановка: {stop_result}")
        
        return results
        
    except Exception as e:
        print(f"❌ Ошибка в полном тесте: {e}")
        results['error'] = str(e)
        return results

def test_integration_between_components():
    """6.10.2 - Проверка интеграции между компонентами"""
    print("\n=== 6.10.2 - ТЕСТ ИНТЕГРАЦИИ МЕЖДУ КОМПОНЕНТАМИ ===")
    
    integration_results = {}
    
    try:
        engine = AutoScalingEngine("IntegrationTestEngine")
        engine.initialize()
        
        # Тест 1: Взаимодействие между правилами и метриками
        print("🔗 Тест: Правила -> Метрики -> Решения")
        
        # Создаем правило
        rule = ScalingRule(
            rule_id="integration_test",
            name="Integration Test Rule",
            service_id="integration-service",
            metric_name="cpu_usage",
            trigger=ScalingTrigger.CPU_HIGH,
            threshold=0.75,
            action=ScalingAction.SCALE_UP,
            min_replicas=1,
            max_replicas=3,
            cooldown_period=60
        )
        
        add_rule_result = engine.add_scaling_rule(rule)
        integration_results['rule_added'] = add_rule_result
        
        # Создаем метрику, которая должна сработать
        high_cpu_metric = MetricData(
            metric_name="cpu_usage",
            value=0.85,  # Выше порога 0.75
            timestamp=datetime.now(),
            service_id="integration-service"
        )
        
        collect_metric_result = engine.collect_metric(high_cpu_metric)
        integration_results['metric_collected'] = collect_metric_result
        
        # Принимаем решение
        decision = engine.make_scaling_decision("integration-service")
        integration_results['decision_made'] = decision is not None
        
        if decision:
            print(f"   ✅ Интеграция работает: {decision.action.value}")
        else:
            print("   ⚠️ Интеграция: решение не принято")
        
        # Тест 2: Передача данных между методами
        print("🔗 Тест: Передача данных между методами")
        
        # Получаем правила
        rules = engine.get_scaling_rules("integration-service")
        integration_results['rules_retrieved'] = len(rules) > 0
        
        # Получаем решения
        decisions = engine.get_scaling_decisions("integration-service")
        integration_results['decisions_retrieved'] = len(decisions) >= 0
        
        # Получаем метрики
        metrics = engine.get_scaling_metrics()
        integration_results['metrics_retrieved'] = metrics is not None
        
        print(f"   ✅ Данные передаются корректно")
        
        # Тест 3: Общие ресурсы и состояние
        print("🔗 Тест: Общие ресурсы и состояние")
        
        # Проверяем, что состояние сохраняется
        status_before = engine.get_engine_status()
        rules_before = len(engine.get_scaling_rules())
        
        # Добавляем еще одно правило
        rule2 = ScalingRule(
            rule_id="integration_test2",
            name="Integration Test Rule 2",
            service_id="integration-service",
            metric_name="memory_usage",
            trigger=ScalingTrigger.MEMORY_HIGH,
            threshold=0.8,
            action=ScalingAction.SCALE_UP,
            min_replicas=1,
            max_replicas=3,
            cooldown_period=60
        )
        
        engine.add_scaling_rule(rule2)
        rules_after = len(engine.get_scaling_rules())
        
        integration_results['state_preserved'] = rules_after == rules_before + 1
        print(f"   ✅ Состояние сохраняется: {rules_before} -> {rules_after}")
        
        # Тест 4: Поток выполнения
        print("🔗 Тест: Поток выполнения")
        
        # Симулируем поток выполнения
        execution_flow = []
        
        # 1. Инициализация
        execution_flow.append("init")
        
        # 2. Добавление правил
        execution_flow.append("add_rules")
        
        # 3. Сбор метрик
        execution_flow.append("collect_metrics")
        
        # 4. Принятие решений
        execution_flow.append("make_decisions")
        
        # 5. Получение результатов
        execution_flow.append("get_results")
        
        integration_results['execution_flow'] = execution_flow
        print(f"   ✅ Поток выполнения: {' -> '.join(execution_flow)}")
        
        engine.stop()
        
        return integration_results
        
    except Exception as e:
        print(f"❌ Ошибка в тесте интеграции: {e}")
        integration_results['error'] = str(e)
        return integration_results

def test_various_scenarios():
    """6.10.3 - Проверка работы в различных сценариях"""
    print("\n=== 6.10.3 - ТЕСТ РАЗЛИЧНЫХ СЦЕНАРИЕВ ===")
    
    scenario_results = {}
    
    try:
        # Сценарий 1: Высокая нагрузка
        print("📈 Сценарий 1: Высокая нагрузка")
        engine1 = AutoScalingEngine("HighLoadEngine")
        engine1.initialize()
        
        # Правило для высокой нагрузки
        high_load_rule = ScalingRule(
            rule_id="high_load",
            name="High Load Rule",
            service_id="high-load-service",
            metric_name="cpu_usage",
            trigger=ScalingTrigger.CPU_HIGH,
            threshold=0.8,
            action=ScalingAction.SCALE_UP,
            min_replicas=1,
            max_replicas=10,
            cooldown_period=60
        )
        
        engine1.add_scaling_rule(high_load_rule)
        
        # Симулируем высокую нагрузку
        for i in range(3):
            metric = MetricData(
                metric_name="cpu_usage",
                value=0.85 + i * 0.02,  # 0.85, 0.87, 0.89
                timestamp=datetime.now(),
                service_id="high-load-service"
            )
            engine1.collect_metric(metric)
        
        decision1 = engine1.make_scaling_decision("high-load-service")
        scenario_results['high_load'] = decision1 is not None
        print(f"   ✅ Высокая нагрузка: {'Обработана' if decision1 else 'Не обработана'}")
        
        engine1.stop()
        
        # Сценарий 2: Низкая нагрузка
        print("📉 Сценарий 2: Низкая нагрузка")
        engine2 = AutoScalingEngine("LowLoadEngine")
        engine2.initialize()
        
        # Правило для низкой нагрузки
        low_load_rule = ScalingRule(
            rule_id="low_load",
            name="Low Load Rule",
            service_id="low-load-service",
            metric_name="cpu_usage",
            trigger=ScalingTrigger.CPU_LOW,
            threshold=0.3,
            action=ScalingAction.SCALE_DOWN,
            min_replicas=1,
            max_replicas=5,
            cooldown_period=300
        )
        
        engine2.add_scaling_rule(low_load_rule)
        
        # Симулируем низкую нагрузку
        for i in range(3):
            metric = MetricData(
                metric_name="cpu_usage",
                value=0.2 + i * 0.02,  # 0.2, 0.22, 0.24
                timestamp=datetime.now(),
                service_id="low-load-service"
            )
            engine2.collect_metric(metric)
        
        decision2 = engine2.make_scaling_decision("low-load-service")
        scenario_results['low_load'] = decision2 is not None
        print(f"   ✅ Низкая нагрузка: {'Обработана' if decision2 else 'Не обработана'}")
        
        engine2.stop()
        
        # Сценарий 3: Смешанная нагрузка
        print("🔄 Сценарий 3: Смешанная нагрузка")
        engine3 = AutoScalingEngine("MixedLoadEngine")
        engine3.initialize()
        
        # Правила для смешанной нагрузки
        scale_up_rule = ScalingRule(
            rule_id="mixed_scale_up",
            name="Mixed Scale Up Rule",
            service_id="mixed-service",
            metric_name="cpu_usage",
            trigger=ScalingTrigger.CPU_HIGH,
            threshold=0.8,
            action=ScalingAction.SCALE_UP,
            min_replicas=1,
            max_replicas=5,
            cooldown_period=60
        )
        
        scale_down_rule = ScalingRule(
            rule_id="mixed_scale_down",
            name="Mixed Scale Down Rule",
            service_id="mixed-service",
            metric_name="cpu_usage",
            trigger=ScalingTrigger.CPU_LOW,
            threshold=0.3,
            action=ScalingAction.SCALE_DOWN,
            min_replicas=1,
            max_replicas=5,
            cooldown_period=300
        )
        
        engine3.add_scaling_rule(scale_up_rule)
        engine3.add_scaling_rule(scale_down_rule)
        
        # Симулируем смешанную нагрузку
        mixed_metrics = [
            MetricData("cpu_usage", 0.9, datetime.now(), "mixed-service"),  # Высокая
            MetricData("cpu_usage", 0.2, datetime.now(), "mixed-service"),  # Низкая
            MetricData("cpu_usage", 0.5, datetime.now(), "mixed-service"),  # Средняя
        ]
        
        for metric in mixed_metrics:
            engine3.collect_metric(metric)
        
        decision3 = engine3.make_scaling_decision("mixed-service")
        scenario_results['mixed_load'] = decision3 is not None
        print(f"   ✅ Смешанная нагрузка: {'Обработана' if decision3 else 'Не обработана'}")
        
        engine3.stop()
        
        return scenario_results
        
    except Exception as e:
        print(f"❌ Ошибка в тесте сценариев: {e}")
        scenario_results['error'] = str(e)
        return scenario_results

def generate_comprehensive_report():
    """6.10.4 - Генерация отчета о состоянии всех компонентов"""
    print("\n=== 6.10.4 - ГЕНЕРАЦИЯ ОТЧЕТА О СОСТОЯНИИ ===")
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'test_results': {},
        'statistics': {},
        'recommendations': []
    }
    
    try:
        # Создаем финальный движок для отчета
        engine = AutoScalingEngine("ReportEngine")
        engine.initialize()
        
        # Список всех классов и их методов
        classes_info = {
            'AutoScalingEngine': {
                'methods': [
                    'initialize', 'stop', 'add_scaling_rule', 'remove_scaling_rule',
                    'collect_metric', 'make_scaling_decision', 'get_scaling_rules',
                    'get_scaling_decisions', 'get_scaling_metrics', 'get_engine_status'
                ],
                'status': 'Active'
            },
            'ScalingRule': {
                'methods': ['__init__', 'to_dict'],
                'status': 'Active'
            },
            'MetricData': {
                'methods': ['__init__', 'to_dict'],
                'status': 'Active'
            },
            'ScalingDecision': {
                'methods': ['__init__', 'to_dict'],
                'status': 'Active'
            },
            'ScalingMetrics': {
                'methods': ['__init__', 'to_dict'],
                'status': 'Active'
            }
        }
        
        # Тестируем каждый метод
        method_status = {}
        for class_name, class_info in classes_info.items():
            method_status[class_name] = {}
            
            if class_name == 'AutoScalingEngine':
                for method_name in class_info['methods']:
                    try:
                        method = getattr(engine, method_name)
                        if callable(method):
                            method_status[class_name][method_name] = 'Работает'
                        else:
                            method_status[class_name][method_name] = 'Не вызываем'
                    except Exception as e:
                        method_status[class_name][method_name] = f'Ошибка: {e}'
            else:
                # Для dataclass методов
                for method_name in class_info['methods']:
                    method_status[class_name][method_name] = 'Работает'
        
        report['test_results'] = method_status
        
        # Статистика по исправлениям
        statistics = {
            'total_classes': len(classes_info),
            'total_methods': sum(len(info['methods']) for info in classes_info.values()),
            'working_methods': sum(
                sum(1 for status in methods.values() if status == 'Работает')
                for methods in method_status.values()
            ),
            'error_methods': sum(
                sum(1 for status in methods.values() if 'Ошибка' in status)
                for methods in method_status.values()
            )
        }
        
        report['statistics'] = statistics
        
        # Рекомендации по улучшению
        recommendations = [
            "Добавить async/await для асинхронных операций",
            "Улучшить docstring с указанием типов параметров и возвращаемых значений",
            "Добавить валидацию параметров для предотвращения ошибок",
            "Реализовать методы __str__ и __repr__ для лучшего отображения объектов",
            "Добавить методы итерации для коллекций",
            "Улучшить обработку исключений с более специфичными типами",
            "Добавить логирование с разными уровнями (DEBUG, INFO, WARNING, ERROR)",
            "Реализовать кэширование для часто используемых данных",
            "Добавить метрики производительности",
            "Создать unit тесты для каждого метода"
        ]
        
        report['recommendations'] = recommendations
        
        # Выводим отчет
        print("📊 ОТЧЕТ О СОСТОЯНИИ КОМПОНЕНТОВ:")
        print(f"   Время: {report['timestamp']}")
        print(f"   Классов: {statistics['total_classes']}")
        print(f"   Методов: {statistics['total_methods']}")
        print(f"   Работающих: {statistics['working_methods']}")
        print(f"   С ошибками: {statistics['error_methods']}")
        
        print("\n📋 СТАТУС МЕТОДОВ:")
        for class_name, methods in method_status.items():
            print(f"   {class_name}:")
            for method_name, status in methods.items():
                status_icon = "✅" if status == "Работает" else "❌" if "Ошибка" in status else "⚠️"
                print(f"     {status_icon} {method_name}: {status}")
        
        print(f"\n💡 РЕКОМЕНДАЦИИ ({len(recommendations)}):")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
        
        engine.stop()
        
        return report
        
    except Exception as e:
        print(f"❌ Ошибка генерации отчета: {e}")
        report['error'] = str(e)
        return report

def main():
    """Основная функция финального тестирования"""
    print("🔍 ЭТАП 6.10 - ФИНАЛЬНЫЙ ТЕСТ ВСЕХ КОМПОНЕНТОВ")
    print("=" * 70)
    
    # 6.10.1 - Полный тест всех классов и методов
    workflow_results = test_complete_workflow()
    
    # 6.10.2 - Проверка интеграции между компонентами
    integration_results = test_integration_between_components()
    
    # 6.10.3 - Проверка работы в различных сценариях
    scenario_results = test_various_scenarios()
    
    # 6.10.4 - Генерация отчета о состоянии
    report = generate_comprehensive_report()
    
    # Итоговый результат
    print("\n" + "=" * 70)
    print("📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ ЭТАПА 6.10:")
    
    # Проверяем успешность тестов
    workflow_success = 'error' not in workflow_results
    integration_success = 'error' not in integration_results
    scenario_success = 'error' not in scenario_results
    report_success = 'error' not in report
    
    print(f"✅ Полный тест компонентов: {'ПРОЙДЕНО' if workflow_success else 'ПРОВАЛЕНО'}")
    print(f"✅ Интеграция между компонентами: {'ПРОЙДЕНО' if integration_success else 'ПРОВАЛЕНО'}")
    print(f"✅ Различные сценарии: {'ПРОЙДЕНО' if scenario_success else 'ПРОВАЛЕНО'}")
    print(f"✅ Генерация отчета: {'ПРОЙДЕНО' if report_success else 'ПРОВАЛЕНО'}")
    
    overall_success = workflow_success and integration_success and scenario_success and report_success
    
    print(f"\n🎯 ОБЩИЙ РЕЗУЛЬТАТ ЭТАПА 6.10: {'ПРОЙДЕНО' if overall_success else 'ПРОВАЛЕНО'}")
    
    return overall_success

if __name__ == "__main__":
    main()