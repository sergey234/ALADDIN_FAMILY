#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Быстрый мониторинг системы ALADDIN
Показывает CPU, RAM и статистику SFM
"""

import sys
import os
import time
import psutil
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.safe_function_manager import SafeFunctionManager

def get_system_stats():
    """Получение системных ресурсов"""
    cpu = psutil.cpu_percent(interval=0.1)
    ram = psutil.virtual_memory()
    
    return {
        'cpu_percent': cpu,
        'ram_percent': ram.percent,
        'ram_used_gb': ram.used / (1024**3),
        'ram_total_gb': ram.total / (1024**3),
        'ram_available_gb': ram.available / (1024**3)
    }

def get_sfm_stats():
    """Получение статистики SFM"""
    config = {
        'thread_pool_enabled': True,
        'max_thread_pool_workers': 5,
        'async_io_enabled': True,
        'redis_cache_enabled': True,
        'enable_auto_management': False,
        'enable_sleep_mode': False
    }
    
    sfm = SafeFunctionManager('MonitorSFM', config)
    
    total = len(sfm.functions)
    active = 0
    sleeping = 0
    critical = 0
    critical_sleeping = 0
    
    for func_id, func_obj in sfm.functions.items():
        if getattr(func_obj, 'is_critical', False):
            critical += 1
            status = str(getattr(func_obj, 'status', ''))
            if 'sleep' in status.lower():
                critical_sleeping += 1
        
        status = str(getattr(func_obj, 'status', ''))
        if 'active' in status.lower():
            active += 1
        elif 'sleep' in status.lower():
            sleeping += 1
    
    return {
        'total_functions': total,
        'active_functions': active,
        'sleeping_functions': sleeping,
        'critical_functions': critical,
        'critical_sleeping': critical_sleeping,
        'active_percentage': (active / total * 100) if total > 0 else 0
    }

def test_sfm_performance():
    """Тест производительности SFM"""
    config = {
        'thread_pool_enabled': True,
        'max_thread_pool_workers': 5,
        'async_io_enabled': True,
        'redis_cache_enabled': True,
        'enable_auto_management': False,
        'enable_sleep_mode': False
    }
    
    sfm = SafeFunctionManager('PerfSFM', config)
    
    start_time = time.time()
    for i in range(10):
        _ = list(sfm.functions.keys())
        critical_functions = []
        for func_id, func_obj in sfm.functions.items():
            if getattr(func_obj, 'is_critical', False):
                critical_functions.append(func_id)
    end_time = time.time()
    
    avg_response = (end_time - start_time) / 10
    operations_per_sec = 10 / (end_time - start_time)
    
    return {
        'avg_response_ms': avg_response * 1000,
        'operations_per_sec': operations_per_sec,
        'total_time': end_time - start_time
    }

def main():
    print("🖥️  БЫСТРЫЙ МОНИТОРИНГ СИСТЕМЫ ALADDIN")
    print("=" * 60)
    
    # Системные ресурсы
    sys_stats = get_system_stats()
    print("💻 СИСТЕМНЫЕ РЕСУРСЫ:")
    print(f"   🖥️  CPU: {sys_stats['cpu_percent']:.1f}%")
    print(f"   💾 RAM: {sys_stats['ram_percent']:.1f}% ({sys_stats['ram_used_gb']:.2f}GB / {sys_stats['ram_total_gb']:.2f}GB)")
    print(f"   📊 Доступно RAM: {sys_stats['ram_available_gb']:.2f}GB")
    print()
    
    # SFM статистика
    sfm_stats = get_sfm_stats()
    print("🔧 СТАТИСТИКА SFM:")
    print(f"   📦 Всего функций: {sfm_stats['total_functions']}")
    print(f"   ✅ Активных: {sfm_stats['active_functions']} ({sfm_stats['active_percentage']:.1f}%)")
    print(f"   💤 Спящих: {sfm_stats['sleeping_functions']}")
    print(f"   🚨 Критических: {sfm_stats['critical_functions']}")
    print(f"   ⚠️  Критических спящих: {sfm_stats['critical_sleeping']}")
    print()
    
    # Производительность SFM
    perf_stats = test_sfm_performance()
    print("⚡ ПРОИЗВОДИТЕЛЬНОСТЬ SFM:")
    print(f"   🏃 Средний отклик: {perf_stats['avg_response_ms']:.2f} мс")
    print(f"   🚀 Операций/сек: {perf_stats['operations_per_sec']:.1f}")
    print()
    
    # Критические проблемы
    print("🚨 КРИТИЧЕСКИЕ ПРОБЛЕМЫ:")
    if sfm_stats['critical_sleeping'] > 0:
        print(f"   ❌ {sfm_stats['critical_sleeping']} критических функций спят!")
    else:
        print("   ✅ Все критические функции активны")
    
    if sfm_stats['sleeping_functions'] > 0:
        print(f"   ⚠️  {sfm_stats['sleeping_functions']} функций в спящем режиме ({sfm_stats['sleeping_functions']/sfm_stats['total_functions']*100:.1f}%)")
    else:
        print("   ✅ Все функции активны")
    
    print()
    print("💡 РЕКОМЕНДАЦИИ:")
    if sfm_stats['critical_sleeping'] > 0:
        print("   1. Активировать критические спящие функции")
    if sfm_stats['sleeping_functions'] > sfm_stats['critical_sleeping']:
        print("   2. Активировать оставшиеся спящие функции")
    if sys_stats['cpu_percent'] > 80:
        print("   3. Высокая нагрузка CPU - оптимизировать систему")
    if sys_stats['ram_percent'] > 90:
        print("   4. Высокое использование RAM - освободить память")

if __name__ == "__main__":
    main()