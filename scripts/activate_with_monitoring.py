#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт активации функций с мониторингом статистики
Активирует функции пакетами по 10 и показывает статистику после каждого пакета
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

        if 'ACTIVE' in status_str:
            active_count += 1
        elif 'SLEEPING' in status_str:
            sleeping_count += 1

        if is_critical:
            critical_count += 1
            if 'SLEEPING' in status_str:
                critical_sleeping_count += 1

    return {
        'total_functions': total_functions,
        'active_count': active_count,
        'sleeping_count': sleeping_count,
        'critical_count': critical_count,
        'critical_sleeping_count': critical_sleeping_count
    }

def print_status(sfm_instance, batch_num, activated_count):
    """Вывод статуса системы"""
    print("=" * 60)
    print(f"📦 ПАКЕТ {batch_num}: Активировано {activated_count} функций")
    print("=" * 60)
    
    # Системные ресурсы
    sys_stats = get_system_stats()
    print(f"💻 CPU: {sys_stats['cpu_percent']:.1f}%")
    print(f"💾 RAM: {sys_stats['ram_percent']:.1f}% ({sys_stats['ram_used_gb']:.2f}GB / {sys_stats['ram_total_gb']:.2f}GB)")
    print(f"📊 Доступно RAM: {sys_stats['ram_available_gb']:.2f}GB")
    
    # Производительность SFM
    sfm_perf = get_sfm_performance(sfm_instance)
    if sfm_perf:
        print(f"⚡ SFM отклик: {sfm_perf['avg_response_ms']:.2f} мс")
        print(f"🚀 Операций/сек: {sfm_perf['operations_per_sec']:.0f}")
        
        # Оценка производительности
        if sfm_perf['avg_response_ms'] < 1.0:
            print("✅ Отлично!")
        elif sfm_perf['avg_response_ms'] < 5.0:
            print("✅ Хорошо")
        else:
            print("⚠️  Требует оптимизации")
    else:
        print("❌ Ошибка получения производительности SFM")
    
    # Статистика функций
    func_stats = get_function_stats(sfm_instance)
    print(f"📦 Всего функций: {func_stats['total_functions']}")
    print(f"💤 Спящих функций: {func_stats['sleeping_count']}")
    print(f"🚨 Критических спящих: {func_stats['critical_sleeping_count']}")
    
    print("=" * 60)

def activate_functions_batch(sfm_instance, function_list, batch_size=10):
    """Активация функций пакетами"""
    total_activated = 0
    
    for i in range(0, len(function_list), batch_size):
        batch = function_list[i:i+batch_size]
        batch_num = (i // batch_size) + 1
        
        print(f"\n🚀 АКТИВАЦИЯ ПАКЕТА {batch_num}")
        print(f"   Функций в пакете: {len(batch)}")
        
        activated_in_batch = 0
        start_time = time.time()
        
        for func_id in batch:
            try:
                if func_id in sfm_instance.functions:
                    func_obj = sfm_instance.functions[func_id]
                    current_status = str(getattr(func_obj, 'status', 'UNKNOWN')).upper()
                    
                    if 'SLEEPING' in current_status:
                        # Попытка активации (используем wake_function вместо activate_function)
                        sfm_instance.wake_function(func_id)
                        
                        # Проверяем результат
                        new_status = str(getattr(func_obj, 'status', 'UNKNOWN')).upper()
                        if 'ACTIVE' in new_status:
                            activated_in_batch += 1
                            print(f"   ✅ {func_id}: SLEEPING → ACTIVE")
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
        
        # Показываем статистику после каждого пакета
        print_status(sfm_instance, batch_num, total_activated)
        
        # Пауза между пакетами
        if i + batch_size < len(function_list):
            print(f"\n⏸️  Пауза 2 секунды перед следующим пакетом...")
            time.sleep(2)
    
    return total_activated

def main():
    print("🚀 ЗАПУСК АКТИВАЦИИ ФУНКЦИЙ С МОНИТОРИНГОМ")
    print()
    
    # Список 17 критических спящих функций
    CRITICAL_SLEEPING_FUNCTIONS = [
        'security_recoveryreport',
        'security_mobileinterface',
        'bot_website',
        'security_healthcheckinterface',
        'security_metricscollectorinterface',
        'security_interfacerequest',
        'security_loadbalancingalgorithminterface',
        'security_interfaceeventrecord',
        'security_interfaceconfig',
        'security_voiceinterface',
        'security_forensicsreport',
        'security_threatreport',
        'security_authenticationinterface',
        'security_webinterface',
        'security_interfaceresponse',
        'security_userinterfacemanager',
        'security_interfacerecord'
    ]
    
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
    
    # Показываем начальную статистику
    print_status(sfm, "НАЧАЛЬНАЯ", 0)
    
    # Активируем критические функции пакетами по 10
    print(f"\n🎯 АКТИВАЦИЯ {len(CRITICAL_SLEEPING_FUNCTIONS)} КРИТИЧЕСКИХ ФУНКЦИЙ...")
    
    try:
        total_activated = activate_functions_batch(sfm, CRITICAL_SLEEPING_FUNCTIONS, 10)
        
        print(f"\n🎉 ЗАВЕРШЕНО!")
        print(f"📊 Итого активировано: {total_activated} из {len(CRITICAL_SLEEPING_FUNCTIONS)} критических функций")
        
        # Финальная статистика
        func_stats = get_function_stats(sfm)
        print(f"\n📈 ФИНАЛЬНАЯ СТАТИСТИКА:")
        print(f"   🚨 Критических спящих: {func_stats['critical_sleeping_count']}")
        print(f"   💤 Всего спящих: {func_stats['sleeping_count']}")
        
        if func_stats['critical_sleeping_count'] == 0:
            print("✅ Все критические функции активированы!")
        else:
            print(f"⚠️  Осталось {func_stats['critical_sleeping_count']} критических функций в спящем режиме")
            
    except KeyboardInterrupt:
        print(f"\n⏹️  Активация прервана пользователем")
        func_stats = get_function_stats(sfm)
        print(f"📊 Активировано до прерывания: {func_stats['total_functions'] - func_stats['sleeping_count'] - func_stats['active_count']} функций")

if __name__ == "__main__":
    main()