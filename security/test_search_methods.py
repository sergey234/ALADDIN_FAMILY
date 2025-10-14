#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест методов поиска SFM - проверка критических методов поиска
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.safe_function_manager import SafeFunctionManager, FunctionStatus, SecurityLevel

def test_search_methods():
    """Тестирование методов поиска SFM"""
    print("🔍 ТЕСТИРОВАНИЕ МЕТОДОВ ПОИСКА SFM")
    print("=" * 50)
    
    # Создание экземпляра SFM
    sfm = SafeFunctionManager("TestSFM")
    
    # Регистрация тестовых функций
    test_functions = [
        {
            "function_id": "test_security_001",
            "name": "Security Scanner",
            "description": "Сканирование системы на угрозы",
            "function_type": "SECURITY",
            "security_level": SecurityLevel.HIGH,
            "is_critical": True
        },
        {
            "function_id": "test_family_001", 
            "name": "Family Monitor",
            "description": "Мониторинг семейной безопасности",
            "function_type": "FAMILY",
            "security_level": SecurityLevel.MEDIUM,
            "is_critical": False
        },
        {
            "function_id": "test_ai_001",
            "name": "AI Analyzer", 
            "description": "Анализ данных с помощью ИИ",
            "function_type": "AI_ML",
            "security_level": SecurityLevel.HIGH,
            "is_critical": True
        }
    ]
    
    # Регистрация функций
    for func_data in test_functions:
        sfm.register_function(
            function_id=func_data["function_id"],
            name=func_data["name"],
            description=func_data["description"],
            function_type=func_data["function_type"],
            security_level=func_data["security_level"],
            is_critical=func_data["is_critical"]
        )
        sfm.enable_function(func_data["function_id"])
    
    print(f"✅ Зарегистрировано {len(test_functions)} тестовых функций")
    
    # Тест 1: search_functions
    print("\n🔍 ТЕСТ 1: search_functions")
    results = sfm.search_functions("security")
    print(f"Поиск 'security': найдено {len(results)} функций")
    for result in results:
        print(f"  - {result['name']} ({result['function_id']})")
    
    # Тест 2: find_function
    print("\n🔍 ТЕСТ 2: find_function")
    function = sfm.find_function("test_security_001")
    if function:
        print(f"Функция найдена: {function['name']}")
    else:
        print("❌ Функция не найдена")
    
    # Тест 3: get_functions_by_category
    print("\n🔍 ТЕСТ 3: get_functions_by_category")
    security_functions = sfm.get_functions_by_category("SECURITY")
    print(f"Функции SECURITY: {len(security_functions)}")
    for func in security_functions:
        print(f"  - {func['name']}")
    
    # Тест 4: get_functions_by_status
    print("\n🔍 ТЕСТ 4: get_functions_by_status")
    enabled_functions = sfm.get_functions_by_status("enabled")
    print(f"Включенные функции: {len(enabled_functions)}")
    
    # Тест 5: search_functions_advanced
    print("\n🔍 ТЕСТ 5: search_functions_advanced")
    advanced_results = sfm.search_functions_advanced(
        query="monitor",
        category="FAMILY",
        is_critical=False
    )
    print(f"Расширенный поиск: найдено {advanced_results['total_found']} функций")
    print(f"Примененные фильтры: {advanced_results['filters_applied']}")
    
    # Тест 6: get_functions_by_type
    print("\n🔍 ТЕСТ 6: get_functions_by_type")
    ai_functions = sfm.get_functions_by_type("AI_ML")
    print(f"Функции AI_ML: {len(ai_functions)}")
    
    print("\n✅ ВСЕ ТЕСТЫ МЕТОДОВ ПОИСКА ЗАВЕРШЕНЫ")
    return True

if __name__ == "__main__":
    try:
        test_search_methods()
        print("\n🎉 КРИТИЧЕСКАЯ ЗАДАЧА ВЫПОЛНЕНА: Методы поиска добавлены в SFM!")
    except Exception as e:
        print(f"\n❌ ОШИБКА ТЕСТИРОВАНИЯ: {e}")
        sys.exit(1)