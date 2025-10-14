#!/usr/bin/env python3
"""
Отладка загрузки SFM - простой тест
"""

import sys
import json
sys.path.append('.')

def test_sfm_loading():
    """Тестируем загрузку SFM пошагово"""
    
    print("🔍 ОТЛАДКА SFM - ПОШАГОВЫЙ АНАЛИЗ")
    print("=" * 50)
    
    # 1. Проверяем реестр
    print("\n1. 📄 ПРОВЕРЯЕМ РЕЕСТР")
    print("-" * 30)
    try:
        with open('data/sfm/function_registry.json', 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        functions_count = len(registry.get('functions', {}))
        print(f"✅ Реестр загружен: {functions_count} функций")
        
        # Показываем первые 5 функций
        print("📋 Первые 5 функций в реестре:")
        for i, func_id in enumerate(list(registry.get('functions', {}).keys())[:5]):
            print(f"   {i+1}. {func_id}")
            
    except Exception as e:
        print(f"❌ Ошибка загрузки реестра: {e}")
        return
    
    # 2. Создаем SFM и проверяем что происходит
    print("\n2. 🔧 СОЗДАЕМ SFM")
    print("-" * 30)
    try:
        from security.safe_function_manager import SafeFunctionManager
        sfm = SafeFunctionManager()
        print(f"✅ SFM создан: {len(sfm.functions)} функций")
        
        # Показываем функции в SFM
        print("📋 Функции в SFM:")
        for i, func_id in enumerate(sfm.functions.keys()):
            print(f"   {i+1}. {func_id}")
            
    except Exception as e:
        print(f"❌ Ошибка создания SFM: {e}")
        return
    
    # 3. Проверяем что происходит в _load_saved_functions
    print("\n3. 🔍 АНАЛИЗИРУЕМ _load_saved_functions")
    print("-" * 30)
    
    # Читаем код метода _load_saved_functions
    try:
        with open('security/safe_function_manager.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Ищем строку с self.functions[func_id] = func
        if 'self.functions[func_id] = func' in content:
            print("✅ Найдена строка: self.functions[func_id] = func")
        else:
            print("❌ НЕ найдена строка: self.functions[func_id] = func")
            
        # Ищем строку с functions_loaded
        if 'functions_loaded' in content:
            print("✅ Найдена переменная: functions_loaded")
        else:
            print("❌ НЕ найдена переменная: functions_loaded")
            
    except Exception as e:
        print(f"❌ Ошибка чтения кода: {e}")
    
    # 4. Проверяем что происходит после загрузки
    print("\n4. 📊 ФИНАЛЬНАЯ ПРОВЕРКА")
    print("-" * 30)
    print(f"📊 Всего функций в реестре: {functions_count}")
    print(f"📊 Всего функций в SFM: {len(sfm.functions)}")
    
    if len(sfm.functions) == functions_count:
        print("✅ ВСЕ ФУНКЦИИ ЗАГРУЖЕНЫ!")
    else:
        print(f"❌ ПРОБЛЕМА: Загружено {len(sfm.functions)} из {functions_count}")
        
        # Проверяем разницу
        registry_functions = set(registry.get('functions', {}).keys())
        sfm_functions = set(sfm.functions.keys())
        missing_functions = registry_functions - sfm_functions
        
        print(f"📋 Отсутствующих функций: {len(missing_functions)}")
        if missing_functions:
            print("📋 Первые 10 отсутствующих функций:")
            for i, func_id in enumerate(list(missing_functions)[:10]):
                print(f"   {i+1}. {func_id}")

if __name__ == "__main__":
    test_sfm_loading()