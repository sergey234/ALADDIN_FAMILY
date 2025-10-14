#!/usr/bin/env python3
"""
Скрипт для тестовой активации критических функций
Активирует по 10 функций за раз, исключая web и портовые функции
"""

import json
import os
import time
import psutil
from datetime import datetime

def load_registry():
    """Загружает реестр функций"""
    with open('data/sfm/function_registry.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_registry(data):
    """Сохраняет реестр функций"""
    with open('data/sfm/function_registry.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_sleeping_critical_functions(data):
    """Получает критические функции в спящем режиме"""
    functions = data.get('functions', {})
    critical_sleeping = []
    
    for func_id, func_data in functions.items():
        status = func_data.get('status', '')
        priority = func_data.get('priority', '')
        func_type = func_data.get('function_type', '')
        name = func_data.get('name', '')
        
        # Исключаем web функции и функции с портами
        if any(exclude in name.lower() for exclude in ['web', 'interface', 'server', 'api']):
            continue
        if any(exclude in func_type.lower() for exclude in ['web', 'interface', 'server', 'api']):
            continue
            
        # Ищем критические спящие функции
        if status == 'sleeping' and priority == 'critical':
            critical_sleeping.append((func_id, func_data))
    
    return critical_sleeping

def get_system_stats():
    """Получает статистику системы"""
    return {
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory_percent': psutil.virtual_memory().percent,
        'memory_available': psutil.virtual_memory().available,
        'timestamp': datetime.now().isoformat()
    }

def activate_functions(functions_to_activate):
    """Активирует функции в реестре"""
    data = load_registry()
    functions = data.get('functions', {})
    
    activated = []
    for func_id, func_data in functions_to_activate:
        if func_id in functions:
            functions[func_id]['status'] = 'active'
            functions[func_id]['last_updated'] = datetime.now().isoformat()
            activated.append(func_id)
    
    save_registry(data)
    return activated

def test_activation(batch_size=10):
    """Тестирует активацию функций"""
    print(f"🚀 ТЕСТОВАЯ АКТИВАЦИЯ КРИТИЧЕСКИХ ФУНКЦИЙ")
    print(f"================================================")
    
    # Загружаем реестр
    data = load_registry()
    critical_sleeping = get_sleeping_critical_functions(data)
    
    print(f"Всего критических спящих функций: {len(critical_sleeping)}")
    print(f"Размер партии: {batch_size}")
    print("")
    
    # Получаем начальную статистику
    stats_before = get_system_stats()
    print(f"📊 СТАТИСТИКА ДО АКТИВАЦИИ:")
    print(f"   CPU: {stats_before['cpu_percent']:.1f}%")
    print(f"   Memory: {stats_before['memory_percent']:.1f}%")
    print(f"   Available: {stats_before['memory_available'] / 1024**3:.1f} GB")
    print("")
    
    # Активируем функции
    functions_to_activate = critical_sleeping[:batch_size]
    activated = activate_functions(functions_to_activate)
    
    print(f"✅ АКТИВИРОВАНО {len(activated)} ФУНКЦИЙ:")
    for func_id in activated:
        func_data = next(f for f_id, f in functions_to_activate if f_id == func_id)
        print(f"   • {func_data[1].get('name', func_id)} ({func_id})")
    
    # Ждем стабилизации
    print(f"\n⏳ Ожидание стабилизации системы (5 сек)...")
    time.sleep(5)
    
    # Получаем статистику после активации
    stats_after = get_system_stats()
    print(f"\n📊 СТАТИСТИКА ПОСЛЕ АКТИВАЦИИ:")
    print(f"   CPU: {stats_after['cpu_percent']:.1f}% (Δ{stats_after['cpu_percent'] - stats_before['cpu_percent']:+.1f}%)")
    print(f"   Memory: {stats_after['memory_percent']:.1f}% (Δ{stats_after['memory_percent'] - stats_before['memory_percent']:+.1f}%)")
    print(f"   Available: {stats_after['memory_available'] / 1024**3:.1f} GB")
    
    # Анализ результатов
    print(f"\n🔍 АНАЛИЗ РЕЗУЛЬТАТОВ:")
    cpu_delta = stats_after['cpu_percent'] - stats_before['cpu_percent']
    memory_delta = stats_after['memory_percent'] - stats_before['memory_percent']
    
    if cpu_delta > 10:
        print(f"   ⚠️  Высокая нагрузка на CPU: +{cpu_delta:.1f}%")
    elif cpu_delta > 5:
        print(f"   ⚡ Умеренная нагрузка на CPU: +{cpu_delta:.1f}%")
    else:
        print(f"   ✅ Низкая нагрузка на CPU: +{cpu_delta:.1f}%")
    
    if memory_delta > 5:
        print(f"   ⚠️  Высокое потребление памяти: +{memory_delta:.1f}%")
    elif memory_delta > 2:
        print(f"   ⚡ Умеренное потребление памяти: +{memory_delta:.1f}%")
    else:
        print(f"   ✅ Низкое потребление памяти: +{memory_delta:.1f}%")
    
    # Сохраняем отчет
    report = {
        'timestamp': datetime.now().isoformat(),
        'batch_size': batch_size,
        'activated_functions': activated,
        'stats_before': stats_before,
        'stats_after': stats_after,
        'cpu_delta': cpu_delta,
        'memory_delta': memory_delta
    }
    
    with open('data/sfm/repair_reports/activation_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=4)
    
    print(f"\n💾 Отчет сохранен: data/sfm/repair_reports/activation_report.json")
    
    return activated, stats_before, stats_after

if __name__ == "__main__":
    test_activation(batch_size=10)
