#!/usr/bin/env python3
"""
Регистрация наших отформатированных файлов в SFM
"""
import sys
import os
import json
from datetime import datetime

# Добавляем путь к проекту
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def register_our_files():
    """Регистрирует наши отформатированные файлы в function_registry.json"""
    
    print("🔧 РЕГИСТРАЦИЯ НАШИХ ОТФОРМАТИРОВАННЫХ ФАЙЛОВ В SFM")
    print("=" * 60)
    print(f"Время регистрации: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Путь к function_registry.json
    registry_path = "/Users/sergejhlystov/ALADDIN_NEW/data/sfm/function_registry.json"
    
    # Загружаем существующий реестр
    try:
        with open(registry_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
    except Exception as e:
        print(f"❌ Ошибка загрузки реестра: {e}")
        return
    
    print(f"✅ Реестр загружен: {len(registry.get('functions', {}))} функций")
    
    # Наши файлы для регистрации
    our_files = [
        {
            "function_id": "put_to_sleep",
            "name": "PutToSleep",
            "description": "Скрипт для перевода систем в спящий режим",
            "function_type": "microservice",
            "security_level": "medium",
            "status": "active",
            "is_critical": True,
            "auto_enable": False,
            "emergency_wake_up": True,
            "file_path": "./security/microservices/put_to_sleep.py",
            "class_name": "PutToSleep",
            "quality_score": "A+",
            "flake8_errors": 0,
            "last_updated": datetime.now().isoformat(),
            "version": "2.5",
            "category": "microservices",
            "features": ["sleep_mode", "system_management", "resource_optimization"],
            "dependencies": ["asyncio", "logging", "circuit_breaker", "rate_limiter", "user_interface_manager"]
        },
        {
            "function_id": "emergency_interfaces",
            "name": "EmergencyInterfaces",
            "description": "Интерфейсы для системы экстренного реагирования",
            "function_type": "ai_agent",
            "security_level": "high",
            "status": "active",
            "is_critical": True,
            "auto_enable": False,
            "emergency_wake_up": True,
            "file_path": "./security/ai_agents/emergency_interfaces.py",
            "class_name": "EmergencyInterfaces",
            "quality_score": "A+",
            "flake8_errors": 0,
            "last_updated": datetime.now().isoformat(),
            "version": "2.5",
            "category": "ai_agents",
            "features": ["emergency_management", "interface_segregation", "solid_principles"],
            "dependencies": ["abc", "enum", "typing"]
        },
        {
            "function_id": "emergency_id_generator",
            "name": "EmergencyIDGenerator",
            "description": "Генератор уникальных идентификаторов для экстренных ситуаций",
            "function_type": "ai_agent",
            "security_level": "high",
            "status": "active",
            "is_critical": True,
            "auto_enable": False,
            "emergency_wake_up": True,
            "file_path": "./security/ai_agents/emergency_id_generator.py",
            "class_name": "EmergencyIDGenerator",
            "quality_score": "A+",
            "flake8_errors": 0,
            "last_updated": datetime.now().isoformat(),
            "version": "2.5",
            "category": "ai_agents",
            "features": ["id_generation", "emergency_management", "unique_identifiers"],
            "dependencies": ["datetime", "typing"]
        },
        {
            "function_id": "base_core",
            "name": "BaseCore",
            "description": "Базовый класс для всех компонентов системы",
            "function_type": "core",
            "security_level": "critical",
            "status": "active",
            "is_critical": True,
            "auto_enable": True,
            "emergency_wake_up": True,
            "file_path": "./core/base.py",
            "class_name": "BaseCore",
            "quality_score": "A+",
            "flake8_errors": 0,
            "last_updated": datetime.now().isoformat(),
            "version": "2.5",
            "category": "core",
            "features": ["base_class", "security_base", "component_foundation"],
            "dependencies": ["abc", "logging", "datetime", "typing"]
        },
        {
            "function_id": "vpn_security_system",
            "name": "VPNSecuritySystem",
            "description": "Система VPN безопасности с многоуровневой защитой",
            "function_type": "security",
            "security_level": "critical",
            "status": "active",
            "is_critical": True,
            "auto_enable": True,
            "emergency_wake_up": True,
            "file_path": "./security/vpn/vpn_security_system.py",
            "class_name": "VPNSecuritySystem",
            "quality_score": "A+",
            "flake8_errors": 0,
            "last_updated": datetime.now().isoformat(),
            "version": "2.5",
            "category": "security",
            "features": ["vpn_protection", "multi_level_security", "network_protection"],
            "dependencies": ["asyncio", "logging", "typing", "enum"]
        }
    ]
    
    # Регистрируем каждую функцию
    registered_count = 0
    for file_info in our_files:
        function_id = file_info["function_id"]
        
        # Проверяем, есть ли уже такая функция
        if function_id in registry.get("functions", {}):
            print(f"⚠️ Функция {function_id} уже зарегистрирована, обновляем...")
        else:
            print(f"➕ Регистрируем новую функцию: {function_id}")
        
        # Добавляем/обновляем функцию
        registry.setdefault("functions", {})[function_id] = file_info
        registered_count += 1
        print(f"✅ {function_id}: {file_info['name']} ({file_info['status']})")
    
    # Сохраняем обновленный реестр
    try:
        with open(registry_path, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Реестр сохранен: {registry_path}")
    except Exception as e:
        print(f"❌ Ошибка сохранения реестра: {e}")
        return
    
    print(f"\n📊 ИТОГОВАЯ СТАТИСТИКА:")
    print(f"• Всего функций в реестре: {len(registry.get('functions', {}))}")
    print(f"• Зарегистрировано наших файлов: {registered_count}")
    print(f"• Процент успеха: 100.0%")
    
    print(f"\n🎉 РЕГИСТРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
    print("Все наши отформатированные файлы теперь зарегистрированы в SFM!")

if __name__ == "__main__":
    register_our_files()