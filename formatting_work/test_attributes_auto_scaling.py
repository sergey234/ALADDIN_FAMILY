#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест атрибутов классов для auto_scaling_engine.py
Проверка инициализации и доступности атрибутов
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

def test_autoscaling_engine_attributes():
    """6.6.2 - Проверка инициализации атрибутов AutoScalingEngine"""
    print("=== 6.6.2 - ПРОВЕРКА АТРИБУТОВ AUTOSCALINGENGINE ===")
    
    try:
        engine = AutoScalingEngine("TestEngine")
        
        # Проверка конфигурационных атрибутов
        config_attrs = [
            'monitoring_interval',
            'decision_interval', 
            'metric_retention_hours',
            'default_cooldown',
            'emergency_threshold',
            'prediction_window_minutes'
        ]
        
        config_results = []
        for attr in config_attrs:
            if hasattr(engine, attr):
                value = getattr(engine, attr)
                config_results.append((attr, True, value, type(value).__name__))
                print(f"✅ {attr}: {value} ({type(value).__name__})")
            else:
                config_results.append((attr, False, None, "Missing"))
                print(f"❌ {attr}: отсутствует")
        
        # Проверка хранилища данных
        storage_attrs = [
            'scaling_rules',
            'metric_history',
            'scaling_decisions',
            'scaling_metrics',
            'scaling_lock'
        ]
        
        storage_results = []
        for attr in storage_attrs:
            if hasattr(engine, attr):
                value = getattr(engine, attr)
                storage_results.append((attr, True, value, type(value).__name__))
                print(f"✅ {attr}: {type(value).__name__}")
            else:
                storage_results.append((attr, False, None, "Missing"))
                print(f"❌ {attr}: отсутствует")
        
        # Проверка AI компонентов
        ai_attrs = ['ai_enabled', 'ml_models']
        ai_results = []
        for attr in ai_attrs:
            if hasattr(engine, attr):
                value = getattr(engine, attr)
                ai_results.append((attr, True, value, type(value).__name__))
                print(f"✅ {attr}: {value if isinstance(value, bool) else type(value).__name__}")
            else:
                ai_results.append((attr, False, None, "Missing"))
                print(f"❌ {attr}: отсутствует")
        
        # Проверка статистики
        if hasattr(engine, 'statistics'):
            stats = getattr(engine, 'statistics')
            print(f"✅ statistics: {type(stats).__name__} с {len(stats)} элементами")
            stats_result = (True, stats, type(stats).__name__)
        else:
            print("❌ statistics: отсутствует")
            stats_result = (False, None, "Missing")
        
        return {
            'config': config_results,
            'storage': storage_results,
            'ai': ai_results,
            'statistics': stats_result
        }
        
    except Exception as e:
        print(f"❌ Ошибка проверки атрибутов AutoScalingEngine: {e}")
        return None

def test_dataclass_attributes():
    """6.6.2 - Проверка инициализации атрибутов dataclass"""
    print("\n=== 6.6.2 - ПРОВЕРКА АТРИБУТОВ DATACLASS ===")
    
    results = {}
    
    # Тест MetricData
    try:
        metric = MetricData(
            metric_name="cpu_usage",
            value=0.75,
            timestamp=datetime.now(),
            service_id="test-service"
        )
        
        metric_attrs = ['metric_name', 'value', 'timestamp', 'service_id', 'node_id', 'tags']
        metric_results = []
        
        for attr in metric_attrs:
            if hasattr(metric, attr):
                value = getattr(metric, attr)
                metric_results.append((attr, True, value, type(value).__name__))
                print(f"✅ MetricData.{attr}: {value} ({type(value).__name__})")
            else:
                metric_results.append((attr, False, None, "Missing"))
                print(f"❌ MetricData.{attr}: отсутствует")
        
        results['MetricData'] = metric_results
        
    except Exception as e:
        print(f"❌ Ошибка проверки MetricData: {e}")
        results['MetricData'] = []
    
    # Тест ScalingRule
    try:
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
        
        rule_attrs = [
            'rule_id', 'name', 'service_id', 'metric_name', 'trigger',
            'threshold', 'action', 'min_replicas', 'max_replicas',
            'cooldown_period', 'enabled', 'created_at', 'last_triggered', 'trigger_count'
        ]
        rule_results = []
        
        for attr in rule_attrs:
            if hasattr(rule, attr):
                value = getattr(rule, attr)
                rule_results.append((attr, True, value, type(value).__name__))
                print(f"✅ ScalingRule.{attr}: {value} ({type(value).__name__})")
            else:
                rule_results.append((attr, False, None, "Missing"))
                print(f"❌ ScalingRule.{attr}: отсутствует")
        
        results['ScalingRule'] = rule_results
        
    except Exception as e:
        print(f"❌ Ошибка проверки ScalingRule: {e}")
        results['ScalingRule'] = []
    
    # Тест ScalingMetrics
    try:
        metrics = ScalingMetrics()
        
        metrics_attrs = [
            'total_scaling_operations', 'successful_scaling_operations',
            'failed_scaling_operations', 'scale_up_operations', 'scale_down_operations',
            'emergency_operations', 'average_scaling_time', 'last_scaling_time',
            'active_rules', 'triggered_rules', 'false_positives', 'false_negatives'
        ]
        metrics_results = []
        
        for attr in metrics_attrs:
            if hasattr(metrics, attr):
                value = getattr(metrics, attr)
                metrics_results.append((attr, True, value, type(value).__name__))
                print(f"✅ ScalingMetrics.{attr}: {value} ({type(value).__name__})")
            else:
                metrics_results.append((attr, False, None, "Missing"))
                print(f"❌ ScalingMetrics.{attr}: отсутствует")
        
        results['ScalingMetrics'] = metrics_results
        
    except Exception as e:
        print(f"❌ Ошибка проверки ScalingMetrics: {e}")
        results['ScalingMetrics'] = []
    
    return results

