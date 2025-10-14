#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт активации 10 функций с мониторингом "было-стало"
Активирует только 10 функций за один запуск
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

def get_sfm_performance(sfm_instance):
    """Тест производительности SFM"""
    try:
        start_time = time.time()
        for i in range(10):
            _ = list(sfm_instance.functions.keys())
            critical_functions = []
            for func_id, func_obj in sfm_instance.functions.items():
                if getattr(func_obj, 'is_critical', False):
                    critical_functions.append(func_id)
        end_time = time.time()
        
        avg_response = (end_time - start_time) / 10
        operations_per_sec = 10 / (end_time - start_time)
        
        return {
            'avg_response_ms': avg_response * 1000,
            'operations_per_sec': operations_per_sec
        }
    except Exception as e:
        return None

def get_function_stats(sfm_instance):
    """Получение статистики функций"""
    total_functions = len(sfm_instance.functions)
    active_count = 0
    sleeping_count = 0
    critical_count = 0
    critical_sleeping_count = 0

    for func_id, func_obj in sfm_instance.functions.items():
        status_str = str(getattr(func_obj, 'status', 'UNKNOWN')).upper()
        is_critical = getattr(func_obj, 'is_critical', False)

        if 'ACTIVE' in status_str or 'ENABLED' in status_str:
            active_count += 1
        elif 'SLEEPING' in status_str or 'DISABLED' in status_str:
            sleeping_count += 1

        if is_critical:
            critical_count += 1
            if 'SLEEPING' in status_str or 'DISABLED' in status_str:
                critical_sleeping_count += 1

    return {
        'total_functions': total_functions,
        'active_count': active_count,
        'sleeping_count': sleeping_count,
        'critical_count': critical_count,
        'critical_sleeping_count': critical_sleeping_count
    }

def get_sleeping_functions(sfm_instance, limit=10):
    """Получение первых N спящих функций"""
    sleeping_functions = []
    
    for func_id, func_obj in sfm_instance.functions.items():
        status_str = str(getattr(func_obj, 'status', 'UNKNOWN')).upper()
        if 'SLEEPING' in status_str or 'DISABLED' in status_str:
            sleeping_functions.append(func_id)
            if len(sleeping_functions) >= limit:
                break
    
    return sleeping_functions

def print_comparison(before_stats, after_stats, before_sys, after_sys, before_perf, after_perf, activated_count):
    """Вывод сравнения до и после активации"""
    print("=" * 80)
    print(f"📦 АКТИВАЦИЯ 10 ФУНКЦИЙ: Активировано {activated_count} функций")
    print("=" * 80)
    
    # Сравнение системных ресурсов
    print("💻 СИСТЕМНЫЕ РЕСУРСЫ:")
    print(f"   CPU: {before_sys['cpu_percent']:.1f}% → {after_sys['cpu_percent']:.1f}% ({after_sys['cpu_percent']-before_sys['cpu_percent']:+.1f}%)")
    print(f"   RAM: {before_sys['ram_percent']:.1f}% → {after_sys['ram_percent']:.1f}% ({after_sys['ram_percent']-before_sys['ram_percent']:+.1f}%)")
    print(f"   RAM: {before_sys['ram_used_gb']:.2f}GB → {after_sys['ram_used_gb']:.2f}GB ({after_sys['ram_used_gb']-before_sys['ram_used_gb']:+.2f}GB)")
    
    # Сравнение производительности SFM
    if before_perf and after_perf:
        print(f"\n⚡ ПРОИЗВОДИТЕЛЬНОСТЬ SFM:")
        print(f"   Отклик: {before_perf['avg_response_ms']:.2f} мс → {after_perf['avg_response_ms']:.2f} мс ({after_perf['avg_response_ms']-before_perf['avg_response_ms']:+.2f} мс)")
        print(f"   Операций/сек: {before_perf['operations_per_sec']:.0f} → {after_perf['operations_per_sec']:.0f} ({after_perf['operations_per_sec']-before_perf['operations_per_sec']:+.0f})")
        
        # Оценка производительности
        if after_perf['avg_response_ms'] < 1.0:
            print("   ✅ Отлично!")
        elif after_perf['avg_response_ms'] < 5.0:
            print("   ✅ Хорошо")
        else:
            print("   ⚠️  Требует оптимизации")
    else:
        print("\n❌ Ошибка получения производительности SFM")
    
    # Сравнение статистики функций
    print(f"\n📦 СТАТИСТИКА ФУНКЦИЙ:")
    print(f"   Всего функций: {before_stats['total_functions']} → {after_stats['total_functions']} (без изменений)")
    print(f"   Активных: {before_stats['active_count']} → {after_stats['active_count']} (+{after_stats['active_count']-before_stats['active_count']})")
    print(f"   Спящих: {before_stats['sleeping_count']} → {after_stats['sleeping_count']} ({after_stats['sleeping_count']-before_stats['sleeping_count']:+d})")
    print(f"   Критических спящих: {before_stats['critical_sleeping_count']} → {after_stats['critical_sleeping_count']} ({after_stats['critical_sleeping_count']-before_stats['critical_sleeping_count']:+d})")
    
    # Прогресс активации
    total_sleeping_before = before_stats['sleeping_count']
    total_sleeping_after = after_stats['sleeping_count']
    activated_total = total_sleeping_before - total_sleeping_after
    progress_percent = (activated_total / total_sleeping_before * 100) if total_sleeping_before > 0 else 0
    
    print(f"\n📈 ПРОГРЕСС АКТИВАЦИИ:")
    print(f"   Активировано в этом запуске: {activated_count}")
    print(f"   Активировано всего: {activated_total}")
    print(f"   Прогресс: {progress_percent:.1f}% ({activated_total}/{total_sleeping_before})")
    print(f"   Осталось спящих: {total_sleeping_after}")
    
    print("=" * 80)

