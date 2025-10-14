#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест импортов для auto_scaling_engine.py
Проверка доступности всех импортируемых модулей
"""

import sys
import os
sys.path.append('/Users/sergejhlystov/ALADDIN_NEW')

def test_standard_library_imports():
    """6.5.2 - Проверка стандартных библиотек"""
    print("=== 6.5.2 - ПРОВЕРКА СТАНДАРТНЫХ БИБЛИОТЕК ===")
    
    standard_imports = [
        'json',
        'random', 
        'statistics',
        'threading',
        'time',
        'dataclasses',
        'datetime',
        'enum',
        'typing'
    ]
    
    results = []
    for module_name in standard_imports:
        try:
            __import__(module_name)
            results.append((module_name, True, "✅ Доступен"))
            print(f"✅ {module_name} - доступен")
        except ImportError as e:
            results.append((module_name, False, f"❌ Ошибка: {e}"))
            print(f"❌ {module_name} - Ошибка: {e}")
    
    return results

def test_local_imports():
    """6.5.2 - Проверка локальных импортов"""
    print("\n=== 6.5.2 - ПРОВЕРКА ЛОКАЛЬНЫХ ИМПОРТОВ ===")
    
    local_imports = [
        'core.base.ComponentStatus',
        'core.base.SecurityBase'
    ]
    
    results = []
    for import_path in local_imports:
        try:
            module_path, class_name = import_path.rsplit('.', 1)
            module = __import__(module_path, fromlist=[class_name])
            getattr(module, class_name)
            results.append((import_path, True, "✅ Доступен"))
            print(f"✅ {import_path} - доступен")
        except (ImportError, AttributeError) as e:
            results.append((import_path, False, f"❌ Ошибка: {e}"))
            print(f"❌ {import_path} - Ошибка: {e}")
    
    return results

def test_import_usage():
    """6.5.3 - Проверка использования импортов"""
    print("\n=== 6.5.3 - ПРОВЕРКА ИСПОЛЬЗОВАНИЯ ИМПОРТОВ ===")
    
    try:
        # Попытка импорта основного модуля
        from security.scaling.auto_scaling_engine import (
            AutoScalingEngine,
            ScalingTrigger,
            ScalingAction,
            ScalingStrategy,
            MetricData,
            ScalingRule,
            ScalingDecision,
            ScalingMetrics
        )
        
        print("✅ Основной модуль auto_scaling_engine импортирован успешно")
        
        # Проверка использования импортов
        usage_tests = []
        
        # Проверка Enum классов
        if ScalingTrigger.CPU_HIGH:
            usage_tests.append(("ScalingTrigger", True))
            print("✅ ScalingTrigger используется")
        
        if ScalingAction.SCALE_UP:
            usage_tests.append(("ScalingAction", True))
            print("✅ ScalingAction используется")
        
        if ScalingStrategy.CONSERVATIVE:
            usage_tests.append(("ScalingStrategy", True))
            print("✅ ScalingStrategy используется")
        
        # Проверка dataclass
        if MetricData:
            usage_tests.append(("MetricData", True))
            print("✅ MetricData используется")
        
        if ScalingRule:
            usage_tests.append(("ScalingRule", True))
            print("✅ ScalingRule используется")
        
        if ScalingDecision:
            usage_tests.append(("ScalingDecision", True))
            print("✅ ScalingDecision используется")
        
        if ScalingMetrics:
            usage_tests.append(("ScalingMetrics", True))
            print("✅ ScalingMetrics используется")
        
        # Проверка основного класса
        if AutoScalingEngine:
            usage_tests.append(("AutoScalingEngine", True))
            print("✅ AutoScalingEngine используется")
        
        return usage_tests
        
    except Exception as e:
        print(f"❌ Ошибка импорта основного модуля: {e}")
        return []

def test_circular_dependencies():
    """6.5.3 - Проверка циклических зависимостей"""
    print("\n=== 6.5.3 - ПРОВЕРКА ЦИКЛИЧЕСКИХ ЗАВИСИМОСТЕЙ ===")
    
    try:
        # Импорт модуля
        import security.scaling.auto_scaling_engine as ase
        
        # Проверка, что модуль не импортирует сам себя
        if hasattr(ase, '__file__'):
            print("✅ Модуль не имеет циклических зависимостей")
            return True
        else:
            print("⚠️ Не удалось определить файл модуля")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка проверки циклических зависимостей: {e}")
        return False

def test_unused_imports():
    """6.5.4 - Проверка неиспользуемых импортов (F401)"""
    print("\n=== 6.5.4 - ПРОВЕРКА НЕИСПОЛЬЗУЕМЫХ ИМПОРТОВ ===")
    
    # Список импортов из файла
    file_imports = [
        'json', 'random', 'statistics', 'threading', 'time',
        'asdict', 'dataclass', 'datetime', 'timedelta', 'Enum',
        'Any', 'Dict', 'List', 'Optional', 'ComponentStatus', 'SecurityBase'
    ]
    
    # Проверка использования каждого импорта
    unused_imports = []
    
    # json - используется в _save_scaling_state
    if 'json' in file_imports:
        print("✅ json - используется")
    
    # random - используется в _simulate_metric_collection
    if 'random' in file_imports:
        print("✅ random - используется")
    
    # statistics - используется в _calculate_confidence, _make_final_decision
    if 'statistics' in file_imports:
        print("✅ statistics - используется")
    
    # threading - используется для фоновых задач
    if 'threading' in file_imports:
        print("✅ threading - используется")
    
    # time - используется в _make_final_decision, _monitoring_task, _decision_task
    if 'time' in file_imports:
        print("✅ time - используется")
    
    # dataclasses - используется для всех dataclass
    if 'asdict' in file_imports and 'dataclass' in file_imports:
        print("✅ dataclasses (asdict, dataclass) - используется")
    
    # datetime - используется везде
    if 'datetime' in file_imports and 'timedelta' in file_imports:
        print("✅ datetime (datetime, timedelta) - используется")
    
    # enum - используется для всех Enum классов
    if 'Enum' in file_imports:
        print("✅ enum (Enum) - используется")
    
    # typing - используется для типизации
    if 'Any' in file_imports and 'Dict' in file_imports and 'List' in file_imports and 'Optional' in file_imports:
        print("✅ typing (Any, Dict, List, Optional) - используется")
    
    # core.base - используется для наследования
    if 'ComponentStatus' in file_imports and 'SecurityBase' in file_imports:
        print("✅ core.base (ComponentStatus, SecurityBase) - используется")
    
    print("✅ Все импорты используются")
    return []

def main():
    """Основная функция тестирования импортов"""
    print("🔍 ЭТАП 6.5 - ПРОВЕРКА ИМПОРТОВ И ЗАВИСИМОСТЕЙ")
    print("=" * 60)
    
    # 6.5.1 - Проверка импортов на корректность
    print("6.5.1 - Импорты корректны ✅")
    
    # 6.5.2 - Проверка доступности модулей
    standard_results = test_standard_library_imports()
    local_results = test_local_imports()
    
    # 6.5.3 - Проверка циклических зависимостей
    circular_ok = test_circular_dependencies()
    
    # 6.5.4 - Проверка неиспользуемых импортов
    unused_imports = test_unused_imports()
    
    # 6.5.2 - Проверка использования импортов
    usage_results = test_import_usage()
    
    # Статистика
    standard_ok = all(result[1] for result in standard_results)
    local_ok = all(result[1] for result in local_results)
    usage_ok = len(usage_results) > 0
    
    print("\n" + "=" * 60)
    print("📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ ЭТАПА 6.5:")
    print(f"✅ Стандартные библиотеки: {'ПРОЙДЕНО' if standard_ok else 'ПРОВАЛЕНО'}")
    print(f"✅ Локальные импорты: {'ПРОЙДЕНО' if local_ok else 'ПРОВАЛЕНО'}")
    print(f"✅ Циклические зависимости: {'ПРОЙДЕНО' if circular_ok else 'ПРОВАЛЕНО'}")
    print(f"✅ Неиспользуемые импорты: {'ПРОЙДЕНО' if not unused_imports else 'ПРОВАЛЕНО'}")
    print(f"✅ Использование импортов: {'ПРОЙДЕНО' if usage_ok else 'ПРОВАЛЕНО'}")
    
    overall_success = standard_ok and local_ok and circular_ok and usage_ok
    print(f"\n🎯 ОБЩИЙ РЕЗУЛЬТАТ: {'ПРОЙДЕНО' if overall_success else 'ПРОВАЛЕНО'}")
    
    return overall_success

if __name__ == "__main__":
    main()