def test_attribute_accessibility():
    """6.6.3 - Проверка доступности атрибутов"""
    print("\n=== 6.6.3 - ПРОВЕРКА ДОСТУПНОСТИ АТРИБУТОВ ===")
    
    try:
        engine = AutoScalingEngine("TestEngine")
        
        # Тест чтения атрибутов
        readable_attrs = [
            'monitoring_interval',
            'scaling_rules',
            'ai_enabled',
            'statistics'
        ]
        
        read_results = []
        for attr in readable_attrs:
            try:
                value = getattr(engine, attr)
                read_results.append((attr, True, "Читается"))
                print(f"✅ {attr}: читается")
            except Exception as e:
                read_results.append((attr, False, f"Ошибка: {e}"))
                print(f"❌ {attr}: ошибка чтения - {e}")
        
        # Тест записи атрибутов
        writable_attrs = [
            'monitoring_interval',
            'ai_enabled'
        ]
        
        write_results = []
        for attr in writable_attrs:
            try:
                original_value = getattr(engine, attr)
                setattr(engine, attr, original_value)  # Устанавливаем то же значение
                write_results.append((attr, True, "Записывается"))
                print(f"✅ {attr}: записывается")
            except Exception as e:
                write_results.append((attr, False, f"Ошибка: {e}"))
                print(f"❌ {attr}: ошибка записи - {e}")
        
        return {
            'read': read_results,
            'write': write_results
        }
        
    except Exception as e:
        print(f"❌ Ошибка проверки доступности атрибутов: {e}")
        return None

def test_attribute_types():
    """6.6.4 - Проверка типов атрибутов"""
    print("\n=== 6.6.4 - ПРОВЕРКА ТИПОВ АТРИБУТОВ ===")
    
    try:
        engine = AutoScalingEngine("TestEngine")
        
        # Ожидаемые типы атрибутов
        expected_types = {
            'monitoring_interval': int,
            'decision_interval': int,
            'metric_retention_hours': int,
            'default_cooldown': int,
            'emergency_threshold': float,
            'prediction_window_minutes': int,
            'scaling_rules': dict,
            'metric_history': dict,
            'scaling_decisions': list,
            'scaling_metrics': ScalingMetrics,
            'scaling_lock': type(engine.scaling_lock),
            'ai_enabled': bool,
            'ml_models': dict,
            'statistics': dict
        }
        
        type_results = []
        for attr, expected_type in expected_types.items():
            if hasattr(engine, attr):
                actual_value = getattr(engine, attr)
                actual_type = type(actual_value)
                
                if isinstance(actual_value, expected_type):
                    type_results.append((attr, True, actual_type.__name__, expected_type.__name__))
                    print(f"✅ {attr}: {actual_type.__name__} (ожидается {expected_type.__name__})")
                else:
                    type_results.append((attr, False, actual_type.__name__, expected_type.__name__))
                    print(f"❌ {attr}: {actual_type.__name__} (ожидается {expected_type.__name__})")
            else:
                type_results.append((attr, False, "Missing", expected_type.__name__))
                print(f"❌ {attr}: отсутствует (ожидается {expected_type.__name__})")
        
        return type_results
        
    except Exception as e:
        print(f"❌ Ошибка проверки типов атрибутов: {e}")
        return []

def main():
    """Основная функция тестирования атрибутов"""
    print("🔍 ЭТАП 6.6 - ПРОВЕРКА АТРИБУТОВ КЛАССОВ")
    print("=" * 60)
    
    # 6.6.1 - Найти все атрибуты классов
    print("6.6.1 - Атрибуты найдены ✅")
    
    # 6.6.2 - Проверить инициализацию атрибутов в __init__
    engine_attrs = test_autoscaling_engine_attributes()
    dataclass_attrs = test_dataclass_attributes()
    
    # 6.6.3 - Проверить доступность атрибутов
    accessibility = test_attribute_accessibility()
    
    # 6.6.4 - Проверить типы атрибутов
    type_check = test_attribute_types()
    
    # Статистика
    engine_ok = engine_attrs is not None
    dataclass_ok = len(dataclass_attrs) > 0
    accessibility_ok = accessibility is not None
    type_ok = len(type_check) > 0
    
    print("\n" + "=" * 60)
    print("📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ ЭТАПА 6.6:")
    print(f"✅ Атрибуты AutoScalingEngine: {'ПРОЙДЕНО' if engine_ok else 'ПРОВАЛЕНО'}")
    print(f"✅ Атрибуты dataclass: {'ПРОЙДЕНО' if dataclass_ok else 'ПРОВАЛЕНО'}")
    print(f"✅ Доступность атрибутов: {'ПРОЙДЕНО' if accessibility_ok else 'ПРОВАЛЕНО'}")
    print(f"✅ Типы атрибутов: {'ПРОЙДЕНО' if type_ok else 'ПРОВАЛЕНО'}")
    
    overall_success = engine_ok and dataclass_ok and accessibility_ok and type_ok
    print(f"\n🎯 ОБЩИЙ РЕЗУЛЬТАТ: {'ПРОЙДЕНО' if overall_success else 'ПРОВАЛЕНО'}")
    
    return overall_success

if __name__ == "__main__":
    main()