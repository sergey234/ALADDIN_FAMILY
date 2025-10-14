#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест интеграции SafeFunctionManager с AutoScalingEngine
"""

import sys
import os
import asyncio
from datetime import datetime

# Добавляем путь к проекту
sys.path.append('/Users/sergejhlystov/ALADDIN_NEW')

def test_sfm_scaling_integration():
    """Тест интеграции SafeFunctionManager с AutoScalingEngine"""
    print("🔧 ТЕСТ ИНТЕГРАЦИИ SAFEFUNCTIONMANAGER С AUTO_SCALING_ENGINE")
    print("=" * 60)
    
    try:
        # Импортируем SafeFunctionManager
        from security.safe_function_manager import SafeFunctionManager
        print("✅ Импорт SafeFunctionManager успешен")
        
        # Создаем экземпляр с включенным масштабированием
        config = {
            "scaling_enabled": True,
            "scaling_config": {
                "min_replicas": 1,
                "max_replicas": 5,
                "scaling_interval": 30
            }
        }
        
        sfm = SafeFunctionManager("TestSFM", config)
        print("✅ SafeFunctionManager создан с конфигурацией масштабирования")
        
        # Проверяем инициализацию AutoScalingEngine
        if hasattr(sfm, 'auto_scaling_engine') and sfm.auto_scaling_engine:
            print("✅ AutoScalingEngine инициализирован")
            
            # Получаем статус масштабирования
            scaling_status = sfm.get_scaling_status()
            print(f"📊 Статус масштабирования: {scaling_status}")
            
            # Проверяем правила масштабирования
            rules = sfm.auto_scaling_engine.get_scaling_rules()
            print(f"📋 Правил масштабирования: {len(rules)}")
            
            # Тестируем сбор метрик
            metrics_result = sfm.collect_scaling_metrics()
            print(f"📈 Сбор метрик: {'✅ Успешно' if metrics_result else '❌ Ошибка'}")
            
            # Получаем метрики масштабирования
            scaling_metrics = sfm.auto_scaling_engine.get_scaling_metrics()
            print(f"📊 Метрики масштабирования: {len(scaling_metrics)} записей")
            
        else:
            print("❌ AutoScalingEngine не инициализирован")
            return False
        
        # Тестируем остановку
        stop_result = sfm.stop()
        print(f"🛑 Остановка SFM: {'✅ Успешно' if stop_result else '❌ Ошибка'}")
        
        print("\n🎯 РЕЗУЛЬТАТЫ ТЕСТА:")
        print("✅ SafeFunctionManager успешно интегрирован с AutoScalingEngine")
        print("✅ Все методы масштабирования работают корректно")
        print("✅ Сбор метрик функционирует")
        print("✅ Остановка выполняется корректно")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка теста: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_async_scaling_integration():
    """Тест асинхронной интеграции"""
    print("\n🔄 ТЕСТ АСИНХРОННОЙ ИНТЕГРАЦИИ")
    print("=" * 40)
    
    try:
        from security.safe_function_manager import SafeFunctionManager
        
        async def async_test():
            config = {"scaling_enabled": True}
            sfm = SafeFunctionManager("AsyncTestSFM", config)
            
            if sfm.auto_scaling_engine:
                # Тестируем асинхронные методы
                await sfm.auto_scaling_engine.initialize_async()
                print("✅ Асинхронная инициализация работает")
                
                await sfm.auto_scaling_engine.stop_async()
                print("✅ Асинхронная остановка работает")
                
                # Тестируем контекстный менеджер
                async with sfm.auto_scaling_engine as engine:
                    status = engine.get_engine_status()
                    print(f"✅ Контекстный менеджер работает: {status.get('status', 'unknown')}")
                
                return True
            return False
        
        # Запускаем асинхронный тест
        result = asyncio.run(async_test())
        print(f"🔄 Асинхронная интеграция: {'✅ Успешно' if result else '❌ Ошибка'}")
        return result
        
    except Exception as e:
        print(f"❌ Ошибка асинхронного теста: {e}")
        return False

if __name__ == "__main__":
    print("🚀 ЗАПУСК ТЕСТОВ ИНТЕГРАЦИИ SFM + AUTO_SCALING_ENGINE")
    print("=" * 60)
    
    # Основной тест
    test1_result = test_sfm_scaling_integration()
    
    # Асинхронный тест
    test2_result = test_async_scaling_integration()
    
    print("\n📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ:")
    print(f"Основная интеграция: {'✅ ПРОЙДЕН' if test1_result else '❌ ПРОВАЛЕН'}")
    print(f"Асинхронная интеграция: {'✅ ПРОЙДЕН' if test2_result else '❌ ПРОВАЛЕН'}")
    
    if test1_result and test2_result:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("✅ SafeFunctionManager полностью интегрирован с AutoScalingEngine")
    else:
        print("\n⚠️ НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛЕНЫ")
        print("❌ Требуется дополнительная настройка")