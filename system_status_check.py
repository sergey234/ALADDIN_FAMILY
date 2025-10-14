#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка статуса системы ALADDIN
"""

import sys
import os
import json
from datetime import datetime

sys.path.append('.')

def check_api_status():
    """Проверка статуса API сервера"""
    try:
        import requests
        response = requests.get('http://localhost:5000/api/status', timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                "status": "running",
                "uptime": data.get('uptime_minutes', 0),
                "requests": data.get('total_requests', 0),
                "success_rate": data.get('success_rate', 0)
            }
    except:
        pass
    return {"status": "stopped"}

def check_auto_learning_status():
    """Проверка статуса системы автоматического обучения"""
    try:
        from security.ai_agents.auto_learning_system import AutoLearningSystem
        auto_learning = AutoLearningSystem()
        status = auto_learning.get_status()
        return status
    except Exception as e:
        return {"error": str(e), "status": "not_available"}

def check_data_collection():
    """Проверка сбора данных"""
    data_dirs = [
        "data/auto_learning/",
        "data/enhanced_collection/",
        "data/ml_models/",
        "data/demo_russian_fraud_data.json"
    ]
    
    results = {}
    for dir_path in data_dirs:
        if os.path.exists(dir_path):
            if os.path.isdir(dir_path):
                files = os.listdir(dir_path)
                results[dir_path] = {
                    "exists": True,
                    "type": "directory",
                    "files_count": len(files),
                    "files": files[:5]  # Первые 5 файлов
                }
            else:
                size = os.path.getsize(dir_path)
                results[dir_path] = {
                    "exists": True,
                    "type": "file",
                    "size_bytes": size
                }
        else:
            results[dir_path] = {"exists": False}
    
    return results

def check_sfm_integration():
    """Проверка интеграции с SFM"""
    try:
        sfm_path = "data/sfm/function_registry.json"
        if os.path.exists(sfm_path):
            with open(sfm_path, 'r', encoding='utf-8') as f:
                registry = json.load(f)
            
            # Ищем новые функции
            new_functions = [
                "auto_learning_system",
                "enhanced_data_collector", 
                "fraud_detection_api",
                "improved_ml_models"
            ]
            
            found_functions = []
            for func_id in new_functions:
                if func_id in registry.get('functions', {}):
                    found_functions.append(func_id)
            
            return {
                "exists": True,
                "total_functions": len(registry.get('functions', {})),
                "new_functions_found": found_functions,
                "new_functions_count": len(found_functions)
            }
    except Exception as e:
        return {"error": str(e), "exists": False}
    
    return {"exists": False}

def main():
    """Основная функция проверки"""
    print("🔍 ПРОВЕРКА СТАТУСА СИСТЕМЫ ALADDIN")
    print("=" * 60)
    print(f"📅 Время проверки: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    print()
    
    # Проверка API сервера
    print("🌐 API СЕРВЕР:")
    api_status = check_api_status()
    if api_status["status"] == "running":
        print(f"   ✅ Статус: Работает")
        print(f"   ⏰ Время работы: {api_status['uptime']} минут")
        print(f"   📊 Запросов обработано: {api_status['requests']}")
        print(f"   🎯 Успешность: {api_status['success_rate']}%")
    else:
        print(f"   ❌ Статус: Остановлен")
    print()
    
    # Проверка автоматического обучения
    print("🤖 СИСТЕМА АВТОМАТИЧЕСКОГО ОБУЧЕНИЯ:")
    auto_status = check_auto_learning_status()
    if "error" not in auto_status:
        print(f"   🟢 Работает: {auto_status.get('is_running', False)}")
        print(f"   📅 Последнее обновление: {auto_status.get('last_update', 'Никогда')}")
        print(f"   ⏰ Интервал обновления: {auto_status.get('update_interval', 0)} секунд")
        print(f"   📊 Интервал сбора данных: {auto_status.get('data_collection_interval', 0)} секунд")
        print(f"   🔄 Следующий сбор: {auto_status.get('next_collection', 'Не запланирован')}")
    else:
        print(f"   ❌ Ошибка: {auto_status['error']}")
    print()
    
    # Проверка сбора данных
    print("📊 СБОР ДАННЫХ:")
    data_status = check_data_collection()
    for path, info in data_status.items():
        if info.get("exists"):
            if info["type"] == "directory":
                print(f"   ✅ {path}: {info['files_count']} файлов")
                if info['files']:
                    print(f"      📁 Файлы: {', '.join(info['files'])}")
            else:
                size_kb = info['size_bytes'] / 1024
                print(f"   ✅ {path}: {size_kb:.1f} KB")
        else:
            print(f"   ❌ {path}: Не найден")
    print()
    
    # Проверка SFM интеграции
    print("🔧 SFM ИНТЕГРАЦИЯ:")
    sfm_status = check_sfm_integration()
    if sfm_status.get("exists"):
        print(f"   ✅ Реестр функций: Найден")
        print(f"   📊 Всего функций: {sfm_status['total_functions']}")
        print(f"   🆕 Новых функций: {sfm_status['new_functions_count']}")
        if sfm_status['new_functions_found']:
            print(f"      🔧 Интегрированы: {', '.join(sfm_status['new_functions_found'])}")
    else:
        print(f"   ❌ Реестр функций: Не найден")
    print()
    
    # Итоговый статус
    print("🎯 ИТОГОВЫЙ СТАТУС СИСТЕМЫ:")
    
    active_components = 0
    total_components = 4
    
    if api_status["status"] == "running":
        active_components += 1
        print("   ✅ API сервер: АКТИВЕН")
    else:
        print("   ❌ API сервер: НЕ АКТИВЕН")
    
    if auto_status.get("is_running", False):
        active_components += 1
        print("   ✅ Автообучение: АКТИВНО")
    else:
        print("   ❌ Автообучение: НЕ АКТИВНО")
    
    if any(info.get("exists") for info in data_status.values()):
        active_components += 1
        print("   ✅ Сбор данных: АКТИВЕН")
    else:
        print("   ❌ Сбор данных: НЕ АКТИВЕН")
    
    if sfm_status.get("exists", False):
        active_components += 1
        print("   ✅ SFM интеграция: АКТИВНА")
    else:
        print("   ❌ SFM интеграция: НЕ АКТИВНА")
    
    print()
    percentage = (active_components / total_components) * 100
    print(f"📊 ОБЩАЯ АКТИВНОСТЬ: {active_components}/{total_components} ({percentage:.0f}%)")
    
    if percentage >= 75:
        print("🟢 СИСТЕМА РАБОТАЕТ ОТЛИЧНО!")
    elif percentage >= 50:
        print("🟡 СИСТЕМА РАБОТАЕТ ЧАСТИЧНО")
    else:
        print("🔴 СИСТЕМА ТРЕБУЕТ ВНИМАНИЯ")
    
    print()
    print("💡 РЕКОМЕНДАЦИИ:")
    if api_status["status"] != "running":
        print("   🔧 Запустите API сервер: python3 security/ai_agents/fraud_detection_api.py")
    if not auto_status.get("is_running", False):
        print("   🔧 Запустите автообучение: python3 security/ai_agents/auto_learning_system.py")
    if not any(info.get("exists") for info in data_status.values()):
        print("   🔧 Запустите сбор данных: python3 security/ai_agents/enhanced_data_collector.py")

if __name__ == "__main__":
    main()