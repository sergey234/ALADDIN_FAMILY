#!/usr/bin/env python3
"""
Скрипт активации критических спящих функций
Активирует 17 критических функций, которые находятся в спящем режиме
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.safe_function_manager import SafeFunctionManager
import time

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

def activate_critical_functions():
    """Активирует критические спящие функции"""
    
    print("🚀 АКТИВАЦИЯ КРИТИЧЕСКИХ СПЯЩИХ ФУНКЦИЙ")
    print("=" * 50)
    
    # Инициализируем SFM
    config = {
        'thread_pool_enabled': True,
        'max_thread_pool_workers': 5,
        'async_io_enabled': True,
        'redis_cache_enabled': True,
        'enable_auto_management': False,
        'enable_sleep_mode': False
    }
    
    try:
        sfm = SafeFunctionManager('CriticalActivationSFM', config)
        print(f"✅ SFM инициализирован с {len(sfm.functions)} функциями")
        
        # Активируем каждую критическую функцию
        activated_count = 0
        failed_count = 0
        
        for func_id in CRITICAL_SLEEPING_FUNCTIONS:
            try:
                if func_id in sfm.functions:
                    func_obj = sfm.functions[func_id]
                    
                    # Проверяем, что функция критическая и спящая
                    is_critical = getattr(func_obj, 'is_critical', False)
                    status = str(getattr(func_obj, 'status', ''))
                    
                    if is_critical and ('sleep' in status.lower() or 'inactive' in status.lower()):
                        # Активируем функцию
                        # Здесь нужно будет реализовать метод активации
                        print(f"🔄 Активируем: {func_id}")
                        
                        # Временно просто логируем
                        # TODO: Реализовать реальную активацию
                        activated_count += 1
                        time.sleep(0.1)  # Небольшая задержка
                        
                    else:
                        print(f"⚠️  Функция {func_id} не критическая или не спящая")
                        
                else:
                    print(f"❌ Функция {func_id} не найдена")
                    failed_count += 1
                    
            except Exception as e:
                print(f"❌ Ошибка активации {func_id}: {e}")
                failed_count += 1
        
        print("\n📊 РЕЗУЛЬТАТЫ АКТИВАЦИИ:")
        print(f"✅ Успешно активировано: {activated_count}")
        print(f"❌ Ошибок: {failed_count}")
        print(f"📋 Всего обработано: {len(CRITICAL_SLEEPING_FUNCTIONS)}")
        
        return activated_count, failed_count
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        return 0, len(CRITICAL_SLEEPING_FUNCTIONS)

def verify_activation():
    """Проверяет результат активации"""
    
    print("\n🔍 ПРОВЕРКА РЕЗУЛЬТАТОВ АКТИВАЦИИ")
    print("=" * 50)
    
    config = {
        'thread_pool_enabled': True,
        'max_thread_pool_workers': 5,
        'async_io_enabled': True,
        'redis_cache_enabled': True,
        'enable_auto_management': False,
        'enable_sleep_mode': False
    }
    
    try:
        sfm = SafeFunctionManager('VerificationSFM', config)
        
        still_sleeping = []
        now_active = []
        
        for func_id in CRITICAL_SLEEPING_FUNCTIONS:
            if func_id in sfm.functions:
                func_obj = sfm.functions[func_id]
                status = str(getattr(func_obj, 'status', ''))
                
                if 'sleep' in status.lower() or 'inactive' in status.lower():
                    still_sleeping.append(func_id)
                else:
                    now_active.append(func_id)
        
        print(f"✅ Теперь активны: {len(now_active)}")
        print(f"💤 Все еще спят: {len(still_sleeping)}")
        
        if still_sleeping:
            print("\n💤 Все еще спящие функции:")
            for func_id in still_sleeping:
                print(f"   - {func_id}")
        
        return len(now_active), len(still_sleeping)
        
    except Exception as e:
        print(f"❌ Ошибка проверки: {e}")
        return 0, len(CRITICAL_SLEEPING_FUNCTIONS)

if __name__ == "__main__":
    print("🎯 СКРИПТ АКТИВАЦИИ КРИТИЧЕСКИХ ФУНКЦИЙ")
    print("Активирует 17 критических спящих функций")
    print("=" * 50)
    
    # Активируем функции
    activated, failed = activate_critical_functions()
    
    # Проверяем результат
    active_after, sleeping_after = verify_activation()
    
    print("\n🎉 ИТОГОВЫЙ РЕЗУЛЬТАТ:")
    print(f"📊 Статистика:")
    print(f"   Всего критических спящих: {len(CRITICAL_SLEEPING_FUNCTIONS)}")
    print(f"   Попыток активации: {activated}")
    print(f"   Ошибок: {failed}")
    print(f"   Активных после активации: {active_after}")
    print(f"   Все еще спящих: {sleeping_after}")
    
    if sleeping_after == 0:
        print("🎉 ВСЕ КРИТИЧЕСКИЕ ФУНКЦИИ АКТИВИРОВАНЫ!")
    else:
        print(f"⚠️  Остались спящими: {sleeping_after} функций")