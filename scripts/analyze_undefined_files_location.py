#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализ расположения неопределенных файлов
Проверка где находятся файлы и где должны быть по архитектуре
"""

import sys
import os
from pathlib import Path

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent.parent))

def find_undefined_files():
    """Найти все неопределенные файлы и их расположение"""
    print("🔍 АНАЛИЗ РАСПОЛОЖЕНИЯ НЕОПРЕДЕЛЕННЫХ ФАЙЛОВ")
    print("=" * 80)
    
    # Список неопределенных файлов из анализа
    undefined_files = [
        "anti_fraud_master_ai.py",
        "voice_response_generator.py", 
        "natural_language_processor.py",
        "family_communication_replacement.py",
        "emergency_id_generator.py",
        "parent_control_panel.py",
        "emergency_models.py",
        "emergency_ml_models.py",
        "emergency_formatters.py",
        "emergency_base_models.py",
        "emergency_base_models_refactored.py",
        "emergency_statistics_models.py",
        "emergency_service.py",
        "emergency_service_caller.py",
        "messenger_integration.py",
        "circuit_breaker.py",
        "rate_limiter.py",
        "put_to_sleep.py",
        "simple_sleep.py",
        "configuration.py",
        "singleton.py",
        "logging_module.py",
        "code_quality_config.py",
        "safe_config.py",
        "replacement_components_config.py"
    ]
    
    # Анализ каждого файла
    file_analysis = {}
    
    for file_name in undefined_files:
        print(f"\n📁 Анализ файла: {file_name}")
        print("-" * 50)
        
        # Ищем файл в системе
        found_locations = []
        for root, dirs, files in os.walk("."):
            if file_name in files:
                found_locations.append(root)
        
        if found_locations:
            print(f"✅ НАЙДЕН в {len(found_locations)} местах:")
            for location in found_locations:
                print(f"   • {location}")
        else:
            print("❌ НЕ НАЙДЕН")
            continue
        
        # Определяем где должен быть файл
        file_lower = file_name.lower()
        suggested_location = "❓ НЕОПРЕДЕЛЕННО"
        
        if "agent" in file_lower or "ai" in file_lower:
            suggested_location = "security/ai_agents/"
        elif "manager" in file_lower:
            suggested_location = "security/managers/"
        elif "engine" in file_lower or "system" in file_lower:
            suggested_location = "security/engines/"
        elif "bot" in file_lower:
            suggested_location = "security/bots/"
        elif "analyzer" in file_lower or "detector" in file_lower:
            suggested_location = "security/analyzers/"
        elif "service" in file_lower or "microservice" in file_lower:
            suggested_location = "security/microservices/"
        elif "model" in file_lower or "base" in file_lower:
            suggested_location = "security/models/"
        elif "integration" in file_lower:
            suggested_location = "security/integrations/"
        elif "utils" in file_lower or "helper" in file_lower:
            suggested_location = "security/utils/"
        elif "config" in file_lower:
            suggested_location = "config/"
        elif "core" in file_lower or "singleton" in file_lower or "logging" in file_lower:
            suggested_location = "core/"
        elif "privacy" in file_lower:
            suggested_location = "security/privacy/"
        elif "ci" in file_lower or "cd" in file_lower:
            suggested_location = "security/ci_cd/"
        
        print(f"🎯 ДОЛЖЕН БЫТЬ: {suggested_location}")
        
        # Проверяем правильность расположения
        current_location = found_locations[0] if found_locations else ""
        is_correct = suggested_location in current_location
        
        if is_correct:
            print("✅ РАСПОЛОЖЕНИЕ ПРАВИЛЬНОЕ")
        else:
            print("❌ РАСПОЛОЖЕНИЕ НЕПРАВИЛЬНОЕ")
            print(f"   Текущее: {current_location}")
            print(f"   Должно быть: {suggested_location}")
        
        file_analysis[file_name] = {
            "current_location": current_location,
            "suggested_location": suggested_location,
            "is_correct": is_correct,
            "found_locations": found_locations
        }
    
    return file_analysis

def analyze_architecture_violations():
    """Анализ нарушений архитектуры"""
    print("\n🚨 АНАЛИЗ НАРУШЕНИЙ АРХИТЕКТУРЫ")
    print("=" * 80)
    
    file_analysis = find_undefined_files()
    
    # Группируем по нарушениям
    violations = {
        "❌ НЕПРАВИЛЬНОЕ РАСПОЛОЖЕНИЕ": [],
        "✅ ПРАВИЛЬНОЕ РАСПОЛОЖЕНИЕ": [],
        "❓ ТРЕБУЕТ РУЧНОЙ КЛАССИФИКАЦИИ": []
    }
    
    for file_name, analysis in file_analysis.items():
        if analysis["is_correct"]:
            violations["✅ ПРАВИЛЬНОЕ РАСПОЛОЖЕНИЕ"].append(file_name)
        elif analysis["suggested_location"] == "❓ НЕОПРЕДЕЛЕННО":
            violations["❓ ТРЕБУЕТ РУЧНОЙ КЛАССИФИКАЦИИ"].append(file_name)
        else:
            violations["❌ НЕПРАВИЛЬНОЕ РАСПОЛОЖЕНИЕ"].append(file_name)
    
    # Выводим результаты
    for violation_type, files in violations.items():
        if files:
            print(f"\n{violation_type} ({len(files)} файлов):")
            for file_name in files:
                analysis = file_analysis[file_name]
                print(f"  • {file_name}")
                if not analysis["is_correct"] and analysis["suggested_location"] != "❓ НЕОПРЕДЕЛЕННО":
                    print(f"    Текущее: {analysis['current_location']}")
                    print(f"    Должно быть: {analysis['suggested_location']}")
    
    return violations

def suggest_architecture_fixes():
    """Предложения по исправлению архитектуры"""
    print("\n🔧 ПРЕДЛОЖЕНИЯ ПО ИСПРАВЛЕНИЮ АРХИТЕКТУРЫ")
    print("=" * 80)
    
    violations = analyze_architecture_violations()
    
    print("\n📋 ПЛАН ИСПРАВЛЕНИЙ:")
    print("=" * 50)
    
    # Создаем недостающие папки
    missing_folders = [
        "security/engines/",
        "security/analyzers/", 
        "security/models/",
        "security/integrations/",
        "security/utils/"
    ]
    
    print("1️⃣ СОЗДАТЬ НЕДОСТАЮЩИЕ ПАПКИ:")
    for folder in missing_folders:
        if not os.path.exists(folder):
            print(f"   mkdir -p {folder}")
        else:
            print(f"   ✅ {folder} уже существует")
    
    print("\n2️⃣ ПЕРЕМЕСТИТЬ ФАЙЛЫ:")
    
    # Файлы для перемещения
    move_commands = [
        ("security/ai_agents/emergency_models.py", "security/models/"),
        ("security/ai_agents/emergency_ml_models.py", "security/models/"),
        ("security/ai_agents/emergency_formatters.py", "security/models/"),
        ("security/ai_agents/emergency_base_models.py", "security/models/"),
        ("security/ai_agents/emergency_base_models_refactored.py", "security/models/"),
        ("security/ai_agents/emergency_statistics_models.py", "security/models/"),
        ("security/ai_agents/emergency_service.py", "security/microservices/"),
        ("security/ai_agents/emergency_service_caller.py", "security/microservices/"),
        ("security/ai_agents/messenger_integration.py", "security/integrations/"),
        ("security/ai_agents/emergency_location_utils.py", "security/utils/"),
        ("security/ai_agents/emergency_security_utils.py", "security/utils/"),
        ("security/ai_agents/emergency_time_utils.py", "security/utils/"),
        ("security/ai_agents/emergency_utils.py", "security/utils/"),
        ("security/ai_agents/emergency_ml_analyzer.py", "security/analyzers/"),
        ("security/ai_agents/emergency_performance_analyzer.py", "security/analyzers/"),
        ("security/ai_agents/emergency_risk_analyzer.py", "security/analyzers/"),
        ("security/ai_agents/emergency_validators.py", "security/analyzers/"),
        ("security/ai_agents/voice_security_validator.py", "security/analyzers/"),
        ("security/ai_agents/behavioral_analytics_engine.py", "security/engines/"),
        ("security/ai_agents/contextual_alert_system.py", "security/engines/"),
        ("security/ai_agents/deepfake_protection_system.py", "security/engines/"),
        ("security/ai_agents/voice_analysis_engine.py", "security/engines/"),
        ("security/ai_agents/speech_recognition_engine.py", "security/engines/")
    ]
    
    for source, destination in move_commands:
        if os.path.exists(source):
            print(f"   mv {source} {destination}")
        else:
            print(f"   ❌ {source} не найден")
    
    print("\n3️⃣ ОБНОВИТЬ ИМПОРТЫ:")
    print("   После перемещения файлов необходимо обновить все импорты")
    print("   в файлах, которые используют перемещенные модули")
    
    print("\n4️⃣ ПРОВЕРИТЬ ФУНКЦИОНАЛЬНОСТЬ:")
    print("   Запустить тесты после перемещения файлов")

def main():
    """Основная функция"""
    print("🚀 АНАЛИЗ АРХИТЕКТУРЫ НЕОПРЕДЕЛЕННЫХ ФАЙЛОВ")
    print("=" * 80)
    
    # Анализ расположения файлов
    file_analysis = find_undefined_files()
    
    # Анализ нарушений архитектуры
    violations = analyze_architecture_violations()
    
    # Предложения по исправлению
    suggest_architecture_fixes()
    
    print("\n🎯 ЗАКЛЮЧЕНИЕ:")
    print("=" * 50)
    print("✅ Проанализированы все неопределенные файлы")
    print("✅ Выявлены нарушения архитектуры")
    print("✅ Предложен план исправлений")
    print("✅ Определены необходимые действия")

if __name__ == "__main__":
    main()