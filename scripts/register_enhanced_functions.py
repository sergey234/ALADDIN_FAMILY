#!/usr/bin/env python3
"""
Скрипт для регистрации enhanced функций в SFM
"""

import json
import os
from datetime import datetime
from pathlib import Path

def register_enhanced_functions():
    """Регистрирует enhanced функции в SFM"""
    
    # Загружаем текущий SFM реестр
    sfm_file = Path("data/sfm/function_registry.json")
    
    if not sfm_file.exists():
        print("❌ SFM файл не найден!")
        return False
    
    with open(sfm_file, 'r', encoding='utf-8') as f:
        sfm_data = json.load(f)
    
    functions = sfm_data.get('functions', {})
    
    # Список enhanced функций для регистрации
    enhanced_functions = [
        {
            "name": "mobile_security_agent_enhanced",
            "file_path": "security/ai_agents/mobile_security_agent_enhanced.py",
            "category": "ai_agents",
            "description": "Enhanced Mobile Security Agent with advanced features"
        },
        {
            "name": "financial_protection_hub_enhanced", 
            "file_path": "security/ai_agents/financial_protection_hub_enhanced.py",
            "category": "ai_agents",
            "description": "Enhanced Financial Protection Hub with improved algorithms"
        },
        {
            "name": "malware_detection_agent_enhanced",
            "file_path": "security/ai_agents/malware_detection_agent_enhanced.py", 
            "category": "ai_agents",
            "description": "Enhanced Malware Detection Agent with better detection"
        },
        {
            "name": "safe_quality_analyzer_enhanced",
            "file_path": "security/ai_agents/safe_quality_analyzer_enhanced.py",
            "category": "ai_agents", 
            "description": "Enhanced Safe Quality Analyzer with advanced analysis"
        },
        {
            "name": "security_quality_analyzer_enhanced",
            "file_path": "security/ai_agents/security_quality_analyzer_enhanced.py",
            "category": "ai_agents",
            "description": "Enhanced Security Quality Analyzer with improved metrics"
        },
        {
            "name": "family_communication_hub_enhanced",
            "file_path": "security/family/family_communication_hub_enhanced.py",
            "category": "family",
            "description": "Enhanced Family Communication Hub with better features"
        },
        {
            "name": "parental_control_bot_v2_enhanced",
            "file_path": "security/bots/parental_control_bot_v2_enhanced.py",
            "category": "bots",
            "description": "Enhanced Parental Control Bot v2 with advanced controls"
        },
        {
            "name": "notification_service_enhanced",
            "file_path": "security/microservices/notification_service_enhanced.py",
            "category": "microservices",
            "description": "Enhanced Notification Service with improved delivery"
        },
        {
            "name": "time_monitor_enhanced",
            "file_path": "security/active/time_monitor_enhanced.py",
            "category": "active",
            "description": "Enhanced Time Monitor with better tracking"
        },
        {
            "name": "elderly_interface_manager_enhanced",
            "file_path": "security/managers/elderly_interface_manager_enhanced.py",
            "category": "managers",
            "description": "Enhanced Elderly Interface Manager with improved UX"
        },
        {
            "name": "content_analyzer_enhanced",
            "file_path": "security/ai_agents/content_analyzer_enhanced.py",
            "category": "ai_agents",
            "description": "Enhanced Content Analyzer with better analysis"
        },
        {
            "name": "put_to_sleep_enhanced",
            "file_path": "security/microservices/put_to_sleep_enhanced.py",
            "category": "microservices",
            "description": "Enhanced Put to Sleep function with improved efficiency"
        },
        {
            "name": "user_interface_manager_extra_enhanced",
            "file_path": "security/microservices/user_interface_manager_extra_enhanced.py",
            "category": "microservices",
            "description": "Enhanced User Interface Manager Extra with additional features"
        }
    ]
    
    print("🔄 РЕГИСТРАЦИЯ ENHANCED ФУНКЦИЙ В SFM")
    print("=" * 60)
    
    registered_count = 0
    failed_count = 0
    
    for i, func in enumerate(enhanced_functions, 1):
        func_name = func["name"]
        file_path = func["file_path"]
        category = func["category"]
        description = func["description"]
        
        print(f"\n{i:2d}. {func_name}")
        print(f"    📁 {file_path}")
        print(f"    📂 {category}")
        
        # Проверяем существование файла
        if not Path(file_path).exists():
            print(f"    ❌ Файл не найден!")
            failed_count += 1
            continue
        
        # Проверяем, не зарегистрирована ли уже
        if func_name in functions:
            print(f"    ⚠️  Уже зарегистрирована!")
            continue
        
        # Создаем запись функции
        function_data = {
            "name": func_name,
            "file_path": file_path,
            "category": category,
            "description": description,
            "status": "sleeping",  # По умолчанию спящая
            "priority": "medium",
            "created_at": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat(),
            "version": "enhanced",
            "dependencies": [],
            "tags": ["enhanced", "backup_derived", category]
        }
        
        # Добавляем в реестр
        functions[func_name] = function_data
        
        print(f"    ✅ Зарегистрирована (sleeping)")
        registered_count += 1
    
    # Обновляем статистику
    sfm_data["total_functions"] = len(functions)
    sfm_data["last_updated"] = datetime.now().isoformat()
    
    # Сохраняем обновленный реестр
    try:
        with open(sfm_file, 'w', encoding='utf-8') as f:
            json.dump(sfm_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 ИТОГОВАЯ СТАТИСТИКА:")
        print(f"   • Зарегистрировано: {registered_count}")
        print(f"   • Ошибок: {failed_count}")
        print(f"   • Всего функций в SFM: {len(functions)}")
        
        if failed_count == 0:
            print(f"\n🎉 ВСЕ ENHANCED ФУНКЦИИ УСПЕШНО ЗАРЕГИСТРИРОВАНЫ!")
            return True
        else:
            print(f"\n⚠️  ЕСТЬ ОШИБКИ! Проверьте детали выше.")
            return False
            
    except Exception as e:
        print(f"\n❌ Ошибка сохранения SFM: {e}")
        return False

if __name__ == "__main__":
    success = register_enhanced_functions()
    exit(0 if success else 1)
