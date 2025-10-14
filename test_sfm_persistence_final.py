#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальный тест персистентности SFM
Проверяет что новые функции сохраняются в data/sfm/function_registry.json
"""

import sys
import os
import json
from datetime import datetime

# Добавить путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

try:
    from security.safe_function_manager import SafeFunctionManager, SecurityLevel
    from core.base import SecurityBase
    
    print("🔍 ФИНАЛЬНЫЙ ТЕСТ ПЕРСИСТЕНТНОСТИ SFM")
    print("=" * 60)
    
    # 1. Проверка текущего состояния реестра
    registry_path = "data/sfm/function_registry.json"
    if os.path.exists(registry_path):
        with open(registry_path, 'r', encoding='utf-8') as f:
            registry_data = json.load(f)
        functions_before = len(registry_data.get('functions', {}))
        active_before = registry_data.get('active_functions_count', 0)
        print(f"📊 Состояние ДО теста:")
        print(f"   Всего функций: {functions_before}")
        print(f"   Активных: {active_before}")
        print(f"   Спящих: {registry_data.get('sleeping_functions_count', 0)}")
    else:
        functions_before = 0
        active_before = 0
        print("❌ Реестр не найден!")
        
    print("\n" + "-" * 40)
    
    # 2. Создание SFM и проверка загрузки
    print("🚀 Создание SafeFunctionManager...")
    base_module = SecurityBase("test_base")
    sfm = SafeFunctionManager(base_module)
    
    print(f"✅ SFM создан")
    print(f"   Функций в памяти SFM: {len(sfm.functions)}")
    print(f"   Персистентность включена: {sfm.enable_persistence}")
    print(f"   Путь к реестру: {sfm.registry_file}")
    
    # 3. Регистрация новой функции
    print("\n" + "-" * 40)
    test_function_id = f"test_persistence_function_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"🔧 Регистрация новой функции: {test_function_id}")
    
    result = sfm.register_function(
        function_id=test_function_id,
        name="Test Persistence Function",
        description="Тестовая функция для проверки персистентности",
        function_type="test",
        security_level=SecurityLevel.LOW,
        is_critical=False,
        auto_enable=True
    )
    
    if result:
        print("✅ Функция зарегистрирована в памяти SFM")
        print(f"   Функций в памяти SFM теперь: {len(sfm.functions)}")
    else:
        print("❌ Ошибка регистрации функции!")
        
    # 4. Проверка что функция сохранилась в файл
    print("\n" + "-" * 40)
    print("🔍 Проверка сохранения в файл...")
    
    if os.path.exists(registry_path):
        with open(registry_path, 'r', encoding='utf-8') as f:
            registry_data_after = json.load(f)
        functions_after = len(registry_data_after.get('functions', {}))
        active_after = registry_data_after.get('active_functions_count', 0)
        
        print(f"📊 Состояние ПОСЛЕ теста:")
        print(f"   Всего функций: {functions_after}")
        print(f"   Активных: {active_after}")
        print(f"   Спящих: {registry_data_after.get('sleeping_functions_count', 0)}")
        
        # Проверка что новая функция есть в файле
        if test_function_id in registry_data_after.get('functions', {}):
            print(f"✅ НОВАЯ ФУНКЦИЯ НАЙДЕНА В РЕЕСТРЕ!")
            func_data = registry_data_after['functions'][test_function_id]
            print(f"   Статус: {func_data.get('status')}")
            print(f"   Тип: {func_data.get('function_type')}")
            print(f"   Создана: {func_data.get('created_at')}")
        else:
            print(f"❌ НОВАЯ ФУНКЦИЯ НЕ НАЙДЕНА В РЕЕСТРЕ!")
            print("   Доступные функции:")
            for func_id in list(registry_data_after.get('functions', {}).keys())[:5]:
                print(f"     - {func_id}")
            if len(registry_data_after.get('functions', {})) > 5:
                print(f"     ... и еще {len(registry_data_after.get('functions', {})) - 5}")
        
        # Проверка изменения количества
        if functions_after > functions_before:
            print(f"✅ Количество функций увеличилось на {functions_after - functions_before}")
        else:
            print(f"❌ Количество функций НЕ изменилось")
            
    else:
        print("❌ Реестр не найден после теста!")
    
    print("\n" + "=" * 60)
    print("🏁 ТЕСТ ЗАВЕРШЕН")
    
except Exception as e:
    print(f"❌ ОШИБКА ТЕСТА: {e}")
    import traceback
    traceback.print_exc()