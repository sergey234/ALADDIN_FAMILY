#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт активации ВСЕХ спящих функций с мониторингом "было-стало"
Активирует функции пакетами по 10 и показывает статистику до и после каждого пакета
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

def print_comparison(before_stats, after_stats, before_sys, after_sys, before_perf, after_perf, batch_num, activated_count):
    """Вывод сравнения до и после активации"""
    print("=" * 80)
    print(f"📦 ПАКЕТ {batch_num}: Активировано {activated_count} функций")
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
    print(f"   Активировано в пакете: {activated_count}")
    print(f"   Активировано всего: {activated_total}")
    print(f"   Прогресс: {progress_percent:.1f}% ({activated_total}/{total_sleeping_before})")
    print(f"   Осталось спящих: {total_sleeping_after}")
    
    print("=" * 80)

def get_sleeping_functions(sfm_instance):
    """Получение списка всех спящих функций"""
    sleeping_functions = []
    
    for func_id, func_obj in sfm_instance.functions.items():
        status_str = str(getattr(func_obj, 'status', 'UNKNOWN')).upper()
        if 'SLEEPING' in status_str or 'DISABLED' in status_str:
            sleeping_functions.append(func_id)
    
    return sleeping_functions

def activate_functions_batch(sfm_instance, function_list, batch_size=10):
    """Активация функций пакетами с мониторингом до/после"""
    total_activated = 0
    
    for i in range(0, len(function_list), batch_size):
        batch = function_list[i:i+batch_size]
        batch_num = (i // batch_size) + 1
        
        print(f"\n🚀 АКТИВАЦИЯ ПАКЕТА {batch_num}")
        print(f"   Функций в пакете: {len(batch)}")
        
        # Получаем статистику ДО активации
        before_stats = get_function_stats(sfm_instance)
        before_sys = get_system_stats()
        before_perf = get_sfm_performance(sfm_instance)
        
        activated_in_batch = 0
        start_time = time.time()
        
        for func_id in batch:
            try:
                if func_id in sfm_instance.functions:
                    func_obj = sfm_instance.functions[func_id]
                    current_status = str(getattr(func_obj, 'status', 'UNKNOWN')).upper()
                    
                    if 'SLEEPING' in current_status or 'DISABLED' in current_status:
                        # Попытка активации
                        sfm_instance.wake_function(func_id)
                        
                        # Проверяем результат
                        new_status = str(getattr(func_obj, 'status', 'UNKNOWN')).upper()
                        if 'ACTIVE' in new_status or 'ENABLED' in new_status:
                            activated_in_batch += 1
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
        
        print(f"   ✅ Активировано: {activated_in_batch}")
        print(f"   ⏱️  Время активации: {activation_time:.3f} сек")
        
        total_activated += activated_in_batch
        
        # Получаем статистику ПОСЛЕ активации
        after_stats = get_function_stats(sfm_instance)
        after_sys = get_system_stats()
        after_perf = get_sfm_performance(sfm_instance)
        
        # Показываем сравнение до/после
        print_comparison(
            before_stats, after_stats,
            before_sys, after_sys,
            before_perf, after_perf,
            batch_num, total_activated
        )
        
        # Пауза между пакетами
        if i + batch_size < len(function_list):
            print(f"\n⏸️  Пауза 3 секунды перед следующим пакетом...")
            time.sleep(3)
    
    return total_activated

def main():
    print("🚀 ЗАПУСК АКТИВАЦИИ ВСЕХ СПЯЩИХ ФУНКЦИЙ С МОНИТОРИНГОМ 'БЫЛО-СТАЛО'")
    print()
    
    config = {
        'thread_pool_enabled': True,
        'max_thread_pool_workers': 5,
        'async_io_enabled': True,
        'redis_cache_enabled': True,
        'enable_auto_management': False,
        'enable_sleep_mode': False
    }
    
    sfm = SafeFunctionManager('FullActivationMonitorSFM', config)
    print(f"✅ SFM инициализирован: {len(sfm.functions)} функций")
    
    # Получаем список всех спящих функций
    sleeping_functions = get_sleeping_functions(sfm)
    print(f"📦 Найдено спящих функций: {len(sleeping_functions)}")
    
    if not sleeping_functions:
        print("✅ Все функции уже активны!")
        return
    
    # Показываем начальную статистику
    initial_stats = get_function_stats(sfm)
    initial_sys = get_system_stats()
    initial_perf = get_sfm_performance(sfm)
    
    print("\n" + "=" * 80)
    print("📊 НАЧАЛЬНАЯ СТАТИСТИКА")
    print("=" * 80)
    print(f"💻 CPU: {initial_sys['cpu_percent']:.1f}%")
    print(f"💾 RAM: {initial_sys['ram_percent']:.1f}% ({initial_sys['ram_used_gb']:.2f}GB / {initial_sys['ram_total_gb']:.2f}GB)")
    if initial_perf:
        print(f"⚡ SFM отклик: {initial_perf['avg_response_ms']:.2f} мс")
        print(f"🚀 Операций/сек: {initial_perf['operations_per_sec']:.0f}")
    print(f"📦 Всего функций: {initial_stats['total_functions']}")
    print(f"💤 Спящих функций: {initial_stats['sleeping_count']}")
    print(f"🚨 Критических спящих: {initial_stats['critical_sleeping_count']}")
    print("=" * 80)
    
    # Активируем функции пакетами по 10
    print(f"\n🎯 АКТИВАЦИЯ {len(sleeping_functions)} СПЯЩИХ ФУНКЦИЙ ПО 10 ШТУК...")
    
    try:
        total_activated = activate_functions_batch(sfm, sleeping_functions, 10)
        
        print(f"\n🎉 ЗАВЕРШЕНО!")
        print(f"📊 Итого активировано: {total_activated} из {len(sleeping_functions)} спящих функций")
        
        # Финальная статистика
        final_stats = get_function_stats(sfm)
        final_sys = get_system_stats()
        final_perf = get_sfm_performance(sfm)
        
        print(f"\n📈 ФИНАЛЬНАЯ СТАТИСТИКА:")
        print(f"   🚨 Критических спящих: {final_stats['critical_sleeping_count']}")
        print(f"   💤 Всего спящих: {final_stats['sleeping_count']}")
        print(f"   ✅ Активировано всего: {total_activated}")
        
        if final_stats['sleeping_count'] == 0:
            print("✅ Все функции активированы!")
        else:
            print(f"⚠️  Осталось {final_stats['sleeping_count']} функций в спящем режиме")
            
    except KeyboardInterrupt:
        print(f"\n⏹️  Активация прервана пользователем")
        final_stats = get_function_stats(sfm)
        print(f"📊 Активировано до прерывания: {len(sleeping_functions) - final_stats['sleeping_count']} функций")

if __name__ == "__main__":
    main()