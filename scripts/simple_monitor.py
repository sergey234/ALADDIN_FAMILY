#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой мониторинг системы
Показывает CPU, RAM и SFM производительность
"""

import sys
import os
import time
import psutil
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

def get_sfm_performance():
    """Тест производительности SFM"""
    try:
        from security.safe_function_manager import SafeFunctionManager
        
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
            'total_functions': len(sfm.functions)
        }
    except Exception as e:
        return None

def print_status():
    """Вывод статуса системы"""
    print("=" * 60)
    
    # Системные ресурсы
    sys_stats = get_system_stats()
    print(f"💻 CPU: {sys_stats['cpu_percent']:.1f}%")
    print(f"💾 RAM: {sys_stats['ram_percent']:.1f}% ({sys_stats['ram_used_gb']:.2f}GB / {sys_stats['ram_total_gb']:.2f}GB)")
    print(f"📊 Доступно RAM: {sys_stats['ram_available_gb']:.2f}GB")
    
    # Производительность SFM
    sfm_perf = get_sfm_performance()
    if sfm_perf:
        print(f"⚡ SFM отклик: {sfm_perf['avg_response_ms']:.2f} мс")
        print(f"🚀 Операций/сек: {sfm_perf['operations_per_sec']:.0f}")
        print(f"📦 Всего функций: {sfm_perf['total_functions']}")
        
        # Оценка производительности
        if sfm_perf['avg_response_ms'] < 1.0:
            print("✅ Отлично!")
        elif sfm_perf['avg_response_ms'] < 5.0:
            print("✅ Хорошо")
        else:
            print("⚠️  Требует оптимизации")
    else:
        print("❌ Ошибка получения производительности SFM")
    
    print("=" * 60)

def main():
    print("🖥️  ПРОСТОЙ МОНИТОРИНГ СИСТЕМЫ ALADDIN")
    print()
    
    try:
        while True:
            print_status()
            print()
            print("Нажмите Enter для обновления или Ctrl+C для выхода...")
            input()
            print()
            
    except KeyboardInterrupt:
        print("\n👋 Выход из мониторинга")

if __name__ == "__main__":
    main()