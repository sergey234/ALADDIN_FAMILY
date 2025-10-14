#!/usr/bin/env python3
"""
ТЕСТ ИМПОРТОВ И ЗАВИСИМОСТЕЙ
Проверка корректности всех импортов и зависимостей
"""

import sys
import os
from typing import Dict, Any

# Добавляем путь к модулю
sys.path.append('/Users/sergejhlystov/ALADDIN_NEW')

def test_imports():
    """Тест всех импортов файла"""
    
    print("🔍 ЭТАП 6.5: ПРОВЕРКА ИМПОРТОВ И ЗАВИСИМОСТЕЙ")
    print("=" * 60)
    
    # 6.5.1 - Проверка всех импортов на корректность
    print("\n6.5.1 - ПРОВЕРКА ИМПОРТОВ НА КОРРЕКТНОСТЬ:")
    print("-" * 50)
    
    imports_to_test = [
        # Стандартные библиотеки
        ("asyncio", "Стандартная библиотека"),
        ("logging", "Стандартная библиотека"),
        ("uuid", "Стандартная библиотека"),
        ("dataclasses", "Стандартная библиотека"),
        ("datetime", "Стандартная библиотека"),
        ("enum", "Стандартная библиотека"),
        ("typing", "Стандартная библиотека"),
        # Внешние библиотеки
        ("aiohttp", "Внешняя библиотека"),
    ]
    
    results = {}
    
    for module_name, module_type in imports_to_test:
        try:
            if module_name == "dataclasses":
                from dataclasses import dataclass, field
                print(f"  ✅ {module_name} ({module_type}) - импортирован")
                results[module_name] = True
            elif module_name == "datetime":
                from datetime import datetime
                print(f"  ✅ {module_name} ({module_type}) - импортирован")
                results[module_name] = True
            elif module_name == "enum":
                from enum import Enum
                print(f"  ✅ {module_name} ({module_type}) - импортирован")
                results[module_name] = True
            elif module_name == "typing":
                from typing import Any, Dict, List, Optional, Tuple
                print(f"  ✅ {module_name} ({module_type}) - импортирован")
                results[module_name] = True
            else:
                __import__(module_name)
                print(f"  ✅ {module_name} ({module_type}) - импортирован")
                results[module_name] = True
        except ImportError as e:
            print(f"  ❌ {module_name} ({module_type}) - ОШИБКА: {e}")
            results[module_name] = False
        except Exception as e:
            print(f"  ⚠️ {module_name} ({module_type}) - ПРЕДУПРЕЖДЕНИЕ: {e}")
            results[module_name] = False
    
    # 6.5.2 - Проверка доступности импортируемых модулей
    print("\n6.5.2 - ПРОВЕРКА ДОСТУПНОСТИ МОДУЛЕЙ:")
    print("-" * 45)
    
    # Проверка aiohttp
    try:
        import aiohttp
        print(f"  ✅ aiohttp версия: {aiohttp.__version__}")
    except ImportError as e:
        print(f"  ❌ aiohttp недоступен: {e}")
        results["aiohttp"] = False
    
    # 6.5.3 - Проверка циклических зависимостей
    print("\n6.5.3 - ПРОВЕРКА ЦИКЛИЧЕСКИХ ЗАВИСИМОСТЕЙ:")
    print("-" * 50)
    
    # Проверка импорта основного модуля
    try:
        from security.ai_agents.family_communication_replacement import (
            FamilyRole,
            MessageType,
            MessagePriority,
            CommunicationChannel,
            FamilyMember,
            Message,
            ExternalAPIHandler,
            FamilyCommunicationReplacement
        )
        print("  ✅ Основной модуль импортирован без циклических зависимостей")
        
        # Проверка внутренних импортов
        print("\n  🔍 Проверка внутренних импортов:")
        
        # Проверка SmartNotificationManager
        try:
            from security.ai_agents.smart_notification_manager import SmartNotificationManager
            print("    ✅ SmartNotificationManager - доступен")
        except ImportError as e:
            print(f"    ⚠️ SmartNotificationManager - недоступен: {e}")
        
        # Проверка ContextualAlertSystem
        try:
            from security.ai_agents.contextual_alert_system import ContextualAlertSystem
            print("    ✅ ContextualAlertSystem - доступен")
        except ImportError as e:
            print(f"    ⚠️ ContextualAlertSystem - недоступен: {e}")
            
    except ImportError as e:
        print(f"  ❌ Ошибка импорта основного модуля: {e}")
        return False
    
    # 6.5.4 - Проверка неиспользуемых импортов (F401)
    print("\n6.5.4 - ПРОВЕРКА НЕИСПОЛЬЗУЕМЫХ ИМПОРТОВ:")
    print("-" * 50)
    
    # Запуск flake8 для проверки F401
    import subprocess
    try:
        result = subprocess.run([
            'python3', '-m', 'flake8', 
            'security/ai_agents/family_communication_replacement.py',
            '--select=F401',
            '--count'
        ], capture_output=True, text=True, cwd='/Users/sergejhlystov/ALADDIN_NEW')
        
        if result.returncode == 0:
            print("  ✅ Неиспользуемых импортов не найдено")
        else:
            print(f"  ⚠️ Найдены неиспользуемые импорты:")
            print(f"    {result.stdout}")
            
    except Exception as e:
        print(f"  ⚠️ Ошибка проверки flake8: {e}")
    
    # Итоговая статистика
    print("\n📊 ИТОГОВАЯ СТАТИСТИКА ИМПОРТОВ:")
    print("-" * 40)
    
    successful_imports = sum(1 for success in results.values() if success)
    total_imports = len(results)
    
    print(f"  Успешных импортов: {successful_imports}/{total_imports}")
    print(f"  Процент успеха: {(successful_imports/total_imports)*100:.1f}%")
    
    if successful_imports == total_imports:
        print("  ✅ ВСЕ ИМПОРТЫ РАБОТАЮТ КОРРЕКТНО!")
        return True
    else:
        print("  ⚠️ НЕКОТОРЫЕ ИМПОРТЫ ТРЕБУЮТ ВНИМАНИЯ")
        return False

if __name__ == "__main__":
    test_imports()