def main():
    print("🚀 АКТИВАЦИЯ 10 ФУНКЦИЙ С МОНИТОРИНГОМ 'БЫЛО-СТАЛО'")
    print()
    
    config = {
        'thread_pool_enabled': True,
        'max_thread_pool_workers': 5,
        'async_io_enabled': True,
        'redis_cache_enabled': True,
        'enable_auto_management': False,
        'enable_sleep_mode': False
    }
    
    sfm = SafeFunctionManager('ActivationMonitorSFM', config)
    print(f"✅ SFM инициализирован: {len(sfm.functions)} функций")
    
    # Получаем список первых 10 спящих функций
    sleeping_functions = get_sleeping_functions(sfm, 10)
    print(f"📦 Найдено спящих функций для активации: {len(sleeping_functions)}")
    
    if not sleeping_functions:
        print("✅ Все функции уже активны!")
        return
    
    # Получаем статистику ДО активации
    before_stats = get_function_stats(sfm)
    before_sys = get_system_stats()
    before_perf = get_sfm_performance(sfm)
    
    print(f"\n🚀 АКТИВАЦИЯ {len(sleeping_functions)} ФУНКЦИЙ...")
    
    activated_count = 0
    start_time = time.time()
    
    for func_id in sleeping_functions:
        try:
            if func_id in sfm.functions:
                func_obj = sfm.functions[func_id]
                current_status = str(getattr(func_obj, 'status', 'UNKNOWN')).upper()
                
                if 'SLEEPING' in current_status or 'DISABLED' in current_status:
                    # Попытка активации
                    sfm.wake_function(func_id)
                    
                    # Проверяем результат
                    new_status = str(getattr(func_obj, 'status', 'UNKNOWN')).upper()
                    if 'ACTIVE' in new_status or 'ENABLED' in new_status:
                        activated_count += 1
                        print(f"   ✅ {func_id}: {current_status} → {new_status}")
                    else:
                        print(f"   ❌ {func_id}: остался {new_status}")
                else:
                    print(f"   ℹ️  {func_id}: уже {current_status}")
            else:
                print(f"   ❌ {func_id}: не найдена в SFM")
        except Exception as e:
            print(f"   ❌ {func_id}: ошибка активации - {e}")
    
    end_time = time.time()
    activation_time = end_time - start_time
    
    print(f"   ✅ Активировано: {activated_count}")
    print(f"   ⏱️  Время активации: {activation_time:.3f} сек")
    
    # Получаем статистику ПОСЛЕ активации
    after_stats = get_function_stats(sfm)
    after_sys = get_system_stats()
    after_perf = get_sfm_performance(sfm)
    
    # Показываем сравнение до/после
    print_comparison(
        before_stats, after_stats,
        before_sys, after_sys,
        before_perf, after_perf,
        activated_count
    )
    
    print(f"\n🎉 ЗАВЕРШЕНО!")
    print(f"📊 Активировано: {activated_count} из {len(sleeping_functions)} функций")
    
    if after_stats['sleeping_count'] == 0:
        print("✅ Все функции активированы!")
    else:
        print(f"⚠️  Осталось {after_stats['sleeping_count']} функций в спящем режиме")
        print(f"💡 Запустите скрипт еще раз для активации следующих 10 функций")

if __name__ == "__main__":
    main()