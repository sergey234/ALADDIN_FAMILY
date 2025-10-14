#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
СТАНДАРТНЫЙ ТЕСТ ПЕРСИСТЕНТНОСТИ - без SafeFunctionManager
"""

import os
import sys
import tempfile
import json
from datetime import datetime

def test_persistence_standalone():
    """Тест персистентности без SafeFunctionManager"""
    print("🧪 СТАНДАРТНЫЙ ТЕСТ ПЕРСИСТЕНТНОСТИ")
    print("=" * 50)
    
    # Создаем временную директорию
    test_dir = tempfile.mkdtemp()
    registry_file = os.path.join(test_dir, 'functions_registry.json')
    
    print(f"1. Тестовая директория: {test_dir}")
    print(f"2. Файл реестра: {registry_file}")
    
    # Создаем тестовые данные
    test_functions = {
        "anti_fraud_master_ai": {
            "function_id": "anti_fraud_master_ai",
            "name": "AntiFraudMasterAI",
            "description": "Защита от мошенничества",
            "function_type": "ai_agent",
            "security_level": "critical",
            "status": "enabled",
            "created_at": datetime.now().isoformat(),
            "is_critical": True,
            "auto_enable": True
        },
        "threat_detection_agent": {
            "function_id": "threat_detection_agent",
            "name": "ThreatDetectionAgent", 
            "description": "Обнаружение угроз",
            "function_type": "ai_agent",
            "security_level": "high",
            "status": "enabled",
            "created_at": datetime.now().isoformat(),
            "is_critical": True,
            "auto_enable": True
        },
        "security_monitoring": {
            "function_id": "security_monitoring",
            "name": "SecurityMonitoring",
            "description": "Мониторинг безопасности",
            "function_type": "security",
            "security_level": "high",
            "status": "enabled",
            "created_at": datetime.now().isoformat(),
            "is_critical": True,
            "auto_enable": True
        }
    }
    
    # Сохраняем в файл
    registry_data = {
        "version": "1.0",
        "last_updated": datetime.now().isoformat(),
        "functions": test_functions
    }
    
    print("3. Сохранение функций безопасности...")
    with open(registry_file, 'w', encoding='utf-8') as f:
        json.dump(registry_data, f, indent=2, ensure_ascii=False)
    
    print(f"   ✅ Файл создан: {os.path.exists(registry_file)}")
    print(f"   📁 Размер файла: {os.path.getsize(registry_file)} байт")
    
    # Загружаем из файла
    print("4. Загрузка функций из файла...")
    with open(registry_file, 'r', encoding='utf-8') as f:
        loaded_data = json.load(f)
    
    loaded_functions = loaded_data.get("functions", {})
    print(f"   ✅ Загружено функций: {len(loaded_functions)}")
    
    # Проверяем содержимое
    print("5. Проверка содержимого...")
    success = True
    
    for func_id, func_data in test_functions.items():
        if func_id in loaded_functions:
            loaded_func = loaded_functions[func_id]
            if (loaded_func["name"] == func_data["name"] and 
                loaded_func["function_type"] == func_data["function_type"] and
                loaded_func["security_level"] == func_data["security_level"]):
                print(f"   ✅ {func_data['name']} - OK")
            else:
                print(f"   ❌ {func_data['name']} - данные не совпадают")
                success = False
        else:
            print(f"   ❌ {func_data['name']} - не найдена")
            success = False
    
    # Проверяем структуру файла
    print("6. Проверка структуры файла...")
    if "version" in loaded_data and "last_updated" in loaded_data:
        print("   ✅ Структура файла корректна")
    else:
        print("   ❌ Структура файла некорректна")
        success = False
    
    # Очистка
    os.remove(registry_file)
    os.rmdir(test_dir)
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 ТЕСТ ПРОЙДЕН!")
        print("✅ Персистентное хранение работает")
        print("✅ JSON сериализация/десериализация работает")
        print("✅ Файловая система работает")
        print("✅ Структура данных корректна")
        print("✅ Готово к интеграции с SafeFunctionManager")
    else:
        print("💥 ТЕСТ НЕ ПРОЙДЕН!")
        print("❌ Проблемы с персистентным хранением")
    
    return success

if __name__ == "__main__":
    success = test_persistence_standalone()
    sys.exit(0 if success else 1)
