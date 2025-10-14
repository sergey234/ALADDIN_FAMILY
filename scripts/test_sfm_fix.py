#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест исправления SFM - Фаза 1
Проверяем что SFM больше не зависает при регистрации функций
"""

import sys
import os
import time
from datetime import datetime

# Добавляем путь к проекту
sys.path.insert(0, '/Users/sergejhlystov/ALADDIN_NEW')

def test_sfm_fix():
    """Тест исправления SFM"""
    print("🔧 ТЕСТ ИСПРАВЛЕНИЯ SFM - ФАЗА 1")
    print("=" * 50)
    print(f"Время теста: {datetime.now()}")
    print()
    
    try:
        # Импортируем SFM
        from security.safe_function_manager import SafeFunctionManager, SecurityFunction, FunctionStatus
        from core.base import SecurityLevel
        
        print("✅ SafeFunctionManager импортирован успешно")
        
        # Создаем SFM с отключенными фоновыми процессами
        print("🔧 Создание SFM с отключенными фоновыми процессами...")
        sfm = SafeFunctionManager("TestSFM")
        
        print("✅ SFM создан успешно")
        print(f"   • enable_auto_management: {sfm.enable_auto_management}")
        print(f"   • enable_sleep_mode: {sfm.enable_sleep_mode}")
        print(f"   • auto_sleep_enabled: {sfm.auto_sleep_enabled}")
        print(f"   • optimization_enabled: {sfm.optimization_enabled}")
        print(f"   • monitoring_integration_enabled: {sfm.monitoring_integration_enabled}")
        
        # Тест регистрации функции
        print("\n🔧 Тест регистрации функции...")
        start_time = time.time()
        
        success = sfm.register_function(
            function_id="test_function",
            name="Test Function",
            description="Тестовая функция для проверки исправления",
            function_type="test",
            security_level=SecurityLevel.MEDIUM,
            is_critical=False,
            auto_enable=True
        )
        
        end_time = time.time()
        registration_time = end_time - start_time
        
        if success:
            print(f"✅ Функция зарегистрирована успешно за {registration_time:.2f} секунд")
        else:
            print(f"❌ Ошибка регистрации функции за {registration_time:.2f} секунд")
            return False
            
        # Проверяем статус функции
        print("\n🔧 Проверка статуса функции...")
        function_status = sfm.get_function_status("test_function")
        print(f"   • Статус функции: {function_status}")
        
        # Проверяем все функции
        print("\n🔧 Проверка всех функций...")
        all_functions = sfm.get_all_functions_status()
        print(f"   • Всего функций: {len(all_functions)}")
        
        # Проверяем тип возвращаемого значения
        if isinstance(all_functions, dict):
            for func_id, func_data in all_functions.items():
                print(f"   • {func_id}: {func_data.get('status', 'unknown')}")
        elif isinstance(all_functions, list):
            for func_data in all_functions:
                func_id = func_data.get('function_id', 'unknown')
                status = func_data.get('status', 'unknown')
                print(f"   • {func_id}: {status}")
        else:
            print(f"   • Неожиданный тип: {type(all_functions)}")
        
        # Тест сбора метрик (должен быть быстрым)
        print("\n🔧 Тест сбора метрик...")
        start_time = time.time()
        
        try:
            metrics = sfm._collect_performance_metrics()
            end_time = time.time()
            metrics_time = end_time - start_time
            
            print(f"✅ Метрики собраны за {metrics_time:.2f} секунд")
            print(f"   • CPU: {metrics.get('cpu_usage', 'N/A')}%")
            print(f"   • Memory: {metrics.get('memory_usage', 'N/A')}%")
            print(f"   • Total functions: {metrics.get('total_functions', 'N/A')}")
            
        except Exception as e:
            print(f"❌ Ошибка сбора метрик: {e}")
            return False
        
        print("\n🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("✅ SFM исправлен и работает без зависаний")
        return True
        
    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_sfm_fix()
    if success:
        print("\n🚀 ФАЗА 1 ЗАВЕРШЕНА УСПЕШНО!")
        sys.exit(0)
    else:
        print("\n💥 ФАЗА 1 ПРОВАЛЕНА!")
        sys.exit(1)